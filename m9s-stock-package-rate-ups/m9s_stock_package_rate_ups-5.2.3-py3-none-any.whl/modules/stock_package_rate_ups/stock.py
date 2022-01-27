# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import ssl

from itertools import zip_longest

import requests

from trytond.config import config
from trytond.i18n import gettext
from trytond.model.exceptions import AccessError
from trytond.modules.stock_package_shipping_ups.exceptions import UPSError
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.wizard import StateAction, StateTransition, Wizard

from .exceptions import UPSResult

SERVER_URLS = {
    #'testing': 'https://wwwcie.ups.com/rest/Rate',
    'testing': 'https://wwwcie.ups.com/json/Rate',
    'production': 'https://onlinetools.ups.com/json/Rate',
    }


class GetRate(metaclass=PoolMeta):
    __name__ = 'stock.shipment.get_rate'

    ups = StateAction(
        'stock_package_rate_ups.act_get_rate_ups_wizard')

    def transition_start(self):
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')

        shipment = ShipmentOut(Transaction().context['active_id'])
        next_state = super().transition_start()
        if shipment.carrier.shipping_service == 'ups':
            next_state = 'ups'
        return next_state

    def do_ups(self, action):
        ctx = Transaction().context
        return action, {
            'model': ctx['active_model'],
            'id': ctx['active_id'],
            'ids': [ctx['active_id']],
            }


