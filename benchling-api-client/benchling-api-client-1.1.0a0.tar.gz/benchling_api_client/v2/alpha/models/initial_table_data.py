from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="InitialTableData")


@attr.s(auto_attribs=True, repr=False)
class InitialTableData:
    """  """

    _csv_data: Union[Unset, str] = UNSET
    _template_table_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("csv_data={}".format(repr(self._csv_data)))
        fields.append("template_table_id={}".format(repr(self._template_table_id)))
        return "InitialTableData({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        csv_data = self._csv_data
        template_table_id = self._template_table_id

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if csv_data is not UNSET:
            field_dict["csvData"] = csv_data
        if template_table_id is not UNSET:
            field_dict["templateTableID"] = template_table_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_csv_data() -> Union[Unset, str]:
            csv_data = d.pop("csvData")
            return csv_data

        csv_data = get_csv_data() if "csvData" in d else cast(Union[Unset, str], UNSET)

        def get_template_table_id() -> Union[Unset, str]:
            template_table_id = d.pop("templateTableID")
            return template_table_id

        template_table_id = (
            get_template_table_id() if "templateTableID" in d else cast(Union[Unset, str], UNSET)
        )

        initial_table_data = cls(
            csv_data=csv_data,
            template_table_id=template_table_id,
        )

        return initial_table_data

    @property
    def csv_data(self) -> str:
        """ blobId of data """
        if isinstance(self._csv_data, Unset):
            raise NotPresentError(self, "csv_data")
        return self._csv_data

    @csv_data.setter
    def csv_data(self, value: str) -> None:
        self._csv_data = value

    @csv_data.deleter
    def csv_data(self) -> None:
        self._csv_data = UNSET

    @property
    def template_table_id(self) -> str:
        """ Template table API id """
        if isinstance(self._template_table_id, Unset):
            raise NotPresentError(self, "template_table_id")
        return self._template_table_id

    @template_table_id.setter
    def template_table_id(self, value: str) -> None:
        self._template_table_id = value

    @template_table_id.deleter
    def template_table_id(self) -> None:
        self._template_table_id = UNSET
