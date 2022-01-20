# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from rer.ufficiostampa.testing import RER_UFFICIOSTAMPA_INTEGRATION_TESTING
from rer.ufficiostampa.utils import get_next_comunicato_number
from rer.ufficiostampa.interfaces.settings import IRerUfficiostampaSettings
from transaction import commit

import unittest


class TestComunicatoNumber(unittest.TestCase):
    """"""

    layer = RER_UFFICIOSTAMPA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.invito = api.content.create(
            type="InvitoStampa", title="Invito", container=self.portal
        )

    def tearDown(self):
        api.portal.set_registry_record(
            "comunicato_year", 0, interface=IRerUfficiostampaSettings,
        )
        api.portal.set_registry_record(
            "comunicato_number", 0, interface=IRerUfficiostampaSettings,
        )
        commit()

    def test_by_default_number_is_1(self):
        self.assertEqual(
            get_next_comunicato_number(), "1/{}".format(datetime.now().year)
        )

    def test_calling_util_twice_return_a_new_number(self):
        self.assertEqual(
            get_next_comunicato_number(), "1/{}".format(datetime.now().year)
        )
        self.assertEqual(
            get_next_comunicato_number(), "2/{}".format(datetime.now().year)
        )

    def test_calling_util_on_new_year_return_1(self):
        current_year = datetime.now().year
        api.portal.set_registry_record(
            "comunicato_year",
            current_year - 1,
            interface=IRerUfficiostampaSettings,
        )
        api.portal.set_registry_record(
            "comunicato_number", 123, interface=IRerUfficiostampaSettings,
        )
        self.assertEqual(
            get_next_comunicato_number(), "1/{}".format(current_year)
        )

    def test_publishing_comunicato_increase_number_and_set_it_to_content(self):
        comunicato1 = api.content.create(
            type="ComunicatoStampa",
            title="Comunicato 1",
            container=self.portal,
        )
        comunicato2 = api.content.create(
            type="ComunicatoStampa",
            title="Comunicato 2",
            container=self.portal,
        )
        current_year = datetime.now().year

        self.assertEqual(getattr(comunicato1, "comunicato_number", ""), "")
        self.assertEqual(getattr(comunicato2, "comunicato_number", ""), "")

        # now publish the first one
        api.content.transition(obj=comunicato1, transition="publish")
        self.assertEqual(
            getattr(comunicato1, "comunicato_number", None),
            "1/{}".format(current_year),
        )
        self.assertEqual(getattr(comunicato2, "comunicato_number", ""), "")

        # and then publish the second one
        api.content.transition(obj=comunicato2, transition="publish")
        self.assertEqual(
            getattr(comunicato2, "comunicato_number", None),
            "2/{}".format(current_year),
        )

        #  if i retract and re-publish it, the number doesn't change
        api.content.transition(obj=comunicato1, transition="retract")
        api.content.transition(obj=comunicato1, transition="publish")
        self.assertEqual(
            getattr(comunicato1, "comunicato_number", None),
            "1/{}".format(current_year),
        )
        self.assertEqual(
            get_next_comunicato_number(), "3/{}".format(current_year)
        )

    def test_publishing_invito_does_not_increase_number_and_set_it_to_content(
        self,
    ):
        comunicato = api.content.create(
            type="ComunicatoStampa",
            title="Comunicato 1",
            container=self.portal,
        )
        invito = api.content.create(
            type="InvitoStampa", title="Invito 2", container=self.portal,
        )
        current_year = datetime.now().year

        self.assertEqual(getattr(comunicato, "comunicato_number", ""), "")
        self.assertEqual(getattr(invito, "comunicato_number", ""), "")

        # now publish the invito
        api.content.transition(obj=invito, transition="publish")
        self.assertEqual(
            getattr(invito, "comunicato_number", ""), "",
        )
        self.assertEqual(getattr(comunicato, "comunicato_number", ""), "")

        # and then publish the comunicato
        api.content.transition(obj=comunicato, transition="publish")
        self.assertEqual(
            getattr(comunicato, "comunicato_number", ""),
            "1/{}".format(current_year),
        )
