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
import transaction
import unittest


class TestSubscriptionsGet(unittest.TestCase):

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
        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_anon_cant_post_data(self):
        self.assertEqual(
            self.anon_api_session.post(self.url, json={}).status_code, 401
        )

    def test_gestore_comunicati_can_post_data(self):
        api_session = RelativeSession(self.portal_url)
        api_session.headers.update({"Accept": "application/json"})
        api_session.auth = ("memberuser", "secret")

        self.assertEqual(api_session.post(self.url, json={}).status_code, 401)

        setRoles(self.portal, "memberuser", ["Gestore Comunicati"])
        transaction.commit()
        # 400 because there are some missing fields
        self.assertEqual(api_session.post(self.url, json={}).status_code, 400)

        api_session.close()

    def test_required_params(self):
        """
        email and channel are required.
        """
        self.assertEqual(self.api_session.post(self.url).status_code, 400)
        self.assertEqual(
            self.api_session.post(self.url, json={}).status_code, 400
        )
        self.assertEqual(
            self.api_session.post(
                self.url, json={"channels": ["foo"]}
            ).status_code,
            400,
        )
        self.assertEqual(
            self.api_session.post(
                self.url, json={"channels": ["foo"], "email": "dfsdf@dfdf.it"}
            ).status_code,
            204,
        )

    def test_correctly_save_data(self):
        self.api_session.post(
            self.url, json={"channels": ["foo"], "email": "foo@foo.it"}
        )
        self.assertEqual(
            self.api_session.get(self.url).json()["items_total"], 1
        )

    def test_store_only_known_fields(self):

        self.api_session.post(
            self.url,
            json={
                "channels": ["foo"],
                "email": "foo@foo.it",
                "unknown": "mistery",
                "name": "John",
                "surname": "Doe",
                "phone": "123456",
            },
        )
        res = self.api_session.get(self.url).json()
        self.assertEqual(res["items_total"], 1)
        self.assertEqual(res["items"][0].get("unknown", None), None)
        self.assertEqual(res["items"][0].get("email", None), "foo@foo.it")
        self.assertEqual(res["items"][0].get("channels", None), ["foo"])
        self.assertEqual(res["items"][0].get("name", None), "John")
        self.assertEqual(res["items"][0].get("surname", None), "Doe")
        self.assertEqual(res["items"][0].get("phone", None), "123456")
