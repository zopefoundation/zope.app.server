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
"""Implementation of the mkzopeinstance script.

This creates a new instances of the Zope server instance home.  An
'instance home' contains two things:

- application server configuration and data

- server process control scripts and data

$Id$
"""
import optparse
import os
import shutil
import sys

import zope

from zope.app.applicationcontrol import zopeversion


def main(argv=None):
    """Top-level script function to create a new Zope instance."""
    if argv is None:
        argv = sys.argv
    try:
        options = parse_args(argv)
    except SystemExit, e:
        if e.code:
            return 2
        else:
            return 0
    app = Application(options)
    return app.process()


class Application:

    def __init__(self, options):
        self.options = options

    def read_input_line(self, prompt):
        # The tests replace this to make sure the right things happen.
        return raw_input(prompt)

    def process(self):
        options = self.options

        # make sure we can find the skeleton
        if not os.path.isdir(options.skeleton):
            print >>sys.stderr, "skeleton directory", options.skeleton
            print >>sys.stderr, "does not exist or is not a directory"
            return 1

        # create the destination
        if not options.destination:
            options.destination = self.get_skeltarget()
        options.destination = os.path.abspath(options.destination)
        if not os.path.exists(options.destination):
            try:
                os.mkdir(options.destination)
            except OSError, e:
                print >>sys.stderr, "could not create instance home:", e
                return 1
        elif not os.path.isdir(options.destination):
            print >>sys.stderr, options.destination, "is not a directory"
            print >>sys.stderr, ("(instance homes cannot be created in"
                                 " non-directories)")
            return 1

        # XXX for now, bail if the username/password hasn't been
        # provided from the command line; this should be improved
        # after the ZopeX3 alpha:
        if not (options.username and options.password):
            print >>sys.stderr, ("username and password must be"
                                 " provided using the --user option")
            return 2

        # now create the instance!
        self.copy_skeleton()
        return 0

    def get_skeltarget(self):
        print SKELTARGET_MESSAGE
        while 1:
            skeltarget = self.read_input_line("Directory: ").strip()
            if skeltarget == '':
                print >>sys.stderr, 'You must specify a directory'
                continue
            else:
                break
        return os.path.expanduser(skeltarget)

    def copy_skeleton(self):
        options = self.options
        # XXX we should be able to compute the script
        script = os.path.abspath(sys.argv[0])
        zope_home = os.path.dirname(os.path.dirname(script))
        zope_init = os.path.abspath(zope.__file__)
        software_home = os.path.dirname(os.path.dirname(zope_init))
        self.replacements = [
            ("<<USERNAME>>",      options.username),
            ("<<PASSWORD>>",      options.password),
            ("<<PYTHON>>",        sys.executable),
            ("<<INSTANCE_HOME>>", options.destination),
            ("<<ZOPE_HOME>>",     zope_home),
            ("<<SOFTWARE_HOME>>", software_home),
            ]
        self.copytree(self.options.skeleton, self.options.destination)

    def copytree(self, src, dst):
        # Similar to shutil.copytree(), but doesn't care about
        # symlinks, doesn't collect errors, and uses self.copyfile()
        # instead of shutil.copy2().
        assert os.path.isdir(dst), dst
        names = os.listdir(src)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                os.mkdir(dstname)
                self.copytree(srcname, dstname)
            else:
                self.copyfile(srcname, dstname)
            # XXX What about devices, sockets etc.?

    def copyfile(self, src, dst):
        if dst.endswith(".in"):
            dst = dst[:-3]
            text = open(src, "rU").read()
            # perform replacements
            for var, string in self.replacements:
                text = text.replace(var, string)
            f = open(dst, "w")
            f.write(text)
            f.close()
            shutil.copymode(src, dst)
            shutil.copystat(src, dst)
        else:
            shutil.copy2(src, dst)


SKELTARGET_MESSAGE = """\
Please choose a directory in which you'd like to install Zope
'instance home' files such as database files, configuration files,
etc.
"""


def parse_args(argv):
    """Parse the command line, returning an object representing the input."""
    path, prog = os.path.split(os.path.realpath(argv[0]))
    basedir = os.path.dirname(path)
    # no assurance that this exists!
    default_skeleton = os.path.join(basedir, "zopeskel")
    version = "%prog for " + zopeversion.ZopeVersionUtility.getZopeVersion()
    p = optparse.OptionParser(prog=prog,
                              usage="%prog [options]",
                              version=version)
    p.add_option("-d", "--dir", dest="destination", metavar="DIR",
                 help="the dir in which the instance home should be created")
    p.add_option("-s", "--skelsrc", dest="skeleton", metavar="DIR",
                 default=default_skeleton,
                 help="template skeleton directory")
    p.add_option("-u", "--user", dest="username", metavar="USER:PASSWORD",
                 help="set the user name and password of the initial user")
    options, args = p.parse_args(argv[1:])
    options.program = prog
    options.version = version
    if args:
        p.error("too many arguments")
    options.password = None
    if options.username and ":" in options.username:
        options.username, options.password = options.username.split(":", 1)
    return options
