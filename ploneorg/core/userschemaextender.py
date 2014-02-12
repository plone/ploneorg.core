from zope import schema
from zope.component import adapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.form.field import Fields

from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.userdatapanel import UserDataPanel
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible

from ploneorg.core import _


class IEnhancedUserDataSchema(model.Schema):

    github_username = schema.TextLine(
        title=_(u"Github username"),
        description=_(u"[Contributor] The GitHub username for personal stats retrieval"),
        required=False
    )

    stackoverflow_username = schema.TextLine(
        title=_(u"StackOverflow username"),
        description=_(u"[Contributor] The StackOverflow username for personal stats retrieval"),
        required=False
    )

    contrib_email_addresses = schema.List(
        title=_(u"Contributor e-mail addresses"),
        description=_(u"[Contributor] The e-mail addresses that you've used as contributor in all the supported sources."),
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[])


class EnhancedUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IEnhancedUserDataSchema


@adapter(Interface, IDefaultBrowserLayer, UserDataPanel)
class UserDataPanelExtender(extensible.FormExtender):
    def update(self):
        fields = Fields(IEnhancedUserDataSchema)
        self.add(fields, prefix="IEnhancedUserDataSchema")
