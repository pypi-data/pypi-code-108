from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.codon_usage_table import CodonUsageTable
from ..types import UNSET, Unset

T = TypeVar("T", bound="CodonUsageTablesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class CodonUsageTablesPaginatedList:
    """  """

    _codon_usage_tables: Union[Unset, List[CodonUsageTable]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("codon_usage_tables={}".format(repr(self._codon_usage_tables)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "CodonUsageTablesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        codon_usage_tables: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._codon_usage_tables, Unset):
            codon_usage_tables = []
            for codon_usage_tables_item_data in self._codon_usage_tables:
                codon_usage_tables_item = codon_usage_tables_item_data.to_dict()

                codon_usage_tables.append(codon_usage_tables_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if codon_usage_tables is not UNSET:
            field_dict["codonUsageTables"] = codon_usage_tables
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_codon_usage_tables() -> Union[Unset, List[CodonUsageTable]]:
            codon_usage_tables = []
            _codon_usage_tables = d.pop("codonUsageTables")
            for codon_usage_tables_item_data in _codon_usage_tables or []:
                codon_usage_tables_item = CodonUsageTable.from_dict(codon_usage_tables_item_data)

                codon_usage_tables.append(codon_usage_tables_item)

            return codon_usage_tables

        codon_usage_tables = (
            get_codon_usage_tables()
            if "codonUsageTables" in d
            else cast(Union[Unset, List[CodonUsageTable]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        codon_usage_tables_paginated_list = cls(
            codon_usage_tables=codon_usage_tables,
            next_token=next_token,
        )

        return codon_usage_tables_paginated_list

    @property
    def codon_usage_tables(self) -> List[CodonUsageTable]:
        if isinstance(self._codon_usage_tables, Unset):
            raise NotPresentError(self, "codon_usage_tables")
        return self._codon_usage_tables

    @codon_usage_tables.setter
    def codon_usage_tables(self, value: List[CodonUsageTable]) -> None:
        self._codon_usage_tables = value

    @codon_usage_tables.deleter
    def codon_usage_tables(self) -> None:
        self._codon_usage_tables = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
