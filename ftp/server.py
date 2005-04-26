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

from twisted.cred import portal, checkers, credentials
from twisted.protocols import ftp
from twisted.internet import reactor, defer

from zope.publisher.ftp import FTPRequest

from zope.app.server.server import ServerType
from zope.app.publication.ftp import FTPPublication
from zope.app.publication.interfaces import IPublicationRequestFactory

from ftp import ZopeFTPShell

class ZopeSimpleAuthenticatation(object):
    implements(checkers.ICredentialsChecker)

    credentialInterfaces = credentials.IUsernamePassword

    def requestAvatarId(self, credentials):
        """
        see zope.server.ftp.publisher.PublisherFileSystemAccess

        We can't actually do any authentication initially, as the
        user may not be defined at the root.
        """
        # -> the user = username, password so we can authenticate later on.
        return defer.succeed(credentials)

class FTPRealm(object):

    def __init__(self, request_factory, logout = None):
        self.request_factory = request_factory
        self.logout = logout

    def requestAvatar(self, avatarId, mind, *interfaces):
        if ftp.IFTPShell in interfaces:
            avatar = ZopeFTPShell(avatarId.username, avatarId.password,
                                  self.request_factory)
            avatar.logout = self.logout
            return ftp.IFTPShell, avatar, avatar.logout
        raise NotImplementedError, \
                  "Only IFTPShell interface is supported by this realm")

class FTPFactory(ftp.FTPFactory):
    allowAnonymous = False

    def __init__(self, request_factory):
        r = FTPRealm(request_factory)
        p = portal.Portal(r)
        p.registerChecker(ZopeSimpleAuthenticatation(),
                          credentials.IUsernamePassword)

        self.portal = p

class FTPRequestFactory(object):
    """FTP Request factory

    FTP request factories for a given database create FTP requets with
    publications on the given database:
        
      >>> from ZODB.tests.util import DB
      >>> db = DB()
      >>> factory = FTPRequestFactory(db)
      >>> from cStringIO import StringIO
      >>> request = factory(StringIO(''), StringIO(),
      ...                   {'credentials': None, 'path': '/'})
      >>> request.publication.db is db
      True
      >>> db.close()

    """
    implements(IPublicationRequestFactory)

    def __init__(self, db):
        self.publication = FTPPublication(db)

    def __call__(self, input_stream, output_steam, env):
        request = FTPRequest(input_stream, output_steam, env)
        request.setPublication(self.publication)
        return request
