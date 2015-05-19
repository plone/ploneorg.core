# -*- coding: utf-8 -*-
from plone.app.content.interfaces import INameFromTitle
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from ploneorg.core import _
from ploneorg.core.content.foundationmember import IFoundationMember
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


class INameFromFullName(INameFromTitle):
    """Get the name from the full name.

    This is really just a marker interface, automatically set by
    enabling the corresponding behavior.

    Note that when you want this behavior, then you MUST NOT enable
    the IDublinCore, IBasic, INameFromTitle or INameFromFile behaviors
    on your type.
    """


@implementer(INameFromFullName)
@adapter(IFoundationMember)
class NameFromFullName(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.get_full_name()


@provider(IFormFieldProvider)
class IPloneStatistics(model.Schema):
    """Behavior for github statistics data
    """

    model.fieldset(
        'github',
        label=_(u'Plone Statistics'),
        fields=[
            'stats_provider',
            'stats_countries',
            'stats_languages',
            'stats_downloads',
            'stats_new_issues',
            'stats_commits',
            'stats_blockers',
            'stats_pr_last_week',
            'stats_needs_review',
        ]
    )

    stats_provider = schema.Int(
        title=_(u'provider', default=u'Solution Provider'),
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

    stats_pr_last_week = schema.Int(
        title=_(u'pr_last_week', default=u'New PR last week'),
        description=u'PR created last week',
        default=0,
        required=False,
    )

    stats_needs_review = schema.Int(
        title=_(u'needs_review', default=u'Needs review'),
        description=u'PR needing review',
        default=0,
        required=False,
    )
