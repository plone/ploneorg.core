# -*- coding: utf-8 -*-
from plone.app.dexterity import _ as _PMF
from plone.app.textfield import RichText
from plone.autoform.directives import read_permission
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from ploneorg.core import _
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

    read_permission(email='ploneorg.core.foundationmember.view')
    email = schema.TextLine(
        title=_PMF(u'Email', default=u'Email'),
        required=True
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

    read_permission(state='ploneorg.core.foundationmember.view')
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

    read_permission(merit='ploneorg.core.foundationmember.view')
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
    )

    read_permission(ploneuse='ploneorg.core.foundationmember.view')
    ploneuse = RichText(
        title=_(u'Plone use'),
        description=_(u'How is Plone used by your organization?'),
        required=True
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

    def get_full_name(self):
        names = [
            self.fname,
            self.lname,
        ]
        return u' '.join([name for name in names if name])

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


from plone.app.content.interfaces import INameFromTitle
from zope.interface import implements


class INameFromPersonNames(INameFromTitle):
    def title():
        """Return a processed title"""


class NameFromPersonNames(object):
    implements(INameFromPersonNames)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.fname + ' ' + self.context.lname
