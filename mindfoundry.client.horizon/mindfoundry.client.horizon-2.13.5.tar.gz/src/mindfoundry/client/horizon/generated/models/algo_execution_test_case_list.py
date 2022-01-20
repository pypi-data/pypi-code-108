from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.algo_execution_test_case import AlgoExecutionTestCase

T = TypeVar("T", bound="AlgoExecutionTestCaseList")


@attr.s(auto_attribs=True)
class AlgoExecutionTestCaseList:
    """  """

    test_cases: List[AlgoExecutionTestCase]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        test_cases = []
        for test_cases_item_data in self.test_cases:
            test_cases_item = test_cases_item_data.to_dict()

            test_cases.append(test_cases_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "testCases": test_cases,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        test_cases = []
        _test_cases = d.pop("testCases")
        for test_cases_item_data in _test_cases:
            test_cases_item = AlgoExecutionTestCase.from_dict(test_cases_item_data)

            test_cases.append(test_cases_item)

        algo_execution_test_case_list = cls(
            test_cases=test_cases,
        )

        algo_execution_test_case_list.additional_properties = d
        return algo_execution_test_case_list

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
