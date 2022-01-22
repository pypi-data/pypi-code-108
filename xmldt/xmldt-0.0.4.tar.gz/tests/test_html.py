from xmldt import XmlDt
from xmldt.htmldt import HtmlDt


# 1. Test standard XmlDt with html flag
def test_xmldt_html_flag():
    class MyHtmlParser (XmlDt):
        def html(self, element):
            assert True, "Called"

    parser = MyHtmlParser(html=True)
    parser("tests/python.html")


# 2. Test HtmlDt with object
def test_htmldt_with_object():
    class MyHtmlParser2 (HtmlDt):
        def html(self, e):
            assert True, "Called"

    parser = MyHtmlParser2()
    parser("tests/python.html")


# 3. Test HtmlDt with direct call
def test_htmldt_with_direct_call():
    class MyHtmlParser3 (HtmlDt):
        def html(self, e):
            assert True, "Called"

    MyHtmlParser3(filename="tests/python.html")

