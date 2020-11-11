import unittest
import warnings
from contextlib import contextmanager


class TestZpasswdDeprecation(unittest.TestCase):

    if not hasattr(unittest.TestCase, 'asserWarns'):
        # Python 2.7 compat, *sigh*
        @contextmanager
        def assertWarns(self, what):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                yield
                self.assertEqual(len(w), 1)
                self.assertTrue(issubclass(w[-1].category, what))

    def test(self):
        with self.assertWarns(DeprecationWarning):
            from zope.app.server.zpasswd import Principal  # noqa
