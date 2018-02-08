# -*- coding: utf-8 -*-
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity import _ as _PMF
from plone.app.textfield import RichText
from plone.autoform.directives import read_permission
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from ploneorg.core import _
from ploneorg.core.content.foundationsponsor import isHTTP, isEmail
from ploneorg.core.vocabularies import country_vocabulary
from zope import schema
from zope.interface import implementer


class IFoundationMember(Schema):
    """A foundation member"""

    fieldset(
        'Contact',
        label=u'Contact',
        fields=[
            'fname',
            'lname',
            'email',
            'showEmail',
            'website',
            'twitter',
            'facebook',
            'linkedin',
            'github',
            'address',
            'city',
            'state',
            'postalCode',
            'country',
            'organization',
        ]
    )

    fieldset(
        'Merit',
        label=u'Merit',
        fields=[
            'merit',
        ]
    )

    fieldset(
        'Survey',
        label=u'Survey',
        fields=[
            'orgsize',
            'ploneuse',
        ]
    )

    fname = schema.TextLine(
        title=_PMF(u'First name', default=u'First name'),
        required=True
    )

    lname = schema.TextLine(
        title=_PMF(u'Last name', default=u'Last name'),
        required=True
    )

    email = schema.TextLine(
        title=_PMF(u'Email', default=u'Email'),
        constraint=isEmail,
        required=True
    )

    showEmail = schema.Bool(
        title=_PMF(
            u'Share email address to everyone',
            default=u'Share email address to everyone'),
        description=_PMF(
            u'If unchecked, email will be visible to managers and foundation membership committee only.',
            default=u'If unchecked, email will be visible to managers and foundation membership committee only.'),
        default=False
    )

    website = schema.URI(
        title=_PMF(u'Personal web Site', default=u'Personal web Site'),
        description=_(u'Enter a http:// or https:// web address'),
        required=False,
        constraint=isHTTP,
    )

    twitter = schema.TextLine(
        title=_PMF(u'Twitter account', default=u'Twitter account'),
        description=_PMF(u'(without the leading ''@'')', default=u'(without the leading ''@'')'),
        required=False
    )

    facebook = schema.TextLine(
        title=_PMF(u'Facebook account', default=u'Facebook account'),
        description=_PMF(u'Only the account name, not the full url.',
                         default=u'Only the account name, not the full url.'),
        required=False
    )

    linkedin = schema.TextLine(
        title=_PMF(u'LinkedIn account', default=u'LinkedIn account'),
        description=_PMF(u'Only the account name, not the full url.',
                         default=u'Only the account name, not the full url.'),
        required=False
    )

    github = schema.TextLine(
        title=_PMF(u'Github account', default=u'Github account'),
        description=_PMF(u'Only the account name, not the full url.',
                         default=u'Only the account name, not the full url.'),
        required=False
    )

    read_permission(address='ploneorg.core.foundationmember.view')
    address = schema.TextLine(
        title=_PMF(u'Address', default=u'Address'),
        required=True
    )

    city = schema.TextLine(
        title=_PMF(u'City', default=u'City'),
        required=True
    )

    state = schema.TextLine(
        title=_PMF(u'State', default=u'State'),
        required=True
    )

    read_permission(postalCode='ploneorg.core.foundationmember.view')
    postalCode = schema.TextLine(
        title=_PMF(u'Postal code', default=u'Postal code'),
        required=True
    )

    country = schema.Choice(
        title=_PMF(u'Country', default=u'Country'),
        vocabulary=country_vocabulary,
        required=True
    )

    organization = schema.TextLine(
        title=_PMF(u'Organization', default=u'Organization'),
        required=True
    )

    merit = RichText(
        title=_(u'Contributions'),
        description=_(u'Describe your contributions to the project.'),
        required=True
    )

    read_permission(orgsize='ploneorg.core.foundationmember.view')
    orgsize = schema.Int(
        title=_(u'Organization size'),
        description=_(
            u'Number of people in your organization. It\'s fine to estimate.'),
        required=False
    )

    ploneuse = RichText(
        title=_(u'Plone use'),
        description=_(u'How is Plone used by your organization?'),
        required=False
    )


@implementer(IFoundationMember)
class FoundationMember(Item):

    @property
    def title(self):
        if hasattr(self, 'fname') and hasattr(self, 'lname'):
            if self.fname and self.lname:
                return self.fname + ' ' + self.lname
            elif self.fname and not self.lname:
                return self.fname
            elif not self.fname and self.lname:
                return self.lname
        else:
            return ''

    def setTitle(self, value):
        return

    def country_name(self):
        if not self.country:
            return None
        return country_vocabulary.getTerm(self.country).title

    def get_full_name(self):
        names = [
            self.fname,
            self.lname,
        ]
        return u' '.join([name for name in names if name])

    def twitter_url(self):
        twitter = self.twitter and self.twitter.strip() or None
        if not twitter:
            return None
        return "https://twitter.com/%s" % (twitter)

    def facebook_url(self):
        facebook = self.facebook and self.facebook.strip() or None
        if not facebook:
            return None
        return "https://www.facebook.com/%s" % (facebook)

    def linkedin_url(self):
        linkedin = self.linkedin and self.linkedin.strip() or None
        if not linkedin:
            return None
        return "https://www.linkedin.com/in/%s" % (linkedin)

    def github_url(self):
        github = self.github and self.github.strip() or None
        if not github:
            return None
        return "https://github.com/%s" % (github)

    def toXML(self, schematas=['contact', 'survey']):
        """To XML for Paul ;) """

        out = ''
        out += '<foundationmember id="%s">' % self.getId()
        fields = [f for f in self.Schema().fields()
                  if (f.schemata in schematas) and f.getName() != 'id']
        for f in fields:
            out += '<%s>%s</%s>' % (
                f.getName(),
                getattr(self, f.accessor)(),
                f.getName()
            )
        out += '</foundationmember>'
        return out


class INameFromPersonNames(INameFromTitle):
    def title():
        """Return a processed title"""


@implementer(INameFromPersonNames)
class NameFromPersonNames(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.fname + ' ' + self.context.lname
