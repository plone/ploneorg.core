# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IDocument
from plone.dexterity.content import Item
from zope.interface import implements


class IHomePage(IDocument):
    """ Marker for homepage schema"""


class HomePage(Item):
    implements(IHomePage)
