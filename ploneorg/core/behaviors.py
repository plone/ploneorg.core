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
class IGithubStatistics(model.Schema):
    """Behavior for github statistics data
    """

    model.fieldset(
        'github',
        label=_(u"Github Statistics"),
        fields=[
            'gh_new_issues',
            'gh_commits',
            'gh_blockers',
            'gh_pr_last_week',
            'gh_needs_review',
        ]
    )

    gh_new_issues = schema.Int(
        title=_(u'new_issues', default=u'New issues'),
        description=u'New issues in last 24h',
        default=0,
        required=False,
    )

    gh_commits = schema.Int(
        title=_(u'commits', default=u'Commits'),
        description=u'Commits this calender week',
        default=0,
        required=False,
    )

    gh_blockers = schema.Int(
        title=_(u'blockers', default=u'Blockers'),
        description=u'Issues blocking release',
        default=0,
        required=False,
    )

    gh_pr_last_week = schema.Int(
        title=_(u'pr_last_week', default=u'New PR last week'),
        description=u'PR created last week',
        default=0,
        required=False,
    )

    gh_needs_review = schema.Int(
        title=_(u'needs_review', default=u'Needs review'),
        description=u'PR needing review',
        default=0,
        required=False,
    )
