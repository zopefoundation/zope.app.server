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
"""HTTP server factories

$Id$
"""

from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.server.servertype import ServerType
from zope.server.http.commonaccesslogger import CommonAccessLogger
from zope.server.http.publisherhttpserver import PMDBHTTPServer
from zope.server.http.publisherhttpserver import PublisherHTTPServer

http = ServerType(PublisherHTTPServer,
                  HTTPPublicationRequestFactory,
                  CommonAccessLogger,
                  8080, True)

pmhttp = ServerType(PMDBHTTPServer,
                    HTTPPublicationRequestFactory,
                    CommonAccessLogger,
                    8013, True)
