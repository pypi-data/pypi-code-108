import os
import json
import logging
from urllib.parse import urlparse
import xml.etree.ElementTree as ElementTree

import yaml

import aurore.jsonpointer
from aurore.utils import norm_join

# from aurore.fpointer import resolve_fpointer
from . import proc_rst

logger = logging.getLogger("aurore.uri_utils")

def extract_uri(
    scheme="aurore",
    base="",
    path=""
    ): pass


def resolve_uri(ref:str, local_base="",fmt=None)->ElementTree:
    ref = norm_join(local_base, ref)
    # if local_base:
    #     ref = os.path.join(local_base, ref)
    # ref = os.path.expandvars(ref)
    url = urlparse(ref)

    if os.path.isfile(url.path):
        _, ext = os.path.splitext(url.path)
        fmt = fmt if fmt else ext
        if fmt in [".xml", ".html"]:
            item = ElementTree.parse(url.path)
            if url.fragment:
                if url.fragment[0] not in ['.', '/']:
                    return item.find(f".//*[@id='{url.fragment}']")
                else:
                    return item.find(url.fragment)
            else:
                return item
        elif fmt in [".json", ".ipynb"]:
            logger.info(f"Resolving URI: {ref}")
            with open(url.path,"r") as f:
                item = json.load(f)
            if url.fragment:
                return resolve_fragment(item, url.fragment, "jsonpointer")
            else:
                return item
        elif fmt in ["yaml",".yaml", "yml", ".yml"]:
            with open(url.path,"r") as f:
                item = yaml.load(f, Loader=yaml.Loader)
            if url.fragment:
                return resolve_fragment(item, url.fragment, "jsonpointer")
            else:
                return item
        elif fmt in [".rst"]:
            document: ElementTree = proc_rst.rst_to_xml(url.path)
            if url.fragment:
                return resolve_fragment(document, url.fragment, "xpath")
            else:
                return document
    else:
        raise FileNotFoundError(url.path)

def resolve_fragment(item, fragment, scheme):
    # if fragment[0] in ["%","@"]:
    #     return resolve_fpointer(item, fragment)
    if scheme.lower() in ["jsonpointer"]:
        return aurore.jsonpointer.resolve_pointer(item, fragment)
        # for key in fragment.split("/"):
        #     if key: item = item[key]
    elif scheme.lower() == "xpath":
        if "/@" in fragment:
            fragment, attrib = fragment.split("/@")
        else:
            attrib=None
        elem = item.find(fragment)

        if elem is not None:
            if attrib:
                return elem.attrib[attrib]
            else:
                return elem.text 
        else:
            return elem

    return item

def resolve_xpath(item, fragid):
    pass 

