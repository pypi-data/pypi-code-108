# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import abc
from enum import Enum
from typing import List, Optional

from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import THING_CLASS, OntologyClassReference
from knowledge.services.base import WacomServiceAPIClient, RESTAPIClient


class EntityType(Enum):
    """
    Entity types
    ------------
    Different types of entities.
    """
    PUBLIC_ENTITY = 0
    """Public entity - Entity from a public knowledge graph"""
    PERSONAL_ENTITY = 1
    """Personal entity - Entity from a personal / organisational knowledge graph"""
    NAMED_ENTITY = 2
    """Simple entity - Entity type not linked to a knowledge graph"""


class KnowledgeSource(Enum):
    """
    Knowledge source
    ----------------
    List of knowledge sources which a used within Semantic Ink.
    """
    WIKIDATA = 'wikidata'
    """Wikidata"""
    DBPEDIA = 'dbpedia'
    """dbpedia"""
    WACOM_KNOWLEDGE = 'wacom'
    """Wacom Personal Knowledge"""


class BasicType(Enum):
    """
    Basic type
    ----------
    Basic type of entities.
    """
    UNKNOWN = 'Unknown'
    MONEY = 'Money'
    PERSON = 'Person'
    DATE = 'Date'
    PLACE = 'Place'
    TIME = 'Time'
    NUMBER = 'Number'


class EntitySource(object):
    """
    EntitySource
    ------------
    Source of the entity.

    Parameters
    ----------
    uri: str
        URI of entity
    source: KnowledgeSource
        Identifier where the entity originates.
    """

    def __init__(self, uri: str, source: KnowledgeSource):
        self.__uri = uri
        self.__source: KnowledgeSource = source

    @property
    def uri(self) -> str:
        """Identifier with the knowledge graph."""
        return self.__uri

    @property
    def source(self) -> KnowledgeSource:
        """Source of the entity."""
        return self.__source

    def __repr__(self):
        return f'{self.uri} ({self.source})'


class NamedEntity(abc.ABC):
    """
    NamedEntity
    -----------
    A named entity which is recognized by recognition engine.
    The class contains information on the found entity, found in reference text.

    Parameters
    ----------
    ref_text: str
        Reference text. Entity found for this specific text
    start_idx: int
        Start index within the full reference text
    end_idx: int
        End index with the full reference text
    entity_type: EntityType
        Type of the entity.
    """

    def __init__(self, ref_text: str, start_idx: int, end_idx: int, entity_type: EntityType):
        self.__ref_text: str = ref_text
        self.__start_idx: int = start_idx
        self.__end_idx: int = end_idx
        self.__type: EntityType = entity_type

    @property
    def ref_text(self) -> str:
        """Reference text for which the entity has been found"""
        return self.__ref_text

    @property
    def start_idx(self) -> int:
        """Start index within the text handed to the named entity recognition."""
        return self.__start_idx

    @property
    def end_idx(self) -> int:
        """End index within the text handed to the named entity recognition."""
        return self.__end_idx

    @property
    def entity_type(self) -> EntityType:
        """Type of the entity."""
        return self.__type

    def __repr__(self):
        return f'{self.ref_text} [{self.start_idx}-{self.end_idx}'


class KnowledgeGraphEntity(NamedEntity):
    """
    Knowledge graph entity
    ----------------------
    Entity from a knowledge graph.

    Parameters
    ----------
    ref_text: str
        Reference text. Entity found for this specific text
    start_idx: int
        Start index within the full reference text
    end_idx: int
        End index with the full reference text
    label: str
        Main label of the entity.
    confidence: float
        Confidence value if available
    source: EntitySource
        Source of the entity
    content_link: str
        Link to side with content
    ontology_types: List[str]
        List of ontology types (class names)
    entity_type: EntityType
        Type of the entity.
    """

    def __init__(self, ref_text: str, start_idx: int, end_idx: int, label: str, confidence: float,
                 source: EntitySource, content_link: str,
                 ontology_types: List[str], entity_type: EntityType = EntityType.PUBLIC_ENTITY):
        super().__init__(ref_text, start_idx, end_idx, entity_type)
        self.__source: EntitySource = source
        self.__content_link: str = content_link
        self.__label: str = label
        self.__confidence: float = confidence
        self.__description: Optional[str] = None
        self.__thumbnail: Optional[str] = None
        self.__ontology_types: List[str] = ontology_types
        self.__relevant_type: OntologyClassReference = THING_CLASS

    @property
    def entity_source(self) -> EntitySource:
        """Source of the entity."""
        return self.__source

    @property
    def label(self) -> str:
        """Label of the entity from the knowledge graph."""
        return self.__label

    @property
    def confidence(self) -> float:
        """Confidence level of the system that links the entities."""
        return self.__confidence

    @confidence.setter
    def confidence(self, value: float):
        self.__confidence = value

    @property
    def description(self) -> Optional[str]:
        """Description of the entity if available."""
        return self.__description

    @description.setter
    def description(self, value: str):
        self.__description = value

    @property
    def thumbnail(self) -> Optional[str]:
        """Thumbnail to describes the entity."""
        return self.__thumbnail

    @thumbnail.setter
    def thumbnail(self, value: str):
        self.__thumbnail = value

    @property
    def content_link(self) -> str:
        """Link to content page."""
        return self.__content_link

    @property
    def ontology_types(self) -> List[str]:
        """List of ontology types."""
        return self.__ontology_types

    @property
    def relevant_type(self) -> OntologyClassReference:
        """"Most relevant ontology type. That likes to Wacom's personal knowledge base ontology."""
        return self.__relevant_type

    @relevant_type.setter
    def relevant_type(self, value: OntologyClassReference):
        self.__relevant_type = value

    def __repr__(self):
        return f'{self.ref_text} [{self.start_idx}-{self.end_idx}] -> {self.entity_source} [{self.entity_type}]'


