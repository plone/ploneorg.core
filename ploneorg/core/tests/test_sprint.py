# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from ploneorg.core.testing import PLONEORG_CORE_FUNCTIONAL_TESTING

import unittest


class SprintFunctionalTest(unittest.TestCase):

    layer = PLONEORG_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()

        # Set up browser
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD, )
        )

    def test_add_sprint(self):
        self.browser.open(self.portal_url + '/++add++sprint')

        control = 'form.widgets.IBasic.title'
        self.browser.getControl(name=control).value = 'My Sprint'
        control = 'form.widgets.IBasic.description'
        self.browser.getControl(name=control).value = 'Sprint description'
        self.browser.getControl('Save').click()

        self.assertEqual(
            'My Sprint',
            self.portal['my-sprint'].title,
        )
