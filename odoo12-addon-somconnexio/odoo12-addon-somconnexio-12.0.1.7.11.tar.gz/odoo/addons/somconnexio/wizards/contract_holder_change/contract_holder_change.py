from datetime import date
from odoo import models, fields, api, _


class ContractIbanChangeWizard(models.TransientModel):
    _name = 'contract.holder.change.wizard'
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    contract_id = fields.Many2one('contract.contract')
    change_date = fields.Date('Change Date', required=True)
    payment_mode = fields.Many2one(
        'account.payment.mode',
        string='Payment mode',
        required=True,
    )
    banking_mandate_required = fields.Boolean(
        related="payment_mode.payment_method_id.bank_account_required"
    )
    available_banking_mandates = fields.Many2many(
        'account.banking.mandate',
        compute="_compute_available_banking_mandates"
    )
    banking_mandate_id = fields.Many2one(
        'account.banking.mandate',
        string='Banking mandate',
    )
    email_ids = fields.Many2many(
        'res.partner',
        string='Emails',
        required=True,
    )
    available_email_ids = fields.Many2many(
        'res.partner',
        string="Available Emails",
        compute="_load_available_email_ids"
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['contract_id'] = self.env.context['active_id']
        defaults['payment_mode'] = self.env.ref(
            'somconnexio.payment_mode_inbound_sepa').id
        defaults['change_date'] = date.today()
        return defaults

    @api.multi
    @api.depends("partner_id")
    def _load_available_email_ids(self):
        if self.partner_id:
            self.available_email_ids = [
                (6, 0, self.partner_id.get_available_email_ids())
            ]

    @api.multi
    @api.depends("partner_id")
    def _compute_available_banking_mandates(self):
        if self.partner_id:
            partner_mandates = self.env['account.banking.mandate'].search([
                ('partner_id', '=', self.partner_id.id),
            ])
            self.available_banking_mandates = partner_mandates

    @api.multi
    def button_change(self):
        self.ensure_one()

        new_contract = self._create_new_contract()
        self._terminate_contract(new_contract)
        return True

    def _get_or_create_service_partner_id(self):

        service_partner = self.env['res.partner'].search([
            ('parent_id', '=', self.partner_id.id),
            ('type', '=', 'service'),
            ('street', 'ilike', self.contract_id.service_partner_id.street),
        ])

        if not service_partner:
            service_partner = self.env['res.partner'].create({
                'parent_id': self.partner_id.id,
                'name': 'New partner service',
                'type': 'service',
                'street': self.contract_id.service_partner_id.street,
                'street2': self.contract_id.service_partner_id.street2,
                'city': self.contract_id.service_partner_id.city,
                'zip': self.contract_id.service_partner_id.zip,
                'state_id': self.contract_id.service_partner_id.state_id.id,
                'country_id': self.contract_id.service_partner_id.country_id.id,
            })

        return service_partner

    def _create_new_contract(self):

        service_partner = self._get_or_create_service_partner_id()

        new_contract_params = {
            'partner_id': self.partner_id.id,
            'service_partner_id': service_partner.id,
            'payment_mode_id': self.payment_mode.id,
            'mandate_id': self.banking_mandate_id.id,
            'email_ids': [(6, 0, [email.id for email in self.email_ids])],
            'journal_id': self.contract_id.journal_id.id,
            'service_technology_id': self.contract_id.service_technology_id.id,
            'service_supplier_id': self.contract_id.service_supplier_id.id,
            'contract_line_ids': [
                (0, 0, self._prepare_create_line(line))
                for line in self.contract_id.contract_line_ids
            ],
        }

        # TODO: This code is duplicated in ContractService
        if self.contract_id.mobile_contract_service_info_id:
            new_contract_params['name'] = \
                self.contract_id.mobile_contract_service_info_id.phone_number
            new_contract_params['mobile_contract_service_info_id'] = \
                self.contract_id.mobile_contract_service_info_id.id
        elif self.contract_id.adsl_service_contract_info_id:
            new_contract_params['name'] = \
                self.contract_id.adsl_service_contract_info_id.phone_number
            new_contract_params['adsl_service_contract_info_id'] = \
                self.contract_id.adsl_service_contract_info_id.id
        elif self.contract_id.vodafone_fiber_service_contract_info_id:
            new_contract_params['name'] = \
                self.contract_id.vodafone_fiber_service_contract_info_id.phone_number
            new_contract_params['vodafone_fiber_service_contract_info_id'] = \
                self.contract_id.vodafone_fiber_service_contract_info_id.id
        elif self.contract_id.mm_fiber_service_contract_info_id:
            new_contract_params['name'] = \
                self.contract_id.mm_fiber_service_contract_info_id.phone_number
            new_contract_params['mm_fiber_service_contract_info_id'] = \
                self.contract_id.mm_fiber_service_contract_info_id.id

        return self.env['contract.contract'].create(new_contract_params)

    def _terminate_contract(self, new_contract):
        self.contract_id._terminate_contract(
            self.env.ref('somconnexio.reason_holder_change'),
            'New contract created with ID: {}\nNotes: {}'.format(
                new_contract.id,
                self.notes or ''
            ),
            self.change_date,
            self.env.ref('somconnexio.user_reason_other'),
        )

        # TODO: Notify the change?
        message = _("""
            Holder change wizard
            New contract created with ID: {}
            Notes: {}
            """)
        self.contract_id.message_post(
            message.format(new_contract.id, self.notes or '')
        )

    def _prepare_create_line(self, line):
        return {
            "name": line.product_id.name,
            "product_id": line.product_id.id,
            "date_start": self.change_date
        }

    @api.onchange('partner_id')
    def check_partner_id_change(self):
        self.service_partner_id = False
        self.bank_id = False
        self.email_ids = False

        if not self.partner_id:
            partner_id_domain = []
            bank_domain = []
        else:
            partner_id_domain = [
                '|',
                ('id', '=', self.partner_id.id),
                ('parent_id', '=', self.partner_id.id)
            ]
            bank_domain = [
                ('partner_id', '=', self.partner_id.id)
            ]

        return {
            'domain': {
                'service_partner_id': partner_id_domain,
                'bank_id': bank_domain
            }
        }
