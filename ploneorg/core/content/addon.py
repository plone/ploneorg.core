# -*- coding: utf-8 -*-
from five import grok
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.multifile import MultiFileFieldWidget
from plone.indexer import indexer
from plone.namedfile.field import NamedFile
from plone.supermodel import model

from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from ploneorg.core import _


product_categories = SimpleVocabulary(
    [SimpleTerm(value=u'auth_and_user',
                title=_(u'Authentication and user management')),
     SimpleTerm(value=u'communication',
                title=_(u'Communication')),
     SimpleTerm(value=u'calendaring',
                title=_(u'Calendaring')),
     SimpleTerm(value=u'collaboration',
                title=_(u'Collaboration')),
     SimpleTerm(value=u'databases_and_external_storage',
                title=_(u'Databases and external tools')),
     SimpleTerm(value=u'ecommerce',
                title=_(u'E-commerce')),
     SimpleTerm(value=u'forms_and_surveys',
                title=_(u'Forms, surveys and polls')),
     SimpleTerm(value=u'geo',
                title=_(u'Geospatial')),
     SimpleTerm(value=u'i18n',
                title=_(u'Internationalization')),
     SimpleTerm(value=u'layout_and_presentation',
                title=_(u'Layout and presentation')),
     SimpleTerm(value=u'media',
                title=_(u'Media (photo/video/audio')),
     SimpleTerm(value=u'project_management',
                title=_(u'Project management')),
     SimpleTerm(value=u'search_and_navigation',
                title=_(u'Search and navigation')),
     SimpleTerm(value=u'social_media',
                title=_(u'Social media')),
     SimpleTerm(value=u'theming',
                title=_(u'Theming and look and feel')),
     SimpleTerm(value=u'upload',
                title=_(u'Uploads')),
     SimpleTerm(value=u'weblogs',
                title=_(u'Weblogs')),
     SimpleTerm(value=u'workflow',
                title=_(u'Workflow')),
     SimpleTerm(value=u'widgets',
                title=_(u'Widgets')),
     SimpleTerm(value=u'other',
                title=_(u'Other'))]
)

certification_checklist = SimpleVocabulary(
    [SimpleTerm(value=u'pypi_page',
                title=_(u'Has a curated PyPi page (README.rst/README.md)')),
     SimpleTerm(value=u'public_repo',
                title=_(u'Has a public and open to contributions repo (GitHub/BitBucket, etc)')),
     SimpleTerm(value=u'updated_last_plone_version',
                title=_(u'Works on latest Plone version')),
     SimpleTerm(value=u'dexterity_ready',
                title=_(u'Dexterity ready')),
     SimpleTerm(value=u'proper_screenshots',
                title=_(u'Has proper screenshots')),
     SimpleTerm(value=u'used_in_production',
                title=_(u'Widely used in production')),
     SimpleTerm(value=u'install_uninstall_profile',
                title=_(u'Uninstall profile, installs and uninstalls cleanly')),
     SimpleTerm(value=u'code_structure',
                title=_(u'Code structure follows best practice')),
     SimpleTerm(value=u'maintained',
                title=_(u'Existed and maintained for at least 6 months')),
     SimpleTerm(value=u'internal_documentation',
                title=_(u'Internal documentation (documentation, interfaces, etc.)')),
     SimpleTerm(value=u'enduser_documentation',
                title=_(u'End-user documentation')),
     SimpleTerm(value=u'tested',
                title=_(u'Fair test coverage')),
     SimpleTerm(value=u'i18n',
                title=_(u'Internationalized')), ]
)


class IAddon(model.Schema):
    """ A Plone product
    """

    form.fieldset(
        'URLs',
        label=u'URLs',
        fields=['pypi_link', 'github_link', 'homepage']
    )

    form.fieldset(
        'quality',
        label=u'Quality review',
        fields=['certification', ]
    )

    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    summary = RichText(
        title=_(u'Short summary'),
        description=_(u'The summary of the features of the product.'),
        required=True
    )

    form.widget(screenshots=MultiFileFieldWidget)
    screenshots = schema.List(
        title=u'Screenshots',
        description=_(u'Upload some screenshots showing the main product '
                      u'functionality and features.'),
        value_type=NamedFile()
    )

    categories = schema.List(
        title=_(u'Categories'),
        value_type=schema.Choice(
            vocabulary=product_categories),
        required=False,
    )

    pypi_link = schema.TextLine(
        title=_(u'Pypi URL'),
        description=_(u'The PyPi egg URL for the releases of this product.'),
        required=True
    )

    github_link = schema.TextLine(
        title=_(u'GitHub URL'),
        description=_(u'The GitHub repo URL for this product.'),
        required=True
    )

    homepage = schema.TextLine(
        title=_(u'Homepage URL'),
        description=_(u'The home page URL for this product, if any.'),
    )

    form.widget(certification=CheckBoxFieldWidget)
    certification = schema.Set(
        title=_(u'Certification checklist'),
        description=_(u'This is the feature checklist of add-on developing. Once the product accomplish all of them, you can send it for review and earn the certified add-on badge.'),
        value_type=schema.Choice(
            vocabulary=certification_checklist),
        required=False
    )


@indexer(IAddon)
def addon_categories(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``context.categories`` value and index it.
    """
    return context.categories
grok.global_adapter(addon_categories, name='addon_categories')


# class View(grok.View):
#     grok.context(IAddon)
