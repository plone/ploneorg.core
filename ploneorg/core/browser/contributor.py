from copy import deepcopy
from OFS.Image import Image

from zope.interface import implements
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.publisher.interfaces import IPublishTraverse, NotFound

from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize_contextless

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class contributorProfile(BrowserView):
    """ Return an user profile ../profile/{username} """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(contributorProfile, self).__init__(context, request)
        self.username = None

    def publishTraverse(self, request, name):
        if self.username is None:  # ../profile/username
            self.username = name
        else:
            raise NotFound(self, name, request)
        return self

    index = ViewPageTemplateFile('contributor.pt')

    def __call__(self):
        return self.index()

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def has_complete_profile(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        user = pm.getAuthenticatedMember()
        portrait = pm.getPersonalPortrait()

        if user.getProperty('fullname') \
           and user.getProperty('fullname') != user.getProperty('username') \
           and user.getProperty('email') \
           and isinstance(portrait, Image):
            return True
        else:
            return False

    def get_member_data(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        user = pm.getMemberById(self.username)
        return user

    def get_member_image(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        portrait = pm.getPersonalPortrait(self.username)
        return portrait.absolute_url()
