from odoo import models
from odoo.exceptions import UserError
import logging
import re
import base64
_logger = logging.getLogger(__name__)


class AccountPaymentReturnEmailGateway(models.Model):
    _name = 'account.payment.return.gateway'
    _inherit = 'mail.thread'

    def message_new(self, msg_dict, custom_values=None):
        import_model = self.env['payment.return.import']
        return_model = self.env['payment.return']
        journal_model = self.env['account.journal']
        thread = super().message_new(msg_dict, custom_values)
        if 'attachments' in msg_dict:
            attach_str = msg_dict['attachments'][0][1]
            if type(attach_str) == bytes:
                attach_str = attach_str.decode('ascii')
            _logger.info("attachments: {}".format(msg_dict['attachments']))
            pattern = re.compile(r'filename=".*?".*\n\n(.*?)\n-+', re.DOTALL)
            match = pattern.search(attach_str)
            if match:
                attach_str = match[1].strip()
            return_file = attach_str.encode('ascii')
            try:
                base64.b64decode(return_file)
                if return_file[0:2] == b'21':
                    return_file = base64.b64encode(return_file)
            except Exception:
                return_file = base64.b64encode(return_file)
            journal = journal_model.search([('code', '=', 'REM')])
            bank_return_id = import_model.create(
                dict(
                    data_file=return_file,
                    journal_id=journal.id,
                    match_after_import=False
                )
            )
            result = bank_return_id.import_file()
            payment_return = return_model.browse(result['res_id'])
            payment_return.action_confirm()
        else:
            raise UserError('Missing attachment in Payment Return email')
        return thread
