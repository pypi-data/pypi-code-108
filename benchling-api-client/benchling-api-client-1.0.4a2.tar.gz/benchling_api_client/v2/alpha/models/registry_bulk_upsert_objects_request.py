from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.registry_bulk_upsert_aa_sequence import RegistryBulkUpsertAaSequence
from ..models.registry_bulk_upsert_custom_entity import RegistryBulkUpsertCustomEntity
from ..models.registry_bulk_upsert_dna_sequence import RegistryBulkUpsertDnaSequence
from ..models.registry_bulk_upsert_oligo import RegistryBulkUpsertOligo
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistryBulkUpsertObjectsRequest")


@attr.s(auto_attribs=True, repr=False)
class RegistryBulkUpsertObjectsRequest:
    """  """

    _aa_sequences: Union[Unset, List[RegistryBulkUpsertAaSequence]] = UNSET
    _custom_entities: Union[Unset, List[RegistryBulkUpsertCustomEntity]] = UNSET
    _dna_oligos: Union[Unset, List[RegistryBulkUpsertOligo]] = UNSET
    _dna_sequences: Union[Unset, List[RegistryBulkUpsertDnaSequence]] = UNSET
    _rna_oligos: Union[Unset, List[RegistryBulkUpsertOligo]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("aa_sequences={}".format(repr(self._aa_sequences)))
        fields.append("custom_entities={}".format(repr(self._custom_entities)))
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        fields.append("dna_sequences={}".format(repr(self._dna_sequences)))
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        return "RegistryBulkUpsertObjectsRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aa_sequences, Unset):
            aa_sequences = []
            for aa_sequences_item_data in self._aa_sequences:
                aa_sequences_item = aa_sequences_item_data.to_dict()

                aa_sequences.append(aa_sequences_item)

        custom_entities: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._custom_entities, Unset):
            custom_entities = []
            for custom_entities_item_data in self._custom_entities:
                custom_entities_item = custom_entities_item_data.to_dict()

                custom_entities.append(custom_entities_item)

        dna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligos, Unset):
            dna_oligos = []
            for dna_oligos_item_data in self._dna_oligos:
                dna_oligos_item = dna_oligos_item_data.to_dict()

                dna_oligos.append(dna_oligos_item)

        dna_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_sequences, Unset):
            dna_sequences = []
            for dna_sequences_item_data in self._dna_sequences:
                dna_sequences_item = dna_sequences_item_data.to_dict()

                dna_sequences.append(dna_sequences_item)

        rna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_oligos, Unset):
            rna_oligos = []
            for rna_oligos_item_data in self._rna_oligos:
                rna_oligos_item = rna_oligos_item_data.to_dict()

                rna_oligos.append(rna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if aa_sequences is not UNSET:
            field_dict["aaSequences"] = aa_sequences
        if custom_entities is not UNSET:
            field_dict["customEntities"] = custom_entities
        if dna_oligos is not UNSET:
            field_dict["dnaOligos"] = dna_oligos
        if dna_sequences is not UNSET:
            field_dict["dnaSequences"] = dna_sequences
        if rna_oligos is not UNSET:
            field_dict["rnaOligos"] = rna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aa_sequences() -> Union[Unset, List[RegistryBulkUpsertAaSequence]]:
            aa_sequences = []
            _aa_sequences = d.pop("aaSequences")
            for aa_sequences_item_data in _aa_sequences or []:
                aa_sequences_item = RegistryBulkUpsertAaSequence.from_dict(aa_sequences_item_data)

                aa_sequences.append(aa_sequences_item)

            return aa_sequences

        aa_sequences = (
            get_aa_sequences()
            if "aaSequences" in d
            else cast(Union[Unset, List[RegistryBulkUpsertAaSequence]], UNSET)
        )

        def get_custom_entities() -> Union[Unset, List[RegistryBulkUpsertCustomEntity]]:
            custom_entities = []
            _custom_entities = d.pop("customEntities")
            for custom_entities_item_data in _custom_entities or []:
                custom_entities_item = RegistryBulkUpsertCustomEntity.from_dict(custom_entities_item_data)

                custom_entities.append(custom_entities_item)

            return custom_entities

        custom_entities = (
            get_custom_entities()
            if "customEntities" in d
            else cast(Union[Unset, List[RegistryBulkUpsertCustomEntity]], UNSET)
        )

        def get_dna_oligos() -> Union[Unset, List[RegistryBulkUpsertOligo]]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos or []:
                dna_oligos_item = RegistryBulkUpsertOligo.from_dict(dna_oligos_item_data)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        dna_oligos = (
            get_dna_oligos() if "dnaOligos" in d else cast(Union[Unset, List[RegistryBulkUpsertOligo]], UNSET)
        )

        def get_dna_sequences() -> Union[Unset, List[RegistryBulkUpsertDnaSequence]]:
            dna_sequences = []
            _dna_sequences = d.pop("dnaSequences")
            for dna_sequences_item_data in _dna_sequences or []:
                dna_sequences_item = RegistryBulkUpsertDnaSequence.from_dict(dna_sequences_item_data)

                dna_sequences.append(dna_sequences_item)

            return dna_sequences

        dna_sequences = (
            get_dna_sequences()
            if "dnaSequences" in d
            else cast(Union[Unset, List[RegistryBulkUpsertDnaSequence]], UNSET)
        )

        def get_rna_oligos() -> Union[Unset, List[RegistryBulkUpsertOligo]]:
            rna_oligos = []
            _rna_oligos = d.pop("rnaOligos")
            for rna_oligos_item_data in _rna_oligos or []:
                rna_oligos_item = RegistryBulkUpsertOligo.from_dict(rna_oligos_item_data)

                rna_oligos.append(rna_oligos_item)

            return rna_oligos

        rna_oligos = (
            get_rna_oligos() if "rnaOligos" in d else cast(Union[Unset, List[RegistryBulkUpsertOligo]], UNSET)
        )

        registry_bulk_upsert_objects_request = cls(
            aa_sequences=aa_sequences,
            custom_entities=custom_entities,
            dna_oligos=dna_oligos,
            dna_sequences=dna_sequences,
            rna_oligos=rna_oligos,
        )

        return registry_bulk_upsert_objects_request

    @property
    def aa_sequences(self) -> List[RegistryBulkUpsertAaSequence]:
        if isinstance(self._aa_sequences, Unset):
            raise NotPresentError(self, "aa_sequences")
        return self._aa_sequences

    @aa_sequences.setter
    def aa_sequences(self, value: List[RegistryBulkUpsertAaSequence]) -> None:
        self._aa_sequences = value

    @aa_sequences.deleter
    def aa_sequences(self) -> None:
        self._aa_sequences = UNSET

    @property
    def custom_entities(self) -> List[RegistryBulkUpsertCustomEntity]:
        if isinstance(self._custom_entities, Unset):
            raise NotPresentError(self, "custom_entities")
        return self._custom_entities

    @custom_entities.setter
    def custom_entities(self, value: List[RegistryBulkUpsertCustomEntity]) -> None:
        self._custom_entities = value

    @custom_entities.deleter
    def custom_entities(self) -> None:
        self._custom_entities = UNSET

    @property
    def dna_oligos(self) -> List[RegistryBulkUpsertOligo]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[RegistryBulkUpsertOligo]) -> None:
        self._dna_oligos = value

    @dna_oligos.deleter
    def dna_oligos(self) -> None:
        self._dna_oligos = UNSET

    @property
    def dna_sequences(self) -> List[RegistryBulkUpsertDnaSequence]:
        if isinstance(self._dna_sequences, Unset):
            raise NotPresentError(self, "dna_sequences")
        return self._dna_sequences

    @dna_sequences.setter
    def dna_sequences(self, value: List[RegistryBulkUpsertDnaSequence]) -> None:
        self._dna_sequences = value

    @dna_sequences.deleter
    def dna_sequences(self) -> None:
        self._dna_sequences = UNSET

    @property
    def rna_oligos(self) -> List[RegistryBulkUpsertOligo]:
        if isinstance(self._rna_oligos, Unset):
            raise NotPresentError(self, "rna_oligos")
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[RegistryBulkUpsertOligo]) -> None:
        self._rna_oligos = value

    @rna_oligos.deleter
    def rna_oligos(self) -> None:
        self._rna_oligos = UNSET
