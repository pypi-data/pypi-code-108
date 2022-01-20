# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PloneRestApiDXLayer
from plone.testing import z2

import rer.sitesearch
import plone.restapi
import collective.z3cform.jsonwidget


class RERSiteSearchLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.sitesearch)
        self.loadZCML(package=collective.z3cform.jsonwidget)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "rer.sitesearch:default")


RER_SITESEARCH_FIXTURE = RERSiteSearchLayer()


RER_SITESEARCH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_SITESEARCH_FIXTURE,),
    name="RERSiteSearchLayer:IntegrationTesting",
)


RER_SITESEARCH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_SITESEARCH_FIXTURE,),
    name="RERSiteSearchLayer:FunctionalTesting",
)


class RERSiteSearchRestApiLayer(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(RERSiteSearchRestApiLayer, self).setUpZope(app, configurationContext)

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.sitesearch)
        self.loadZCML(package=collective.z3cform.jsonwidget)

    def setUpPloneSite(self, portal):

        applyProfile(portal, "rer.sitesearch:default")


RER_SITESEARCH_API_FIXTURE = RERSiteSearchRestApiLayer()
RER_SITESEARCH_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_SITESEARCH_API_FIXTURE,),
    name="RERSiteSearchRestApiLayer:Integration",
)

RER_SITESEARCH_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_SITESEARCH_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="RERSiteSearchRestApiLayer:Functional",
)
