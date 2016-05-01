# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from ploneorg.core import _
from zope import schema
from zope.interface import implementer
from collective.z3cform.datagridfield import DictRow
from collective.z3cform.datagridfield.datagridfield import \
        DataGridFieldFactory
from plone.directives import form
from ploneorg.core.vocabularies import platform_vocabulary


class IReleaseUpload(Schema):
    """ File download link for a Plone release
    """
    description = schema.TextLine(
        title=_(u'Description'),
        required=False
    )
    platform = schema.Choice(
        title=_(u'Platform'),
        vocabulary = platform_vocabulary,
        required=False
    )
    url = schema.TextLine(
        title=_(u'URL'),
        required=False
    )
    file_size = schema.TextLine(
        title=_(u'File size'),
        required=False
    )


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
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=('text/plain', 'text/html', 'text/restructured', 'text/x-web-markdown'),
        required=False,
    )
    changelog = RichText(
        title=_(u"Changelog"),
        default_mime_type='text/restructured',
        output_mime_type='text/html',
        allowed_mime_types=('text/plain', 'text/html', 'text/restructured', 'text/x-web-markdown'),
        required=False,
    )

    form.widget(files=DataGridFieldFactory)
    files = schema.List(
        title=_(u'Files'),
        value_type=DictRow(title=_(u'Uploads'), schema=IReleaseUpload),
        required=False
    )

@implementer(IPloneRelease)
class PloneRelease(Item):

    @property
    def title(self):
        return "Plone %s" % self.version
