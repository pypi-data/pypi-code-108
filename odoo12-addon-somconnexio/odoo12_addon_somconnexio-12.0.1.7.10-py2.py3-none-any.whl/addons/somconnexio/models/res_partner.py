from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.addons.queue_job.job import job

from ..somoffice.user import SomOfficeUser
from ..services.vat_normalizer import VATNormalizer

from pyopencell.resources.customer import Customer
from ..opencell_services.crm_account_hierarchy_update_service \
    import CRMAccountHierarchyFromPartnerUpdateService
from ..opencell_services.customer_update_service \
    import CustomerFromPartnerUpdateService
from .opencell_configuration import OpenCellConfiguration


class ResPartner(models.Model):
    _inherit = 'res.partner'

    coop_agreement_id = fields.Many2one(
        'coop.agreement',
        string='Coop Agreement'
    )
    coop_agreement = fields.Boolean(string="Has cooperator agreement?",
                                    compute="_compute_coop_agreement",
                                    store=True,
                                    readonly=True)
    cooperator_end_date = fields.Date(string="Cooperator End Date",
                                      compute="_compute_cooperator_end_date",
                                      readonly=True)
    effective_date = fields.Date(compute="_compute_effective_date")
    volunteer = fields.Boolean(string="Volunteer")

    type = fields.Selection(
        [('contract-email', 'Contract Email'),
         ('service', 'Service Address'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Other address'),
         ('representative', 'Representative'),
         ], string='Address Type',
        default='representative',
    )
    nationality = fields.Many2one('res.country', 'Nacionality')

    contract_ids = fields.One2many(string="Contracts",
                                          comodel_name="contract.contract",
                                          inverse_name="partner_id")
    full_street = fields.Char(
        compute='_get_full_street',
        store=True
    )
    sc_effective_date = fields.Date('Somconnexio Effective Date')
    sc_cooperator_end_date = fields.Date('Somconnexio Cooperator End Date')
    sc_cooperator_register_number = fields.Integer('Somconnexio Cooperator Number')
    mail_activity_count = fields.Integer(
        compute='_compute_mail_activity_count',
        string='Activity Count'
    )
    has_active_contract = fields.Boolean(
        string='Has active contract',
        compute='_compute_active_contract',
        store=True,
        readonly=True
    )

    def _domain_sponsor_id(self):
        return [
            '|',
            ('member', '=', True),
            ('coop_candidate', '=', True),
        ]

    def _compute_mail_activity_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search(
            [('id', 'child_of', self.ids)]
        )
        all_partners.read(['parent_id'])

        mail_activity_groups = self.env['mail.activity'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in mail_activity_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.mail_activity_count += group['partner_id_count']
                partner = partner.parent_id

    @api.model
    def _name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        if ['customer', '=', True] in args:
            search_customer = True
        else:
            search_customer = False
        if ['parent_id', '=', False] in args:
            search_not_children = True
        else:
            search_not_children = False
        args = [
            arg for arg in args
            if arg != ['customer', '=', True] and arg != ['parent_id', '=', False]
        ]
        result = super()._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid
        )
        partner_ids = []
        for r in result:
            partner = self.browse(r[0])
            if partner.type == 'contract-email':
                partner_ids.append(partner.parent_id.id)
                continue
            else:
                if search_customer and not partner.customer:
                    continue
                if search_not_children and partner.parent_id:
                    continue
            partner_ids.append(r[0])
        if partner_ids:
            partner_ids = list(set(partner_ids))
            result = models.lazy_name_get(self.browse(partner_ids))
        else:
            result = []
        return result

    @api.multi
    def get_available_emails(self):
        self.ensure_one()
        email_list = self.env['res.partner'].search(
            [('parent_id', '=', self.id),
             ('type', '=', 'contract-email')
             ]
        )

        emails = set([e.email for e in email_list])
        if self.email and self.email not in emails:
            email_list = email_list | self

        return email_list

    @api.multi
    def get_available_email_ids(self):
        self.ensure_one()
        email_id_list = [self.id] if self.email else []
        email_id_obj = self.env['res.partner'].search(
            [('parent_id', '=', self.id),
             ('type', '=', 'contract-email')
             ]
        )
        for data in email_id_obj:
            email_id_list.append(data.id)
        return email_id_list

    def _get_name(self):
        if 'email_tags' in self.env.context:
            return self.email
        if self.type == 'service':
            self.name = dict(self.fields_get(['type'])['type']['selection'])[self.type]
        res = super()._get_name()
        return res

    @api.multi
    @api.depends("sponsor_id", "coop_agreement_id")
    @api.depends("subscription_request_ids.state")
    def _compute_coop_candidate(self):
        for partner in self:
            if partner.member:
                is_candidate = False
            else:
                sub_requests = partner.subscription_request_ids.filtered(
                    lambda record: (
                        record.state == 'done' and
                        not record.sponsor_id and
                        not record.coop_agreement_id
                    )
                )
                is_candidate = bool(sub_requests)
            partner.coop_candidate = is_candidate

    @api.multi
    @api.depends("sponsor_id", "coop_agreement_id")
    def _compute_coop_agreement(self):
        for partner in self:
            if partner.coop_agreement_id:
                partner.coop_agreement = True
            else:
                partner.coop_agreement = False

    @api.multi
    @api.depends("old_member", "member", "coop_candidate")
    def _compute_cooperator_end_date(self):
        for partner in self:
            if not partner.old_member or partner.coop_candidate or partner.member:
                end_date = False
            else:
                subsc_register_end_date = self.env['subscription.register'].search(
                    [
                        ('partner_id', '=', partner.id),
                        ('type', '=', 'sell_back'),
                    ],
                    limit=1,
                    order="date DESC"
                )
                end_date = subsc_register_end_date.date or False
            partner.cooperator_end_date = end_date

    @api.one
    @api.constrains('child_ids')
    def _check_invoice_address(self):
        invoice_addresses = self.env['res.partner'].search([
            ('parent_id', '=', self.id),
            ('type', '=', 'invoice')
        ])
        if len(invoice_addresses) > 1:
            raise ValidationError(
                _('More than one Invoice address by partner is not allowed')
            )

    def _set_contract_emails_vals(self, vals):
        new_vals = {}
        if 'parent_id' in vals:
            new_vals['parent_id'] = vals['parent_id']
        if 'email' in vals:
            new_vals['email'] = vals['email']
        new_vals['type'] = 'contract-email'
        new_vals['customer'] = False
        return new_vals

    @api.depends('street', 'street2')
    def _get_full_street(self):
        for record in self:
            if record.street2:
                record.full_street = "{} {}".format(record.street, record.street2)
            else:
                record.full_street = record.street

    @api.depends('contract_ids.is_terminated')
    def _compute_active_contract(self):
        for record in self:
            contracts = self.env["contract.contract"].search([
                ("partner_id", "=", record.id),
            ])
            if not contracts:
                record.has_active_contract = False
            if any(not contract.is_terminated for contract in contracts):
                record.has_active_contract = True

    @job
    def create_user(self, partner):
        SomOfficeUser(
            partner.ref,
            partner.email,
            partner.vat,
            partner.lang,
        ).create()

    @job
    def update_accounts_address(self):
        customer = Customer.get(self.ref).customer
        customer_accounts = customer.customerAccounts['customerAccount']
        for customer_account_code in [ca.get('code') for ca in customer_accounts]:
            self.with_delay().update_subscription('address', customer_account_code)

    @job
    def update_subscription(self, updated_field, customer_account_code):
        CRMAccountHierarchyFromPartnerUpdateService(
            self, updated_field, customer_account_code
        ).run()

    @job
    def update_customer(self):
        CustomerFromPartnerUpdateService(
            self, OpenCellConfiguration(self.env)
        ).run()

    @api.model
    def create(self, vals):
        if not (vals.get("ref") or vals.get("parent_id")):
            vals['ref'] = self.env.ref(
                "somconnexio.sequence_partner"
            ).next_by_id()

        if 'type' in vals and vals['type'] == 'contract-email':
            vals = self._set_contract_emails_vals(vals)
        elif 'type' in vals and vals['type'] == 'invoice':
            raise UserError(_('Invoice addresses should not be used anymore'))
        if 'vat' in vals:
            vals['vat'] = VATNormalizer(vals['vat']).normalize()

            existing_vats = self.env['res.partner'].search([
                "|",
                ('vat', '=', vals['vat']),
                ('vat', '=', VATNormalizer(vals['vat']).convert_spanish_vat()),
            ])
            if existing_vats:
                raise UserError(
                    _(
                        "A partner with VAT %s already exists in our system"
                    ) % vals['vat']
                )
        return super().create(vals)

    def write(self, vals):
        def obj_to_name(model, id):
            return self.env[model].browse(id).name
        if 'vat' in vals:
            vals['vat'] = VATNormalizer(vals['vat']).normalize()
        if 'type' in vals and vals['type'] == 'contract-email':
            vals = self._set_contract_emails_vals(vals)
            for partner in self:
                partner.name = False
                partner.street = False
                partner.street2 = False
                partner.city = False
                partner.state_id = False
                partner.country_id = False
                partner.customer = False
        if 'active' in vals and self.env.user.login not in ("admin", "__system__"):
            raise UserError(_('You cannot archive contacts'))
        address_fields_str = ['street',  'street2', 'zip', 'city']
        address_fields_obj = {
            'state_id': 'res.country.state',
            'country_id': 'res.country'
        }
        message_template = _("Contact address has been changed from {} to {}")
        messages = {}
        for partner in self:
            messages[partner.id] = [
                message_template.format(partner[field], vals[field])
                for field in vals for address_field in address_fields_str
                if field == address_field and vals[field] != partner[field]
            ]
            messages[partner.id] += [
                message_template.format(
                    partner[field].name,
                    obj_to_name(address_fields_obj[field], vals[field])
                )
                for field in vals for address_field in address_fields_obj
                if field == address_field and vals[field] != partner[field].id
            ]

        super().write(vals)
        for partner in self:
            for message in messages[partner.id]:
                partner.message_post(message)
        return True

    # TAKE IN MIND: We can overwrite this method from res_partner for now,
    # but in the future we might need the 'representative' feature.
    # https://github.com/coopiteasy/vertical-cooperative/blob/12.0/easy_my_coop/models/partner.py#L217  # noqa
    @api.multi
    def has_representative(self):
        return True

    def _invoice_state_action_view_partner_invoices(self):
        """ Return a list of states to filter the invoices with operator 'not in' """
        return ['cancel']

    # Override this method of account to modify the invoice states used to filter
    # the invoices to show.
    # This code can be moved to the original account model.
    @api.multi
    def action_view_partner_invoices(self):
        action = super().action_view_partner_invoices()
        domain = action["domain"]
        domain = [rule for rule in domain if rule[0] != 'state']
        domain.append(
            (
                'state',
                'not in',
                self._invoice_state_action_view_partner_invoices()
            )
        )
        action["domain"] = domain
        return action

    @api.multi
    @api.depends("share_ids")
    def _compute_effective_date(self):
        for partner in self:
            if partner.share_ids:
                partner.effective_date = partner.share_ids.sorted(
                    "effective_date",
                    reverse=True
                )[0].effective_date

    def _construct_constraint_msg(self, country_code):
        # This method overrides the one from base_vat module to get adequate translation
        # and removes funcionality we were not using
        # https://github.com/OCA/OCB/blob/14.0/addons/base_vat/models/res_partner.py
        return '\n' + _(
            'The VAT number {vat} for partner {name} does not seem to be valid. \n'
            'Note: Expected format for DNI is ESXXXXXXXX [Letter], for NIE is ES [Letter] XXXXXXX [Letter]').format(  # noqa
            vat=self.vat,
            name=self.name,
        )
