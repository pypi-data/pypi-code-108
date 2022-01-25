from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError
from mock import patch, MagicMock
import base64


class TestImport(SavepointCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.journal = self.env['account.journal'].create({
            'name': 'Remesa',
            'code': 'REM',
            'type': 'general',
            'update_posted': True,
        })

    @patch('odoo.addons.account_payment_return.models.payment_return.PaymentReturn.browse')  # noqa
    @patch('odoo.addons.account_payment_return_import.wizard.payment_return_import.PaymentReturnImport.create')  # noqa
    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_new')
    def test_payment_return_import_right(self, _, create_mock, browse_mock):
        create_mock.return_value = MagicMock(spec=['import_file'])
        create_mock.return_value.import_file.return_value = {'res_id': 123}
        browse_mock.return_value = MagicMock(spec=['action_confirm'])
        gateway_model = self.env['account.payment.return.gateway']
        file_name = 'return-file.txt'
        return_attach = b'XXX'
        return_attach_enc = base64.b64encode(return_attach).decode('ascii')
        return_attach_prefix = (
            'filename="QUA19DEVCG.txt"\n'
            'Content-Transfer-Encoding: base64\n'
            '\n\n'
        )
        return_attach_suffix = '\n---'
        return_attach = return_attach_prefix + return_attach_enc + return_attach_suffix
        gateway_model.message_new(
            {'attachments': [(file_name, return_attach)]}
        )
        create_mock.assert_called_with({
            'data_file': return_attach_enc.encode('ascii'),
            'journal_id': self.journal.id,
            'match_after_import': False
        })
        create_mock.return_value.import_file.assert_called()
        browse_mock.assert_called_with(123)
        browse_mock.return_value.action_confirm.assert_called()

    @patch('odoo.addons.account_payment_return.models.payment_return.PaymentReturn.browse')  # noqa
    @patch('odoo.addons.account_payment_return_import.wizard.payment_return_import.PaymentReturnImport.create')  # noqa
    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_new')
    def test_payment_return_import_right_bytes(self, _, create_mock, browse_mock):
        create_mock.return_value = MagicMock(spec=['import_file'])
        create_mock.return_value.import_file.return_value = {'res_id': 123}
        browse_mock.return_value = MagicMock(spec=['action_confirm'])
        gateway_model = self.env['account.payment.return.gateway']
        file_name = 'return-file.txt'
        return_attach = b'XXX'
        return_attach_enc = base64.b64encode(return_attach).decode('ascii')
        return_attach_prefix = (
            'filename="QUA19DEVCG.txt"\n'
            'Content-Transfer-Encoding: base64\n'
            '\n\n'
        )
        return_attach_suffix = '\n---'
        return_attach = return_attach_prefix + return_attach_enc + return_attach_suffix
        return_attach_bytes = return_attach.encode('ascii')
        gateway_model.message_new(
            {'attachments': [(file_name, return_attach_bytes)]}
        )
        create_mock.assert_called_with({
            'data_file': return_attach_enc.encode('ascii'),
            'journal_id': self.journal.id,
            'match_after_import': False
        })
        create_mock.return_value.import_file.assert_called()
        browse_mock.assert_called_with(123)
        browse_mock.return_value.action_confirm.assert_called()

    @patch('odoo.addons.account_payment_return_import.wizard.payment_return_import.PaymentReturnImport.create')  # noqa
    def test_payment_return_import_missing_attachments(self, create_mock):
        create_mock.return_value = MagicMock(spec=['import_file'])
        gateway_model = self.env['account.payment.return.gateway']
        self.assertRaises(
            UserError,
            gateway_model.message_new,
            [{}]
        )

    @patch('odoo.addons.account_payment_return.models.payment_return.PaymentReturn.browse')  # noqa
    @patch('odoo.addons.account_payment_return_import.wizard.payment_return_import.PaymentReturnImport.create')  # noqa
    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_new')
    def test_payment_return_import_direct_bytes(self, _, create_mock, browse_mock):
        create_mock.return_value = MagicMock(spec=['import_file'])
        create_mock.return_value.import_file.return_value = {'res_id': 123}
        browse_mock.return_value = MagicMock(spec=['action_confirm'])
        gateway_model = self.env['account.payment.return.gateway']
        file_name = 'return-file.txt'
        return_attach_bytes = b'XXX'
        return_attach_bytes_enc = base64.b64encode(return_attach_bytes).decode('ascii')
        gateway_model.message_new(
            {'attachments': [(file_name, return_attach_bytes)]}
        )
        create_mock.assert_called_with({
            'data_file': return_attach_bytes_enc.encode('ascii'),
            'journal_id': self.journal.id,
            'match_after_import': False
        })
        create_mock.return_value.import_file.assert_called()
        browse_mock.assert_called_with(123)
        browse_mock.return_value.action_confirm.assert_called()
