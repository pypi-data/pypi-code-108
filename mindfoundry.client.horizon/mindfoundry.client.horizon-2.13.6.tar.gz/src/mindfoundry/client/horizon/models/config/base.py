import abc
import uuid
from dataclasses import dataclass
from typing import Any, List, Optional, Union

from mindfoundry.client.horizon.generated.models import IndividualDataset


class ValidatedConfig(abc.ABC):
    @abc.abstractmethod
    def validate(self) -> None:
        pass


@dataclass
class ModelConfig(ValidatedConfig):
    name: Optional[str] = None
    """
    Name of the model. Although not necessary, it is advised to give models a name so that
    multiple models can be easily told apart. If not provided, the model will be given a
    random name.
    """

    inputs: Optional[List[str]] = None
    """
    List of column names to be used as features for the forecasting. Only the specified columns
    will be processed and analyzed. Any column that is not in this list will be ignored.
    By default, all columns will be used.
    Mutually exclusive with `exclude_from_input` (use one or the other but not both).
    """

    exclude_from_input: Optional[List[str]] = None
    """
    List of column names to be ignored in the forecasting. Every other column that is present in
    the data but not specified in this list will be used as a feature.
    By default, no column will be excluded.
    Mutually exclusive with `inputs` (use one or the other but not both).
    """

    def validate(self) -> None:
        assert self.inputs is None or self.exclude_from_input is None, (
            "inputs and exclude_from_input cannot be specified together at the same time."
            "Use one or the other"
        )

        assert_not_empty_if_provided("name", self.name)
        assert_not_empty_if_provided("inputs", self.inputs, True)
        assert_not_empty_if_provided("exclude_from_input", self.exclude_from_input, True)

    def resolve_dataset_name(self) -> str:
        code = str(uuid.uuid4())
        return self.name or f"Dataset {code[:8]}"

    def resolve_pipeline_name(self) -> str:
        code = str(uuid.uuid4())
        return self.name or f"Pipeline {code[:8]}"

    def resolve_active_columns(self, dataset: IndividualDataset) -> List[int]:
        if self.inputs is not None:
            assert_no_missing_columns(dataset, self.inputs)
            return [cp.id for cp in dataset.analysis if cp.name in self.inputs]

        if self.exclude_from_input is not None:
            assert_no_missing_columns(dataset, self.exclude_from_input)
            return [cp.id for cp in dataset.analysis if cp.name not in self.exclude_from_input]

        return [cp.id for cp in dataset.analysis]


def assert_not_empty_if_provided(
    field: str,
    value: Optional[Union[str, List[Any]]] = None,
    must_be_list: Optional[bool] = False,
) -> None:
    if value is not None:
        assert len(value) > 0, f"{field} cannot be empty"
        if must_be_list:
            assert isinstance(value, List), f"{field} must be a List"


def assert_no_missing_columns(dataset: IndividualDataset, wanted_names: List[str]) -> None:
    existing_column_names = [cp.name for cp in dataset.analysis]
    missing_columns = [name for name in wanted_names if name not in existing_column_names]
    assert len(missing_columns) == 0, (
        "Some column names were used that are not actually present in the dataset. "
        f"Please review the following: {missing_columns}"
    )
