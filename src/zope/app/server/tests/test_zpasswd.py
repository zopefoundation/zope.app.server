import unittest


class TestZpasswdDeprecation(unittest.TestCase):

    def test(self):
        with self.assertWarns(DeprecationWarning):
            from zope.app.server.zpasswd import Principal  # noqa
