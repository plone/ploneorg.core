# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.Image import Pdata
from Products.PlonePAS.tools.membership import default_portrait
from plone import api
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.userdatapanel import UserDataPanel
# from plone.autoform import directives as form
# from plone.namedfile.field import NamedBlobImage
from plone.namedfile.file import NamedBlobImage as NamedBlobImageFile
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from ploneorg.core import _
from ploneorg.core.vocabularies import country_vocabulary
from z3c.form.field import Fields
from zope import schema
from zope.component import adapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEnhancedUserDataSchema(model.Schema):

    # Put this into fridge by now
    # large_portrait = NamedBlobImage(
    #     title=_(u'label_large_portrait', default=u'Large Portrait'),
    #     description=_(
    #         u'help_large_portrait',
    #         default=u'You can set a large hero portrait image for display on'
    #                 u'your community profile. Recommended '
    #                 u'image size is X pixels wide by Y pixels tall.'
    #     ),
    #     required=False)
    # form.widget(large_portrait='plone.app.users.schema.PortraitFieldWidget')

    country = schema.Choice(
        title=_(u'Country'),
        description=_(u'Please, enter your country.'),
        source=country_vocabulary,
        required=False,
    )

    github_username = schema.TextLine(
        title=_(u'Github username'),
        description=_(u'[Contributor] The GitHub username for '
                      'personal stats retrieval'),
        required=False
    )

    stackoverflow_username = schema.TextLine(
        title=_(u'StackOverflow username'),
        description=_(u'[Contributor] The StackOverflow username '
                      'for personal stats retrieval'),
        required=False
    )

    twitter_username = schema.TextLine(
        title=_(u'Twitter username'),
        description=_(u'[Contributor] The Twitter username for personal '
                      'stats retrieval'),
        required=False
    )

    additional_emails = schema.List(
        title=_(u'Additional emails'),
        description=_(
            u'Contributions are usually keyed on email, but often people '
            u'use work and home addresses for email, or move jobs and gain '
            u'new addresses. Enter all email addresses that represent you '
            u'in the Plone community here, so we can include these '
            u'contributions.'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
        default=[])

    contributing_since = schema.TextLine(
        title=_(u'Contributing since'),
        description=_(
            u'State the year since you are contributing to Plone.'),
        required=False,
        )


class EnhancedUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IEnhancedUserDataSchema

    def get_large_portrait(self):
        portal = api.portal.get()
        mt = api.portal.get_tool(name='portal_membership')
        if not self.context.getId():
            return None
        value = mt.getPersonalPortrait(self.context.getId() + '_large')
        if aq_inner(value) == aq_inner(getattr(portal,
                                               default_portrait,
                                               None)):
            return None
        # Sometimes it got saved with this, no time to know why.
        if isinstance(value.data, Pdata):
            return NamedBlobImageFile(
                value.data.data,
                contentType=value.content_type,
                filename=getattr(value, 'filename', None)
            )
        else:
            return NamedBlobImageFile(
                value.data,
                contentType=value.content_type,
                filename=getattr(value, 'filename', None)
            )

    def set_large_portrait(self, value):
        mt = api.portal.get_tool(name='portal_membership')
        if value is None:
            mt.deletePersonalPortrait(str(self.context.getId() + '_large'))
        else:
            portrait_file = value.open()
            portrait_file.filename = value.filename
            mt.changeMemberPortrait(portrait_file,
                                    str(self.context.getId() + '_large'))

    large_portrait = property(get_large_portrait, set_large_portrait)


@adapter(Interface, IDefaultBrowserLayer, UserDataPanel)
class UserDataPanelExtender(extensible.FormExtender):
    def update(self):
        fields = Fields(
            IEnhancedUserDataSchema,
            prefix='IEnhancedUserDataSchema')
        self.add(fields)
