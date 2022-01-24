from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.category import Category
from ..models.definition import Definition
from ..models.multilingual_term import MultilingualTerm
from ..models.statement import Statement
from ..types import UNSET, Unset

T = TypeVar("T", bound="Concept")


@attr.s(auto_attribs=True)
class Concept:
    """ """

    raw_name: Union[Unset, str] = UNSET
    preferred_term: Union[Unset, str] = UNSET
    confidence_score: Union[Unset, float] = UNSET
    wikipedia_external_ref: Union[Unset, int] = UNSET
    wikidata_id: Union[Unset, str] = UNSET
    definitions: Union[Unset, List[Definition]] = UNSET
    categories: Union[Unset, List[Category]] = UNSET
    domains: Union[Unset, List[str]] = UNSET
    multilingual: Union[Unset, List[MultilingualTerm]] = UNSET
    statements: Union[Unset, List[Statement]] = UNSET
    type: Union[Unset, str] = UNSET
    sense: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        raw_name = self.raw_name
        preferred_term = self.preferred_term
        confidence_score = self.confidence_score
        wikipedia_external_ref = self.wikipedia_external_ref
        wikidata_id = self.wikidata_id
        definitions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.definitions, Unset):
            definitions = []
            for definitions_item_data in self.definitions:
                definitions_item = definitions_item_data.to_dict()

                definitions.append(definitions_item)

        categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.categories, Unset):
            categories = []
            for categories_item_data in self.categories:
                categories_item = categories_item_data.to_dict()

                categories.append(categories_item)

        domains: Union[Unset, List[str]] = UNSET
        if not isinstance(self.domains, Unset):
            domains = self.domains

        multilingual: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.multilingual, Unset):
            multilingual = []
            for multilingual_item_data in self.multilingual:
                multilingual_item = multilingual_item_data.to_dict()

                multilingual.append(multilingual_item)

        statements: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.statements, Unset):
            statements = []
            for statements_item_data in self.statements:
                statements_item = statements_item_data.to_dict()

                statements.append(statements_item)

        type = self.type
        sense = self.sense

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if raw_name is not UNSET:
            field_dict["rawName"] = raw_name
        if preferred_term is not UNSET:
            field_dict["preferredTerm"] = preferred_term
        if confidence_score is not UNSET:
            field_dict["confidence_score"] = confidence_score
        if wikipedia_external_ref is not UNSET:
            field_dict["wikipediaExternalRef"] = wikipedia_external_ref
        if wikidata_id is not UNSET:
            field_dict["wikidataId"] = wikidata_id
        if definitions is not UNSET:
            field_dict["definitions"] = definitions
        if categories is not UNSET:
            field_dict["categories"] = categories
        if domains is not UNSET:
            field_dict["domains"] = domains
        if multilingual is not UNSET:
            field_dict["multilingual"] = multilingual
        if statements is not UNSET:
            field_dict["statements"] = statements
        if type is not UNSET:
            field_dict["type"] = type
        if sense is not UNSET:
            field_dict["sense"] = sense

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        raw_name = d.pop("rawName", UNSET)

        preferred_term = d.pop("preferredTerm", UNSET)

        confidence_score = d.pop("confidence_score", UNSET)

        wikipedia_external_ref = d.pop("wikipediaExternalRef", UNSET)

        wikidata_id = d.pop("wikidataId", UNSET)

        definitions = []
        _definitions = d.pop("definitions", UNSET)
        for definitions_item_data in _definitions or []:
            definitions_item = Definition.from_dict(definitions_item_data)

            definitions.append(definitions_item)

        categories = []
        _categories = d.pop("categories", UNSET)
        for categories_item_data in _categories or []:
            categories_item = Category.from_dict(categories_item_data)

            categories.append(categories_item)

        domains = cast(List[str], d.pop("domains", UNSET))

        multilingual = []
        _multilingual = d.pop("multilingual", UNSET)
        for multilingual_item_data in _multilingual or []:
            multilingual_item = MultilingualTerm.from_dict(multilingual_item_data)

            multilingual.append(multilingual_item)

        statements = []
        _statements = d.pop("statements", UNSET)
        for statements_item_data in _statements or []:
            statements_item = Statement.from_dict(statements_item_data)

            statements.append(statements_item)

        type = d.pop("type", UNSET)

        sense = d.pop("sense", UNSET)

        concept = cls(
            raw_name=raw_name,
            preferred_term=preferred_term,
            confidence_score=confidence_score,
            wikipedia_external_ref=wikipedia_external_ref,
            wikidata_id=wikidata_id,
            definitions=definitions,
            categories=categories,
            domains=domains,
            multilingual=multilingual,
            statements=statements,
            type=type,
            sense=sense,
        )

        return concept
