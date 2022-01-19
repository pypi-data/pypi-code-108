from django.test import TestCase
from psu_base.classes.Auth import Auth
from psu_base.classes.User import User
from psu_base.classes.DynamicRole import DynamicRole
import collections


class AuthTestCase(TestCase):
    def setUp(self):
        pass

    def test_auth_user(self):
        """Create a User from username"""
        # Lookup via Finti
        mjg = User("mjg")
        self.assertTrue(mjg.username == "mjg", "Incorrect username for mjg")
        self.assertTrue(type(mjg.authorities) is list, "No authority list")

        # Restore from dict
        mjg_dict = mjg.to_dict()
        self.assertTrue(type(mjg_dict) is dict, "mjg_dict is not a dict")
        re_mjg = User(mjg_dict)
        self.assertTrue(re_mjg.username == "mjg", "Incorrect username for mjg")
        self.assertTrue(re_mjg.psu_id == "988213600", "Incorrect psu_id for mjg")
        self.assertTrue(type(re_mjg.authorities) is list, "No authority list")

    def test_auth_impersonation(self):
        mjg = Auth("mjg")
        self.assertTrue(
            mjg.sso_user.username == "mjg", "Incorrect username for sso_user: mjg"
        )
        self.assertTrue(
            type(mjg.sso_user.authorities) is list, "No authority list for sso_user"
        )
        self.assertTrue(mjg.impersonated_user is None, "Impersonated should be None")
        self.assertTrue(mjg.proxied_user is None, "Proxy should be None")
        self.assertTrue(
            mjg.get_user().username == "mjg", "SSO user should be default user"
        )
        self.assertTrue(
            mjg.start_impersonating("bbras"), "Impersonating Brandon should work"
        )
        self.assertTrue(
            mjg.impersonated_user.username == "bbras",
            "Impersonated username should be Brandon",
        )
        self.assertTrue(mjg.proxied_user is None, "Proxy should be None")
        self.assertTrue(
            mjg.get_user().username == "bbras",
            "Impersonated user should be default user",
        )
        self.assertTrue(
            mjg.start_impersonating(""),
            "Empty search value should remove Impersonated and not be an error",
        )
        self.assertTrue(
            mjg.get_user().username == "mjg", "SSO user should be default user"
        )
        self.assertFalse(
            mjg.start_impersonating("some-non-existing-user"),
            "Invalid Impersonation should be an error",
        )
        self.assertTrue(
            mjg.get_user().username == "mjg", "SSO user should be default user"
        )

    def test_proxy(self):
        mjg = Auth("mjg")
        mjg.set_proxy("bbras")
        self.assertTrue(mjg.impersonated_user is None, "Impersonated should be None")
        self.assertFalse(mjg.proxied_user is None, "Proxy should NOT be None")
        self.assertTrue(
            mjg.get_user().username == "mjg", "SSO user should be default user"
        )
        self.assertTrue(
            mjg.proxied_user.psu_id == "903645048", "Incorrect PSU ID for proxy"
        )

    def test_authority(self):
        bbras = Auth("bbras")
        self.assertTrue(bbras.has_authority("developer"), "bbras should be a developer")
        bbras.start_impersonating("davidsh")
        self.assertFalse(
            bbras.has_authority("developer"),
            "bbras as davidsh should NOT be a developer",
        )
        bbras.start_impersonating(None)
        self.assertTrue(
            bbras.has_authority("developer"), "bbras should be a developer again"
        )

    def test_dynamic_roles(self):
        security_roles = DynamicRole().security_officer()
        self.assertTrue(type(security_roles) is list)
        self.assertTrue(len(security_roles) > 1)
        self.assertTrue("authorize" in security_roles)

        sec_from_string = DynamicRole().decode("~SecurityOfficer")
        self.assertTrue(type(sec_from_string) is list)
        self.assertTrue(
            collections.Counter(security_roles) == collections.Counter(sec_from_string)
        )

        security_plus_roles = DynamicRole().security_officer(plus="proxy")
        self.assertTrue(type(security_plus_roles) is list)
        self.assertTrue(len(security_plus_roles) == len(security_roles) + 1)

        sec_plus_from_string = DynamicRole().decode("~SecurityOfficer+proxy+whatever")
        self.assertTrue(type(sec_from_string) is list)
        self.assertTrue(len(sec_plus_from_string) == len(security_plus_roles) + 1)
        self.assertTrue("authorize" in sec_plus_from_string)
        self.assertTrue("proxy" in sec_plus_from_string)
        self.assertTrue("whatever" in sec_plus_from_string)
