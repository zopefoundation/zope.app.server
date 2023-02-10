import unittest

from zope.applicationcontrol.interfaces import IServerControl
from zope.interface.verify import verifyObject

import zope.app.server.main
from zope.app.server.servercontrol import serverControl


class TestServerControl(unittest.TestCase):

    def tearDown(self):
        zope.app.server.main.exit_status = None

    def test(self):
        verifyObject(IServerControl, serverControl)

    def test_shutdown(self):
        serverControl.shutdown()
        self.assertEqual(zope.app.server.main.exit_status, 0)

    def test_restart(self):
        serverControl.restart()
        self.assertEqual(zope.app.server.main.exit_status, 1)
