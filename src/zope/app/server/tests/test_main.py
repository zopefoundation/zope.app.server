import unittest

from zope.app.server.main import main, load_options
from zope.app.server._testing import capture_output


class TestMain(unittest.TestCase):

    def test_main(self):
        with self.assertRaises(SystemExit) as cm:
            with capture_output() as (stdout, stderr):
                main(['invalid'])
        self.assertEqual(cm.exception.code, 2)
        self.assertNotEqual(stderr.getvalue(), "")

    def test_load_options(self):
        options = load_options([])
