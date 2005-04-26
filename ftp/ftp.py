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

## cStringIO is causing me problems with unicode charactors.
from cStringIO import StringIO
import posixpath
from datetime import date, timedelta

from zope.interface import implements

from twisted.protocols import ftp

from zope.app.server.ftp.publisher import PublisherFileSystem

def ls(ls_info):
    """Formats a directory entry similarly to the 'ls' command.
    """

    info = {
        'owner_name': 'na',
        'owner_readable': True,
        'owner_writable': True,
        'group_name': "na",
        'group_readable': True,
        'group_writable': True,
        'other_readable': False,
        'other_writable': False,
        'nlinks': 1,
        'size': 0,
        }

    if ls_info['type'] == 'd':
        info['owner_executable'] = True
        info['group_executable'] = True
        info['other_executable'] = True
    else:
        info['owner_executable'] = False
        info['group_executable'] = False
        info['other_executable'] = False

    info.update(ls_info)

    mtime = info.get('mtime')
    if mtime is not None:
        if date.today() - mtime.date() > timedelta(days=180):
            mtime = mtime.strftime('%b %d  %Y')
        else:
            mtime = mtime.strftime('%b %d %H:%M')
    else:
        mtime = "Jan 02  0000"

    return "%s%s%s%s%s%s%s%s%s%s %3d %-8s %-8s %8d %s %s" % (
        info['type'] == 'd' and 'd' or '-',
        info['owner_readable'] and 'r' or '-',
        info['owner_writable'] and 'w' or '-',
        info['owner_executable'] and 'x' or '-',
        info['group_readable'] and 'r' or '-',
        info['group_writable'] and 'w' or '-',
        info['group_executable'] and 'x' or '-',
        info['other_readable'] and 'r' or '-',
        info['other_writable'] and 'w' or '-',
        info['other_executable'] and 'x' or '-',
        info['nlinks'],
        info['owner_name'],
        info['group_name'],
        info['size'],
        mtime,
        info['name'],
        )

## this should correspond to zope.server.ftp.server.FTPServerChannel
class ZopeFTPShell(object):
    """An abstraction of the shell commands used by the FTP protocol
    for a given user account
    """
    implements(ftp.IFTPShell)

    def __init__(self, username, password, request_factory):
        self.fs_access = PublisherFileSystem((username, password),
                                             request_factory)
        self._dir = '/'

    def mapCPathToSPath(self, path):
        if not path or path[0] != '/':
            path = posixpath.join(self._dir, path)

        path = posixpath.normpath(path)
        if path.startswith('..'):
            path = '/'

        return path, path

    def pwd(self):
        return self._dir

    def cwd(self, path):
        dummy, path = self.mapCPathToSPath(path)

        if self.fs_access.type(path) is None:
            raise ftp.FileNotFoundError(path)

        if self.fs_access.type(path) == 'd':
            self._dir = path
        else:
            raise ftp.FileNotFoundError(path)

    def cdup(self):
        self.cwd('..')

    def size(self, path):
        dummy, path = self.mapCPathToSPath(path)

        fs = self.fs_access
        if fs.type(path) != 'f':
            raise ftp.FileNotFoundError(path)
        return fs.size(path)

    def _generatePath(self, args):
        """Convert relative paths to absolute paths."""
        # We use posixpath even on non-Posix platforms because we don't want
        # slashes converted to backslashes.
        path = posixpath.join(self._dir, args)
        return posixpath.normpath(path)

    def mkd(self, path):
        if not path:
            raise ftp.CmdSyntaxError('Bad command arguments.')
        path = self._generatePath(path)
        try:
            self.fs_access.mkdir(path)
        except OSError, err:
            raise ftp.CmdActionNotTaken('creating directory %s' % path)

    def rmd(self, path):
        if not path:
            raise ftp.CmdSyntaxError('Bad command arguments.')
        path = self._generatePath(path)
        try:
            self.fs_access.rmdir(path)
        except OSError, err:
            raise ftp.CmdActionNotTaken('deleting directory %s' % path)

    def dele(self, path):
        if not path:
            raise ftp.CmdSyntaxError('Bad command arguments.')
        path = self._generatePath(path)

        try:
            self.fs_access.remove(path)
        except OSError, err:
            raise ftp.CmdOpenReadError(path)

    def getList(self, args, long=0, directory=0):
        # we need to scan the command line for arguments to '/bin/ls'...
        ## fs = self._getFileSystem()
        fs = self.fs_access
        path_args = []
        for arg in args:
            if arg[0] != '-':
                path_args.append (arg)
            else:
                # ignore arguments
                pass
        if len(path_args) < 1:
            path = '.'
        else:
            path = path_args[0]

        path = self._generatePath(path)

        if fs.type(path) == 'd' and not directory:
            if long:
                file_list = map(ls, fs.ls(path))
            else:
                file_list = fs.names(path)
        else:
            if long:
                file_list = [ls(fs.lsinfo(path))]
            else:
                file_list = [posixpath.split(path)[1]]

        return '\r\n'.join(file_list) + '\r\n'

    def _list(self, path, long = 1, directory = False, *args):
        path = self._generatePath(path)

        dummy, path = self.mapCPathToSPath(path)

        if not self.fs_access.type(path):
            raise ftp.FileNotFoundError(path)

        s = self.getList(args, long, directory)

        return StringIO(str(s)), len(s)

    def list(self, path):
        return self._list(path)

    def nlst(self, path):
        return self._list(path, long = 0)

    def retr(self, path):
        fs = self.fs_access
        if not path:
            raise ftp.CmdSyntaxError('Bad command arguments.')
        path = self._generatePath(path)

        if not (fs.type(path) == 'f'):
            raise ftp.FileNotFoundError(path)

