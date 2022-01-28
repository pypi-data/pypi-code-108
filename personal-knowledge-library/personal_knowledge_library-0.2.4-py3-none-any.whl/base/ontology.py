# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
from json import JSONEncoder
from typing import List, Union, Set, Tuple

from knowledge.base.access import TenantAccessRight
from knowledge.base.entity import *

# ---------------------------------------------- Vocabulary base URI ---------------------------------------------------
PREFIX: str = "xsd"
BASE_URI: str = "http://www.w3.org/2001/XMLSchema#"
# ---------------------------------------------------- Constants -------------------------------------------------------
SUB_CLASS_OF_TAG: str = 'subClassOf'
TENANT_ID: str = 'tenantId'
NAME_TAG: str = "name"


class PropertyType(enum.Enum):
    """
    PropertyType
    -----------
    Within the ontology two different property types are defined. A data- and an object property.
    """
    OBJECT_PROPERTY = "Relation"
    DATA_PROPERTY = "Literal"


INVERSE_PROPERTY_TYPE: Dict[str, PropertyType] = dict([(pt.value, pt) for pt in PropertyType])


class DataPropertyType(enum.Enum):
    """
    DataPropertyType.
    -----------------
    Data types that are used by Datatype properties.
    """
    STRING = BASE_URI + "string"
    """Character strings (but not all Unicode character strings) """
    BOOLEAN = BASE_URI + "boolean"
    """boolean: true, false"""
    DECIMAL = BASE_URI + "decimal"
    """Arbitrary-precision decimal numbers"""
    INTEGER = BASE_URI + "integer"
    """Arbitrary-size integer numbers"""
    DOUBLE = BASE_URI + "double"
    """64-bit floating point numbers incl. ±Inf, ±0, NaN"""
    FLOAT = BASE_URI + "float"
    """32-bit floating point numbers incl. ±Inf, ±0, NaN"""
    DATE = BASE_URI + "date"
    """Dates (yyyy-mm-dd) with or without timezone"""
    TIME = BASE_URI + "time"
    """Times (hh:mm:ss.sss…) with or without timezone"""
    DATE_TIME = BASE_URI + "dateTime"
    """Date and time with or without timezone"""
    DATE_TIMESTAMP = BASE_URI + "dateTimeStamp"
    """Date and time with required timezone """
    G_YEAR = BASE_URI + "gYear"
    """Gregorian calendar year"""
    G_MONTH = BASE_URI + "gMonth"
    """Gregorian calendar month"""
    G_DAY = BASE_URI + "gDay"
    """Gregorian calendar day of the month"""
    G_YEAR_MONTH = BASE_URI + "gYearMonth"
    """Gregorian calendar year and month"""
    G_MONTH_DAY = BASE_URI + "gMonthDay"
    """Gregorian calendar month and day"""
    DURATION = BASE_URI + "duration"
    """Duration of time"""
    YEAR_MONTH_DURATION = BASE_URI + "yearMonthDuration"
    """Duration of time (months and years only)"""
    DAYTIME_DURATION = BASE_URI + "dayTimeDuration"
    """Duration of time (days, hours, minutes, seconds only)"""
    BYTES = BASE_URI + "byte"
    """-128…+127 (8 bit)"""
    SHORT = BASE_URI + "short"
    """-32768… + 32767 (16 bit)"""
    INT = BASE_URI + "int"
    """-2147483648…+2147483647 (32 bit)"""
    LONG = BASE_URI + "long"
    """-9223372036854775808…+9223372036854775807 (64 bit)"""
    UNSIGNED_BYTE = BASE_URI + "unsignedByte"
    """0 … 255 (8 bit)"""
    UNSIGNED_SHORT = BASE_URI + "unsignedShort"
    """0 … 65535 (16 bit)"""
    UNSIGNED_INT = BASE_URI + "unsignedInt"
    """ 0 … 4294967295 (32 bit)"""
    UNSIGNED_LONG = BASE_URI + "unsignedLong"
    """  0 … 18446744073709551615 (64 bit)"""
    POSITIVE_INTEGER = BASE_URI + "positiveInteger"
    """Integer numbers > 0 """
    NON_NEGATIVE_INTEGER = BASE_URI + "nonNegativeInteger"
    """Integer numbers ≥ 0"""
    NEGATIVE_INTEGER = BASE_URI + "negativeInteger"
    """Integer numbers ≤ 0"""
    NON_POSITIVE_INTEGER = BASE_URI + "nonPositiveInteger"
    """Integer numbers ≤ 0"""
    HEX_BINARY = BASE_URI + "hexBinary"
    """Hex-encoded binary data"""
    BASE64_BINARY = BASE_URI + "base64Binary"
    """Base64-encoded binary data"""
    ANY_URI = BASE_URI + "anyURI"
    """Absolute or relative URIs and IRIs"""
    LANGUAGE = BASE_URI + "language_code"
    """Language tags per http://tools.ietf.org/html/bcp47"""
    NORMALIZED = BASE_URI + "normalizedString"
    """Whitespace-normalized strings"""
    TOKEN = BASE_URI + "token"
    """Tokenized strings"""
    NM_TOKEN = BASE_URI + "NMTOKEN"
    """XML NMTOKENs"""
    NAME = BASE_URI + "Name"
    """XML Names"""
    NC_NAME = BASE_URI + "NCName"
    """XML NCNames"""


