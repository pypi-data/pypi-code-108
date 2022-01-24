from django.test import TestCase


class TestSetUp(TestCase):
    """Class with setup and teardown for tests in XIS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        # globally accessible data sets

        self.supplemental_api_endpoint = 'http://openlxp-xis:8020' \
                                         '/api/supplemental-data/'

        self.receive_email_list = ['receiver1@openlxp.com',
                                   'receiver1@openlxp.com']
        self.sender_email = "sender@openlxp.com"

        self.Subject = 'Test Email'
        self.Email_Content = 'Here is the email content'
        self.Signature = 'Email Signature'
        self.Email_Us = 'sample_email@openlxp.com'
        self.FAQ_URL = 'https://sample.url.com'
        self.Unsubscribe_Email_ID = 'unsubscribe_email@openlxp.com'

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
