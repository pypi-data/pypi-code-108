from guillotina_stripe.events import ObjectPaidEvent, ObjectTrailingEvent
from guillotina_stripe.events import ObjectFailedEvent
from guillotina_stripe.utility import StripePayUtility
from guillotina_stripe.models import BillingDetails, Card
from guillotina_stripe.interfaces import (
    ICustomerSubscriptionDeleted, ICustomerSubscriptionTrialWillEnd, IInvoicePaidEvent,
    IInvoicePaymentFailed,
    IMarkerSubscription,
    ISubscription,
)
from guillotina import configure
from guillotina.component import get_utility
from guillotina_stripe.interfaces import IStripePayUtility
from guillotina.response import HTTPPreconditionFailed
from guillotina.browser import get_physical_path
from guillotina import app_settings
from guillotina.event import notify
from guillotina import task_vars
from guillotina.utils import get_database
from guillotina.transactions import transaction
from guillotina.utils.content import navigate_to
from guillotina.exceptions import DatabaseNotFound


@configure.service(
    method="GET",
    name="@cards",
    permission="guillotina.ModifyContent",
    context=IMarkerSubscription,
    summary="Get payment method",
)
async def get_cards(context, request):
    bhr = ISubscription(context)
    if bhr.customer is None:
        return {"data": []}

    util = get_utility(IStripePayUtility)

    cards = await util.get_payment_methods(customer=bhr.customer, type="card")
    customer = await util.get_customer(bhr.customer)
    cards["customer"] = customer
    return cards


@configure.service(
    method="POST",
    name="@register-card",
    permission="guillotina.ModifyContent",
    context=IMarkerSubscription,
    validate=True,
    requestBody={
        "content": {
            "application/json": {
                "schema": {
                    "properties": {
                        "email": {"type": "string"},
                        "number": {"type": "string"},
                        "expMonth": {"type": "string"},
                        "expYear": {"type": "string"},
                        "cvc": {"type": "string"},
                        "cardholderName": {"type": "string"},
                        "address": {"type": "string"},
                        "state": {"type": "string"},
                        "city": {"type": "string"},
                        "cp": {"type": "string"},
                        "country": {"type": "string"},
                        "phone": {"type": "string"},
                        "tax": {"type": "string"},
                    }
                }
            }
        }
    },
    summary="Register payment method",
)
async def register_paymentmethod(context, request):
    bhr = ISubscription(context)
    payload = await request.json()
    billing_email = payload.get("email", None)
    if billing_email is None:
        return {"status": "error", "error": "Need email"}

    bhr.billing_email = billing_email
    util: StripePayUtility = get_utility(IStripePayUtility)
    customer = await util.set_customer(billing_email, payload.get("customer_id", None))
    taxid = payload.get("tax")

    customerid = customer.get("id", None)
    if taxid is not None:
        await util.set_tax(customerid, taxid)
    bhr.customer = customerid

    billing_details = BillingDetails(
        city=payload.get("city"),
        country=payload.get("country"),
        postal_code=payload.get("cp"),
        line1=payload.get("address"),
        state=payload.get("state"),
        email=billing_email,
        name=payload.get("cardholderName"),
        phone=payload.get("phone"),
    )

    card = Card(
        exp_month=payload.get("expMonth"),
        exp_year=payload.get("expYear"),
        number=payload.get("number"),
        cvc=payload.get("cvc"),
    )

    result = await util.create_paymentmethod(
        type="card", billing_details=billing_details, card=card
    )
    pmid = result.get("id")
    bhr.pmid = pmid
    if pmid is not None:
        await util.attach_payment_method(pmid, customerid)
        await util.modify_customer(pmid, customerid)
    context.register()
    return result


@configure.service(
    method="GET",
    name="@subscriptions",
    permission="guillotina.ModifyContent",
    context=IMarkerSubscription,
    summary="Get subscriptions",
)
async def subscriptions(context, request):
    util = get_utility(IStripePayUtility)
    bhr = ISubscription(context)

    if bhr.customer is None:
        return {"data": [], "error": "No customer"}
    subscriptions = {}

    if bhr.customer is not None:
        subs = await util.get_subscriptions(customer=bhr.customer)
        subscriptions["data"] = subs

    return subscriptions


@configure.service(
    method="DELETE",
    name="@subscribe",
    permission="guillotina.ModifyContent",
    context=IMarkerSubscription,
)
async def unsubscribe(context, request):
    util = get_utility(IStripePayUtility)
    bhr = ISubscription(context)

    if bhr.subscription is not None and bhr.customer is not None:
        await util.cancel_subscription(bhr.subscription)
    bhr.register()


@configure.service(
    method="PATCH",
    name="@subscribe",
    permission="guillotina.ModifyContent",
    context=IMarkerSubscription,
)
async def update_subscription(context, request):
    payload = await request.json()
    util = get_utility(IStripePayUtility)
    bhr = ISubscription(context)

    if bhr.subscription is not None and bhr.customer is not None:
        subscription = await util.update_subscription(bhr.subscription, payload)

    bhr.cancel_at_period_end = subscription.get("cancel_at_period_end")
    bhr.register()

    return subscription


