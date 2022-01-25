"""eduNEXT custom payment processor file.

Contain a configurable payment processor for multiples custom processors, the
configuration will set the transaction parameters and custom requirements for
every different processors, ONLY one configuration can be set by site so it is
not possible multiple custom processors by site.

Classes:
    EdnxPaymentProcessor: Configurable payment class processor.
"""
import logging
from decimal import Decimal
from hashlib import sha256

from crum import get_current_request
from django.conf import settings
from django.urls import reverse
from django.utils.decorators import classproperty
from django.utils.functional import cached_property
from oscar.apps.payment.exceptions import GatewayError, TransactionDeclined
from oscar.core.loading import get_model

from ecommerce_extensions.payment.encryption_utils import encode_string
from ecommerce_extensions.payment.exceptions import InvalidEdnxDecision, TransactionPending

try:
    from ecommerce.extensions.payment.exceptions import InvalidSignatureError
    from ecommerce.extensions.payment.processors import BasePaymentProcessor, HandledProcessorResponse
except ImportError:
    BasePaymentProcessor = object

logger = logging.getLogger(__name__)

PaymentEvent = get_model('order', 'PaymentEvent')
PaymentEventType = get_model('order', 'PaymentEventType')
ProductClass = get_model('catalogue', 'ProductClass')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')
DEFAULT_NAME = 'edupay'