class RateUPSMixin:

    start = StateTransition()

    def transition_start(self):
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')
        Carrier = pool.get('carrier')

        context = Transaction().context
        shipment = ShipmentOut(context['active_id'])

        credential = self.get_credential(shipment)
        packages = shipment.root_packages
        shipment_request = self.get_rate_request(
            shipment, packages, credential)
        api_url = config.get('stock_package_shipping_ups', credential.server,
            default=SERVER_URLS[credential.server])
        nb_tries, response = 0, None
        error_message = ''
        try:
            while nb_tries < 5 and response is None:
                try:
                    req = requests.post(api_url, json=shipment_request)
                except ssl.SSLError as e:
                    error_message = e.message
                    nb_tries += 1
                    continue
                req.raise_for_status()
                response = req.json()
        except requests.HTTPError as e:
            error_message = e.message

        if error_message:
            raise UPSError(
                gettext('stock_package_shipping_ups.msg_ups_webservice_error',
                    message=error_message))

        if 'Fault' in response:
            error = response['Fault']['detail']['Errors']
            message = '%s\n\n%s - %s' % (response['Fault']['faultstring'],
                error['ErrorDetail']['PrimaryErrorCode']['Code'],
                error['ErrorDetail']['PrimaryErrorCode']['Description'])
            raise UPSError(
                gettext('stock_package_shipping_ups.msg_ups_webservice_error',
                    message=message))

        rate_response = response['RateResponse']
        response_status = rate_response['Response']['ResponseStatus']
        if response_status['Code'] != '1':
            raise UPSError(
                gettext('stock_package_shipping_ups.msg_ups_webservice_error',
                    message=response_status['Description']))
        rate_results = rate_response['RatedShipment']
        if context['active_model'] == 'sale.sale':
            return rate_results
        ups_packages = rate_results['RatedPackage']
        if len(packages) == 1:
            # In case only one package is requested UPS returns a dictionnary
            # instead of a list of one package
            ups_packages = [ups_packages]

        service_types = dict(Carrier.ups_service_type.selection)
        service = service_types[shipment.carrier.ups_service_type]

        spacer = ' ' * 2
        message = gettext('stock_package_rate_ups.msg_package_weight')
        message += ':\n'
        msg_weight = gettext('stock_package_rate_ups.msg_weight')
        for tryton_pkg, ups_pkg in zip_longest(packages, ups_packages):
            message += '%s%s: %s\n' % (spacer, msg_weight, ups_pkg['Weight'])
        msg_billing_weight = gettext(
            'stock_package_rate_ups.msg_billing_weight')
        message += '\n%s:\n' % (msg_billing_weight,)
        message += '%s%s: %s\n' % (spacer, msg_weight,
            rate_results['BillingWeight']['Weight'],)
        msg_charges = gettext('stock_package_rate_ups.msg_charges')
        message += '\n%s:\n' % (msg_charges,)
        msg_trans_charges = gettext(
            'stock_package_rate_ups.msg_transportation_charges')
        message += '%s%s: %s\n' % (spacer, msg_trans_charges,
            rate_results['TransportationCharges']['MonetaryValue'])
        msg_options_charges = gettext(
            'stock_package_rate_ups.msg_options_charges')
        message += '%s%s: %s\n' % (spacer, msg_options_charges,
            rate_results['ServiceOptionsCharges']['MonetaryValue'])
        msg_total_charges = gettext('stock_package_rate_ups.msg_total_charges')
        message += '%s%s: %s\n' % (spacer, msg_total_charges,
            rate_results['TotalCharges']['MonetaryValue'])
        alerts = rate_results.get('RatedShipmentAlert')
        if alerts:
            msg_alerts = gettext('stock_package_rate_ups.msg_alerts')
            message += '\n%s:\n' % (msg_alerts,)
            for alert in alerts:
                message += '%s%s: %s\n' % (spacer, alert['Code'],
                    alert['Description'])
        raise UPSResult(
            gettext('stock_package_rate_ups.msg_ups_webservice_result',
                service=service, message=message))

        return 'end'

    def get_credential_pattern(self, shipment):
        return {
            'company': shipment.company.id,
            }

    def get_credential(self, shipment):
        pool = Pool()
        UPSCredential = pool.get('carrier.credential.ups')

        credential_pattern = self.get_credential_pattern(shipment)
        for credential in UPSCredential.search([]):
            if credential.match(credential_pattern):
                return credential

    def get_security(self, credential):
        return {
            'UsernameToken': {
                'Username': credential.user_id,
                'Password': credential.password,
                },
            'ServiceAccessToken': {
                'AccessLicenseNumber': credential.license,
                },
            #'LoginAcceptTermsAndConditionsRequest': {
            #    'Request': '',
            #    },
            }

    def get_rate_request_container(self, shipment):
        '''
        Override the RequestOption for rate requests

        Available options are 'Rate' or 'Shop'
        'SubVersion': '1703' return more info in the response
        'RequestOption': 'Rate' rate for a specified service type (Default)
        'RequestOption': 'Shop' all available rates for a service type
        'RequestOption': 'Ratetimeintransit' -> different API
        'RequestOption': 'Shoptimeintransit' -> different API
        '''
        request_container = {
            'TransactionReference': {
                'CustomerContext': (shipment.number or '')[:512],
                },
            }
        context = Transaction().context
        option = 'Rate'
        if context.get('ups_rate_api_mode'):
            option = context['ups_rate_api_mode']
        request_container['RequestOption'] = option
        return request_container

    def get_rate_shipping_party(self, party, address):
        return {
            'Name': address.party_full_name[:35],
            'AttentionName': party.full_name[:35],
            'Address': {
                'AddressLine': [l[:35]
                    for l in (address.street or '').splitlines()[:3]],
                'City': address.city[:30],
                'PostalCode': (address.zip or '').replace(' ', '')[:9],
                'CountryCode': address.country.code if address.country else '',
                },
            }

    def get_rate_package(self, use_metric, package):
        pool = Pool()
        UoM = pool.get('product.uom')
        ModelData = pool.get('ir.model.data')

        cm = UoM(ModelData.get_id('product', 'uom_centimeter'))
        inch = UoM(ModelData.get_id('product', 'uom_inch'))

        kg = UoM(ModelData.get_id('product', 'uom_kilogram'))
        lb = UoM(ModelData.get_id('product', 'uom_pound'))

        weight = UoM.compute_qty(kg, package.total_weight,
                        kg if use_metric else lb)
        # Fallback to the minimal accepted weight when the weight in kg is
        # displayed as zero kg after rounding to the first decimal
        if weight < 0.1:
            weight = 0.1

        package = {
            'PackagingType': {
                'Code': package.type.ups_code,
                },
            'Dimensions': {
                'UnitOfMeasurement': {
                    'Code': 'CM' if use_metric else 'IN',
                    },
                'Length': '%i' % round(UoM.compute_qty(package.type.length_uom,
                        package.type.length, cm if use_metric else inch)),
                'Width': '%i' % round(UoM.compute_qty(package.type.width_uom,
                        package.type.width, cm if use_metric else inch)),
                'Height': '%i' % round(UoM.compute_qty(package.type.height_uom,
                        package.type.height, cm if use_metric else inch)),
                },
            'PackageWeight': {
                'UnitOfMeasurement': {
                    'Code': 'KGS' if use_metric else 'LBS',
                    },
                'Weight': str(weight),
                },
            }
        return package

    def get_rate_shipment_container(
            self, shipment, packages, credential, request_container):
        warehouse_address = shipment.warehouse.address
        shipper = self.get_rate_shipping_party(shipment.company.party,
            warehouse_address)
        ship_from = shipper.copy()
        shipper['ShipperNumber'] = credential.account_number
        ship_to = self.get_rate_shipping_party(shipment.customer,
            shipment.delivery_address),

        packages = [self.get_rate_package(credential.use_metric, p)
            for p in packages]

        shipment_container = {
            'Shipper': shipper,
            'ShipTo': ship_to,
            'ShipFrom': ship_from,
            'Package': packages,
            }
        if request_container['RequestOption'] == 'Rate':
            # Only if the request is for one special service (Rate)
            service = {
                'Code': shipment.carrier.ups_service_type,
                'Description': 'Standard',
                }
            shipment_container['Service'] = service
        if shipment.carrier and shipment.carrier.ups_negotiated_rates:
            rating_options = {
                        # no shipper_number in shipper for
                        #'UserLevelDiscountIndicator': 'TRUE',
                        'NegotiatedRatesIndicator': '',
                        }
            shipment_container['ShipmentRatingOptions'] = rating_options
        return shipment_container

    def get_rate_request(self, shipment, packages, credential):
        request_container = self.get_rate_request_container(shipment)
        shipment_container = self.get_rate_shipment_container(
            shipment, packages, credential, request_container)
        return {
            'UPSSecurity': self.get_security(credential),
            'RateRequest': {
                'Request': request_container,
                'Shipment': shipment_container,
                }
             }


