from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.algo_output_signal import AlgoOutputSignal
from ..models.algo_test_error import AlgoTestError
from ..models.algo_test_spec import AlgoTestSpec
from ..models.trading_algo import TradingAlgo

T = TypeVar("T", bound="AlgoTestResult")


@attr.s(auto_attribs=True)
class AlgoTestResult:
    """  """

    algo: TradingAlgo
    spec: AlgoTestSpec
    output: List[AlgoOutputSignal]
    stdout: str
    errors: List[AlgoTestError]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        algo = self.algo.to_dict()

        spec = self.spec.to_dict()

        output = []
        for output_item_data in self.output:
            output_item = output_item_data.to_dict()

            output.append(output_item)

        stdout = self.stdout
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()

            errors.append(errors_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "algo": algo,
                "spec": spec,
                "output": output,
                "stdout": stdout,
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        algo = TradingAlgo.from_dict(d.pop("algo"))

        spec = AlgoTestSpec.from_dict(d.pop("spec"))

        output = []
        _output = d.pop("output")
        for output_item_data in _output:
            output_item = AlgoOutputSignal.from_dict(output_item_data)

            output.append(output_item)

        stdout = d.pop("stdout")

        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = AlgoTestError.from_dict(errors_item_data)

            errors.append(errors_item)

        algo_test_result = cls(
            algo=algo,
            spec=spec,
            output=output,
            stdout=stdout,
            errors=errors,
        )

        algo_test_result.additional_properties = d
        return algo_test_result

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
