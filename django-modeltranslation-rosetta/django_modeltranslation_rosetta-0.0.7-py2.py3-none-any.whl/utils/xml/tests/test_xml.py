import io

from django.utils.encoding import smart_bytes

from modeltranslation_rosetta.utils.xml.parse import XMLParser
from modeltranslation_rosetta.utils.xml.render import XMLRenderer


def test_build_xml():
    x = XMLRenderer()
    x.cdata = False

    data = [
        {
            "#attrs": {"id": 1234},
            "@foo": "bar",
            "first_name": {
                "lang": [
                    {"#attrs": {"code": "en"}, "#text": 123},
                    {"#attrs": {"code": "tr"}},
                ]
            },
        }
    ]

    assert x.render(data, parent_tag_name="object") == (
        "<root>\n"
        "  <Objects>\n"
        '    <Object foo="bar" id="1234">\n'
        "      <FirstName>\n"
        '        <Lang code="en">123</Lang>\n'
        '        <Lang code="tr"/>\n'
        "      </FirstName>\n"
        "    </Object>\n"
        "  </Objects>\n"
        "</root>\n"
    )


def test_xml_with_html_tags():
    x = XMLRenderer()
    data = [
        {"test": "<html>тест</html>", "test2": "Foo & бар", "test3": "", "test4": None}
    ]

    assert x.render(data, parent_tag_name="object") == (
        "<root>\n"
        "  <Objects>\n"
        "    <Test><![CDATA[<html>тест</html>]]></Test>\n"
        "    <Test2><![CDATA[Foo & бар]]></Test2>\n"
        "    <Test3><![CDATA[]]></Test3>\n"
        "    <Test4/>\n"
        "  </Objects>\n"
        "</root>\n"
    )


def test_parse_xml():
    xml = (
        "<root>\n"
        "  <Objects>\n"
        '    <Object id="1234">\n'
        "      <FirstName>\n"
        '        <Lang code="en">123</Lang>\n'
        '        <Lang code="tr"><![CDATA[<html>тест</html>]]></Lang>\n'
        '        <Lang code="ru">Foo &amp; bar</Lang>\n'
        "      </FirstName>\n"
        "    </Object>\n"
        "  </Objects>\n"
        "</root>\n"
    )

    x = XMLParser()
    assert list(x.parse(io.BytesIO(smart_bytes(xml)), tags=["Object"])) == [
        {
            "Object": {
                "@id": "1234",
                "FirstName": {
                    "Lang": [
                        {"#text": "123", "@code": "en"},
                        {"#text": "<html>тест</html>", "@code": "tr"},
                        {"#text": "Foo & bar", "@code": "ru"},
                    ]
                },
            }
        }
    ]
