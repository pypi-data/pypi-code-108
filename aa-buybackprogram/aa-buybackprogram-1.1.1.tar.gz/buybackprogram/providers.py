import os

from esi.clients import EsiClientProvider

from . import __version__


def get_swagger_spec_path() -> str:
    """returns the path to the current swagger spec file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "swagger.json")


esi = EsiClientProvider(
    spec_file=get_swagger_spec_path(),
    app_info_text=f"aa-buyback-program v{__version__}",
)
