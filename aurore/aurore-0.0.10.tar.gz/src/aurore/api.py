import os
import json
import logging
import subprocess
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom as minidom
from datetime import datetime, timezone

from .uri_utils import resolve_uri
from .proc_xml import xml_to_map, proc_var, proc_elem, post_proc

logger = logging.getLogger("aurore.api")

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
       if isinstance(obj, set):
          return list(obj)
       return json.JSONEncoder.default(self, obj)


def feed_init(args, config)->dict:
    pass

#--------------------------------------------
# Post
#--------------------------------------------
def post_init(args, config)->dict:
    if "type" in args: args.base = args.type.split("/")[0]
    #print(args.base)
    lids = [k for k in config.namespace].sort()
    if lids:
        _, num = lids[-1].split("-")
        lid = f"{(int(num) + 1):04}"
    else:
        lid = f"{args.base}-0001"
    with open(config.init_type[args.type], "r") as f:
        lines = f.readlines()

    for i, ln in enumerate(lines):
        lines[i] = ln.replace("$$lid",lid)
        lines[i] = ln.replace("$$published",datetime.now(timezone.utc).astimezone().isoformat())
    accum =  {
        "lid": lid,
        "base": ElementTree.fromstringlist(lines),
        "lines": [line for line in lines if "<input" not in line]
    }
    return accum

def post_close(args, config, accum):
    data = {}
    for i, ipt in enumerate(accum["base"].findall("input")):
        val = input(ipt.attrib["key"]+": ")
        try:
            val = eval(val)
        except:
            pass
        data[ipt.attrib["key"]] = val

    if "$$lid" in args.location:
        destination = args.location.replace("$$lid",accum["lid"])
        os.mkdir(accum["lid"])
    else:
        destination = args.location
    with open(destination,"w+") as f:
        f.writelines(build_template(accum["lines"], data))

def build_template(template:list, data:dict):
    for k,v in data.items():
        for j,ln in enumerate(template):
            template[j] = ln.replace(k, str(v))
    return template

#--------------------------------------------
# Get
#--------------------------------------------

def get_init(args,config)->dict:

    accum = {"items": {}, "categories": {}, "tags": {}}
    accum["categories"] = {
        scheme.attrib["key"]: {
            "map": xml_to_map(scheme.find("map")),
            "var": scheme.find("var")
        } for scheme in args.category_schemes
    }
    accum["tags"] = _tag(args.tag_schemes) if args.tag_schemes else {}
    #print(accum["tags"])
    return accum

def get_item(rsrc, args:object, config:object, accum:dict)->dict:
    if "rel_path" in args:
        if args.rel_path:
            relpath = os.path.expandvars(args.rel_path)
        else:
            # relpath=os.getcwd()
            relpath = None
    else:
        relpath = None
    logger.debug(f"Relative path: {relpath}")

    raw_item: dict = xml_to_map(rsrc, args.base_uri, relpath=relpath)
    logger.debug(raw_item)

    if "base" in rsrc.attrib:
        base = rsrc.attrib["base"]
    else:
        base = args.base_uri

    item = categorize(accum["categories"], raw_item, base) if accum["categories"] else raw_item
    item = tag_item(accum["tags"], item, base) if accum["tags"] else item
    accum['items'].update({rsrc.attrib["id"]: item})
    return accum

def get_close(args, config, accum):
    output = {
        "items":  accum["items"]
    }
    if accum["categories"]:
        output.update({
            "categories": {
                category: accum["categories"][category]["map"] for category in accum["categories"]
            }
        })

    print(json.dumps(output,indent=2,cls=SetEncoder))

def tag_item(tags, map_item: dict, base_uri):
    logger.debug(map_item)
    map_item["tags"] = []
    for tag in tags:
        logger.info(f"Tag base uri: {base_uri}")
        val = proc_elem(tags[tag], base_uri, {"item": map_item})[0]
        logger.info(f"Tag value: {val}")
        if val:
            map_item["tags"].append(tag)

    return map_item

def categorize(categories, map_item: dict, base_uri):
    logger.debug(map_item)
    map_item["categories"] = {}

    for category in categories:
        logger.info(f"Category base uri: {base_uri}")
        val = proc_elem(categories[category]["var"], base_uri, {"item": map_item})[0]
        if val is None: val="None"
        if "cast" in categories[category]["var"].attrib:
            val = post_proc[categories[category]["var"].attrib["cast"]](val)
        logger.info(f"Category value: {val}")
        assert val in categories[category]["map"], f"Key {val} not in mapping {categories[category]['map']}"
        map_item["categories"].update({category: val})

    return map_item

def _tag(tag_schemes:ElementTree, base:str="")->dict:
    #print(f"_tag({tag_schemes.attrib['key']})")
    a = {
            ".".join([base, tag_schemes.attrib["key"], scheme.attrib["key"]]).strip(".") : scheme
                for scheme in tag_schemes.findall("./tag")
    }
    for b in tag_schemes.findall(".//tag-scheme"):
        if "src" in b.attrib:
            #print(b.attrib["src"])
            scheme = resolve_uri(b.attrib["src"])
            #print(scheme)
        else:
            scheme = b

        a.update(_tag(scheme,base=".".join([base,tag_schemes.attrib["key"]])))
    #print(f"a: {a}")
    return a

