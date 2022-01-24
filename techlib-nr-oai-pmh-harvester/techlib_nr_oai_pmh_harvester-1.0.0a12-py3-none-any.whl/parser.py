from collections import defaultdict

from dojson.contrib.marc21.utils import create_record
from oarepo_oai_pmh_harvester.decorators import parser

from nr_oai_pmh_harvester.utils import transform_to_dict


@parser("marcxml")
def marcxml_parser_caller(element):
    return transform_to_dict(marcxml_parser(element))  # pragma: no cover


def marcxml_parser(element):
    xml_dict = create_record(element)
    return xml_dict


@parser("xoai")
def xoai_parser_refine(etree):
    return xml_to_dict_xoai(list(list(etree)[1])[0])


def xml_to_dict_xoai(tree):
    tree_dict = defaultdict(list)
    children = list(tree)
    if len(children) == 0:
        return tree.text
    for child in children:
        name = child.get("name")
        tree_dict[name].append(xml_to_dict_xoai(child))
    remove_key(tree_dict, "none")
    remove_key(tree_dict, "null")
    remove_key(tree_dict, None)
    tree_dict.pop("none", True)
    tree_dict.pop("null", True)
    tree_dict.pop(None, True)
    return tree_dict


def remove_key(tree_dict, key):
    if key in tree_dict:
        for item in tree_dict[key]:
            for k, v in item.items():
                tree_dict[k].append(v)
