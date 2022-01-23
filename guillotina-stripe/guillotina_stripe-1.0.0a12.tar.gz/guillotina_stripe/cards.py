from guillotina_stripe.utility import StripePayUtility
from guillotina_stripe.models import BillingDetails, Card
from guillotina_stripe.interfaces import (
    IMarkerCards,
    IStripeCards,
)
from guillotina import configure
from guillotina.component import get_utility
from guillotina_stripe.interfaces import IStripePayUtility


@configure.service(
    method="GET",
    name="@cards",
    permission="guillotina.ModifyContent",
    context=IMarkerCards,
    summary="Get payment method",
)
async def get_cards(context, request):
    bhr = IStripeCards(context)
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
    context=IMarkerCards,
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
    bhr = IStripeCards(context)
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
    if pmid is not None:
        await util.attach_payment_method(pmid, customerid)
        await util.modify_customer(pmid, customerid)
    context.register()
    result['customer'] = customerid
    return result
