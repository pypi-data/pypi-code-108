from odoo import _
from odoo.addons.component.core import Component
from datetime import datetime

# 5 mins in seconds to delay the jobs
ETA = 300


class ContractLineListener(Component):
    _name = 'contract.line.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['contract.line']

    def on_record_create(self, record, fields=None):

        one_shot_products_categ_id_list = [
            self.env.ref('somconnexio.mobile_oneshot_service').id,
            self.env.ref('somconnexio.broadband_oneshot_service').id,
        ]
        service_products_categ_id_list = [
            self.env.ref('somconnexio.mobile_service').id,
            self.env.ref('somconnexio.broadband_fiber_service').id,
            self.env.ref('somconnexio.broadband_adsl_service').id,
            self.env.ref('somconnexio.broadband_4G_service').id,
        ]
        additional_service_products_categ_id_list = [
            self.env.ref('somconnexio.broadband_additional_service').id,
            self.env.ref('somconnexio.mobile_additional_service').id,
        ]

        if record.product_id.categ_id.id in one_shot_products_categ_id_list:
            self.env['contract.contract'].with_delay(
                eta=ETA
            ).add_one_shot(
                record.contract_id.id,
                record.product_id.default_code
            )
        elif record.product_id.categ_id.id in (service_products_categ_id_list + additional_service_products_categ_id_list):  # noqa
            self.env['contract.contract'].with_delay(
                eta=ETA
            ).add_service(
                record.contract_id.id,
                record
            )

        if record.product_id.categ_id.id in additional_service_products_categ_id_list:
            message = _("Added product {} with start date {}").format(
                record.product_id.showed_name,
                record.date_start
            )
            record.contract_id.message_post(body=message)

    def on_record_write(self, record, fields=None):
        additional_service_products_categ_id_list = [
            self.env.ref('somconnexio.broadband_additional_service').id,
            self.env.ref('somconnexio.mobile_additional_service').id,
        ]
        if record.date_end:
            eta = 0
            if record.date_end > datetime.today().date():
                end_datetime = datetime.combine(record.date_end, datetime.min.time())
                eta = end_datetime - datetime.today()
            self.env['contract.contract'].with_delay(
                eta=eta
            ).terminate_service(
                record.contract_id.id,
                record
            )
            if record.product_id.categ_id.id in additional_service_products_categ_id_list:  # noqa
                message = _("Updated product {} with end date {}").format(
                    record.product_id.showed_name,
                    record.date_end
                )
                record.contract_id.message_post(body=message)
