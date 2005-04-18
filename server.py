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
"""Datatype for a <server> section in a Zope 3 configuration file.

This is called by the ZConfig machinery while processing a configuration.

$Id$
"""
import logging

from zope.interface import implements
from zope.app import zapi
from zope.app.server.interfaces import IServerType, ISSLServerType

from twisted.application import internet
from twisted.internet import reactor, interfaces

class SSLNotSupported(Exception):
    ''' '''

def logStartUp(service):
    logging.info('-- %s Server started.\n'
                 '\tHostname: %s\n\tPort: %d' % (
            service.name,
            service.kwargs['interface'] or 'localhost',
            service.args[0]
            ))
    

class ZopeTCPServer(internet.TCPServer):

    def __init__(self, name, *args, **kwargs):
        internet.TCPServer.__init__(self, *args, **kwargs)        
        self.name = name

    def startService(self):
        internet.TCPServer.startService(self)
        logStartUp(self)

class ZopeSSLServer(internet.SSLServer):

    def __init__(self, name, *args, **kwargs):
        internet.SSLServer.__init__(self, *args, **kwargs)        
        self.name = name

    def startService(self):
        internet.SSLServer.startService(self)
        logStartUp(self)
        

class ServerType(object):

    implements(IServerType)

    def __init__(self, factory, defaultPort, defaultIP=''):
        self._factory = factory
        self._defaultPort = defaultPort
        self._defaultIP = defaultIP

    def create(self, name, db, ip=None, port=None, backlog=50):
        'See IServerType'
        if port is None:
            port = self._defaultPort

        if ip is None:
            ip = self._defaultIP

        # Given a database, create a twisted.internet.interfaces.IServerFactory
        factory = self._factory(db)
        return ZopeTCPServer(name, port, factory, interface=ip, backlog=backlog)


class SSLServerType(ServerType):

    implements(IServerType)

    def create(self, name, db, privateKeyPath, certificatePath, tls=False,
               ip=None, port=None, backlog=50):
        'See IServerType'
        if port is None:
            port = self._defaultPort

        if ip is None:
            ip = self._defaultIP

        if not interfaces.IReactorSSL.providedBy(reactor):
            raise SSLNotSupported

        from twisted.internet import ssl
        from OpenSSL import SSL
        if tls:
            method = SSL.TLSv1_METHOD
        else:
            method = SSL.SSLv23_METHOD

        contextFactory = ssl.DefaultOpenSSLContextFactory(
            privateKeyPath, certificatePath, method)

        # Given a database, create a twisted.internet.interfaces.IServerFactory
        factory = self._factory(db)
        return ZopeSSLServer(name, port, factory, contextFactory,
                             interface=ip, backlog=backlog)


class ServerFactory(object):
    """Factory for server objects.

    This object will be created for each ``server``

    The factories are part of the configuration data returned by
    ZConfig.
    """

    def __init__(self, section):
        """Initialize the factory based on a <server> section."""
        self.type = section.type
        self.address = section.address
        self.backlog = section.backlog

    def create(self, database):
        """Return a server based on the server types defined via ZCML."""

        servertype = zapi.getUtility(IServerType, self.type)

        return servertype.create(
            self.type,
            database,
            ip=self.address[0],
            port=self.address[1],
            backlog=self.backlog)


class SSLServerFactory(object):
    """Factory for SSL server objects."""

    def __init__(self, section):
        """Initialize the factory based on a <server> section."""
        self.type = section.type
        self.address = section.address
        self.backlog = section.backlog
        self.privateKeyPath = section.privatekeypath
        self.certificatePath = section.certificatepath
        self.tls = section.tls

    def create(self, database):
        """Return a server based on the server types defined via ZCML."""

        servertype = zapi.getUtility(IServerType, self.type)

        return servertype.create(
            self.type,
            database,
            privateKeyPath = self.privateKeyPath,
            certificatePath = self.certificatePath,
            tls = self.tls,
            ip=self.address[0],
            port=self.address[1],
            backlog=self.backlog,
            )
