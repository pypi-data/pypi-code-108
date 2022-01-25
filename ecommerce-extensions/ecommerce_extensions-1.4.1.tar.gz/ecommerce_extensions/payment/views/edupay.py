""" edupay payment processing views """
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from oscar.apps.partner import strategy
from oscar.apps.payment.exceptions import PaymentError, TransactionDeclined
from oscar.core.loading import get_class, get_model
from rest_framework import status
from rest_framework.views import APIView

from ecommerce_extensions.payment.constants import DECLINED_STATUS, PENDING_STATUS
from ecommerce_extensions.payment.encryption_utils import decode_string
from ecommerce_extensions.payment.processors.edupay import EdnxPaymentProcessor, TransactionPending

try:
    from ecommerce.extensions.checkout.mixins import EdxOrderPlacementMixin
    from ecommerce.extensions.checkout.utils import get_receipt_page_url
    from ecommerce.extensions.payment.exceptions import InvalidSignatureError
except ImportError:
    from ecommerce_extensions.payment.tests.exceptions import (  # pylint: disable=ungrouped-imports,useless-suppression
        InvalidSignatureError
    )

    class EdxOrderPlacementMixin:
        """This a class in order to avoid errors in a test scenario,
        since the dependency is not available.
        """

        # Empty variable to avoid errors in a test scenario
        order_placement_failure_msg = ''

        def handle_payment(self, reponse, basket):
            """ Empty method to avoid errors in a test scenario. """

logger = logging.getLogger(__name__)

Applicator = get_class('offer.applicator', 'Applicator')
Basket = get_model('basket', 'Basket')
BillingAddress = get_model('order', 'BillingAddress')
Country = get_model('address', 'Country')
NoShippingRequired = get_class('shipping.methods', 'NoShippingRequired')
Order = get_model('order', 'Order')
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')


