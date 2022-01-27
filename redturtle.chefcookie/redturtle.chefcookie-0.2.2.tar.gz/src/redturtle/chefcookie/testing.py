# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import redturtle.chefcookie


class RedturtleChefcookieLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=redturtle.chefcookie)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "redturtle.chefcookie:default")


REDTURTLE_CHEFCOOKIE_FIXTURE = RedturtleChefcookieLayer()


REDTURTLE_CHEFCOOKIE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REDTURTLE_CHEFCOOKIE_FIXTURE,),
    name="RedturtleChefcookieLayer:IntegrationTesting",
)


REDTURTLE_CHEFCOOKIE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REDTURTLE_CHEFCOOKIE_FIXTURE,),
    name="RedturtleChefcookieLayer:FunctionalTesting",
)


REDTURTLE_CHEFCOOKIE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        REDTURTLE_CHEFCOOKIE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="RedturtleChefcookieLayer:AcceptanceTesting",
)
