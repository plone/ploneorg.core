import datetime
import json
import re

from OFS.Image import Image

from plone import api
from plone.memoize.view import memoize_contextless

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.component.hooks import getSite
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


STACKOVERFLOW_RE = re.compile(r'http[s]*://stackoverflow\.com/([0-9]+).*')


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
                'github': member_data.getProperty('github_username'),
                'plone_commits': member_data.getProperty('plone_commits'),
                'collective_commits': member_data.getProperty(
                    'collective_commits'),
                'home_page': member_data.getProperty('home_page'),
                'twitter': member_data.getProperty('twitter_username'),
                'stackoverflow_username': member_data.getProperty(
                    'stackoverflow_username'),
                'stackoverflow_answers': member_data.getProperty(
                    'stackoverflow_answers')}

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
        lock = (status != 200)  # prevent later status modification if
                                # we return an error
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

    def add_github_data(self, members, data, response_data):
        for org in ['plone', 'collective']:
            commits_by_user = data['github'][org]['contributions']
            updated_members = {}  # map member to github username
            unknown_github_users = commits_by_user.keys()
            # create the key that should be defined in
            # memberdata_properties.xml
            properties_key = '%s_commits' % org
            for member in members:
                # use the github_username if added to the profile. otherwise
                # we fall back to the plone username.
                member_name = member.getName()
                github_username = (member.getProperty('github_username') or
                                   member_name)
                if github_username in commits_by_user:
                    commits = int(commits_by_user[github_username])
                    member.setMemberProperties(
                        mapping={properties_key: commits})
                    updated_members[member_name] = github_username
                    unknown_github_users.remove(github_username)

            response_data['github'][org] = {
                'updatedMembers': updated_members,
                'unknownGithubUsers': unknown_github_users}

    def add_stackoverflow_data(self, members, data, response_data):
        answers_by_member = data['stackoverflow']
        for member in members:
            answers = answers_by_member.get(member.getName(), 0)
            member.setMemberProperties(
                mapping={'stackoverflow_answers': answers})

    def __call__(self):
        data = self.read_json()
        response_data = {'github': {},
                         'stackoverflow': {}}
        members = api.user.get_users()
        self.add_github_data(members, data, response_data)
        self.add_stackoverflow_data(members, data, response_data)
        return self.json_success(response_data)


class StackOverflowIds(JsonApiView):

    def __call__(self):
        response_data = {}
        for member in api.user.get_users():
            so_url = member.getProperty('stackoverflow_username')
            if so_url:
                match = STACKOVERFLOW_RE.match(so_url)
                if match:
                    so_uid = match.groups()[0]
                    response_data[member.getName()] = so_uid
        return self.json_success(response_data)
