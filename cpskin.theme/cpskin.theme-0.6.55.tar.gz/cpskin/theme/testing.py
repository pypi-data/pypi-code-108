# -*- coding: utf-8 -*-
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.testing import z2

import cpskin.theme


class CPSkinThemePloneWithPackageLayer(PloneWithPackageLayer):
    def setUpZope(self, app, configurationContext):
        super(CPSkinThemePloneWithPackageLayer, self).setUpZope(
            app,
            configurationContext
        )
        z2.installProduct(app, 'Products.DateRecurringIndex')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.DateRecurringIndex')


CPSKIN_THEME_FIXTURE = CPSkinThemePloneWithPackageLayer(
    name='CPSKIN_THEME_FIXTURE',
    zcml_filename='testing.zcml',
    zcml_package=cpskin.theme,
    gs_profile_id='cpskin.theme:testing')

CPSKIN_THEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CPSKIN_THEME_FIXTURE,),
    name='CPSkinTheme:Integration')
