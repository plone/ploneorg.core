# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.testing import z2
from zope.configuration import xmlconfig


class PloneAppContenttypes(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import ploneorg.core
        xmlconfig.file(
            'configure.zcml',
            ploneorg.core,
            context=configurationContext
        )
        z2.installProduct(app, 'Products.DateRecurringIndex')

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        applyProfile(portal, 'ploneorg.core:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(
            'Folder',
            id='TEST_FOLDER_ID',
            title=u'Test Folder'
        )


PLONEORG_CORE_FIXTURE = PloneAppContenttypes()
PLONEORG_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEORG_CORE_FIXTURE,),
    name='PloneorgCore:Integration'
)
PLONEORG_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEORG_CORE_FIXTURE,),
    name='PloneorgCore:Functional'
)
