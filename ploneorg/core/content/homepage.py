# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import implements


class IHomePage(Schema):
    """Marker for homepage schema"""

    # Download

    fieldset(
        'Download',
        label=u'Download',
        fields=[
            'download_title',
            'download_text',
            'download_button_text',
            'download_url',
            'download_below_button_text',
        ]
    )
    download_title = schema.TextLine(
        title=u"Title",
        required=True,
    )
    download_text = RichText(
        title=u"Text",
        required=True,
    )
    download_button_text = schema.TextLine(
        title=u"Button text",
        required=True,
    )
    download_url = schema.URI(
        title=u"Download URL",
        required=True,
    )
    download_below_button_text = RichText(
        title=u"Text below download button",
        required=True,
    )

    # Events

    fieldset(
        'Events',
        label=u'Events',
        fields=[
            'event_title',
            'event_text',
            'event_page',
        ]
    )
    event_title = schema.TextLine(
        title=u"Title",
        required=True,
    )
    event_text = RichText(
        title=u"Text",
        required=True,
    )
    event_page = RelationChoice(
        title=u"Events page",
        vocabulary="plone.app.vocabularies.Catalog",
        required=True,
    )

    # Community

    fieldset(
        'Community',
        label=u'Community',
        fields=[
            'community_title',
            'community_text',
            'community_page',
        ]
    )
    community_title = schema.TextLine(
        title=u"Title",
        required=True,
    )
    community_text = RichText(
        title=u"Text",
        required=True,
    )
    community_page = RelationChoice(
        title=u"Community page",
        vocabulary="plone.app.vocabularies.Catalog",
        required=False,
    )

    # Sponsors

    fieldset(
        'Sponsors',
        label=u'Sponsors',
        fields=[
            'sponsor_title',
            'sponsor_text',
            'sponsor_page',
        ]
    )
    sponsor_title = schema.TextLine(
        title=u"Title",
        required=True,
    )
    sponsor_text = RichText(
        title=u"Text",
        required=True,
    )
    sponsor_page = RelationChoice(
        title=u"Sponsor page",
        vocabulary="plone.app.vocabularies.Catalog",
        required=True,
    )


class HomePage(Item):
    """
    Dexterity content item for Cases
    """
    implements(IHomePage)
