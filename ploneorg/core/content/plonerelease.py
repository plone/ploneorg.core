# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from ploneorg.core import _
from zope import schema
from zope.interface import implementer


class IPloneRelease(Schema):
    """ A Plone release """

    version = schema.TextLine(
        title=_(u'Version'),
        required=True
    )
    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )
    release_date = schema.Date(
        title=_(u'Release date'),
        required=False,
    )
    release_notes = RichText(
        title=_(u'Release notes'),
        required=False,
    )
    changelog = RichText(
        title=_(u"Changelog"),
        required=False,
    )

@implementer(IPloneRelease)
class PloneRelease(Item):

    @property
    def title(self):
        return "Plone %s" % self.version
