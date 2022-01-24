import logging
from unittest.mock import patch

from ddt import ddt
from django.test import tag

from openlxp_notifications.management.commands.conformance_alerts import \
    send_log_email, send_log_email_with_msg
from openlxp_notifications.models import (ReceiverEmailConfiguration,
                                          SenderEmailConfiguration,
                                          EmailConfiguration)

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class CommandTests(TestSetUp):

    # Test cases for conformance_alerts

    def test_send_log_email(self):
        """Test for function to send emails of log file to personas with
        attachment"""
        with patch('openlxp_notifications.management.commands.'
                   'conformance_alerts.ReceiverEmailConfiguration') \
                as receive_email_cfg, \
                patch(
                    'openlxp_notifications.management.commands.'
                    'conformance_alerts.SenderEmailConfiguration') \
                as sender_email_cfg, \
                patch(
                    'openlxp_notifications.management.commands.'
                    'conformance_alerts.EmailConfiguration') \
                as email_cfg, \
                patch(
                    'openlxp_notifications.management.commands.'
                    'conformance_alerts.send_notifications',
                    return_value=None
                ) as mock_send_notification:
            receive_email = ReceiverEmailConfiguration(
                email_address=self.receive_email_list)
            receive_email_cfg.first.return_value = receive_email

            send_email = SenderEmailConfiguration(
                sender_email_address=self.sender_email)
            sender_email_cfg.first.return_value = send_email

            email_config = EmailConfiguration(
                Subject=self.Subject, Email_Content=self.Email_Content,
                Signature=self.Signature, Email_Us=self.Email_Us,
                FAQ_URL=self.FAQ_URL,
                Unsubscribe_Email_ID=self.Unsubscribe_Email_ID,
                Logs_Type='ATTACHMENT', HTML_File='HTML_Files/My_Html.html')

            email_cfg.first.return_value = email_config

            send_log_email()
            self.assertEqual(mock_send_notification.call_count, 1)

    def test_send_log_email_with_msg(self):
        """Test for function to send emails of log file to personas with
        message"""
        with patch('openlxp_notifications.management.commands.'
                   'conformance_alerts.EmailConfiguration') \
                as email_cfg, \
                patch(
                    'openlxp_notifications.management.commands.'
                    'conformance_alerts.send_notifications_with_msg',
                    return_value=None
                ) as mock_send_notifications_with_msg:
            email_config = EmailConfiguration(
                Subject=self.Subject, Email_Content=self.Email_Content,
                Signature=self.Signature, Email_Us=self.Email_Us,
                FAQ_URL=self.FAQ_URL,
                Unsubscribe_Email_ID=self.Unsubscribe_Email_ID,
                Logs_Type='MESSAGE', HTML_File='HTML_Files/My_Html.html')

            email_cfg.first.return_value = email_config

            send_log_email_with_msg(self.receive_email_list, self.sender_email,
                                    'Message')
            self.assertEqual(mock_send_notifications_with_msg.call_count, 1)
