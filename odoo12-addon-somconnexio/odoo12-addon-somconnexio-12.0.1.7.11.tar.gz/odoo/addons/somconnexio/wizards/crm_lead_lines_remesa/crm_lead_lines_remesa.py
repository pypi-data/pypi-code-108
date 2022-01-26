from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CRMLeadLinesRemesaWizard(models.TransientModel):
    _name = 'crm.lead.lines.remesa.wizard'
    crm_lead_line_ids = fields.Many2many('crm.lead.line')
    errors = fields.Char(string="Errors in remesa")

    @api.multi
    def button_remesa(self):
        for line in self.crm_lead_line_ids:
            line.lead_id.skip_duplicated_phone_validation = True
            line.action_remesa()
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        crm_lead_line_ids = self.env.context['active_ids']
        defaults['crm_lead_line_ids'] = crm_lead_line_ids
        errors = self._validate_crm_lines()
        if errors:
            defaults['errors'] = _("The next CRMLeadLines have a phone number that already exists in another contract/CRMLead: {}").format(  # noqa
                " ".join(
                    [str(id) for id in errors]
                ).strip()
            )
        return defaults

    def _validate_crm_lines(self):
        errors = []
        crm_lead_lines = self.env["crm.lead.line"].browse(
            self.env.context['active_ids']
        )
        for line in crm_lead_lines:
            if len(line.lead_id.lead_line_ids) > 1:
                raise ValidationError(_(
                    "The CRMLead to validate has more than one CRMLeadLine associated."
                    " This shouldn't happen. Please contact the IP team."
                ))
            else:
                try:
                    line.lead_id.validate_remesa()
                except ValidationError as error:
                    if _("Contract or validated CRMLead with the same phone already exists.") in error.name:  # noqa
                        errors.append(line.id)
                    else:
                        raise error
        if errors:
            return errors
