##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Tests for zope.app.server.server

$Id$
"""
import unittest

from zope.interface.verify import verifyObject
from zope.testing import doctest
from zope.app.testing import ztapi, setup, placelesssetup


def doctest_ServerFactory():
    r"""Tests for ServerFactory

    Zope 3 has many server types -- HTTP, FTP, HTTP with postmortem debugging,
    etc.  All of them are registered as IServerType utilities in ZCML.

        >>> setup.placelessSetUp()

        >>> from zope.interface import implements
        >>> from zope.app.server.servertype import IServerType
        >>> class MyServerType:
        ...     implements(IServerType)
        ...     def create(self, name, task_dispatcher, resource_factory,
        ...                port='unknown', verbose='unspecified', ip=''):
        ...         if not ip:
        ...             ip = '*' # listen on all interfaces
        ...         return ('%s server on %s:%d, registered with %s,\n'
        ...                 'serving from %s, verbosity %s'
        ...                 % (name, ip, port, task_dispatcher, resource_factory, verbose))
        >>> ztapi.provideUtility(IServerType, MyServerType(), name='HTTP')
        >>> ztapi.provideUtility(IServerType, MyServerType(), name='FTP')

    ServerFactory is used to hook into ZConfig and create instances of servers
    specified in zope.conf.  It gets a `section` argument that contains
    settings specified in a ZConfig <server> section.

        >>> class ServerSectionStub:
        ...     type = 'HTTP'
        ...     address = ('', 8080)
        ...     verbose = False
        >>> my_section = ServerSectionStub()

        >>> from zope.app.server.server import ServerFactory
        >>> sf = ServerFactory(my_section)

    The server factory object knows how to create a server, given a task
    dispatcher (see IDispatcher from zope.server.interfaces) and a ZODB
    database object.

        >>> task_dispatcher = 'my task dispatcher'
        >>> resource_factory = 'my resource factory'
        >>> print sf.create(task_dispatcher, resource_factory)
        HTTP server on *:8080, registered with my task dispatcher,
        serving from my resource factory, verbosity False

    The settings actually work

        >>> my_section.type = 'FTP'
        >>> my_section.address = ('127.0.0.1', 8021)
        >>> my_section.verbose = True
        >>> sf = ServerFactory(my_section)
        >>> print sf.create(task_dispatcher, resource_factory)
        FTP server on 127.0.0.1:8021, registered with my task dispatcher,
        serving from my resource factory, verbosity True

    That's it.

        >>> setup.placelessTearDown()

    """


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
