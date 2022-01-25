from odoo import api, fields, models, _
import base64
import csv


class ContractInvoicePayment(models.TransientModel):
    _name = 'contract.invoice.payment.wizard'
    data = fields.Binary("Upload file")
    errors = fields.Text("Errors")
    state = fields.Selection([
        ('errors', 'errors'),
        ('load', 'load'),
    ], default='load')

    @api.multi
    def run_wizard(self):
        decoded_data = base64.b64decode(self.data)
        f = (line.strip() for line in decoded_data.decode('utf-8').split('\n'))
        fr = csv.DictReader(f)
        errors = []
        for row in fr:
            invoice = self.env['account.invoice'].search(
                [('name', '=', row['Invoice number'])]
            )
            if not invoice:
                errors.append(
                    _("The invoice {} has not be found (the contract is {})").format(
                        row['Invoice number'], row['Subscription code']
                    )
                )
                continue
            contract = self.env['contract.contract'].search(
                [('code', '=', row['Subscription code'])]
            )
            if not contract:
                errors.append(
                    _("The contract {} has not be found (the invoice is {})").format(
                        row['Subscription code'], row['Invoice number']
                    )
                )
                continue
            contract = contract[0]
            invoice.payment_term_id = contract.payment_term_id
            invoice.payment_mode_id = contract.payment_mode_id
            invoice.mandate_id = contract.mandate_id
        if errors:
            self.errors = "\n".join(errors)
            self.state = 'errors'
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'contract.invoice.payment.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        return True
