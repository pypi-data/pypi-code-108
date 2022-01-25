from levo_commons.models import Module
from levo_commons.providers import Provider

from .bespoke import BespokeProvider
from .schemathesis import SchemathesisProvider
from .zaproxy import ZaproxyProvider


def get_provider_for_module(name: str) -> Provider:
    try:
        return {
            Module.BESPOKE: BespokeProvider(),
            Module.SCHEMATHESIS: SchemathesisProvider(),
            Module.ZAPROXY: ZaproxyProvider(),
        }[Module[name]]
    except KeyError:
        raise Exception(f"Unrecognized module: {name}")
