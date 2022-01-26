from odoo.addons.component.core import Component


class Partner(Component):
    _name = 'partner.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['res.partner']

    def on_record_create(self, record, fields=None):
        # Early return if is not a Contact(is the parent)
        if record.parent_id:
            return
        if record.customer and record.cooperator:
            self.env['res.partner'].with_delay().create_user(record)

    def on_record_write(self, record, fields=None):
        address_fields = ['street',  'street2', 'zip', 'city', 'state_id', 'country_id']
        is_address_edited = any(True for field in fields if field in address_fields)
        if is_address_edited and record.contract_ids:
            record.with_delay().update_accounts_address()
            record.with_delay().update_customer()
