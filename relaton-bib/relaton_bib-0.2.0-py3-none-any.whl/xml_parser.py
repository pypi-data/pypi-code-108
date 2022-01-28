import logging
import xml.etree.ElementTree as ET
import dateutil.parser as DU
from typing import List, Union

from .address import Address
from .affiliation import Affiliation
from .biblio_version import BibliographicItemVersion
from .bibliographic_date import BibliographicDate, BibliographicDateType
from .bibliographic_item import BibliographicItem
from .biblio_note import BiblioNoteCollection, BiblioNote
from .bib_item_locality import Locality, BibItemLocality, LocalityStack, \
    SourceLocalityStack, SourceLocality
from .contact import Contact, ContactType
from .classification import Classification
from .contribution_info import ContributionInfo, ContributorRole
from .copyright_association import CopyrightAssociation
from .document_identifier import DocumentIdentifier
from .document_relation import DocumentRelation
from .document_status import DocumentStatus
from .editorial_group import EditorialGroup
from .formatted_ref import FormattedRef
from .formatted_string import FormattedString, FormattedStringFormat
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


def from_xml(xml: Union[ET.ElementTree, ET.Element]) -> BibliographicItem:
    bibitem = xml.getroot() if isinstance(xml, ET.ElementTree) else xml
    if bibitem.tag in ["bibitem", "bibdata"]:
        return _fetch_bibliographic_item(bibitem)
    else:
        logging.warning(
            "[relaton-bib] WARNING: "
            "can't find bibitem or bibdata element in the XML")


def _fetch_bibliographic_item(bibitem: ET.Element):
    fetched = bibitem.find("./fetched")
    if fetched is not None:
        fetched = DU.parse(fetched.text)
    docnumber = bibitem.find("./docnumber")
    if docnumber is not None:
        docnumber = docnumber.text
    edition = bibitem.find("./edition")
    if edition is not None:
        edition = edition.text
    ext = bibitem.find("./ext")
    doctype = None
    subdoctype = None
    if ext is not None:
        doctype = ext.find("doctype")
        if doctype is not None:
            doctype = doctype.text

        subdoctype = ext.find("subdoctype")
        if subdoctype is not None:
            subdoctype = subdoctype.text

    return BibliographicItem(
        id=bibitem.get("id", None),
        type=bibitem.get("type", None),
        fetched=fetched,
        title=_fetch_titles(bibitem),
        formattedref=_fref(bibitem),
        link=_fetch_link(bibitem),
        docidentifier=_fetch_docid(bibitem),
        docnumber=docnumber,
        date=_fetch_dates(bibitem),
        contributor=_fetch_contributors(bibitem),
        edition=edition,
        version=_fetch_version(bibitem),
        biblionote=_fetch_note(bibitem),
        language=_fetch_list(bibitem, "./language"),
        script=_fetch_list(bibitem, "./script"),
        abstract=_fetch_abstract(bibitem),
        status=_fetch_status(bibitem),
        copyright=_fetch_copyright(bibitem),
        relation=_fetch_relations(bibitem),
        series=_fetch_series(bibitem),
        medium=_fetch_medium(bibitem),
        place=_fetch_place(bibitem),
        extent=_fetch_extent(bibitem),
        accesslocation=_fetch_list(bibitem, "./accesslocation"),
        classification=_fetch_classification(bibitem),
        keyword=_fetch_list(bibitem, "./keyword"),
        license=_fetch_list(bibitem, "./license"),
        validity=_fetch_validity(bibitem),
        doctype=doctype,
        subdoctype=subdoctype,
        editorialgroup=_fetch_editorialgroup(ext),
        ics=_fetch_ics(ext),
        structuredidentifier=_fetch_structuredidentifier(ext),
    )


def _fetch_titles(item: ET.Element) -> TypedTitleStringCollection:
    return TypedTitleStringCollection(list(map(
        lambda t: _ttitle(t), item.findall("./title"))))


def _fetch_version(item: ET.Element) -> BibliographicItemVersion:
    version = item.find("./version")
    if not version:
        return

    rev_date = version.find("revision-date")
    if rev_date is not None:
        rev_date = rev_date.text
    draft = _fetch_list(version, "draft")

    return BibliographicItemVersion(revision_date=rev_date, draft=draft)