class EdnxPaymentResponseView(EdxOrderPlacementMixin, View):
    """ Validates a response from the payment processor and processes the associated basket/order appropriately. """

    @property
    def payment_processor(self):
        """An instance of ednx payment processor."""
        return EdnxPaymentProcessor(self.request.site)

    # Disable atomicity for the view. Otherwise, we'd be unable to commit to the database
    # until the request had concluded; Django will refuse to commit when an atomic() block
    # is active, since that would break atomicity. Without an order present in the database
    # at the time fulfillment is attempted, asynchronous order fulfillment tasks will fail.
    @method_decorator(transaction.non_atomic_requests)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def _get_billing_address(self, edupay_response):
        """Return the billing address in the payment processor response"""

        return BillingAddress(
            first_name=edupay_response.get('cc_holder', ''),
            last_name=edupay_response.get('cc_holder', ''),
            line1=edupay_response.get('billing_address', ''),
            line4=edupay_response.get('billing_city', ''),  # Oscar uses line4 for city
            country=Country.objects.get(iso_3166_1_a2=edupay_response['billing_country']),
        )

    def _get_basket(self, basket_id):
        """Return basket object from the basket_id."""
        if not basket_id:
            return None

        try:
            basket_id = int(basket_id)
            basket = Basket.objects.get(id=basket_id)
            basket.strategy = strategy.Default()
            Applicator().apply(basket, basket.owner, self.request)
            return basket
        except (ValueError, ObjectDoesNotExist):
            return None

    def record_payment_response(self, request, edupay_response):
        """Record in the database the payment processor response"""
        basket = None
        transaction_id = None

        try:
            transaction_id = edupay_response.get('transaction_id')
            order_number = edupay_response.get('reference_sale')
            basket_id = OrderNumberGenerator().basket_id(order_number)

            logger.info(
                'Received [%s] merchant notification for transaction [%s], associated with basket [%d].',
                EdnxPaymentProcessor.NAME,
                transaction_id,
                basket_id,
            )

            basket = self._get_basket(basket_id)

            if not basket:
                logger.error('Received payment for non-existent basket [%s].', basket_id)
                return HttpResponseBadRequest("Error recording payment")
        finally:
            # Store the response in the database.
            response_stored = self.payment_processor.record_processor_response(
                edupay_response,
                transaction_id=transaction_id,
                basket=basket,
            )
        response = self.handle_payment_status(request, edupay_response, basket, order_number, response_stored)
        return response

    def handle_payment_status(self, request, edupay_response, basket, order_number, response_stored):
        """Raise an exception if the payment status is pending or declined"""
        try:
            # Explicitly delimit operations which will be rolled back if an exception occurs.
            with transaction.atomic():
                try:
                    self.handle_payment(edupay_response, basket)
                except InvalidSignatureError:
                    logger.exception(
                        'Received an invalid [%s] response. The payment response was recorded in entry [%d].',
                        EdnxPaymentProcessor.NAME,
                        response_stored.id,
                    )
                    return HttpResponseBadRequest("Wrong signature")
                except TransactionPending:
                    logger.info(
                        '[%s] payment is pending for basket [%d]. '
                        'The payment response was recorded in entry [%d].',
                        EdnxPaymentProcessor.NAME,
                        basket.id,
                        response_stored.id,
                    )
                    basket.status = PENDING_STATUS
                    basket.save()
                    return HttpResponse(status=status.HTTP_200_OK)
                except TransactionDeclined as exception:
                    logger.info(
                        '[%s] payment did not complete for basket [%d] because [%s]. '
                        'The payment response was recorded in entry [%d].',
                        EdnxPaymentProcessor.NAME,
                        basket.id,
                        exception.__class__.__name__,
                        response_stored.id,
                    )
                    basket.status = DECLINED_STATUS
                    basket.save()
                    return HttpResponse(status=status.HTTP_200_OK)
                except PaymentError:
                    logger.exception(
                        '[%s] payment failed for basket [%d]. The payment response was recorded in entry [%d].',
                        EdnxPaymentProcessor.NAME,
                        basket.id,
                        response_stored.id,
                    )
                    return HttpResponseBadRequest("Payment error")
        except:  # pylint: disable=bare-except
            logger.exception('Attempts to handle payment for basket [%d] failed.', basket.id)
            return HttpResponseBadRequest("Unspecified error processing response")
        response = self.record_order(request, edupay_response, basket, order_number)
        return response

    def record_order(self, request, edupay_response, basket, order_number):
        """Record the order in the database"""
        try:
            # Note (CCB): In the future, if we do end up shipping physical products, we will need to
            # properly implement shipping methods. For more, see
            # http://django-oscar.readthedocs.org/en/latest/howto/how_to_configure_shipping.html.
            shipping_method = NoShippingRequired()
            shipping_charge = shipping_method.calculate(basket)

            # Note (CCB): This calculation assumes the payment processor has not sent a partial authorization,
            # thus we use the amounts stored in the database rather than those received from the payment processor.
            user = basket.owner
            order_total = OrderTotalCalculator().calculate(basket, shipping_charge)
            billing_address = self._get_billing_address(edupay_response)

            self.handle_order_placement(
                order_number,
                user,
                basket,
                None,
                shipping_method,
                shipping_charge,
                billing_address,
                order_total,
                request=request,
            )

            return HttpResponse(status=status.HTTP_200_OK)
        except:  # pylint: disable=bare-except
            payment_processor = None
            if self.payment_processor:
                payment_processor = self.payment_processor.NAME.title()  # pylint: disable=no-member
            logger.exception(self.order_placement_failure_msg, payment_processor, basket.id)
            return HttpResponseBadRequest("Error recording order")

    def post(self, request):
        """Process a payment processor merchant notification and place an order for paid products as appropriate."""

        # Note (CCB): Orders should not be created until the payment processor has validated the response's signature.
        # This validation is performed in the handle_payment method. After that method succeeds, the response can be
        # safely assumed to have originated from PP.
        edupay_response = request.POST.dict()
        response = self.record_payment_response(request, edupay_response)
        return response


class EdnxPaymentStatusView(APIView):
    """Polls payment status.

    Return the current status of the payment by polling the order
    or the basket status.
    """
    def get(self, request, order_number):
        """Provide confirmation of payment."""
        order_id = decode_string(order_number)
        payment_status = self._get_payment_status(order_id)
        if payment_status.lower() != 'submitted':
            return render(request, 'payment/pending_status.html', {'msg': payment_status})
        else:
            try:
                order = Order.objects.get(number=order_id)  # pylint: disable=unused-variable
            except Order.DoesNotExist:
                logger.info(
                    'Edupay Payment: No payment found for order [%s] ',
                    order_id,
                )
                return render(request, 'payment/pending_status.html', {'msg': 'error'})

        basket_id = OrderNumberGenerator().basket_id(order_id)
        basket = Basket.objects.get(id=basket_id)

        receipt_url = get_receipt_page_url(
            order_number=basket.order_number,
            site_configuration=basket.site.siteconfiguration,
        )

        return redirect(receipt_url)

    def _get_payment_status(self, order_number):
        """Get the current state of the payment."""
        try:
            basket_id = OrderNumberGenerator().basket_id(order_number)
            basket = Basket.objects.get(id=basket_id)

            logger.info(
                '[%s] Payment: Basket [%s] for order [%s] ',
                EdnxPaymentProcessor.NAME,
                basket.status,
                order_number,
            )
            return basket.status

        except:  # pylint: disable=bare-except
            logger.info(
                '[%s] Payment: Basket not found',
                EdnxPaymentProcessor.NAME,
            )

        logger.info(
            '[%s] Payment: Unknown processing error',
            EdnxPaymentProcessor.NAME,
        )
        return 'error'
