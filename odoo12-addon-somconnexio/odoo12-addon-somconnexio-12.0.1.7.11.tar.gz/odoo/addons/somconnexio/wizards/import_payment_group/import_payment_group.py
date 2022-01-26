from odoo import api, fields, models
import base64
import csv

from ...services.account_payment_group_process \
    import AccountPaymentGroupProcess


class ImportPaymentGroupWizard(models.TransientModel):
    _name = 'import.payment.group.wizard'
    data = fields.Binary("Upload file")
    reference = fields.Char("Reference")

    @api.multi
    def run_wizard(self):
        decoded_data = base64.b64decode(self.data)
        f = (line.strip() for line in decoded_data.decode('utf-8').split('\n'))
        fr = csv.DictReader(f)
        raw_payment_lines = [row for row in fr]
        AccountPaymentGroupProcess(self.env).process_payment_group(
            self.reference,
            raw_payment_lines
        )
        return True
