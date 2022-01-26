from odoo import models, fields, api, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError

from otrs_somconnexio.otrs_models.ticket_factory import TicketFactory
from otrs_somconnexio.services.update_process_ticket_with_coverage_tickets_info_service\
    import UpdateProcessTicketWithCoverageTicketsInfoService

from ..otrs_factories.customer_data_from_res_partner import CustomerDataFromResPartner
from ..otrs_factories.service_data_from_crm_lead_line import ServiceDataFromCRMLeadLine


class CRMLeadLine(models.Model):
    _inherit = 'crm.lead.line'

    broadband_isp_info = fields.Many2one(
        'broadband.isp.info',
        string='Broadband ISP Info'
    )
    mobile_isp_info = fields.Many2one(
        'mobile.isp.info',
        string='Mobile ISP Info'
    )

    is_mobile = fields.Boolean(
        compute='_get_is_mobile',
        store=True
    )
    is_adsl = fields.Boolean(
        compute='_get_is_adsl',
    )
    is_fiber = fields.Boolean(
        compute='_get_is_fiber',
    )
    ticket_number = fields.Char(string='Ticket Number')

    subscription_request_id = fields.Many2one(
        'subscription.request', related='lead_id.subscription_request_id'
    )
    create_date = fields.Datetime('Creation Date')
    mobile_isp_info_type = fields.Selection(related='mobile_isp_info.type')
    mobile_isp_info_icc = fields.Char(related='mobile_isp_info.icc', store=True)
    mobile_isp_info_has_sim = fields.Boolean(
        related='mobile_isp_info.has_sim',
        store=False, readonly=False
    )
    mobile_isp_info_phone_number = fields.Char(
        related='mobile_isp_info.phone_number'
    )
    mobile_isp_info_invoice_street = fields.Char(
        related='mobile_isp_info.invoice_street'
    )
    mobile_isp_info_invoice_street2 = fields.Char(
        related='mobile_isp_info.invoice_street2'
    )
    mobile_isp_info_invoice_zip_code = fields.Char(
        related='mobile_isp_info.invoice_zip_code'
    )
    mobile_isp_info_invoice_city = fields.Char(
        related='mobile_isp_info.invoice_city'
    )
    mobile_isp_info_invoice_state_id = fields.Many2one(
        related='mobile_isp_info.invoice_state_id'
    )
    mobile_isp_info_delivery_street = fields.Char(
        related='mobile_isp_info.delivery_street'
    )
    mobile_isp_info_delivery_street2 = fields.Char(
        related='mobile_isp_info.delivery_street2'
    )
    mobile_isp_info_delivery_zip_code = fields.Char(
        related='mobile_isp_info.delivery_zip_code'
    )
    mobile_isp_info_delivery_city = fields.Char(
        related='mobile_isp_info.delivery_city'
    )
    mobile_isp_info_delivery_state_id = fields.Many2one(
        related='mobile_isp_info.delivery_state_id'
    )
    partner_id = fields.Many2one(related='lead_id.partner_id')
    broadband_isp_info_type = fields.Selection(related='broadband_isp_info.type')
    broadband_isp_info_phone_number = fields.Char(
        related='broadband_isp_info.phone_number'
    )
    broadband_isp_info_service_street = fields.Char(
        related='broadband_isp_info.service_street'
    )
    broadband_isp_info_service_street2 = fields.Char(
        related='broadband_isp_info.service_street2'
    )
    broadband_isp_info_service_zip_code = fields.Char(
        related='broadband_isp_info.service_zip_code'
    )
    broadband_isp_info_service_city = fields.Char(
        related='broadband_isp_info.service_city'
    )
    broadband_isp_info_service_state_id = fields.Many2one(
        'res.country.state', related='broadband_isp_info.service_state_id'
    )
    broadband_isp_info_delivery_street = fields.Char(
        related='broadband_isp_info.delivery_street'
    )
    broadband_isp_info_delivery_street2 = fields.Char(
        related='broadband_isp_info.delivery_street2'
    )
    broadband_isp_info_delivery_city = fields.Char(
        related='broadband_isp_info.delivery_city'
    )
    broadband_isp_info_delivery_state_id = fields.Many2one(
        'res.country.state', related='broadband_isp_info.delivery_state_id'
    )
    broadband_isp_info_invoice_street = fields.Char(
        related='broadband_isp_info.invoice_street'
    )
    broadband_isp_info_invoice_street2 = fields.Char(
        related='broadband_isp_info.invoice_street2'
    )
    broadband_isp_info_invoice_city = fields.Char(
        related='broadband_isp_info.invoice_city'
    )
    broadband_isp_info_invoice_state_id = fields.Many2one(
        'res.country.state', related='broadband_isp_info.invoice_state_id'
    )
    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        related='lead_id.stage_id'
    )
    notes = fields.Text(
        string='Notes',
        related='lead_id.description',
        readonly=False,
    )
    tree_view_notes = fields.Text(
        compute='_trim_notes',
    )
    active = fields.Boolean(
        related='lead_id.active',
    )
    create_user_id = fields.Many2one(
        'res.users', string='Creator',
        default=lambda self: self.env.user,
        index=True)

    @api.depends('product_id')
    def _get_is_mobile(self):
        mobile = self.env.ref('somconnexio.mobile_service')
        for record in self:
            record.is_mobile = (
                mobile.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_adsl(self):
        adsl = self.env.ref('somconnexio.broadband_adsl_service')
        for record in self:
            record.is_adsl = (
                adsl.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_fiber(self):
        fiber = self.env.ref('somconnexio.broadband_fiber_service')
        for record in self:
            record.is_fiber = (
                fiber.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.onchange('mobile_isp_info_icc')
    def _onchange_icc(self):
        self.mobile_isp_info.write({'icc': self.mobile_isp_info_icc})

    @api.depends('notes')
    def _trim_notes(self):
        for record in self:
            if record.notes and len(record.notes) > 50:
                record.tree_view_notes = record.notes[0:50]+"..."
            else:
                record.tree_view_notes = record.notes

    @api.constrains('is_mobile', 'broadband_isp_info', 'mobile_isp_info')
    def _check_isp_info(self):
        for record in self:
            if record.is_mobile:
                if not record.mobile_isp_info:
                    raise ValidationError(
                        _('A mobile lead line needs a Mobile ISP Info '
                          + 'instance related.')
                    )
            else:
                if not record.broadband_isp_info:
                    raise ValidationError(
                        _('A broadband lead line needs a Broadband '
                          + 'ISP Info instance related.')
                    )

    @api.multi
    def action_validate(self):
        for lead_line in self:
            lead_line.lead_id.action_set_won()

    @api.multi
    def action_cancel(self):
        for lead_line in self:
            lead_line.lead_id.action_set_lost()

    @api.multi
    def action_pause(self):
        for lead_line in self:
            lead_line.lead_id.action_set_paused()

    @api.multi
    def action_remesa(self):
        for lead_line in self:
            lead_line.lead_id.action_set_remesa()

    @api.multi
    def action_set_new(self):
        for lead_line in self:
            new_stage_id = self.env.ref('crm.stage_lead1')
            lead_line.lead_id.write({'stage_id': new_stage_id.id})

    @api.multi
    def action_restore(self):
        for lead_line in self:
            lead_line.lead_id.toggle_active()
            new_stage_id = self.env.ref('crm.stage_lead1')
            lead_line.lead_id.write({'stage_id': new_stage_id.id})

    @job
    def create_ticket(self):
        ticket = TicketFactory(
            ServiceDataFromCRMLeadLine(self).build(),
            CustomerDataFromResPartner(self.lead_id.partner_id).build()
        ).build()
        ticket.create()
        self.write({'ticket_number': ticket.number})
        self.with_delay().update_ticket_with_coverage_info(ticket.id)

    @job
    def update_ticket_with_coverage_info(self, ticket_id):
        # Do not add coverage tickets in mobile ones
        if self.is_mobile:
            return

        # Search all the emails of partner
        contract_emails = self.env['res.partner'].search([
            ('parent_id', '=', self.partner_id.id),
            ('type', '=', 'contract-email'),
        ])
        emails = [c.email for c in contract_emails]
        emails.append(self.partner_id.email)

        update_ticket_service = UpdateProcessTicketWithCoverageTicketsInfoService(
            ticket_id
        )
        for email in emails:
            update_ticket_service.run(email)
