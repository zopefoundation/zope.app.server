##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""startup ZCML namespace directive tests

$Id$
"""
import unittest
from zope.app.publication.interfaces import IPublicationRequestFactoryFactory
from zope.app.server.requestfactoryregistry import getRequestFactory
from zope.app.server.servertyperegistry import getServerType
from zope.app.publication.browser import BrowserPublication
from zope.configuration import xmlconfig
from zope.interface import implements
from zope.publisher.browser import BrowserRequest
from zope.server.http.publisherhttpserver import PublisherHTTPServer
from zope.server.http.commonhitlogger import CommonHitLogger
from zope.testing.cleanup import CleanUp
import zope.app.server.tests

class TF:
    "test request factory"
    implements(IPublicationRequestFactoryFactory)

tf = TF()


class DirectivesTest(CleanUp, unittest.TestCase):

    def setUp(self):
        CleanUp.setUp(self)
        self.context = xmlconfig.file("startup.zcml", zope.app.server.tests)

    def test_registerServerType(self):
        self.assertEqual(getServerType('Browser')._factory,
                         PublisherHTTPServer)
        self.assertEqual(getServerType('Browser')._logFactory, CommonHitLogger)
        self.assertEqual(getServerType('Browser')._requestFactory,
                         "BrowserRequestFactory")
        self.assertEqual(getServerType('Browser')._defaultPort, 8080)
        self.assertEqual(getServerType('Browser')._defaultVerbose, True)

    def test_registerRequestFactory(self):
        self.assertEqual(
            getRequestFactory('BrowserRequestFactory')._pubFactory,
            BrowserPublication)
        self.assertEqual(
            getRequestFactory('BrowserRequestFactory')._request,
            BrowserRequest)

    def test_registerRequestFactory_with_Factory(self):
        self.assertEqual(getRequestFactory('BrowserRequestFactory2'), tf)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
