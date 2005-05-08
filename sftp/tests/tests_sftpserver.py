from unittest import TestSuite, main

from zope.testing import doctest
from zope.app.server.sftp import HAS_CRYPTO

def test_suite():
    if HAS_CRYPTO:
        return TestSuite((
            doctest.DocTestSuite('zope.app.server.sftp.server'),
            ))
    else:
        return

if __name__ == "__main__":
    main(defaultTest = 'test_suite')
