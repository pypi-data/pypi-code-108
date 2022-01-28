from relaton_bib import BibliographicDate, BibliographicDateType


def test_nov_2014():
    date = BibliographicDate(type=BibliographicDateType.PUBLISHED.value,
                             on="November 2014")
    assert date.on == "2014-11"


def test_nov_2014_to_xml():
    date = BibliographicDate(type=BibliographicDateType.PUBLISHED.value,
                             on="November 2014")

    result = date.to_xml(None, {})

    assert result.attrib["type"] == BibliographicDateType.PUBLISHED.value
    assert result.find("./on").text == "2014-11"


def test_nov_2014_full_date():
    date = BibliographicDate(type=BibliographicDateType.ISSUED.value,
                             on="November 2014")

    result = date.to_xml(None, {"date_format": "full"})

    assert result.attrib["type"] == BibliographicDateType.ISSUED.value
    assert result.find("./on").text == "2014-11-01"


def test_from_to_xml():
    date = BibliographicDate(type=BibliographicDateType.COPIED.value,
                             from_="2014-11", to="2015-12")
    result = date.to_xml(None, {})

    assert result.attrib["type"] == BibliographicDateType.COPIED.value
    assert result.find("./from").text == "2014-11"
    assert result.find("./to").text == "2015-12"


def test_from_to_short_xml():
    date = BibliographicDate(type=BibliographicDateType.ADAPTED.value,
                             from_="2014-11", to="2015-12")

    result = date.to_xml(None, {"date_format": "short"})

    assert result.attrib["type"] == BibliographicDateType.ADAPTED.value
    assert result.find("./from").text == "2014-11"
    assert result.find("./to").text == "2015-12"


def test_on_format_year_only():
    date = BibliographicDate(type=BibliographicDateType.ACCESSED.value,
                             on="2014")

    result = date.to_xml(None, {"date_format": "full"})

    assert result.attrib["type"] == BibliographicDateType.ACCESSED.value
    assert result.find("./on").text == "2014-01-01"


# FIXME
# def test_date_not_matched_any_patterns():
#     date = BibliographicDate(type=BibliographicDateType.ACCESSED.value, on="")
#     item.instance_variable_set :@on, "Nov 2020"
#     expect(item.on(:month)).to eq "Nov 2020"
