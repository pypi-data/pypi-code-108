from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.column_passport import ColumnPassport
from ..models.dataset import Dataset

T = TypeVar("T", bound="IndividualDataset")


@attr.s(auto_attribs=True)
class IndividualDataset:
    """ Dataset summary info and analysis of its columns  """

    analysis: List[ColumnPassport]
    summary: Dataset
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        analysis = []
        for analysis_item_data in self.analysis:
            analysis_item = analysis_item_data.to_dict()

            analysis.append(analysis_item)

        summary = self.summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "analysis": analysis,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        analysis = []
        _analysis = d.pop("analysis")
        for analysis_item_data in _analysis:
            analysis_item = ColumnPassport.from_dict(analysis_item_data)

            analysis.append(analysis_item)

        summary = Dataset.from_dict(d.pop("summary"))

        individual_dataset = cls(
            analysis=analysis,
            summary=summary,
        )

        individual_dataset.additional_properties = d
        return individual_dataset

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
