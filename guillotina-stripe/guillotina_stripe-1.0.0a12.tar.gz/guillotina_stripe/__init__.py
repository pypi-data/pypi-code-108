from guillotina import configure
import logging

logger = logging.getLogger('guillotina_stripe')

app_settings = {
    "load_utilities": {
        "stripe": {
            "provides": "guillotina_stripe.interfaces.IStripePayUtility",
            "factory": "guillotina_stripe.utility.StripePayUtility",
            "settings": {
                "secret": "",
                "signing": ""
            },
        }
    },
    "stripe": {
        "subscriptions": {},
        "products": {},
    }
}


def includeme(root, settings):
    configure.scan("guillotina_stripe.utility")
    configure.scan("guillotina_stripe.behavior")
    configure.scan("guillotina_stripe.install")
    configure.scan("guillotina_stripe.events")
    configure.scan("guillotina_stripe.subscription")
    configure.scan("guillotina_stripe.product")
    configure.scan("guillotina_stripe.webhook")
    configure.scan("guillotina_stripe.cards")
