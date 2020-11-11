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
"""Tests for zope.app.server.accesslog.
"""
import logging
import unittest

from ZConfig.components.logger import loghandler

try:
    # ZConfig < 2.9.2
    from ZConfig.components.logger.tests.test_logger import LoggingTestBase
except ImportError:
    try:
        # ZConfig >= 3.4.0
        from ZConfig.components.logger.tests.support import LoggingTestHelper
    except ImportError:
        # ZConfig >= 2.9.2, < 3.4.0
        from ZConfig.components.logger.tests.test_logger import \
            LoggingTestHelper

    class LoggingTestBase(LoggingTestHelper, unittest.TestCase):
        pass


class TestAccessLogging(LoggingTestBase):

    name = "accesslog"

    _schematext = """
      <schema>
        <import package='zope.app.server' file='accesslog.xml'/>
        <section type='accesslog' name='*' attribute='accesslog'/>
      </schema>
    """

    def test_config_without_logger(self):
        conf = self.get_config("")
        self.assertIsNone(conf.accesslog)

    def test_config_without_handlers(self):
        logger = self.check_simple_logger("<accesslog/>")
        # Make sure there's a NullHandler, since a warning gets
        # printed if there are no handlers:
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], loghandler.NullHandler)

    def test_formatter(self):
        logger = self.check_simple_logger("<accesslog>\n"
                                          "  <syslog>\n"
                                          "    level error\n"
                                          "    facility local3\n"
                                          "    format %(message)s\n"
                                          "  </syslog>\n"
                                          "</accesslog>")
        self.assertEqual(len(logger.handlers), 1)
        syslog = logger.handlers[0]
        self.assertEqual(syslog.level, logging.ERROR)
        self.assertIsInstance(syslog, loghandler.SysLogHandler)
        self.assertEqual(syslog.formatter._fmt, "%(message)s")
        syslog.close()  # avoid ResourceWarnings

    def check_simple_logger(self, text):
        conf = self.get_config(text)
        self.assertIsNotNone(conf.accesslog)
        logger = conf.accesslog()
        self.assertIsInstance(logger, logging.Logger)
        self.assertFalse(logger.propagate)
        self.assertEqual(logger.name, "accesslog")
        self.assertEqual(logger.level, logging.INFO)
        return logger
