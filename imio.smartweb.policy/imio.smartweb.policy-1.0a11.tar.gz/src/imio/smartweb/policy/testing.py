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
from z3c.form.interfaces import IFormLayer
from zope.globalrequest import setRequest
from zope.interface import alsoProvides

import imio.smartweb.policy


class ImioSmartwebPolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=imio.smartweb.policy)

    def setUpPloneSite(self, portal):
        request = portal.REQUEST
        # set basic request to be able to handle redirect in subscribers
        setRequest(request)
        alsoProvides(request, IFormLayer)
        applyProfile(portal, "imio.smartweb.policy:default")


IMIO_SMARTWEB_POLICY_FIXTURE = ImioSmartwebPolicyLayer()


IMIO_SMARTWEB_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_SMARTWEB_POLICY_FIXTURE,),
    name="ImioSmartwebPolicyLayer:IntegrationTesting",
)


IMIO_SMARTWEB_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_SMARTWEB_POLICY_FIXTURE,),
    name="ImioSmartwebPolicyLayer:FunctionalTesting",
)


IMIO_SMARTWEB_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_SMARTWEB_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioSmartwebPolicyLayer:AcceptanceTesting",
)
