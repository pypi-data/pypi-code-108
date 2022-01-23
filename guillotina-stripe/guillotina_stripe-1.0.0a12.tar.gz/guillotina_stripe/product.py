from guillotina.response import HTTPPreconditionFailed
from guillotina import configure
from guillotina_stripe.interfaces import IProduct, IMarkerProduct, IStripeConfiguration
from guillotina_stripe.interfaces import IPaymentIntentFailed
from guillotina_stripe.interfaces import IPaymentIntentSucceded
from guillotina_stripe.interfaces import IStripePayUtility
from guillotina_stripe.utility import StripePayUtility
from guillotina_stripe.models import BillingDetails, Card
from guillotina_stripe.events import ObjectPaidEvent
from guillotina_stripe.events import ObjectFailedEvent
from guillotina.component import get_utility
from guillotina import app_settings
from guillotina.browser import get_physical_path
from guillotina import task_vars
from guillotina.event import notify
from guillotina.utils import get_database
from guillotina.utils import get_registry
from guillotina.transactions import transaction
from guillotina.utils.content import navigate_to
from guillotina.exceptions import DatabaseNotFound
from guillotina_stripe import logger


@configure.service(
    method="GET",
    name="@cards",
    permission="guillotina.ModifyContent",
    context=IMarkerProduct,
    summary="Get payment method",
)
async def get_cards(context, request):
    bhr = IProduct(context)
    if bhr.customer is None:
        return {"data": []}

    util = get_utility(IStripePayUtility)

    cards = await util.get_payment_methods(customer=bhr.customer, type="card")
    customer = await util.get_customer(bhr.customer)
    cards['customer'] = customer

    return cards


@configure.service(
    method="POST",
    name="@register-card",
    permission="guillotina.ModifyContent",
    context=IMarkerProduct,
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
                        "tax": {"type": "string"}
                    }
                }
            }
        }
    },
    summary="Register payment method",
)
async def register_paymentmethod(context, request):
    bhr = IProduct(context)
    payload = await request.json()
    billing_email = payload.get("email", None)
    if billing_email is None:
        return {"status": "error", "error": "Need email"}

    bhr.billing_email = billing_email
    util: StripePayUtility = get_utility(IStripePayUtility)
    customer = await util.set_customer(billing_email, payload.get("customer_id", None))
    customerid = customer.get("id", None)

    taxid = payload.get('tax')
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
    name="@prices",
    permission="guillotina.ModifyContent",
    context=IMarkerProduct,
    summary="View Prices",
)
async def view_prices(context, request):
    registry = await get_registry()
    settings = registry.for_interface(IStripeConfiguration)
    util = get_utility(IStripePayUtility)
    product_prices = settings['product_prices']
    if context.type_name in product_prices:
        price_info = product_prices[context.type_name]
        return {
            'prices': [
                {
                    'id': pi.get('id'),
                    'price': await util.get_price(pi.get('price'))
                } for pi in price_info
            ]
        }
    return {
        'prices': []
    }


@configure.service(
    method="POST",
    name="@pay",
    permission="guillotina.ModifyContent",
    context=IMarkerProduct,
    summary="Pay",
    validate=True,
    requestBody={
        "content": {
            "application/json": {
                "schema": {
                    "properties": {
                        "pmid": {"type": "string"},
                        "price": {"type": "string"},
                        "quantity": {"type": "number"},
                        "shipping_name": {"type": "string"},
                        "shipping_line1": {"type": "string"},
                        "shipping_line2": {"type": "string"},
                        "shipping_city": {"type": "string"},
                        "shipping_state": {"type": "string"},
                        "shipping_country": {"type": "string"},
                        "customer": {"type": "string"}
                    }
                }
            }
        }
    },
)
async def pay_bought(context, request):
    payload = await request.json()
    bhr = IProduct(context)

    customer = payload.get('customer', bhr.customer)
    if customer is None:
        raise HTTPPreconditionFailed(content={"reason": "No customer"})

    if payload.get("shipping_line1", None) in (None, ""):
        shipping = None
    else:
        shipping = {
            "name": payload.get("shipping_name", None),
            "address": {
                "line1": payload.get("shipping_line1", None),
                "line2": payload.get("shipping_line2", None),
                "postal_code": payload.get("shipping_zip", None),
                "city": payload.get("shipping_city", None),
                "state": payload.get("shipping_state", None),
                "country": payload.get("shipping_country", None)
            },
        }

    pmid = payload.get('pmid')
    coupon = payload.get("coupon")
    if pmid is None:
        raise HTTPPreconditionFailed(content={"reason": "No pmid"})

    price = payload.get('price')
    obj_type = context.type_name
    prices = app_settings["stripe"].get("products", {}).get(obj_type, [])

    if price is None and len(prices) == 1:
        price = prices[0]

    if price is None:
        raise HTTPPreconditionFailed(content={"reason": "No price"})

    quantity = int(payload.get('quantity'))
    if quantity <= 0:
        raise Exception('Invalid quantity')

    path = "/".join(get_physical_path(context))
    db = task_vars.db.get()

    util = get_utility(IStripePayUtility)
    price_obj = await util.get_price(price)

    if 'unit_amount' not in price_obj:
        return {
            'error': {
                'message': 'No price configured'
            }
        }

    total = price_obj['unit_amount'] * quantity
    charge = await util.create_paymentintent(
        description=f"{obj_type} {context.id} {quantity}",
        path=path,
        db=db.id,
        currency='eur',
        customer=customer,
        payment_method=pmid,
        amount=total,
        shipping=shipping,
        coupon=coupon
    )

    if charge.get("id") is not None:
        bhr.quantity = quantity
        bhr.price = price
        bhr.pmid = pmid
        bhr.paid = False
        bhr.charge = charge.get("id")

        if charge.get('status') == "succeeded":
            bhr.paid = True
            await notify(ObjectPaidEvent(context, charge))

        context.register()

    return charge


@configure.subscriber(for_=IPaymentIntentSucceded)
async def webhook_paid(event):
    if event.data['object'] != 'payment_intent':
        return
    
    pmid = event.data['id']
    metadata = event.data["metadata"]
    path = metadata.get("path", None)
    db_id = metadata.get("db", None)

    try:
        db = await get_database(db_id)
    except DatabaseNotFound:
        db = None

    if db is not None:
        async with transaction(db=db):
            obj = await navigate_to(db, path)
            bhr = IProduct(obj)
            if bhr.pmid != pmid:
                logger.error('Invalid pmid on charge')
                bhr.pmid = pmid
            bhr.paid = True
            obj.register()
            await notify(ObjectPaidEvent(obj, event.data))


@configure.subscriber(for_=IPaymentIntentFailed)
async def webhook_failed(event):
    if event.data['object'] != 'payment_intent':
        return
    
    pmid = event.data['id']
    metadata = event.data["metadata"]
    path = metadata.get("path", None)
    db_id = metadata.get("db", None)
    try:
        db = await get_database(db_id)
    except DatabaseNotFound:
        db = None

    if db is not None:
        async with transaction(db=db):
            obj = await navigate_to(db, path)
            bhr = IProduct(obj)
            if bhr.pmid != pmid:
                logger.error('Invalid pmid on charge')
                bhr.pmid = pmid
            bhr.paid = False
            obj.register()
            await notify(ObjectPaidEvent(obj, event.data))
