# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PloneRestApiDXLayer
from plone.testing import z2

import collective.MockMailHost
import collective.z3cform.jsonwidget
import rer.ufficiostampa
import souper.plone
import plone.restapi


class RerUfficiostampaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.ufficiostampa)
        self.loadZCML(package=collective.z3cform.jsonwidget)
        self.loadZCML(package=souper.plone)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "rer.ufficiostampa:default")


RER_UFFICIOSTAMPA_FIXTURE = RerUfficiostampaLayer()


RER_UFFICIOSTAMPA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_UFFICIOSTAMPA_FIXTURE,),
    name="RerUfficiostampaLayer:IntegrationTesting",
)


RER_UFFICIOSTAMPA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_UFFICIOSTAMPA_FIXTURE,),
    name="RerUfficiostampaLayer:FunctionalTesting",
)


class RerUfficiostampaLayerApi(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(RerUfficiostampaLayerApi, self).setUpZope(
            app, configurationContext
        )
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.ufficiostampa)
        self.loadZCML(package=collective.z3cform.jsonwidget)
        self.loadZCML(package=souper.plone)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "rer.ufficiostampa:default")


RER_UFFICIOSTAMPA_API_FIXTURE = RerUfficiostampaLayerApi()
RER_UFFICIOSTAMPA_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_UFFICIOSTAMPA_API_FIXTURE,),
    name="RerUfficiostampaLayerApi:Integration",
)

RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_UFFICIOSTAMPA_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="RerUfficiostampaLayerApi:Functional",
)
