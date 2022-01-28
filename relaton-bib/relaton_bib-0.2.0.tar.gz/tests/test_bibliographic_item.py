from __future__ import annotations
import datetime
import logging
import pytest
import re
import os
import xml.etree.ElementTree as ET

from lxml import etree

from . import elements_equal

from relaton_bib import BibliographicItem, BibliographicItemType
from relaton_bib import Address
from relaton_bib import Contact
from relaton_bib import Affiliation
from relaton_bib import TypedUri
from relaton_bib import DocumentIdentifier, DocumentIdType
from relaton_bib import CopyrightAssociation
from relaton_bib import FormattedString, FormattedStringFormat
from relaton_bib import ContributionInfo, ContributorRole
from relaton_bib import BibliographicDate, BibliographicDateType
from relaton_bib import Series, SeriesType
from relaton_bib import DocumentStatus
from relaton_bib import Organization, OrgIdentifier
from relaton_bib import LocalizedString
from relaton_bib import TypedTitleString, TypedTitleStringCollection
from relaton_bib import TechnicalCommittee
from relaton_bib import FormattedRef
from relaton_bib import Medium
from relaton_bib import Classification
from relaton_bib import Validity
from relaton_bib import BibItemLocality, Locality, BibItemLocalityType, \
    SourceLocalityStack, SourceLocality, LocalityStack
from relaton_bib import BiblioNote, BiblioNoteCollection
from relaton_bib import BibliographicItemVersion
from relaton_bib import Place
from relaton_bib import Person, FullName, PersonIdentifier
from relaton_bib import StructuredIdentifierCollection
from relaton_bib import EditorialGroup
from relaton_bib import ICS
from relaton_bib import DocRelationCollection
from relaton_bib import DocumentRelation
from relaton_bib import WorkGroup
from relaton_bib import StructuredIdentifier


@pytest.fixture
def title() -> TypedTitleStringCollection:
    result = TypedTitleString.from_string("Geographic information")
    result.append(TypedTitleString(content="Information géographique",
                                   language=["fr"],
                                   script=["Latn"]))
    return result


