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
"""
I do not think it is necessary to do the entire SimpleRegistry tests again.
Instead we will test whether the module in itself works.

$Id$
"""

import unittest
from zope.app.server.requestfactoryregistry import \
     registerRequestFactory, getRequestFactory
from zope.app.publication.interfaces import IRequestFactory
from zope.interface import implements


class RequestFactory:
    """RequestFactory Stub."""

    implements(IRequestFactory)


class Test(unittest.TestCase):


    def testRegistry(self):

        factory = RequestFactory()

        registerRequestFactory('factory', factory)
        self.assertEqual(getRequestFactory('factory'), factory)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
