from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.benchling_app import BenchlingApp
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppsPaginatedList:
    """  """

    _apps: Union[Unset, List[BenchlingApp]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("apps={}".format(repr(self._apps)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "BenchlingAppsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        apps: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._apps, Unset):
            apps = []
            for apps_item_data in self._apps:
                apps_item = apps_item_data.to_dict()

                apps.append(apps_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if apps is not UNSET:
            field_dict["apps"] = apps
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_apps() -> Union[Unset, List[BenchlingApp]]:
            apps = []
            _apps = d.pop("apps")
            for apps_item_data in _apps or []:
                apps_item = BenchlingApp.from_dict(apps_item_data)

                apps.append(apps_item)

            return apps

        apps = get_apps() if "apps" in d else cast(Union[Unset, List[BenchlingApp]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        benchling_apps_paginated_list = cls(
            apps=apps,
            next_token=next_token,
        )

        return benchling_apps_paginated_list

    @property
    def apps(self) -> List[BenchlingApp]:
        if isinstance(self._apps, Unset):
            raise NotPresentError(self, "apps")
        return self._apps

    @apps.setter
    def apps(self, value: List[BenchlingApp]) -> None:
        self._apps = value

    @apps.deleter
    def apps(self) -> None:
        self._apps = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
