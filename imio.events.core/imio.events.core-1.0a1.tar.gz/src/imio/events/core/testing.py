# -*- coding: utf-8 -*-

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.api import portal as portal_api
from plone.testing import z2
from zope.globalrequest import setRequest

import imio.events.core
import mock


class ImioEventsCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=imio.events.core)

    def setUpPloneSite(self, portal):
        request = portal.REQUEST
        # set basic request to be able to get current language from it during
        # policy setuphandlers
        setRequest(request)
        portal_api.get_current_language = mock.Mock(return_value="fr")
        applyProfile(portal, "imio.events.core:default")


IMIO_EVENTS_CORE_FIXTURE = ImioEventsCoreLayer()


IMIO_EVENTS_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_EVENTS_CORE_FIXTURE,),
    name="ImioEventsCoreLayer:IntegrationTesting",
)


IMIO_EVENTS_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_EVENTS_CORE_FIXTURE,),
    name="ImioEventsCoreLayer:FunctionalTesting",
)


IMIO_EVENTS_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_EVENTS_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioEventsCoreLayer:AcceptanceTesting",
)
