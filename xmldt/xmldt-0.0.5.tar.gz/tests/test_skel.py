from xmldt.skel import Skel, build_skel
# import sys
import re


def test_build_skel():
    skel = build_skel(["tests/test1.xml"])

    # print(skel, file=sys.stderr)
    assert type(skel) is str
    assert re.search(r"def __default__", skel)
    assert re.search(r"# def body", skel)
    assert re.search(r"# def root", skel)


