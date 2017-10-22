import unittest

from zope.interface.verify import verifyObject
from zope.app.server.servertype import IServerType
from zope.app.server.wsgi import http, pmhttp


class TestWSGIServerType(unittest.TestCase):

    def test(self):
        verifyObject(IServerType, http)
        verifyObject(IServerType, pmhttp)
