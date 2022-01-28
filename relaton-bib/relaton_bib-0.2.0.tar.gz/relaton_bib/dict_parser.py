import re
import datetime
from typing import Union, Dict, List

import dateutil.parser as DU

from .address import Address
from .affiliation import Affiliation
from .biblio_version import BibliographicItemVersion
from .bibliographic_date import BibliographicDate
from .bibliographic_item import BibliographicItem
from .biblio_note import BiblioNoteCollection, BiblioNote
from .bib_item_locality import Locality, BibItemLocality, LocalityStack, \
    SourceLocalityStack, SourceLocality
from .contact import Contact
from .classification import Classification
from .contribution_info import ContributionInfo, ContributorRole
from .copyright_association import CopyrightAssociation
from .document_identifier import DocumentIdentifier
from .document_relation import DocumentRelation
from .document_status import DocumentStatus
from .editorial_group import EditorialGroup
from .formatted_ref import FormattedRef
from .formatted_string import FormattedString
from .ics import ICS
from .localized_string import LocalizedString
from .person import Person, FullName, PersonIdentifier
from .place import Place
from .series import Series
from .structured_identifier import StructuredIdentifier, \
    StructuredIdentifierCollection
from .technical_committee import TechnicalCommittee
from .typed_title_string import TypedTitleString, TypedTitleStringCollection
from .typed_uri import TypedUri
from .organization import Organization, OrgIdentifier
from .medium import Medium
from .validity import Validity
from .workgroup import WorkGroup

from .relaton_bib import dict_replace_key


def from_dict(item: Dict) -> BibliographicItem:
    if not isinstance(item, dict):
        return None

    return BibliographicItem(
        fetched=item.get("fetched", datetime.datetime.now()),
        id=item.get("id"),
        type=item.get("type"),
        docidentifier=_docid(item),
        docnumber=item.get("docnumber"),
        script=_array(item.get("script")),
        language=_array(item.get("language")),
        version=_version(item),
        date=_dates(item),
        title=_titles(item),
        contributor=_contributors(item),
        abstract=_abstract(item),
        copyright=_copyright(item),
        link=[TypedUri(**link) for link in _array(item.get("link"))],
        ics=[ICS(**ics) for ics in _array(item.get("ics"))],
        keyword=_array(item.get("keyword")),
        accesslocation=_array(item.get("accesslocation")),
        place=_places(item),
        extent=_extent(item),
        biblionote=_notes(item),
        formattedref=_formattedref(item.get("formattedref")),
        status=_docstatus(item),
        relation=_relations(item),
        series=_series(item),
        medium=_medium(item),
        classification=_classification(item),
        validity=_validity(item),
        license=_array(item.get("license")),
        editorialgroup=_editorialgroup(item),
        structuredidentifier=_structuredidentifiers(item)
    )


def _array(arr: Union[List, Dict, None]) -> List:
    if not arr:
        return []
    elif not isinstance(arr, List):
        return [arr]

    return arr


def _extent(dictitem: Dict) -> List[BibItemLocality]:
    extent = _array(dictitem.get("extent"))
    return [BibItemLocality(reference_from=e.get("reference_from"),
                            reference_to=e.get("reference_to"),
                            type=e.get("type")) for e in extent]


def _titles(dictitem: Dict) -> TypedTitleStringCollection:
    result = []
    for title in _array(dictitem.get("title")):
        if isinstance(title, Dict):
            result.append(TypedTitleString(**title))
        elif isinstance(title, str):
            result.append(TypedTitleString.from_string(title))

    return TypedTitleStringCollection(result) if result else None


def _dates(dictitem: Dict) -> List[BibliographicDate]:
    return [
        BibliographicDate(**dict_replace_key(
            date,
            {"value": "on", "from": "from_"}
            )) for date in _array(dictitem.get("date"))
        ]


def _version(dictitem: Dict) -> BibliographicItemVersion:
    revdate = dictitem.get("revdate")
    return BibliographicItemVersion(revision_date=revdate) if revdate else None


def _abstract(dictitem: Dict) -> List[FormattedString]:
    # return [FormattedString(**a) for a in _array(dictitem.get("abstract"))]
    result = []
    for title in _array(dictitem.get("abstract")):
        if isinstance(title, str):
            result.append(FormattedString(content=title))
        else:
            result.append(FormattedString(**title))

    return result


def _places(dictitem: Dict) -> List[Place]:
    result = []
    for pl in _array(dictitem.get("place")):
        if isinstance(pl, str):
            result.append(Place(name=pl))
        else:
            result.append(Place(**pl))

    return result


