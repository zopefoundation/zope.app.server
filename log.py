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
import time
import twisted.python.log
from twisted import web2
from zope.interface import implements
from zope.app.http.httpdate import monthname


class CommonAccessLoggingObserver(object):
    """Outputs accesses in common HTTP log format."""

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger('accesslog')
        self.logger = logger

    def computeTimezoneForLog(self, tz):
        if tz > 0:
            neg = 1
        else:
            neg = 0
            tz = -tz
        h, rem = divmod (tz, 3600)
        m, rem = divmod (rem, 60)
        if neg:
            return '-%02d%02d' % (h, m)
        else:
            return '+%02d%02d' % (h, m)

    tzForLog = None
    tzForLogAlt = None

    def logDateString(self, when):
        logtime = time.localtime(when)
        Y, M, D, h, m, s = logtime[:6]
        
        if not time.daylight:
            tz = self.tzForLog
            if tz is None:
                tz = self.computeTimezoneForLog(time.timezone)
                self.tzForLog = tz
        else:
            tz = self.tzForLogAlt
            if tz is None:
                tz = self.computeTimezoneForLog(time.altzone)
                self.tzForLogAlt = tz

        return '%d/%s/%02d:%02d:%02d:%02d %s' % (
            D, monthname[M], Y, h, m, s, tz)

    def emit(self, eventDict):
        """See zope.app.logger.interfaces.IPublisherRequestLogger"""
        if eventDict.get('interface') is not web2.iweb.IRequest:
            return

        request = eventDict['request']

        firstLine = '%s %s HTTP/%s' %(
            request.method,
            request.uri,
            '.'.join([str(x) for x in request.clientproto]))
        
        self.logger.log(logging.INFO,
            '%s - %s [%s] "%s" %s %d "%s" "%s"' %(
                request.chanRequest.transport.client[0],
                request.response.headers.getRawHeaders(
                    'x-zope-principal', ['anonymous'])[-1],
                self.logDateString(
                    request.response.headers.getHeader('date', time.time())),
                firstLine,
                request.response.code,
                request.bytesSent,
                request.headers.getHeader('referer', '-'),
                request.headers.getHeader('user-agent', '-')
                )
            )

    def start(self):
        """Start observing log events."""
        twisted.python.log.addObserver(self.emit)

    def stop(self):
        """Stop observing log events."""
        twisted.python.log.removeObserver(self.emit)



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
