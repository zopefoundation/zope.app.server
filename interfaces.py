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
"""Interfaces for the zope.app.server package.

$Id$
"""

from zope.interface import Interface

class ISimpleRegistry(Interface):
    """
    The Simple Registry is minimal collection of registered objects. This can
    be useful, when it is expected that objects of a particular type are added
    from many places in the system (through 3rd party products for example).

    A good example for this are the Formulator fields. While the basic types
    are defined inside the Formulator tree, other parties might add many
    more later on in their products, so it is useful to provide a registry via
    ZCML that allows to collect these items.

    There is only one constraint on the objects. They all must implement a
    particular interface specified during the initialization of the registry.

    Note that it does not matter whether we have classes or instances as
    objects. If the objects are instances, they must implement simply
    IInstanceFactory.
    """

    def register(name, object):
        """Registers the object under the id name."""

    def getF(name):
        """This returns the object with id name."""