def _docid(dictitem: Dict) -> List[Place]:
    result = []
    for docid in _array(dictitem.get("docid")):
        type_search = re.search(r"^\w+(?=\s)", docid.get("id"))
        type = docid.get("type", type_search.group(0) if type_search else None)
        result.append(
            DocumentIdentifier(id=docid.get("id"),
                               type=type,
                               scope=docid.get("scope"))
        )
    return result


def _notes(dictitem: Dict) -> List[BiblioNote]:
    result = []
    for note in _array(dictitem.get("biblionote")):
        if isinstance(note, str):
            result.append(BiblioNote(content=note))
        else:
            result.append(BiblioNote(**note))

    return BiblioNoteCollection(result) if result else None


def _docstatus(dictitem: Dict) -> DocumentStatus:
    if "docstatus" in dictitem:
        docstatus = dictitem.get("docstatus")
        return DocumentStatus(
            stage=_stage(docstatus.get("stage")),
            substage=_stage(docstatus.get("substage")),
            iteration=docstatus.get("iteration")
        )
    return None


def _stage(stg: Union[str, Dict]) -> DocumentStatus.Stage:
    if not stg:
        return None

    args = {"value": stg} if isinstance(stg, str) else stg
    return DocumentStatus.Stage(**args)


def _contributors(dictitem: Dict) -> List[ContributionInfo]:
    contrib = dictitem.get("contributor")
    result = []
    for c in _array(contrib):
        roles = []
        for r in _array(c.get("role")):
            if isinstance(r, Dict):
                roles.append(ContributorRole(
                    type=r.get("type"),
                    description=_array(r.get("description"))))
            else:
                roles.append(ContributorRole(type=r))

        entity = None
        if "person" in c:
            entity = _person(c.get("person"))
        else:
            entity = _org(c.get("organization"))

        result.append(ContributionInfo(entity=entity, role=roles))

    return result


def _org(org: Dict) -> Organization:
    if not org:
        return None

    org["identifier"] = [OrgIdentifier(
                         **dict_replace_key(idft, {"id": "value"}))
                         for idft in _array(org.get("identifier"))]
    org["subdivision"] = [_localizedstring(subd)
                          for subd in _array(org.get("subdivision"))]

    return Organization(**dict_replace_key(org, {"url": "uri"}))


def _person(person: Dict) -> Person:
    return Person(
        name=_fullname(person),
        affiliation=_affiliation(person),
        contact=_contacts(person),
        identifier=_person_identifiers(person)
    )


def _fullname(person) -> FullName:
    n = person.get("name")
    return FullName(
        forename=[_localname(f, person) for f in _array(n.get("forename"))],
        initial=[_localname(f, person) for f in _array(n.get("initial"))],
        addition=[_localname(f, person) for f in _array(n.get("addition"))],
        prefix=[_localname(f, person) for f in _array(n.get("prefix"))],
        surname=_localname(n.get("surname"), person),
        completename=_localname(n.get("completename"), person))


def _person_identifiers(person: Dict) -> List[PersonIdentifier]:
    return [PersonIdentifier(**dict_replace_key(a, {"id": "value"}))
            for a in _array(person.get("identifier"))]


def _affiliation(person: Dict) -> List[Affiliation]:
    affiliation = person.get("affiliation")
    if not affiliation:
        return []

    result = []
    for a in _array(affiliation):
        descr = []
        for d in _array(a.get("description")):
            cnt = d
            if not isinstance(d, Dict):
                cnt = {"content": d}
            descr.append(FormattedString(**cnt))
        result.append(Affiliation(
            organization=_org(a.get("organization")),
            description=descr
        ))

    return result


def _contacts(person: Dict) -> List[Contact]:
    contact = person.get("contact")
    if not contact:
        return []

    result = []
    for a in _array(contact):
        if a.get("city") or a.get("country"):
            a["street"] = _array(a.pop("street"))
            result.append(Address(**a))
        else:
            result.append(Contact(**a))

    return result


def _copyright(dictitem: Dict) -> List[CopyrightAssociation]:
    result = []

    for c in _array(dictitem.get("copyright")):
        if "owner" in c:
            owner = []
            for o in _array(c.get("owner")):
                entity = None
                if "person" in c:
                    entity = _person(c.get("person"))
                else:
                    entity = _org(c.get("organization"))
                owner.append(ContributionInfo(entity=entity))
            c["owner"] = owner

        result.append(CopyrightAssociation(
            from_=DU.parse(c.get("from")),
            owner=c.get("owner")
        ))

    return result


