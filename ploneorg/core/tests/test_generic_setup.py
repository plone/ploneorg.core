# -*- coding: utf-8 -*-
from plone import api
from ploneorg.core.testing import PLONEORG_CORE_INTEGRATION_TESTING

import unittest


class TestSetup(unittest.TestCase):

    layer = PLONEORG_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_foundation_member_workflow(self):
        """Check that the workflow is installed."""
        workflow_tool = api.portal.get_tool('portal_workflow')
        self.assertIn(
            'foundation_member_workflow',
            workflow_tool.listWorkflows()
        )

    def test_workflow_for_foundation_member(self):
        """Check that the foundation member content type has the right
        workflow.
        """
        workflow_tool = api.portal.get_tool('portal_workflow')
        self.assertIn(
            'foundation_member_workflow',
            workflow_tool.getChainForPortalType('FoundationMember')
        )
