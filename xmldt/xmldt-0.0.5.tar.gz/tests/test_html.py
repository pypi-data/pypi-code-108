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


# 4. processor by class
def test_htmldt_by_class():
    class MyHtmlParser4 (HtmlDt):
        class_called = False
        class_not_called = True
        body_not_called = True

        @HtmlDt.html_class("python")
        def my_python(self, e):
            MyHtmlParser4.class_called = True

        @HtmlDt.html_class("non_existing")  # pragma: no cover
        def something(self, e):
            MyHtmlParser4.class_not_called = False

        def body(self, e):  # pragma: no cover
            MyHtmlParser4.body_not_called = False

    MyHtmlParser4(filename="tests/python.html")
    assert MyHtmlParser4.class_called, "Class called"
    assert MyHtmlParser4.body_not_called, "Body not called"
    assert MyHtmlParser4.class_not_called, "Weird class not called"
