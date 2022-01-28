from __future__ import annotations
import copy
import datetime
import logging
import re
import xml.etree.ElementTree as ET
import typing
from dataclasses import dataclass, field, is_dataclass
from enum import Enum
from typing import List

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

from .address import Address
from .formatted_string import FormattedString
from .contribution_info import ContributionInfo, \
    ContributorRoleType
from .contact import Contact
from .contributor import Contributor
from .copyright_association import CopyrightAssociation
from .bibliographic_date import BibliographicDate, BibliographicDateType
from .series import Series, SeriesType
from .document_status import DocumentStatus
from .localized_string import LocalizedString
from .typed_title_string import TypedTitleString, TypedTitleStringCollection
from .typed_uri import TypedUri
from .formatted_ref import FormattedRef
from .medium import Medium
from .organization import Organization
from .classification import Classification
from .validity import Validity
from .bib_item_locality import BibItemLocality
from .biblio_note import BiblioNoteCollection
from .biblio_version import BibliographicItemVersion
from .place import Place
from .person import Person
from .structured_identifier import StructuredIdentifierCollection
from .editorial_group import EditorialGroup
from .ics import ICS

from .relaton_bib import to_ds_instance

from .document_relation import *
from .document_relation_collection import *

# from .bibtex_parser import BibtexPaser
# from .xml_parser import XmlPaser


