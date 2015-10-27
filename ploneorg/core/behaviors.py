# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from ploneorg.core import _
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IPloneStatistics(model.Schema):
    """Behavior for github statistics data"""

    fieldset(
        'github',
        label=_(u'Plone Statistics'),
        fields=[
            'stats_contributors',
            'stats_addons',
            'stats_providers',
            'stats_countries',
            'stats_languages',
            'stats_downloads',
            'stats_new_issues',
            'stats_commits',
            'stats_blockers',
            'stats_pull_requests',
            'stats_needs_review',
        ]
    )

    stats_contributors = schema.Int(
        title=_(u'contributors', default=u'Contributors'),
        description=u'Number of contributors',
        default=0,
        required=False,
    )

    stats_addons = schema.Int(
        title=_(u'addons', default=u'Add-ons'),
        description=u'Number of add-onss',
        default=0,
        required=False,
    )

    stats_providers = schema.Int(
        title=_(u'providers', default=u'Solution Providers'),
        description=u'Number of solution providers',
        default=0,
        required=False,
    )

    stats_countries = schema.Int(
        title=_(u'countries', default=u'Countries'),
        description=u'Number of countries',
        default=0,
        required=False,
    )

    stats_languages = schema.Int(
        title=_(u'languages', default=u'Languages'),
        description=u'Number of languages',
        default=0,
        required=False,
    )

    stats_downloads = schema.Int(
        title=_(u'downloads', default=u'Downloads'),
        description=u'Todays downloads',
        default=0,
        required=False,
    )

    stats_new_issues = schema.Int(
        title=_(u'new_issues', default=u'New issues'),
        description=u'New issues in last 24h',
        default=0,
        required=False,
    )

    stats_commits = schema.Int(
        title=_(u'commits', default=u'Commits'),
        description=u'Commits this calender week',
        default=0,
        required=False,
    )

    stats_blockers = schema.Int(
        title=_(u'blockers', default=u'Blockers'),
        description=u'Issues blocking release',
        default=0,
        required=False,
    )

    stats_pull_requests = schema.Int(
        title=_(u'pull_requests', default=u'New PR last week'),
        description=u'Pull requests created last week',
        default=0,
        required=False,
    )

    stats_needs_review = schema.Int(
        title=_(u'needs_review', default=u'Needs review'),
        description=u'PR needing review',
        default=0,
        required=False,
    )

    stats_community_posts = schema.Int(
        title=_(u'forum_messages', default=u'Forum messages'),
        description=u'Posts on community.plone.org',
        default=0,
        required=False,
    )
