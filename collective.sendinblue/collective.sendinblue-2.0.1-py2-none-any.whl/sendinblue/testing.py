# -*- coding: utf-8 -*-

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile

import collective.sendinblue


class CollectiveSendinblueLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.sendinblue)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.sendinblue:default')


COLLECTIVE_SENDINBLUE_FIXTURE = CollectiveSendinblueLayer()


COLLECTIVE_SENDINBLUE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_SENDINBLUE_FIXTURE,),
    name='CollectiveSendinblueLayer:IntegrationTesting'
)


COLLECTIVE_SENDINBLUE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_SENDINBLUE_FIXTURE,),
    name='CollectiveSendinblueLayer:FunctionalTesting'
)
