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
from zope.app.server.interfaces import ISimpleRegistry
from zope.interface import implements

ListTypes = (tuple, list)


class ZopeDuplicateRegistryEntryError(Exception):
    """
    This Error is raised when the user tries to add an object with
    a name that already exists in the registry. Therefore,
    overwriting is not allowed.
    """

    def __init__(self, name):
        """Initializes Error"""
        self.name = name

    def __str__(self):
        """Returns string representation of Error"""
        return "The name '%s' is already defined in this registry." \
               %self.name


class ZopeIllegalInterfaceError(Exception):
    """This Error is thrown, when the passed object does not implement
    the specified interface."""

    def __init__(self, name, interface):
        """Initalize Error"""
        self.name = name
        self.interface = interface

    def __str__(self):
        """Returns string representation of Error"""
        return ("The object with name " + self.name + " does not implement "
                "the interface " + self.interface.getName() + ".")


class SimpleRegistry:
    """ """

    implements(ISimpleRegistry)

    def __init__(self, interface):
        """Initialize registry"""
        self.objects = {}
        self.interface = interface

    def _clear(self):
        self.objects.clear()

    def register(self, name, object):
        '''See ISimpleRegistry'''

        if name in self.objects.keys():
            raise ZopeDuplicateRegistryEntryError(name)

        if self.interface.providedBy(object):
            self.objects[name] = object
        else:
            raise ZopeIllegalInterfaceError(name, self.interface)

        return []

    def get(self, name):
        '''See ISimpleRegistry'''
        if name in self.objects.keys():
            return self.objects[name]
        else:
            return None
