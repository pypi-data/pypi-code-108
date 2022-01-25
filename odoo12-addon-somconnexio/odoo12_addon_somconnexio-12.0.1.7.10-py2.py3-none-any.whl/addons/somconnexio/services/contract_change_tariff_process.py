import logging

from datetime import date
from odoo.exceptions import UserError
from odoo import _
from . import schemas
try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class ContractChangeTariffProcess:
    _description = """
        Run Contract Change Tariff Request Wizard from API
    """

    def __init__(self, env=False):
        self.env = env

    def run_from_api(self, **params):
        _logger.info(
            "Starting process to change a contract's tariff with body: {}".format(
                params)
        )
        v = Validator(purge_unknown=True)
        if not v.validate(params, self.validator_create(),):
            raise UserError(_('BadRequest {}').format(v.errors))
        params = self._prepare_create(params)
        wiz = self.env["contract.tariff.change.wizard"].with_context(
            active_id=params['contract_id']
        ).sudo().create(params)
        wiz.button_change()
        return self.to_dict(wiz)

    def _prepare_create(self, params):
        requested_phone = params.get("phone_number")
        requested_product = params.get("product_code")

        mobile_contract = self.env['contract.contract'].sudo().search([
            ("mobile_contract_service_info_id.phone_number", "=", requested_phone),
            '|',
            ('date_end', '>', date.today().strftime('%Y-%m-%d')),
            ('date_end', '=', False)
        ])

        mobile_templ = self.env["product.template"].sudo().search([
            ("categ_id", '=', self.env.ref('somconnexio.mobile_service').id)
        ])
        mobile_product = self.env["product.product"].sudo().search([
            ("product_tmpl_id", 'in', [tmpl.id for tmpl in mobile_templ]),
            ("default_code", '=', requested_product),
        ])

        if not mobile_contract:
            raise UserError(
                _("Mobile contract not found with phone: {}".format(requested_phone))
            )
        elif not mobile_product:
            raise UserError(
                _("Mobile service product not found with code: {}".format(requested_product))  # noqa
            )

        return {
            "contract_id": mobile_contract.id,
            "start_date": self.get_first_day_of_next_month(date.today()),
            "new_tariff_product_id": mobile_product.id,
            "summary": "{} {}".format("Canvi de tarifa a", mobile_product.showed_name)
        }

    @staticmethod
    def get_first_day_of_next_month(request_date):
        if request_date.month == 12:
            return date(request_date.year+1, 1, 1)
        else:
            return date(request_date.year, request_date.month+1, 1)

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_CHANGE_TARIFF

    @staticmethod
    def to_dict(wiz):
        return {'wiz_id': wiz.id}
