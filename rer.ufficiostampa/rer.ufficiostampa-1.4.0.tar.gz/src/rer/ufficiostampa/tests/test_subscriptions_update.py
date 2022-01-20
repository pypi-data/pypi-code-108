# -*- coding: utf-8 -*-
from rer.ufficiostampa.testing import (
    RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING,  # noqa: E501,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from zope.component import getUtility
from rer.ufficiostampa.interfaces import ISubscriptionsStore

import transaction
import unittest


class TestSubscriptionsUpdate(unittest.TestCase):

    layer = RER_UFFICIOSTAMPA_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(
            email="memberuser@example.com",
            username="memberuser",
            password="secret",
        )

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.url = "{}/@subscriptions".format(self.portal_url)

        self.tool = getUtility(ISubscriptionsStore)
        self.id = self.tool.add(
            {
                "channels": ["foo"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "Doe",
                "phone": "123456",
            },
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_patch_should_be_called_with_id(self):
        res = self.api_session.patch(self.url, json={})
        self.assertEqual(
            self.api_session.patch(self.url, json={}).status_code, 400
        )
        self.assertEqual("Missing id", res.json()["message"])

    def test_anon_cant_update_data(self):
        url = "{}/123".format(self.url)
        self.assertEqual(
            self.anon_api_session.patch(url, json={}).status_code, 401
        )

    def test_gestore_comunicati_can_update_data(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        api_session.auth = ("memberuser", "secret")

        url = "{}/123".format(self.url)
        self.assertEqual(api_session.patch(url, json={}).status_code, 401)

        setRoles(self.portal, "memberuser", ["Gestore Comunicati"])
        transaction.commit()
        # 400 because it's a fake id
        self.assertEqual(api_session.patch(self.url, json={}).status_code, 400)

        api_session.close()

    def test_bad_request_if_pass_wrong_id(self):

        res = self.api_session.patch("{}/foo".format(self.url), json={})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["message"], "Id should be a number.")

        res = self.api_session.patch("{}/123".format(self.url), json={})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json()["message"], 'Unable to find item with id "123"'
        )

    def test_correctly_save_data(self):
        url = "{}/{}".format(self.url, self.id)
        record = self.tool.get_record(self.id)

        self.assertEqual(record.attrs["name"], "John")

        self.api_session.patch(url, json={"name": "Jack"})

        res = self.api_session.get(self.url).json()
        self.assertEqual(res["items"][0]["name"], "Jack")
        self.assertEqual(res["items"][0]["id"], self.id)
