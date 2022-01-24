from django.test import TestCase
from .email import Email


class EmailTest(TestCase):

    def test_initialization_with_string_recipient(self):
        email = Email('some subject', 'some sender', 'some recipient')
        self.assertEqual(email.subject, 'some subject')
        self.assertEqual(email.sender, 'some sender')
        self.assertEqual(email.recipients, ['some recipient'])

    def test_initialization_with_list_recipient(self):
        email = Email('some subject', 'some sender', ['r1', 'r2', 'r3'])
        self.assertEqual(email.subject, 'some subject')
        self.assertEqual(email.sender, 'some sender')
        self.assertEqual(email.recipients, ['r1', 'r2', 'r3'])

    def test_set_recipient_with_list(self):
        email = Email('S1', 'SS', [])
        email.set_recipients(['x1', 'x2', 'x3'])
        self.assertEqual(email.recipients, ['x1', 'x2', 'x3'])

    def test_set_recipient_with_string(self):
        email = Email('S1', 'SS', [])
        email.set_recipients('somerecipient')
        self.assertEqual(email.recipients, ['somerecipient'])

    def test_add_recipient_with_list(self):
        email = Email('S1', 'SS', [])
        email.add_recipients(['y1', 'y2', 'y3'])
        email.add_recipients(['y4', 'y5'])
        email.add_recipients(['y6', 'y7', 'y8', 'y9'])
        self.assertEqual(email.recipients, ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9'])

    def test_add_recipient_with_string(self):
        email = Email('S1', 'SS', [])
        email.add_recipients('y1')
        email.add_recipients('y2')
        email.add_recipients('y3')
        self.assertEqual(email.recipients, ['y1', 'y2', 'y3'])

    def test_set_recipient_cc_with_list(self):
        email = Email('S1', 'SS', [])
        email.set_recipients_cc(['x1', 'x2', 'x3'])
        self.assertEqual(email.recipients_cc, ['x1', 'x2', 'x3'])

    def test_set_recipient_cc_with_string(self):
        email = Email('S1', 'SS', [])
        email.set_recipients_cc('somerecipient')
        self.assertEqual(email.recipients_cc, ['somerecipient'])

    def test_add_recipient_cc_with_list(self):
        email = Email('S1', 'SS', [])
        email.add_recipients_cc(['y1', 'y2', 'y3'])
        email.add_recipients_cc(['y4', 'y5'])
        email.add_recipients_cc(['y6', 'y7', 'y8', 'y9'])
        self.assertEqual(email.recipients_cc, ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9'])

    def test_add_recipient_cc_with_string(self):
        email = Email('S1', 'SS', [])
        email.add_recipients_cc('y1')
        email.add_recipients_cc('y2')
        email.add_recipients_cc('y3')
        self.assertEqual(email.recipients_cc, ['y1', 'y2', 'y3'])

    def test_set_recipient_bcc_with_list(self):
        email = Email('S1', 'SS', [])
        email.set_recipients_bcc(['x1', 'x2', 'x3'])
        self.assertEqual(email.recipients_bcc, ['x1', 'x2', 'x3'])

    def test_set_recipient_bcc_with_string(self):
        email = Email('S1', 'SS', [])
        email.set_recipients_bcc('somerecipient')
        self.assertEqual(email.recipients_bcc, ['somerecipient'])

    def test_add_recipient_bcc_with_list(self):
        email = Email('S1', 'SS', [])
        email.add_recipients_bcc(['y1', 'y2', 'y3'])
        email.add_recipients_bcc(['y4', 'y5'])
        email.add_recipients_bcc(['y6', 'y7', 'y8', 'y9'])
        self.assertEqual(email.recipients_bcc, ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9'])

    def test_add_recipient_bcc_with_string(self):
        email = Email('S1', 'SS', [])
        email.add_recipients_bcc('y1')
        email.add_recipients_bcc('y2')
        email.add_recipients_bcc('y3')
        self.assertEqual(email.recipients_bcc, ['y1', 'y2', 'y3'])

    def test_add_attachment_with_list(self):
        email = Email('S1', 'SS', [])
        email.add_attachment('f1', 'c1', 'ct1')
        email.add_attachment('f2', 'c2', 'ct2')
        email.add_attachment('f3', 'c3', 'ct3')
        self.assertItemsEqual(email.email_attachments, [
            ('f1', 'c1', 'ct1'),
            ('f2', 'c2', 'ct2'),
            ('f3', 'c3', 'ct3')
        ])