@pytest.fixture
def subject(title: TypedTitleStringCollection) -> BibliographicItem:
    return BibliographicItem(
        id="ISOTC211",
        title=title,
        fetched=datetime.date(2021, 8, 30),
        type=BibliographicItemType.STANDARD,
        doctype="document",
        subdoctype="subdocument",
        docidentifier=[
            DocumentIdentifier("TC211", DocumentIdType.ISO),
            DocumentIdentifier("ISBN", "isbn"),
            DocumentIdentifier("LCCN", "lccn"),
            DocumentIdentifier("ISSN", "issn", "series"),
            DocumentIdentifier("urn:iso:std:iso:123:stage-90.93:ed-3:en,fr",
                               "URN"),
            DocumentIdentifier("XYZ"),
            DocumentIdentifier("10.17487/rfc1149", "DOI"),
            DocumentIdentifier("draft-ietf-somewg-someprotocol-07",
                               "Internet-Draft")
        ],
        docnumber="123456",
        edition="1",
        language=["en", "fr"],
        script=["Latn"],
        version=BibliographicItemVersion(revision_date="2019-04-01",
                                         draft=["draft"]),
        biblionote=BiblioNoteCollection([
            BiblioNote(content="note"),
            BiblioNote(content="An note", type="annote"),
            BiblioNote(content="How published", type="howpublished"),
            BiblioNote(content="Comment", type="comment"),
            BiblioNote(content="Table Of Contents", type="tableOfContents"),

        ]),
        status=DocumentStatus(
            stage=DocumentStatus.Stage(value="30", abbreviation="CD"),
            substage=DocumentStatus.Stage(value="substage"),
            iteration="final"
        ),
        date=[
            BibliographicDate(
                type=BibliographicDateType.ISSUED, on="2014"),
            BibliographicDate(
                type=BibliographicDateType.PUBLISHED, on="2014-04"),
            BibliographicDate(
                type=BibliographicDateType.ACCESSED, on="2015-05-20")
        ],
        abstract=[
            FormattedString(
                content="ISO 19115-1:2014 defines the schema required for ...",
                language="en",
                script="Latn",
                format="text/plain"
            ),
            FormattedString(
                content="L'ISO 19115-1:2014 définit le schéma requis pour ...",
                language="fr",
                script="Latn",
                format="text/plain"
            )
        ],
        contributor=[
            ContributionInfo(
                role=[
                    ContributorRole(
                        type="publisher",
                        description=[FormattedString(content="Publisher role",
                                                     format=None)])
                ],
                entity=Organization(
                    name="International Organization for Standardization",
                    abbreviation="ISO",
                    subdivision=[LocalizedString("division")],
                    uri="www.iso.org")
            ),
            ContributionInfo(
                role=[ContributorRole(type="author")],
                entity=Person(
                    name=FullName(completename=LocalizedString(
                        content="A. Bierman",
                        language="en",
                        script="Latn")),
                    affiliation=[Affiliation(Organization(
                        name="IETF",
                        abbreviation="IETF",
                        identifier=[OrgIdentifier(
                            type="uri",
                            value="www.ietf.org")]
                    ))],
                    contact=[
                        Address(
                            street=["Street"],
                            city="City",
                            state="State",
                            country="Country",
                            postcode="123456"),
                        Contact(type="phone", value="223322")
                    ]
                )
            ),
            ContributionInfo(
                role=[
                    ContributorRole(
                        type="publisher",
                        description=[FormattedString(
                            content="Publisher description",
                            format=None)]),
                    ContributorRole(
                        type="editor",
                        description=[FormattedString(
                            content="Editor description", format=None)])
                ],
                entity=Organization(
                    name="IETF",
                    abbreviation="IETF",
                    identifier=[OrgIdentifier(
                        type="uri",
                        value="www.ietf.org")])
            ),
            ContributionInfo(
                role=[ContributorRole(type="author")],
                entity=Person(
                    name=FullName(
                        initial=[LocalizedString(
                            content="A.", language="en", script="Latn")],
                        surname=LocalizedString(
                            content="Bierman", language="en", script="Latn"),
                        forename=[LocalizedString(
                            content="Forename", language="en", script="Latn")],
                        addition=[LocalizedString(
                            content="Addition", language="en", script="Latn")],
                        prefix=[LocalizedString(
                            content="Prefix", language="en", script="Latn")]),
                    affiliation=[Affiliation(
                        organization=Organization(
                            name="IETF",
                            abbreviation="IETF"),
                        description=[FormattedString(
                            content="Description",
                            language="en",
                            format=None)]
                    )],
                    contact=[
                        Address(
                            street=["Street"],
                            city="City",
                            postcode="123456",
                            country="Country",
                            state="State"),
                        Contact(type="phone", value="223322")
                    ],
                    identifier=[PersonIdentifier(
                        type="uri",
                        value="www.person.com")]
                )
            ),
            ContributionInfo(
                entity=Organization(name="Institution"),
                role=[ContributorRole(
                    type="distributor",
                    description=[FormattedString(content="sponsor",
                                                 format=None)])],
            )
        ],
        copyright=[CopyrightAssociation(
            owner=[ContributionInfo(
                Organization(
                    name="International Organization for Standardization",
                    abbreviation="ISO",
                    uri="www.iso.org"))],
            from_="2014",
            to="2020",
            scope="Scope"
        )],
        link=[
            TypedUri(type="src",
                     content="https://www.iso.org/standard/53798.html"),
            TypedUri(type="obp",
                     content="https://www.iso.org/obp/ui/#!iso:std:53798:en"),
            TypedUri(
                type="rss",
                content="https://www.iso.org/contents/data/standard/05/37/"
                        "53798.detail.rss"),
            TypedUri(type="doi", content="http://standrd.org/doi-123"),
            TypedUri(type="file", content="file://path/file"),
        ],
        relation=DocRelationCollection([
            DocumentRelation(
                type=DocumentRelation.Type.updates,
                bibitem=BibliographicItem(
                    formattedref=FormattedRef(
                        content="ISO 19115:2003",
                        format=None)),
                locality=[
                    LocalityStack([
                        Locality(
                            type="section",
                            reference_from="Reference from")
                    ]),
                    LocalityStack([
                        Locality(type="chapter", reference_from="1"),
                        Locality(type="page", reference_from="2")
                    ])
                ],
                source_locality=[
                    SourceLocalityStack([
                        SourceLocality(type="volume", reference_from="2"),
                        SourceLocality(type="chapter", reference_from="3")

                    ])
                ]),
            DocumentRelation(
                type=DocumentRelation.Type.obsoletes,
                description=FormattedString(format="text/plain",
                                            content="supersedes"),
                bibitem=BibliographicItem(
                    type=BibliographicItemType.STANDARD,
                    formattedref=FormattedRef(
                        content="ISO 19115:2003/Cor 1:2006",
                        format=None))),
            DocumentRelation(
                type=DocumentRelation.Type.partOf,
                bibitem=BibliographicItem(
                    title=TypedTitleStringCollection(
                        [TypedTitleString(
                            type=TypedTitleString.Type.MAIN,
                            content="Book title")]))
            )
        ]),
        series=[
            Series(
                type=SeriesType.MAIN,
                title=TypedTitleString(
                    type="original",
                    content="ISO/IEC FDIS 10118-3",
                    language="en",
                    script="Latn",
                    format="text/plain"
                ),
                place="Serie's place",
                organization="Serie's organization",
                abbreviation=LocalizedString("ABVR"),
                from_="2009-02-01",
                to="2010-12-20",
                number="serie1234",
                partnumber="part5678"),
            Series(
                type="alt",
                formattedref=FormattedRef(
                    content="serieref",
                    language="en",
                    script="Latn")
            ),
            Series(
                type="journal",
                title=TypedTitleString(content="Journal"),
                number="7"
            ),
            Series(
                title=TypedTitleString(content=[
                    LocalizedString(content="Series",
                                    language="en",
                                    script="Latn"),
                    LocalizedString(content="Séries",
                                    language="fr",
                                    script="Latn")])
            ),
            Series(
                title=TypedTitleString(content="RFC"),
                number="4"
            )
        ],
        medium=Medium(
            form="medium form",
            size="medium size",
            scale="medium scale"),
        place=[
            Place("bib place"),
            Place(name="Geneva", uri="geneva.place", region="Switzelznd")
        ],
        extent=[
            BibItemLocality(
                type=BibItemLocalityType.SECTION,
                reference_from="Reference from",
                reference_to="Reference to"),
            BibItemLocality(
                type=BibItemLocalityType.CHAPTER,
                reference_from="4"),
            BibItemLocality(
                type=BibItemLocalityType.PAGE,
                reference_from="10",
                reference_to="20"),
            BibItemLocality(
                type=BibItemLocalityType.VOLUME,
                reference_from="1"),
        ],
        accesslocation=["accesslocation1", "accesslocation2"],
        classification=[
            Classification(type="type", value="value"),
            Classification("Keywords", "keyword"),
            Classification("Mendeley Tags", "mendeley")
        ],
        keyword=[LocalizedString("Keyword"), LocalizedString("Key Word")],
        license=["License"],
        validity=Validity(
            begins=datetime.datetime.strptime("2010-10-10 12:21",
                                              Validity.FORMAT),
            ends=datetime.datetime.strptime("2011-02-03 18:30",
                                            Validity.FORMAT),
            revision=datetime.datetime.strptime("2011-03-04 09:00",
                                                Validity.FORMAT),
        ),
        editorialgroup=EditorialGroup([
            TechnicalCommittee(
                WorkGroup(
                    name="Editorial group",
                    number=1,
                    type="Type",
                    identifier="Identifier",
                    prefix="Prefix"
                ))
        ]),
        ics=[ICS(code="01", text="First")],
        structuredidentifier=StructuredIdentifierCollection([
            StructuredIdentifier(
                type="type 1",
                agency=["agency 1", "agency 2"],
                class_="class 1",
                docnumber="123",
                partnumber="4",
                edition="1",
                version="2",
                supplementtype="type 2",
                supplementnumber="5",
                language="en",
                year="2020"),
            StructuredIdentifier(docnumber="456", agency=["agency 3"])
        ])
    )


