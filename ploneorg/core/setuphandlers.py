# -*- coding: utf-8 -*-

from plone.dexterity.utils import createContentInContainer

from Products.CMFCore.utils import getToolByName

import logging
import transaction

PROFILE_ID = 'profile-ploneorg.core:default'
# Specify the indexes you want, with ('index_name', 'index_type')
INDEXES = (('addon_categories', 'KeywordIndex'),
           )


# Afegit creació d'indexos programàticament i controladament per:
# http://maurits.vanrees.org/weblog/archive/2009/12/catalog
def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger(__name__)

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    indexables = []
    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info('Added %s for field %s.', meta_type, name)
    if len(indexables) > 0:
        logger.info('Indexing new indexes %s.', ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('ploneorg.core_various.txt') is None:
        return

    portal = context.getSite()
    logger = logging.getLogger(__name__)

    add_catalog_indexes(portal, logger)

    # Add the DX front-page object if needed
    # pl = getToolByName(portal, 'portal_languages')
    # from plone.dexterity.interfaces import IDexterityContent
    # front_page = getattr(portal, 'front-page', False)
    # if front_page and not IDexterityContent.providedBy(front_page):
    #     portal.manage_delObjects('front-page')
    #     frontpage = createContentInContainer(portal, 'Document',
    #                                          title=u'front-page',
    #                                          checkConstraints=False)
    #     frontpage.exclude_from_nav = True
    #     frontpage.language = pl.getDefaultLanguage()
    #     frontpage.reindexObject()
    #     logger.info('DX default content site setup successfully.')
    # elif not front_page:
    #     frontpage = createContentInContainer(portal, 'Document',
    #                                          title=u'front-page',
    #                                          checkConstraints=False)
    #     frontpage.exclude_from_nav = True
    #     frontpage.language = pl.getDefaultLanguage()
    #     frontpage.reindexObject()
    #     logger.info('DX default content site setup successfully.')

    # # Set the default page to the homepage view
    # portal.setDefaultPage('front-page')

    transaction.commit()
