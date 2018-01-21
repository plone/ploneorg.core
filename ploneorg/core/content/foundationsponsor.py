# -*- coding: utf-8 -*-
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity import _ as _PMF
from plone.app.textfield import RichText
from plone.autoform.directives import read_permission
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from ploneorg.core import _
from ploneorg.core.vocabularies import country_vocabulary, payment_frequency_vocabulary, payment_method_vocabulary, \
    sponsorship_type_vocabulary, org_size_vocabulary, payment_currency_vocabulary
from zope import schema
from zope.interface import implementer, alsoProvides
from plone.namedfile import field as namedfile
import re
from plone.rfc822.interfaces import IPrimaryField


# email re w/o leading '^'
EMAIL_RE = "([0-9a-zA-Z_&.'+-]+!)*[0-9a-zA-Z_&.'+-]+@(([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-z-A-Z])?\.)+[a-zA-Z]{2,}|([0-9]{1,3}\.){3}[0-9]{1,3})$"

def isEmail(value):
     prog = re.compile('^'+EMAIL_RE)
     result = prog.match(value)
     if result is None:
         raise zope.interface.Invalid(_PMF(u'is not a valid email address.'))
     return True

def isHTTP(value):
    if not value.startswith('http'):
        raise zope.interface.Invalid(_PMF(u'is not a valid HTTP or HTTPS web address.'))
    return True


