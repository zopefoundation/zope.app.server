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
"""e.py,v 1.1.2.2 2002/04/02 02:20:40 srichter Exp $
"""

from zope.interface import Interface, implements
from zope.app.server.requestfactoryregistry import getRequestFactory


class IServerType(Interface):
    """This is a pure read-only interface, since the values are set through
       a ZCML directive and we shouldn't be able to change them.
    """

    def create(task_dispatcher, db, port=None, verbose=None):
        """Create the server knowing the port, task dispatcher and the ZODB.
        """

class ServerType:

    implements(IServerType)

    def __init__(self, name, factory, requestFactory, logFactory,
                 defaultPort, defaultVerbose):
        """ """
        self._name = name
        self._factory = factory
        self._requestFactory = requestFactory
        self._logFactory = logFactory
        self._defaultPort = defaultPort
        self._defaultVerbose = defaultVerbose


    def create(self, task_dispatcher, db, port=None, verbose=None):
        'See IServerType'

        request_factory = getRequestFactory(self._requestFactory)
        request_factory = request_factory.realize(db)

        if port is None:
            port = self._defaultPort

        if verbose is None:
            verbose = self._defaultVerbose

        apply(self._factory,
              (request_factory, self._name, '', port),
              {'task_dispatcher': task_dispatcher,
               'verbose': verbose,
               'hit_log': self._logFactory()})
