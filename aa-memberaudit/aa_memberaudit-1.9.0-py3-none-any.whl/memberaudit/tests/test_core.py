from unittest.mock import Mock, patch

from allianceauth.eveonline.evelinks import dotlan, evewho
from app_utils.testing import NoSocketsTestCase

from ..core.xml_converter import eve_xml_to_html
from .testdata.esi_client_stub import load_test_data
from .testdata.load_entities import load_entities
from .testdata.load_eveuniverse import load_eveuniverse

MODULE_PATH = "memberaudit.core.xml_converter"


class TestHTMLConversion(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        load_entities()

    def test_convert_eve_xml_alliance(self):
        """can convert an alliance link in CCP XML to HTML"""
        with patch(
            "eveuniverse.models.EveEntity.objects.resolve_name",
            Mock(return_value="An Alliance"),
        ):
            result = eve_xml_to_html(
                load_test_data()
                .get("Mail")
                .get("get_characters_character_id_mail_mail_id")
                .get("2")
                .get("body")
            )
            self.assertTrue(result.find(dotlan.alliance_url("An Alliance")) != -1)

    def test_convert_eve_xml_character(self):
        """can convert a character link in CCP XML to HTML"""
        result = eve_xml_to_html(
            load_test_data()
            .get("Mail")
            .get("get_characters_character_id_mail_mail_id")
            .get("2")
            .get("body")
        )
        self.assertTrue(result.find(evewho.character_url(1001)) != -1)

    def test_convert_eve_xml_corporation(self):
        """can convert a corporation link in CCP XML to HTML"""
        with patch(
            "eveuniverse.models.EveEntity.objects.resolve_name",
            Mock(return_value="A Corporation"),
        ):
            result = eve_xml_to_html(
                load_test_data()
                .get("Mail")
                .get("get_characters_character_id_mail_mail_id")
                .get("2")
                .get("body")
            )
            self.assertTrue(result.find(dotlan.alliance_url("A Corporation")) != -1)

    def test_convert_eve_xml_solar_system(self):
        """can convert a solar system link in CCP XML to HTML"""
        with patch(
            "eveuniverse.models.EveEntity.objects.resolve_name",
            Mock(return_value="Polaris"),
        ):
            result = eve_xml_to_html(
                load_test_data()
                .get("Mail")
                .get("get_characters_character_id_mail_mail_id")
                .get("2")
                .get("body")
            )
            self.assertTrue(result.find(dotlan.solar_system_url("Polaris")) != -1)

    def test_convert_bio_1(self):
        """can convert a bio includes lots of non-ASCII characters and handle the u-bug"""
        with patch(
            "eveuniverse.models.EveEntity.objects.resolve_name",
            Mock(return_value="An Alliance"),
        ):
            result = eve_xml_to_html(
                load_test_data()
                .get("Character")
                .get("get_characters_character_id")
                .get("1002")
                .get("description")
            )
            self.assertIn(
                "Zuverlässigkeit, Eigeninitiative, Hilfsbereitschaft, Teamfähigkeit",
                result,
            )
            self.assertNotEqual(result[:2], "u'")

    def test_convert_bio_2(self):
        """can convert a bio that resulted in a syntax error (#77)"""
        with patch(
            "eveuniverse.models.EveEntity.objects.resolve_name",
            Mock(return_value="An Alliance"),
        ):
            try:
                result = eve_xml_to_html(
                    load_test_data()
                    .get("Character")
                    .get("get_characters_character_id")
                    .get("1003")
                    .get("description")
                )
            except Exception as ex:
                self.fail(f"Unexpected exception was raised: {ex}")

            self.assertNotEqual(result[:2], "u'")
