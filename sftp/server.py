##############################################################################
#
# Copyright (c) 2001,2002,2003 Zope Corporation and Contributors.
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
""" Twisted specific integration classes for SFTP.
"""
from zope.interface import implements

from zope.app.server.utils import ZopeSimpleAuthenticatation
from zope.app.server.utils import PublisherFileSystem
from zope.app.server.interfaces import IFileSystem

from twisted.cred.portal import IRealm, Portal
from twisted.cred.credentials import IUsernamePassword

from twisted.conch.ssh.filetransfer import FileTransferServer
from twisted.conch.ssh.connection import SSHConnection
from twisted.conch.ssh.session import SSHSession
from twisted.conch.ssh.common import getNS
from twisted.conch.ssh.forwarding import openConnectForwardingClient
try:
    from twisted.conch.ssh.factory import SSHFactory
    from twisted.conch.ssh.userauth import SSHUserAuthServer
    from twisted.conch.ssh.keys import getPublicKeyString, \
         getPrivateKeyObject, objectType
except ImportError, e:
    SSHFactory = object
    SSHUserAuthServer = None
    getPublicKeyString = getPrivateKeyObject = objectType = None
from twisted.conch.avatar import ConchUser
from twisted.conch.interfaces import IConchUser


class ZopeAvatar(ConchUser):
    implements(IConchUser)
    
    def __init__(self, fs_access):
        ConchUser.__init__(self)

        assert IFileSystem.providedBy(fs_access), "Invalid File Publisher"
        self.fs_access = fs_access

        self.channelLookup.update(
            {'session': SSHSession,
             'direct-tcpip': openConnectForwardingClient})

        self.subsystemLookup.update(
            {'sftp': FileTransferServer})


class SFTPRealm(object):
    implements(IRealm)

    def __init__(self, request_factory):
        self.request_factory = request_factory

    def requestAvatar(self, avatarId, mind, *interfaces):
        """
          >>> from zope.app.server.utils import FTPRequestFactory
          >>> from ZODB.tests.util import DB
          >>> from twisted.cred import credentials
          >>> creds = credentials.UsernamePassword('bob', '123')
          >>> db = DB()
          >>> request_factory = FTPRequestFactory(db)
          >>> realm = SFTPRealm(request_factory)
          >>> print realm.request_factory is request_factory
          True

        Now test this method

          >>> result = realm.requestAvatar(creds, None, IConchUser)
          >>> print result[0] is IConchUser
          True
          >>> print isinstance(result[1], ZopeAvatar)
          True

        ZopeAvatar should contain a PublisherFileSystem instance assigned to
        its fs_access attribute.
          
          >>> from zope.app.server.utils import PublisherFileSystem
          >>> print isinstance(result[1].fs_access, PublisherFileSystem)
          True

        Make sure the PublisherFileSystems credentials are correct.
          
          >>> print result[1].fs_access.credentials[0] == 'bob'
          True
          >>> print result[1].fs_access.credentials[1] == '123'
          True

        This method only supports the IConchUser has the interface for
        the avatar.

          >>> from zope.interface import Interface
          >>> realm.requestAvatar(creds, None, Interface)
          Traceback (most recent call last):
          ...
          NotImplementedError: Only IConchUser interface is supported by this realm.
          >>> db.close()

        """
        if IConchUser in interfaces:
            fs_access = PublisherFileSystem(
                (avatarId.username, avatarId.password),
                self.request_factory)
            avatar = ZopeAvatar(fs_access)
            return IConchUser, avatar, lambda : None
        raise NotImplementedError, \
              "Only IConchUser interface is supported by this realm."


class SFTPFactory(SSHFactory):
    services = {
        'ssh-userauth': SSHUserAuthServer,
        'ssh-connection': SSHConnection
        }

    def getPublicKeys(self):
        ks = {}
        k = getPublicKeyString(self.hostkey + '.pub')
        t = getNS(k)[0]
        ks[t] = k
        return ks

    def getPrivateKeys(self):
        ks = {}
        k = getPrivateKeyObject(self.hostkey)
        t = objectType(k)
        ks[t] = k
        return ks

    def getPrimes(self):
        return None

    def __init__(self, request_factory, hostkey):
        """
        The portal performs a simple authentication

          >>> from ZODB.tests.util import DB
          >>> from zope.app.server.utils import FTPRequestFactory
          >>> db = DB()
          >>> request_factory = FTPRequestFactory(db)
          >>> sftpfactory = SFTPFactory(request_factory, hostkey = None)
          >>> print sftpfactory.portal.realm.request_factory is request_factory
          True

        So the portal initializes ok.
          
          >>> from twisted.cred import credentials
          >>> portal = sftpfactory.portal
          >>> creds = credentials.UsernamePassword('bob', '123')
          >>> deferred = portal.login(creds, None, IConchUser)
          >>> result = deferred.result
          >>> print type(result)
          <type 'tuple'>
          >>> db.close()

        The result variable should be the return value of the 'requestAvatar' method
        of the SFTPRealm method. This method contains its own test.
        """
        self.hostkey = hostkey
        
        r = SFTPRealm(request_factory)
        p = Portal(r)

        p.registerChecker(ZopeSimpleAuthenticatation(),
                          IUsernamePassword)
        self.portal = p
