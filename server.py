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
from zope.app import zapi
from zope.app.server.servertype import IServerType

class ServerFactory(object):
    """Factory for server objects.

    The factories are part of the configuration data returned by
    ZConfig.
    """

    def __init__(self, section):
        """Initialize the factory based on a <server> section."""
        self.type = section.type
        self.address = section.address
        self.verbose = section.verbose

    def create(self, task_dispatcher, database):
        """Return a server based on the server types defined via ZCML."""

        servertype = zapi.getUtility(IServerType, self.type)
        # The server object self-registers with the asyncore mainloop.
        servertype.create(
            self.type,
            task_dispatcher, database,
            self.address[1],
            self.verbose)