INVERSE_DATA_PROPERTY_TYPE_MAPPING: Dict[str, DataPropertyType] = dict([(lit_type.value, lit_type)
                                                                        for lit_type in DataPropertyType])
"""Maps the string representation of the XSD data types to the data types enum constants."""


# ------------------------------------------ Ontology References -------------------------------------------------------

class OntologyObjectReference(abc.ABC):
    """
        Ontology class type
        ------------------
        Associated to an entity to link the type of the entity.

        Parameters
        ----------
        scheme: str
            Scheme or owner of the ontology object
        context: str
            Context of ontology object
        name: str
            Ontology object reference name
    """

    def __init__(self, scheme: str, context: str, name: str):
        self.__scheme: str = scheme
        self.__context: str = context
        self.__name: str = name

    @property
    def scheme(self):
        """Scheme."""
        return self.__scheme

    @property
    def context(self):
        """Context."""
        return self.__context

    @property
    def name(self):
        """Name."""
        return self.__name

    @property
    def iri(self):
        """Internationalized Resource Identifier (IRI) encoded ontology class name."""
        return f'{self.scheme}:{self.context}#{self.name}'

    def __repr__(self):
        return self.iri

    @classmethod
    def parse_iri(cls, iri: str) -> Tuple[str, str, str]:
        colon_idx: int = iri.index(':')
        hash_idx: int = iri.index('#')
        scheme: str = iri[:colon_idx]
        context: str = iri[colon_idx + 1:hash_idx]
        name: str = iri[hash_idx + 1:]
        return scheme, context, name


class OntologyClassReference(OntologyObjectReference):
    """
    Ontology class type
    -------------------
    Associated to an ontology class.

    Parameters
    ----------
    scheme: str
        Scheme or owner
    context: str
        Context of class
    class_name: str
        Class name
    """

    def __init__(self, scheme: str, context: str, class_name: str):
        super().__init__(scheme, context, class_name)

    @property
    def class_name(self):
        """Class name."""
        return self.name

    @classmethod
    def parse(cls, iri: str) -> 'OntologyClassReference':
        scheme, context, name = OntologyObjectReference.parse_iri(iri)
        return OntologyClassReference(scheme, context, name)

    def __eq__(self, other):
        if not isinstance(other, OntologyClassReference):
            return False
        return self.iri == other.iri

    def __hash__(self):
        return hash(self.iri)


class OntologyPropertyReference(OntologyObjectReference):
    """
    Property reference
    ------------------
    Associated to an ontology property.

    Parameters
    ----------
    scheme: str
        Scheme or owner
    context: str
        Context of class
    property_name: str
        Property name
    """

    def __init__(self, scheme: str, context: str, property_name: str):
        super().__init__(scheme, context, property_name)

    @property
    def property_name(self):
        """Property name."""
        return self.name

    @classmethod
    def parse(cls, iri: str) -> 'OntologyPropertyReference':
        scheme, context, name = OntologyObjectReference.parse_iri(iri)
        return OntologyPropertyReference(scheme, context, name)

    def __eq__(self, other):
        if not isinstance(other, OntologyPropertyReference):
            return False
        return self.iri == other.iri

    def __hash__(self):
        return hash(self.iri)


# ------------------------------------------------- Constants ----------------------------------------------------------
THING_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
SYSTEM_SOURCE_SYSTEM: OntologyPropertyReference = OntologyPropertyReference('wacom', 'core', 'sourceSystem')
SYSTEM_SOURCE_REFERENCE_ID: OntologyPropertyReference = OntologyPropertyReference('wacom', 'core', 'sourceReferenceId')


class OntologyClass(OntologyObject):
    """
    OntologyClass
    ----------------
    Concept for ontology.

    Parameters
    ----------
    tenant_id: str
        Tenant id for ontology
    context: str
        Context
    reference: OntologyClassReference
        Reference for ontology class
    icon: str
        Icon representing concept
    labels: List[Label]
        List of labels
    comments: List[Comment]
        List of comments

    subclass_of: str (default: None)
        Subclass of ontology class
    """

    def __init__(self, tenant_id: str, context: str, reference: OntologyClassReference,
                 subclass_of: OntologyClassReference = None, icon: Optional[str] = None,
                 labels: Optional[List[Label]] = None, comments: Optional[List[Comment]] = None):
        self.__subclass_of: OntologyClassReference = subclass_of
        self.__reference: OntologyClassReference = reference
        super().__init__(tenant_id, reference.iri, icon, labels, comments, context)

    @property
    def subclass_of(self) -> Optional[OntologyClassReference]:
        """
        Superclass of the class.
        """
        return self.__subclass_of

    @property
    def reference(self) -> OntologyClassReference:
        """
        Reference of ontology class.
        """
        return self.__reference

    def __repr__(self):
        return f'<OntologyClass> - [reference:={self.reference}, subclass_of:={self.subclass_of}]'

    @classmethod
    def from_dict(cls, concept_dict: Dict[str, Any]):
        labels: List[Label] = [] if concept_dict[LABELS_TAG] is None else \
            [Label(content=la[VALUE_TAG], language_code=la[LANGUAGE_CODE_TAG]) for la in concept_dict[LABELS_TAG]]
        comments: List[Comment] = [] if concept_dict['comments'] is None else \
            [Comment(text=la[VALUE_TAG], language_code=la[LANGUAGE_CODE_TAG]) for la in concept_dict['comments']]
        return OntologyClass(tenant_id=concept_dict[TENANT_ID], context=concept_dict['context'],
                             reference=OntologyClassReference.parse(concept_dict[NAME_TAG]),
                             subclass_of=OntologyClassReference.parse(concept_dict[SUB_CLASS_OF_TAG]),
                             icon=concept_dict['icon'], labels=labels, comments=comments)

    @classmethod
    def new(cls) -> 'OntologyClass':
        return OntologyClass('', '', THING_CLASS)


