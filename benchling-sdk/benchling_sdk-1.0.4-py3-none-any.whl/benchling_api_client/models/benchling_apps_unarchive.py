from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppsUnarchive")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppsUnarchive:
    """  """

    _app_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("app_ids={}".format(repr(self._app_ids)))
        return "BenchlingAppsUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app_ids = self._app_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "appIds": app_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_app_ids() -> List[str]:
            app_ids = cast(List[str], d.pop("appIds"))

            return app_ids

        app_ids = get_app_ids() if "appIds" in d else cast(List[str], UNSET)

        benchling_apps_unarchive = cls(
            app_ids=app_ids,
        )

        return benchling_apps_unarchive

    @property
    def app_ids(self) -> List[str]:
        """ Array of app IDs """
        if isinstance(self._app_ids, Unset):
            raise NotPresentError(self, "app_ids")
        return self._app_ids

    @app_ids.setter
    def app_ids(self, value: List[str]) -> None:
        self._app_ids = value
