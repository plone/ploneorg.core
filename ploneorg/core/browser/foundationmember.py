# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from zope.security import checkPermission


class FoundationMemberView(BrowserView):
    """ Default view for foundation member """

    def canViewDetails(self):
        return checkPermission('ploneorg.core.foundationmember.view', self.context)

