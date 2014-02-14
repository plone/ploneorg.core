from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.multifile import MultiFileFieldWidget
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


class IProduct(model.Schema):
    """ A Plone product
    """

    form.fieldset(
        'URLs',
        label=u"Product URLs",
        fields=['pypi_link', 'github_link', 'homepage']
    )

    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    summary = RichText(
        title=_(u"Short summary"),
        description=_(u"The summary of the features of the product."),
        required=True
    )

    form.widget(screenshots=MultiFileFieldWidget)
    screenshots = schema.List(
        title=u'Screenshots',
        description=_(u"Upload some screenshots showing the main product "
                      u"functionality and features."),
        value_type=NamedFile()
    )

    categories = schema.List(
        title=_(u"Categories"),
        value_type=schema.Choice(
            vocabulary=product_categories),
        required=False,
    )

    pypi_link = schema.TextLine(
        title=_(u"Pypi URL"),
        description=_(u"The PyPi egg URL for the releases of this product."),
        required=True
    )

    github_link = schema.TextLine(
        title=_(u"GitHub URL"),
        description=_(u"The GitHub repo URL for this product."),
        required=True
    )

    homepage = schema.TextLine(
        title=_(u"Homepage URL"),
        description=_(u"The home page URL for this product, if any."),
        required=True
    )
