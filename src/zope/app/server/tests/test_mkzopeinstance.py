##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Tests for the implementation of the mkzopeinstance script.
"""
import os
import shutil
import sys
import tempfile
import unittest
import zope.app.server

from StringIO import StringIO

from zope.app.server import mkzopeinstance


class TestBase(unittest.TestCase):

    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


class ArgumentParsingTestCase(TestBase):
    """Ensure the command line is properly converted to an options
    object.
    """

    def parse_args(self, args):
        argv = ["foo/bar.py"] + args
        options = mkzopeinstance.parse_args(argv)
        self.assertEqual(options.program, "bar.py")
        self.assert_(options.version)
        return options

    def test_no_arguments(self):
        options = self.parse_args([])

    def test_version_long(self):
        self.check_stdout_content(["--version"])

    def test_help_long(self):
        self.check_stdout_content(["--help"])

    def test_help_short(self):
        self.check_stdout_content(["-h"])

    def check_stdout_content(self, args):
        try:
            options = self.parse_args(args)
        except SystemExit, e:
            self.assertEqual(e.code, 0)
            self.assert_(self.stdout.getvalue())
            self.failIf(self.stderr.getvalue())
        else:
            self.fail("expected SystemExit")

    def test_without_destination(self):
        options = self.parse_args([])
        self.assertEqual(options.destination, None)

    def test_destination_long(self):
        options = self.parse_args(["--dir", "some/dir"])
        self.assertEqual(options.destination, "some/dir")

    def test_destination_short(self):
        options = self.parse_args(["-d", "some/dir"])
        self.assertEqual(options.destination, "some/dir")

    def test_without_skeleton(self):
        # make sure we get *some* skeleton directory by default
        # there's no claim that it exists
        options = self.parse_args([])
        self.assertNotEqual(options.skeleton, None)

    def test_with_skeleton_long(self):
        options = self.parse_args(["--skelsrc", "some/dir"])
        self.assertEqual(options.skeleton, "some/dir")
        self.failIf(options.add_package_includes)

    def test_with_skeleton_short(self):
        options = self.parse_args(["-s", "some/dir"])
        self.assertEqual(options.skeleton, "some/dir")
        self.failIf(options.add_package_includes)

    def test_without_username(self):
        options = self.parse_args([])
        self.assertEqual(options.username, None)
        self.assertEqual(options.password, None)

    def test_username_without_password_long(self):
        options = self.parse_args(["--user", "User"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, None)

    def test_username_without_password_short(self):
        options = self.parse_args(["-u", "User"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, None)

    def test_username_with_password_long(self):
        options = self.parse_args(["--user", "User:Pass"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, "Pass")

    def test_username_with_password_short(self):
        options = self.parse_args(["-u", "User:Pass"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, "Pass")

    def test_without_password_manager(self):
        options = self.parse_args([])
        self.assertEqual(options.password_manager, None)

    def test_password_manager_short(self):
        options = self.parse_args(["-m", "Manager"])
        self.assertEqual(options.password_manager, "Manager")

    def test_password_manager_long(self):
        options = self.parse_args(["--password-manager", "Manager"])
        self.assertEqual(options.password_manager, "Manager")

    def test_junk_positional_arg(self):
        try:
            self.parse_args(["junk"])
        except SystemExit, e:
            self.assert_(e.code)
        else:
            self.fail("expected SystemExit")


class InputCollectionTestCase(TestBase):

    def setUp(self):
        super(InputCollectionTestCase, self).setUp()
        self.tmpdir = tempfile.mkdtemp(prefix="test-mkzopeinstance-")
        self.skeleton = os.path.join(self.tmpdir, "skel")
        self.instance = os.path.join(self.tmpdir, "inst")
        os.mkdir(self.skeleton)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        super(InputCollectionTestCase, self).tearDown()

    def createOptions(self):
        options = Options()
        options.skeleton = self.skeleton
        options.interactive = True
        return options

    def test_get_skeltarget(self):
        options = self.createOptions()
        input = ["  ", " foo "]
        app = ControlledInputApplication(options, input)
        skel = app.get_skeltarget()
        self.assertEqual(skel, "foo")
        self.assertEqual(input, [])
        self.assert_(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_process_creates_destination(self):
        options = self.createOptions()
        input = [self.instance]
        app = ControlledInputApplication(options, input)
        self.assertEqual(app.process(), 0)
        self.assert_(os.path.isdir(self.instance))
        self.assertEqual(input, [])
        self.failUnless(app.all_input_consumed())

    def test_zserver_support(self):
        # test the zserver option.  We should get zserver versions of
        # runzope, zopectl, debugzope and zope.conf.  Any of these
        # that we provide in put skeleton should be overritten.

        # privide a dummy runzope
        os.mkdir(os.path.join(self.skeleton, 'bin'))
        f = open(os.path.join(self.skeleton, 'bin', 'runzope.in'), 'w')
        f.write('runzope')
        f.close()

        options = self.createOptions()
        options.destination = self.instance
        options.interactive = False
        options.zserver = True
        app = ControlledInputApplication(options, [])
        self.assertEqual(app.process(), 0)
        self.assert_(
            'from zope.app.server.main import main' in
            open(os.path.join(self.instance, 'bin', 'runzope')).read()
            )
        self.assert_(
            'from zope.app.server.main import debug' in
            open(os.path.join(self.instance, 'bin', 'debugzope')).read()
            )
        self.assert_(os.path.exists(
            os.path.join(self.instance, 'etc', 'zope.conf')
            ))


    def test_process_aborts_on_file_destination(self):
        options = self.createOptions()
        options.destination = self.instance
        open(self.instance, "w").close()
        app = ControlledInputApplication(options, [])
        self.assertEqual(app.process(), 1)
        self.assert_(self.stderr.getvalue())

    def test_process_aborts_on_failed_destination_creation(self):
        options = self.createOptions()
        options.destination = os.path.join(self.instance, "foo")
        app = ControlledInputApplication(options, [])
        self.assertEqual(app.process(), 1)
        self.assert_(self.stderr.getvalue())

    def test_get_username(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["myuser"])
        usr = app.get_username()
        self.assertEqual(usr, "myuser")
        self.failIf(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_username_strips_whitespace(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["  myuser\t"])
        usr = app.get_username()
        self.assertEqual(usr, "myuser")
        self.failIf(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_username_ignores_empty_names(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["", "  ", "\t", "myuser"])
        usr = app.get_username()
        self.assertEqual(usr, "myuser")
        self.failUnless(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_manager(self):
        options = self.createOptions()
        options.password_manager = None
        app = ControlledInputApplication(options, ["1"])
        name, pwm = app.get_password_manager()
        self.assertEqual(name, "Plain Text")
        self.assertEqual(pwm.encodePassword("foo"), "foo")
        self.failIf(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_wrong_password_manager(self):
        options = self.createOptions()
        options.password_manager = "Unknown"
        app = ControlledInputApplication(options, [])
        try:
            app.get_password_manager()
        except SystemExit, e:
            self.assertEqual(e.code, 1)
        else:
            self.fail("expected SystemExit")
        self.failUnless(self.stderr.getvalue())
        self.failIf(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["foo", "foo"])
        pw = app.get_password()
        self.assertEqual(pw, "foo")
        self.failIf(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_not_verified(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["foo", "bar"])
        try:
            app.get_password()
        except SystemExit, e:
            self.assertEqual(e.code, 1)
        else:
            self.fail("expected SystemExit")
        self.failUnless(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_empty(self):
        # Make sure the empty password is ignored.
        options = self.createOptions()
        app = ControlledInputApplication(options, ["", "foo", "foo"])
        pw = app.get_password()
        self.assertEqual(pw, "foo")
        self.failUnless(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_disallows_whitespace(self):
        # Any password that contains spaces is disallowed.
        options = self.createOptions()
        app = ControlledInputApplication(options, [" ", "\t", "a b",
                                                   " a", "b ", "foo", "foo"])
        pw = app.get_password()
        self.assertEqual(pw, "foo")
        self.failUnless(self.stderr.getvalue())
        self.failUnless(self.stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_can_rewrite_existing_instance(self):
        # Fill out the skeleton a little so we test more cases:
        os.mkdir(os.path.join(self.skeleton, "etc"))
        f = open(os.path.join(self.skeleton, "etc", "README.txt"), "w")
        f.write("Configuration goes here.\n")
        f.close()

        # Create an instance home:
        options = self.createOptions()
        options.destination = self.instance
        app = ControlledInputApplication(options, [])
        rc = app.process()
        self.assertEqual(rc, 0)
        self.failUnless(app.all_input_consumed())
        self.failUnless(os.path.exists(os.path.join(self.instance, "etc")))

        # Make sure we can do it again:
        options = self.createOptions()
        options.destination = self.instance
        app = ControlledInputApplication(options, [])
        rc = app.process()
        self.assertEqual(rc, 0)
        self.failUnless(app.all_input_consumed())
        self.failUnless(os.path.exists(os.path.join(self.instance, "etc")))

    def test_zope_namespace_package_doesnt_affect_software_home(self):
        # Make sure that a zope namespace package in a different
        # location won't affect SOFTWARE_HOME

        # let's mess with zope's __file__
        import zope
        old_path = zope.__file__
        zope.__file__ = os.path.join(
            *'and now for something completely different'.split())

        # place a test file into the skeleton dir that'll be expanded
        # to SOFTWARE_HOME by mkzopeinstance
        f = file(os.path.join(self.skeleton, 'test.in'), 'w')
        f.write('<<SOFTWARE_HOME>>')
        f.close()

        # run mkzopeinstance
        options = self.createOptions()
        options.destination = self.instance
        app = ControlledInputApplication(options, [])
        rc = app.process()

        # check for the expected output: mkzopeinstance should take
        # zope.app as an anchor for determining SOFTWARE_HOME
        import zope.app
        expected = os.path.dirname(os.path.dirname(
            os.path.dirname(zope.app.__file__)))
        self.assertEqual(file(os.path.join(self.instance, 'test')).read(),
                         expected)

        # cleanup the fake 'zope' module
        zope.__file__ = old_path

class ControlledInputApplication(mkzopeinstance.Application):

    def __init__(self, options, input_lines):
        mkzopeinstance.Application.__init__(self, options)
        self.__input = input_lines

    def read_input_line(self, prompt):
        return self.__input.pop(0)

    read_password = read_input_line

    def all_input_consumed(self):
        return not self.__input


class Options(object):

    username = "[test-username]"
    password_manager = "Plain Text"
    password = "[test-password]"
    destination = None
    version = "[test-version]"
    program = "[test-program]"
    add_package_includes = False
    zserver = False


def test_suite():
    suite = unittest.makeSuite(ArgumentParsingTestCase)
    suite.addTest(unittest.makeSuite(InputCollectionTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
