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
"""Schemas for the 'startup' ZCML Namespace

$Id$
"""
from zope.configuration.fields import GlobalObject, Bool
from zope.interface import Interface
from zope.schema import TextLine, BytesLine, Int


class IBaseStartup(Interface):
    """Interface that specified common attributes of the startup
    directives."""
    
    publication = GlobalObject(
        title=u"Publication",
        description=u"Specifies the Publication component for which this " \
                    u"request is used.",
        required=False)

    request = GlobalObject(
        title=u"Request",
        description=u"Request component that is being instantiated.",
        required=False)


class IRegisterRequestFactoryDirective(IBaseStartup):
    """Register a particular request factory that can be used by a server."""
    
    name = TextLine(
        title=u"Name",
        description=u"Name of the request factory",
        required=True)

    factory = GlobalObject(
        title=u"Factory",
        description=u"If specified, this factory is used to create the" \
                    u"request.",
        required=False)


class IRegisterServerTypeDirective(IBaseStartup):
    """Register a server type."""

    name = TextLine(
        title=u"Name",
        description=u"Name as which the server will be known.",
        required=True)

    factory = GlobalObject(
        title=u"Factory",
        description=u"This factory is used to create the server component.",
        required=True)

    requestFactory = BytesLine(
        title=u"Request Factory",
        description=u"This is the factory id that is used to create the" \
                    u"request.",
        required=True)

    defaultPort = Int(
        title=u"Default Port",
        description=u"Start the server on this port, if no port is specified.",
        required=True)

    logFactory = GlobalObject(
        title=u"Log Factory",
        description=u"This factory is used to create the logging component.",
        required=True)

    defaultVerbose = Bool(
        title=u"Default Verbose",
        description=u"If not specifed, should the server start in verbose" \
                    u"mode.",
        required=True)
