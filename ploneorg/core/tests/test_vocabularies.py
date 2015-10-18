# -*- coding: utf-8 -*-
from ploneorg.core.testing import PLONEORG_CORE_INTEGRATION_TESTING
from ploneorg.core.vocabularies import country_vocabulary
from zope.schema.vocabulary import SimpleVocabulary

import unittest


class TestSetup(unittest.TestCase):

    layer = PLONEORG_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_vocabulary(self):
        """Check that the vocabulary exists."""
        self.assertTrue(country_vocabulary)
        self.assertIsInstance(
            country_vocabulary,
            SimpleVocabulary
        )

    def test_country_in_vocabulary(self):
        """Check that Romania is in the vocabulary."""
        self.assertIn(
            'ROU',
            country_vocabulary
        )
