from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.dna_alignment_base_algorithm import DnaAlignmentBaseAlgorithm
from ..models.dna_alignment_base_files_item import DnaAlignmentBaseFilesItem
from ..models.dna_template_alignment_file import DnaTemplateAlignmentFile
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaAlignmentBase")


@attr.s(auto_attribs=True, repr=False)
class DnaAlignmentBase:
    """  """

    _algorithm: DnaAlignmentBaseAlgorithm
    _files: List[Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]]
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("algorithm={}".format(repr(self._algorithm)))
        fields.append("files={}".format(repr(self._files)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaAlignmentBase({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        algorithm = self._algorithm.value

        files = []
        for files_item_data in self._files:
            if isinstance(files_item_data, UnknownType):
                files_item = files_item_data.value
            elif isinstance(files_item_data, DnaAlignmentBaseFilesItem):
                files_item = files_item_data.to_dict()

            else:
                files_item = files_item_data.to_dict()

            files.append(files_item)

        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "algorithm": algorithm,
                "files": files,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_algorithm() -> DnaAlignmentBaseAlgorithm:
            _algorithm = d.pop("algorithm")
            try:
                algorithm = DnaAlignmentBaseAlgorithm(_algorithm)
            except ValueError:
                algorithm = DnaAlignmentBaseAlgorithm.of_unknown(_algorithm)

            return algorithm

        algorithm = get_algorithm() if "algorithm" in d else cast(DnaAlignmentBaseAlgorithm, UNSET)

        def get_files() -> List[Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]]:
            files = []
            _files = d.pop("files")
            for files_item_data in _files:

                def _parse_files_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]:
                    files_item: Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        files_item = DnaAlignmentBaseFilesItem.from_dict(data)

                        return files_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        files_item = DnaTemplateAlignmentFile.from_dict(data)

                        return files_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                files_item = _parse_files_item(files_item_data)

                files.append(files_item)

            return files

        files = (
            get_files()
            if "files" in d
            else cast(List[Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]], UNSET)
        )

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        dna_alignment_base = cls(
            algorithm=algorithm,
            files=files,
            name=name,
        )

        dna_alignment_base.additional_properties = d
        return dna_alignment_base

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
    def algorithm(self) -> DnaAlignmentBaseAlgorithm:
        if isinstance(self._algorithm, Unset):
            raise NotPresentError(self, "algorithm")
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: DnaAlignmentBaseAlgorithm) -> None:
        self._algorithm = value

    @property
    def files(self) -> List[Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]]:
        if isinstance(self._files, Unset):
            raise NotPresentError(self, "files")
        return self._files

    @files.setter
    def files(
        self, value: List[Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]]
    ) -> None:
        self._files = value

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