def _fetch_place(item: ET.Element) -> List[Place]:
    return list(map(
        lambda pl: Place(name=pl.text,
                         uri=pl.get("uri"),
                         region=pl.get("region")),
        item.findall("./place")))


def _fetch_note(item: ET.Element) -> BiblioNoteCollection:
    return BiblioNoteCollection(list(map(
        lambda n: BiblioNote(content=n.text, **n.attrib),
        item.findall("./note"))))


def _fetch_list(item: ET.Element, xpath: str) -> List[str]:
    if item is None:
        return []
    return list(map(
        lambda l: l.text,
        item.findall(xpath)))


def _fetch_series(item: ET.Element) -> List[Series]:
    result = []
    for sr in item.findall("./series"):
        abbr = sr.find("abbreviation")
        if abbr is not None:
            abbr = _localized_str(abbr)

        formattedref = _fref(sr)
        title = _ttitle(sr.find("title"))
        if not (formattedref or title):
            continue

        props = {p: n.text
                 for p in ["place",
                           "organization",
                           "from",
                           "to",
                           "number",
                           "partnumber"] if (n := sr.find(p)) is not None}

        result.append(Series(
            type=sr.get("type"),
            formattedref=formattedref,
            title=title,
            place=props.get("place"),
            organization=props.get("organization"),
            abbreviation=abbr,
            from_=props.get("from"),
            to=props.get("to"),
            number=props.get("number"),
            partnumber=props.get("partnumber")))
    return result


def _fetch_medium(item: ET.Element) -> Medium:
    medium = item.find("./medium")
    if not medium:
        return

    props = {p: n.text
             for p in ["form", "size", "scale"]
             if (n := medium.find(p)) is not None}

    return Medium(**props)


def _fetch_extent(item: ET.Element) -> List[BibItemLocality]:
    result = []

    for ext in item.findall("./extent"):
        type = ext.get("type")
        reference_from = ext.find("referenceFrom")
        if reference_from is not None:
            reference_from = reference_from.text
        reference_to = ext.find("referenceTo")
        if reference_to is not None:
            reference_to = reference_to.text
        result.append(BibItemLocality(
            type=type,
            reference_from=reference_from,
            reference_to=reference_to))

    return result


def _fetch_classification(item: ET.Element) -> List[Classification]:
    return list(map(
        lambda cls: Classification(type=cls.get("type"),
                                   value=cls.text),
        item.findall("./classification")))


def _fetch_validity(item: ET.Element) -> Validity:
    validity = item.find("./validity")
    if validity is None:
        return

    begins = validity.find("validityBegins")
    if begins is not None:
        begins = DU.parse(begins.text)
    ends = validity.find("validityEnds")
    if ends is not None:
        ends = DU.parse(ends.text)
    revision = validity.find("revision")
    if revision is not None:
        revision = DU.parse(revision.text)

    props = {p: DU.parse(n.text)
             for t, p in {"validityBegins": "begins",
                          "validityEnds": "ends",
                          "revision": "revision"}.items()
             if (n := validity.find(t)) is not None}

    return Validity(**props)


def _fetch_docid(item: ET.Element) -> List[DocumentIdentifier]:
    return list(map(
        lambda did: DocumentIdentifier(id=did.text,
                                       type=did.get("type"),
                                       scope=did.get("scope")),
        item.findall("./docidentifier")))


def _ttitle(title: ET.Element) -> TypedTitleString:
    if title is None:
        return []

    content = _localized_strs(title, "./variant")
    if not any(content):
        content = title.text

    props = title.attrib.copy()
    props["content"] = content

    return TypedTitleString(**props)


def _localized_strs(node: ET.Element, xpath: str) -> List[LocalizedString]:
    return list(map(
        lambda v: _localized_str(v),
        node.findall(xpath)))


def _fetch_status(item: ET.Element) -> DocumentStatus:
    status = item.find("./status")
    if status is None:
        return

    stg = status.find("stage")
    iter = status.find("iteration")
    if iter is not None:
        iter = iter.text
    return DocumentStatus(
        stage=status.text if stg is None else _stage(stg),
        substage=_stage(status.find("substage")),
        iteration=iter,
    )


def _stage(node: ET.Element) -> DocumentStatus.Stage:
    if node is None:
        return

    return DocumentStatus.Stage(
        value=node.text,
        abbreviation=node.get("abbreviation"))


