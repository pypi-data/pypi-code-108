"""Unit test package for relaton_bib."""

import xml.etree.ElementTree as ET


def elements_equal(e1: ET.Element, e2: ET.Element, path: list = [], counter: dict = {}) -> bool:
    if e1.tag != e2.tag:
        print(f"{''.join(path)}| <{e1.tag} .../> != <{e2.tag} .../>")
        return False
    if e1.text != e2.text:
        if (e1.text and e2.text) and (e1.text.strip() and e2.text.strip()):
            print(f"{''.join(path)}| <{e1.tag} ...>{e1.text}</{e1.tag}> != <{e2.tag} ...>{e2.text}</{e2.tag}>")
            return False
    if e1.attrib != e2.attrib:
        diff = set(e1.attrib.keys()).symmetric_difference(e2.attrib.keys())
        if diff != {"format"}:
            print(f"{''.join(path)}| <{e1.tag} {e1.attrib} .../> != <{e2.tag} {e2.attrib} .../>")
            return False
    path.append(f"/{e1.tag}")
    if len(e1) != len(e2):
        print(f"len({''.join(path)}) {len(e1)} != {len(e2)}")
        return False
    result = all(elements_equal(c1, c2, path, dict) for c1, c2 in zip(e1, e2))
    path.pop()
    return result
