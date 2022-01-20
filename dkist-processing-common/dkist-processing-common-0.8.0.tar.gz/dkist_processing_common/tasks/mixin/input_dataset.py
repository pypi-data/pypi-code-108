"""
Mixin for a WorkflowDataTaskBase subclass which implements input data set access functionality
"""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from dkist_processing_common.models.tags import Tag


@dataclass
class InputDatasetParameterValue:
    parameter_value_id: int
    parameter_value: Any = None
    parameter_value_start_date: Optional[datetime] = None


class InputDatasetMixin:
    """
    Mixin for WorkflowDataTaskBase that does x
    """

    @property
    def input_dataset_document(self):
        result = dict()
        paths: List[Path] = list(self.read(tags=[Tag.input_dataset()]))
        if not paths:
            return result
        if len(paths) > 1:
            raise ValueError("There are more than one input datasets to parse")
        p = paths[0]  # can loop in the future if multiple input datasets happen
        with p.open(mode="rb") as f:
            result = json.load(f)
        return result

    @property
    def input_dataset_frames(self) -> List[str]:
        return self.input_dataset_document.get("frames", list())

    @property
    def input_dataset_bucket(self) -> Union[str, None]:
        return self.input_dataset_document.get("bucket")

    @property
    def input_dataset_parameters(self) -> Dict[str, List[InputDatasetParameterValue]]:
        parameters = self.input_dataset_document.get("parameters", list())
        result = dict()
        for p in parameters:
            result.update(self._input_dataset_parse_parameter(p))
        return result

    def _input_dataset_parse_parameter(
        self, parameter: dict
    ) -> Dict[str, List[InputDatasetParameterValue]]:
        name: str = parameter["parameterName"]
        raw_values: List[dict] = parameter["parameterValues"]
        values = self._input_dataset_parse_parameter_values(raw_values=raw_values)
        return {name: values}

    def _input_dataset_parse_parameter_values(
        self, raw_values: List[Dict[str, Any]]
    ) -> List[InputDatasetParameterValue]:
        values = list()
        for v in raw_values:
            parsed_value = InputDatasetParameterValue(parameter_value_id=v["parameterValueId"])
            parsed_value.parameter_value = self._input_dataset_parse_parameter_value(
                raw_parameter_value=v["parameterValue"]
            )
            if d := v.get("parameterValueStartDate"):
                parsed_value.parameter_value_start_date = datetime.fromisoformat(d)
            else:
                parsed_value.parameter_value_start_date = datetime(1, 1, 1)
            values.append(parsed_value)
        return values

    @staticmethod
    def _input_dataset_parse_parameter_value(raw_parameter_value: str) -> Any:
        return json.loads(raw_parameter_value)
