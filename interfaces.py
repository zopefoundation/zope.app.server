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
"""Server Setup Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
from zope.interface import Interface

class IServerType(Interface):
    """Server Type utility.

    A utility that the can create a server instance.

    This is a pure read-only interface, since the values are set through
    a ZCML directive and we shouldn't be able to change them.
    """

    def create(name, db, ip=None, port=None, backlog=50):
        """Create the server knowing the port, IP address and the ZODB.

        Returns the new server.
        """

class ISSLServerType(IServerType):
    """SSL Server Type utility"""
    
    def create(name, db, privateKeyPath, certificatePath, tls=False,
               ip=None, port=None, backlog=50):
        """Create an SSL server instance.

        This differs only in respect to that it needs the private key path,
        certificate key path and TLS flag to instantiate the server.
        """