class OntologyProperty(OntologyObject):
    """
    Ontology Property
    -----------------
    Property ontology object.

    Parameters
    ----------
    kind: str
        Kind of relation
    tenant_id: str
        Tenant id
    context: str
        Context
    name: OntologyPropertyReference
        Name of property object
    icon: str
        Icon describing the property
    property_domain: OntologyClassReference
        Domain for the property
    property_range: OntologyClassReference
        Range for the property
    labels: List[Label]
        List of labels (localized)
    comments: List[Comment],
        List of comments
    subproperty_of: str (default: = None)
        Subproperty
    inverse_property_of: str (optional)
        Inverse property
    """

    def __init__(self, kind: PropertyType, tenant_id: str, context: str, name: OntologyPropertyReference,
                 icon: str = None,
                 property_domain: Optional[OntologyClassReference] = None,
                 property_range: Optional[Union[OntologyClassReference, DataPropertyType]] = None,
                 labels: Optional[List[Label]] = None,
                 comments: Optional[List[Comment]] = None,
                 subproperty_of: Optional[OntologyPropertyReference] = None,
                 inverse_property_of: Optional[OntologyPropertyReference] = None):
        self.__kind: PropertyType = kind
        self.__subproperty_of: OntologyPropertyReference = subproperty_of
        self.__inverse_property_of: OntologyPropertyReference = inverse_property_of
        self.__domain: OntologyClassReference = property_domain
        self.__range: Optional[Union[OntologyClassReference, DataPropertyType]] = property_range
        self.__reference: OntologyPropertyReference = name
        super().__init__(tenant_id, name.iri, icon, labels, comments, context)

    @property
    def is_data_property(self) -> bool:
        return self.kind != PropertyType.OBJECT_PROPERTY

    @property
    def kind(self) -> PropertyType:
        """Kind of the property."""
        return self.__kind

    @property
    def reference(self) -> OntologyPropertyReference:
        """Reference to property"""
        return self.__reference

    @property
    def subproperty_of(self) -> OntologyPropertyReference:
        """Reference to the super property"""
        return self.__subproperty_of

    @property
    def inverse_property_of(self) -> OntologyPropertyReference:
        """Reference to the inverse property"""
        return self.__inverse_property_of

    @property
    def domain(self) -> OntologyClassReference:
        """Domain of the property."""
        return self.__domain

    @property
    def range(self) -> Optional[Union[OntologyClassReference, DataPropertyType]]:
        return self.__range

    def __repr__(self):
        return f'<OntologyProperty> - [name:= {self.iri} domain:={self.domain}, range:={self.range}, ' \
               f'subproperty_of:={self.subproperty_of}, type:={self.kind}]'

    @classmethod
    def from_dict(cls, property_dict: Dict[str, Any]):
        labels: List[Label] = [] if property_dict[LABELS_TAG] is None else \
            [Label.create_from_dict(la) for la in property_dict[LABELS_TAG]]
        comments: List[Comment] = [] if property_dict['comments'] is None else \
            [Comment.create_from_dict(co) for co in property_dict['comments']]
        return OntologyProperty(INVERSE_PROPERTY_TYPE[property_dict['kind']],
                                property_dict['tenantId'], property_dict['context'],
                                OntologyPropertyReference.parse(property_dict['name']),
                                property_dict['icon'],
                                OntologyClassReference.parse(property_dict['domain'])
                                if property_dict['domain'] is not None else None,
                                OntologyClassReference.parse(property_dict['range'])
                                if property_dict['range'] is not None else None,
                                labels, comments,
                                OntologyPropertyReference.parse(property_dict['subPropertyOf'])
                                if property_dict['subPropertyOf'] is not None else None,
                                OntologyPropertyReference.parse(property_dict['inverseOf'])
                                if property_dict['inverseOf'] is not None else None)

    @classmethod
    def new(cls, kind: PropertyType) -> 'OntologyProperty':
        return OntologyProperty(kind, '', '',
                                OntologyPropertyReference.parse('http://www.w3.org/2002/07/owl#topObjectProperty'))


