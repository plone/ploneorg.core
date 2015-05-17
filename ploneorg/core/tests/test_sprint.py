# -*- coding: utf-8 -*-
from datetime import date
from datetime import timedelta
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from ploneorg.core.testing import PLONEORG_CORE_FUNCTIONAL_TESTING

import lxml
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

    def test_dates_invariant_good_dates(self):
        """Check that if sprint start and end dates are chronological."""
        self.browser.open(self.portal_url + '/++add++sprint')

        control = 'form.widgets.IBasic.title'
        self.browser.getControl(name=control).value = 'My Sprint'
        control = 'form.widgets.IBasic.description'
        self.browser.getControl(name=control).value = 'Sprint description'

        sprint_start = date.today()
        sprint_end = sprint_start + timedelta(days=3)
        sprint_start = sprint_start.strftime('%Y-%m-%d')
        sprint_end = sprint_end.strftime('%Y-%m-%d')
        control = 'form.widgets.start_date'
        self.browser.getControl(name=control).value = sprint_start
        control = 'form.widgets.end_date'
        self.browser.getControl(name=control).value = sprint_end

        self.browser.getControl('Save').click()
        self.assertEqual(
            'My Sprint',
            self.portal['my-sprint'].title,
        )

    def test_dates_invariant_wrong_dates(self):
        """Check that a sprint can not be created if ends before starting."""
        self.browser.open(self.portal_url + '/++add++sprint')

        control = 'form.widgets.IBasic.title'
        self.browser.getControl(name=control).value = 'My Sprint'
        control = 'form.widgets.IBasic.description'
        self.browser.getControl(name=control).value = 'Sprint description'

        start = date.today()
        end = start + timedelta(days=3)
        sprint_start = end.strftime('%Y-%m-%d')
        sprint_end = start.strftime('%Y-%m-%d')
        control = 'form.widgets.start_date'
        self.browser.getControl(name=control).value = sprint_start
        control = 'form.widgets.end_date'
        self.browser.getControl(name=control).value = sprint_end

        self.browser.getControl('Save').click()

        html = lxml.html.fromstring(self.browser.contents)

        self.assertEqual(self.browser.url, self.portal_url + '/++add++sprint')
        self.assertTrue(html.xpath('//*[contains(@class, "error")]'))
