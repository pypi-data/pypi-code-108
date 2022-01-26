from odoo import models, fields, api, _


class BaseServiceContractInfo(models.AbstractModel):
    _name = 'base.service.contract.info'
    _rec_name = 'phone_number'
    phone_number = fields.Char("Phone number", required=True)

    @api.multi
    def write(self, values):
        for contract_info in self:
            for key in values:
                message = _("{} changed from {} to {}").format(
                    self._fields[key].string, self[key], values[key]
                )
                contract_info.contract_ids.message_post(message)
        super().write(values)
