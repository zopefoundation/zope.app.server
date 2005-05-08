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
""" Implementation of the ISFTPServer ssh file transfer protocol for Zope.
"""

import posixpath, os, stat, array, datetime
from cStringIO import StringIO

from zope.interface import implements

from twisted.conch.interfaces import ISFTPServer, ISFTPFile
from twisted.conch.ssh.filetransfer import FXF_APPEND, FXF_READ

class SFTPServerForZope(object):
    implements(ISFTPServer)

    def __init__(self, avatar):
        self.avatar = avatar

    def gotVersion(self, otherVersion, extData):
        return {}

    def openFile(self, filename, flags, attrs):
        fp = ZopeSFTPFile(self, self._generatePath(filename), flags, attrs)

        return fp

    def removeFile(self, filename):
        self.avatar.fs_access.remove(self._generatePath(filename))

    def renameFile(self, oldpath, newpath):
        oldpath = self._generatePath(oldpath)
        newpath = self._generatePath(newpath)
        self.avatar.fs_access.rename(oldpath, newpath)

    def makeDirectory(self, path, attrs):
        self.avatar.fs_access.mkdir(self._generatePath(path))

    def removeDirectory(self, path):
        self.avatar.fs_access.rmdir(self._generatePath(path))

    def openDirectory(self, path):
        return ZopeSFTPDirectory(self, self._generatePath(path))

    def getAttrs(self, path, followLinks):
        fp = ZopeSFTPFile(self, self._generatePath(path), FXF_READ, {})

        return fp.getAttrs()

    def setAttrs(self, path, attrs):
        pass

    def readLink(self, path):
        raise NotImplementedError, "readLink not implemented."

    def makeLink(self, linkPath, targetPath):
        raise NotImplementedError, "makeLink not implemented."

    def realPath(self, path):
        return self._generatePath(path)

    def extendedRequest(self, extendedName, extendedData):
        raise NotImplementedError, \
              "Zope doesn't support any SFTP extensions."

    def _generatePath(self, args):
        path = posixpath.join('/', args)
        return posixpath.normpath(path)


class ZopeSFTPDirectory(object):

    def __init__(self, server, directory):
        self.server = server
        self.dir    = directory
        self.files  = self.server.avatar.fs_access.names(directory)

    def __iter__(self):
        return self

    def next(self):
        try:
            f = self.files.pop(0)
        except IndexError:
            raise StopIteration
        else:
            file = ZopeSFTPFile(self.server, posixpath.join(self.dir, f),
                                FXF_READ, {})
            s = file.getAttrs()
            longname = _lsLine(f, s)
            return (str(f), str(longname), s)

    def close(self):
        self.files = []


class ZopeSFTPFile(object):
    implements(ISFTPFile)

    def __init__(self, server, filename, flags, attrs):
        self.server   = server
        self.filename = filename
        self.attrs    = attrs

        if flags & FXF_APPEND == FXF_APPEND:
            self.append = True
        else:
            self.append = False

    def close(self):
        pass

    def readChunk(self, offset, length):
        outstream = StringIO()
        self.server.avatar.fs_access.readfile(self.filename,
                                              outstream,
                                              start = offset,
                                              end   = offset + length)
        chunk = outstream.getvalue()
        outstream.close()

        return chunk

    def writeChunk(self, offset, data):
        instream = StringIO(data)
        self.server.avatar.fs_access.writefile(self.filename,
                                               instream,
                                               start = offset,
                                               end   = offset + len(data),
                                               append = self.append)
        instream.close()

    def getAttrs(self):
        attrs = self.server.avatar.fs_access.lsinfo(self.filename)

        retattrs = {}
        retattrs['size'] = attrs.get('size', 0)
        ## uid
        ## gid
        ## permissions
        permissions = 0
        def _isKeyTrue(key):
            return attrs.has_key(key) and attrs[key] is True
        if _isKeyTrue('owner_readable'):
            permissions |= stat.S_IRUSR
        if _isKeyTrue('owner_writable'):
            permissions |= stat.S_IWUSR
        if _isKeyTrue('owner_executable'):
            permissions |= stat.S_IXUSR
        if _isKeyTrue('group_readable'):
            permissions |= stat.S_IRGRP
        if _isKeyTrue('group_writable'):
            permissions |= stat.S_IWGRP
        if _isKeyTrue('group_executable'):
            permissions |= stat.S_IXGRP
        if _isKeyTrue('other_readable'):
            permissions |= stat.S_IROTH
        if _isKeyTrue('other_writable'):
            permissions |= stat.S_IWOTH
        if _isKeyTrue('other_executable'):
            permissions |= stat.S_IXOTH
        filetype = self.server.avatar.fs_access.type(self.filename)
        if filetype == 'd':
            permissions |= stat.S_IFDIR
        elif filetype == 'f':
            permissions |= stat.S_IFREG
        retattrs['permissions'] = permissions
        ## atime
        if attrs['mtime'] is not None:
            retattrs['mtime'] = attrs['mtime']
        return retattrs

    def setAttrs(self, attrs):
        ## IFileSystem doesn't currently support the setting of attributes.
        pass

