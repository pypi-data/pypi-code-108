from guillotina.async_util import IAsyncUtility
from zope.interface import Interface
from guillotina import schema
from guillotina.directives import read_permission
from guillotina.directives import write_permission
from guillotina.directives import index_field
from zope.interface import interfaces
import json

PRICES = json.dumps(
    {
        "type": "object",
        "properties": {},
        "additionalProperties": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"price": {"type": "string"}, "id": {"type": "string"}},
            },
        },
    }
)


class IStripePayUtility(IAsyncUtility):
    pass


# EVENTS
class IObjectPaidEvent(interfaces.IObjectEvent):
    """Object paid event"""


class IObjectFailedEvent(interfaces.IObjectEvent):
    """Object failed event"""


class IObjectTrailingEvent(interfaces.IObjectEvent):
    """Object trailing event"""


class IInvoicePaidEvent(Interface):
    pass


class IInvoicePaymentFailed(Interface):
    pass


class IInvoiceFinalized(Interface):
    pass


class IPaymentIntentSucceded(Interface):
    pass


class IPaymentIntentFailed(Interface):
    pass


class ICustomerSubscriptionUpdated(Interface):
    pass


class ICustomerSubscriptionDeleted(Interface):
    pass


class ICustomerSubscriptionTrialWillEnd(Interface):
    pass


class IMarkerProduct(Interface):
    """Marker interface for content with product information."""


class IProduct(Interface):

    write_permission(paid="guillotina.Nobody")
    paid = schema.Bool(title="Is Paid?", required=False, default=False)

    write_permission(charge="guillotina.Nobody")
    read_permission(charge="guillotina.Owner")
    charge = schema.Text(title="Stripe charge", required=False)

    write_permission(customer="guillotina.Nobody")
    read_permission(customer="guillotina.Owner")
    customer = schema.Text(title="Stripe customer", required=False)

    write_permission(billing_email="guillotina.Nobody")
    read_permission(billing_email="guillotina.Owner")
    billing_email = schema.Text(title="Billing email", required=False)

    write_permission(pmid="guillotina.Nobody")
    read_permission(pmid="guillotina.Owner")
    pmid = schema.Text(title="Stripe pmid", required=False)

    write_permission(quantity="guillotina.Nobody")
    read_permission(quantity="guillotina.Owner")
    quantity = schema.Int(title="Quantity", required=False)

    write_permission(price="guillotina.Nobody")
    read_permission(price="guillotina.Owner")
    price = schema.Int(title="Stripe price", required=False)


class IMarkerSubscription(Interface):
    """Marker interface for content with subscription."""


class ISubscription(Interface):

    write_permission(customer="guillotina.Nobody")
    read_permission(customer="guillotina.Owner")
    customer = schema.Text(title="Stripe customer", required=False)

    write_permission(billing_email="guillotina.Nobody")
    read_permission(billing_email="guillotina.Owner")
    billing_email = schema.Text(title="Billing email", required=False)

    write_permission(subscription="guillotina.Nobody")
    read_permission(subscription="guillotina.Owner")
    subscription = schema.Text(title="Stripe subscription", required=False)

    write_permission(pmid="guillotina.Nobody")
    read_permission(pmid="guillotina.Owner")
    pmid = schema.Text(title="Stripe pmid", required=False)

    write_permission(current_period_end="guillotina.Nobody")
    read_permission(current_period_end="guillotina.Owner")
    current_period_end = schema.Int(
        title="Stripe subscription", required=False)

    write_permission(current_period_start="guillotina.Nobody")
    read_permission(current_period_start="guillotina.Owner")
    current_period_start = schema.Int(
        title="Stripe subscription", required=False)

    write_permission(price_id="guillotina.Nobody")
    read_permission(price_id="guillotina.Owner")
    index_field("creators", type="keyword")
    price_ids = schema.List(
        title="Stripe subscription",
        required=False,
        value_type=schema.TextLine(title="price", required=False),
    )

    write_permission(price_id="guillotina.Nobody")
    read_permission(price_id="guillotina.Owner")
    paid = schema.Bool(title="Paid", required=False, default=False)

    write_permission(trailing="guillotina.Nobody")
    read_permission(trailing="guillotina.Owner")
    trailing = schema.Bool(title="Trailing", required=False, default=False)

    write_permission(cancel_at_period_end="guillotina.Nobody")
    read_permission(cancel_at_period_end="guillotina.Owner")
    cancel_at_period_end = schema.Bool(
        title="Cancel at period end", required=False, default=False)

    write_permission(trial_end="guillotina.Nobody")
    read_permission(trial_end="guillotina.Owner")
    trial_end = schema.Int(title="Trial end", required=False, default=False)


class IStripeConfiguration(Interface):

    product_prices = schema.JSONField(
        title="Product prices definition", required=False, schema=PRICES
    )

    subscription_prices = schema.JSONField(
        title="Subscription prices definition", required=False, schema=PRICES
    )


class IMarkerCards(Interface):
    """Marker interface for content with cards."""


class IStripeCards(Interface):

    write_permission(customer="guillotina.Nobody")
    read_permission(customer="guillotina.Owner")
    customer = schema.Text(title="Stripe customer", required=False)

    write_permission(billing_email="guillotina.Nobody")
    read_permission(billing_email="guillotina.Owner")
    billing_email = schema.Text(title="Billing email", required=False)
