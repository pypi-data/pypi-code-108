#/usr/bin/env python


import os
import re
import sys
import argparse
import distutils, shutil, logging
from distutils import dir_util
import xml.etree.ElementTree as ElementTree
import urllib.parse
from pathlib import Path

import yaml

from .api import \
    post_init, post_close, \
    get_init, get_item, get_close

from .uri_utils import resolve_uri
from .utils import norm_join
from aurore import config


from aurore import __version__ #= "0.0.1"

def pass_item(item, args, config, accum:dict)->dict:
    return accum

def _apply_filter(rsrc:dict,filter:dict)->set:
    if "match" in filter:
        for key, pattern in filter["match"].items():
            if re.match(pattern,rsrc[key]):
                continue
            else:
                return False
    return set(filter["rules"]) if "rules" in filter else True

def apply_field_filters(resource:ElementTree,filters:dict)->bool:
    matches = []
    for field,fltrs in filters.items():
        j_matches = []
        if ":" in field:
            elem_name, attrib = field.split(":")
            for fltr in fltrs:
                fltr_j_matched = False
                for el in resource.findall(elem_name):
                    if fltr.search(el.attrib[attrib]):
                        fltr_j_matched = True
                        break
                j_matches.append(fltr_j_matched)
        matches.append(all(j_matches))
    return all(matches)


def main(args:list=None)->int:
    parser = argparse.ArgumentParser(prog='aurore', description="Distributed document-oriented DBMS.")
    parser.add_argument("-D","--database-file",
            nargs="?",
            default=".aurore/aurore.db.xml",
            help="Specify a database file"
    )

    parser.add_argument("-C","--config-file",
            default=".aurore/config.yml",
            help="Specify a config file"
    )
    # parser.add_argument("-I","--include-item", nargs="?", action="append")
    # parser.add_argument("-E","--exclude",nargs="*", action="extend")
    parser.add_argument("-B","--base-uri", default="", help="hi")
    parser.add_argument("-d","--defaults",
        help="Specify a default yaml file.",
        nargs="?",
        action="append"
    )
    parser.add_argument("-v","--verbose",
        help="Generate verbose logging output.",
        action="count",
        default=0
    )
    parser.add_argument("-q","--quiet", action="store_true")
    parser.add_argument("--version",
        help="Output version information and exit.",
        action="store_true")

    subparsers = parser.add_subparsers(title='subcommands') #,description='list of subcommands',help='additional help')

    #-Post-------------------------------------------------------------
    post_parser = subparsers.add_parser("post", help="Create new entity [INCOMPLETE]")
    post_parser.add_argument("type")
    post_parser.add_argument("location", nargs="?", default="$$lid/metadata.xml")
    post_parser.set_defaults(initfunc=post_init)
    post_parser.set_defaults(func=None)
    post_parser.set_defaults(closefunc=post_close)

    #-Get-------------------------------------------------------------
    get_parser = subparsers.add_parser("get", help="Retrieve data from entities")
    get_parser.add_argument("-p","--rel-path")
    get_parser.add_argument("item-selectors", nargs="*", default=["*"])
    get_parser.set_defaults(initfunc=get_init)
    get_parser.set_defaults(func=get_item)
    get_parser.set_defaults(closefunc=get_close)


    #-----------------------------------------------------------------
    # Main
    #-----------------------------------------------------------------
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    #-Logging-----------------------------------------------------------
    logger = logging.getLogger("aurore")
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    levelNames = ["ERROR", "WARN", "INFO", "DEBUG"]
    logger.setLevel(levels[
        0 if args.quiet else min(args.verbose,3) if args.verbose else 0
        ])
    try:
        import coloredlogs
        coloredlogs.install(level=levelNames[
            0 if args.quiet else min(args.verbose,3) if args.verbose else 0
            ])
    except:
        pass

    if args.version:
        print(__version__)
        exit(0)

    #-Config----------------------------------------------------------
    cfg = config.load_config(args.config_file)

    #-Main-----------------------------------------------------------

    accum = {}
    if args.base_uri:
        chdir = args.base_uri
    else:
        chdir = None
        args.base_uri = cfg["base_uri"]

    logger.info(f"{args}")

    if args.database_file =="-":
        # logger.debug(f"STDIN:\n{sys.stdin.read()}")
        # tree = ElementTree.ElementTree(ElementTree.fromstring(sys.stdin.read()))
        tree = ElementTree.parse(sys.stdin)
    else:
        tree = ElementTree.parse(args.database_file)
    root = tree.getroot()
    items = root.find("items")
    if items is None:
        items = root
    if not args.base_uri and "base" in items.attrib:
        args.base_uri = root.find("items").attrib["base"]

    category_schemes = tree.findall(".//category-scheme")
    if "category_file" in args and args.category_file:
        categories = ElementTree.parse(args.category_file[0])
        category_schemes.append(categories.findall("category-scheme"))


    setattr(args, "category_schemes", category_schemes)
    logger.debug(f"category schemes: {category_schemes}")

    tag_schemes = root.find("tag-scheme")
    setattr(args, "tag_schemes", tag_schemes)

    FILTERS = {}

    #-------------------------------------------------------------------
    if "initfunc" in args:
        accum = args.initfunc(args,cfg)
    else:
        accum = {}

    if args.func:
        if chdir: os.chdir(chdir)
        for item in items:
            if "src" in item.attrib:
                resource_path = norm_join(args.base_uri, item.attrib["src"])
                logger.info(f"Resource path: {resource_path}")
                resource = resolve_uri(resource_path)
                resource.attrib.update({"id": item.attrib["id"]})
            
            elif "type" in item.attrib:
                xml_string = cfg["types"][item.attrib["type"]].render(**item.attrib)
                resource = ElementTree.fromstring(xml_string)
            
            else:
                resource = item

            if apply_field_filters(resource,FILTERS):
                logger.info("Entering {}".format(item.attrib["id"]))
                logger.debug(f"Item: {item}")
                key = ElementTree.Element("str")
                key.attrib.update({"key": "id"})
                key.text = item.attrib["id"]
                resource.insert(0, key)
                accum = args.func(resource, args, cfg, accum)


    if "closefunc" in args:
        args.closefunc(args, cfg, accum)
    
    return 0

if __name__ == "__main__": main()
