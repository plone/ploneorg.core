# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile


class PloneOrgCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import ploneorg.core
        self.loadZCML(package=ploneorg.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneorg.core:default')


PLONEORG_CORE_FIXTURE = PloneOrgCoreLayer()
PLONEORG_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEORG_CORE_FIXTURE, ),
    name='PloneorgCore:Integration'
)
PLONEORG_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEORG_CORE_FIXTURE, ),
    name='PloneorgCore:Functional'
)
