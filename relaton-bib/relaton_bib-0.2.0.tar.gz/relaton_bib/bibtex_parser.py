import datetime
from typing import List

import bibtexparser
from bibtexparser.bparser import BibTexParser
import iso639

from .bibliographic_date import BibliographicDate, BibliographicDateType
from .bibliographic_item import BibliographicItem, BibliographicItemType
from .bib_item_locality import BibItemLocality
from .biblio_note import BiblioNote
from .classification import Classification
from .contribution_info import ContributionInfo, ContributorRole, \
                               ContributorRoleType
from .document_identifier import DocumentIdentifier
from .document_relation import DocumentRelation
from .formatted_string import FormattedString
from .localized_string import LocalizedString
from .person import Person, FullName
from .place import Place
from .series import Series, SeriesType
from .typed_title_string import TypedTitleString, TypedTitleStringCollection
from .typed_uri import TypedUri
from .organization import Organization


def from_bibtex(bibtex: str) -> dict:
    # https://github.com/sciunto-org/python-bibtexparser/issues/280#issuecomment-932478235
    parser = BibTexParser(common_strings=True)
    bt = bibtexparser.loads(bibtex, parser)

    return {e["ID"]: BibliographicItem(
        id=e["ID"],
        docidentifier=_fetch_docid(e),
        fetched=_fetch_fetched(e),
        type=_fetch_type(e),
        title=_fetch_title(e),
        contributor=_fetch_contributor(e),
        date=_fetch_date(e),
        place=_fetch_place(e),
        biblionote=_fetch_note(e),
        relation=_fetch_relation(e),
        extent=_fetch_extent(e),
        edition=e.get("edition"),
        series=_fetch_series(e),
        link=_fetch_link(e),
        language=_fetch_language(e),
        classification=_fetch_classification(e),
        keyword=_fetch_keyword(e)) for e in bt.entries}


def _fetch_docid(bibtex: dict) \
        -> List[DocumentIdentifier]:
    docid = []

    for key in ["isbn", "lccn", "isbn"]:
        value = bibtex.get(key)
        if value:
            docid.append(DocumentIdentifier(id=value, type=key))

    return docid


def _fetch_fetched(bibtex: dict) -> datetime.datetime:
    # TODO replace strptime with
    # https://dateutil.readthedocs.io/en/stable/index.html
    # to support more formats
    timestamp = bibtex.get("timestamp")
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") \
        if timestamp else None


def _fetch_type(bibtex: dict) -> str:
    # todo move all string constants to enums
    t = bibtex.get("type")
    if t in ["mastersthesis", "phdthesis"]:
        return BibliographicItemType.THESIS.value
    elif t == "conference":
        return BibliographicItemType.INPROCEEDINGS.value
    elif t == "misc":
        return BibliographicItemType.STANDARD.value
    else:
        return str(t)


def _fetch_place(bibtex: dict) -> List[Place]:
    address = bibtex.get("address")
    return [Place(address)] if address else []


def _fetch_title(bibtex: dict) -> TypedTitleStringCollection:
    titles = []
    for key in ["title", "subtitle"]:
        value = bibtex.get(key)
        if value:
            titles.append(TypedTitleString(type="main", content=value))
    return TypedTitleStringCollection(titles)


def _fetch_contributor(bibtex: dict) -> List[ContributionInfo]:
    contributor = []

    for key in [ContributorRoleType.AUTHOR, ContributorRoleType.EDITOR]:
        for entity in _fetch_person(bibtex.get(key)):
            contributor.append(
                ContributionInfo(entity=entity,
                                 role=[ContributorRole(type=key)]))

    for key in [ContributorRoleType.PUBLISHER,
                ContributorRoleType.INSTITUTION,
                ContributorRoleType.ORGANIZATION,
                ContributorRoleType.SCHOOL]:
        value = bibtex.get(key)
        if value:
            is_publisher = key == "publisher"
            descr = [] if is_publisher \
                else [FormattedString(content="sponsor")]
            entity_cls = Person if is_publisher else Organization
            contributor.append(
                ContributionInfo(
                    entity=entity_cls(name=value),
                    role=[ContributorRole(type=key, description=descr)]))

    return contributor


def _fetch_person(person) -> List[Person]:
    if not person:
        return []

    result = []
    for name in person:
        parts = name.split(", ")
        surname = LocalizedString(parts[0])
        fname = parts[1].split(" ") if len(parts) > 1 else []
        forename = [LocalizedString(fn) for fn in fname]
        pname = FullName(surname=surname, forename=forename)
        result.append(Person(name=pname))

    return result


def _fetch_date(bibtex: dict) -> List[BibliographicDate]:
    date = []
    year = bibtex.get("year")
    if year:
        on = datetime.date(int(year), int(bibtex.get("month_numeric",  1)), 1)
        date.append(BibliographicDate(
            type=BibliographicDateType.PUBLISHED, on=on))

    urldate = bibtex.get("urldate")
    if urldate:
        on = datetime.datetime.strptime(urldate, "%Y-%m-%d").date()
        date.append(BibliographicDate(
            type=BibliographicDateType.ACCESSED, on=on))

    return date


def _fetch_note(bibtex: dict) -> List[BiblioNote]:
    types = ["annote", "howpublished", "comment", "note", "content"]
    mapping = {"note": None, "content": "tableOfContents"}
    return [BiblioNote(type=mapping.get(k, k), content=bibtex.get(k))
            for k in types if k in bibtex]


def _fetch_relation(bibtex: dict) -> TypedTitleStringCollection:
    booktitle = bibtex.get("booktitle")
    if not booktitle:
        return []

    ttl = TypedTitleString(type=TypedTitleString.Type.MAIN, content=booktitle)
    title = TypedTitleStringCollection([ttl])
    return DocumentRelation(type=DocumentRelation.Type.partOf,
                            bibitem=BibliographicItem(title=title))


def _fetch_extent(bibtex: dict) -> List[BibItemLocality]:
    result = []
    for key in ["chapter", "pages", "volume"]:
        value = bibtex.get(key)
        if value:
            t = key
            if key == "pages":
                t = "page"
                from_, to = value.split("-")
            else:
                from_, to = (value, None)

            result.append(BibItemLocality(t, from_, to))

    return result


def _fetch_series(bibtex: dict) -> List[Series]:
    result = []
    journal = bibtex.get("journal")
    if journal:
        result.append(Series(
            type=SeriesType.JOURNAL,
            title=TypedTitleString(content=journal),
            number=bibtex.get("number")))
    series = bibtex.get("series")
    if series:
        result.append(Series(
            title=TypedTitleString(content=series)))
    return result
    pass


def _fetch_link(bibtex: dict) -> List[TypedUri]:
    link = []

    for key in ["url", "doi", "file2"]:
        value = bibtex.get(key)
        if value:
            t = "file" if key == "file2" else key
            link.append(TypedUri(type=t, content=value))

    return link


def _fetch_language(bibtex: dict) -> List[str]:
    lang = bibtex.get("language")
    if not lang:
        return []

    return [iso639.languages.get(name=lang.capitalize()).alpha2]


def _fetch_classification(bibtex: dict) -> List[Classification]:
    cls = []

    for key in ["type", "keyword", "mendeley-tags"]:
        value = bibtex.get(key)
        if value:
            t = "mendeley" if key == "mendeley-tags" else key
            cls.append(Classification(type=t, value=value))

    return cls


def _fetch_keyword(bibtex: dict) -> List[str]:
    keywords = bibtex.get("keywords")
    return map(lambda s: LocalizedString(s), keywords.split(", ")) \
        if keywords else []
