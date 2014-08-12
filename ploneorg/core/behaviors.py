from zope.component import adapts
from zope.interface import implements

from plone.app.content.interfaces import INameFromTitle

from ploneorg.core.content.foundationmember import IFoundationMember


class INameFromFullName(INameFromTitle):
    """Get the name from the full name.

    This is really just a marker interface, automatically set by
    enabling the corresponding behavior.

    Note that when you want this behavior, then you MUST NOT enable
    the IDublinCore, IBasic, INameFromTitle or INameFromFile behaviors
    on your type.
    """


class NameFromFullName(object):
    implements(INameFromFullName)
    adapts(IFoundationMember)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.get_full_name()
