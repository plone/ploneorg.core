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
from ploneorg.core.vocabularies import country_vocabulary


class IEnhancedUserDataSchema(model.Schema):

    country = schema.Choice(
        title=_(u"Country"),
        description=_(u"Please, enter your country."),
        source=country_vocabulary,
        required=False,
    )

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

    twitter_username = schema.TextLine(
        title=_(u"Twitter username"),
        description=_(u"[Contributor] The Twitter username for personal stats retrieval"),
        required=False
    )

    additional_emails = schema.List(
        title=_(u"Additional emails"),
        description=_(u"Contributions are usually keyed on email, but often people use work and home addresses for email, or move jobs and gain new addresses. Enter all email addresses that represent you in the Plone community here, so we can include these contributions."),
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
