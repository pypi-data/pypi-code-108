# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import ssl

from decimal import Decimal

import requests

from trytond.config import config
from trytond.i18n import gettext
from trytond.modules.stock_package_rate_ups.stock import (
    SERVER_URLS, RateUPSMixin)
from trytond.modules.stock_package_shipping_ups.exceptions import UPSError
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.wizard import Wizard


class ApplyShipping(metaclass=PoolMeta):
    __name__ = "sale.sale.apply_shipping"

    def transition_get_rates(self):
        context = Transaction().context
        context = context.copy()
        context['ups_rate_api_mode'] = 'Shop'
        with Transaction().set_context(**context):
            return super().transition_get_rates()


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    def get_shipping_rates(self, carriers=None):
        '''
        Set the active_id in the context when it is missing (can be in the case
        of web requests)
        '''
        context = Transaction().context
        context = context.copy()
        if not context.get('active_id'):
            context['active_id'] = self.id
        if self.carrier and not context.get('ups_rate_api_mode'):
            context['ups_rate_api_mode'] = 'Rate'
        with Transaction().set_context(**context):
            return super().get_shipping_rates(carriers=carriers)

    def get_shipping_rate(self, carrier):
        '''
        Gives a list of rates from provided carrier.
        Creates temporary shipments/packages when there are None to use the
        get_rate wizard from shipment.

        List contains dictionary with following minimum keys:
            [
                {
                    'display_name': Name to display,
                    'cost': cost,
                    'cost_currency': currency.currency active record,
                    'carrier': carrier active record,
                }..
            ]

        '''
        pool = Pool()
        Company = pool.get('company.company')
        Carrier = pool.get('carrier')
        GetRateWizard = pool.get('sale.get_rate.ups', type='wizard')

        if carrier.carrier_cost_method == 'api_ups':
            rates = []
            transaction = Transaction()
            context = {'carrier': carrier.id}
            if not transaction.context.get('ups_rate_api_mode'):
                context['ups_rate_api_mode'] = 'Shop'
            with transaction.set_context(**context):
                rate_wizard = GetRateWizard(GetRateWizard.create()[0])
                currency = Company(transaction.context['company']).currency
                try:
                    result = rate_wizard.transition_start()
                except UPSError as e:
                    return {
                        'display_name': carrier.party.name,
                        'cost': Decimal('0.0'),
                        'cost_currency': currency,
                        'carrier': carrier,
                        'errors': str(e),
                        }
                service_types = dict(Carrier.ups_service_type.selection)
                if not isinstance(result, list):
                    # In case only one package is requested UPS returns
                    # a dictionary instead of a list of one package
                    result = [result]
                for item in result:
                    description = service_types[item['Service']['Code']]
                    service = '%s - %s' % (carrier.party.name, description)
                    rate = {
                        'display_name': service,
                        'cost': Decimal(item['TotalCharges']['MonetaryValue']),
                        'cost_currency': currency,
                        'carrier': carrier,
                        'code': item['Service']['Code'],
                        }
                    rates.append(rate)
            return rates

        return super().get_shipping_rate(carrier)


