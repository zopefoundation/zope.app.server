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
"""Tests for zope.app.server.servertype

$Id$
"""
import logging
import unittest
import cStringIO
from zope.testing import doctest, doctestunit
from zope.app.testing import setup

handler = None

def setUp(test):
    setup.placelessSetUp()
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log = cStringIO.StringIO()
    global handler
    handler = logging.StreamHandler(log)
    logger.addHandler(handler)

    test.globs['log'] = log


def tearDown(test):
    setup.placelessTearDown()

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logger.handlers.remove(handler)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
                             setUp=setUp, tearDown=tearDown,
                             globs={'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite('../log.txt',
                             globs={'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        doctest.DocTestSuite('zope.app.server.ftp.utils')
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
