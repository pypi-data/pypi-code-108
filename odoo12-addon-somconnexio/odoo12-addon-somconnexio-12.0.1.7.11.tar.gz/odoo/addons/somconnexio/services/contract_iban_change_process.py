import logging

from datetime import date
from odoo.exceptions import UserError, ValidationError
from odoo import _
from . import schemas
from odoo.addons.base_iban.models.res_partner_bank import validate_iban
try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class ContractIbanChangeProcess:
    _description = """
        Run Contract Iban Change Wizard from API
    """

    def __init__(self, env=False):
        self.env = env

    def run_from_api(self, **params):
        _logger.info(
            "Starting proces to change contract IBAN with body: {}".format(params)
        )
        v = Validator(purge_unknown=True)
        if not v.validate(params, self.validator_create(),):
            raise UserError(_('BadRequest {}').format(v.errors))
        params = self._prepare_create(params)
        wiz = self.env["contract.iban.change.wizard"].with_context(
            active_id=params['partner_id']
        ).sudo().create(params)
        wiz.button_change()
        return self.to_dict(wiz)

    def _prepare_create(self, params):
        partner_id = self.env['res.partner'].sudo().search(
            [
                ("ref", "=", params['partner_id']),
            ]
        ).id
        if not partner_id:
            raise UserError(
                _('Partner id %s not found') % (params['partner_id'],)
            )
        sanitized_iban = params['iban'].replace(' ', '').upper()
        mandate_id = self._get_mandate(partner_id, sanitized_iban).id
        contract_ids = self._prepare_contract_ids(params, partner_id)
        return {
            'partner_id': partner_id,
            'account_banking_mandate_id': mandate_id,
            'contract_ids': contract_ids
        }

    def _get_mandate(self, partner_id, sanitized_iban):
        mandate = self.env.get('account.banking.mandate').sudo().search(
            [
                ("state", "=", "valid"),
                ("partner_id", "=", partner_id),
                ("partner_bank_id.sanitized_acc_number", "=", sanitized_iban),
            ]
        )
        if mandate:
            return mandate[0]
        else:
            bank_id = self.env['res.partner.bank'].sudo().search(
                [
                    ('acc_number', '=', sanitized_iban),
                    ('partner_id', '=', partner_id)
                ]
            )
            if not bank_id:
                try:
                    validate_iban(sanitized_iban)
                except ValidationError:
                    raise UserError("IBAN {} is incorrect".format(sanitized_iban))
                self.env['res.partner.bank'].sudo().create({
                    'acc_type': 'iban',
                    'acc_number': sanitized_iban,
                    'partner_id': partner_id
                })
            mandate = self.env['account.banking.mandate'].sudo().search([
                ("state", "=", "valid"),
                ("partner_id", "=", partner_id),
                ("partner_bank_id.sanitized_acc_number", "=", sanitized_iban),
            ])
            if mandate:
                return mandate[0]
            raise UserError(
                _('Partner id %s with mandate with acc %s cannot be created') % (
                    partner_id, sanitized_iban
                )
            )

    def _prepare_contract_ids(self, params, partner_id):
        contracts = params.get('contracts')
        if contracts:
            contract_ids = []
            for contract_ref in contracts.split(";"):
                contract_id = self.env['contract.contract'].sudo().search([
                    ('partner_id', '=', partner_id),
                    ('code', '=', contract_ref)
                ]).id
                if not contract_id:
                    raise UserError(
                        _('Contract %s not found for partner %s') % (
                            contract_ref, partner_id
                        )
                    )
                contract_ids.append(contract_id)
        else:
            contract_ids = self.env['contract.contract'].sudo().search([
                ('partner_id', '=', partner_id),
                '|',
                ('date_end', '>', date.today().strftime('%Y-%m-%d')),
                ('date_end', '=', False)
            ]).ids
        return [(6, 0, contract_ids)]

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_IBAN_CHANGE_CREATE

    @staticmethod
    def to_dict(wiz):
        return {'wiz_id': wiz.id}