@configure.service(
    method="POST",
    name="@subscribe",
    permission="guillotina.ModifyContent",
    context=IMarkerSubscription,
    validate=True,
    requestBody={
        "content": {
            "application/json": {
                "schema": {
                    "properties": {
                        "pmid": {"type": "string"},
                        "price": {"type": "string"},
                    }
                }
            }
        }
    },
    summary="Register payment method",
)
async def subscribe(context, request):
    payload = await request.json()
    bhr = ISubscription(context)
    util = get_utility(IStripePayUtility)

    can_activate_trial = True
    if bhr.subscription is not None:
        current_subscription = await util.get_subscription(bhr.subscription)
        if current_subscription['status'] == 'canceled' or current_subscription['status'] == 'ended':
            can_activate_trial = False
        else:
            raise HTTPPreconditionFailed(
                content={"reason": "Subscription already exist"})

    customer = payload.get('customer', bhr.customer)
    if customer is None:
        raise HTTPPreconditionFailed(content={"reason": "No customer"})

    pmid = payload.get("pmid")
    price = payload.get("price")
    coupon = payload.get("coupon")

    if bhr.customer is None:
        customer_response = await util.get_customer(customer)
        bhr.customer = customer
        bhr.billing_email = customer_response['email']

    obj_type = context.type_name
    prices = app_settings["stripe"].get("subscriptions", {}).get(obj_type, [])
    trial = None
    if price is None and len(prices) > 0:
        price = prices[0]["price"]
        trial = prices[0]["trial"]
    elif price is not None:
        for orig_price in prices:
            if price == orig_price['price']:
                trial = orig_price.get('trial', 0)
        if trial is None:
            raise HTTPPreconditionFailed(
                content={"reason": "No price and no trial"})
    else:
        raise HTTPPreconditionFailed(content={"reason": "No price"})

    path = "/".join(get_physical_path(context))
    db = task_vars.db.get()

    if not can_activate_trial:
        trial = 0

    subscription = await util.create_subscription(
        customer=customer,
        price=price,
        payment_method=pmid,
        path=path,
        db=db.id,
        trial=trial,
        coupon=coupon
    )

    if subscription.get("id") is not None:
        if subscription.get("status") == "trailing" or subscription.get("status") == "trialing":
            bhr.trailing = True
            bhr.paid = False
            bhr.trial_end = subscription.get("trial_end")
            await notify(ObjectTrailingEvent(context, subscription))

        payment_intent = subscription.get("latest_invoice", {}).get(
            "payment_intent", {}
        )
        if payment_intent is not None:
            status = payment_intent.get("status", "failed")
            bhr.paid = False
            if status == "succeeded":
                bhr.paid = True
                await notify(ObjectPaidEvent(context, subscription))

        bhr.subscription = subscription.get("id")
        bhr.current_period_end = subscription.get("current_period_end")
        bhr.current_period_start = subscription.get("current_period_start")
        bhr.price_ids = [
            obj["price"]["id"] for obj in subscription.get("items", {}).get("data", [])
        ]
        context.register()

    return subscription


@configure.subscriber(for_=IInvoicePaidEvent)
async def webhook_paid(event):

    elements = []
    for line in event.data["lines"]["data"]:
        if line["type"] == "subscription":
            elements.append(line)

    if len(elements) == 0:
        return

    for element in elements:
        metadata = element.get("metadata", {})
        path = metadata.get("path", None)
        db_id = metadata.get("db", None)

        try:
            db = await get_database(db_id)
        except DatabaseNotFound:
            db = None

        if db is not None:
            async with transaction(db=db):
                obj = await navigate_to(db, path)
                bhr = ISubscription(obj)
                bhr.paid = True
                obj.register()
                await notify(ObjectPaidEvent(obj, event.data))


@configure.subscriber(for_=IInvoicePaymentFailed)
async def webhook_failed(event):
    elements = []
    for line in event.data["lines"]["data"]:
        if line["type"] == "subscription":
            elements.append(line)

    if len(elements) == 0:
        return

    for element in elements:
        metadata = element.get("metadata", {})
        path = metadata.get("path", None)
        db_id = metadata.get("db", None)

        try:
            db = await get_database(db_id)
        except DatabaseNotFound:
            db = None

        if db is not None:
            async with transaction(db=db):
                obj = await navigate_to(db, path)
                bhr = ISubscription(obj)
                bhr.paid = False
                obj.register()
                await notify(ObjectFailedEvent(obj, event.data))


@configure.subscriber(for_=ICustomerSubscriptionTrialWillEnd)
async def webhook_trailend(event):
    if event.data["object"] == "subscription":
        metadata = event.data.get("metadata", {})
        path = metadata.get("path", None)
        db_id = metadata.get("db", None)

        try:
            db = await get_database(db_id)
        except DatabaseNotFound:
            db = None

        if db is not None:
            async with transaction(db=db):
                obj = await navigate_to(db, path)
                bhr = ISubscription(obj)
                bhr.paid = False
                obj.register()
                await notify(ObjectFailedEvent(obj, event.data))


@configure.subscriber(for_=ICustomerSubscriptionDeleted)
async def webhook_deleted(event):
    if event.data["object"] == "subscription":
        metadata = event.data.get("metadata", {})
        path = metadata.get("path", None)
        db_id = metadata.get("db", None)

        try:
            db = await get_database(db_id)
        except DatabaseNotFound:
            db = None

        if db is not None:
            async with transaction(db=db):
                obj = await navigate_to(db, path)
                bhr = ISubscription(obj)
                bhr.paid = False
                bhr.trailing = False
                obj.register()
                await notify(ObjectFailedEvent(obj, event.data))
