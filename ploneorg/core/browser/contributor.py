from copy import deepcopy
import json

from OFS.Image import Image

from zope.interface import implements
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.publisher.interfaces import IPublishTraverse, NotFound

import plone.api as api
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

    def contributor(self):
        member_data = self.get_member_data()
        return {'fullname': member_data.getProperty('fullname'),
                'name': member_data.getName(),
                'github_username': member_data.getProperty('github_username'),
                'github_contributions': member_data.getProperty('github_contributions')}

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


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return super(JSONEncoder, self).default(obj)

    
class JsonApiView(BrowserView):

    def read_json(self):
      return json.loads(self.request.get('BODY'))

    def to_json(self, data):
        return json.dumps(data, indent=4, cls=JSONEncoder)

    def json(self, data, status=200, reason=None):
        self.request.response.setHeader("Content-type", "application/json")

        # set the status
        lock = (status != 200)  # prevent later status modification if we return an error
        self.request.response.setStatus(status, reason=reason, lock=lock)

        json_data = {'status': status,
                     'reason': reason,
                     'data': data}
        return self.to_json(json_data)

    def json_success(self, data):
        return self.json(data)

    def json_error(self, data, status, reason):
        return self.json(data, status=status, reason=reason)
    
  
class UpdateContributorData(JsonApiView):

    def __call__(self):
        data = self.read_json()
        response_data = {'github': {}}
        # github data
        for org in ['plone', 'collective']:
            commits_by_user = data['github'][org]['contributions']
            updated_members = {}  # map member to github username
            unknown_github_users = commits_by_user.keys()
            members = api.user.get_users()
            # create the key that should be defined in memberdata_properties.xml
            properties_key = '%s_commits' % org
            for member in members:
                # use the github_username if added to the profile. otherwise
                # we fall back to the plone username.
                member_name = member.getName()
                github_username = member.getProperty('github_username') or member_name
                if github_username in commits_by_user:
                    commits = commits_by_user[github_username]
                    member.setMemberProperties(mapping={properties_key: commits})
                    updated_members [member_name] = github_username
                    unknown_github_users.remove(github_username)

            response_data['github'][org] = {'updatedMembers': updated_members,
                                            'unknownGithubUsers': unknown_github_users}

        return self.json_success(response_data)
                
                
        