##         start = 0
##         if self.restart_position:
##             start = self.restart_position
##             self.restart_position = 0

##         ok_reply = 'OPEN_CONN', (self.type_map[self.transfer_mode], path)
##         cdc = RETRChannel(self, ok_reply)
##         outstream = ApplicationOutputStream(cdc)

        start = 0
        outstream = StringIO()

        try:
            fs.readfile(path, outstream, start)
        except OSError, err:
            raise ftp.CmdOpenReadError(path)

        l = len(outstream.getvalue())
        outstream.seek(0)

        return outstream, l

##         try:
##             fs.readfile(path, outstream, start)
##             cdc.close_when_done()
##         except OSError, err:
##             self.reply('ERR_OPEN_READ', str(err))
##             cdc.reported = True
##             cdc.close_when_done()
##         except IOError, err:
##             self.reply('ERR_IO', str(err))
##             cdc.reported = True
##             cdc.close_when_done()


    def stor(self, params):
        """This command causes the server-DTP to accept the data
        transferred via the data connection and to store the data as
        a file at the server site.  If the file specified in the
        pathname exists at the server site, then its contents shall
        be replaced by the data being transferred.  A new file is
        created at the server site if the file specified in the
        pathname does not already exist.
        """
        if not params:
            raise ftp.CmdSyntaxError('Bad command arguments.')
        path = self._generatePath(params)

##         start = 0
##         if self.restart_position:
##             self.start = self.restart_position
##         mode = write_mode + self.type_mode_map[self.transfer_mode]

        if not self.fs_access.writable(path):
##             self.reply('ERR_OPEN_WRITE', "Can't write file")
##             return
            raise ftp.CmdOpenWriteError(path)

##         cdc = STORChannel(self, (path, mode, start))
##         self.syncConnectData(cdc)
##         self.reply('OPEN_CONN', (self.type_map[self.transfer_mode], path))

    def writefile(self, path, data):
        """
        this is not in IFTPShell but needed to upload the data into Zope.
        """
        path = self._generatePath(path)

        try:
            self.fs_access.writefile(path, data)
        except OSError, err:
            raise ftp.CmdFileActionError()

    def mdtm(self, args):
        fs = self.fs_access
        # We simply do not understand this non-standard extension to MDTM
        if len(args.split()) > 1:
            raise ftp.CmdSyntaxError('Bad command arguments.')
        path = self._generatePath(args)
        
        if fs.type(path) != 'f':
            raise ftp.FileNotFoundError(path)
        else:
            mtime = fs.mtime(path)
            return mtime.strftime('%Y%m%d%H%M%S')
