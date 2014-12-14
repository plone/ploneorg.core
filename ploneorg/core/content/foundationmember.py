# -*- coding: utf-8 -*-
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.directives import form
from ploneorg.core import _
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import pycountry
import unicodedata


def country_vocabulary_maker(l):
    vocab_list = []
    for row in l:
        value = unicodedata.normalize('NFKD', row)
        value = value.encode('ascii', errors='ignore')
        value = value.decode('ascii')
        entry = SimpleTerm(value=value, title=_(row))
        vocab_list.append(entry)
    return SimpleVocabulary(vocab_list)

countries = country_vocabulary_maker(
    [country.name for country in pycountry.countries]
)


class IFoundationMember(form.Schema):
    """ A foundation member
    """

    form.fieldset(
        'Contact',
        label=u'Contact',
        fields=['fname', 'lname']
    )

    fname = schema.TextLine(
        title=_PMF(u'label_title', default=u'First name'),
        required=True
    )

    lname = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    form.read_permission(email='ploneorg.core.foundationmember.view')
    email = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    form.read_permission(address='ploneorg.core.foundationmember.view')
    address = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    city = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    form.read_permission(state='ploneorg.core.foundationmember.view')
    state = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    form.read_permission(postalCode='ploneorg.core.foundationmember.view')
    postalCode = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    country = schema.Choice(
        title=_PMF(u'label_title', default=u'Last name'),
        vocabulary=countries,
        required=True
    )

    organization = schema.TextLine(
        title=_PMF(u'label_title', default=u'Last name'),
        required=True
    )

    form.read_permission(merit='ploneorg.core.foundationmember.view')
    merit = RichText(
        title=_(u'Short summary'),
        description=_(u'The summary of the features of the product.'),
        required=True
    )

    form.read_permission(orgsize='ploneorg.core.foundationmember.view')
    orgsize = schema.Int(
        title=_(u'Short summary'),
        description=_(u'The summary of the features of the product.'),
    )

    form.read_permission(ploneuse='ploneorg.core.foundationmember.view')
    ploneuse = RichText(
        title=_(u'Short summary'),
        description=_(u'The summary of the features of the product.'),
        required=True
    )


class FoundationMember(Item):
    implements(IFoundationMember)

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
