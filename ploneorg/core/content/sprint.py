# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel.directives import fieldset
from ploneorg.core import _
from zope import schema
from zope.interface import Interface


class ISprint(Interface):
    """
    - organizer(s) (FoundationMember users?)
    - topics of the sprint (keywords so that can be used to generate reports
      and search for them?)
    """

    text = schema.Text(
        title=_(u'Sprint purpose'),
        description=_(
            u'Explain a little bit what this sprint will be about.'
        ),
        required=False,
    )

    start_date = schema.Date(
        title=_(u'Sprint starting date'),
        description=_(
            u'When is this sprint going to start?'
        ),
        required=False
    )

    end_date = schema.Date(
        title=_(u'Finishing date'),
        description=_(
            u'Sadly all sprints end at some point, when will that be '
            u'for this one?'
        ),
        required=False
    )

    location = schema.TextLine(
        title=_(u'Sprint location'),
        description=_(
            u'Where the sprint takes place physically.'
        ),
        required=False,
        max_length=100,
    )

    venue = schema.Text(
        title=_(u'Venue'),
        description=_(
            u'The building where this sprint is going to be held, how '
            u'to reach it, etc...'
        ),
        required=False,
    )

    travel_info = schema.Text(
        title=_(u'Travel information'),
        description=_(
            u'How to get to this sprint location, by plane, train, bus...'
        ),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u'Lead image'),
        description=_(
            u'Nice picture of the venue, the location, etc...'
        ),
        required=False,
    )

    fieldset(
        'travel',
        label=_(u'Travel'),
        fields=[
            'location',
            'venue',
            'travel_info',
        ]
    )


class Sprint(Container):
    pass