def _relations(dictitem: Dict) -> List[DocumentRelation]:
    relations = dictitem.get("relation")
    if not relations:
        return []

    result = []
    for r in _array(relations):
        if r.get("description"):
            r["description"] = FormattedString(**r.get("description"))

        result.append(DocumentRelation(
            type=r.get("type"),
            bibitem=_relation_bibitem(r),
            description=r.get("description"),
            locality=_relation_locality(r),
            source_locality=_relation_source_locality(r)))

    return result


def _relation_bibitem(dictitem: Dict) -> DocumentRelation:
    return from_dict(dictitem["bibitem"]) if "bibitem" in dictitem else None


def _relation_locality(rel: Dict) -> List[LocalityStack]:
    result = []
    for bl in _array(rel.get("locality")):
        locality = None
        if "locality_stack" in bl:
            locality = [Locality(**ls)
                        for ls in _array(bl.get("locality_stack"))]
        else:
            locality = [Locality(**bl)]
        result.append(LocalityStack(locality=locality))
    return result


def _relation_source_locality(rel: Dict) -> List[SourceLocalityStack]:
    result = []
    src_locality = rel.get("source_locality")
    for s in _array(src_locality):
        src_locs = None
        if "source_locality_stack" in s:
            src_locs = [SourceLocality(**loc)
                        for loc in src_locality["source_locality_stack"]]
        else:
            src_locs = [SourceLocality(**s)]
        result.append(SourceLocalityStack(locality=src_locs))
    return result


def _series(dictitem: Dict) -> List[Series]:
    result = []
    for s in _array(dictitem.get("series")):
        if "formattedref" in s:
            s["formattedref"] = _formattedref(s.pop("formattedref"))

        if "title" in s:
            if not isinstance(s["title"], Dict):
                s["title"] = {"content": s.pop("title")}
            s["title"] = _typed_string(s.pop("title"))

        if "abbreviation" in s:
            s["abbreviation"] = _localizedstring(s.pop("abbreviation"))

        result.append(Series(**dict_replace_key(s, {"from": "from_"})))

    return result


def _typed_string(title: Dict) -> TypedTitleString:
    return TypedTitleString(**title)


def _medium(dictitem: Dict) -> Medium:
    return Medium(**dictitem.get("medium")) if dictitem.get("medium") else None


def _classification(dictitem: Dict) -> List[Classification]:
    return [Classification(**c)
            for c in _array(dictitem.get("classification"))]


def _validity(dictitem: Dict) -> Validity:
    if dictitem is None or dictitem.get("validity") is None:
        return None

    validity = dictitem.get("validity")

    args = dict(
        begins=_parse_validity_time(validity, "begins"),
        ends=_parse_validity_time(validity, "ends"),
        revision=_parse_validity_time(validity, "revision")
    )

    return Validity(**args)


def _parse_validity_time(val: Dict, period: str) -> datetime.datetime:
    if isinstance(val.get(period), datetime.datetime):
        return val.get(period)

    return DU.parse(val.get(period))


def _editorialgroup(dictitem: Dict) -> EditorialGroup:
    result = [TechnicalCommittee(WorkGroup(**wg))
              for wg in _array(dictitem.get("editorialgroup"))]

    return EditorialGroup(result) if result else None


def _ics(dictitem: Dict) -> List[ICS]:
    return [ICS(**ics) for ics in dictitem.get("ics")]


def _structuredidentifiers(dictitem: Dict) -> StructuredIdentifierCollection:
    result = []
    for si in _array(dictitem.get("structuredidentifier")):
        si["agency"] = _array(si.pop("agency"))
        result.append(StructuredIdentifier(
            **dict_replace_key(si, {"class": "class_"})))

    return StructuredIdentifierCollection(result) if result else None


def _localname(name: Dict, person: Dict) -> LocalizedString:
    if not name:
        return None

    result = name if isinstance(name, Dict) else {}
    if isinstance(person.get("name"), Dict):
        pname = person.get("name")
        if "language" not in result and pname.get("language"):
            result["language"] = pname.get("language")
        if "script" not in result and pname.get("script"):
            result["script"] = pname.get("script")
        result["content"] = name.get("content") if isinstance(name, Dict) \
            else name

    return LocalizedString(**result)


def _localizedstring(lst: Union[str, List, Dict]) -> LocalizedString:
    return LocalizedString(**lst) if isinstance(lst, Dict) \
        else LocalizedString(content=lst)


def _formattedref(frf: Union[str, Dict]) -> FormattedRef:
    if not frf:
        return None

    return FormattedRef(**frf) if isinstance(frf, Dict) \
        else FormattedRef(content=frf)
