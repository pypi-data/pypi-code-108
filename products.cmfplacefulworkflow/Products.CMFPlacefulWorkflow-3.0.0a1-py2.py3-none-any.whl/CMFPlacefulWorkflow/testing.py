# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2
from Products.CMFCore.interfaces import ISiteRoot
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

import Products.CMFPlacefulWorkflow


class ProductsCmfplacefulworkflowLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=Products.CMFPlacefulWorkflow)
        profile_registry.registerProfile(
            name='exportimport', title='Test Placeful Workflow Profile',
            description=(
                "Tests the placeful workflow policy handler."),
            path='profiles/exportimport',
            product='Products.CMFPlacefulWorkflow.tests',
            profile_type=EXTENSION, for_=ISiteRoot)
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])
        applyProfile(portal, 'Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow')


PRODUCTS_CMFPLACEFULWORKFLOW_FIXTURE = ProductsCmfplacefulworkflowLayer()


PRODUCTS_CMFPLACEFULWORKFLOW_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCTS_CMFPLACEFULWORKFLOW_FIXTURE,),
    name='ProductsCmfplacefulworkflowLayer:IntegrationTesting',
)


PRODUCTS_CMFPLACEFULWORKFLOW_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCTS_CMFPLACEFULWORKFLOW_FIXTURE,),
    name='ProductsCmfplacefulworkflowLayer:FunctionalTesting',
)


PRODUCTS_CMFPLACEFULWORKFLOW_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PRODUCTS_CMFPLACEFULWORKFLOW_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ProductsCmfplacefulworkflowLayer:AcceptanceTesting',
)
