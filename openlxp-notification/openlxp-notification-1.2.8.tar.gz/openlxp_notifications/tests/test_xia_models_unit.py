from django.test import SimpleTestCase, tag

from django.core.exceptions import ValidationError

from openlxp_notifications.models import (ReceiverEmailConfiguration,
                                          SenderEmailConfiguration,
                                          EmailConfiguration)
from unittest.mock import patch


@tag('unit')
class ModelTests(SimpleTestCase):

    def test_create_sender_email_config(self):
        """Test that creating a new Sender Email Configuration entry is
        successful with defaults """
        sender_email_address = 'example@test.com'

        sender_email_Config = SenderEmailConfiguration(
            sender_email_address=sender_email_address)

        self.assertEqual(sender_email_Config.sender_email_address,
                         sender_email_address)

    def test_create_two_sender_email_configuration(self):
        """Test that trying to create more than one EMAIL Configuration throws
        ValidationError """
        with patch('openlxp_notifications.models.SenderEmailConfiguration'):
            with self.assertRaises(ValidationError):
                sender_email_address = 'example@test.com'
                sender_email_address1 = 'example@test.com'

                sender_email_Config = SenderEmailConfiguration(
                    sender_email_address=sender_email_address)

                sender_email_Config1 = SenderEmailConfiguration(
                    sender_email_address=sender_email_address1)

                sender_email_Config.save()
                sender_email_Config1.save()

    def test_create_receiver_email_config(self):
        """Test that creating a new Receiver Email Configuration entry is
        successful with defaults """
        email_address = 'example@test.com'

        receiver_email_Config = ReceiverEmailConfiguration(
            email_address=email_address)

        self.assertEqual(receiver_email_Config.email_address,
                         email_address)

    def test_create_email_config(self):
        """Test that creating a Email Configuration entry is
        successful with defaults """
        Subject = 'Notifications'
        Email_Content = 'Please find the email'
        Signature = 'OpenLXP'
        Email_Us = 'example@test.com'
        FAQ_URL = 'https.abc.xyz'
        Unsubscribe_Email_ID = 'example@test.com'
        Logs_Type = 'Message'

        email_config = EmailConfiguration(
            Subject=Subject, Email_Content=Email_Content,
            Signature=Signature, Email_Us=Email_Us, FAQ_URL=FAQ_URL,
            Unsubscribe_Email_ID=Unsubscribe_Email_ID, Logs_Type=Logs_Type)

        self.assertEqual(email_config.Subject,
                         Subject)
        self.assertEqual(email_config.Email_Content,
                         Email_Content)
        self.assertEqual(email_config.Signature,
                         Signature)
        self.assertEqual(email_config.Email_Us,
                         Email_Us)
        self.assertEqual(email_config.FAQ_URL,
                         FAQ_URL)
        self.assertEqual(email_config.Unsubscribe_Email_ID,
                         Unsubscribe_Email_ID)
        self.assertEqual(email_config.Logs_Type,
                         Logs_Type)

    def test_create_two_email_configuration(self):
        """Test that trying to create more than one EMAIL Configuration throws
        ValidationError """
        with patch('openlxp_notifications.models.EmailConfiguration'):
            with self.assertRaises(ValidationError):
                Subject = 'Notifications'
                Email_Content = 'Please find the email'
                Signature = 'OpenLXP'
                Email_Us = 'example@test.com'
                FAQ_URL = 'https.abc.xyz'
                Unsubscribe_Email_ID = 'example@test.com'
                Logs_Type = 'Message'

                emailConfig = EmailConfiguration(
                    Subject=Subject, Email_Content=Email_Content,
                    Signature=Signature, Email_Us=Email_Us, FAQ_URL=FAQ_URL,
                    Unsubscribe_Email_ID=Unsubscribe_Email_ID,
                    Logs_Type=Logs_Type)

                Subject1 = 'Notifications'
                Email_Content1 = 'Please find the email'
                Signature1 = 'OpenLXP'
                Email_Us1 = 'example@test.com'
                FAQ_URL1 = 'https.abc.xyz'
                Unsubscribe_Email_ID1 = 'example@test.com'
                Logs_Type1 = 'Message'

                emailConfig2 = EmailConfiguration(
                    Subject=Subject1, Email_Content=Email_Content1,
                    Signature=Signature1, Email_Us=Email_Us1, FAQ_URL=FAQ_URL1,
                    Unsubscribe_Email_ID=Unsubscribe_Email_ID1,
                    Logs_Type=Logs_Type1)

                emailConfig.save()
                emailConfig2.save()
