from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.dna_alignment_base_algorithm import DnaAlignmentBaseAlgorithm
from ..models.dna_alignment_base_files_item import DnaAlignmentBaseFilesItem
from ..models.dna_consensus_alignment_create_new_sequence import DnaConsensusAlignmentCreateNewSequence
from ..models.dna_template_alignment_file import DnaTemplateAlignmentFile
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaConsensusAlignmentCreate")


@attr.s(auto_attribs=True, repr=False)
class DnaConsensusAlignmentCreate:
    """  """

    _algorithm: DnaAlignmentBaseAlgorithm
    _files: List[Union[DnaAlignmentBaseFilesItem, DnaTemplateAlignmentFile, UnknownType]]
    _new_sequence: Union[Unset, DnaConsensusAlignmentCreateNewSequence] = UNSET
    _sequence_id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("algorithm={}".format(repr(self._algorithm)))
        fields.append("files={}".format(repr(self._files)))
        fields.append("new_sequence={}".format(repr(self._new_sequence)))
        fields.append("sequence_id={}".format(repr(self._sequence_id)))
        fields.append("name={}".format(repr(self._name)))
        return "DnaConsensusAlignmentCreate({})".format(", ".join(fields))

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

        new_sequence: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._new_sequence, Unset):
            new_sequence = self._new_sequence.to_dict()

        sequence_id = self._sequence_id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "algorithm": algorithm,
                "files": files,
            }
        )
        if new_sequence is not UNSET:
            field_dict["newSequence"] = new_sequence
        if sequence_id is not UNSET:
            field_dict["sequenceId"] = sequence_id
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

        def get_new_sequence() -> Union[Unset, DnaConsensusAlignmentCreateNewSequence]:
            new_sequence: Union[Unset, DnaConsensusAlignmentCreateNewSequence] = UNSET
            _new_sequence = d.pop("newSequence")
            if not isinstance(_new_sequence, Unset):
                new_sequence = DnaConsensusAlignmentCreateNewSequence.from_dict(_new_sequence)

            return new_sequence

        new_sequence = (
            get_new_sequence()
            if "newSequence" in d
            else cast(Union[Unset, DnaConsensusAlignmentCreateNewSequence], UNSET)
        )

        def get_sequence_id() -> Union[Unset, str]:
            sequence_id = d.pop("sequenceId")
            return sequence_id

        sequence_id = get_sequence_id() if "sequenceId" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        dna_consensus_alignment_create = cls(
            algorithm=algorithm,
            files=files,
            new_sequence=new_sequence,
            sequence_id=sequence_id,
            name=name,
        )

        return dna_consensus_alignment_create

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
    def new_sequence(self) -> DnaConsensusAlignmentCreateNewSequence:
        if isinstance(self._new_sequence, Unset):
            raise NotPresentError(self, "new_sequence")
        return self._new_sequence

    @new_sequence.setter
    def new_sequence(self, value: DnaConsensusAlignmentCreateNewSequence) -> None:
        self._new_sequence = value

    @new_sequence.deleter
    def new_sequence(self) -> None:
        self._new_sequence = UNSET

    @property
    def sequence_id(self) -> str:
        if isinstance(self._sequence_id, Unset):
            raise NotPresentError(self, "sequence_id")
        return self._sequence_id

    @sequence_id.setter
    def sequence_id(self, value: str) -> None:
        self._sequence_id = value

    @sequence_id.deleter
    def sequence_id(self) -> None:
        self._sequence_id = UNSET

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