class RateUPSInsuranceMixin:

    def get_package_insurance(self):
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')
        SaleLine = pool.get('sale.line')
        # product_kit
        try:
            SaleLineComponent = pool.get('sale.line.component')
        except KeyError:
            SaleLineComponent = None

        insurance = None
        shipment = ShipmentOut(Transaction().context['active_id'])
        carrier = shipment.carrier
        if carrier and carrier.ups_declare_insurance:
            sale_lines = set()
            for move in shipment.outgoing_moves:
                if isinstance(move.origin, SaleLine):
                    sale_lines.add(move.origin)
                elif (SaleLineComponent
                        and isinstance(move.origin, SaleLineComponent)):
                    sale_lines.add(move.origin.line)
            total_amount = sum([line.amount_w_tax for line in sale_lines])
            currency = shipment.outgoing_moves[0].currency
            insurance = {
                'PackageServiceOptions': {
                    'DeclaredValue': {
                        'MonetaryValue': str(total_amount),
                        'CurrencyCode': currency.code,
                        },
                    },
                }
        return insurance


class GetRateUPS(RateUPSInsuranceMixin, RateUPSMixin, Wizard):
    'Get UPS Rates'
    __name__ = 'stock.shipment.get_rate.ups'

    def get_rate_package(self, use_metric, package):
        package = super().get_rate_package(use_metric, package)
        insurance = self.get_package_insurance()
        if insurance:
            package.update(insurance)
        return package


class ShippingUPSMixin:

    def validate_packing_ups(self):
        super().validate_packing_ups()
        # TODO validate carrier service type against selected package type/UPS
        # code
        carrier = self.carrier
        #if not warehouse.address:
        #    raise PackingValidationError(
        #        gettext('stock_package_shipping_ups'
        #            '.msg_warehouse_address_required',
        #            shipment=self.rec_name,
        #            warehouse=warehouse.rec_name))
        #if warehouse.address.country != self.delivery_address.country:
        #    for party in {self.shipping_to, self.company.party}:
        #        for mechanism in party.contact_mechanisms:
        #            if mechanism.type in ('phone', 'mobile'):
        #                break
        #        else:
        #            raise PackingValidationError(
        #                gettext('stock_package_shipping_ups'
        #                    '.msg_phone_required',
        #                    shipment=self.rec_name,
        #                    party=party.rec_name))
        #    if not self.shipping_description:
        #        if (any(p.type.ups_code != '01' for p in self.root_packages)
        #                and self.carrier.ups_service_type != '11'):
        #            # TODO Should also test if a country is not in the EU
        #            raise PackingValidationError(
        #                gettext('stock_package_shipping_ups'
        #                    '.msg_shipping_description_required',
        #                    shipment=self.rec_name))


class ShipmentOut(ShippingUPSMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'


class ShipmentInReturn(ShippingUPSMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.in.return'


class CreateShippingUPS(RateUPSInsuranceMixin, metaclass=PoolMeta):
    __name__ = 'stock.shipment.create_shipping.ups'

    def get_package(self, use_metric, package):
        package = super().get_package(use_metric, package)
        insurance = self.get_package_insurance()
        if insurance:
            package.update(insurance)
        return package
