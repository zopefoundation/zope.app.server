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
"""Server Type

$Id$
"""
from zope.interface import Interface, implements


class IServerType(Interface):
    """This is a pure read-only interface, since the values are set through
       a ZCML directive and we shouldn't be able to change them.
    """

    def create(task_dispatcher, db, port=None, verbose=None):
        """Create the server knowing the port, task dispatcher and the ZODB.
        """

class ServerType(object):

    implements(IServerType)

    def __init__(self, factory, requestFactory, logFactory,
                 defaultPort, defaultVerbose):
        self._factory = factory
        self._requestFactory = requestFactory
        self._logFactory = logFactory
        self._defaultPort = defaultPort
        self._defaultVerbose = defaultVerbose


    def create(self, name, task_dispatcher, db, port=None, verbose=None):
        'See IServerType'

        request_factory = self._requestFactory(db)

        if port is None:
            port = self._defaultPort

        if verbose is None:
            verbose = self._defaultVerbose

        self._factory(request_factory, name, '', port,
                      task_dispatcher=task_dispatcher,
                      verbose=verbose,
                      hit_log=self._logFactory(),
                      )
