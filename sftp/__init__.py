##############################################################################
#
# Copyright (c) 2001,2002,2003 Zope Corporation and Contributors.
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
""" SFTP Server Factories.
"""
from zope.app.server.utils import FTPRequestFactory
HAS_CRYPTO = True
try:
    from zope.app.server.server import SSHServerType
    from server import SFTPFactory
except ImportError, e:
    HAS_CRYPTO = False

def createSFTPFactory(db, hostkey):
    """
    note that all SSH factories must contain the extra hostkey arguement.
    """
    request_factory = FTPRequestFactory(db)

    factory = SFTPFactory(request_factory, hostkey = hostkey)

    return factory

if HAS_CRYPTO is True:
    sftpserver = SSHServerType(createSFTPFactory, 8115)
else:
    sftpserver = False
