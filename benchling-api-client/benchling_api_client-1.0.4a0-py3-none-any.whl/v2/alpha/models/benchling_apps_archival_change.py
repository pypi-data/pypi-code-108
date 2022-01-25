from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppsArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of apps that were archived / unarchived."""

    _app_ids: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("app_ids={}".format(repr(self._app_ids)))
        return "BenchlingAppsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._app_ids, Unset):
            app_ids = self._app_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if app_ids is not UNSET:
            field_dict["appIds"] = app_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_app_ids() -> Union[Unset, List[str]]:
            app_ids = cast(List[str], d.pop("appIds"))

            return app_ids

        app_ids = get_app_ids() if "appIds" in d else cast(Union[Unset, List[str]], UNSET)

        benchling_apps_archival_change = cls(
            app_ids=app_ids,
        )

        return benchling_apps_archival_change

    @property
    def app_ids(self) -> List[str]:
        if isinstance(self._app_ids, Unset):
            raise NotPresentError(self, "app_ids")
        return self._app_ids

    @app_ids.setter
    def app_ids(self, value: List[str]) -> None:
        self._app_ids = value

    @app_ids.deleter
    def app_ids(self) -> None:
        self._app_ids = UNSET
