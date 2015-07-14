# -*- coding: utf-8 -*-
from OFS.Image import Image
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize_contextless
from ploneorg.core import HOMEPAGE_ID
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

import datetime
import json
import re


BADGE_TEAMS = ['foundation.members',
               'board.members',
               'team.testing',
               'team.ui',
               'team.installers']

STACKOVERFLOW_RE = re.compile(
    r'http[s]*://stackoverflow\.com/users/([0-9]+).*')


@implementer(IPublishTraverse)
class contributorProfile(BrowserView):
    """ Return an user profile ../profile/{username} """

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
                'name': member_data.getUserName(),
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
        return api.portal.get()

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
        pm = api.portal.get_tool(name='portal_membership')
        user = pm.getMemberById(self.username)
        return user

    def get_member_image(self):
        pm = api.portal.get_tool(name='portal_membership')
        portrait = pm.getPersonalPortrait(self.username)
        return portrait.absolute_url()

    def get_member_large_image(self):
        pm = api.portal.get_tool(name='portal_membership')
        portrait = pm.getPersonalPortrait(self.username + '_large')
        return portrait.absolute_url()

    def get_user_badges(self):
        # import ipdb;ipdb.set_trace()
        pass


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
        self.request.response.setHeader('Content-type', 'application/json')

        # set the status
        # prevent later status modification if we return an error
        lock = (status != 200)
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

    def add_github_member_related_data(self, members, data, response_data):
        if 'github' not in data:
            response_data['error'] = 'No data for github available.'
            return
        ghdata = data['github']
        for org in ['plone', 'collective']:
            if org not in ghdata:
                response_data[org] = (
                    'No github data for org "%s" available.' % org
                )
                continue
            commits_by_user = ghdata[org]['contributions']
            updated_members = {}  # map member to github username
            unknown_github_users = commits_by_user.keys()
            # create the key that should be defined in
            # memberdata_properties.xml
            properties_key = '%s_commits' % org
            for member in members:
                # use the github_username if added to the profile. otherwise
                # we fall back to the plone username.
                member_name = member.getUserName()
                github_username = (member.getProperty('github_username') or
                                   member_name)
                if github_username in commits_by_user:
                    commits = int(commits_by_user[github_username])
                    member.setMemberProperties(
                        mapping={properties_key: commits})
                    updated_members[member_name] = github_username
                    unknown_github_users.remove(github_username)

            response_data[org] = {
                'updatedMembers': updated_members,
                'unknownGithubUsers': unknown_github_users}

    def add_stackoverflow_data(self, members, data, response_data):
        stackoverflow = 'stackoverflow'
        if stackoverflow not in data:
            response_data['error'] = (
                'No data for stackoverflow available.')
            return
        answers_by_member = data[stackoverflow]
        for member in members:
            member_name = member.getUserName()
            answers = answers_by_member.get(member_name, 0)
            response_data[member_name] = answers
            member.setMemberProperties(
                mapping={'stackoverflow_answers': answers})

    @property
    def _homepage(self):
        portal = api.portal.get()
        return portal.get(HOMEPAGE_ID, None)

    def add_github_overall_stats(self, data, response_data):
        hp = self._homepage
        if hp is None:
            response_data['error'] = 'no homepage to store'
            return
        if 'github' not in data:
            response_data['error'] = 'No data for github available.'
        ghdata = data['github']['plone']
        if ghdata['new_issues'] >= 0:
            hp.stats_new_issues = ghdata['new_issues']
        if ghdata['commits'] >= 0:
            hp.stats_commits = ghdata['commits']
        if ghdata['blockers'] >= 0:
            hp.stats_blockers = ghdata['blockers']
        if ghdata['pull_requests'] >= 0:
            hp.stats_pull_requests = ghdata['pull_requests']
        if ghdata['needs_review'] >= 0:
            hp.stats_needs_review = ghdata['needs_review']
        response_data['done'] = True

    def add_pypi_stats(self, data, response_data):
        hp = self._homepage
        if hp is None:
            response_data['error'] = 'no homepage to store'
            return
        if 'pypi' not in data:
            response_data['errors'] = 'No data for pypi available.'
        pypidata = data['pypi']
        if pypidata['last_day'] >= 0:
            hp.stats_downloads = pypidata['last_day']
        response_data['done'] = True

    def __call__(self):
        data = self.read_json()
        response_data = {
            'github_members': {},
            'github_stats': {},
            'stackoverflow': {},
            'pypi': {},
        }
        members = api.user.get_users()
        self.add_github_member_related_data(
            members,
            data,
            response_data['github_members']
        )
        self.add_stackoverflow_data(
            members,
            data,
            response_data['stackoverflow']
        )
        self.add_github_overall_stats(data, response_data['github_stats'])
        self.add_pypi_stats(data, response_data['pypi'])
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
                    response_data[member.getUserName()] = so_uid
        return self.json_success(response_data)
