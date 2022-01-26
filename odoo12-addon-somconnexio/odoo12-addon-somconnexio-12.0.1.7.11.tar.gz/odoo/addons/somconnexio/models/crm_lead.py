from odoo import _, models, fields, api
from odoo.exceptions import ValidationError

from odoo.addons.base_iban.models.res_partner_bank import \
    normalize_iban, pretty_iban, _map_iban_template

import re


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    subscription_request_id = fields.Many2one(
        'subscription.request', 'Subscription Request'
    )
    iban = fields.Char(string="IBAN")

    mobile_lead_line_id = fields.Many2one(
        'crm.lead.line',
        compute='_compute_mobile_lead_line_id',
        string="Mobile Lead Line",
    )

    skip_duplicated_phone_validation = fields.Boolean(
        string="Skip duplicated phone validation"
    )

    lead_line_id = fields.Integer(
        compute='_compute_lead_line_id',
        string="Lead Line ID",
    )

    # TODO: To modify if in the future we can have more than one `mobile_lead_line_id`
    def _compute_lead_line_id(self):
        for crm_lead in self:
            crm_lead.lead_line_id = crm_lead.lead_line_ids[0].id

    # TODO: To modify if in the future we can have more than one `mobile_lead_line_id`
    def _compute_mobile_lead_line_id(self):
        for crm_lead in self:
            for line in crm_lead.lead_line_ids:
                if line.mobile_isp_info:
                    crm_lead.mobile_lead_line_id = line
                    break

    def _ensure_crm_lead_iban_belongs_to_partner(self, crm_lead):
        partner_bank_ids = crm_lead.partner_id.bank_ids
        partner_iban_list = [bank.sanitized_acc_number for bank in partner_bank_ids]

        if crm_lead.iban and crm_lead.iban not in partner_iban_list:
            self.env['res.partner.bank'].create({
                'acc_type': 'iban',
                'acc_number': crm_lead.iban,
                'partner_id': crm_lead.partner_id.id
            })

    def action_set_won(self):
        for crm_lead in self:
            crm_lead.validate_won()
            if crm_lead.iban:
                self._ensure_crm_lead_iban_belongs_to_partner(crm_lead)
        super(CrmLead, self).action_set_won()

    def validate_won(self):
        if self.stage_id != self.env.ref("crm.stage_lead3"):
            raise ValidationError(
                _("The crm lead must be in remesa stage.")
            )
        if len(self.lead_line_ids) > 1:
            raise ValidationError(_(
                "The CRMLead to validate has more than one CRMLeadLine associated."
                " This shouldn't happen. Please contact the IP team."
            ))

    def _get_email_from_partner_or_SR(self, vals):
        if vals.get('partner_id'):
            contact_id = vals.get('partner_id')
            model = self.env['res.partner']
        else:
            contact_id = vals.get('subscription_request_id')
            model = self.env['subscription.request']
        return model.browse(contact_id).email

    @api.model
    def create(self, vals):
        if not vals.get("email_from"):
            vals["email_from"] = self._get_email_from_partner_or_SR(vals)
        return super(CrmLead, self).create(vals)

    def action_set_paused(self):
        paused_stage_id = self.env.ref('crm.stage_lead2').id
        for crm_lead in self:
            crm_lead.write({'stage_id': paused_stage_id})

    def action_set_remesa(self):
        remesa_stage_id = self.env.ref('crm.stage_lead3').id
        for crm_lead in self:
            crm_lead.validate_remesa()
            crm_lead.write({'stage_id': remesa_stage_id})

    def validate_remesa(self):
        self.ensure_one()
        # Check if related SR is validated
        if not self.partner_id:
            raise ValidationError(
                _("Error in {}: The subscription request related must be validated.").format(self.lead_line_id)  # noqa
            )
        # Validate IBAN
        if not self._get_bank_from_iban():
            raise ValidationError(
                _("Error in {}: Invalid bank.").format(self.lead_line_id)
            )
        # Validate phone number
        self._validate_phone_number()

        if self.stage_id != self.env.ref("crm.stage_lead1"):
            raise ValidationError(
                _("The crm lead must be in new stage.")
            )

    def _get_bank_from_iban(self):
        self.ensure_one()
        # Code copied from base_bank_from_iban module:
        # https://github.com/OCA/community-data-files/blob/12.0/base_bank_from_iban/models/res_partner_bank.py#L13  # noqa
        acc_number = pretty_iban(normalize_iban(self.iban)).upper()
        country_code = acc_number[:2].lower()
        iban_template = _map_iban_template[country_code]
        first_match = iban_template[2:].find('B') + 2
        last_match = iban_template.rfind('B') + 1
        bank_code = acc_number[first_match:last_match].replace(' ', '')
        bank = self.env['res.bank'].search([
            ('code', '=', bank_code),
            ('country.code', '=', country_code.upper()),
        ], limit=1)
        return bank

    def _phones_already_used(self, line):
        if self.skip_duplicated_phone_validation:
            return False

        phone = False
        if line.mobile_isp_info:
            phone = line.mobile_isp_info.phone_number
        else:
            phone = line.broadband_isp_info.phone_number
        if not phone:
            return False
        contracts = self.env["contract.contract"].search([
            ("is_terminated", "=", False),
            "|",
            "|",
            "|",
            ("mobile_contract_service_info_id.phone_number", "=", phone),
            ("vodafone_fiber_service_contract_info_id.phone_number", "=", phone),
            ("mm_fiber_service_contract_info_id.phone_number", "=", phone),
            ("adsl_service_contract_info_id.phone_number", "=", phone),
        ])
        won_stage_id = self.env.ref("crm.stage_lead4").id
        remesa_stage_id = self.env.ref("crm.stage_lead3").id
        new_stage_id = self.env.ref("crm.stage_lead1").id
        order_lines = self.env["crm.lead.line"].search([
            "|",
            ("lead_id.stage_id", "=", won_stage_id),
            ("lead_id.stage_id", "=", remesa_stage_id),
            "|",
            ("mobile_isp_info.phone_number", "=", phone),
            ("broadband_isp_info.phone_number", "=", phone),
        ])
        if contracts or order_lines:
            raise ValidationError(
                _("Error in {}: Contract or validated CRMLead with the same phone already exists.").format(self.lead_line_id)  # noqa
            )
        new_lines = self.env["crm.lead.line"].search([
            ("lead_id.stage_id", "=", new_stage_id),
            "|",
            ("mobile_isp_info.phone_number", "=", phone),
            ("broadband_isp_info.phone_number", "=", phone),
        ])
        if len(new_lines) > 1:
            raise ValidationError(
                _("Error in {}: Duplicated phone number in CRMLead petitions.").format(self.lead_line_id)  # noqa
            )

    def _phone_number_portability_format_validation(self, line):
        if line.mobile_isp_info_type == 'portability' or line.broadband_isp_info_type == 'portability':  # noqa
            phone = line.mobile_isp_info_phone_number or line.broadband_isp_info_phone_number  # noqa
            if not phone:
                raise ValidationError(
                    _('Phone number is required in a portability')
                )
            if line.mobile_isp_info:
                pattern = re.compile(r"^(6|7)?[0-9]{8}$")
                message = _('Mobile phone number has to be a 9 digit number starting with 6 or 7') # noqa
            else:
                pattern = re.compile(r"^(8|9)?[0-9]{8}$")
                message = _('Landline phone number has to be a 9 digit number starting with 8 or 9') # noqa

            isValid = pattern.match(phone)
            if not isValid:
                raise ValidationError(message)

    def _validate_phone_number(self):
        self.ensure_one()
        for line in self.lead_line_ids:
            self._phone_number_portability_format_validation(line)
            self._phones_already_used(line)
