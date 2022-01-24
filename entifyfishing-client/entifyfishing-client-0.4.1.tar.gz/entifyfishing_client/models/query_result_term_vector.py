from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.language import Language
from ..models.multilingual_term import MultilingualTerm
from ..models.weighted_term_entities import WeightedTermEntities
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryResultTermVector")


@attr.s(auto_attribs=True)
class QueryResultTermVector:
    """ """

    term_vector: List[WeightedTermEntities]
    software: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    date: Union[Unset, str] = UNSET
    runtime: Union[Unset, int] = UNSET
    nbest: Union[Unset, bool] = UNSET
    language: Union[Unset, Language] = UNSET
    multilingual: Union[Unset, List[MultilingualTerm]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        term_vector = []
        for term_vector_item_data in self.term_vector:
            term_vector_item = term_vector_item_data.to_dict()

            term_vector.append(term_vector_item)

        software = self.software
        version = self.version
        date = self.date
        runtime = self.runtime
        nbest = self.nbest
        language: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.language, Unset):
            language = self.language.to_dict()

        multilingual: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.multilingual, Unset):
            multilingual = []
            for multilingual_item_data in self.multilingual:
                multilingual_item = multilingual_item_data.to_dict()

                multilingual.append(multilingual_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "termVector": term_vector,
            }
        )
        if software is not UNSET:
            field_dict["software"] = software
        if version is not UNSET:
            field_dict["version"] = version
        if date is not UNSET:
            field_dict["date"] = date
        if runtime is not UNSET:
            field_dict["runtime"] = runtime
        if nbest is not UNSET:
            field_dict["nbest"] = nbest
        if language is not UNSET:
            field_dict["language"] = language
        if multilingual is not UNSET:
            field_dict["multilingual"] = multilingual

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        term_vector = []
        _term_vector = d.pop("termVector")
        for term_vector_item_data in _term_vector:
            term_vector_item = WeightedTermEntities.from_dict(term_vector_item_data)

            term_vector.append(term_vector_item)

        software = d.pop("software", UNSET)

        version = d.pop("version", UNSET)

        date = d.pop("date", UNSET)

        runtime = d.pop("runtime", UNSET)

        nbest = d.pop("nbest", UNSET)

        _language = d.pop("language", UNSET)
        language: Union[Unset, Language]
        if isinstance(_language, Unset):
            language = UNSET
        else:
            language = Language.from_dict(_language)

        multilingual = []
        _multilingual = d.pop("multilingual", UNSET)
        for multilingual_item_data in _multilingual or []:
            multilingual_item = MultilingualTerm.from_dict(multilingual_item_data)

            multilingual.append(multilingual_item)

        query_result_term_vector = cls(
            term_vector=term_vector,
            software=software,
            version=version,
            date=date,
            runtime=runtime,
            nbest=nbest,
            language=language,
            multilingual=multilingual,
        )

        return query_result_term_vector
