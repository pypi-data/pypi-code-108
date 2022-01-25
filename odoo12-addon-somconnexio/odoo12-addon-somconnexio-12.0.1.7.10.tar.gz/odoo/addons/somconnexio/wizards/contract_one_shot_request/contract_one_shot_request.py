from datetime import datetime, date
from calendar import monthrange

from odoo import models, fields, api, _
from odoo.addons.queue_job.job import job
from ...services.contract_one_shot_process import ContractOneShotProcess


class ContractOneShotRequestWizard(models.TransientModel):
    _name = 'contract.one.shot.request.wizard'
    contract_id = fields.Many2one('contract.contract')
    summary = fields.Char(required=True)
    done = fields.Boolean(required=True)
    location = fields.Char()
    note = fields.Char()

    product_category_id = fields.Many2one(
        'product.category',
        compute="_load_product_category_id"
    )
    start_date = fields.Date('Start Date', required=True)
    one_shot_product_id = fields.Many2one(
        'product.product',
        string='One Shot products',
    )
    activity_type = fields.Many2one('mail.activity.type')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['contract_id'] = self.env.context['active_id']
        defaults['start_date'] = datetime.strftime(date.today(), "%Y-%m-%d")
        return defaults

    @api.depends("contract_id")
    def _load_product_category_id(self):
        if not self.contract_id:
            return False

        if self.contract_id.service_technology_id.id == self.env.ref(
                'somconnexio.service_technology_mobile').id:
            self.product_category_id = self.env.ref(
                'somconnexio.mobile_oneshot_service').id
        else:
            self.product_category_id = self.env.ref(
                'somconnexio.broadband_oneshot_service').id

    @api.onchange("one_shot_product_id")
    def onchange_one_shot_product_id(self):
        router_list = [
            self.env.ref('somconnexio.EnviamentRouter_product_template'),
            self.env.ref('somconnexio.RecollidaRouter_product_template')
        ]

        if self.one_shot_product_id.product_tmpl_id == self.env.ref(
            'somconnexio.DadesAddicionals500MB_product_template'
        ):
            self.summary = _(self.one_shot_product_id.showed_name)
            self.done = True
            self.activity_type = self.env.ref('somconnexio.mail_activity_type_one_shot')
        elif self.one_shot_product_id.product_tmpl_id == self.env.ref(
            'somconnexio.SMSMassius500SMS_product_template'
        ):
            self.summary = ""
            self.done = True
            self.activity_type = self.env.ref('somconnexio.mail_activity_type_one_shot')
        elif self.one_shot_product_id.product_tmpl_id in router_list:
            self.summary = ""
            self.done = True
            self.activity_type = self.env.ref('somconnexio.mail_activity_type_router_send_or_return')  # noqa
        else:
            self.summary = ""
            self.done = False
            self.activity_type = self.env.ref('somconnexio.mail_activity_type_sim_change')  # noqa

    def button_add(self):
        self.ensure_one()

        one_shot_contract_line = {
            "name": self.one_shot_product_id.name,
            "product_id": self.one_shot_product_id.id,
            "date_start": self.start_date,
            "date_end": self._get_last_day_of_month(self.start_date)
        }

        self.contract_id.write(
            {'contract_line_ids': [(0, 0, one_shot_contract_line)]}
        )

        message = _("One shot product '{}' added on '{}'")
        self.contract_id.message_post(
            message.format(
                self.one_shot_product_id.showed_name,
                self.start_date,
            )
        )

        self._create_activity()
        return True

    def _get_last_day_of_month(self, request_date):
        #  Touple with weekday (0-6) and number of days (28-31) for a given month
        month_range = monthrange(request_date.year, request_date.month)

        return date(request_date.year, request_date.month, month_range[1])

    def _create_activity(self):
        self.env['mail.activity'].create({
            'summary': self.summary,
            'res_id': self.contract_id.id,
            'res_model_id': self.env.ref('contract.model_contract_contract').id,
            'user_id': self.env.user.id,
            'activity_type_id': self.activity_type.id,
            'done': self.done,
            'date_done': date.today(),
            'date_deadline': date.today(),
            'location': self.location,
            'note': self.note,
        })

    @job
    def run_from_api(self, **params):
        service = ContractOneShotProcess(self.env)
        service.run_from_api(**params)
