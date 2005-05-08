##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the FTP server.
"""

import os
from unittest import TestCase, TestSuite, main, makeSuite

from twisted.cred import checkers, portal
from twisted.internet import reactor, protocol
from twisted.protocols import ftp
from twisted.trial.util import wait

from zope.testing import doctest

from zope.app.server.ftp.server import FTPFactory

from zope.app.server.tests.test_publisher import RequestFactory
from zope.app.server.tests import demofs

class TestServerSetup(TestCase):

    def setUp(self):
        root = demofs.Directory()
        # the tuple has a user name is used by ZopeSimpleAuthentication to
        # authenticate users.
        root.grant(('root', 'root'), demofs.write)
        rootfs = demofs.DemoFileSystem(root, ('root', 'root'))

        self.factory = FTPFactory(request_factory = RequestFactory(rootfs))
        self.port = reactor.listenTCP(0, self.factory, interface="127.0.0.1")

        buildProtocol = self.factory.buildProtocol
        def _rememberProtocolInstance(addr):
            protocol = buildProtocol(addr)
            self.serverProtocol = protocol.wrappedProtocol
            return protocol
        self.factory.buildProtocol = _rememberProtocolInstance

        # Connect a client to it
        portNum = self.port.getHost().port
        clientCreator = protocol.ClientCreator(reactor, ftp.FTPClientBasic)
        self.client = wait(clientCreator.connectTCP("127.0.0.1", portNum))

    def tearDown(self):
        # Clean up sockets
        self.client.transport.loseConnection()
        d = self.port.stopListening()
        if d is not None:
            wait(d)

        del self.serverProtocol

    def test_serverUp(self):
        # test if we can bring the server up and down.
        pass

    def _authLogin(self):
        # Reconfigure the server to disallow anonymous access.
        responseLines = wait(self.client.queueStringCommand('USER root'))
        self.assertEqual(['331 Password required for root.'], responseLines)

        responseLines = wait(self.client.queueStringCommand('PASS root'))
        self.assertEqual(['230 User logged in, proceed'], responseLines)

    def test_MLD(self):
        self._authLogin()
        responseLines = wait(self.client.queueStringCommand('MKD /newdir'))
        self.assertEqual(['257 "/newdir" created.'], responseLines)


def test_suite():
    return TestSuite((
        makeSuite(TestServerSetup),
        doctest.DocTestSuite('zope.app.server.ftp.server'),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
