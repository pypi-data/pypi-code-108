"""Top-level package for relaton-bib."""

__author__ = """Aliaksandr Babrykovich"""
__email__ = 'abobrikovich@gmail.com'
__version__ = '0.1.0'

from .address import Address
from .affiliation import Affiliation
from .bib_item_locality import BibItemLocality, Locality, \
    BibItemLocalityType, SourceLocalityStack, SourceLocality, LocalityStack
from .biblio_note import BiblioNote, BiblioNoteCollection
from .biblio_version import BibliographicItemVersion
from .bibliographic_date import BibliographicDate, BibliographicDateType
from .bibliographic_item import BibliographicItem, BibliographicItemType
from .classification import Classification
from .contact import Contact, ContactType
from .contributor import Contributor
from .contribution_info import ContributionInfo, ContributorRole
from .copyright_association import CopyrightAssociation
from .document_identifier import DocumentIdentifier, DocumentIdType
from .document_relation_collection import DocRelationCollection
from .document_relation import DocumentRelation
from .document_status import DocumentStatus
from .editorial_group import EditorialGroup
from .formatted_ref import FormattedRef
from .formatted_string import FormattedString, FormattedStringFormat
from .hit import Hit
from .hit_collection import HitCollection
from .ics import ICS
from .organization import Organization, OrgIdentifier
from .localized_string import LocalizedString
from .medium import Medium
from .place import Place
from .person import Person, FullName, PersonIdentifier
from .series import Series, SeriesType
from .structured_identifier import StructuredIdentifier
from .structured_identifier import StructuredIdentifierCollection
from .typed_title_string import TypedTitleString, TypedTitleStringCollection
from .technical_committee import TechnicalCommittee
from .typed_uri import TypedUri
from .validity import Validity
from .workgroup import WorkGroup

from .bibtex_parser import from_bibtex
from .xml_parser import from_xml
from .dict_parser import from_dict

__all__ = [
    from_bibtex,
    from_xml,
    from_dict,
    BibliographicItem,
    BibliographicItemType,
    Address,
    Contact,
    ContactType,
    Contributor,
    Hit,
    HitCollection,
    Affiliation,
    TypedUri,
    DocumentIdentifier, DocumentIdType,
    CopyrightAssociation,
    FormattedString, FormattedStringFormat,
    ContributionInfo, ContributorRole,
    BibliographicDate, BibliographicDateType,
    Series, SeriesType,
    DocumentStatus,
    Organization, OrgIdentifier,
    LocalizedString,
    TypedTitleString, TypedTitleStringCollection,
    TechnicalCommittee,
    FormattedRef,
    Medium,
    Classification,
    Validity,
    BibItemLocality,
    Locality,
    BibItemLocalityType,
    SourceLocalityStack,
    SourceLocality,
    LocalityStack,
    BiblioNote,
    BiblioNoteCollection,
    BibliographicItemVersion,
    Place,
    Person, FullName, PersonIdentifier,
    StructuredIdentifierCollection,
    EditorialGroup,
    ICS,
    DocRelationCollection,
    DocumentRelation,
    WorkGroup,
    StructuredIdentifier
]
