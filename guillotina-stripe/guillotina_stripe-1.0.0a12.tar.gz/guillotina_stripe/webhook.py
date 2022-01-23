from guillotina import configure
from guillotina.interfaces import IContainer
from guillotina.interfaces import IApplication

from guillotina.component import get_utility
from guillotina_stripe.interfaces import IStripePayUtility
from guillotina.event import notify
from guillotina_stripe.events import InvoicePaidEvent
from guillotina_stripe.events import InvoicePaymentFailed
from guillotina_stripe.events import InvoiceFinalized
from guillotina_stripe.events import PaymentIntentSucceded
from guillotina_stripe.events import PaymentIntentFailed

from guillotina_stripe.events import CustomerSubscriptionUpdated
from guillotina_stripe.events import CustomerSubscriptionDeleted
from guillotina_stripe.events import CustomerSubscriptionTrialWillEnd

import logging

logger = logging.getLogger('guillotina_stripe')

@configure.service(
    method="POST",
    name="@stripe",
    permission="guillotina.Public",
    context=IContainer,
    allow_access=True,
    summary="get album validation",
)
@configure.service(
    method="POST",
    name="@stripe",
    permission="guillotina.Public",
    context=IApplication,
    allow_access=True,
    summary="get album validation",
)
async def validate(context, request):
    util = get_utility(IStripePayUtility)

    request_data = await request.text()

    # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
    signature = request.headers.get('stripe-signature')

    data = await util.get_event(request_data, signature)
    # Get the type of webhook event sent - used to check the status of PaymentIntents.
    event_type = data['type']

    data_object = data['data']['object']

    if event_type == 'invoice.paid':
        await notify(InvoicePaidEvent(data_object))

    if event_type == 'invoice.payment_failed':
        await notify(InvoicePaymentFailed(data_object))

    if event_type == 'payment_intent.succeeded':
        await notify(PaymentIntentSucceded(data_object))

    if event_type == 'payment_intent.payment_failed':
        await notify(PaymentIntentFailed(data_object))

    if event_type == 'invoice.finalized':
        # If you want to manually send out invoices to your customers
        # or store them locally to reference to avoid hitting Stripe rate limits.
        await notify(InvoiceFinalized(data_object))

    if event_type == 'customer.subscription.updated':
        # handle subscription cancelled automatically based
        # upon your subscription settings. Or if the user cancels it.

        # subs_id = data['object']['id']
        # status = data['object']['incomplete_expired']

        await notify(CustomerSubscriptionUpdated(data_object))

    if event_type == 'customer.subscription.deleted':
        # handle subscription cancelled automatically based
        # upon your subscription settings. Or if the user cancels it.
        await notify(CustomerSubscriptionDeleted(data_object))

    if event_type == 'customer.subscription.trial_will_end':
        # Send notification to your user that the trial will end
        await notify(CustomerSubscriptionTrialWillEnd(data_object))

    print(event_type)
    logger.info(event_type)
    return {'status': 'success'}

