from zope.interface import implementer
from guillotina.events import ObjectEvent
from guillotina_stripe.interfaces import IObjectFailedEvent, IObjectTrailingEvent
from guillotina_stripe.interfaces import IObjectPaidEvent
from guillotina_stripe.interfaces import IInvoicePaidEvent
from guillotina_stripe.interfaces import IInvoicePaymentFailed
from guillotina_stripe.interfaces import IInvoiceFinalized
from guillotina_stripe.interfaces import IPaymentIntentSucceded
from guillotina_stripe.interfaces import IPaymentIntentFailed
from guillotina_stripe.interfaces import ICustomerSubscriptionUpdated
from guillotina_stripe.interfaces import ICustomerSubscriptionDeleted
from guillotina_stripe.interfaces import ICustomerSubscriptionTrialWillEnd


@implementer(IObjectPaidEvent)
class ObjectPaidEvent(ObjectEvent):
    def __init__(self, object, data=None):
        self.object = object
        self.data = data or {}


@implementer(IObjectTrailingEvent)
class ObjectTrailingEvent(ObjectEvent):
    def __init__(self, object, data=None):
        self.object = object
        self.data = data or {}


@implementer(IObjectFailedEvent)
class ObjectFailedEvent(ObjectEvent):
    def __init__(self, object, data=None):
        self.object = object
        self.data = data or {}


@implementer(IInvoicePaidEvent)
class InvoicePaidEvent:
    def __init__(self, data):
        self.data = data

@implementer(IInvoicePaymentFailed)
class InvoicePaymentFailed:
    def __init__(self, data):
        self.data = data

@implementer(IInvoiceFinalized)
class InvoiceFinalized:
    def __init__(self, data):
        self.data = data

@implementer(IPaymentIntentSucceded)
class PaymentIntentSucceded:
    def __init__(self, data):
        self.data = data

@implementer(IPaymentIntentFailed)
class PaymentIntentFailed:
    def __init__(self, data):
        self.data = data

@implementer(ICustomerSubscriptionUpdated)
class CustomerSubscriptionUpdated:
    def __init__(self, data):
        self.data = data

@implementer(ICustomerSubscriptionDeleted)
class CustomerSubscriptionDeleted:
    def __init__(self, data):
        self.data = data

@implementer(ICustomerSubscriptionTrialWillEnd)
class CustomerSubscriptionTrialWillEnd:
    def __init__(self, data):
        self.data = data
