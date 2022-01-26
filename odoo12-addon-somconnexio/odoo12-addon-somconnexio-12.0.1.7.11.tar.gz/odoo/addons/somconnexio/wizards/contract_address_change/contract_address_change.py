from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fibre import MMFibreCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fibre import VdfFibreCoverage
from otrs_somconnexio.otrs_models.coverage.orange_fibre import OrangeFibreCoverage

from odoo import api, fields, models


class ContractAddressChangeWizard(models.TransientModel):
    _name = 'contract.address.change.wizard'

    contract_id = fields.Many2one('contract.contract')
    partner_id = fields.Many2one(
        'res.partner',
        related='contract_id.partner_id'
    )

    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Partner Bank',
        required=True
    )
    service_street = fields.Char(
        string='Service Street',
        required=True
    )
    service_street2 = fields.Char(string='Service Street 2')
    service_zip_code = fields.Char(
        string='Service ZIP',
        required=True
    )
    service_city = fields.Char(
        string='Service City',
        required=True
    )
    service_state_id = fields.Many2one(
        'res.country.state',
        string='Service State',
        required=True
    )
    service_country_id = fields.Many2one(
        'res.country',
        string='Service Country',
        required=True
    )
    previous_tariff_contract_line = fields.Many2one(
        'contract.line',
        related='contract_id.current_tariff_contract_line',
    )
    previous_product_id = fields.Many2one(
        'product.product',
        'Previous Product',
        related='previous_tariff_contract_line.product_id',
    )
    service_supplier_id = fields.Many2one(
        'service.supplier',
        'Service Supplier',
        related='contract_id.service_supplier_id',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Requested product',
        required=True,
    )
    new_product_category_id = fields.Many2one(
        'product.category',
        related='product_id.product_tmpl_id.categ_id',
    )
    mm_fiber_coverage = fields.Selection(
        MMFibreCoverage.VALUES,
        'MM Fiber Coverage',
    )
    vdf_fiber_coverage = fields.Selection(
        VdfFibreCoverage.VALUES,
        'Vdf Fiber Coverage',
    )
    orange_fiber_coverage = fields.Selection(
        OrangeFibreCoverage.VALUES,
        'Orange Fiber Coverage',
    )
    adsl_coverage = fields.Selection(
        ADSLCoverage.VALUES,
        'ADSL Coverage',
    )
    notes = fields.Text(
        string='Notes',
    )
    previous_contract_phone = fields.Char(
        related='contract_id.phone_number',
    )
    previous_contract_address = fields.Char(
        compute='_compute_previous_contract_address',
    )
    previous_contract_pon = fields.Char(
        compute='_compute_previous_contract_pon',
    )
    previous_contract_fiber_speed = fields.Char(
        compute='_compute_previous_contract_fiber_speed',
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['contract_id'] = self.env.context['active_id']
        defaults['service_country_id'] = self.env["res.country"].search([("code", "=", "ES")]).id  # noqa
        return defaults

    def _previous_service(self):
        service_technology = {
            self.env.ref('somconnexio.broadband_adsl_service').id: "adsl",
            self.env.ref('somconnexio.broadband_fiber_service').id: "fiber"
        }
        return service_technology.get(
            self.previous_product_id.product_tmpl_id.categ_id.id
        )

    @api.depends('contract_id')
    def _compute_previous_contract_address(self):
        self.previous_contract_address = "{}, {} - {} ({})".format(
            self.contract_id.service_partner_id.full_street,
            self.contract_id.service_partner_id.city,
            self.contract_id.service_partner_id.zip,
            self.contract_id.service_partner_id.state_id.name
        )

    @api.depends('contract_id')
    def _compute_previous_contract_pon(self):
        if self.contract_id.vodafone_fiber_service_contract_info_id:
            self.previous_contract_pon = self.contract_id.vodafone_fiber_service_contract_info_id.vodafone_id  # noqa
        else:
            self.previous_contract_pon = ""

    @api.depends('contract_id')
    def _compute_previous_contract_fiber_speed(self):
        if (self.contract_id.vodafone_fiber_service_contract_info_id
                or self.contract_id.mm_fiber_service_contract_info_id):
            # All non Greta fiber products have a single attribute value, their velocity
            # (100Mb/600Mb/1Gb)
            self.previous_contract_fiber_speed = self.contract_id.current_tariff_contract_line.product_id.attribute_value_ids[0].name  # noqa
        elif self.contract_id.xoln_fiber_service_contract_info_id:
            # Greta fiber contracts have 600Mb
            self.previous_contract_fiber_speed = "600Mb"
        else:
            self.previous_contract_fiber_speed = ""

    @api.multi
    def button_change(self):
        self.ensure_one()
        broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "service_street": self.service_street,
                "service_street2": self.service_street2,
                "service_zip_code": self.service_zip_code,
                "service_city": self.service_city,
                "service_state_id": self.service_state_id.id,
                "service_country_id": self.service_country_id.id,
                "type": "new",
                "previous_service": self._previous_service(),
                "service_supplier_id": self.service_supplier_id.id,
                "change_address": True,
                "mm_fiber_coverage": self.mm_fiber_coverage or "NoRevisat",
                "vdf_fiber_coverage": self.vdf_fiber_coverage or "NoRevisat",
                "orange_fiber_coverage": self.orange_fiber_coverage or "NoRevisat",
                "adsl_coverage": self.adsl_coverage or "NoServei",
                "previous_owner_vat_number": self.partner_id.vat,
                "previous_owner_first_name": self.partner_id.firstname,
                "previous_owner_name": self.partner_id.lastname,
                "previous_contract_address": self.previous_contract_address,
                "previous_contract_phone": self.previous_contract_phone,
                "previous_contract_pon": self.previous_contract_pon,
                "previous_contract_fiber_speed": self.previous_contract_fiber_speed,
            }
        )
        line_params = {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "category_id": self.product_id.product_tmpl_id.categ_id.id,
            "broadband_isp_info": broadband_isp_info.id,
        }
        crm_lead_line = self.env["crm.lead.line"].create(line_params)

        self.env['crm.lead'].create({
            "name": "Change Address process",
            "description": self.notes,
            "partner_id": self.partner_id.id,
            "iban": self.partner_bank_id.sanitized_acc_number,
            "lead_line_ids": [(6, 0, [crm_lead_line.id])]
        })

        action = self.env.ref("somconnexio.action_crm_lead_line_broadband").read()[0]

        action.update({
            "target": "current",
            "xml_id": "somconnexio.view_form_lead_line_broadband",
            "views": [[
                self.env.ref("somconnexio.view_form_lead_line_broadband").id, "form"
            ]],
            "res_id": crm_lead_line.id,
        })

        return action
