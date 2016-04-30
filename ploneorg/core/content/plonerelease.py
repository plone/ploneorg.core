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
    features = schema.Text(
        title=_(u"Features"),
        required=False,
    )
    fixes = schema.Text(
        title=_(u"Fixes"),
        required=False,
    )
    incompatibilities = schema.Text(
        title=_(u"Incompatibilities"),
        required=False,
    )
    dependency_changes = schema.Text(
        title=_(u"Dependency Version Changes"),
        required=False,
    )


@implementer(IPloneRelease)
class PloneRelease(Item):

    @property
    def title(self):
        return "Plone %s" % self.version
