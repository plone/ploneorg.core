# -*- coding: utf-8 -*-
from collective.badge.api import badges_for_user
from OFS.Image import Image
from plone import api
from plone.memoize.view import memoize_contextless
from plone.protect.interfaces import IDisableCSRFProtection
from ploneorg.core import HOMEPAGE_ID
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
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

TWITTER_RE = re.compile(
    r'http[s]*://twitter\.com/(.*)/*')


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
        if member_data is None:
            return None
        return {
            'fullname': member_data.getProperty('fullname'),
            'name': member_data.getUserName(),
            'bio': member_data.getProperty('description'),
            'avatar_url': member_data.getProperty('avatar_url'),
            'location': member_data.getProperty('location'),
            'country': member_data.getProperty('country'),
            'plone_commits': member_data.getProperty('plone_commits'),
            'collective_commits': member_data.getProperty(
                'collective_commits'),
            'home_page': member_data.getProperty('home_page'),
            'twitter': member_data.getProperty('twitter_url'),
            'stackoverflow_url': member_data.getProperty(
                'stackoverflow_url'),
            'stackoverflow_questions': member_data.getProperty(
                'stackoverflow_questions'),
            'sprints_attended':
                '<br/>'.join(
                    member_data.getProperty('sprints_attended').split('\r\n')),
            'contributing_since': member_data.getProperty(
                'contributing_since'),
            'tweets': member_data.getProperty('tweets'),
        }

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
        return badges_for_user(self.username)

    def has_social(self):
        user = self.get_member_data()
        return user.getProperty('home_page', False) or \
            user.getProperty('twitter_url', False) or \
            user.getProperty('github', False)


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
                # use the github_url if added to the profile. otherwise
                # we fall back to the plone username.
                member_name = member.getUserName()
                github_url = (member.getProperty('github_url') or member_name)
                if github_url in commits_by_user:
                    commits = int(commits_by_user[github_url])
                    member.setMemberProperties(
                        mapping={properties_key: commits})
                    updated_members[member_name] = github_url
                    unknown_github_users.remove(github_url)

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

        if answers_by_member is None:
            response_data['done'] = 'No data'
            return

        for member in members:
            member_name = member.getUserName()
            answers = answers_by_member.get(member_name, 0)
            response_data[member_name] = answers
            member.setMemberProperties(
                mapping={'stackoverflow_questions': answers})

    def add_twitter_data(self, members, data, response_data):
        twitter = 'twitter'
        if twitter not in data:
            response_data['error'] = (
                'No data for twitter available.')
            return
        tweets = data[twitter]

        if tweets is None:
            response_data['done'] = 'No data'
            return

        for member in members:
            member_name = member.getUserName()
            member_tweets = tweets.get(member_name, 0)
            response_data[member_name] = member_tweets
            member.setMemberProperties(
                mapping={'tweets': member_tweets})

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
        if 'plone' not in data['github']:
            response_data['done'] = 'No data'
            return
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

        if pypidata is None:
            response_data['done'] = 'No data'
            return
        if pypidata['last_month'] >= 0:
            hp.stats_downloads = pypidata['last_month']
        response_data['done'] = True

    def add_community_stats(self, data, response_data):
        hp = self._homepage
        if hp is None:
            response_data['error'] = 'no homepage to store'
            return
        if 'community' not in data:
            response_data['errors'] = 'No data for community available.'
        community_data = data['community']

        if community_data is None:
            response_data['done'] = 'No data'
            return
        if community_data >= 0:
            hp.stats_community_posts = community_data
        response_data['done'] = True

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        data = self.read_json()
        response_data = {
            'github_members': {},
            'github_stats': {},
            'stackoverflow': {},
            'pypi': {},
            'twitter': {},
            'community': {},
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
        self.add_twitter_data(
            members,
            data,
            response_data['twitter']
        )
        self.add_github_overall_stats(data, response_data['github_stats'])
        self.add_pypi_stats(data, response_data['pypi'])
        self.add_community_stats(data, response_data['community'])
        return self.json_success(response_data)


class StackOverflowIds(JsonApiView):

    def __call__(self):
        response_data = {}
        for member in api.user.get_users():
            so_url = member.getProperty('stackoverflow_url')
            if so_url:
                match = STACKOVERFLOW_RE.match(so_url)
                if match:
                    so_uid = match.groups()[0]
                    response_data[member.getUserName()] = so_uid
        return self.json_success(response_data)


class TwitterIds(JsonApiView):

    def __call__(self):
        response_data = {}
        for member in api.user.get_users():
            twitter_url = member.getProperty('twitter_url')
            if twitter_url:
                match = TWITTER_RE.match(twitter_url)
                if match:
                    twitter_id = match.groups()[0]
                    response_data[member.getUserName()] = twitter_id
        return self.json_success(response_data)