class GetRateUPS(RateUPSMixin, Wizard):
    'Get UPS Rates'
    __name__ = 'sale.get_rate.ups'

    def transition_start(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Carrier = pool.get('carrier')

        context = Transaction().context
        sale_id = context.get('sale') or context.get('active_id')
        sale = Sale(sale_id)
        if context.get('carrier'):
            carrier = Carrier(context['carrier'])
        else:
            raise

        credential = self.get_credential(sale)
        shipment_request = self.get_rate_request(
            sale, carrier, credential)
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
        return rate_results

    def get_credential_pattern(self, sale):
        return {
            'company': sale.company.id,
            }

    def get_credential(self, sale):
        pool = Pool()
        UPSCredential = pool.get('carrier.credential.ups')

        credential_pattern = self.get_credential_pattern(sale)
        for credential in UPSCredential.search([]):
            if credential.match(credential_pattern):
                return credential

    def get_rate_request_container(self, sale):
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
                'CustomerContext': 'Sale %s' % ((sale.number or '')[:512],),
                },
            }
        context = Transaction().context
        option = 'Rate'
        if context.get('ups_rate_api_mode'):
            option = context['ups_rate_api_mode']
        request_container['RequestOption'] = option
        return request_container

    def get_rate_package(self, use_metric, sale, package_type, carrier):
        pool = Pool()
        UoM = pool.get('product.uom')
        ModelData = pool.get('ir.model.data')

        cm = UoM(ModelData.get_id('product', 'uom_centimeter'))
        inch = UoM(ModelData.get_id('product', 'uom_inch'))

        kg = UoM(ModelData.get_id('product', 'uom_kilogram'))
        lb = UoM(ModelData.get_id('product', 'uom_pound'))
        weight = UoM.compute_qty(sale.weight_uom, sale.weight,
                        kg if use_metric else lb)
        # Fallback to the minimal accepted weight when the weight in kg is
        # displayed as zero kg after rounding to the first decimal
        if weight < 0.1:
            weight = 0.1

        package = {
            'PackagingType': {
                'Code': package_type.ups_code,
                },
            'Dimensions': {
                'UnitOfMeasurement': {
                    'Code': 'CM' if use_metric else 'IN',
                    },
                'Length': '%i' % round(UoM.compute_qty(package_type.length_uom,
                        package_type.length, cm if use_metric else inch)),
                'Width': '%i' % round(UoM.compute_qty(package_type.width_uom,
                        package_type.width, cm if use_metric else inch)),
                'Height': '%i' % round(UoM.compute_qty(package_type.height_uom,
                        package_type.height, cm if use_metric else inch)),
                },
            'PackageWeight': {
                'UnitOfMeasurement': {
                    'Code': 'KGS' if use_metric else 'LBS',
                    },
                'Weight': str(weight),
                },
            }
        if carrier.ups_declare_insurance:
            insurance = {
                'PackageServiceOptions': {
                    'DeclaredValue': {
                        'MonetaryValue': str(sale.total_amount),
                        'CurrencyCode': sale.currency.code,
                        },
                    },
                }
            package.update(insurance)
        return package

    def get_rate_shipment_container(
            self, sale, carrier, credential, request_container):
        warehouse_address = sale.warehouse.address
        shipper = self.get_rate_shipping_party(sale.company.party,
            warehouse_address)
        ship_from = shipper.copy()
        shipper['ShipperNumber'] = credential.account_number
        ship_to = self.get_rate_shipping_party(sale.party,
            sale.shipment_address),

        package_type = carrier.package_types[0]
        packages = [self.get_rate_package(credential.use_metric, sale,
                package_type, carrier)]

        shipment_container = {
            'Shipper': shipper,
            'ShipTo': ship_to,
            'ShipFrom': ship_from,
            'Package': packages,
            }
        if request_container['RequestOption'] == 'Rate':
            # Only if the request is for one special service (Rate)
            service = {
                'Code': carrier.ups_service_type,
                'Description': 'Standard',
                }
            shipment_container['Service'] = service
        if carrier.ups_negotiated_rates:
            rating_options = {
                        # no shipper_number in shipper for
                        #'UserLevelDiscountIndicator': 'TRUE',
                        'NegotiatedRatesIndicator': '',
                        }
            shipment_container['ShipmentRatingOptions'] = rating_options
        return shipment_container

    def get_rate_request(self, sale, carrier, credential):
        request_container = self.get_rate_request_container(sale)
        shipment_container = self.get_rate_shipment_container(
            sale, carrier, credential, request_container)
        return {
            'UPSSecurity': self.get_security(credential),
            'RateRequest': {
                'Request': request_container,
                'Shipment': shipment_container,
                }
             }


class ShippingUPSMixin:

    def validate_packing_ups(self):
        super().validate_packing_ups()

        # TODO validate carrier service type against selected package type/UPS
        # code
        #carrier = self.carrier
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
