# -*- coding: utf-8 -*-
import datetime

from collective.z3cform.datagridfield import DictRow
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from plone.app.content.interfaces import INameFromTitle
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.autoform import directives
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.supermodel.model import Schema
from ploneorg.core import _
from ploneorg.core.vocabularies import platform_vocabulary
from zope import schema
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPRequest


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
        default=datetime.date.today()
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

    directives.widget(files=DataGridFieldFactory)
    files = schema.List(
        title=_(u'Files'),
        value_type=DictRow(title=_(u'Uploads'), schema=IReleaseUpload),
        required=False
    )


@implementer(IPloneRelease)
class PloneRelease(Item):
    """ """
    @property
    def title(self):
        return "Plone %s" % self.version

    def Title(self):
        return self.title


class INameFromVersion(INameFromTitle):
    def title():
        """ Return the version number"""


@implementer(INameFromVersion)
class NameFromVersion(object):

    def __init__(self, context):
        self.context = context
        request = getattr(context, "REQUEST", None)
        if request is None or isinstance(request, basestring):
            # Handle '<Special Object Used to Force Acquisition>' case
            request = getRequest()
        alsoProvides(request, IChooseMyOwnDamnName)

    @property
    def title(self):
        return self.context.version


class IChooseMyOwnDamnName(IHTTPRequest):
    """We need to be able to adapt the request for PloneRelease objects to
       get to our own IUserPreferredURLNormalizer.
    """


@implementer(IUserPreferredURLNormalizer)
class VersionNumberURLNormalizer(object):
    """Override the id normalizer so that we get something that looks like
    a version number.
    """

    def __init__(self, context):
        self.context = context

    def normalize(self, text):
        """Returns the text as submitted, otherwise we wind up with version
        numbers like '5-0.7'.
        Also, unicode fails the folder's checkIdAvailable test, so we make sure
        it's a string.
        """
        return str(text)
