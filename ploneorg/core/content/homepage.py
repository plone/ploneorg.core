from zope.interface import implements

from plone.dexterity.content import Item
from plone.app.contenttypes.interfaces import IDocument


class IHomePage(IDocument):
    """ Marker for homepage schema"""


class HomePage(Item):
    implements(IHomePage)