class BibliographicItemType(str, Enum):
    ARTICLE = "article"
    BOOK = "book"
    BOOKLET = "booklet"
    CONFERENCE = "conference"
    MANUAL = "manual"
    PROCEEDINGS = "proceedings"
    PRESENTATION = "presentation"
    THESIS = "thesis"
    TECHREPORT = "techreport"
    STANDARD = "standard"
    UNPUBLISHED = "unpublished"
    MAP = "map"
    ELECTRONICS = "electronics"
    RESOURCE = "resource"
    AUDIOVISUAL = "audiovisual"
    FILM = "film"
    VIDEO = "video"
    BROADCAST = "broadcast"
    GRAPHIC_WORK = "graphic_work"
    MUSIC = "music"
    PATENT = "patent"
    INBOOK = "inbook"
    INCOLLECTION = "incollection"
    INPROCEEDINGS = "inproceedings"
    JOURNAL = "journal"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class BibliographicItem:
    FETCHED_FORMAT: typing.ClassVar[str] = "%Y-%m-%d"

    id: str = None
    type: str = None
    docnumber: str = None
    edition: str = None
    doctype: str = None  # TODO check if Enum type better then str
    subdoctype: str = None
    title: TypedTitleStringCollection = field(
        default=TypedTitleStringCollection([]))
    link: List[TypedUri] = field(default_factory=list)
    docidentifier: List[DocumentIdentifier] = field(default_factory=list)
    date: List[BibliographicDate] = field(default_factory=list)
    abstract: List[FormattedString] = field(default_factory=list)
    contributor: List[ContributionInfo] = field(default_factory=list)
    version: BibliographicItemVersion = None
    biblionote: BiblioNoteCollection = field(default=BiblioNoteCollection([]))
    language: List[str] = field(default_factory=list)
    script: List[str] = field(default_factory=list)
    formattedref: FormattedRef = None
    status: DocumentStatus = None
    copyright: List[CopyrightAssociation] = field(default_factory=list)
    relation: DocRelationCollection = field(default=DocRelationCollection([]))
    series: List[Series] = field(default_factory=list)
    medium: Medium = None
    place: List[Place] = field(default_factory=list)
    extent: List[BibItemLocality] = field(default_factory=list)
    accesslocation: List[str] = field(default_factory=list)
    license: List[str] = field(default_factory=list)
    classification: List[Classification] = field(default_factory=list)
    validity: Validity = None
    fetched: datetime.date = None
    keyword: List[LocalizedString] = field(default_factory=list)
    editorialgroup: EditorialGroup = None
    ics: List[ICS] = field(default_factory=list)
    structuredidentifier: StructuredIdentifierCollection = None

    all_parts: bool = field(default=False, init=False, repr=False)
    _id_attribute: bool = field(default=True, init=False, repr=False)

    def __post_init__(self):
        if not BibliographicItemType.has_value(self.type):
            logging.warning(
                f"[relaton-bib] invalid document type: {self.type}")
        if isinstance(self.title, str):
            self.title = TypedTitleStringCollection([self.title])
        elif isinstance(self.title, list):
            self.title = TypedTitleStringCollection(self.title)

        self.date = list(map(to_ds_instance(BibliographicDate), self.date))

        self.abstract = list(map(to_ds_instance(FormattedString),
                                 self.abstract))

        self.copyright = list(map(to_ds_instance(CopyrightAssociation),
                                  self.copyright))

        if not self.id:
            self.id = self.makeid(None, False)

        self.link = list(map(to_ds_instance(TypedUri), self.link))
        self.place = list(map(to_ds_instance(Place), self.place))
        self.keyword = list(map(to_ds_instance(LocalizedString), self.keyword))
        if isinstance(self.type, BibliographicItemType):
            self.type = self.type.value

    def abstract_for_lang(self, lang=None):
        if lang:
            return next((a for a in self.abstract if lang in a.language), None)
        else:
            return self.abstract

    def makeid(self, docid, attribute=None):
        # TODO how this handled if not set
        # ORIGINAL CODE: return nil if attribute && !@id_attribute
        if attribute and not self._id_attribute:
            return None

        if not docid:
            docid = next((i for i in self.docidentifier if i.type != "DOI"),
                         None)
        if not docid:
            return None

        idstr = re.sub(r":", "-", docid.id)
        idstr = re.sub(r"\s", "", idstr)
        return idstr.strip()

    def shortref(self, identifier, opts={}):
        pubdate = next((d for d in self.date
                        if d.type == BibliographicDateType.PUBLISHED), None)
        year = "" if opts.get("no_year", False) or not pubdate else \
            f":{pubdate.value('on', 'year')}"
        if opts.get("all_parts") or self.all_parts:
            year += ": All Parts"

        return f"{self.makeid(identifier, False)}{year}"

    def to_xml(self, parent=None, opts={}):
        return self.render_xml(parent, opts)

    def to_bibtex(self, bibtex: BibDatabase = None) -> str:
        item = {"ENTRYTYPE": self._bibtex_type(), "ID": self.id}
        self._bibtex_title(item)
        if self.edition:
            item["edition"] = self.edition
        self._bibtex_author(item)
        self._bibtex_contributor(item)
        if any(self.place):
            item["address"] = self.place[0].name
        self._bibtex_note(item)
        self._bibtex_relation(item)
        self._bibtex_extent(item)
        self._bibtex_date(item)
        self._bibtex_series(item)
        self._bibtex_classification(item)
        if any(self.keyword):
            item["keywords"] = ", ".join(list(map(lambda k: k.content,
                                                  self.keyword)))
        self._bibtex_docidentifier(item)
        if self.fetched:
            item["timestamp"] = datetime.datetime.strftime(
                self.fetched,
                BibliographicItem.FETCHED_FORMAT)
        self._bibtex_link(item)
        if not bibtex:
            bibtex = BibDatabase()
        bibtex.entries.append(item)
        writer = BibTexWriter()
        writer.indent = '  '
        writer.common_strings = True
        writer.display_order = (
            "tile",
            "edition",
            "author",
            "publisher",
            "school",
            "organization",
            "institution",
            "address",
            "note",
            "annote",
            "howpublished",
            "comment",
            "content",
            "booktitle",
            "chapter",
            "pages",
            "volume",
            "year",
            "month",
            "urldate",
            "journal",
            "number",
            "series",
            "type",
            "mendeley-tags",
            "mendeley",
            "keywords",
            "isbn",
            "lccn",
            "issn",
            "timestamp",
            "url",
            "doi",
            "file2",
            "month_numeric")

        return bibtexparser.dumps(bibtex, writer)

    def title_for_lang(self, lang=None):
        return self.title.lang(lang)

    def url(self, link_type="src"):
        link = next((s for s in self.link if s.type == link_type), None)
        return link.content if link else None

    def disable_id_attribute(self):
        self._id_attribute = False

    def to_all_parts(self):
        """remove title part components and abstract"""
        me = copy.deepcopy(self)
        me.disable_id_attribute()
        me.relation.append(DocumentRelation(
            type=DocumentRelation.Type.instance,
            bibitem=self))
        for lang in me.language:
            me.title.delete_title_part()
            tm_en = " - ".join([t.title.content for t in me.title
                                if t.type != TypedTitleString.Type.MAIN
                                and lang in t.title.language])
            t = next((t.title for t in me.title
                      if t.type == TypedTitleString.Type.MAIN
                      and lang in t.title.language), None)
            if t:
                t.content = tm_en
        me.abstract = []
        for di in me.docidentifier:
            di.remove_part()
            di.all_parts()
            di.remove_date()
        me.structuredidentifier.remove_part()
        me.structuredidentifier.all_parts()
        me.structuredidentifier.remove_date()
        me.all_parts = True
        return me

    def to_most_recent_reference(self):
        me = copy.deepcopy(self)
        self.disable_id_attribute()
        me.relation.append(DocumentRelation(
            type=DocumentRelation.Type.instance,
            bibitem=self))
        me.abstract = []
        me.date = []
        for di in me.docidentifier:
            di.remove_date()
        si = me.structuredidentifier
        if si:
            si.remove_date()
        if me.id:
            me.id = re.sub(r"-[12]\d\d\d", "", me.id)
        return me

    def revdate(self):
        """If revision_date exists then returns it
           else returns published date or None"""
        if self.rev_date:
            return self.rev_date

        if self.version and self.version.revision_date:
            self.rev_date = self.version.revision_date
        else:
            published = next(
                (d.on for d in self.date
                    if d.type == BibliographicDateType.PUBLISHED),
                None)
            published = published
        return self.rev_date

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}." if prefix else prefix
        out = [] if prefix else ["[%bibitem]", "== {blank}"]

        order = ["id", "fetched", "title", "type", "docidentifier",
                 "docnumber", "edition", "language", "script", "version",
                 "biblionote", "status", "date", "abstract", "copyright",
                 "link", "medium", "place", "extent", "accesslocation",
                 "classification", "validity", "contributor", "relation",
                 "series", "doctype", "subdoctype", "formattedref", "keyword",
                 "editorialgroup", "ics", "structuredidentifier"]

        for prop in order:
            value = getattr(self, prop)

            if isinstance(value, (str)):
                out.append(f"{pref}{prop}:: {value}")
            elif isinstance(value, datetime.date):
                out.append(
                    f"{pref}{prop}:: {value.strftime(type(self).FETCHED_FORMAT)}")
            elif hasattr(value, 'to_asciibib'):
                out.append(value.to_asciibib(prefix))
            elif hasattr(value, '__iter__'):
                if len(value) == 0:
                    continue
                if is_dataclass(value[0]):
                    p = prefix
                    if prop in ["abstract", "extent", "accesslocation",
                                "keyword"]:
                        p = f"{pref}{prop}"
                    elif prop == "contributor":
                        p = "contributor.*"
                    out += [v.to_asciibib(p, len(value)) for v in value]
                else:
                    out += [f"{pref}{prop}:: {v}" for v in value]
            elif is_dataclass(value):
                out.append(value.to_asciibib(prefix))
            elif value:
                out.append(f"{pref}{prop}:: {value}")

        return "\n".join([l for l in out if l])  # drop empty lines

    def _bibtex_title(self, item: dict):
        for t in self.title:
            if t.type == TypedTitleString.Type.MAIN:
                item["tile"] = t.title.content

    def _bibtex_type(self):
        if not self.type or self.type == BibliographicItemType.STANDARD:
            return "misc"
        return self.type

    def _bibtex_author(self, item: dict):
        def filter_authors(c):
            return isinstance(c.entity, Person) and \
                ContributorRoleType.AUTHOR in list(
                    map(lambda r: r.type, c.role))
        authors = list(
            map(lambda x: x.entity,
                list(filter(filter_authors, self.contributor))))
        if not any(authors):
            return

        authors_view = []
        for a in authors:
            if a.name.surname:
                fornames = " ".join(
                    list(map(lambda fn: str(fn), a.name.forename)))
                authors_view.append(f"{str(a.name.surname)}, {fornames}")
            else:
                authors_view.append(str(a.name.completename))

        item["author"] = " and ".join(authors_view)

    def _bibtex_contributor(self, item: dict):
        for c in self.contributor:
            role_types = list(map(lambda r: r.type, c.role))

            inst_name = None
            if ContributorRoleType.PUBLISHER in role_types:
                inst_name = "publisher"
            elif ContributorRoleType.DISTRIBUTOR in role_types:
                inst_name = None
                if self.type == BibliographicItemType.TECHREPORT:
                    inst_name = "institution"
                elif self.type in [BibliographicItemType.INPROCEEDINGS,
                                   BibliographicItemType.CONFERENCE,
                                   BibliographicItemType.MANUAL,
                                   BibliographicItemType.PROCEEDINGS]:
                    inst_name = "organization"
                elif self.type in ["mastersthesis", "phdthesis"]:
                    inst_name = "school"

            if inst_name:
                item[inst_name] = c.entity.bib_name()

    def _bibtex_note(self, item: dict):
        mapping = {
            "annote": "annote",
            "howpublished": "howpublished",
            "comment": "comment",
            "tableOfContents": "content",
            None: "note"
        }
        for n in self.biblionote:
            if n.type in mapping.keys():
                item[mapping[n.type]] = n.content

    def _bibtex_relation(self, item: dict):
        rel = next(
            (r for r in self.relation
             if r.type == DocumentRelation.Type.partOf), None)
        if rel:
            title_main = next(
                (r
                 for r in rel.bibitem.title
                 if r.type == TypedTitleString.Type.MAIN), None)
            item["booktitle"] = title_main.title.content

    def _bibtex_extent(self, item: dict):
        for e in self.extent:
            if e.type in ["chapter", "volume"]:
                item[e.type] = str(e.reference_from)
            elif e.type == "page":
                value = str(e.reference_from)
                if e.reference_to:
                    value += f"-{e.reference_to}"
                item["pages"] = value

    def _bibtex_date(self, item: dict):
        for d in self.date:
            if d.type == BibliographicDateType.PUBLISHED:
                item["year"] = str(d.value("on", "year"))
                month_num = d.value("on", "month")
                month_name = datetime.date(1900, month_num, 1).strftime('%b')
                item["month"] = month_name.lower()
                item["month_numeric"] = str(month_num)
            elif d.type == BibliographicDateType.ACCESSED:
                item["urldate"] = d.value("on")

    def _bibtex_series(self, item: dict):
        for s in self.series:
            if s.type == SeriesType.JOURNAL:
                item["journal"] = str(s.title.title.content)
                if s.number:
                    item["number"] = s.number
            elif not s.type:
                item["series"] = str(s.title.title)

    def _bibtex_classification(self, item: dict):
        mapping = {"type": "type", "mendeley": "mendeley-tags"}
        for c in self.classification:
            if c.type in mapping:
                item[mapping[c.type]] = c.value

    def _bibtex_docidentifier(self, item: dict):
        for i in self.docidentifier:
            if i.type in ["isbn", "lccn", "issn"]:
                item[i.type] = i.id

    def _bibtex_link(self, item: dict):
        mapping = {"doi": "doi", "file": "file2", "src": "url"}
        for l in self.link:
            if l.type in mapping:
                item[mapping[l.type]] = l.content

    def render_xml(self, parent: ET.Element, opts: dict) -> ET.Element:
        bibdata = opts.get("bibdata")
        lang = opts.get("lang")
        name = "bibdata" if opts.get("bibdata") else "bibitem"
        root = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        if self.fetched:
            ET.SubElement(root, "fetched").text = self.fetched.strftime(
                BibliographicItem.FETCHED_FORMAT)
        self.title.to_xml(root, opts)
        if self.formattedref:
            self.formattedref.to_xml(root)
        for s in self.link:
            s.to_xml(root, opts)
        for di in self.docidentifier:
            di.to_xml(root, opts)
        if self.docnumber:
            ET.SubElement(root, "docnumber").text = self.docnumber
        for d in self.date:
            d.to_xml(root, opts)
        for c in self.contributor:
            node = ET.SubElement(root, "contributor")
            for r in c.role:
                r.to_xml(node, opts)
            c.to_xml(node, opts)
        if self.edition:
            ET.SubElement(root, "edition").text = self.edition
        if self.version:
            self.version.to_xml(root)
        if self.biblionote:
            self.biblionote.to_xml(root, opts)
        if hasattr(opts.get("note"), "__iter__"):
            for n in opts["note"]:
                node = ET.SubElement(root, "note")
                node.text = n.get("text")
                node.attrib["format"] = "text/plain"
                node.attrib["type"] = n.get("type")
        for l in self.language:
            ET.SubElement(root, "language").text = l
        for s in self.script:
            ET.SubElement(root, "script").text = s
        abstr = list(filter(
            lambda ab: ab.language and lang in ab.language, self.abstract))
        abstr = abstr if any(abstr) else self.abstract
        for a in abstr:
            a.to_xml(ET.SubElement(root, "abstract"))
        if self.status:
            self.status.to_xml(root)
        for c in self.copyright:
            c.to_xml(root, opts)
        for r in self.relation:
            r.to_xml(root, opts)
        for s in self.series:
            s.to_xml(root, opts)
        if self.medium:
            self.medium.to_xml(root)
        for pl in self.place:
            pl.to_xml(root)
        for e in self.extent:
            e.to_xml(ET.SubElement(root, "extent"))
        for al in self.accesslocation:
            ET.SubElement(root, "accesslocation").text = al
        for al in self.license:
            ET.SubElement(root, "license").text = al
        for cl in self.classification:
            cl.to_xml(root)
        kwrd = list(filter(
            lambda k: k.language and lang in k.language, self.keyword))
        kwrd = kwrd if any(kwrd) else self.keyword
        for kw in kwrd:
            kw.to_xml(ET.SubElement(root, "keyword"))
        if self.validity:
            self.validity.to_xml(root)
        if opts.get("lambda"):
            opts["lambda"](root, opts)
        elif bibdata and (self.doctype or self.editorialgroup
                          or (self.ics and any(self.ics))
                          or (self.structuredIdentifier
                              and self.structuredIdentifier.presence)):
            ext = ET.SubElement(root, "ext")
            if self.doctype:
                ET.SubElement(ext, "doctype").text = self.doctype
            if self.subdoctype:
                ET.SubElement(ext, "subdoctype").text = self.subdoctype
            if self.editorialgroup:
                self.editorialgroup.to_xml(ext)
            for i in self.ics:
                i.to_xml(ext)
            if self.structuredidentifier:
                self.structuredidentifier.to_xml(ext)
        if self.id and not bibdata and not opts.get("embedded"):
            root.attrib["id"] = self.id
        if self.type:
            root.attrib["type"] = self.type
        return root

    def to_bibxml(self, parent: ET.Element = None) -> ET.Element:
        """ Render BibXML (RFC)
            parent: node where output BibXML will be built
            return root node of BibXML document"""
        reference = ET.Element("reference") if parent is None \
            else ET.SubElement(parent, "reference")
        front = ET.SubElement(reference, "front")

        reference.attrib["anchor"] = self.anchor
        if any(self.title):
            first = self.title[0].title.content
            ET.SubElement(front, "title").text = first

        self.render_seriesinfo(front)
        self.render_authors(front)
        self.render_date(front)
        self.render_workgroup(front)
        self.render_keyword(front)
        self.render_abstract(front)

        target = self.bibxml_target
        if target:
            reference.attrib["target"] = str(target.content)

        return reference

    @property
    def bibxml_target(self) -> TypedUri:
        src_link = None
        doi_link = None
        for lnk in self.link:
            if lnk.type == "src":
                src_link = lnk
                break
            elif lnk.type == "doi":
                doi_link = lnk
        return src_link or doi_link

    @property
    def anchor(self):
        did = next(
            (di for di in self.docidentifier if di.type == "rfc-anchor"),
            None)
        if did is not None:
            return did.id

        type = self.docidentifier[0].type
        return f"{type}.{self.docnumber}"

    def render_keyword(self, parent: ET.Element):
        for kw in self.keyword:
            ET.SubElement(parent, "keyword").text = kw.content

    def render_workgroup(self, parent: ET.Element):
        if self.editorialgroup is not None:
            if self.editorialgroup.technical_committee is not None:
                for tc in self.editorialgroup.technical_committee:
                    ET.SubElement(parent, "workgroup").text = tc.workgroup.name

    def render_abstract(self, parent: ET.Element):
        if not any(self.abstract):
            return

        ET.SubElement(parent, "abstract").text = re.sub(
            r"(<\/?)p(>)", r"\1t\2", self.abstract[0].content)

    def render_date(self, parent: ET.Element):
        dt = next((d for d in self.date if d.type == "published"), None)
        if dt is None:
            return

        elm = ET.SubElement(parent, "date")
        for part in ["year", "month", "day"]:
            value = dt.part(part)
            if value:
                elm.attrib[part] = month_name(value) if part == "month" \
                                                     else str(value)

    def render_seriesinfo(self, parent: ET.Element):
        for di in self.docidentifier:
            if di.type in ["DOI", "Internet-Draft"]:
                si = ET.SubElement(parent, "seriesInfo")
                si.attrib["name"] = di.type
                si.attrib["value"] = di.id

        snames = [di.type for di in self.docidentifier]
        for s in self.series:
            if s.title is None or str(s.title.title) in snames:
                continue
            si = ET.SubElement(parent, "seriesInfo")
            si.attrib["name"] = str(s.title.title)
            if s.number:
                si.attrib["value"] = s.number

    def render_authors(self, parent: ET.Element):
        for c in self.contributor:
            a = ET.SubElement(parent, "author")
            is_editor = any(r for r in c.role if r.type == "editor")
            if is_editor:
                a.attrib["role"] = "editor"

            if isinstance(c.entity, Person):
                self.render_person(a, c.entity)
            else:
                self.render_organization(a, c.entity)

            self.render_address(a, c)

    def render_address(self, parent: ET.Element, contrib: Contributor):
        addr = [cn for cn in contrib.entity.contact
                if not(isinstance(cn, Address) and cn.postcode is None)]

        if any(addr):
            address = ET.SubElement(parent, "address")
            addr = next((cn for cn in addr if isinstance(cn, Address)), None)
            postal = ET.SubElement(address, "postal")
            if addr.city:
                ET.SubElement(postal, "city").text = addr.city
            if addr.postcode:
                ET.SubElement(postal, "code").text = addr.postcode
            if addr.country:
                ET.SubElement(postal, "country").text = addr.country
            if addr.state:
                ET.SubElement(postal, "region").text = addr.state
            if any(addr.street):
                ET.SubElement(postal, "street").text = addr.street[0]

            self.render_contact(address, contrib.entity.contact)

    def render_contact(self, parent: ET.Element, addr: List[Address]):
        for t in ["phone", "email", "uri"]:
            cont = next((cn for cn in addr if isinstance(cn, Contact)
                         and cn.type == t), None)
            if cont:
                ET.SubElement(parent, t).text = cont.value

    def render_person(self, parent: ET.Element, person: Person):
        if len(person.affiliation) > 0:
            self.render_organization(parent,
                                     person.affiliation[0].organization)
        if person.name.completename is not None:
            parent.attrib["fullname"] = person.name.completename.content

        if any(person.name.initial):
            parent.attrib["initials"] = " ".join(
                [i.content for i in person.name.initial])

        if person.name.surname is not None:
            parent.attrib["surname"] = person.name.surname.content

    def render_organization(self, parent: ET.Element, org: Organization):
        o = ET.SubElement(parent, "organization")
        if len(org.name) > 0:
            o.text = org.name[0].content

        if org.abbreviation:
            o.attrib["abbrev"] = org.abbreviation.content


def month_name(month_number) -> str:
    if isinstance(month_number, str):
        month_number = int(month_number)

    return datetime.date(1900, month_number, 1).strftime('%B')
