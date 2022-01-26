from odoo import models, fields, api, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError, UserError
from datetime import date

from ..opencell_services.crm_account_hierarchy_create_service \
    import CRMAccountHierarchyFromContractCreateService
from ..opencell_services.subscription_service \
    import SubscriptionService
from ..opencell_services.crm_account_hierarchy_update_service \
    import CRMAccountHierarchyFromContractUpdateService
from .opencell_configuration import OpenCellConfiguration
from ..services.contract_contract_process import ContractContractProcess


class Contract(models.Model):
    _inherit = 'contract.contract'

    def _get_default_journal(self):
        return self.env.ref('somconnexio.consumption_invoices_journal')

    name = fields.Char(compute='_compute_name', store=True, readonly=True)
    service_technology_id = fields.Many2one(
        'service.technology',
        'Service Technology',
        required=True,
    )
    service_supplier_id = fields.Many2one(
        'service.supplier',
        'Service Supplier',
        required=True,
    )

    service_partner_id = fields.Many2one(
        'res.partner',
        'Service Contact',
    )
    is_broadband = fields.Boolean(
        compute='_get_is_broadband',
    )
    service_contract_type = fields.Char(
        compute='_get_contract_type',
    )
    email_ids = fields.Many2many(
        'res.partner',
        string='Emails',
    )
    available_email_ids = fields.Many2many(
        'res.partner',
        string="Available Emails",
        compute="_load_available_email_ids"
    )

    crm_lead_line_id = fields.Many2one(
        'crm.lead.line',
        string="Crm Lead Line"
    )
    mobile_contract_service_info_id = fields.Many2one(
        'mobile.service.contract.info',
        domain=[('id', '=', 0)],
        string='Service Contract Info'
    )
    vodafone_fiber_service_contract_info_id = fields.Many2one(
        'vodafone.fiber.service.contract.info',
        domain=[('id', '=', 0)],
        string="Service Contract Info"
    )
    mm_fiber_service_contract_info_id = fields.Many2one(
        'mm.fiber.service.contract.info',
        domain=[('id', '=', 0)],
        string='Service Contract Info'
    )
    orange_fiber_service_contract_info_id = fields.Many2one(
        'orange.fiber.service.contract.info',
        domain=[('id', '=', 0)],
        string='Service Contract Info'
    )
    router_4G_service_contract_info_id = fields.Many2one(
        'router.4g.service.contract.info',
        domain=[('id', '=', 0)],
        string='Service Contract Info'
    )
    xoln_fiber_service_contract_info_id = fields.Many2one(
        'xoln.fiber.service.contract.info',
        domain=[('id', '=', 0)],
        string='Service Contract Info'
    )
    adsl_service_contract_info_id = fields.Many2one(
        'adsl.service.contract.info',
        domain=[('id', '=', 0)],
        string='Service Contract Info'
    )
    current_tariff_contract_line = fields.Many2one(
        'contract.line',
        compute='_compute_current_tariff_contract_line',
        store=True
    )
    tariff_contract_line = fields.Many2one(
        'contract.line',
        compute='_compute_tariff_contract_line',
    )
    current_tariff_product = fields.Many2one(
        'product.product',
        related='current_tariff_contract_line.product_id',
        string="Current Tariff",
        store=True
    )
    tariff_product = fields.Many2one(
        'product.product',
        related='tariff_contract_line.product_id',
        string="Current Tariff"
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=_get_default_journal,
    )

    date_start = fields.Date(
        compute='_compute_date_start', string='Date Start', store=True
    )
    phone_number = fields.Char(
        compute='_compute_phone_number', string='Service Phone Number', store=True
    )

    icc = fields.Char('ICC', related='mobile_contract_service_info_id.icc')
    ppp_user = fields.Char(
        'PPP User', related='adsl_service_contract_info_id.ppp_user'
    )
    ppp_password = fields.Char(
        'PPP Password', related='adsl_service_contract_info_id.ppp_password'
    )
    endpoint_user = fields.Char(
        'Endpoint User', related='adsl_service_contract_info_id.endpoint_user'
    )
    endpoint_password = fields.Char(
        'Endpoint Password', related='adsl_service_contract_info_id.endpoint_password'
    )
    vodafone_id = fields.Char(
        'Vodafone ID',
        compute='_compute_vodafone_id',
        store=True,
    )
    vodafone_offer_code = fields.Char(
        'Vodafone Offer Code',
        compute='_compute_vodafone_offer_code',
    )
    mm_id = fields.Char(
        'MásMóvil ID',
        related='mm_fiber_service_contract_info_id.mm_id'
    )
    suma_id = fields.Char(
        'Suma ID',
        related='orange_fiber_service_contract_info_id.suma_id'
    )
    external_id = fields.Char(
        'External ID',
        related='xoln_fiber_service_contract_info_id.external_id'
    )
    project = fields.Selection(
        'Project',
        related='xoln_fiber_service_contract_info_id.project'
    )
    id_order = fields.Char(
        'Order ID',
        related='xoln_fiber_service_contract_info_id.id_order'
    )
    administrative_number = fields.Char(
        'Administrative Number',
        related='adsl_service_contract_info_id.administrative_number'
    )
    order_id = fields.Char(
        'Order Id',
        related='adsl_service_contract_info_id.id_order'
    )
    router_product_id = fields.Many2one(
        'product.product', 'Router Model',
        compute='_compute_router_product_id',
    )
    router_lot_id = fields.Many2one(
        'stock.production.lot', 'S/N / MAC Address',
        compute='_compute_router_lot_id',
    )
    partner_priority = fields.Text(
        'Partner priority',
        related='partner_id.priority_id.description'
    )
    mail_activity_count = fields.Integer(
        compute='_compute_mail_activity_count',
        string='Activity Count'
    )
    ticket_number = fields.Char(string='Ticket Number')

    terminate_user_reason_id = fields.Many2one(
        'contract.terminate.user.reason',
        string="Termination User Reason",
        ondelete="restrict",
        readonly=True,
        copy=False,
        track_visibility="onchange",
    )

    category_id = fields.Many2many(
        'res.partner.category',
        string='Tags',
        related="partner_id.category_id",
    )

    res_partner_user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        related='partner_id.user_id'
    )

    previous_id = fields.Char(
        compute='_compute_previous_id',
        inverse='_set_previous_id',
        string='Previous Id',
        readonly=False,
    )

    fiber_signal_type_id = fields.Many2one(
        'fiber.signal.type',
        string="Fiber Signal Type",
    )

    service_partner_street = fields.Char(
        related='service_partner_id.street'
    )
    service_partner_zip = fields.Char(
        related='service_partner_id.zip'
    )
    service_partner_city = fields.Char(
        related='service_partner_id.city'
    )
    service_partner_state = fields.Many2one(
        related='service_partner_id.state_id'
    )

    # Hide fields from odoo custom filter by inheriting function fields_get()
    @api.model
    def fields_get(self, fields=None):
        res = super().fields_get()
        res.pop('tariff_product', None)
        return res

    def _compute_mail_activity_count(self):
        for contract in self:
            count = self.env['mail.activity'].search_count([
                ('res_id', '=', contract.id),
                ('res_model', '=', 'contract.contract')
            ])
            contract.mail_activity_count = count

    @api.depends(
        'vodafone_fiber_service_contract_info_id.vodafone_id',
        'router_4G_service_contract_info_id.vodafone_id'
    )
    def _compute_vodafone_id(self):
        for contract in self:
            contract.vodafone_id = (
                contract.vodafone_fiber_service_contract_info_id.vodafone_id or  # noqa
                contract.router_4G_service_contract_info_id.vodafone_id          # noqa
            )

    @api.depends(
        'vodafone_fiber_service_contract_info_id.vodafone_offer_code',
        'router_4G_service_contract_info_id.vodafone_offer_code'
    )
    def _compute_vodafone_offer_code(self):
        for contract in self:
            contract.vodafone_offer_code = (
                contract.vodafone_fiber_service_contract_info_id.vodafone_offer_code or  # noqa
                contract.router_4G_service_contract_info_id.vodafone_offer_code          # noqa
            )

    @api.depends(
        'service_contract_type', 'mobile_contract_service_info_id.phone_number',
        'adsl_service_contract_info_id.phone_number',
        'mm_fiber_service_contract_info_id.phone_number',
        'vodafone_fiber_service_contract_info_id.phone_number',
        'orange_fiber_service_contract_info_id.phone_number',
        'router_4G_service_contract_info_id.phone_number'
    )
    def _compute_phone_number(self):
        contract_type = self.service_contract_type
        if contract_type == 'mobile':
            self.phone_number = (
                self.mobile_contract_service_info_id.phone_number
            )
        elif contract_type == 'adsl':
            self.phone_number = (
                self.adsl_service_contract_info_id.phone_number
            )
        elif contract_type == 'vodafone':
            self.phone_number = (
                self.vodafone_fiber_service_contract_info_id.phone_number
            )
        elif contract_type == 'masmovil':
            self.phone_number = (
                self.mm_fiber_service_contract_info_id.phone_number
            )
        elif contract_type == 'xoln':
            self.phone_number = (
                self.xoln_fiber_service_contract_info_id.phone_number
            )
        elif contract_type == 'router4G':
            self.phone_number = (
                self.router_4G_service_contract_info_id.phone_number
            )
        elif contract_type == 'orange':
            self.phone_number = (
                self.orange_fiber_service_contract_info_id.phone_number
            )

    @api.depends(
        'service_contract_type',
        'xoln_fiber_service_contract_info_id.router_product_id',
        'adsl_service_contract_info_id.router_product_id',
    )
    def _compute_router_product_id(self):
        for contract in self:
            contract_type = contract.service_contract_type
            if contract_type == 'adsl':
                contract.router_product_id = (
                    contract.adsl_service_contract_info_id.router_product_id
                )
            elif contract_type == 'xoln':
                contract.router_product_id = (
                    contract.xoln_fiber_service_contract_info_id.router_product_id
                )
            else:
                contract.router_product_id = False

    @api.depends(
        'service_contract_type',
        'xoln_fiber_service_contract_info_id.router_lot_id',
        'adsl_service_contract_info_id.router_lot_id',
    )
    def _compute_router_lot_id(self):
        for contract in self:
            contract_type = contract.service_contract_type
            if contract_type == 'adsl':
                contract.router_lot_id = (
                    contract.adsl_service_contract_info_id.router_lot_id
                )
            elif contract_type == 'xoln':
                contract.router_lot_id = (
                    contract.xoln_fiber_service_contract_info_id.router_lot_id
                )
            else:
                contract.router_product_id = False

    @api.depends(
        'service_contract_type',
        'adsl_service_contract_info_id.previous_id',
        'mm_fiber_service_contract_info_id.previous_id',
        'router_4G_service_contract_info_id.previous_id',
        'vodafone_fiber_service_contract_info_id.previous_id',
        'xoln_fiber_service_contract_info_id.previous_id',
        'orange_fiber_service_contract_info_id.previous_id'
    )
    def _compute_previous_id(self):
        for record in self:
            contract_type = record.service_contract_type
            if contract_type == 'adsl':
                record.previous_id = (
                    record.adsl_service_contract_info_id.previous_id
                )
            elif contract_type == 'masmovil':
                record.previous_id = (
                    record.mm_fiber_service_contract_info_id.previous_id
                )
            elif contract_type == 'vodafone':
                record.previous_id = (
                    record.vodafone_fiber_service_contract_info_id.previous_id
                )
            elif contract_type == 'xoln':
                record.previous_id = (
                    record.xoln_fiber_service_contract_info_id.previous_id
                )
            elif contract_type == 'router4G':
                record.previous_id = (
                    record.router_4G_service_contract_info_id.previous_id
                )
            elif contract_type == 'orange':
                record.previous_id = (
                    record.orange_fiber_service_contract_info_id.previous_id
                )

    def _set_previous_id(self):
        for record in self:
            contract_type = record.service_contract_type
            if contract_type == 'adsl':
                record.adsl_service_contract_info_id.previous_id = (
                    record.previous_id
                )
            elif contract_type == 'masmovil':
                record.mm_fiber_service_contract_info_id.previous_id = (
                    record.previous_id
                )
            elif contract_type == 'vodafone':
                record.vodafone_fiber_service_contract_info_id.previous_id = (
                    record.previous_id
                )
            elif contract_type == 'xoln':
                record.xoln_fiber_service_contract_info_id.previous_id = (
                    record.previous_id
                )
            elif contract_type == 'router4G':
                record.router_4G_service_contract_info_id.previous_id = (
                    record.previous_id
                )
            elif contract_type == 'orange':
                record.orange_fiber_service_contract_info_id.previous_id = (
                    record.previous_id
                )

    @api.depends('phone_number')
    def _compute_name(self):
        self.name = self.phone_number

        if not self.name and self.service_contract_type == "router4G":
            self.name = self.router_4G_service_contract_info_id.name

    @api.onchange('service_supplier_id')
    def onchange_service_supplier_id(self):
        coaxial = self.env.ref('somconnexio.coaxial_fiber_signal')
        ftth = self.env.ref('somconnexio.FTTH_fiber_signal')
        neba_ftth = self.env.ref('somconnexio.FTTH_neba_fiber_signal')
        indirect = self.env.ref('somconnexio.indirect_fiber_signal')

        if (self.service_supplier_id ==
                self.env.ref('somconnexio.service_supplier_vodafone')):
            allowed_types = [coaxial.id, ftth.id, neba_ftth.id]
        elif (self.service_supplier_id ==
                self.env.ref('somconnexio.service_supplier_masmovil')):
            allowed_types = [ftth.id, indirect.id]
        elif (self.service_supplier_id ==
                self.env.ref('somconnexio.service_supplier_orange')):
            allowed_types = [ftth.id, indirect.id]
        else:
            return

        return {'domain': {'fiber_signal_type_id': [('id', 'in', allowed_types)]}}

    @api.constrains('service_technology_id', 'service_supplier_id')
    def validate_contract_service_info(self):
        if self.service_technology_id == self.env.ref(
            'somconnexio.service_technology_mobile'
        ) and not self.mobile_contract_service_info_id:
            raise ValidationError(_(
                'Mobile Contract Service Info is required'
                'for technology Mobile'
            ))
        if self.service_technology_id == self.env.ref(
            'somconnexio.service_technology_adsl'
        ) and not self.adsl_service_contract_info_id:
            raise ValidationError(_(
                'ADSL Contract Service Info is required'
                'for technology ADSL'
            ))
        if self.service_technology_id == self.env.ref(
            'somconnexio.service_technology_4G'
        ) and not self.router_4G_service_contract_info_id:
            raise ValidationError(_(
                'Router 4G Contract Service Info is required '
                'for technology Router 4G'
            ))

        if self.service_technology_id == self.env.ref(
            'somconnexio.service_technology_fiber'
        ):
            if self.service_supplier_id == self.env.ref(
                'somconnexio.service_supplier_masmovil'
            ) and not self.mm_fiber_service_contract_info_id:
                raise ValidationError(_(
                    'MásMóvil Fiber Contract Service Info is required'
                    'for technology Fiber and supplier MásMóvil'
                ))

            if self.service_supplier_id == self.env.ref(
                'somconnexio.service_supplier_vodafone'
            ) and not self.vodafone_fiber_service_contract_info_id:
                raise ValidationError(_(
                    'Vodafone Fiber Contract Service Info is required'
                    'for technology Fiber and supplier Vodafone'
                ))
            if self.service_supplier_id == self.env.ref(
                'somconnexio.service_supplier_xoln'
            ) and not self.xoln_fiber_service_contract_info_id:
                raise ValidationError(_(
                    'XOLN Fiber Contract Service Info is required'
                    'for technology Fiber and supplier XOLN'
                ))
            if self.service_supplier_id == self.env.ref(
                'somconnexio.service_supplier_orange'
            ) and not self.orange_fiber_service_contract_info_id:
                raise ValidationError(_(
                    'Orange Fiber Contract Service Info is required'
                    'for technology Fiber and supplier Orange'
                ))

    @api.multi
    @api.depends("partner_id")
    def _load_available_email_ids(self):
        for contract in self:
            if contract.partner_id:
                contract.available_email_ids = [
                    (6, 0, contract.partner_id.get_available_email_ids())
                ]

    @api.depends('service_technology_id')
    def _get_is_broadband(self):
        for record in self:
            adsl = self.env.ref('somconnexio.service_technology_adsl')
            fiber = self.env.ref('somconnexio.service_technology_fiber')
            router4G = self.env.ref('somconnexio.service_technology_4G')
            record.is_broadband = (
                adsl.id == record.service_technology_id.id
                or
                fiber.id == record.service_technology_id.id
                or
                router4G.id == record.service_technology_id.id
            )

    @api.depends('service_technology_id', 'service_supplier_id')
    def _get_contract_type(self):
        adsl = self.env.ref('somconnexio.service_technology_adsl')
        fiber = self.env.ref('somconnexio.service_technology_fiber')
        mobile = self.env.ref('somconnexio.service_technology_mobile')
        router4G = self.env.ref('somconnexio.service_technology_4G')
        vodafone = self.env.ref('somconnexio.service_supplier_vodafone')
        masmovil = self.env.ref('somconnexio.service_supplier_masmovil')
        orange = self.env.ref('somconnexio.service_supplier_orange')
        xoln = self.env.ref('somconnexio.service_supplier_xoln')
        for record in self:
            if record.service_technology_id == mobile:
                record.service_contract_type = 'mobile'
            elif record.service_technology_id == adsl:
                record.service_contract_type = 'adsl'
            elif record.service_technology_id == router4G:
                record.service_contract_type = 'router4G'
            elif record.service_technology_id == fiber:
                if record.service_supplier_id == vodafone:
                    record.service_contract_type = 'vodafone'
                elif record.service_supplier_id == masmovil:
                    record.service_contract_type = 'masmovil'
                elif record.service_supplier_id == xoln:
                    record.service_contract_type = 'xoln'
                elif record.service_supplier_id == orange:
                    record.service_contract_type = 'orange'

    def _tariff_contract_line(self, field, current):
        adsl = self.env.ref('somconnexio.service_technology_adsl')
        mobile = self.env.ref('somconnexio.service_technology_mobile')
        ba_4G = self.env.ref('somconnexio.service_technology_4G')
        for contract in self:
            if contract.service_technology_id == mobile:
                service_categ = self.env.ref('somconnexio.mobile_service')
            elif contract.service_technology_id == adsl:
                service_categ = self.env.ref('somconnexio.broadband_adsl_service')
            elif contract.service_technology_id == ba_4G:
                service_categ = self.env.ref('somconnexio.broadband_4G_service')
            else:  # fiber
                service_categ = self.env.ref('somconnexio.broadband_fiber_service')

            for line in contract.contract_line_ids:
                if (
                    line.product_id.categ_id.id == service_categ.id
                    and (
                        contract._is_contract_line_active(line)
                        or not current
                    )
                ):
                    setattr(contract, field, line)
                    break

    @api.model
    def cron_compute_current_tariff_contract_line(self):
        domain = [
            ('mobile_contract_service_info_id', '!=', False),
            '|',
            ('date_end', '>', date.today().strftime('%Y-%m-%d')),
            ('date_end', '=', False)
        ]
        mobile_contracts = self.search(domain)
        for contract in mobile_contracts:
            contract._compute_current_tariff_contract_line()

    @api.depends('service_technology_id', 'contract_line_ids')
    def _compute_current_tariff_contract_line(self):
        self._tariff_contract_line('current_tariff_contract_line', current=True)

    @api.depends('service_technology_id', 'contract_line_ids')
    def _compute_tariff_contract_line(self):
        self._tariff_contract_line('tariff_contract_line', current=False)

    def _is_contract_line_active(self, line):
        if (
            (line.date_end and line.date_start <= date.today() <= line.date_end)
            or (not line.date_end and line.date_start <= date.today())
        ):
            return True
        else:
            return False

    @api.one
    @api.constrains('partner_id', 'service_partner_id')
    def _check_service_partner_id(self):
        if (
            self.service_technology_id == self.env.ref(
                'somconnexio.service_technology_mobile'
            )
        ):
            return True
        if self.service_partner_id == self.partner_id:
            return True
        if self.service_partner_id.parent_id != self.partner_id:
            raise ValidationError(
                _('Service contact must be a child of %s') % (
                    self.partner_id.name
                )
            )
        if self.service_partner_id.type != 'service':
            raise ValidationError(
                _('Service contact %s must be service type') % (
                    self.service_partner_id.name
                )
            )

    @api.one
    @api.constrains('partner_id', 'invoice_partner_id')
    def _check_invoice_partner_id(self):
        if not self.invoice_partner_id or self.invoice_partner_id == self.partner_id:
            return True
        if self.invoice_partner_id.parent_id != self.partner_id:
            raise ValidationError(
                _('Invoicing contact must be a child of %s') % (
                    self.partner_id.name
                )
            )
        if self.invoice_partner_id.type != 'invoice':
            raise ValidationError(
                _('Invoicing contact %s must be invoice type') % (
                    self.invoice_partner_id.name
                )
            )

    @api.one
    @api.constrains('service_technology_id', 'service_supplier_id')
    def _check_service_technology_service_supplier(self):
        available_relations = (
            self.env['service.technology.service.supplier'].search([
                ('service_technology_id', '=', self.service_technology_id.id)
            ])
        )
        available_service_suppliers = [
            s.service_supplier_id.id for s in available_relations
        ]
        if self.service_supplier_id.id not in available_service_suppliers:
            raise ValidationError(
                _('Service supplier %s is not allowed by service technology %s')
                % (
                    self.service_supplier_id.name,
                    self.service_technology_id.name
                )
            )

    @api.one
    @api.constrains('service_technology_id', 'service_supplier_id', 'contract_line_ids')
    def _check_service_category_products(self):
        available_relations = self.env['product.category.technology.supplier'].search([
            ('service_technology_id', '=', self.service_technology_id.id),
            ('service_supplier_id', '=', self.service_supplier_id.id)
        ])
        available_categories = [c.product_category_id.id for c in available_relations]
        available_products_categ = self.env['product.template'].search([
            ('categ_id', 'in', available_categories)
        ])

        for line in self.contract_line_ids:
            if line.product_id.product_tmpl_id not in available_products_categ:
                raise ValidationError(
                    _('Product %s is not allowed by contract with \
                            technology %s and supplier %s') % (
                        line.product_id.name,
                        self.service_technology_id.name,
                        self.service_supplier_id.name
                    )
                )

    @api.one
    @api.constrains('partner_id', 'contract_line_ids')
    def _check_coop_agreement(self):
        if self.partner_id.coop_agreement:
            for line in self.contract_line_ids:
                line_prod_tmpl_id = line.product_id.product_tmpl_id
                agreement = self.partner_id.coop_agreement_id
                if line_prod_tmpl_id not in agreement.products:
                    raise ValidationError(
                        _('Product %s is not allowed by agreement %s') % (
                            line.product_id.name, agreement.code
                        )
                    )

    @api.model
    def create(self, values):
        if not values.get('code'):
            values['code'] = self.env.ref(
                "somconnexio.sequence_contract"
            ).next_by_id()
        if (
            'service_technology_id' in values
            and
            'service_supplier_id' not in values
        ):
            service_tech_id = values['service_technology_id']
            if (
                service_tech_id == self.env.ref(
                    'somconnexio.service_technology_mobile'
                ).id
            ):
                values['service_supplier_id'] = self.env.ref(
                    'somconnexio.service_supplier_masmovil'
                ).id
            if (
                service_tech_id == self.env.ref(
                    'somconnexio.service_technology_adsl'
                ).id
            ):
                values['service_supplier_id'] = self.env.ref(
                    'somconnexio.service_supplier_jazztel'
                ).id
        res = super(Contract, self).create(values)
        return res

    def write(self, vals):
        if 'active' in vals and self.env.user.login not in ("admin", "__system__"):
            raise UserError(_('You cannot archive contracts'))
        super().write(vals)
        return True

    @api.one
    @api.constrains('partner_id', 'email_ids')
    def _validate_emails(self):
        available_email_ids = self.available_email_ids
        for email_id in self.email_ids:
            if email_id not in available_email_ids:
                raise ValidationError(_('Email(s) not valid'))

    @api.depends('contract_line_ids.date_start')
    def _compute_date_start(self):
        for contract in self:
            contract.date_start = False
            date_start = contract.contract_line_ids.mapped('date_start')
            if date_start and all(date_start):
                contract.date_start = min(date_start)

    # The following two methods are overwritten instead of using super
    # in order to produce a single register note.

    @api.multi
    def _terminate_contract(
        self, terminate_reason_id, terminate_comment,
        terminate_date, terminate_user_reason_id
    ):
        self.ensure_one()
        if not self.env.user.has_group("contract.can_terminate_contract"):
            raise UserError(_('You are not allowed to terminate contracts.'))
        self.contract_line_ids.filtered('is_stop_allowed').stop(terminate_date)
        if not all(self.contract_line_ids.mapped('date_end')):
            raise UserError(_(
                'Please set an end-date to all of its '
                'contract lines manually and try again'
            ))
        self.write({
            'is_terminated': True,
            'terminate_reason_id': terminate_reason_id.id,
            'terminate_user_reason_id': terminate_user_reason_id.id,
            'terminate_comment': terminate_comment,
            'terminate_date': terminate_date,
        })
        return True

    @api.multi
    def action_cancel_contract_termination(self):
        self.ensure_one()
        self.write({
            'is_terminated': False,
            'terminate_reason_id': False,
            'terminate_user_reason_id': False,
            'terminate_comment': False,
            'terminate_date': False,
        })

    @job
    def create_subscription(self, id):
        contract = self.browse(id)
        CRMAccountHierarchyFromContractCreateService(
            contract,
            OpenCellConfiguration(self.env)
        ).run()

    @job
    def terminate_subscription(self, id):
        contract = self.browse(id)
        SubscriptionService(contract).terminate()

    @job
    def update_subscription(self, contracts, updated_field):
        CRMAccountHierarchyFromContractUpdateService(
            contracts, updated_field).run()

    @job
    def add_one_shot(self, id, product_default_code):
        contract = self.browse(id)
        SubscriptionService(contract).create_one_shot(product_default_code)

    @job
    def add_service(self, id, contract_line):
        contract = self.browse(id)
        SubscriptionService(contract).create_service(contract_line)

    @job
    def terminate_service(self, id, contract_line):
        contract = self.browse(id)
        SubscriptionService(contract).terminate_service(
            contract_line.product_id, contract_line.date_end)

    @job
    def create_contract(self, **params):
        service = ContractContractProcess(self.env)
        service.create(**params)
