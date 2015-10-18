# -*- coding: utf-8 -*-
from plone import api
from plone.registry.interfaces import IRegistry
from ploneorg.core import HOMEPAGE_ID
from ploneorg.core.testing import PLONEORG_CORE_INTEGRATION_TESTING
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from zope.component import getUtility

import unittest


PACKAGE_NAME = 'ploneorg.core'


class TestSetup(unittest.TestCase):

    layer = PLONEORG_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installation(self):
        quick_installer = api.portal.get_tool('portal_quickinstaller')
        installable_products = quick_installer.listInstallableProducts(
            skipInstalled=False
        )
        products = [p['id'] for p in installable_products]
        self.assertTrue(PACKAGE_NAME in products)

    def test_icons_disabled(self):
        """Check that the icon_visibility is turned off."""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema,
            prefix='plone',
            check=False
        )
        self.assertEqual(
            settings.icon_visibility,
            'false'
        )

    def test_homepage_created(self):
        """Check that the homepage is created."""
        self.assertIn(
            HOMEPAGE_ID,
            self.portal
        )

    def test_homepage_not_in_navigation(self):
        """Check that the homepage is created."""
        self.assertTrue(self.portal[HOMEPAGE_ID].exclude_from_nav)

    def test_portal_default_page(self):
        """Check that the homepage is the portal default page."""
        self.assertEqual(
            HOMEPAGE_ID,
            self.portal.getDefaultPage()
        )
