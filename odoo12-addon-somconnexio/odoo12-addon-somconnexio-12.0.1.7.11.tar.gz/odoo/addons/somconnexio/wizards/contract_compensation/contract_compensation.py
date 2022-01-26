from odoo import api, fields, models, _
from odoo.tools.misc import clean_context
from ...opencell_services.subscription_service import SubscriptionService
from odoo.exceptions import ValidationError


class CustomPopMessage(models.TransientModel):
    _name = "custom.pop.message"
    name = fields.Char('Message')


class ContractCompensationWizard(models.TransientModel):
    _name = 'contract.compensation.wizard'
    partner_id = fields.Many2one('res.partner')
    contract_ids = fields.Many2many('contract.contract')
    type = fields.Selection([
        ('days_without_service', 'Days without Service'),
        ('exact_amount', 'Exact Amount'),
    ], 'Compensation Type')
    product_id = fields.Many2one(
        'product.product', 'Product', related='contract_ids.tariff_product'
    )
    days_without_service = fields.Integer('Days without Service')
    exact_amount = fields.Float('Exact Amount')
    is_opencell_compensation = fields.Boolean(
        'Compensation to Open Cell?', compute='_is_opencell_compensation'
    )
    state = fields.Selection([
        ('details', 'details'),
        ('load', 'load'),
    ], default='load')

    days_without_service_import = fields.Float('Compensation amount')
    operation_date = fields.Date('Compensation date')
    description = fields.Char('Description')

    @api.depends('contract_ids')
    def _is_opencell_compensation(self):
        self.is_opencell_compensation = not self.contract_ids.is_terminated

    @api.multi
    def opencell_compensate(self):
        compensation_code = 'CH_SC_OSO_COMPENSATION'
        amount_without_taxes = round(self.days_without_service_import, 4)
        SubscriptionService(self.contract_ids).create_one_shot(
            compensation_code, -amount_without_taxes,
            description=self.description,
            operation_date=self.operation_date
        )
        message = _(
            'A compensation line has been created in Open Cell with {} €'
        ).format(amount_without_taxes)
        return {
            'name': 'Message',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.pop.message',
            'target': 'new',
            'context': {'default_name': message}
        }

    @api.multi
    def button_compensate(self):
        if self.type == 'days_without_service':
            if self.days_without_service <= 0.0:
                raise ValidationError(
                    _('The amount of days without service must be greater than zero')
                )
            tariff_product = self.product_id
            pricelist = self.env['product.pricelist'].search([
                ('code', '=', '0IVA')
            ])
            amount = (
                tariff_product.with_context(pricelist=pricelist.id).price
                / 30.0 * self.days_without_service
            )
            if self.is_opencell_compensation:
                self.state = 'details'
                self.days_without_service_import = amount
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'contract.compensation.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.id,
                    'views': [(False, 'form')],
                    'target': 'new',
                }
        else:
            amount = self.exact_amount
            if amount <= 0.0:
                raise ValidationError(_('The amount must be greater than zero €'))
        summary = _("The amount to compensate is %.2f €") % amount
        ctx = dict(
            clean_context(self.env.context),
            default_activity_type_id=self.env.ref(
                'somconnexio.mail_activity_type_sc_compensation'
            ).id,
            default_res_id=self.contract_ids.id,
            default_res_model_id=self.env.ref('contract.model_contract_contract').id,
            default_summary=summary,
            default_confirmation=True
        )
        return {
            'name': _('Schedule an Activity'),
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['partner_id'] = self.env.context['active_id']
        return defaults

    @api.onchange('contract_ids')
    @api.multi
    def onchange_contract_ids(self):
        if len(self.contract_ids) > 1:
            self.contract_ids = self.contract_ids[0]
            return {
                'warning': {
                    'title': _('Error'),
                    'message': _(
                        'You can only compensate one contract at the same time'
                    ),
                },
            }
