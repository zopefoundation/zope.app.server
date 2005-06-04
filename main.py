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
"""Functions that control how the Zope appserver knits itself together.

$Id$
"""
import logging
import os
import sys
import time

from zdaemon import zdoptions

import ZODB.interfaces

import ThreadedAsync

from zope import component, interface

import zope.app.appsetup
import zope.app.appsetup.interfaces
from zope.event import notify
from zope.server.taskthreads import ThreadedTaskDispatcher

CONFIG_FILENAME = "zope.conf"

class ZopeOptions(zdoptions.ZDOptions):

    logsectionname = None

    def default_configfile(self):
        dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir, os.pardir, os.pardir))
        for filename in [CONFIG_FILENAME, CONFIG_FILENAME + ".in"]:
            filename = os.path.join(dir, filename)
            if os.path.isfile(filename):
                return filename
        return None


def main(args=None):
    # Record start times (real time and CPU time)
    t0 = time.time()
    c0 = time.clock()

    setup(load_options(args))

    t1 = time.time()
    c1 = time.clock()
    logging.info("Startup time: %.3f sec real, %.3f sec CPU", t1-t0, c1-c0)

    run()
    sys.exit(0)


def multi_database(database_factories):
    """Set up a multi-database from an iterable of database factories

    Return a sequence of databases, and a mapping of from database name to
    database.

    >>> class DB:
    ...     def __init__(self, number):
    ...         self.number = number
    ...     def __repr__(self):
    ...         return "DB(%s)" % self.number

    >>> class Factory:
    ...     def __init__(self, name, number):
    ...         self.name = name
    ...         self.number = number
    ...     def open(self):
    ...         return DB(self.number)

    >>> s, m = multi_database(
    ...           [Factory(None, 3), Factory('y', 2), Factory('x', 1)])

    >>> list(s)
    [DB(3), DB(2), DB(1)]

    >>> [d.database_name for d in s]
    ['', 'y', 'x']

    >>> [d.databases is m for d in s]
    [True, True, True]

    >>> items = m.items()
    >>> items.sort()
    >>> items
    [('', DB(3)), ('x', DB(1)), ('y', DB(2))]

    Each of the databases is registered as an IDatabase utility:

    >>> [(component.getUtility(ZODB.interfaces.IDatabase, name) is m[name])
    ...  for name in m]
    [True, True, True]
    
    """

    databases = {}
    result = []
    for factory in database_factories:
        name = factory.name or ''
        if name in databases:
            raise ValueError("Duplicate database name: %r" % name)
        db = factory.open()
        db.databases = databases
        db.database_name = name
        databases[name] = db
        # Grrr bug in ZODB. Database doesn't declare that it implements
        # IDatabase.
        if not ZODB.interfaces.IDatabase.providedBy(db):
            interface.directlyProvides(db, ZODB.interfaces.IDatabase)
        component.provideUtility(db, ZODB.interfaces.IDatabase, name)
        result.append(db)

    return result, databases
        

def debug(args=None):
    options = load_options(args)

    zope.app.appsetup.config(options.site_definition)

    db = multi_database(options.databases)[0][0]
    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))
    return db


def run():
    try:
        ThreadedAsync.loop()
    except KeyboardInterrupt:
        # Exit without spewing an exception.
        pass


def load_options(args=None):
    if args is None:
        args = sys.argv[1:]
    options = ZopeOptions()
    options.schemadir = os.path.dirname(os.path.abspath(__file__))
    options.realize(args)
    options = options.configroot

    if options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]
    return options


def setup(options):
    sys.setcheckinterval(options.check_interval)

    options.eventlog()
    options.accesslog()

    zope.app.appsetup.config(options.site_definition)

    db = multi_database(options.databases)[0][0]

    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))

    task_dispatcher = ThreadedTaskDispatcher()
    task_dispatcher.setThreadCount(options.threads)

    for server in options.servers:
        server.create(task_dispatcher, db)

    notify(zope.app.appsetup.interfaces.ProcessStarting())

    return db