class EntityProperty(abc.ABC):
    """
    EntityProperty
    --------------
    Abstract class for the different types of properties.
    """
    pass


class DataProperty(EntityProperty):
    """
    DataProperty
    ------------
    Data property for entities.

    Parameter
    ---------
    content: Any
        Content
    literal_type: LiteralProperty
        OntologyPropertyReference type
    language_code: str
        Language code
    data_type: str
        Data type
    """

    def __init__(self, content: Any, property_ref: OntologyPropertyReference,
                 language_code: LanguageCode = LanguageCode('en_US'), data_type: DataPropertyType = None):
        self.__content: Any = content
        self.__language_code: LanguageCode = language_code
        self.__type: OntologyPropertyReference = property_ref
        self.__data_type: Optional[DataPropertyType] = data_type

    @property
    def data_property_type(self) -> OntologyPropertyReference:
        """Ontology type."""
        return self.__type

    @property
    def data_type(self) -> Optional[DataPropertyType]:
        """Data type (optional)."""
        return self.__data_type

    @property
    def value(self) -> Any:
        """Content of the data property."""
        return self.__content

    @property
    def language_code(self) -> LanguageCode:
        """Language code of the content."""
        return self.__language_code

    @staticmethod
    def create_from_dict(data_property_struct: dict):
        if CONTENT_TAG not in data_property_struct or \
                LANGUAGE_CODE_TAG not in data_property_struct \
                and DATA_PROPERTY_TAG not in data_property_struct:
            raise ValueError("Dict is does not contain a data_property structure.")
        data_property_type: str = data_property_struct[DATA_PROPERTY_TAG]
        data_type: DataPropertyType = DataPropertyType.STRING
        if DATA_TYPE_TAG in data_property_struct and data_property_struct[DATA_TYPE_TAG] is not None:
            if data_property_struct[DATA_TYPE_TAG] not in INVERSE_DATA_PROPERTY_TYPE_MAPPING:
                raise ValueError(f"DataProperty data type is not supported. Type: {data_type}")
            else:
                data_type = INVERSE_DATA_PROPERTY_TYPE_MAPPING[data_property_struct[DATA_TYPE_TAG]]
        return DataProperty(data_property_struct[CONTENT_TAG],
                            OntologyPropertyReference.parse(data_property_type),
                            data_property_struct[LANGUAGE_CODE_TAG], data_type)

    def __dict__(self):
        return {
            CONTENT_TAG: self.value,
            LANGUAGE_CODE_TAG: self.language_code,
            DATA_PROPERTY_TAG: self.data_property_type.iri,
            DATA_TYPE_TAG: None if self.data_type is None else self.data_type.value
        }

    def __repr__(self):
        return f'{self.value}@{self.language_code}<{self.data_property_type.name}>'

    @staticmethod
    def create_from_list(param: List[dict]) -> List['DataProperty']:
        DataProperty.create_from_dict(param[0])
        return [DataProperty.create_from_dict(p) for p in param]


class ObjectProperty(EntityProperty):
    """
    Object Property
    ---------------
    ObjectProperty for entities.

    Parameter
    ---------
    relation: OntologyPropertyReference
        OntologyPropertyReference type
    incoming: List[str] (default:= [])
        Incoming relations
    outgoing: List[str] (default:= [])
        Outgoing relations
    """

    def __init__(self, relation: OntologyPropertyReference,
                 incoming: Optional[List[Union[str, 'ThingObject']]] = None,
                 outgoing: Optional[List[Union[str, 'ThingObject']]] = None):
        self.__relation: OntologyPropertyReference = relation
        self.__incoming: List[Union[str, 'ThingObject']] = incoming if incoming is not None else []
        self.__outgoing: List[Union[str, 'ThingObject']] = outgoing if outgoing is not None else []

    @property
    def relation(self) -> OntologyPropertyReference:
        """Reference from the ontology."""
        return self.__relation

    @property
    def incoming_relations(self) -> List[Union[str, 'ThingObject']]:
        """Incoming relation"""
        return self.__incoming

    @property
    def outgoing_relations(self) -> List[Union[str, 'ThingObject']]:
        return self.__outgoing

    @staticmethod
    def create_from_dict(relation_struct: Dict[str, Any]) -> Tuple[OntologyPropertyReference, 'ObjectProperty']:
        relation_type: OntologyPropertyReference = \
            OntologyPropertyReference.parse(relation_struct[RELATION_TAG])
        incoming: List[Union[str, ThingObject]] = []

        for incoming_relation in relation_struct[INCOMING_TAG]:
            if isinstance(incoming_relation, dict):
                incoming.append(ThingObject.from_dict(incoming_relation))
            elif isinstance(incoming_relation, str):
                incoming.append(incoming_relation)

        outgoing: List[Union[str, ThingObject]] = []
        for outgoing_relation in relation_struct[OUTGOING_TAG]:
            if isinstance(outgoing_relation, dict):
                outgoing.append(ThingObject.from_dict(outgoing_relation))
            elif isinstance(outgoing_relation, str):
                outgoing.append(outgoing_relation)
        return relation_type, ObjectProperty(relation_type, incoming, outgoing)

    def __dict__(self):
        return {
            RELATION_TAG: self.relation.iri,
            INCOMING_TAG: [e.uri if isinstance(e, ThingObject) else e for e in self.incoming_relations],
            OUTGOING_TAG: [e.uri if isinstance(e, ThingObject) else e for e in self.outgoing_relations]
        }

    def __repr__(self):
        return f'{self.relation.iri}, in:={self.incoming_relations}, out:={self.outgoing_relations}'

    @staticmethod
    def create_from_list(param: List[dict]) -> Dict[OntologyPropertyReference, 'ObjectProperty']:
        return dict([ObjectProperty.create_from_dict(p) for p in param])


