from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.category import Category
from ..models.entity import Entity
from ..models.language import Language
from ..models.multilingual_term import MultilingualTerm
from ..models.page import Page
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryResultFile")


@attr.s(auto_attribs=True)
class QueryResultFile:
    """ """

    pages: List[Page]
    software: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    date: Union[Unset, str] = UNSET
    runtime: Union[Unset, int] = UNSET
    nbest: Union[Unset, bool] = UNSET
    file: Union[Unset, str] = UNSET
    language: Union[Unset, Language] = UNSET
    entities: Union[Unset, List[Entity]] = UNSET
    global_categories: Union[Unset, List[Category]] = UNSET
    multilingual: Union[Unset, List[MultilingualTerm]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        pages = []
        for pages_item_data in self.pages:
            pages_item = pages_item_data.to_dict()

            pages.append(pages_item)

        software = self.software
        version = self.version
        date = self.date
        runtime = self.runtime
        nbest = self.nbest
        file = self.file
        language: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.language, Unset):
            language = self.language.to_dict()

        entities: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.entities, Unset):
            entities = []
            for entities_item_data in self.entities:
                entities_item = entities_item_data.to_dict()

                entities.append(entities_item)

        global_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.global_categories, Unset):
            global_categories = []
            for global_categories_item_data in self.global_categories:
                global_categories_item = global_categories_item_data.to_dict()

                global_categories.append(global_categories_item)

        multilingual: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.multilingual, Unset):
            multilingual = []
            for multilingual_item_data in self.multilingual:
                multilingual_item = multilingual_item_data.to_dict()

                multilingual.append(multilingual_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "pages": pages,
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
        if file is not UNSET:
            field_dict["file"] = file
        if language is not UNSET:
            field_dict["language"] = language
        if entities is not UNSET:
            field_dict["entities"] = entities
        if global_categories is not UNSET:
            field_dict["global_categories"] = global_categories
        if multilingual is not UNSET:
            field_dict["multilingual"] = multilingual

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pages = []
        _pages = d.pop("pages")
        for pages_item_data in _pages:
            pages_item = Page.from_dict(pages_item_data)

            pages.append(pages_item)

        software = d.pop("software", UNSET)

        version = d.pop("version", UNSET)

        date = d.pop("date", UNSET)

        runtime = d.pop("runtime", UNSET)

        nbest = d.pop("nbest", UNSET)

        file = d.pop("file", UNSET)

        _language = d.pop("language", UNSET)
        language: Union[Unset, Language]
        if isinstance(_language, Unset):
            language = UNSET
        else:
            language = Language.from_dict(_language)

        entities = []
        _entities = d.pop("entities", UNSET)
        for entities_item_data in _entities or []:
            entities_item = Entity.from_dict(entities_item_data)

            entities.append(entities_item)

        global_categories = []
        _global_categories = d.pop("global_categories", UNSET)
        for global_categories_item_data in _global_categories or []:
            global_categories_item = Category.from_dict(global_categories_item_data)

            global_categories.append(global_categories_item)

        multilingual = []
        _multilingual = d.pop("multilingual", UNSET)
        for multilingual_item_data in _multilingual or []:
            multilingual_item = MultilingualTerm.from_dict(multilingual_item_data)

            multilingual.append(multilingual_item)

        query_result_file = cls(
            pages=pages,
            software=software,
            version=version,
            date=date,
            runtime=runtime,
            nbest=nbest,
            file=file,
            language=language,
            entities=entities,
            global_categories=global_categories,
            multilingual=multilingual,
        )

        return query_result_file
