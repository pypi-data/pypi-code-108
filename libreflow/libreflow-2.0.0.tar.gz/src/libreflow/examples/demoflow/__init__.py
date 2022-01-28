from kabaret import flow

from libreflow import baseflow
from .lib import AssetLib
from .film import Seasons, Shot


class Project(flow.Object, flow.InjectionProvider):

    admin = flow.Child(baseflow.Admin)
    asset_library = flow.Child(AssetLib)
    seasons = flow.Child(Seasons)

    _RUNNERS_FACTORY = None

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == "libreflow.baseflow.film.Shot":
            return Shot
