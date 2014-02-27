# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from ploneorg.core.content.addon import IAddon

from ploneorg.core.testing import (
    PLONEORG_CORE_INTEGRATION_TESTING,
    PLONEORG_CORE_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles


class DocumentIntegrationTest(unittest.TestCase):

    layer = PLONEORG_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='addon')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'IAddon')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='addon'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='addon'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IAddon.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'addon',
            'product1'
        )
        self.assertTrue(IAddon.providedBy(self.portal['product1']))