class IFoundationSponsor(Schema):
    """A Foundation sponsor"""

    fieldset(
        'Contacts',
        label=u'Contacts',
        fields=[
            'fname',
            'lname',
            'email',
            'alt_fname',
            'alt_lname',
            'alt_email',
        ]
    )

    fieldset(
        'Address',
        label=u'Address',
        fields=[
            'address',
            'address2',
            'city',
            'state',
            'postalCode',
            'country',
        ]
    )

    fieldset(
        'Payment',
        label=u'Payment',
        fields=[
            'payment_frequency',
            'payment_method',
            'payment_amount',
            'payment_currency',
            'payment_date',
        ]
    )

    fieldset(
        'Status',
        label=u'Status',
        fields=[
            'start_date',
            'end_date',
            'last_verified_date',
            'notes',
        ]
    )

    org_name = schema.TextLine(
        title=_PMF(u'Organization name', default=u'Organization name'),
        required=True
    )

    logo = namedfile.NamedBlobImage(
        title=_(u"Logo"),
        required=False,
    )

    sponsorship_type = schema.Choice(
        title=_PMF(u'Sponsor Type', default=u'Sponsor Type'),
        vocabulary=sponsorship_type_vocabulary,
        required=True,
    )

    read_permission(orgsize='ploneorg.core.foundationsponsor.view')
    orgsize = schema.Choice(
        title=_(u'Organization size'),
        description=_(
            u'Number of people in your organization. It\'s fine to estimate.'),
        vocabulary=org_size_vocabulary,
        required=True,
    )

    is_provider = schema.Bool(
        title=_PMF(u'Is a Plone provider', default=u'Is a Plone provider'),
    )

    website = schema.URI(
        title=_PMF(u'Web Site', default=u'Web Site'),
        description=_(u'Enter a http:// or https:// web address'),
        required=False,
        constraint=isHTTP,
    )

    read_permission(fname='ploneorg.core.foundationsponsor.view')
    fname = schema.TextLine(
        title=_PMF(u'Contact first name', default=u'Contact first name'),
        required=True
    )

    read_permission(lname='ploneorg.core.foundationsponsor.view')
    lname = schema.TextLine(
        title=_PMF(u'Contact last name', default=u'Contact last name'),
        required=True
    )

    read_permission(email='ploneorg.core.foundationsponsor.view')
    email = schema.TextLine(
        title=_PMF(u'Email', default=u'Email'),
        constraint=isEmail,
        required=True
    )

    read_permission(address='ploneorg.core.foundationsponsor.view')
    address = schema.TextLine(
        title=_PMF(u'Address', default=u'Address'),
        required=True
    )

    read_permission(address2='ploneorg.core.foundationsponsor.view')
    address2 = schema.TextLine(
        title=_PMF(u'Address 2', default=u'Address 2'),
        required=False
    )

    city = schema.TextLine(
        title=_PMF(u'City', default=u'City'),
        required=True
    )

    read_permission(state='ploneorg.core.foundationsponsor.view')
    state = schema.TextLine(
        title=_PMF(u'State', default=u'State'),
        required=True
    )

    read_permission(postalCode='ploneorg.core.foundationsponsor.view')
    postalCode = schema.TextLine(
        title=_PMF(u'Postal code', default=u'Postal code'),
        required=True
    )

    country = schema.Choice(
        title=_PMF(u'Country', default=u'Country'),
        vocabulary=country_vocabulary,
        default='USA',
        required=True
    )

    read_permission(alt_fname='ploneorg.core.foundationsponsor.view')
    alt_fname = schema.TextLine(
        title=_PMF(u'Alternate contact first name', default=u'Alternate contact first name'),
        required=False
    )

    read_permission(alt_lname='ploneorg.core.foundationsponsor.view')
    alt_lname = schema.TextLine(
        title=_PMF(u'Alternate contact last name', default=u'Alternate contact last name'),
        required=False
    )

    read_permission(alt_email='ploneorg.core.foundationsponsor.view')
    alt_email = schema.TextLine(
        title=_PMF(u'Alternate email', default=u'Alternate email'),
        constraint=isEmail,
        required=False
    )

    twitter = schema.TextLine(
        title=_PMF(u'Twitter account', default=u'Twitter account'),
        description=_PMF(u'(without the leading ''@'')', default=u'(without the leading ''@'')'),
        required=False
    )

    read_permission(connection_to_plone='ploneorg.core.foundationsponsor.view')
    connection_to_plone = RichText(
        title=_PMF(u'Connection to Plone', default=u'Connection to Plone'),
        description=_(u'What is your connection to Plone? How is Plone used by your organization?'),
        required=False
    )

    read_permission(payment_frequency='ploneorg.core.foundationsponsor.view')
    payment_frequency = schema.Choice(
        title=_PMF(u'Payment frequency', default=u'Payment frequency'),
        vocabulary=payment_frequency_vocabulary,
    )

    read_permission(payment_method='ploneorg.core.foundationsponsor.view')
    payment_method = schema.Choice(
        title=_PMF(u'Payment method', default=u'Payment method'),
        vocabulary=payment_method_vocabulary,
        default='PayPal',
        required=True
    )

    read_permission(payment_amount='ploneorg.core.foundationsponsor.view')
    payment_amount = schema.Float(
        title=_PMF(u'Payment Amount', default=u'Payment Amount'),
        min=0.0,
        required=True
    )

    read_permission(payment_currency='ploneorg.core.foundationsponsor.view')
    payment_currency = schema.Choice(
        title=_PMF(u'Currency', default=u'Currency'),
        vocabulary=payment_currency_vocabulary,
        default='USD',
        required=True
    )

    start_date = schema.Date(
        title=_PMF(u'Start Date', default=u'Start Date'),
        required=True
    )

    end_date = schema.Date(
        title=_PMF(u'End Date', default=u'End Date'),
        required=True
    )

    read_permission(payment_date='ploneorg.core.foundationsponsor.view')
    payment_date = schema.Date(
        title=_PMF(u'Payment Date', default=u'Payment Date'),
        required=True
    )

    read_permission(last_verified_date='ploneorg.core.foundationsponsor.view')
    last_verified_date = schema.Date(
        title=_PMF(u'Status last verified date', default=u'Status last verified date'),
        required=True
    )

    read_permission(notes='ploneorg.core.foundationsponsor.view')
    notes = RichText(
        title=_PMF(u'Notes', default=u'Notes'),
        required=False
    )


alsoProvides(IFoundationSponsor['logo'], IPrimaryField)


@implementer(IFoundationSponsor)
class FoundationSponsor(Item):

    @property
    def title(self):
        return self.org_name

    def setTitle(self, value):
        return

    def get_full_name(self):
        names = [
            self.org_name,
            self.fname,
            self.lname,
        ]
        return u' '.join([name for name in names if name])

    def toXML(self, schematas=['contact', 'survey']):
        """To XML for Paul ;) """

        out = ''
        out += '<foundationsponsor id="%s">' % self.getId()
        fields = [f for f in self.Schema().fields()
                  if (f.schemata in schematas) and f.getName() != 'id']
        for f in fields:
            out += '<%s>%s</%s>' % (
                f.getName(),
                getattr(self, f.accessor)(),
                f.getName()
            )
        out += '</foundationsponsor>'
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
        return self.context.org_name

