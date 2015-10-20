# -*- coding: utf-8 -*-
from plone import api
from plone.app.users.browser.userdatapanel import getUserDataSchema
from ploneorg.core.testing import PLONEORG_CORE_INTEGRATION_TESTING

import unittest


hidden_properties = (
    'plone_commits',
    'collective_commits',
    'stackoverflow_questions',
    'tweets',
)

user_schema_properties = (
    'country',
    'github_url',
    'stackoverflow_url',
    'twitter_url',
    'additional_emails',
    'contributing_since',
)


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

    def test_memberdata_properties(self):
        """Check that the member data properties are installed."""
        member_properties = api.portal.get_tool('portal_memberdata')
        error_msg = 'Property "{0}" not found'
        for field in hidden_properties:
            self.assertIn(
                field,
                member_properties.propertyIds(),
                error_msg.format(field)
            )
        for field in user_schema_properties:
            self.assertIn(
                field,
                member_properties.propertyIds(),
                error_msg.format(field)
            )

    def test_profile_properties(self):
        """Check that the user profile edit form have all the properties."""
        user_schema = getUserDataSchema()

        for field in user_schema_properties:
            self.assertIn(
                field,
                user_schema,
                'Field "{0}" not found on userschema.xml'.format(field)
            )

    def test_hidden_properties_not_on_profile(self):
        """Check that some properties are not on the profile edit."""
        user_schema = getUserDataSchema()
        error_msg = 'Property "{0}" should not be on a member edit profile'
        for field in hidden_properties:
            self.assertNotIn(
                field,
                user_schema,
                error_msg.format(field)
            )