def _fetch_dates(item: ET.Element) -> List[BibliographicDate]:
    result = []
    for d in item.findall("./date"):
        props = {p: n.text
                 for p in ["on", "from", "to"]
                 if (n := d.find(p)) is not None}
        props["type"] = d.get("type", BibliographicDateType.PUBLISHED)
        if "from" in props:
            props["from_"] = props.pop("from")
        elif "on" not in props:
            continue

        result.append(BibliographicDate(**props))

    return result


def _get_org(org: ET.Element) -> Organization:
    props = {p: n.text
             for p in ["abbreviation", "uri"]
             if (n := org.find(p)) is not None}
    props["name"] = list(map(
        lambda n: _localized_str(n),
        org.findall(f"./name")))
    props["identifier"] = list(map(
        lambda i: OrgIdentifier(value=i.text,
                                type=i.get("type")),
        org.findall(f"./identifier")))

    props["subdivision"] = _fetch_list(org, "subdivision")
    return Organization(**props)


def _get_person(person: ET.Element) -> Person:
    affiliations = []
    for a in person.findall("./affiliation"):
        desc = list(map(
            lambda d: _formatted_str(d), a.findall("./description")))
        affiliations.append(
            Affiliation(
                organization=_get_org(a.find("./organization")),
                description=desc
            )
        )

    contact = []
    for c in list(person):
        if c.tag == ContactType.ADDRESS:
            props = {p: n.text
                     for p in ["city", "state", "country", "postcode"]
                     if (n := c.find(p)) is not None}
            props["street"] = _fetch_list(c, "./street")
            contact.append(Address(**props))
        elif c.tag in [ContactType.PHONE,
                       ContactType.EMAIL,
                       ContactType.URI]:
            contact.append(Contact(type=c.tag, value=c.text))

    identifier = list(map(
        lambda pi: PersonIdentifier(type=pi.get("type"), value=pi.text),
        person.findall("./identifier")))

    fullname_props = dict(
        initial=_name_part(person, "initial"),
        forename=_name_part(person, "forename"),
        addition=_name_part(person, "addition"),
        prefix=_name_part(person, "prefix"))

    if (cname := person.find("./name/completename")) is not None:
        fullname_props["completename"] = _localized_str(cname)
    if (sname := person.find("./name/surname")) is not None:
        fullname_props["surname"] = _localized_str(sname)

    name = FullName(**fullname_props)

    return Person(
        name=name,
        affiliation=affiliations,
        contact=contact,
        identifier=identifier)


def _name_part(person: ET.Element, part: str) -> List[LocalizedString]:
    return list(map(
        lambda v: _localized_str(v),
        person.findall(f"./name/{part}")))


def _fetch_contributors(item: ET.Element) -> List[ContributionInfo]:
    result = []
    for c in item.findall("./contributor"):
        entity = None
        if (org := c.find("./organization")) is not None:
            entity = _get_org(org)
        elif (person := c.find("./person")) is not None:
            entity = _get_person(person)

        role = list(map(
            lambda r: ContributorRole(
                type=r.get("type"),
                description=_localized_strs(r, "./description")),
            c.findall("./role")))
        result.append(ContributionInfo(entity=entity, role=role))
    return result


def _fetch_abstract(item: ET.Element) -> List[FormattedString]:
    return list(map(lambda a: _formatted_str(a), item.findall("./abstract")))


def _fetch_copyright(item: ET.Element) -> List[TypedUri]:
    result = []
    for cp in item.findall("./copyright"):
        props = {p: n.text
                 for p in ["from", "to", "scope"]
                 if (n := cp.find(p)) is not None}
        props["from_"] = props.pop("from")
        props["owner"] = list(map(
            lambda o: ContributionInfo(
                entity=_get_org(o.find("organization"))),
            cp.findall("owner")))

        result.append(CopyrightAssociation(**props))
    return result


def _fetch_link(item: ET.Element) -> List[TypedUri]:
    return list(map(
        lambda l: TypedUri(type=l.get("type"), content=l.text),
        item.findall("./uri")))


