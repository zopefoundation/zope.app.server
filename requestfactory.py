##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Request Factory

$Id$
"""
import copy
from zope.app.publication.interfaces import IRequestFactory
from zope.interface import implements

class RequestFactory:
    """This class will generically create RequestFactories. This way I do
       not have to create a method for each Server Type there is.
    """

    implements(IRequestFactory)

    def __init__(self, publication, request):
        """Initialize Request Factory"""
        self._pubFactory = publication
        self._publication = None
        self._request = request


    def realize(self, db):
        'See IRequestFactory'
        realized = copy.copy(self)
        realized._publication = realized._pubFactory(db)
        return realized


    def __call__(self, input_stream, output_steam, env):
        'See IRequestFactory'
        request = self._request(input_stream, output_steam, env)
        request.setPublication(self._publication)
        return request
