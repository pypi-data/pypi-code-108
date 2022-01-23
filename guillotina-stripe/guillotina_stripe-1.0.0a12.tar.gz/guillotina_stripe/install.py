# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.addons import Addon
from guillotina.utils import get_registry
from guillotina_stripe.interfaces import IStripeConfiguration


@configure.addon(name="stripe", title="Guillotina Stripe")
class StripeAddon(Addon):
    @classmethod
    async def install(cls, container, request):
        registry = await get_registry()
        registry.register_interface(IStripeConfiguration)
        registry.register()
