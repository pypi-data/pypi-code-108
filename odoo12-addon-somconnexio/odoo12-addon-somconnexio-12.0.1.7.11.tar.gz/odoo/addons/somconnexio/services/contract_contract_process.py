import logging

from odoo import _

from . import schemas
from odoo.exceptions import UserError
try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class ContractContractProcess:
    _description = """
        Contract creation
    """

    def __init__(self, env=False):
        self.env = env

    @staticmethod
    def validate_service_technology_deps(params):
        errors = []
        if params['service_technology'] == 'Mobile':
            if params['service_supplier'] != 'MásMóvil':
                errors.append('Mobile needs MásMóvil supplier')
            if 'mobile_contract_service_info' not in params:
                errors.append('Mobile needs mobile_contract_service_info')
        elif params['service_technology'] == 'Fiber':
            if 'service_address' not in params:
                errors.append('Fiber needs "service_address"')
            if params['service_supplier'] not in (
                    'Vodafone', 'Orange', 'MásMóvil', 'XOLN'
            ):
                errors.append(
                    'Fiber needs "Vodafone", "Orange", "MásMóvil" or "XOLN" suppliers')
            else:
                if params['service_supplier'] == 'Vodafone':
                    if 'vodafone_fiber_contract_service_info' not in params:
                        errors.append(
                            'Vodafone Fiber needs vodafone_fiber_contract_service_info'
                        )
                    if params.get('fiber_signal_type') == 'fibraIndirecta':
                        errors.append(
                            'Fiber signal "Fibra Indirecta" needs MásMóvil supplier'
                        )
                elif params['service_supplier'] == 'MásMóvil':
                    if 'mm_fiber_contract_service_info' not in params:
                        errors.append(
                            'MásMóvil Fiber needs mm_fiber_contract_service_info'
                        )
                    if params.get('fiber_signal_type') in ('fibraCoaxial', 'NEBAFTTH'):
                        errors.append(
                            'Fiber signal "{}" needs Vodafone supplier'.format(
                                params['fiber_signal_type'])
                        )
                elif params['service_supplier'] == 'XOLN':
                    if 'xoln_fiber_contract_service_info' not in params:
                        errors.append(
                            'XOLN Fiber needs mm_fiber_contract_service_info'
                        )
                elif params['service_supplier'] == 'Orange':
                    if 'orange_fiber_contract_service_info' not in params:
                        errors.append(
                            'Orange Fiber needs orange_fiber_contract_service_info'
                        )
        elif params['service_technology'] == 'ADSL':
            if params['service_supplier'] != 'Jazztel':
                errors.append('ADSL needs Jazztel supplier')
            if 'service_address' not in params:
                errors.append('ADSL needs "service_address"')
            if 'adsl_contract_service_info' not in params:
                errors.append('ADSL needs adsl_contract_service_info')
        if errors:
            raise UserError("\n".join(errors))

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_CREATE

    def create(self, **params):
        _logger.info("Create contract received with body: {}".format(params))
        v = Validator(purge_unknown=True)
        if not v.validate(params, self.validator_create(),):
            raise UserError(_('BadRequest {}').format(v.errors))
        self.validate_service_technology_deps(params)
        params = self._prepare_create(params)
        cc = self.env["contract.contract"].sudo().create(params)
        return self._to_dict(cc)

    @staticmethod
    def _to_dict(contract):
        return {
            "id": contract.id
        }

    def _prepare_create_line(self, line):
        product = self.env["product.product"].sudo().search(
            [('default_code', '=', line['product_code'])]
        )
        if not product:
            raise UserError(
                _('Product with code %s not found') % (
                    line['product_code'],
                )
            )
        response_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": line['date_start']
        }
        return response_line

    def _check_service_combination(self, technology_id, supplier_id):
        if not self.env['service.technology.service.supplier'].sudo().search(
            [
                ('service_technology_id', '=', technology_id),
                ('service_supplier_id', '=', supplier_id)
            ]
        ):
            return False
        else:
            return True

    def _create_mobile_contract_service_info(self, params):
        if not params:
            return False
        return self.env['mobile.service.contract.info'].sudo().create({
            'phone_number': params['phone_number'],
            'icc': params['icc']
        })

    def _create_adsl_contract_service_info(self, params):
        if not params:
            return False
        router_product = self._get_router_product_id(params['router_product_id'])
        if 'router_mac_address' in params and params['router_mac_address'] != '-':
            router_mac_address = params['router_mac_address']
        else:
            router_mac_address = False
        router_lot_id = self._create_router_lot_id(
            params['router_serial_number'],
            router_mac_address,
            router_product,
        )
        return self.env['adsl.service.contract.info'].sudo().create({
            'phone_number': params['phone_number'],
            'administrative_number': params['administrative_number'],
            'router_product_id': router_product.id,
            'router_mac_address': router_mac_address,
            'ppp_user': params['ppp_user'],
            'ppp_password': params['ppp_password'],
            'endpoint_user': params['endpoint_user'],
            'endpoint_password': params['endpoint_password'],
            'router_lot_id': router_lot_id.id,
        })

    def _create_router_4G_contract_service_info(self, params):
        if not params:
            return False
        return self.env['router.4g.service.contract.info'].sudo().create({
            'phone_number': params['phone_number'],
            'vodafone_id': params['vodafone_id'],
            'vodafone_offer_code': params['vodafone_offer_code']
        })

    def _create_vodafone_fiber_contract_service_info(self, params):
        if not params:
            return False
        return self.env['vodafone.fiber.service.contract.info'].sudo().create({
            'phone_number': params['phone_number'],
            'vodafone_id': params['vodafone_id'],
            'vodafone_offer_code': params['vodafone_offer_code']
        })

    def _create_mm_fiber_contract_service_info(self, params):
        if not params:
            return False
        return self.env['mm.fiber.service.contract.info'].sudo().create({
            'phone_number': params['phone_number'],
            'mm_id': params['mm_id'],
        })

    def _create_orange_fiber_contract_service_info(self, params):
        if not params:
            return False
        return self.env['orange.fiber.service.contract.info'].sudo().create({
            'suma_id': params['suma_id'],
        })

    def _create_xoln_fiber_contract_service_info(self, params):
        if not params:
            return False
        if 'router_mac_address' in params and params['router_mac_address'] != '-':
            router_mac_address = params['router_mac_address']
        else:
            router_mac_address = False
        router_product = self._get_router_product_id(params['router_product_id'])
        router_lot_id = self._create_router_lot_id(
            params['router_serial_number'],
            router_mac_address,
            router_product,
        )
        project_options = dict(
            self.env['xoln.fiber.service.contract.info']._fields['project'].selection
        ).keys()
        if params['project'] not in project_options:
            raise UserError(
                'Project %s not found' % (
                    params['project'],
                )
            )
        return self.env['xoln.fiber.service.contract.info'].sudo().create({
            'phone_number': params['phone_number'],
            'external_id': params['external_id'],
            'id_order': params['id_order'],
            'project': params['project'],
            'router_product_id': router_product.id,
            'router_lot_id': router_lot_id.id,
        })

    def _prepare_service_partner_id(self, partner_id, service_address):
        service_address_obj = self.env['res.partner'].sudo().search([
            ('parent_id', '=', partner_id),
            ('street', '=', service_address['street']),
            ('zip', '=', service_address['zip_code']),
            ('city', '=', service_address['city']),
            ('state_id.code', '=', service_address['state']),
            ('type', '=', 'service'),
        ])
        if not service_address_obj:
            state = self.env['res.country.state'].sudo().search([
                ('country_id', '=', self.env.ref('base.es').id),
                ('code', '=', service_address['state'])
            ])
            service_address_obj = self.env['res.partner'].sudo().create({
                'parent_id': partner_id,
                'street': service_address['street'],
                'zip':  service_address['zip_code'],
                'city': service_address['city'],
                'state_id': state.id,
                'type': 'service',
            })
        return service_address_obj.id

    def _prepare_create(self, params):
        if 'code' in params:
            code = params['code']
        else:
            code = None
        partner_id = self.env['res.partner'].sudo().search(
            [
                ("ref", "=", params['partner_id']),
            ]
        ).id

        if not self.env['res.partner'].sudo().browse(partner_id):
            raise UserError(
                _('Partner id %s not found') % (partner_id, )
            )
        email_id = self._get_or_create_contract_email(partner_id, params['email'])

        contract_lines = []
        if params.get('contract_line'):
            contract_lines.append(
                self._prepare_create_line(params['contract_line'])
            )
        else:
            contract_lines.extend(
                self._prepare_create_line(line)
                for line in params['contract_lines']
            )
        mobile_contract_service_info = self._create_mobile_contract_service_info(
            params.get('mobile_contract_service_info')
        )
        adsl_contract_service_info = (
            self._create_adsl_contract_service_info(
                params.get('adsl_contract_service_info')
            )
        )
        vodafone_fiber_contract_service_info = (
            self._create_vodafone_fiber_contract_service_info(
                params.get('vodafone_fiber_contract_service_info')
            )
        )
        router_4G_contract_service_info = (
            self._create_router_4G_contract_service_info(
                params.get('router_4G_contract_service_info')
            )
        )
        mm_fiber_contract_service_info = (
            self._create_mm_fiber_contract_service_info(
                params.get('mm_fiber_contract_service_info')
            )
        )
        xoln_fiber_contract_service_info = (
            self._create_xoln_fiber_contract_service_info(
                params.get('xoln_fiber_contract_service_info')
            )
        )
        orange_fiber_contract_service_info = (
            self._create_orange_fiber_contract_service_info(
                params.get('orange_fiber_contract_service_info')
            )
        )
        if mobile_contract_service_info:
            name = mobile_contract_service_info.phone_number
        elif adsl_contract_service_info:
            name = adsl_contract_service_info.phone_number
        elif vodafone_fiber_contract_service_info:
            name = vodafone_fiber_contract_service_info.phone_number
        elif router_4G_contract_service_info:
            name = router_4G_contract_service_info.phone_number
        elif mm_fiber_contract_service_info:
            name = mm_fiber_contract_service_info.phone_number
        elif xoln_fiber_contract_service_info:
            name = xoln_fiber_contract_service_info.phone_number
        elif orange_fiber_contract_service_info:
            name = orange_fiber_contract_service_info.phone_number
        if 'service_partner_id' in params:
            service_partner_id = params['service_partner_id']
        elif 'service_address' in params:
            service_partner_id = self._prepare_service_partner_id(
                partner_id, params['service_address'])
        else:
            service_partner_id = False

        fiber_signal_type_id = ""
        if params.get('fiber_signal_type'):
            fiber_signal_type_id = self.env['fiber.signal.type'].sudo().search([
                ('code', '=', params['fiber_signal_type']),
            ]).id

        sanitized_iban = params['iban'].replace(' ', '').upper()
        mandate = self._get_mandate(partner_id, sanitized_iban)
        if self.env['contract.contract'].sudo().search([
            ('ticket_number', '=', params['ticket_number']),
        ]):
            raise UserError(
                _('Duplicated Ticket Number #{}').format(params['ticket_number'])
            )
        response = {
            'name': name,
            'partner_id': partner_id,
            'email_ids': [(4, email_id, False)],
            'service_partner_id': service_partner_id,
            'mobile_contract_service_info_id': (
                mobile_contract_service_info and mobile_contract_service_info.id
            ),
            'adsl_service_contract_info_id': (
                adsl_contract_service_info and
                adsl_contract_service_info.id
            ),
            'vodafone_fiber_service_contract_info_id': (
                vodafone_fiber_contract_service_info and
                vodafone_fiber_contract_service_info.id
            ),
            'mm_fiber_service_contract_info_id': (
                mm_fiber_contract_service_info and
                mm_fiber_contract_service_info.id
            ),
            'xoln_fiber_service_contract_info_id': (
                xoln_fiber_contract_service_info and
                xoln_fiber_contract_service_info.id
            ),
            'orange_fiber_service_contract_info_id': (
                orange_fiber_contract_service_info and
                orange_fiber_contract_service_info.id
            ),
            'router_4G_service_contract_info_id': (
                router_4G_contract_service_info and
                router_4G_contract_service_info.id
            ),
            'invoice_partner_id': partner_id,
            'service_technology_id': self._get_service_tech(
                params['service_technology']
            ).id,
            'service_supplier_id': self._get_service_supplier(
                params['service_supplier']
            ).id,
            'fiber_signal_type_id': fiber_signal_type_id,
            'payment_mode_id': self.env.ref('somconnexio.payment_mode_inbound_sepa').id,
            'mandate_id': mandate.id,
            'ticket_number': params['ticket_number']
        }
        if code:
            response['code'] = code
        if not self._check_service_combination(
            response['service_technology_id'],
            response['service_supplier_id']
        ):
            raise UserError(
                _('Bad combination {} and {}').format(
                    params['service_technology'],
                    params['service_supplier']
                )
            )

        if contract_lines:
            response.update({
                'contract_line_ids': [
                    (0, False, contract_line)
                    for contract_line in contract_lines
                ],
            })
        return response

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
            raise UserError(
                _('Partner id %s without mandate with acc %s') % (
                    partner_id, sanitized_iban
                )
            )

    def _get_service_tech(self, name):
        service_tech = self.env['service.technology'].sudo().search(
            [('name', '=', name)]
        )
        if service_tech:
            return service_tech
        else:
            raise UserError(
                _('No service technology for name %s') % name
            )

    def _get_service_supplier(self, name):
        service_supplier = self.env['service.supplier'].sudo().search(
            [('name', '=', name)]
        )
        if service_supplier:
            return service_supplier
        else:
            raise UserError(_('No service supplier for name %s') % name)

    def _get_router_product_id(self, router_code):
        router_product = self.env['product.product'].sudo().search(
            [
                ('default_code', '=', router_code),
            ]
        )
        if router_product:
            return router_product
        else:
            raise UserError('No router product with code %s' % router_code)

    def _create_router_lot_id(self, serial_number, mac_address, product):
        return self.env['stock.production.lot'].sudo().create({
            'product_id': product.id,
            'router_mac_address': mac_address,
            'name': serial_number,
        })

    def _get_or_create_contract_email(self, partner_id, email):

        if not email:
            # If no email is given, take partner's contact email by default
            return partner_id

        email_partner_id = self.env['res.partner'].sudo().search([
            ("email", "=", email),
            '|',
            ("id", "=", partner_id),
            "&",
            ("parent_id", "=", partner_id),
            ("type", "=", "contract-email"),
        ], limit=1)

        if email_partner_id:
            return email_partner_id.id

        # If we can't find the email in the partner or its child contacts, create it
        # as a child partner with type 'contract-email'.
        new_email_partner_id = self.env['res.partner'].sudo().create({
            'name': self.env['res.partner'].sudo().browse(partner_id).name,
            'email': email,
            'parent_id': partner_id,
            'type': 'contract-email'
        })
        return new_email_partner_id.id
