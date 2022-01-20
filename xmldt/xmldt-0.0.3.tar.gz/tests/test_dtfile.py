import pytest

from xmldt import XMLDT


def test_simple_file():
    class T1 (XMLDT):
        pass

    t1 = T1(strip=True, empty=False)
    assert t1(filename="tests/test1.xml") == """<root>text<body>more text</body>text</root>"""


def test_raise():
    class T1 (XMLDT):
        pass

    t1 = T1()
    with pytest.raises(Exception, match="DT called without arguments"):
        t1()


def test_simple_comment():
    class T1 (XMLDT):
        def __comment__(self, text):
            return text

    t1 = T1(strip=True, empty=False)
    assert t1(filename="tests/test1.xml") == """<root>text A comment <body>more text</body>text</root>"""


def test_simple_types():
    class T1 (XMLDT):

        _types={"list": "list"}

#        def __types__(self):
#            return {"list": "list"}

        def list(self, e):
            assert type(e.c) is list
            assert len(e.c) == 3

        def item(self, e):
            return e.tag

    t1 = T1(strip=True, empty=False)
    result = t1(filename="tests/test2.xml")

def test_simple_types2():
    class T1 (XMLDT):

        _types={"list": "list",
                "tests": "mmap"}

        def list(self, e):
            assert type(e.c) is list
            assert len(e.c) == 3
            return e.c

        def tests(self, e):
            assert type(e.c) is dict
            assert len(e.c["aut"]) == 2
            assert len(e.c["list"][0]) == 3

        def item(self, e):
            return e.tag

    t1 = T1(strip=True, empty=False)
    result = t1(filename="tests/test3.xml")
