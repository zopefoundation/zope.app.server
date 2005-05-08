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

class ISSHServerType(IServerType):
    """SSH Server Type utility"""

    def create(name, db, hostkey, ip = None, port = None, backlog = 50):
        """Create a SSH server instance.

        This differs only in respect to that it needs the host key path.
        """

## this is going here since I need it for FTP and SFTP.
class IFileSystem(Interface):
    """An abstract filesystem.

       Opening files for reading, and listing directories, should
       return a producer.

       All paths are POSIX paths, even when run on Windows,
       which mainly means that FS implementations always expect forward
       slashes, and filenames are case-sensitive.

       `IFileSystem`, in generel, could be created many times per
       request. Thus it is not advisable to store state in them. However, if
       you have a special kind of `IFileSystemAccess` object that somhow
       manages an `IFileSystem` for each set of credentials, then it would be
       possible to store some state on this obejct. 
    """

    def type(path):
        """Return the file type at `path`.

        The return valie is 'd', for a directory, 'f', for a file, and
        None if there is no file at `path`.

        This method doesn't raise exceptions.
        """

    def names(path, filter=None):
        """Return a sequence of the names in a directory.

        If `filter` is not None, include only those names for which
        `filter` returns a true value.
        """

    def ls(path, filter=None):
        """Return a sequence of information objects.

        Returm item info objects (see the ls_info operation) for the files
        in a directory.

        If `filter` is not None, include only those names for which
        `filter` returns a true value.
        """

    def readfile(path, outstream, start=0, end=None):
        """Outputs the file at `path` to a stream.

        Data are copied starting from `start`.  If `end` is not None,
        data are copied up to `end`.

        """

    def lsinfo(path):
        """Return information for a unix-style ls listing for `path`.

        Information is returned as a dictionary containing the following keys:

        type

           The path type, either 'd' or 'f'.

        owner_name

           Defaults to "na".  Must not include spaces.

        owner_readable

           Defaults to True.

        owner_writable

           Defaults to True.

        owner_executable

           Defaults to True for directories and False otherwise.

        group_name

           Defaults to "na".  Must not include spaces.

        group_readable

           Defaults to True.

        group_writable

           Defaults to True.

        group_executable

           Defaults to True for directories and False otherwise.

        other_readable

           Defaults to False.

        other_writable

           Defaults to False.

        other_executable

           Defaults to True for directories and false otherwise.

        mtime

           Optional time, as a datetime.datetime object.

        nlinks

           The number of links. Defaults to 1.

        size

           The file size.  Defaults to 0.

        name

           The file name.
        """

    def mtime(path):
        """Return the modification time for the file at `path`.

        This method returns the modification time. It is assumed that the path
        exists. You can use the `type(path)` method to determine whether
        `path` points to a valid file.

        If the modification time is unknown, then return `None`.
        """

    def size(path):
        """Return the size of the file at path.

        This method returns the modification time. It is assumed that the path
        exists. You can use the `type(path)` method to determine whether
        `path` points to a valid file.
        """

    def mkdir(path):
        """Create a directory.

        If it is not possible or allowed to create the directory, an `OSError`
        should be raised describing the reason of failure. 
        """

    def remove(path):
        """Remove a file.  Same as unlink.

        If it is not possible or allowed to remove the file, an `OSError`
        should be raised describing the reason of failure. 
        """

    def rmdir(path):
        """Remove a directory.

        If it is not possible or allowed to remove the directory, an `OSError`
        should be raised describing the reason of failure. 
        """

    def rename(old, new):
        """Rename a file or directory."""

    def writefile(path, instream, start=None, end=None, append=False):
        """Write data to a file.

        Both `start` and `end` must be either None or a non-negative
        integer.

        If `append` is true, `start` and `end` are ignored.

        If `start` or `end` is not None, they specify the part of the
        file that is to be written.

        If `end` is None, the file is truncated after the data are
        written.  If `end` is not None, any parts of the file after
        `end` are left unchanged.

        Note that if `end` is not `None`, and there is not enough data
        in the `instream` it will fill the file up to `end`, then the missing
        data are undefined.

        If both `start` is `None` and `end` is `None`, then the file contents
        are overwritten.

        If `start` is specified and the file doesn't exist or is shorter
        than `start`, the data in the file before `start` file will be
        undefined.

        If you do not want to handle incorrect starting and ending indices,
        you can also raise an `IOError`, which will be properly handled by the
        server.
        """

    def writable(path):
        """Return boolean indicating whether a file at path is writable.

        Note that a true value should be returned if the file doesn't
        exist but its directory is writable.

        """
