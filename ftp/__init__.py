##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""FTP and SFTP server factories.
"""

from zope.app.server.server import ServerType
from zope.app.server.ftp.server import FTPFactory
from zope.app.server.server import SSHServerType

from utils import FTPRequestFactory
from sftpserver import SFTPFactory

def createFTPFactory(db):
    request_factory = FTPRequestFactory(db)

    factory = FTPFactory(request_factory)

    return factory

ftpserver = ServerType(createFTPFactory, 8021)


def createSFTPFactory(db, hostkey):
    """
    Note that all SSH factories must contain the extra hostkey arguement.
    """
    request_factory = FTPRequestFactory(db)

    factory = SFTPFactory(request_factory, hostkey = hostkey)

    return factory

sftpserver = SSHServerType(createSFTPFactory, 8115)
