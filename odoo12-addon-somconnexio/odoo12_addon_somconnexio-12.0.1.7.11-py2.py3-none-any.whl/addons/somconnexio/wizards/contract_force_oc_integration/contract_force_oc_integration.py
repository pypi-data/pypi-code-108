from odoo import models

# 5 mins in seconds to delay the job
ETA = 300


class ContractForceOCIntegration(models.TransientModel):
    _name = 'contract.force.oc.integration.wizard'

    def create_subscription(self):
        contract = self.env['contract.contract'].browse(self.env.context['active_id'])

        contract.with_delay(priority=0).create_subscription(
            contract.id
        )
