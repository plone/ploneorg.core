# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from ploneorg.core.content.foundationmember import IFoundationMember
from ploneorg.core.content.homepage import IHomePage
from ploneorg.core.content.plonerelease import VersionNumberURLNormalizer
from ploneorg.core.testing import PLONEORG_CORE_INTEGRATION_TESTING
from zope.component import queryUtility
from zope.container.interfaces import INameChooser

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


class PloneReleaseTest(unittest.TestCase):

    layer = PLONEORG_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = queryUtility(IDexterityFTI, name='plonerelease')
        fti.global_allow = True
        api.content.create(container=self.portal, type='Folder', id='releases')
        container = self.portal.releases
        api.content.create(
            container=container, type='plonerelease', id='release-1')
        self.obj = container['release-1']

    def _test_version_string(self, obj, version):
        obj.version = version
        chooser = INameChooser(self.portal)
        name = chooser.chooseName(None, obj)
        self.assertEqual(name, version)

    def test_id_from_version_bugfix(self):
        self._test_version_string(self.obj, '5.0.3')

    def test_id_from_version_beta(self):
        self._test_version_string(self.obj, '5.1b3')

    def test_id_from_version_release_candidate(self):
        self._test_version_string(self.obj, '5.2rc3')

    def test_id_from_version_weird(self):
        self._test_version_string(self.obj, '5.0.6.1')

    def test_id_from_version_conflict(self):
        self._test_version_string(self.obj, '5.0.6')
        container = self.portal.releases
        api.content.create(
            container=container, type='plonerelease', id='release-2')
        duplicate = container['release-2']
        self._test_version_string(duplicate, '5.0.6-1')
