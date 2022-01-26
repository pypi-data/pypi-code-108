from odoo import api, fields, models


class ContractContractTerminate(models.TransientModel):

    _inherit = 'contract.contract.terminate'

    terminate_user_reason_id = fields.Many2one(
        comodel_name="contract.terminate.user.reason",
        string="Termination User Reason",
        required=True,
        ondelete="cascade",
    )

    @api.multi
    def terminate_contract(self):
        for wizard in self:
            wizard.contract_id._terminate_contract(
                wizard.terminate_reason_id,
                wizard.terminate_comment,
                wizard.terminate_date,
                wizard.terminate_user_reason_id,
            )
        return True