class Ontology(object):
    """
    Ontology
    --------
    The ontology consists of classes and properties.
    """

    def __init__(self):
        self.__classes: Dict[str, OntologyClass] = {}
        self.__data_properties: Dict[str, OntologyProperty] = {}
        self.__object_properties: Dict[str, OntologyProperty] = {}

    def add_class(self, class_obj: OntologyClass):
        """
        Adding class object.

        Parameters
        ----------
        class_obj: OntologyClass
            Class object
        """
        self.__classes[class_obj.reference.iri] = class_obj

    def add_properties(self, prop_obj: OntologyProperty):
        """
        Adding properties.

        Parameters
        ----------
        prop_obj: OntologyProperty
        """
        if prop_obj.is_data_property:
            self.__data_properties[prop_obj.reference.iri] = prop_obj
        else:
            self.__object_properties[prop_obj.reference.iri] = prop_obj

    @property
    def data_properties(self) -> List[OntologyProperty]:
        """All data properties."""
        return list(self.__data_properties.values())

    @property
    def object_properties(self) -> List[OntologyProperty]:
        """All object properties."""
        return list(self.__object_properties.values())

    @property
    def classes(self) -> List[OntologyClass]:
        """All classes."""
        return list(self.__classes.values())

    def __check_hierarchy__(self, clz: OntologyClassReference, domain: OntologyClassReference) -> bool:
        current_clz: OntologyClass = self.get_class(clz)
        while current_clz is not None:
            if current_clz.reference == domain:
                return True
            current_clz = self.get_class(current_clz.subclass_of)
        return False

    def get_class(self, class_reference: OntologyClassReference) -> Optional[OntologyClass]:
        """
        Get class instance by reference.

        Parameters
        ----------
        class_reference: OntologyClassReference
            Class reference

        Returns
        --------
        instance: Optional[OntologyClass]
            Instance of ontology class.
        """
        return self.__classes.get(class_reference.iri)

    def get_object_properties(self, property_reference: OntologyPropertyReference) -> Optional[OntologyProperty]:
        """
        Get object property instance by reference.

        Parameters
        ----------
        property_reference: OntologyPropertyReference
            Property reference

        Returns
        --------
        instance: Optional[OntologyProperty]
            Instance of ontology object property.
        """
        return self.__object_properties.get(property_reference.iri)

    def get_data_properties(self, property_reference: OntologyPropertyReference) -> Optional[OntologyProperty]:
        """
        Get object property instance by reference.

        Parameters
        ----------
        property_reference: OntologyPropertyReference
            Property reference

        Returns
        --------
        instance: Optional[OntologyProperty]
            Instance of ontology object property.
        """
        return self.__data_properties.get(property_reference.iri)

    def data_properties_for(self, cls_reference: OntologyClassReference) -> List[OntologyPropertyReference]:
        """
        Retrieve a list of data properties.

        Parameters
        ----------
        cls_reference: OntologyClassReference
            Class of the ontology

        Returns
        -------
        data_properties: List[OntologyPropertyReference]
            List of data properties, where domain fit for the class of one of its super classes.
        """
        data_properties: List[OntologyPropertyReference] = []
        clz: Optional[OntologyClass] = self.get_class(cls_reference)
        if clz is not None:
            for dp in self.data_properties:
                if self.__check_hierarchy__(clz.reference, dp.domain):
                    data_properties.append(dp.reference)
        return data_properties

    def object_properties_for(self, cls_reference: OntologyClassReference) -> List[OntologyPropertyReference]:
        """
        Retrieve a list of object properties.

        Parameters
        ----------
        cls_reference: OntologyClassReference
            Class of the ontology

        Returns
        -------
        object_properties: List[OntologyPropertyReference]
            List of object properties, where domain fit for the class of one of its super classes.
        """
        object_properties: List[OntologyPropertyReference] = []
        clz: Optional[OntologyClass] = self.get_class(cls_reference)
        if clz is not None:
            for dp in self.object_properties:
                if self.__check_hierarchy__(clz.reference, dp.domain):
                    object_properties.append(dp.reference)
        return object_properties

    def __repr__(self):
        return f'<Ontology> : classes:= {self.classes}'


