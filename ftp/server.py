##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Twisted-based FTP server for Zope's Publisher.
"""
__docformat__="restructuredtext"

from zope.interface import implements

from twisted.cred import portal, credentials
from twisted.protocols import ftp, policies
from twisted.internet import reactor, defer

from zope.app.server.server import ServerType

from zope.app.server.utils import PublisherFileSystem, \
     ZopeSimpleAuthenticatation
from zope.app.server.ftp.ftp import ZopeFTPShell

class FTPRealm(object):

    implements(portal.IRealm)

    def __init__(self, request_factory, logout = None):
        self.request_factory = request_factory
        self.logout = logout

    def requestAvatar(self, avatarId, mind, *interfaces):
        """
          >>> from ZODB.tests.util import DB
          >>> from zope.app.server.utils import FTPRequestFactory
          >>> creds = credentials.UsernamePassword('bob', '123')
          >>> db = DB()
          >>> request_factory = FTPRequestFactory(db)
          >>> realm = FTPRealm(request_factory)
          >>> print realm.request_factory is request_factory
          True

        Now test this method

          >>> result = realm.requestAvatar(creds, None, ftp.IFTPShell)
          >>> print result[0] is ftp.IFTPShell
          True
          >>> print isinstance(result[1], ZopeFTPShell)
          True

        ZopeFTPShell should contain a PublisherFileSystem istance assigned to
        its fs_access attribute.
          
          >>> from zope.app.server.utils import PublisherFileSystem
          >>> print isinstance(result[1].fs_access, PublisherFileSystem)
          True

        Make sure the PublisherFileSystems credentials are correct.
          
          >>> print result[1].fs_access.credentials[0] == 'bob'
          True
          >>> print result[1].fs_access.credentials[1] == '123'
          True

        This method only supports the ftp.IFTPShell has the interface for
        the avatar.

          >>> from zope.interface import Interface
          >>> realm.requestAvatar(creds, None, Interface)
          Traceback (most recent call last):
          ...
          NotImplementedError: Only IFTPShell interface is supported by this realm.
          >>> db.close()

        """
        if ftp.IFTPShell in interfaces:
            avatar = ZopeFTPShell(avatarId.username, avatarId.password,
                                  self.request_factory)
            avatar.logout = self.logout
            return ftp.IFTPShell, avatar, avatar.logout
        raise NotImplementedError, \
                  "Only IFTPShell interface is supported by this realm."

class FTPFactory(policies.LimitTotalConnectionsFactory):
    protocol = ftp.FTP
    overflowProtocol = ftp.FTPOverflowProtocol
    allowAnonymous = False
    timeOut = 600

    def __init__(self, request_factory):
        """
        The portal performs a simple authentication

          >>> from ZODB.tests.util import DB
          >>> from zope.app.server.utils import FTPRequestFactory
          >>> db = DB()
          >>> request_factory = FTPRequestFactory(db)
          >>> ftpfactory = FTPFactory(request_factory)
          >>> print ftpfactory.portal.realm.request_factory is request_factory
          True

        So the portal initializes ok.

          >>> portal = ftpfactory.portal
          >>> creds = credentials.UsernamePassword('bob', '123')
          >>> deferred = portal.login(creds, None, ftp.IFTPShell)
          >>> result = deferred.result
          >>> print type(result)
          <type 'tuple'>
          >>> db.close()

        The result variable should be the return value of the 'requestAvatar'
        method of the FTPRealm method. This method contains its own test.
        """
        r = FTPRealm(request_factory)
        p = portal.Portal(r)
        p.registerChecker(ZopeSimpleAuthenticatation(),
                          credentials.IUsernamePassword)

        self.portal = p
        self.instances = []

    def buildProtocol(self, addr):
        p = policies.LimitTotalConnectionsFactory.buildProtocol(self, addr)
        if p is not None:
            p.wrappedProtocol.portal = self.portal
            p.wrappedProtocol.timeOut = self.timeOut
        self.instances.append(p.wrappedProtocol)
        return p

    def stopFactory(self):
        # make sure ftp instance's timeouts are set to None
        # to avoid reactor complaints
        [p.setTimeout(None) for p in self.instances if p.timeOut is not None]
        policies.LimitTotalConnectionsFactory.stopFactory(self)
