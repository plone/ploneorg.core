# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IDocument
from plone.dexterity.content import Item
from zope.interface import implementer


class IHomePage(IDocument):
    """ Marker for homepage schema"""


@implementer(IHomePage)
class HomePage(Item):
    """Specific marked HomePage Base class

    (why not use a behavior to mark Item?)
    """