class ThingObject(abc.ABC):
    """
    ThingObject
    -----------
    Generic entity within knowledge graph.

    Each entity is derived from this object, thus all entity shares:
    - **uri**: A unique resource identity to identify the entity and reference it in relations
    - **label**: Human understandable label
    - **icon**: Visual representation of the entity
    - **description**: Description of entity
    - **concept_type**: Type of the concept
    - **concept_type_info**: Information on the concept type

    Parameters
    ----------
    label: List[Label]
        List of labels
    icon: str (optional)
        Icon
    description: List[Description] (optional)
        List of descriptions
    concept_type: OntologyClassReference
        Type of the concept
    uri: str
         URI for entity. For new entities the URI is None, as the knowledge graph backend assigns this.
    tenant_rights: TenantAccessRight
        Rights for tenants
    owner: bool
        Is the logged in user the owner of the entity
    """

    def __init__(self, label: List[Label] = None, concept_type: OntologyClassReference = THING_CLASS,
                 description: Optional[List[Description]] = None, uri: Optional[str] = None, icon: Optional[str] = None,
                 tenant_rights: TenantAccessRight = TenantAccessRight(), owner: bool = True):
        self.__uri: str = uri
        self.__icon: Optional[str] = icon
        self.__label: List[Label] = label if label else []
        self.__description: List[Description] = description if description else []
        self.__alias: List[Label] = []
        self.__concept_type: OntologyClassReference = concept_type
        self.__data_properties: Dict[OntologyPropertyReference, List[DataProperty]] = {}
        self.__object_properties: Dict[OntologyPropertyReference, ObjectProperty] = {}
        self.__tenants_rights: TenantAccessRight = tenant_rights
        self.__status_flag: EntityStatus = EntityStatus.UNKNOWN
        self.__ontology_types: Optional[Set[str]] = None
        self.__owner: bool = owner

    @property
    def uri(self) -> str:
        """Unique identifier for entity."""
        return self.__uri

    @uri.setter
    def uri(self, uri: str):
        self.__uri = uri

    @property
    def owner(self) -> bool:
        """Is current user the owner of the entity."""
        return self.__owner

    @property
    def status_flag(self) -> EntityStatus:
        """Status flag."""
        return self.__status_flag

    @status_flag.setter
    def status_flag(self, flag: EntityStatus):
        self.__status_flag = flag

    @property
    def label(self) -> List[Label]:
        """Labels of the entity."""
        return self.__label

    @label.setter
    def label(self, value: List[Label]):
        self.__label = value

    def add_label(self, label: str, language_code: LanguageCode):
        """Adding an label for entity.

        Parameters
        ----------
        label: str
            Label
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        self.__label.append(Label(label, language_code, True))

    def update_label(self, value: str, language_code: LanguageCode):
        """Update or creates a label for a specific language.

        Parameters
        ----------
        value: str
            Value to be set
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        for label in self.label:
            if label.language_code == language_code:
                label.content = value
                return
        # Label with language does not exist, so create a new label
        self.add_label(value, language_code)

    def remove_label(self, language_code: LanguageCode):
        """
        Remove label for entity if it exists for language.

        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        for idx in range(len(self.label)):
            if self.label[idx].language_code == language_code:
                del self.__label[idx]
                break

    def label_lang(self, language_code: LanguageCode) -> Optional[Label]:
        """
        Get label for language_code code.

        Parameters
        ----------
        language_code: LanguageCode
            Requested language_code code
        Returns
        -------
        label: Optional[Label]
            Returns the label for a specific language code
        """
        for label in self.label:
            if label.language_code == language_code:
                return label
        return None

    @property
    def source_system(self) -> Optional[List[DataProperty]]:
        """Source of the entity."""
        if SYSTEM_SOURCE_SYSTEM in self.__data_properties:
            return self.__data_properties[SYSTEM_SOURCE_SYSTEM]
        return None

    def add_source_system(self, value: DataProperty):
        """
        Adding the source system  of the entity.

        Parameters
        -----------
        value: DataProperty
            Adds the source system as a Data Property. **Remark:** The data property must have the property type
            'wacom:core#sourceSystem'.
        """
        if value.data_property_type != SYSTEM_SOURCE_SYSTEM:
            raise ValueError(f'Data property {value.data_property_type.iri} not supported. '
                             f'Expected:={SYSTEM_SOURCE_SYSTEM.iri}')
        if SYSTEM_SOURCE_SYSTEM not in self.__data_properties:
            self.__data_properties[SYSTEM_SOURCE_SYSTEM] = []
        for idx in range(0, len(self.__data_properties[SYSTEM_SOURCE_SYSTEM])):
            if self.__data_properties[SYSTEM_SOURCE_SYSTEM][idx].language_code == value.language_code:
                del self.__data_properties[SYSTEM_SOURCE_SYSTEM][idx]
        self.__data_properties[SYSTEM_SOURCE_SYSTEM].append(value)

    @property
    def source_reference_id(self) -> Optional[List[DataProperty]]:
        """Reference id for to the source."""
        if SYSTEM_SOURCE_REFERENCE_ID in self.__data_properties:
            return self.__data_properties[SYSTEM_SOURCE_REFERENCE_ID]
        return None

    def add_source_reference_id(self, value: DataProperty):
        """
        Adding the reference id from the source system of the entity.

        Parameters
        -----------
        value: DataProperty
            Adds the source system reference id as a Data Property.
            **Remark:** The data property must have the property type 'wacom:core#sourceReferenceId'.
        """
        if value.data_property_type != SYSTEM_SOURCE_REFERENCE_ID:
            raise ValueError(f'Data property {value.data_property_type.iri} not supported. '
                             f'Expected:={SYSTEM_SOURCE_REFERENCE_ID.iri}')
        if SYSTEM_SOURCE_REFERENCE_ID not in self.__data_properties:
            self.__data_properties[SYSTEM_SOURCE_REFERENCE_ID] = []
        for idx in range(0, len(self.__data_properties[SYSTEM_SOURCE_REFERENCE_ID])):
            if self.__data_properties[SYSTEM_SOURCE_REFERENCE_ID][idx].language_code == value.language_code:
                del self.__data_properties[SYSTEM_SOURCE_REFERENCE_ID][idx]
        self.__data_properties[SYSTEM_SOURCE_REFERENCE_ID].append(value)

    def default_source_reference_id(self, language_code: LanguageCode = LanguageCode('en_US')) -> Optional[str]:
        """
        Getting the source reference id for a certain language code.

        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

        Returns
        -------
        id: str
            Source reference id.
        """
        if SYSTEM_SOURCE_REFERENCE_ID in self.__data_properties:
            for sr in self.data_properties[SYSTEM_SOURCE_REFERENCE_ID]:
                if sr.language_code == language_code:
                    return sr.value
        return None

    @property
    def image(self) -> Optional[str]:
        """Image depicting the entities (optional)."""
        return self.__icon

    @image.setter
    def image(self, value: str):
        self.__icon = value

    @property
    def description(self) -> Optional[List[Description]]:
        """Description of the thing (optional)."""
        return self.__description

    @description.setter
    def description(self, value: List[Description]):
        self.__description = value

    def add_description(self, description: str, language_code: LanguageCode):
        """Adding an description for entity.

        Parameters
        ----------
        description: str
            Description
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        self.__description.append(Description(description=description, language_code=language_code))

    def update_description(self, value: str, language_code: LanguageCode):
        """Update or creates a description for a specific language.

        Parameters
        ----------
        value: str
            Value to be set
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        for desc in self.description:
            if desc.language_code == language_code:
                desc.content = value
                return
        # Description with language does not exist, so create a new description
        self.add_description(value, language_code)

    def description_lang(self, language_code: str) -> Optional[Description]:
        """
        Get description for entity.

        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        Returns
        -------
        label: LocalizedContent
            Returns the  label for a specific language_code code
        """
        for desc in self.description:
            if desc.language_code == language_code:
                return desc
        return None

    def remove_description(self, language_code: LanguageCode):
        """
        Remove description for entity if it exists for language.

        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        for idx in range(len(self.description)):
            if self.description[idx].language_code == language_code:
                del self.__description[idx]
                break

    @property
    def concept_type(self) -> OntologyClassReference:
        """Concept type."""
        return self.__concept_type

    @concept_type.setter
    def concept_type(self, value: OntologyClassReference):
        self.__concept_type = value

    @property
    def ontology_types(self) -> Set[str]:
        """Ontology types. For public entities."""
        return self.__ontology_types

    @ontology_types.setter
    def ontology_types(self, value: Set[str]):
        self.__ontology_types = value

    @property
    def data_properties(self) -> Dict[OntologyPropertyReference, List[DataProperty]]:
        """Literals of the concept."""
        return self.__data_properties

    @data_properties.setter
    def data_properties(self, data_properties: Dict[OntologyPropertyReference, List[DataProperty]]):
        """Literals of the concept."""
        self.__data_properties = data_properties

    @property
    def object_properties(self) -> Dict[OntologyPropertyReference, ObjectProperty]:
        """Relations of the concept."""
        return self.__object_properties

    @object_properties.setter
    def object_properties(self, relations: Dict[OntologyPropertyReference, ObjectProperty]):
        self.__object_properties = relations

    @property
    def alias(self) -> List[Label]:
        """Alternative labels of the concept."""
        return self.__alias

    @alias.setter
    def alias(self, alias: List[Label]):
        self.__alias = alias

    def alias_lang(self, language_code: LanguageCode) -> List[Label]:
        """
        Get alias for language_code code.

        Parameters
        ----------
        language_code: LanguageCode
            Requested language_code code
        Returns
        -------
        aliases: List[Label]
            Returns a list of aliases for a specific language code
        """
        aliases: List[Label] = []
        for a in self.alias:
            if a.language_code == language_code:
                aliases.append(a)
        return aliases

    def update_alias(self, value: str, language_code: LanguageCode):
        """Update or creates a alias for a specific language.

        Parameters
        ----------
        value: str
            Value to be set
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        for a in self.alias:
            if a.language_code == language_code:
                a.content = value
                return
        # Label with language does not exist, so create a new label
        self.add_alias(value, language_code=language_code)

    def add_relation(self, prop: ObjectProperty):
        """Adding a relation to the entity.

        :param prop: ObjectProperty -
            ObjectProperty
        """
        if prop.relation in self.object_properties:
            self.__object_properties[prop.relation].incoming_relations.extend(prop.incoming_relations)
            self.__object_properties[prop.relation].outgoing_relations.extend(prop.outgoing_relations)
        else:
            self.__object_properties[prop.relation] = prop

    def add_data_property(self, data_property: DataProperty):
        """Add data property to the entity.

        Parameters
        ----------
        data_property: DataProperty
            DataProperty
        """
        if data_property.data_property_type not in self.__data_properties:
            self.__data_properties[data_property.data_property_type] = []
        self.__data_properties[data_property.data_property_type].append(data_property)

    def add_alias(self, alias: str, language_code: LanguageCode):
        """Adding an alias for entity.

        Parameters
        ----------
        alias: str
            Alias
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        """
        self.__alias.append(Label(alias, language_code, False))

    @property
    def tenant_access_right(self) -> TenantAccessRight:
        """Access rights for tenant. """
        return self.__tenants_rights

    @tenant_access_right.setter
    def tenant_access_right(self, rights: TenantAccessRight):
        self.__tenants_rights = rights

    def __dict__(self):
        labels: List[Dict[str, Any]] = []
        labels.extend([la.__dict__() for la in self.label])
        labels.extend([la.__dict__() for la in self.alias])
        dict_object: Dict[str, Any] = {
            URI_TAG: self.uri,
            IMAGE_TAG: self.image,
            LABELS_TAG: labels,
            DESCRIPTIONS_TAG: [desc.__dict__() for desc in self.description],
            TYPE_TAG: self.concept_type.iri,
            STATUS_FLAG_TAG: self.status_flag.value,
            DATA_PROPERTIES_TAG: {},
            OBJECT_PROPERTIES_TAG: {},
            OWNER_TAG: self.owner
        }
        for literal_type, items in self.data_properties.items():
            dict_object[DATA_PROPERTIES_TAG][literal_type.iri] = [i.__dict__() for i in items]
        for relation_type, item in self.object_properties.items():
            dict_object[OBJECT_PROPERTIES_TAG][relation_type.iri] = item.__dict__()

        return dict_object

    @staticmethod
    def from_dict(entity: Dict[str, Any]) -> 'ThingObject':
        labels: List[Label] = []
        alias: List[Label] = []
        descriptions: List[Description] = []

        for label in entity[LABELS_TAG]:
            if label[IS_MAIN_TAG]:
                labels.append(Label.create_from_dict(label))
            else:
                alias.append(Label.create_from_dict(label))

        for desc in entity[DESCRIPTIONS_TAG]:
            descriptions.append(Description.create_from_dict(desc))

        thing: ThingObject = ThingObject(label=labels, icon=entity[IMAGE_TAG], description=descriptions,
                                         uri=entity[URI_TAG],
                                         concept_type=OntologyClassReference.parse(entity[TYPE_TAG]),
                                         owner=entity.get(OWNER_TAG, True))
        if DATA_PROPERTIES_TAG in entity:
            if isinstance(entity[DATA_PROPERTIES_TAG], dict):
                for data_property_type_str, data_properties in entity[DATA_PROPERTIES_TAG].items():
                    data_property_type: OntologyPropertyReference = \
                        OntologyPropertyReference.parse(data_property_type_str)
                    for data_property in data_properties:
                        language_code: LanguageCode = LanguageCode(data_property[LANGUAGE_CODE_TAG])
                        value: str = data_property[VALUE_TAG]
                        thing.add_data_property(DataProperty(value, data_property_type, language_code))
            elif isinstance(entity[DATA_PROPERTIES_TAG], list):
                for data_property in entity[DATA_PROPERTIES_TAG]:
                    language_code: LanguageCode = LanguageCode(data_property[LANGUAGE_CODE_TAG])
                    value: str = data_property[VALUE_TAG]
                    data_property_type: OntologyPropertyReference = \
                        OntologyPropertyReference.parse(data_property[DATA_PROPERTY_TAG])
                    thing.add_data_property(DataProperty(value, data_property_type, language_code))
        if OBJECT_PROPERTIES_TAG in entity:
            for object_property in entity[OBJECT_PROPERTIES_TAG].values():
                prop, obj = ObjectProperty.create_from_dict(object_property)
                thing.add_relation(obj)
        thing.alias = alias
        # Finally, retrieve rights
        if TENANT_RIGHTS_TAG in entity:
            thing.tenant_access_right = TenantAccessRight.parse(entity[TENANT_RIGHTS_TAG])
        return thing

    def __hash__(self):
        return 0

    def __eq__(self, other):
        # another object is equal to self, iff
        # it is an instance of MyClass
        return isinstance(other, ThingObject) and other.uri == self.uri

    def __repr__(self):
        return f'<{self.concept_type.iri if self.__concept_type else "UNSET"}: uri:={self.uri}, labels:={self.label}, '\
               f'tenant access right:={self.tenant_access_right}]>'


# -------------------------------------------------- Encoder -----------------------------------------------------------
class ThingEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Label):
            return o.__dict__()
        elif isinstance(o, Description):
            return o.__dict__()
        elif isinstance(o, ThingObject):
            return o.__dict__()
        return str(o)