def test_subject_created(subject: BibliographicItem):
    assert type(subject) == BibliographicItem


def test_titles(subject: BibliographicItem):
    assert type(subject.title) == TypedTitleStringCollection
    assert subject.title_for_lang("fr")[0].title.content == \
        "Information g\u00E9ographique"


def test_urls(subject: BibliographicItem):
    assert subject.url() == "https://www.iso.org/standard/53798.html"
    assert subject.url("rss") \
        == "https://www.iso.org/contents/data/standard/05/37/53798.detail.rss"


def test_shortref(subject: BibliographicItem):
    assert subject.shortref(subject.docidentifier[0]) == "TC211:2014"


def test_abstract(subject: BibliographicItem):
    assert isinstance(subject.abstract_for_lang("en"), FormattedString)


def test_to_most_recent_reference(subject: BibliographicItem):
    item = subject.to_most_recent_reference()
    assert item.relation[3].bibitem.structuredidentifier[0].year == "2020"
    assert item.structuredidentifier[0].year is None


def test_to_all_parts(subject: BibliographicItem):
    item = subject.to_all_parts()
    assert item != subject
    assert item.all_parts
    assert item.relation[-1].type == DocumentRelation.Type.instance
    assert next(
        (t for t in item.title if t.type == TypedTitleString.Type.TPART),
        None) is None
    assert next(
        (t.title.content for t in item.title
         if t.type == TypedTitleString.Type.MAIN),
        None) == "Geographic information"
    assert len(item.abstract) == 0
    assert next(
        (d for d in item.docidentifier
         if d.type != "Internet-Draft" and re.match(r"-\d", d.id)),
        None) is None
    assert len([d for d in item.docidentifier
                if "(all parts)" not in d.id]) == 1
    assert next(
        (d for d in item.docidentifier if re.match(r":[12]\d\d\d", d.id)),
        None) is None
    assert next(
        (si for si in item.structuredidentifier if si.partnumber),
        None) is None
    assert next(
        (si for si in item.structuredidentifier
            if re.match(r"-\d", si.docnumber)),
        None) is None
    assert next(
        (si for si in item.structuredidentifier
            if "(all parts)" not in si.docnumber),
        None) is None
    assert next(
        (si for si in item.structuredidentifier
            if re.match(r":[12]\d\d\d", si.docnumber)),
        None) is None


