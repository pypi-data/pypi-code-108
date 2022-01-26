from odoo import api, models, fields


class PartnerCreateSubscription(models.TransientModel):
    _inherit = "partner.create.subscription"
    bank_id = fields.Many2one('res.partner.bank', 'Bank Account', required=True)
    payment_type = fields.Selection([
        ('single', 'One single payment'),
        ('split', 'Ten payments')
    ], required=True)

    @api.multi
    def create_subscription(self):
        sub_req = self.env["subscription.request"]

        cooperator = self.cooperator
        vals = {
            "partner_id": cooperator.id,
            "vat": cooperator.vat,
            "share_product_id": self.share_product.id,
            "ordered_parts": self.share_qty,
            "cooperator": True,
            "user_id": self.env.uid,
            "email": self.email,
            "source": "crm",
            "address": self.cooperator.street,
            "zip_code": self.cooperator.zip,
            "city": self.cooperator.city,
            "country_id": self.cooperator.country_id.id,
            "lang": self.cooperator.lang,
        }

        if self.is_company:
            vals["company_name"] = cooperator.name
            vals["company_email"] = cooperator.email
            vals["is_company"] = True
        else:
            vals["firstname"] = cooperator.firstname
            vals["lastname"] = cooperator.lastname
            vals["is_company"] = False

        coop_vals = {}
        if not self._get_email():
            coop_vals["email"] = self.email

        vals["iban"] = self.bank_id.acc_number
        vals["payment_type"] = self.payment_type

        if coop_vals:
            cooperator.write(coop_vals)

        new_sub_req = sub_req.create(vals)

        return {
            "type": "ir.actions.act_window",
            "view_type": "form, tree",
            "view_mode": "form",
            "res_model": "subscription.request",
            "res_id": new_sub_req.id,
            "target": "current",
        }
