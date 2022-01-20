from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.algo_execution_test_case import AlgoExecutionTestCase
from ..models.algo_test_spec_algoparams import AlgoTestSpecAlgoparams
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlgoTestSpec")


@attr.s(auto_attribs=True)
class AlgoTestSpec:
    """  """

    algo_params: AlgoTestSpecAlgoparams
    test_case: Union[Unset, AlgoExecutionTestCase] = UNSET
    timeout_seconds: Union[Unset, int] = 30
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        algo_params = self.algo_params.to_dict()

        test_case: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.test_case, Unset):
            test_case = self.test_case.to_dict()

        timeout_seconds = self.timeout_seconds

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "algoParams": algo_params,
            }
        )
        if test_case is not UNSET:
            field_dict["testCase"] = test_case
        if timeout_seconds is not UNSET:
            field_dict["timeoutSeconds"] = timeout_seconds

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        algo_params = AlgoTestSpecAlgoparams.from_dict(d.pop("algoParams"))

        _test_case = d.pop("testCase", UNSET)
        test_case: Union[Unset, AlgoExecutionTestCase]
        if isinstance(_test_case, Unset):
            test_case = UNSET
        else:
            test_case = AlgoExecutionTestCase.from_dict(_test_case)

        timeout_seconds = d.pop("timeoutSeconds", UNSET)

        algo_test_spec = cls(
            algo_params=algo_params,
            test_case=test_case,
            timeout_seconds=timeout_seconds,
        )

        algo_test_spec.additional_properties = d
        return algo_test_spec

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
