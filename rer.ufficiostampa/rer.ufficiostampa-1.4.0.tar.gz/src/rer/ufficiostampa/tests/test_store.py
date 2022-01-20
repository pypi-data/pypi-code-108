# -*- coding: utf-8 -*-
from rer.ufficiostampa.testing import RER_UFFICIOSTAMPA_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from rer.ufficiostampa.interfaces import ISubscriptionsStore

import transaction
import unittest


class TestTool(unittest.TestCase):

    layer = RER_UFFICIOSTAMPA_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def tearDown(self):
        tool = getUtility(ISubscriptionsStore)
        tool.clear()
        transaction.commit()

    def test_correctly_add_data(self):
        tool = getUtility(ISubscriptionsStore)
        self.assertEqual(len(tool.search()), 0)
        tool.add({"channels": ["foo"], "email": "foo@foo.it"})
        self.assertEqual(len(tool.search()), 1)

    def test_only_store_defined_fields(self):
        tool = getUtility(ISubscriptionsStore)
        self.assertEqual(len(tool.search()), 0)
        id = tool.add(
            {
                "channels": ["foo"],
                "email": "foo@foo.it",
                "unknown": "mistery",
                "name": "John",
                "surname": "Doe",
                "phone": "123456",
            }
        )
        self.assertEqual(len(tool.search()), 1)

        item = tool.get_record(id)
        self.assertEqual(item.attrs.get("unknown", None), None)
        self.assertEqual(item.attrs.get("email", None), "foo@foo.it")
        self.assertEqual(item.attrs.get("channels", None), ["foo"])
        self.assertEqual(item.attrs.get("name", None), "John")
        self.assertEqual(item.attrs.get("surname", None), "Doe")
        self.assertEqual(item.attrs.get("phone", None), "123456")

    def test_update_record(self):
        tool = getUtility(ISubscriptionsStore)
        id = tool.add({"channels": ["foo"], "email": "foo@foo.it"})

        item = tool.get_record(id)
        self.assertEqual(item.attrs.get("email", None), "foo@foo.it")
        self.assertEqual(item.attrs.get("channels", None), ["foo"])

        tool.update(id=id, data={"email": "bar@bar.it"})
        item = tool.get_record(id)
        self.assertEqual(item.attrs.get("email", None), "bar@bar.it")
        self.assertEqual(item.attrs.get("channels", None), ["foo"])

    def test_update_record_return_error_if_id_not_found(self):
        tool = getUtility(ISubscriptionsStore)
        res = tool.update(id=1222, data={"email": "bar@bar.it"})
        self.assertEqual(res, {"error": "NotFound"})

    def test_delete_record(self):
        tool = getUtility(ISubscriptionsStore)
        foo = tool.add({"channels": ["foo"], "email": "foo@foo.it"})
        tool.add({"channels": ["bar"], "email": "bar@bar.it"})

        self.assertEqual(len(tool.search()), 2)
        tool.delete(id=foo)
        self.assertEqual(len(tool.search()), 1)

    def test_delete_record_return_error_if_id_not_found(self):
        tool = getUtility(ISubscriptionsStore)
        res = tool.delete(id=1222)
        self.assertEqual(res, {"error": "NotFound"})

    def test_search(self):
        tool = getUtility(ISubscriptionsStore)
        tool.add(
            {
                "channels": ["foo"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "xxx",
                "phone": "123456",
            },
        )
        tool.add(
            {
                "channels": ["foo", "bar"],
                "email": "bar@bar.it",
                "name": "Jack",
                "surname": "yyy",
                "phone": "123456",
            },
        )
        tool.add(
            {
                "channels": ["baz"],
                "email": "baz@baz.it",
                "name": "Jim",
                "surname": "zzz",
                "phone": "123456",
            },
        )
        transaction.commit()

        self.assertEqual(len(tool.search()), 3)

        #  search by text (index name, surname and email)
        self.assertEqual(len(tool.search(query={"text": "John"})), 1)
        self.assertEqual(len(tool.search(query={"text": "baz"})), 1)
        self.assertEqual(len(tool.search(query={"text": "xxx"})), 1)

        # search by channel
        self.assertEqual(len(tool.search(query={"channels": "foo"})), 2)
        self.assertEqual(len(tool.search(query={"channels": "baz"})), 1)
        self.assertEqual(
            len(tool.search(query={"channels": ["foo", "bar"]})), 2
        )

        # combined search
        self.assertEqual(
            len(tool.search(query={"channels": "foo", "text": "Jack"})), 1
        )

    def test_clear(self):
        tool = getUtility(ISubscriptionsStore)
        tool.add(
            {
                "channels": ["foo"],
                "email": "foo@foo.it",
                "name": "John",
                "surname": "xxx",
                "phone": "123456",
            },
        )
        tool.add(
            {
                "channels": ["foo", "bar"],
                "email": "bar@bar.it",
                "name": "Jack",
                "surname": "yyy",
                "phone": "123456",
            },
        )
        tool.add(
            {
                "channels": ["baz"],
                "email": "baz@baz.it",
                "name": "Jim",
                "surname": "zzz",
                "phone": "123456",
            },
        )
        transaction.commit()

        self.assertEqual(len(tool.search()), 3)

        tool.clear()
        self.assertEqual(len(tool.search()), 0)
