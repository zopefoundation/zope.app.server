##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Logging Support

Logging Support for the Twisted logging framework. A special observer will
forward messages to the standard Python Logging Framework. 

$Id$
"""
__docformat__ = "reStructuredText"

import logging
import twisted.web2.log
from twisted import web2


class CommonAccessLoggingObserver(web2.log.BaseCommonAccessLoggingObserver):
    """Writes common access log to python's logging framework."""

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger('accesslog')
        self.logger = logger

    def logMessage(self, message):
        self.logger.log(logging.INFO, message)


class CommonFTPActivityLoggingObserver(CommonAccessLoggingObserver):
    """Outputs hits in common HTTP log format."""

    def log(self, request):
        """See zope.app.logger.interfaces.IPublisherRequestLogger"""
        now = time.time()
        message = ' - %s [%s] "%s %s"' % (task.channel.username,
                                       self.log_date_string(now),
                                       task.m_name[4:].upper(),
                                       task.channel.cwd,
                                       )

        self.output.logRequest(task.channel.addr[0], message)
