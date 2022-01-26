from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationProgressStats")


@attr.s(auto_attribs=True, repr=False)
class AutomationProgressStats:
    """ Processing progress information. """

    _rows_failed: Union[Unset, int] = UNSET
    _rows_succeeded: Union[Unset, int] = UNSET
    _rows_unprocessed: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("rows_failed={}".format(repr(self._rows_failed)))
        fields.append("rows_succeeded={}".format(repr(self._rows_succeeded)))
        fields.append("rows_unprocessed={}".format(repr(self._rows_unprocessed)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AutomationProgressStats({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rows_failed = self._rows_failed
        rows_succeeded = self._rows_succeeded
        rows_unprocessed = self._rows_unprocessed

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rows_failed is not UNSET:
            field_dict["rowsFailed"] = rows_failed
        if rows_succeeded is not UNSET:
            field_dict["rowsSucceeded"] = rows_succeeded
        if rows_unprocessed is not UNSET:
            field_dict["rowsUnprocessed"] = rows_unprocessed

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rows_failed() -> Union[Unset, int]:
            rows_failed = d.pop("rowsFailed")
            return rows_failed

        rows_failed = get_rows_failed() if "rowsFailed" in d else cast(Union[Unset, int], UNSET)

        def get_rows_succeeded() -> Union[Unset, int]:
            rows_succeeded = d.pop("rowsSucceeded")
            return rows_succeeded

        rows_succeeded = get_rows_succeeded() if "rowsSucceeded" in d else cast(Union[Unset, int], UNSET)

        def get_rows_unprocessed() -> Union[Unset, int]:
            rows_unprocessed = d.pop("rowsUnprocessed")
            return rows_unprocessed

        rows_unprocessed = (
            get_rows_unprocessed() if "rowsUnprocessed" in d else cast(Union[Unset, int], UNSET)
        )

        automation_progress_stats = cls(
            rows_failed=rows_failed,
            rows_succeeded=rows_succeeded,
            rows_unprocessed=rows_unprocessed,
        )

        automation_progress_stats.additional_properties = d
        return automation_progress_stats

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
    def rows_failed(self) -> int:
        if isinstance(self._rows_failed, Unset):
            raise NotPresentError(self, "rows_failed")
        return self._rows_failed

    @rows_failed.setter
    def rows_failed(self, value: int) -> None:
        self._rows_failed = value

    @rows_failed.deleter
    def rows_failed(self) -> None:
        self._rows_failed = UNSET

    @property
    def rows_succeeded(self) -> int:
        if isinstance(self._rows_succeeded, Unset):
            raise NotPresentError(self, "rows_succeeded")
        return self._rows_succeeded

    @rows_succeeded.setter
    def rows_succeeded(self, value: int) -> None:
        self._rows_succeeded = value

    @rows_succeeded.deleter
    def rows_succeeded(self) -> None:
        self._rows_succeeded = UNSET

    @property
    def rows_unprocessed(self) -> int:
        if isinstance(self._rows_unprocessed, Unset):
            raise NotPresentError(self, "rows_unprocessed")
        return self._rows_unprocessed

    @rows_unprocessed.setter
    def rows_unprocessed(self, value: int) -> None:
        self._rows_unprocessed = value

    @rows_unprocessed.deleter
    def rows_unprocessed(self) -> None:
        self._rows_unprocessed = UNSET
