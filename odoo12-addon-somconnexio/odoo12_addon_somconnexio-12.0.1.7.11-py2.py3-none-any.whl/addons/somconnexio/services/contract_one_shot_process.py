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


class ContractOneShotProcess:
    _description = """
        Run Contract One Shot Request Wizard from API
    """

    def __init__(self, env=False):
        self.env = env

    def run_from_api(self, **params):
        _logger.info(
            "Starting proces to add one shot bond with body: {}".format(params)
        )
        v = Validator(purge_unknown=True)
        if not v.validate(params, self.validator_create(),):
            raise UserError(_('BadRequest {}').format(v.errors))
        params = self._prepare_create(params)
        wiz = self.env["contract.one.shot.request.wizard"].with_context(
            active_id=params['contract_id']
        ).sudo().create(params)
        wiz.button_add()
        return self.to_dict(wiz)

    def _prepare_create(self, params):
        requested_phone = params.get("phone_number")
        requested_product = params.get("product_code")

        mobile_contract = self.env['contract.contract'].sudo().search([
            ("is_terminated", "=", False),
            ("mobile_contract_service_info_id.phone_number", "=", requested_phone),
        ])

        mobile_one_shot_templ = self.env["product.template"].sudo().search([
            ("categ_id", '=', self.env.ref('somconnexio.mobile_oneshot_service').id)
        ])
        mobile_one_shot_product = self.env["product.product"].sudo().search([
            ("product_tmpl_id", 'in', [tmpl.id for tmpl in mobile_one_shot_templ]),
            ("default_code", '=', requested_product),
        ])

        if not mobile_contract:
            raise UserError(
                _("Mobile contract not found with phone: {}".format(requested_phone))
            )
        elif not mobile_one_shot_product:
            raise UserError(
                _("Mobile additional bond product not found with code: {}".format(requested_product))  # noqa
            )

        return {
            "contract_id": mobile_contract.id,
            "start_date": date.today(),
            "one_shot_product_id": mobile_one_shot_product.id,
            "summary": "{} {}".format("Abonament addicional de",
                                      mobile_one_shot_product.showed_name)
        }

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_ONE_SHOT_ADDITION

    @staticmethod
    def to_dict(wiz):
        return {'wiz_id': wiz.id}
