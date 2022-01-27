from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="AlgoTestError")


@attr.s(auto_attribs=True)
class AlgoTestError:
    """  """

    error_type: str
    details: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        error_type = self.error_type
        details = self.details

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "errorType": error_type,
                "details": details,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        error_type = d.pop("errorType")

        details = d.pop("details")

        algo_test_error = cls(
            error_type=error_type,
            details=details,
        )

        algo_test_error.additional_properties = d
        return algo_test_error

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
