from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.entity import Entity
from ..models.language import Language
from ..models.sentence import Sentence
from ..models.weighted_term import WeightedTerm
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryParameters")


@attr.s(auto_attribs=True)
class QueryParameters:
    """ """

    text: Union[Unset, str] = UNSET
    short_text: Union[Unset, str] = UNSET
    term_vector: Union[Unset, List[WeightedTerm]] = UNSET
    language: Union[Unset, Language] = UNSET
    entities: Union[Unset, List[Entity]] = UNSET
    sentences: Union[Unset, List[Sentence]] = UNSET
    mentions: Union[Unset, List[str]] = UNSET
    nbest: Union[Unset, bool] = UNSET
    sentence: Union[Unset, bool] = UNSET
    customisation: Union[Unset, str] = UNSET
    process_sentence: Union[Unset, List[int]] = UNSET
    structure: Union[Unset, str] = UNSET
    min_selector_score: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        text = self.text
        short_text = self.short_text
        term_vector: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.term_vector, Unset):
            term_vector = []
            for term_vector_item_data in self.term_vector:
                term_vector_item = term_vector_item_data.to_dict()

                term_vector.append(term_vector_item)

        language: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.language, Unset):
            language = self.language.to_dict()

        entities: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.entities, Unset):
            entities = []
            for entities_item_data in self.entities:
                entities_item = entities_item_data.to_dict()

                entities.append(entities_item)

        sentences: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sentences, Unset):
            sentences = []
            for sentences_item_data in self.sentences:
                sentences_item = sentences_item_data.to_dict()

                sentences.append(sentences_item)

        mentions: Union[Unset, List[str]] = UNSET
        if not isinstance(self.mentions, Unset):
            mentions = self.mentions

        nbest = self.nbest
        sentence = self.sentence
        customisation = self.customisation
        process_sentence: Union[Unset, List[int]] = UNSET
        if not isinstance(self.process_sentence, Unset):
            process_sentence = self.process_sentence

        structure = self.structure
        min_selector_score = self.min_selector_score

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if short_text is not UNSET:
            field_dict["shortText"] = short_text
        if term_vector is not UNSET:
            field_dict["termVector"] = term_vector
        if language is not UNSET:
            field_dict["language"] = language
        if entities is not UNSET:
            field_dict["entities"] = entities
        if sentences is not UNSET:
            field_dict["sentences"] = sentences
        if mentions is not UNSET:
            field_dict["mentions"] = mentions
        if nbest is not UNSET:
            field_dict["nbest"] = nbest
        if sentence is not UNSET:
            field_dict["sentence"] = sentence
        if customisation is not UNSET:
            field_dict["customisation"] = customisation
        if process_sentence is not UNSET:
            field_dict["processSentence"] = process_sentence
        if structure is not UNSET:
            field_dict["structure"] = structure
        if min_selector_score is not UNSET:
            field_dict["minSelectorScore"] = min_selector_score

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        text = d.pop("text", UNSET)

        short_text = d.pop("shortText", UNSET)

        term_vector = []
        _term_vector = d.pop("termVector", UNSET)
        for term_vector_item_data in _term_vector or []:
            term_vector_item = WeightedTerm.from_dict(term_vector_item_data)

            term_vector.append(term_vector_item)

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

        sentences = []
        _sentences = d.pop("sentences", UNSET)
        for sentences_item_data in _sentences or []:
            sentences_item = Sentence.from_dict(sentences_item_data)

            sentences.append(sentences_item)

        mentions = cast(List[str], d.pop("mentions", UNSET))

        nbest = d.pop("nbest", UNSET)

        sentence = d.pop("sentence", UNSET)

        customisation = d.pop("customisation", UNSET)

        process_sentence = cast(List[int], d.pop("processSentence", UNSET))

        structure = d.pop("structure", UNSET)

        min_selector_score = d.pop("minSelectorScore", UNSET)

        query_parameters = cls(
            text=text,
            short_text=short_text,
            term_vector=term_vector,
            language=language,
            entities=entities,
            sentences=sentences,
            mentions=mentions,
            nbest=nbest,
            sentence=sentence,
            customisation=customisation,
            process_sentence=process_sentence,
            structure=structure,
            min_selector_score=min_selector_score,
        )

        return query_parameters
