import unittest

from zope.interface.verify import verifyObject
from zope.server.http.wsgihttpserver import WSGIHTTPServer

from zope.app.server.servertype import IServerType
from zope.app.server.wsgi import http
from zope.app.server.wsgi import pmhttp


class TestWSGIServerType(unittest.TestCase):

    def test(self):
        verifyObject(IServerType, http)
        verifyObject(IServerType, pmhttp)

    def test_create(self):
        dispatcher = 'my task dispatcher'
        db = 'my database'
        server = http.create("HTTP", dispatcher, db, port=0)
        self.assertIsInstance(server, WSGIHTTPServer)
