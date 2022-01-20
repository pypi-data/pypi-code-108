from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutoAnnotateDnaSequences")


@attr.s(auto_attribs=True, repr=False)
class AutoAnnotateDnaSequences:
    """  """

    _dna_sequence_ids: List[str]
    _feature_library_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("dna_sequence_ids={}".format(repr(self._dna_sequence_ids)))
        fields.append("feature_library_ids={}".format(repr(self._feature_library_ids)))
        return "AutoAnnotateDnaSequences({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequence_ids = self._dna_sequence_ids

        feature_library_ids = self._feature_library_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaSequenceIds": dna_sequence_ids,
                "featureLibraryIds": feature_library_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_sequence_ids() -> List[str]:
            dna_sequence_ids = cast(List[str], d.pop("dnaSequenceIds"))

            return dna_sequence_ids

        dna_sequence_ids = get_dna_sequence_ids() if "dnaSequenceIds" in d else cast(List[str], UNSET)

        def get_feature_library_ids() -> List[str]:
            feature_library_ids = cast(List[str], d.pop("featureLibraryIds"))

            return feature_library_ids

        feature_library_ids = (
            get_feature_library_ids() if "featureLibraryIds" in d else cast(List[str], UNSET)
        )

        auto_annotate_dna_sequences = cls(
            dna_sequence_ids=dna_sequence_ids,
            feature_library_ids=feature_library_ids,
        )

        return auto_annotate_dna_sequences

    @property
    def dna_sequence_ids(self) -> List[str]:
        """ Array of DNA sequence IDs. """
        if isinstance(self._dna_sequence_ids, Unset):
            raise NotPresentError(self, "dna_sequence_ids")
        return self._dna_sequence_ids

    @dna_sequence_ids.setter
    def dna_sequence_ids(self, value: List[str]) -> None:
        self._dna_sequence_ids = value

    @property
    def feature_library_ids(self) -> List[str]:
        """ Array of feature library IDs. """
        if isinstance(self._feature_library_ids, Unset):
            raise NotPresentError(self, "feature_library_ids")
        return self._feature_library_ids

    @feature_library_ids.setter
    def feature_library_ids(self, value: List[str]) -> None:
        self._feature_library_ids = value
