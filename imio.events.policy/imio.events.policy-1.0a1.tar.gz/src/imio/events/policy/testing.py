# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import imio.events.policy


class ImioEventsPolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=imio.events.policy)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "imio.events.policy:default")


IMIO_EVENTS_POLICY_FIXTURE = ImioEventsPolicyLayer()


IMIO_EVENTS_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_EVENTS_POLICY_FIXTURE,),
    name="ImioEventsPolicyLayer:IntegrationTesting",
)


IMIO_EVENTS_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_EVENTS_POLICY_FIXTURE,),
    name="ImioEventsPolicyLayer:FunctionalTesting",
)


IMIO_EVENTS_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_EVENTS_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioEventsPolicyLayer:AcceptanceTesting",
)