def test_bibitem_xml_string(subject: BibliographicItem):
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "bib_item.xml")
    tree = ET.parse(file)
    reference = tree.getroot()

    subject_xml = subject.to_xml()
    assert elements_equal(reference, subject_xml)

    tree = etree.parse(file)
    relaxng_document = etree.parse(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "../grammars/biblio.rng"))
    xml_document = etree.fromstring(ET.tostring(subject_xml))
    relaxng_processor = etree.RelaxNG(relaxng_document)
    assert relaxng_processor.validate(xml_document)


def test_bibdata_xml_string(subject: BibliographicItem):
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "bibdata_item.xml")
    tree = ET.parse(file)
    reference = tree.getroot()

    subject_xml = subject.to_xml(opts={"bibdata": True})
    assert elements_equal(reference, subject_xml)

    tree = etree.parse(file)
    relaxng_document = etree.parse(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "examples/isobib.rng"))
    xml_document = etree.fromstring(ET.tostring(subject_xml))
    relaxng_processor = etree.RelaxNG(relaxng_document)
    assert relaxng_processor.validate(xml_document)


def test_render_only_fr_lang_tagged_string(subject: BibliographicItem):
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "bibdata_item_fr.xml")
    tree = ET.parse(file)
    reference = tree.getroot()

    subject_xml = subject.to_xml(opts={"bibdata": True, "lang": "fr"})
    assert elements_equal(reference, subject_xml)