class EdnxPaymentProcessor(BasePaymentProcessor):
    """ EdnxPaymentProcessor class

    The following configuration is required in order to work with this:



    EDNX_PAYMENT_PROCESSOR_CONFIG: {
        'PAYMENT_PROCESSOR_NAME': 'a-cool-name',
        'IS_ENABLED': true,
        'SIGNATURE_PAYMENT_KEYS':[
            'referenceCode',
            'amount',
            'currency'
        ],
        'SIGNATURE_CONFIRMATION_KEYS':[
            'reference_sale',
            'value',
            'currency',
            'state_pol'
        ],
        'owner':{
            'key_email': email',
            'key_fullname': 'full_name',
            ...
        },
        'basket':{
            'key_email': order_number',
            'key_fullname': 'currency',
            ...
        },
        'extra_parameters': {
            'key_field': value',
            ...
        },
        'courses': {
            'description':'id',
            ...
        }
    }

    PAYMENT_PROCESSOR_CONFIG : {
        'partner_name': {
            'PAYMENT_PROCESSOR_NAME': {
                'payment_page_url': 'http://payment-page.com',
                'merchant_id': 'some-id',
                'account_id': 'some-id',
                'api_key': 'some-api-key',
            }
        }
    }

    EDNX_PAYMENT_PROCESSOR_CONFIG: This is optional, with the following fields:

        **PAYMENT_PROCESSOR_NAME: This name will identify the payment processor, this name will be shown in the
            payment button.

        **IS_ENABLED: This toggle replaces the Waffle used for other processors. Defaults to False.

        **SIGNATURE_PAYMENT_KEYS: List of key parameters which will be used in the payment signature process.

        **SIGNATURE_CONFIRMATION_KEYS: List of key parameters which will be used in the confirmation signature process.

        ** owner: User information, the key will be the key in the transaction parameters and the value will be
        the attribute returned, example this configuration 'owner': {'buyerEmail': 'email'} will return
        {'buyerEmail': owner.email} in the transaction parameters.

        ** basket: basket information the key will be the key in the transaction parameters and the value will be
        the attribute returned, example this configuration 'basket': {'referenceCode': 'order_number'} will return
        {'referenceCode': basket.order_number} in the transaction parameters.

        ** courses: Course information, the key will be the key in the transaction parameters and the value will be
        the attribute returned, example this configuration 'courses': {'description':'id'} will return
        {'description':'course.id'} in the transaction parameters.

        ** extra_parameters: extra information the key will be the key in the transaction parameters and the value
        will be the same, example this configuration 'extra_parameters': {'site_code': '787895'} will return
        {'site_code': '787895'} in the transaction parameters.

    PAYMENT_PROCESSOR_CONFIG: This setting will contain all the fixed information and this is always required. The key
        PAYMENT_PROCESSOR_NAME must be the same value as the setting.
    """

    TRANSACTION_ACCEPTED = '4'
    TRANSACTION_DECLINED = '6'
    TRANSACTION_PENDING = '7'
    TRANSACTION_ERROR = '104'
    PAYMENT_FORM_SIGNATURE = 1
    CONFIRMATION_SIGNATURE = 2

    def __init__(self, site):
        """
        Constructs a new instance.

        Raises:
            KeyError: If no settings configured for this payment processor
        """
        super().__init__(site)
        configuration = self.configuration
        self.payment_page_url = configuration['payment_page_url']
        self.merchant_id = configuration['merchant_id']
        self.account_id = configuration['account_id']
        self.api_key = configuration['api_key']

    @classproperty
    def NAME(cls):  # pylint: disable=no-self-argument
        """Return the PAYMENT_PROCESSOR_NAME value or the DEFAULT_NAME.

        This is required since this allow to change the processor name per instance.
        """
        return getattr(settings, 'EDNX_PAYMENT_PROCESSOR_CONFIG', {}).get('PAYMENT_PROCESSOR_NAME', DEFAULT_NAME)

    @cached_property
    def ednx_configuration(self):
        """Return EDNX_PAYMENT_PROCESSOR_CONFIG value from django settings."""
        return getattr(settings, 'EDNX_PAYMENT_PROCESSOR_CONFIG', {})

    def get_transaction_parameters(self, basket, **kwargs):  # pylint: disable=unused-argument
        """
        Generate a dictionary of signed parameters requires to complete a transaction.

        Arguments:
            basket (Basket): The basket of products being purchased.
            kwargs: Key arguments.

        Returns:
            dict: Base parameters required to complete a transaction, including a signature.
        """
        confirmation_url = get_current_request().build_absolute_uri(
            reverse('ecommerce_extensions:edupay:notify'),
        )
        response_url = get_current_request().build_absolute_uri(
            reverse(
                'ecommerce_extensions:edupay:status',
                kwargs={'order_number': encode_string(basket.order_number)},
            ),
        )
        parameters = {
            'accountId': self.account_id,
            'confirmationUrl': confirmation_url,
            'merchantId': self.merchant_id,
            'payment_page_url': self.payment_page_url,
            'responseUrl': response_url,
        }
        parameters.update(self._get_basket_parameters(basket))
        parameters.update(self._get_owner_parameters(basket.owner))
        parameters.update(self._get_courses_parameters(self.get_course_list(basket)))
        parameters.update(self.ednx_configuration.get('extra_parameters', {}))
        parameters['signature'] = self._generate_signature(parameters, self.PAYMENT_FORM_SIGNATURE)

        return parameters

    def _get_owner_parameters(self, owner):
        """Generate a dictionary with the user attributes which are set in EDNX_PAYMENT_PROCESSOR_CONFIG['owner'].

        Arguments:
            owner (User): Instance of User model.

        Returns:
            parameters(dict): Founded attributes for the given user.
        """
        parameters = {}

        for key, value in self.ednx_configuration.get('owner', {}).items():
            if hasattr(owner, value):
                parameters[key] = str(getattr(owner, value))
            elif value in getattr(owner, 'extended_profile_fields', {}):
                parameters[key] = str(owner.extended_profile_fields.get(value))
            else:
                parameters[key] = ''
                logger.error(
                    'The configuration owner value [%s] for [%s] is not valid, verify the setting object.',
                    value,
                    self.NAME,
                )

        return parameters

    def _get_basket_parameters(self, basket):
        """Generate a dictionary with the basket attributes which are set in EDNX_PAYMENT_PROCESSOR_CONFIG['basket'].

        Arguments:
            basket (Basket): Instance of Basket model.

        Returns:
            parameters(dict): Founded attributes for the given user.
        """
        parameters = {}

        for key, value in self.ednx_configuration.get('basket', {}).items():
            try:
                parameters[key] = str(getattr(basket, value))
            except AttributeError:
                logger.error(
                    'The configuration basket value [%s] for [%s] is not valid, verify the setting object.',
                    value,
                    self.NAME,
                )

        return parameters

    def _get_courses_parameters(self, courses):
        """Generate a dictionary with the course attributes which are set in EDNX_PAYMENT_PROCESSOR_CONFIG['courses'].

        Arguments:
            courses (List): List of courses.

        Returns:
            parameters(dict): Founded attributes for the given user.
        """
        parameters = {}

        for key, value in self.ednx_configuration.get('courses', {}).items():
            try:
                parameters[key] = ';'.join([str(getattr(course, value)) for course in courses])
            except AttributeError:
                logger.error(
                    'The configuration basket value [%s] for [%s] is not valid, verify the setting object.',
                    value,
                    self.NAME,
                )

        return parameters

    @staticmethod
    def get_course_list(basket):
        """
        Return the products encountered in the basket with the product
        class of 'seat'.  Return None if no such products were found.

        Arguments:
            basket (Basket): Basket being purchased via the payment processor.

        Returns:
            course_list: All the courses in the basket.
        """
        course_list = []
        try:
            seat_class = ProductClass.objects.get(slug='seat')
        except ProductClass.DoesNotExist:
            # this occurs in test configurations where the seat product class is not in use
            return None

        for line in basket.lines.all():
            product = line.product
            if product.get_product_class() == seat_class:
                course_list.append(product.course)

        return course_list if course_list else None

    def handle_processor_response(self, response, basket=None):  # pylint: disable=unused-argument
        """
        Handle a response (i.e., "merchant notification").

        This method does the following:
            1. Verify the validity of the response.
            2. Create PaymentEvents and Sources for successful payments.

        Arguments:
            response (dict): Dictionary of parameters received from the payment processor.

        Keyword Arguments:
            basket (Basket): Basket being purchased via the payment processor.

        Raises:
            TransactionDeclined: Indicates the payment was declined by the processor.
            GatewayError: Indicates a general error on the part of the processor.
            InvalidEdnxDecision: Indicates an unknown decision value

        Returns:
            HandleProcessorResponse: Payment info (transaction_id, total, currency, card_number and card_type)
        """

        # Validate the signature
        if not self.is_signature_valid(response):
            raise InvalidSignatureError
        # Raise an exception for payments that were not accepted. Consuming code should be responsible for handling
        # and logging the exception.
        transaction_state = response['state_pol']

        if transaction_state != self.TRANSACTION_ACCEPTED:
            exception = {
                self.TRANSACTION_DECLINED: TransactionDeclined,
                self.TRANSACTION_ERROR: GatewayError,
                self.TRANSACTION_PENDING: TransactionPending,
            }.get(transaction_state, InvalidEdnxDecision)

            raise exception

        currency = response.get('currency')
        total = Decimal(response.get('value'))
        transaction_id = response.get('transaction_id')
        card_number = response.get('cc_number', '')
        card_type = response.get('lapPaymentMethod', '')

        return HandledProcessorResponse(
            transaction_id=transaction_id,
            total=total,
            currency=currency,
            card_number=card_number,
            card_type=card_type,
        )

    def _generate_signature(self, parameters, signature_type):
        """
        Sign the contents of the provided transaction parameters dictionary.

        This allows PP to verify that the transaction parameters have not been tampered with
        during transit.

        We also use this signature to verify that the signature we get back from PP is valid for
        the parameters that they are giving to us.

        Arguments:
            parameters (dict): A dictionary of transaction parameters.
            signature_type: Digital signature created for each of the transactions

        Returns:
            unicode: the signature for the given parameters
        """
        signature_keys = []
        extra_uncoded = ''
        basic_uncoded = '{api_key}~{merchant_id}'.format(api_key=self.api_key, merchant_id=self.merchant_id)

        if signature_type == self.PAYMENT_FORM_SIGNATURE:
            signature_keys = self.ednx_configuration.get('SIGNATURE_PAYMENT_KEYS', [])
        elif signature_type == self.CONFIRMATION_SIGNATURE:
            # The logic to validate signatures on confirmation page:
            # If the second decimal of the value parameter is zero, e.g. 150.00
            # the parameter new_value to generate the signature should only have one decimal, as follows: 150.0
            # If the second decimal of the value parameter is different from zero, e.g. 150.26
            # the parameter new_value to generate the signature should have two decimals, as follows: 150.26
            # taken from http://developers.payulatam.com/en/web_checkout/integration.html
            # hence the parameter value is mandatory
            value = parameters['value']
            parameters['value'] = value[:-1] if (value[-1] == '0' and value[-3] == '.') else value
            signature_keys = self.ednx_configuration.get('SIGNATURE_CONFIRMATION_KEYS', [])

        try:
            extra_uncoded = '~'.join([parameters[key] for key in signature_keys])
        except KeyError as error:
            logger.error('Invalid signature key [%s]', error)

        uncoded = '{basic_uncoded}~{extra_uncoded}'.format(
            basic_uncoded=basic_uncoded,
            extra_uncoded=extra_uncoded,
        ) if extra_uncoded else basic_uncoded

        return sha256(uncoded.encode('utf-8')).hexdigest()

    def is_signature_valid(self, response):
        """Returns a boolean indicating if the response's signature (indicating potential tampering) is valid."""
        return response and (self._generate_signature(response, self.CONFIRMATION_SIGNATURE) == response.get('sign'))

    def issue_credit(self, order_number, basket, reference_number, amount, currency):  # pylint: disable=unused-argument
        """
        This method should be implemented in the future in order
        to accept payment refunds
        """
        logger.exception('edupay processor can not issue credits or refunds')

        raise NotImplementedError

    @classmethod
    def is_enabled(cls):
        """
        Returns True if this payment processor is enabled, and False otherwise.
        """
        return getattr(settings, 'EDNX_PAYMENT_PROCESSOR_CONFIG', {}).get('IS_ENABLED', False)
