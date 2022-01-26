from odoo.addons.component.core import Component


class CrmLeadListener(Component):
    _name = 'crm.lead.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['crm.lead']

    def on_record_write(self, record, fields=None):
        if "stage_id" in fields and \
                record.stage_id.id == self.env.ref('crm.stage_lead4').id:
            for line in record.lead_line_ids:
                line.with_delay().create_ticket()
