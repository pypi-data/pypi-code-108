from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.feature_library import FeatureLibrary
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureLibrariesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class FeatureLibrariesPaginatedList:
    """  """

    _feature_libraries: Union[Unset, List[FeatureLibrary]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("feature_libraries={}".format(repr(self._feature_libraries)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FeatureLibrariesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        feature_libraries: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._feature_libraries, Unset):
            feature_libraries = []
            for feature_libraries_item_data in self._feature_libraries:
                feature_libraries_item = feature_libraries_item_data.to_dict()

                feature_libraries.append(feature_libraries_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if feature_libraries is not UNSET:
            field_dict["featureLibraries"] = feature_libraries
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_feature_libraries() -> Union[Unset, List[FeatureLibrary]]:
            feature_libraries = []
            _feature_libraries = d.pop("featureLibraries")
            for feature_libraries_item_data in _feature_libraries or []:
                feature_libraries_item = FeatureLibrary.from_dict(feature_libraries_item_data)

                feature_libraries.append(feature_libraries_item)

            return feature_libraries

        feature_libraries = (
            get_feature_libraries()
            if "featureLibraries" in d
            else cast(Union[Unset, List[FeatureLibrary]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        feature_libraries_paginated_list = cls(
            feature_libraries=feature_libraries,
            next_token=next_token,
        )

        feature_libraries_paginated_list.additional_properties = d
        return feature_libraries_paginated_list

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def feature_libraries(self) -> List[FeatureLibrary]:
        if isinstance(self._feature_libraries, Unset):
            raise NotPresentError(self, "feature_libraries")
        return self._feature_libraries

    @feature_libraries.setter
    def feature_libraries(self, value: List[FeatureLibrary]) -> None:
        self._feature_libraries = value

    @feature_libraries.deleter
    def feature_libraries(self) -> None:
        self._feature_libraries = UNSET

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
