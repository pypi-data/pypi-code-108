# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName
from rer.sitesearch.testing import RER_SITESEARCH_API_FUNCTIONAL_TESTING
from plone.api.portal import set_registry_record
from rer.sitesearch.interfaces import IRERSiteSearchSettings

import transaction
import unittest


class SearchFiltersTest(unittest.TestCase):

    layer = RER_SITESEARCH_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        transaction.commit()

    def tearDown(self):
        set_registry_record("available_indexes", [], interface=IRERSiteSearchSettings)
        #  reset elevate
        set_registry_record("types_grouping", [], interface=IRERSiteSearchSettings)
        self.api_session.close()

    def test_route_exists(self):
        response = self.api_session.get("/@search-filters")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

    def test_return_empty_list_if_not_set(self):
        response = self.api_session.get("/@search-filters")

        results = response.json()
        self.assertEqual(results[u"grouping"], [])
        self.assertEqual(results[u"indexes"], [])
