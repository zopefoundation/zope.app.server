##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""This module handles the 'startup' ZCML namespace directives.

$Id$
"""
from zope.app.server import requestfactoryregistry
from zope.app.server import servertyperegistry
from zope.app.server.requestfactory import RequestFactory
from zope.app.server.servertype import ServerType


def registerRequestFactory(_context, name, request=None, publication=None,
                           factory=None):

    if factory:
        if request or publication:
            raise ValuesError(
                """You cannot provide a request or publication (factory) if you
                provide a (request) factory""")
        request_factory = factory

    else:
        request_factory = RequestFactory(publication, request)

    _context.action(
            discriminator = name,
            callable = requestfactoryregistry.registerRequestFactory,
            args = (name, request_factory,) )


def registerServerType(_context, name, factory, requestFactory, logFactory,
                       defaultPort, defaultVerbose):

    server_type = ServerType(name, factory, requestFactory, logFactory,
                             defaultPort, defaultVerbose)

    _context.action(
            discriminator = name,
            callable = servertyperegistry.registerServerType,
            args = (name, server_type) )
