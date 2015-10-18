# -*- coding: utf-8 -*-
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from ploneorg.core import HOMEPAGE_ID
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from zope.component import getUtility

import logging


PROFILE_ID = 'profile-ploneorg.core:default'


def setupVarious(context):
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('ploneorg.core_various.txt') is None:
        return

    portal = context.getSite()
    logger = logging.getLogger(__name__)

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
    settings.icon_visibility = 'false'

    # Create homepage if not present
    homepage = getattr(portal, HOMEPAGE_ID, False)
    if not homepage:
        homepage = createContentInContainer(
            portal,
            HOMEPAGE_ID,
            title=unicode(HOMEPAGE_ID.capitalize()),
            checkConstraints=False)
        homepage.exclude_from_nav = True
        logger.info('Default homepage site setup successfully.')

    portal.setDefaultPage(HOMEPAGE_ID)