## modified from twisted.consh.unix._lsLine
def _lsLine(name, s):
    ## mode = s.st_mode
    mode = s['permissions']
    perms = array.array('c', '-'*10)
    ft = stat.S_IFMT(mode)
    if stat.S_ISDIR(ft): perms[0] = 'd'
    elif stat.S_ISCHR(ft): perms[0] = 'c'
    elif stat.S_ISBLK(ft): perms[0] = 'b'
    elif stat.S_ISREG(ft): perms[0] = '-'
    elif stat.S_ISFIFO(ft): perms[0] = 'f'
    elif stat.S_ISLNK(ft): perms[0] = 'l'
    elif stat.S_ISSOCK(ft): perms[0] = 's'
    else: perms[0] = '!'
    # user
    if mode&stat.S_IRUSR:perms[1] = 'r'
    if mode&stat.S_IWUSR:perms[2] = 'w'
    if mode&stat.S_IXUSR:perms[3] = 'x'
    # group
    if mode&stat.S_IRGRP:perms[4] = 'r'
    if mode&stat.S_IWGRP:perms[5] = 'w'
    if mode&stat.S_IXGRP:perms[6] = 'x'
    # other
    if mode&stat.S_IROTH:perms[7] = 'r'
    if mode&stat.S_IWOTH:perms[8] = 'w'
    if mode&stat.S_IXOTH:perms[9] = 'x'
    # suid/sgid
    if mode&stat.S_ISUID:
        if perms[3] == 'x': perms[3] = 's'
        else: perms[3] = 'S'
    if mode&stat.S_ISGID:
        if perms[6] == 'x': perms[6] = 's'
        else: perms[6] = 'S'
    l = perms.tostring()
    ## l += str(s.st_nlink).rjust(5) + ' '
    l += str(0).rjust(5) + ' '
    ## un = str(s.st_uid)
    un = s.get('owner_name', 'na')
    l += un.ljust(9)
    ## gr = str(s.st_gid)
    gr = s.get('group_name', 'na')
    l += gr.ljust(9)
    ## sz = str(s.st_size)
    sz = str(s.get('size', 0))
    l += sz.rjust(8)
    l += ' '
    ## sixmo = 60 * 60 * 24 * 7 * 26
    sixmo = datetime.timedelta(days = 26 * 7) # six months time delta object
    ## if s.st_mtime + sixmo < time.time(): # last edited more than 6mo ago
    mtime = s['mtime']
    if (mtime + sixmo).date() < datetime.datetime.now().date():
        ## l += time.strftime("%b %2d  %Y ", time.localtime(s.st_mtime))
        l += mtime.strftime("%b %2d  %Y ") ## , time.localtime(mtime))
    else:
        ## l += time.strftime("%b %2d %H:%S ", time.localtime(s.st_mtime))
        l += mtime.strftime("%b %2d %H:%S ") ## , time.localtime(mtime))
    l += name
    return l
