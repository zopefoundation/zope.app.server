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

$Id$
"""

import unittest
from zope.interface import Interface
from zope.app.server.simpleregistry import SimpleRegistry, \
     ZopeDuplicateRegistryEntryError, ZopeIllegalInterfaceError
from zope.interface import implements


class I1(Interface):
    pass


class I2(Interface):
    pass


class Object1:
    implements(I1)


class Object2:
    implements(I2)


class Test(unittest.TestCase):


    def testRegister(self):

        registry = SimpleRegistry(I1)
        obj1 = Object1()

        self.assertEqual(registry.objects, {})

        registry.register('obj1', obj1)
        self.assertEqual(registry.objects, {'obj1': obj1})

        registry.register('obj2', obj1)
        self.assertEqual(registry.objects, {'obj1': obj1, 'obj2': obj1})


    def testIllegalInterfaceError(self):

        registry = SimpleRegistry(I1)
        obj2 = Object2()

        self.failUnlessRaises(ZopeIllegalInterfaceError,
                              registry.register, 'obj2', obj2)


    def testDuplicateEntry(self):

        registry = SimpleRegistry(I1)
        obj1 = Object1()
        registry.register('obj1', obj1)

        self.failUnlessRaises(ZopeDuplicateRegistryEntryError,
                              registry.register, 'obj1', obj1)


    def testGet(self):

        registry = SimpleRegistry(I1)
        obj1 = Object1()
        obj2 = Object1()
        registry.objects = {'obj1': obj1, 'obj2': obj2}

        self.assertEqual(registry.get('obj1'), obj1)
        self.assertEqual(registry.get('obj2'), obj2)

        # Requesting an object that does not exist
        self.assertEqual(registry.get('obj3'), None)



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
