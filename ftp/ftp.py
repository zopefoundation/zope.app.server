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
"""This module defines all the FTP shell classes
"""
__docformat__="restructuredtext"

from cStringIO import StringIO
from types import StringTypes

from zope.interface import implements

from twisted.internet import threads, defer
from twisted.protocols import ftp

from utils import PublisherFileSystem

class ConsumerObject(object):
    def __init__(self, fs, name):
        self.fs = fs
        self.name = name
        self.total = 0

    def registerProducer(self, producer, streaming):
        assert streaming

    def unregisterProducer(self):
        pass

    def write(self, bytes):
        ## XXX - this is going to mess up the transaction machinary since
        ## for a big file this method could be called hundreds of times.
        instream = StringIO(bytes)
        self.fs.writefile(self.name, instream, start = self.total)
        self.total += len(bytes)

class ZopeFTPShell(object):
    """An abstraction of the shell commands used by the FTP protocol
    for a given user account
    """
    implements(ftp.IFTPShell)

    def __init__(self, username, password, request_factory):
        self.fs_access = PublisherFileSystem((username, password),
                                             request_factory)

    def _path(self, path):
        return '/' + '/'.join(path)

    def makeDirectory(self, path):
        return threads.deferToThread(self.fs_access.mkdir, self._path(path))

    def removeDirectory(self, path):
        return threads.deferToThread(self.fs_access.rmdir, self._path(path))

    def removeFile(self, path):
        return threads.deferToThread(self.fs_access.remove, self._path(path))

    def rename(self, fromPath, toPath):
        return threads.deferToThread(self.fs_access.rename,
                                     self._path(fromPath),
                                     self._path(toPath))

    def access(self, path):
        def success(result):
            return None
        def failure(result):
            ## XXX - return more appropriate results
            raise ftp.PermissionDeniedError(path)

        ## XXX - is ls the right method to use here - seems a bit slow.
        d = threads.deferToThread(self.fs_access.ls, self._path(path))
        d.addCallback(success)
        d.addErrback(failure)

        return d

    def _gotlisting(self, result, keys = ()):
        ent = []
        for key in keys:
            val = getattr(self, '_list_' + key)(result)
            if isinstance(val, StringTypes):
                ent.append(val.encode('utf-8'))
            else:
                ent.append(val)
        return result['name'].encode('utf-8'), ent

    def _stat(self, path, keys):
        if self.fs_access.type(path) == 'd':
            raise ftp.WrongFileType()
        result = self._gotlisting(self.fs_access.lsinfo(path), keys)
        return result[1]

    def stat(self, path, keys=()):
        return threads.deferToThread(self._stat, self._path(path), keys)

    def list(self, path, keys=()):
        def gotresults(results, keys):
            ret = []
            for result in results:
                ret.append(self._gotlisting(result, keys))
            return ret

        d = threads.deferToThread(self.fs_access.ls, self._path(path))
        d.addCallback(gotresults, keys)

        return d

    def _list_size(self, value):
        return value.get('size', 0)
    def _list_hardlinks(self, value):
        return value.get('nlinks', 1)
    def _list_owner(self, value):
        return value.get('owner_name', 'na')
    def _list_group(self, value):
        return value.get('group_name', 'na')
    def _list_directory(self, value):
        return value['type'] == 'd'
    def _list_modified(self, value):
        mtime = value.get('mtime', None)
        if mtime:
            return int(mtime.strftime('%s'))
        return 0
    def _list_permissions(self, value):
        ret = 0
        if value.get('other_executable', False):
            ret |= 0001
        if value.get('other_writable', False):
            ret |= 0002
        if value.get('other_readable', False):
            ret |= 0004
        if value.get('group_executable', True):
            ret |= 0010
        if value.get('group_writable', True):
            ret |= 0020
        if value.get('group_readable', True):
            ret |= 0040
        if value.get('owner_executable', True):
            ret |= 0100
        if value.get('owner_writable', True):
            ret |= 0200
        if value.get('owner_readable', True):
            ret |= 0400
        if value.get('type', 'f') == 'f':
            ret |= 0100000
        else:
            ret |= 0040000
        return ret

    def send(self, path, consumer):
        def finished(result, consumer):
            consumer.transport.loseConnection()
        def failed(result, path):
            consumer.transport.loseConnection()
            ## XXX - a more appropriate exception here.
            raise ftp.PermissionDeniedError(path)

        p = self._path(path)
        d = threads.deferToThread(self.fs_access.readfile, p, consumer)
        d.addCallback(finished, consumer)
        d.addErrback(failed, consumer, p)
        return d

    def receive(self, path):
        def accessok(result, fs, path):
            if not result:
                raise ftp.PermissionDeniedError(path)
            return ConsumerObject(fs, p)
        def failure(result, path):
            ## XXX - should be a better exception
            raise ftp.PermissionDeniedError(path)
        p = self._path(path)
        d = threads.deferToThread(self.fs_access.writable, p)
        d.addCallback(accessok, self.fs_access, p)
        d.addErrback(failure, p)

        return d
