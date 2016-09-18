# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from ploneorg.core.content.foundationmember import IFoundationMember
from ploneorg.core.content.homepage import IHomePage
from ploneorg.core.testing import PLONEORG_CORE_INTEGRATION_TESTING
from zope.component import createObject
from zope.component import queryUtility

import unittest


class ContentTypesTest(unittest.TestCase):

    layer = PLONEORG_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema_foundation_member(self):
        fti = queryUtility(IDexterityFTI, name='FoundationMember')
        schema = fti.lookupSchema()
        self.assertEqual(IFoundationMember, schema)

    def test_fti_foundation_member(self):
        fti = queryUtility(IDexterityFTI, name='FoundationMember')
        self.assertTrue(fti)

    def test_factory_foundation_member(self):
        fti = queryUtility(IDexterityFTI, name='FoundationMember')
        factory = fti.factory
        member = createObject(factory)
        self.assertTrue(IFoundationMember.providedBy(member))

    def test_adding_foundation_member(self):
        fti = queryUtility(IDexterityFTI, name='FoundationMember')
        fti.global_allow = True
        self.portal.invokeFactory('FoundationMember', 'member')
        self.assertTrue(IFoundationMember.providedBy(self.portal.member))

    def test_schema_homepage(self):
        fti = queryUtility(IDexterityFTI, name='homepage')
        schema = fti.lookupSchema()
        self.assertEqual(IHomePage, schema)

    def test_fti_homepage(self):
        fti = queryUtility(IDexterityFTI, name='homepage')
        self.assertTrue(fti)

    def test_factory_homepage(self):
        fti = queryUtility(IDexterityFTI, name='homepage')
        factory = fti.factory
        homepage = createObject(factory)
        self.assertTrue(IHomePage.providedBy(homepage))

    def test_adding_homepage(self):
        fti = queryUtility(IDexterityFTI, name='homepage')
        fti.global_allow = True
        self.portal.invokeFactory('homepage', 'home')
        self.assertTrue(IHomePage.providedBy(self.portal.home))
