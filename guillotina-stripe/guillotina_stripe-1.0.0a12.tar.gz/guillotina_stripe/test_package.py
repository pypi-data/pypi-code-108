# this is for testing.py, do not import into other modules
from guillotina_stripe.interfaces import IObjectFailedEvent, IObjectPaidEvent, IObjectTrailingEvent
from guillotina import configure
from guillotina.content import Item
from guillotina.content import Folder
from guillotina.interfaces import IItem
from guillotina.interfaces import IFolder
from guillotina.schema import Bool

app_settings = {"applications": ["guillotina"]}


class ICustomCardsType(IItem):
    pass


@configure.contenttype(
    type_name="CustomCardsType",
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina_stripe.interfaces.IStripeCards",
    ],
    schema=ICustomCardsType,
)
class CustomCardsType(Item):
    pass


class ICustomProductType(IItem):
    ispaid = Bool(title="Is paid", default=False, required=False)


@configure.contenttype(
    type_name="CustomProductType",
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina_stripe.interfaces.IProduct",
    ],
    schema=ICustomProductType,
)
class CustomProductType(Item):
    pass


class ICustomSubscriptionType(IFolder):

    subscribed = Bool(title="Subscribed", default=False, required=False)


@configure.contenttype(
    type_name="CustomSubscriptionType",
    behaviors=[
        "guillotina.behaviors.dublincore.IDublinCore",
        "guillotina_stripe.interfaces.ISubscription",
    ],
    schema=ICustomSubscriptionType,
)
class CustomSubscriptionType(Folder):
    pass


@configure.subscriber(
    for_=(ICustomSubscriptionType, IObjectPaidEvent)
)
def subscribed(obj, event):
    obj.subscribed = True
    obj.register()


@configure.subscriber(
    for_=(ICustomSubscriptionType, IObjectTrailingEvent)
)
def subscribed_trailing(obj, event):
    obj.subscribed = True
    obj.register()


@configure.subscriber(
    for_=(ICustomSubscriptionType, IObjectFailedEvent)
)
def unsubscribed(obj, event):
    obj.subscribed = False
    obj.register()


@configure.subscriber(
    for_=(ICustomProductType, IObjectPaidEvent)
)
def subscribed(obj, event):
    obj.ispaid = True
    obj.register()


@configure.subscriber(
    for_=(ICustomProductType, IObjectFailedEvent)
)
def unsubscribed(obj, event):
    obj.ispaid = False
    obj.register()