def test_render_addition_elements(subject: BibliographicItem):
    def block(node, _):
        ET.SubElement(node, "element").text = "test"
    xml = subject.to_xml(opts={"lambda": block})
    assert b"<element>test</element>" in ET.tostring(xml)


def test_add_note_to_xml(subject: BibliographicItem):
    opts = {"note": [{"text": "Note", "type": "note"}]}
    xml = subject.to_xml(opts=opts)
    assert b"<note format=\"text/plain\" type=\"note\">Note</note>" \
        in ET.tostring(xml)


def test_to_bibtex_standard(subject: BibliographicItem):
    subject.fetched = datetime.datetime(2020, 2, 13)
    bibtex = subject.to_bibtex()

    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "misc_orig.bib")

    assert bibtex == open(file, 'r').read()


def test_techreport(subject: BibliographicItem):
    subject.fetched = datetime.datetime(2020, 2, 13)
    subject.type = BibliographicItemType.TECHREPORT.value
    bibtex = subject.to_bibtex()

    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "techreport_orig.bib")
    assert bibtex == open(file, 'r').read()


def test_manual(subject: BibliographicItem):
    subject.fetched = datetime.datetime(2020, 2, 13)
    subject.type = BibliographicItemType.MANUAL.value
    bibtex = subject.to_bibtex()

    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "manual_orig.bib")

    assert bibtex == open(file, 'r').read()


def test_phdthesis(subject: BibliographicItem):
    subject.fetched = datetime.datetime(2020, 2, 13)
    subject.type = "phdthesis"
    bibtex = subject.to_bibtex()

    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "phdthesis_orig.bib")

    assert bibtex == open(file, 'r').read()


def test_convert_item_to_AsciiBib(subject: BibliographicItem):
    subject.fetched = datetime.datetime(2021, 8, 30)
    adoc = subject.to_asciibib()

    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "asciibib.adoc")

    assert adoc == open(file, 'r').read()


def test_initialize_with_copyright_object():
    org = Organization(
        name="Test Org",
        abbreviation="TO",
        uri="test.org"
    )
    owner = [ContributionInfo(entity=org)]
    copyright = CopyrightAssociation(owner=owner, from_="2018")
    bibitem = BibliographicItem(
      formattedref=FormattedRef(content="ISO123"),
      copyright=[copyright]
    )

    fmtref = bibitem.to_xml().find("./formattedref")

    assert fmtref is not None
    assert fmtref.text == "ISO123"
    assert fmtref.attrib["format"] == FormattedStringFormat.TEXT_PLAIN


def test_warn_invalid_type_argument_error(caplog):
    invalid = "type"

    with caplog.at_level(logging.WARNING):
        BibliographicItem(type=invalid)

    assert f"[relaton-bib] invalid document type: {invalid}" \
        in caplog.text


def test_initialise_with_owner_object():
    org = Organization(name="Test Org", abbreviation="TO", uri="test.org")
    owner = [ContributionInfo(entity=org)]
    copy = CopyrightAssociation(owner=owner, from_="2019")
    assert copy.owner == owner


def test_iconvert_item_to_BibXML_RFC(subject: BibliographicItem):
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "rfc.xml")
    tree = ET.parse(file)
    reference = tree.getroot()

    bibxml = subject.to_bibxml()

    assert elements_equal(reference, bibxml)
