"""
Test fatlinks views
"""

# Standard Library
import datetime as dt

# Third Party
from pytz import utc

# Django
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter

# Alliance Auth AFAT
from afat.models import (
    AFat,
    AFatLink,
    AFatLinkType,
    ClickAFatDuration,
    get_hash_on_save,
)
from afat.tests.fixtures.load_allianceauth import load_allianceauth
from afat.utils import get_main_character_from_user

MODULE_PATH = "afat.views.fatlinks"


class TestFatlinksView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()

        # given
        cls.character_1001 = EveCharacter.objects.get(character_id=1001)
        cls.character_1002 = EveCharacter.objects.get(character_id=1002)
        cls.character_1003 = EveCharacter.objects.get(character_id=1003)
        cls.character_1004 = EveCharacter.objects.get(character_id=1004)
        cls.character_1005 = EveCharacter.objects.get(character_id=1005)
        cls.character_1101 = EveCharacter.objects.get(character_id=1101)

        cls.user_without_access, _ = create_user_from_evecharacter(
            cls.character_1001.character_id
        )

        cls.user_with_basic_access, _ = create_user_from_evecharacter(
            cls.character_1002.character_id, permissions=["afat.basic_access"]
        )

        cls.user_with_manage_afat, _ = create_user_from_evecharacter(
            cls.character_1003.character_id,
            permissions=["afat.basic_access", "afat.manage_afat"],
        )

        cls.user_with_add_fatlink, _ = create_user_from_evecharacter(
            cls.character_1004.character_id,
            permissions=["afat.basic_access", "afat.add_fatlink"],
        )

        # cls.afat_link_type_cta = AFatLinkType.objects.create(name="CTA")
        # cls.afat_link_type_stratop = AFatLinkType.objects.create(name="Strat OP")

        # Generate some FAT links and FATs
        cls.afat_link_april_1 = AFatLink.objects.create(
            fleet="April Fleet 1",
            hash="1231",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 4, 1, tzinfo=utc),
        )
        cls.afat_link_april_2 = AFatLink.objects.create(
            fleet="April Fleet 2",
            hash="1232",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 4, 15, tzinfo=utc),
        )
        cls.afat_link_september = AFatLink.objects.create(
            fleet="September Fleet",
            hash="1233",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 9, 1, tzinfo=utc),
        )
        cls.afat_link_september_no_fats = AFatLink.objects.create(
            fleet="September Fleet 2",
            hash="1234",
            creator=cls.user_with_basic_access,
            character=cls.character_1001,
            afattime=dt.datetime(2020, 9, 1, tzinfo=utc),
        )

        AFat.objects.create(
            character=cls.character_1101,
            afatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1001,
            afatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1002,
            afatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1003,
            afatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1004,
            afatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1005,
            afatlink=cls.afat_link_april_1,
            shiptype="Omen",
        )

        AFat.objects.create(
            character=cls.character_1001,
            afatlink=cls.afat_link_april_2,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1004,
            afatlink=cls.afat_link_april_2,
            shiptype="Thorax",
        )
        AFat.objects.create(
            character=cls.character_1002,
            afatlink=cls.afat_link_april_2,
            shiptype="Thorax",
        )
        AFat.objects.create(
            character=cls.character_1003,
            afatlink=cls.afat_link_april_2,
            shiptype="Omen",
        )

        AFat.objects.create(
            character=cls.character_1001,
            afatlink=cls.afat_link_september,
            shiptype="Omen",
        )
        AFat.objects.create(
            character=cls.character_1004,
            afatlink=cls.afat_link_september,
            shiptype="Guardian",
        )
        AFat.objects.create(
            character=cls.character_1002,
            afatlink=cls.afat_link_september,
            shiptype="Omen",
        )

    def test_should_show_fatlnks_overview(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse("afat:fatlinks_overview")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_fatlnks_overview_with_year(self):
        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        url = reverse("afat:fatlinks_overview", kwargs={"year": 2020})
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_add_fatlink_for_user_with_manage_afat(self):
        # given
        AFatLinkType.objects.create(name="CTA")

        self.client.force_login(self.user_with_manage_afat)

        # when
        url = reverse("afat:fatlinks_add_fatlink")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_add_fatlink_for_user_with_add_fatlinkt(self):
        # given
        self.client.force_login(self.user_with_add_fatlink)

        # when
        url = reverse("afat:fatlinks_add_fatlink")
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_fatlink_details_for_user_with_manage_afat(self):
        # given
        self.client.force_login(self.user_with_manage_afat)

        # when
        url = reverse(
            "afat:fatlinks_details_fatlink",
            kwargs={"fatlink_hash": self.afat_link_april_1.hash},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_show_fatlink_details_for_user_with_add_fatlinkt(self):
        # given
        self.client.force_login(self.user_with_add_fatlink)

        # when
        url = reverse(
            "afat:fatlinks_details_fatlink",
            kwargs={"fatlink_hash": self.afat_link_april_1.hash},
        )
        res = self.client.get(url)

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_not_show_fatlink_details_for_non_existing_fatlink(self):
        # given
        self.client.force_login(self.user_with_manage_afat)

        # when
        url = reverse(
            "afat:fatlinks_details_fatlink",
            kwargs={"fatlink_hash": "foobarsson"},
        )
        res = self.client.get(url)

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)

        messages = list(get_messages(res.wsgi_request))

        self.assertRaises(AFatLink.DoesNotExist)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "<h4>Warning!</h4><p>The hash provided is not valid.</p>",
        )

    def test_ajax_get_fatlinks_by_year(self):
        # given
        # self.maxDiff = None
        self.client.force_login(self.user_with_basic_access)

        fatlink_hash = get_hash_on_save()
        fatlink_type_cta = AFatLinkType.objects.create(name="CTA")
        fatlink_created = AFatLink.objects.create(
            fleet="April Fleet 1",
            creator=self.user_with_manage_afat,
            character=self.character_1001,
            hash=fatlink_hash,
            is_esilink=True,
            is_registered_on_esi=True,
            esi_fleet_id=3726458287,
            link_type=fatlink_type_cta,
            afattime="2021-11-05T13:19:49.676Z",
        )

        ClickAFatDuration.objects.create(fleet=fatlink_created, duration=120)

        # when
        fatlink = (
            AFatLink.objects.select_related_default()
            .annotate_afats_count()
            .get(hash=fatlink_hash)
        )

        url_with_year = reverse(
            "afat:fatlinks_ajax_get_fatlinks_by_year",
            kwargs={"year": 2021},
        )
        result = self.client.get(url_with_year)

        # then
        self.assertEqual(result.status_code, 200)

        creator_main_character = get_main_character_from_user(user=fatlink.creator)
        fleet_time = fatlink.afattime
        fleet_time_timestamp = fleet_time.timestamp()
        esi_marker = (
            '<span class="label label-default afat-label afat-label-via-esi '
            'afat-label-active-esi-fleet">via ESI</span>'
        )

        self.assertJSONEqual(
            str(result.content, encoding="utf8"),
            [
                {
                    "pk": fatlink.pk,
                    "fleet_name": fatlink.fleet + esi_marker,
                    "creator_name": creator_main_character,
                    "fleet_type": "CTA",
                    "fleet_time": {
                        "time": "2021-11-05T13:19:49.676Z",
                        "timestamp": fleet_time_timestamp,
                    },
                    "fats_number": 0,
                    "hash": fatlink.hash,
                    "is_esilink": True,
                    "esi_fleet_id": fatlink.esi_fleet_id,
                    "is_registered_on_esi": True,
                    # "actions": '<a class="btn btn-afat-action btn-info btn-sm" href="/fleet-activity-tracking/fatlink/ncOsHjnjmYZd9k6hI4us8QShRlqJ17/details/"><span class="fas fa-eye"></span></a><a class="btn btn-afat-action btn-danger btn-sm" data-toggle="modal" data-target="#deleteFatLinkModal" data-url="/fleet-activity-tracking/fatlink/ncOsHjnjmYZd9k6hI4us8QShRlqJ17/delete/" data-confirm-text="Delete"data-body-text="<p>Are you sure you want to delete FAT link M2-XFE Keepstar Kill?</p>"><span class="glyphicon glyphicon-trash"></span></a>',
                    "actions": "",
                    "via_esi": "Yes",
                }
            ],
        )
