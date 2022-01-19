from django.test import TestCase
from psu_base.services import email_service, auth_service


class EmailTestCase(TestCase):
    def setUp(self):
        pass

    def test_allowed_recipients(self):
        """
        Most people should never receive emails from non-production
        """
        to = ["MJG@pdx.edu", "mjg@pdx.edu", "susie.student@pdx.edu", "myself@gmail.com"]
        cc = "oit-IA-group@pdx.edu"
        bcc = None
        to, cc, bcc, num = email_service._prepare_recipients(to, cc, bcc, "OIT")

        self.assertTrue(num == 2)
        self.assertTrue(len(to) == 1)
        self.assertTrue(len(cc) == 1)
        self.assertTrue(len(bcc) == 0)
        self.assertTrue(to[0] == "mjg@pdx.edu")
        self.assertTrue(cc[0] == "oit-ia-group@pdx.edu")

    def test_allowed_recipients_clean(self):
        """
        Part of recipient validation is to remove gtest and gdev from the addresses
        """
        to = ["MJG@gTest.pdx.edu", "susie.student@pdx.edu", "myself@gmail.com"]
        cc = "oit-IA-group@GdEv.pdX.Edu"
        bcc = None
        to, cc, bcc, num = email_service._prepare_recipients(to, cc, bcc, "OIT")

        self.assertTrue(num == 2)
        self.assertTrue(len(to) == 1)
        self.assertTrue(len(cc) == 1)
        self.assertTrue(len(bcc) == 0)
        self.assertTrue(to[0] == "mjg@pdx.edu")
        self.assertTrue(cc[0] == "oit-ia-group@pdx.edu")

    def test_redirection(self):
        """
        When no recipients are allowed, email should be sent to the default user
        (default user is the authenticated user, or a specified address for anonymous non-prod testing)
        """
        email_service.set_default_email("some_test_email@whatever.edu")
        to = ["susie.student@pdx.edu", "myself@gmail.com"]
        cc = ""
        bcc = None
        to, cc, bcc, num = email_service._prepare_recipients(to, cc, bcc, "OIT")

        self.assertTrue(num == 1)
        self.assertTrue(len(to) == 1)
        self.assertTrue(len(cc) == 0)
        self.assertTrue(len(bcc) == 0)
        if not auth_service.is_logged_in():
            self.assertTrue(to[0] == "some_test_email@whatever.edu")
