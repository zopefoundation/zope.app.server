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
"""FTP server

$Id$
"""
from zope.app.publication.ftp import FTPPublication
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.publisher.ftp import FTPRequest
from zope.server.ftp.logger import CommonFTPActivityLogger
from zope.server.ftp.publisher import PublisherFTPServer
from zope.app.server.servertype import ServerType
import zope.interface

class FTPRequestFactory(object):
    """FTP Request factory

    FTP request factories for a given resource factory create FTP requests with
    publications on the given resource factory:

      >>> from zope.app.publication.interfaces import IResourceFactory
      >>> class Stub:
      ...     zope.interface.implements(IResourceFactory)
      >>> stub = Stub()
      >>> factory = FTPRequestFactory(stub)
      >>> from cStringIO import StringIO
      >>> request = factory(StringIO(''), {'credentials': None, 'path': '/'})
      >>> request.publication.resource_factory is stub
      True

    """
    zope.interface.implements(IPublicationRequestFactory)

    def __init__(self, resource_factory):
        self.publication = FTPPublication(resource_factory)

    def __call__(self, input_stream, env):
        request = FTPRequest(input_stream, env)
        request.setPublication(self.publication)
        return request

server = ServerType(
    PublisherFTPServer,
    FTPRequestFactory,
    CommonFTPActivityLogger,
    8021, True)
