from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MailActivity(models.Model):
    _inherit = ['mail.thread', 'mail.activity']
    _name = 'mail.activity'
    reference = fields.Char(
        string='Reference',
        compute='_compute_reference',
        readonly=True,
        store=False
    )
    activity_type_name = fields.Char(
        related="activity_type_id.name"
    )
    date_done = fields.Date(readonly=False)
    location = fields.Char()
    partner_id = fields.Many2one(
        'res.partner',
        compute='_compute_res_partner', readonly=True, store=True)
    confirmation = fields.Boolean(default=False)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get('res_model') == 'res.partner':
            partner = self.env['res.partner'].browse(res.get('res_id'))
            if partner.parent_id:
                raise UserError(_("It is not possible to create an activity from a child partner. Do it through its parent instead"))  # noqa
        return res

    @api.depends('res_model', 'res_id')
    def _compute_reference(self):
        for res in self:
            res.reference = "%s,%s" % (res.res_model, res.res_id)

    @api.depends('res_model', 'res_id')
    def _compute_res_partner(self):
        for res in self:
            if res.res_model == 'contract.contract':
                contract = self.env['contract.contract'].browse(res.res_id)
                res.partner_id = contract.partner_id
            elif res.res_model == 'res.partner':
                res.partner_id = self.env['res.partner'].browse(res.res_id)
            elif res.res_model == 'account.invoice':
                invoice = self.env['account.invoice'].browse(res.res_id)
                res.partner_id = invoice.partner_id
            else:
                res.partner_id = False

    def action_reopen(self):
        self.ensure_one()
        self.date_done = False
        self.done = False

        message = _("Activity '{}' reopened on date {}")
        record = self.env[self.res_model].browse(self.res_id)
        record.message_post(
            message.format(
                self.summary,
                date.today().strftime("%d-%m-%Y")
            )
        )
        message = _("Activity reopened on date {}")
        self.message_post(
            message.format(
                date.today().strftime("%d-%m-%Y")
            )
        )

    @api.multi
    def action_done(self):
        ret = super().action_done()
        if ret:
            message = _("Activity set as done on date {}")
            self.message_post(
                message.format(
                    date.today().strftime("%d-%m-%Y")
                )
            )
        return ret

    @api.multi
    def write(self, values):
        ret = super().write(values)
        if values.get('date_done'):
            for act in self:
                if act.date_done != date.today():
                    message = _("Activity's done date set to {} on date {}")
                    act.message_post(
                        message.format(
                            act.date_done.strftime("%d-%m-%Y"),
                            date.today().strftime("%d-%m-%Y")
                        )
                    )
        return ret

    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        summary = self.summary
        super()._onchange_activity_type_id()
        if self.activity_type_id == self.env.ref(
            'somconnexio.mail_activity_type_sc_compensation'
        ):
            self.summary = summary
