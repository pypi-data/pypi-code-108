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

import imio.news.core
import mock


class ImioNewsCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=imio.news.core)

    def setUpPloneSite(self, portal):
        request = portal.REQUEST
        # set basic request to be able to handle redirect in subscribers
        setRequest(request)
        portal_api.get_current_language = mock.Mock(return_value="fr")
        applyProfile(portal, "imio.news.core:default")


IMIO_NEWS_CORE_FIXTURE = ImioNewsCoreLayer()


IMIO_NEWS_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_NEWS_CORE_FIXTURE,),
    name="ImioNewsCoreLayer:IntegrationTesting",
)


IMIO_NEWS_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_NEWS_CORE_FIXTURE,),
    name="ImioNewsCoreLayer:FunctionalTesting",
)


IMIO_NEWS_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_NEWS_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioNewsCoreLayer:AcceptanceTesting",
)
