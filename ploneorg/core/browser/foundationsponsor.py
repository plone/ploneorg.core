# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from zope.security import checkPermission


class FoundationSponsorView(BrowserView):
    """ Default view for foundation sponsor """

    def canViewDetails(self):
        return checkPermission('ploneorg.core.foundationsponsor.view', self.context)