def _fetch_relations(item: ET.Element, klass=DocumentRelation):
    result = []
    for rel in item.findall("./relation"):
        result.append(klass(
            type=rel.get("type"),
            description=_relation_description(rel),
            bibitem=_fetch_bibliographic_item(rel.find("./bibitem")),
            locality=_localities(rel),
            source_locality=_source_localities(rel),
        ))
    return result


def _relation_description(rel: ET.Element) -> FormattedString:
    d = rel.find("./description")
    if d is None:
        return

    return _formatted_str(d)


def _formatted_str(node: ET.Element) -> FormattedString:
    return FormattedString(content=node.text,
                           language=node.get("language", []),
                           script=node.get("script", []),
                           format=node.get("format",
                                           FormattedStringFormat.TEXT_PLAIN))


def _localized_str(node: ET.Element) -> LocalizedString:
    return LocalizedString(content=node.text,
                           language=node.get("language", []),
                           script=node.get("script", []))


def _localities(loc: ET.Element) -> List[LocalityStack]:
    result = []
    for lc in list(loc):
        if lc.tag not in ["locality", "localityStack"]:
            continue
        lcs = None
        if lc.get("type"):
            lcs = [_locality(lc)]
        else:
            lcs = list(filter(None, map(
                lambda l: _locality(l), lc.findall("./locality"))))
        result.append(LocalityStack(lcs))
    return result


def _locality(loc: ET.Element, klass=Locality):
    to = None
    if (rt := loc.find("./referenceTo")) is not None:
        to = LocalizedString(rt.text)
    fr0m = None
    if (rf := loc.find("./referenceFrom")) is not None:
        fr0m = LocalizedString(rf.text)

    return klass(
        type=loc.get("type"),
        reference_from=fr0m,
        reference_to=to
    )


def _source_localities(rel: ET.Element) -> List[SourceLocalityStack]:
    result = []
    for lc in list(rel):
        if lc.tag not in ["sourceLocality", "sourceLocalityStack"]:
            continue
        sls = None
        if lc.get("type"):
            sls = [_locality(lc, SourceLocality)]
        else:
            sls = list(filter(None, map(
                lambda l: _locality(l, SourceLocality),
                lc.findall("./sourceLocality"))))
        result.append(SourceLocalityStack(sls))
    return result


def _fref(item: ET.Element) -> FormattedRef:
    if not item:
        return
    ident = item.find("./formattedref")
    if ident is None:
        return

    return FormattedRef(
        content=ident.text,
        format=ident.get("format", FormattedStringFormat.TEXT_PLAIN),
        language=ident.get("language", []),
        script=ident.get("script", []))


def _fetch_editorialgroup(ext: ET.Element) -> EditorialGroup:
    if ext is None:
        return
    eg = ext.find("editorialgroup")
    if eg is None:
        return

    return EditorialGroup(list(map(
        lambda tc: TechnicalCommittee(
            WorkGroup(name=tc.text,
                      number=int(tc.get("number")),
                      type=tc.get("type"),
                      identifier=tc.get("identifier"),
                      prefix=tc.get("prefix"))),
        eg.findall("./technical-committee"))))


def _fetch_ics(ext: ET.Element) -> List[ICS]:
    if ext is None:
        return []

    result = []
    for ics in ext.findall("ics"):
        props = {p: n.text
                 for p in ["code", "text"]
                 if (n := ics.find(p)) is not None}
        result.append(ICS(**props))
    return result


def _fetch_structuredidentifier(ext: ET.Element) -> StructuredIdentifier:
    if ext is None:
        return

    sids = []
    for si in ext.findall("structuredidentifier"):
        agency = _fetch_list(si, "agency")
        class_ = si.find("class")
        if class_ is not None:
            class_ = class_.text
        props = {p: n.text
                 for p in ["docnumber",
                           "partnumber",
                           "edition",
                           "version",
                           "supplementtype",
                           "supplementnumber",
                           "language",
                           "year"] if (n := si.find(p)) is not None}
        sids.append(StructuredIdentifier(
            type=si.get("type"),
            agency=agency,
            class_=class_,
            docnumber=props.get("docnumber"),
            partnumber=props.get("partnumber"),
            edition=props.get("edition"),
            version=props.get("version"),
            supplementtype=props.get("supplementtype"),
            supplementnumber=props.get("supplementnumber"),
            language=props.get("language"),
            year=props.get("year")))
    return StructuredIdentifierCollection(sids)