class BasicNamedEntity(NamedEntity):
    """
    Basic named entity
    ------------------
    Entity found by Named entity recognition.

    Parameters
    ----------
    ref_text: str
        Reference text. Entity found for this specific text
    start_idx: int
        Start index within the full reference text
    end_idx: int
        End index with the full reference text
    basic_type: BasicType
        Type of the entity.
    """

    def __init__(self, ref_text: str, start_idx: int, end_idx: int, basic_type: BasicType):
        super().__init__(ref_text, start_idx, end_idx, EntityType.NAMED_ENTITY)
        self.__basic_type: BasicType = basic_type

    @property
    def basic_type(self) -> BasicType:
        """Basic type that is recognized."""
        return self.__basic_type

    def __repr__(self):
        return f'{self.ref_text} [{self.start_idx}-{self.end_idx}] -> {self.basic_type}'


class PersonalEntityLinkingProcessor(WacomServiceAPIClient):
    """
    PersonalEntityLinkingProcessor
    ------------------------------
    Service that links entities to a entities in a personal knowledge graph.

    Parameters
    ----------
    service_url: str
        URL where the service has been deployed
    supported_languages: List[str] = None
        List of supported languages
    verify_calls: bool (default:=False)
        Verifies all HTTPS calls and the associated certificate.
    """

    def __init__(self, service_url: str = str, supported_languages: List[str] = None, verify_calls: bool = False):
        super().__init__(application_name="Personal entity linking", service_url=service_url,
                         service_endpoint="graph", verify_calls=verify_calls)
        self.__supported_languages: List[str] = supported_languages if supported_languages else []

    @abc.abstractmethod
    def link_personal_entities(self, auth_key: str, text: str, language_code: LanguageCode = 'en_US') \
            -> List[KnowledgeGraphEntity]:
        """
        Performs Named Entity Linking on a text. It only finds entities which are accessible by the user identified by
        the auth key.

        Parameters
        ----------
        auth_key: str
            Auth key identifying a user within the Wacom personal knowledge service.
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge graph entities.
        """
        raise NotImplemented

    @property
    def supported_language(self) -> List[str]:
        """List of supported languages."""
        return self.__supported_languages

    def is_language_supported(self, language_code: LanguageCode) -> bool:
        """Is the language_code code supported by the engine.

        Parameters
        -----------
        language_code: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        flag: bool
            Flag if this language_code code is supported.
        """
        return language_code in self.supported_language

    def __repr__(self):
        return f'Personal Entity Linking:= {self.service_url}'


class NamedEntityRecognitionProcessor(WacomServiceAPIClient):
    """
    NamedEntityRecognitionProcessor
    -------------------------------
    Service that recognizes entities.

    Parameters
    ----------
    service_url: str
        URL where the service has been deployed
    supported_languages: List[str] = None
        List of supported languages
    verify_calls: bool (default:=False)
        Verifies all HTTPS calls and the associated certificate.
    """

    def __init__(self, service_url: str, supported_languages: List[LanguageCode] = None,
                 verify_calls: bool = False):
        super().__init__(application_name='Named Entity Linking', service_url=service_url, service_endpoint="graph",
                         verify_calls=verify_calls)
        self.__supported_languages: List[LanguageCode] = supported_languages if supported_languages else []

    @abc.abstractmethod
    def named_entities(self, text: str, language_code: LanguageCode = 'en_US') -> List[NamedEntity]:
        """
        Performs Named Entity Recognition on a text.

        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        entities: List[NamedEntity]
            List of knowledge named entities.
        """
        raise NotImplemented

    @property
    def supported_language(self) -> List[LanguageCode]:
        """List of supported languages."""
        return self.__supported_languages

    def is_language_supported(self, language_code: LanguageCode) -> bool:
        """Is the language_code code supported by the engine.

        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        flag: bool
            Flag if this language_code code is supported
        """
        return language_code in self.supported_language

    def __repr__(self):
        return f'Public entity linking:= {self.__service_url}'


class PublicEntityLinkingProcessor(RESTAPIClient):
    """
    Public Entity Linking
    ---------------------
    Service that links entities to a public entities in a knowledge graph.

    Parameters
    ----------
    service_url: str
        URL where the service has been deployed
    supported_languages: List[str] = None
        List of supported languages
    verify_calls: bool (default:=False)
        Verifies all HTTPS calls and the associated certificate.
    """

    def __init__(self, service_url: str = str, supported_languages: List[str] = None, verify_calls: bool = False):
        super().__init__(service_url=service_url, verify_calls=verify_calls)
        self.__supported_languages: List[str] = supported_languages if supported_languages else []

    @abc.abstractmethod
    def link_public_entities(self, text: str, language_code: LanguageCode = 'en_US') -> List[KnowledgeGraphEntity]:
        """
        Performs Named Entity Linking on a text. It only finds entities within a large public knowledge graph.

        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge public knowledge entities.
        """
        raise NotImplemented

    @property
    def supported_language(self) -> List[str]:
        """List of supported languages."""
        return self.__supported_languages

    def is_language_supported(self, language_code: str) -> bool:
        """
        Is the language_code code supported by the engine.

        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        flag: bool
            Flag if this language_code code is supported
        """
        return language_code in self.supported_language

    def __repr__(self):
        return f'Public Entity Linking:= {self.service_url}'
