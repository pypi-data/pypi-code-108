import os
import subprocess
import logging
import xml.etree.ElementTree as ElementTree
from datetime import datetime

from .git_utils import sha1
from .uri_utils import resolve_uri
from .proc_rst import find_dependencies
from .utils import norm_join

logger = logging.getLogger("aurore.proc_xml")

def xml_to_map(xml_item: ElementTree, base=None, context=None, relpath=None,**kwds)->dict:
    return proc_elem(xml_item, base, context, relpath, **kwds)[0]


def proc_elem(elem, base, context, relpath=None,**kwds):
    if test_pull_content(elem):
        logger.info(f"Pulling content for src: {elem.attrib['src']}")
        content, sub_state = pull_content(elem, base)
        val, _ = proc[elem.tag](content, base, context=context, relpath=relpath, **kwds)
    else:
        content = elem
        val, sub_state = proc[elem.tag](content, base, context=context, relpath=relpath,**kwds)
    return val, sub_state


def test_pull_content(elem: ElementTree)->bool:
    """test whether content must be pulled for an element."""
    # return not (elem or elem.text) and "src" in elem.attrib
    return "src" in elem.attrib


def pull_content(elem, base, verbose=True)->ElementTree:
    if "base" in elem.attrib:
        base = elem.attrib["base"]

    src = elem.attrib["src"]
    if "proc" in elem.attrib:
        if "type" in elem.attrib:
            raise Exception("Unimplemented")
        else:
            content, state = proc_src[elem.attrib["proc"]](src, base)
    else:
        logger.info(f"Resolving {src}, {base}")
        content = resolve_uri(src, base)
        state = None
    try:
        elem.text = content.text
    except:
        elem.text = content
    logger.info(f"Pulled content: {content}")
    return elem, {"src": state}


def proc_map(elem, base, context=None, **kwds):
    if "base" in elem.attrib:
        base = elem.attrib["base"]
    logger.info(f"key: {elem.attrib['key'] if 'key' in elem.attrib else ''}, base: {base}")
    output = {}
    state = {}
    for el in elem:
        key = el.attrib["key"] if "key" in el.attrib else el.attrib["id"]
        val, sub_state = proc_elem(el, base, context, **kwds)
        output.update({key : val})
        if sub_state:
            state.update({key: sub_state})
    return output, state

def proc_set(elem, base, context=None, **kwds):
    if "base" in elem.attrib:
        base = elem.attrib["base"]
    if "cast" in elem.attrib:
        cast_type = post_proc[elem.attrib["cast"]]
    else:
        cast_type = lambda x, **kwds: x
    output = set()
    state  = set()
    if isinstance(elem.text,(list,set)):
        output.update(elem.text if isinstance(elem.text,set) else set(elem.text))
    for el in elem:
        val, sub_state = proc_elem(el, base, context=context, cast_type=cast_type, **kwds)

        if "unpack" in el.attrib:
            #getattr(output,el.attrib["unpack"])(val)
            unpacker = getattr(output,el.attrib["unpack"])
            unpacker(cast_type(x,base,**kwds) for x in val)
            getattr(state,el.attrib["unpack"])(sub_state)
        else:
            unpacker = output.update
            if isinstance(val,set):
                unpacker(val)
            elif isinstance(val,list):
                unpacker(set(val))
            else:
                output.add(val)
            state.add(sub_state)
        # if el.tail:
        #     output.append(el.tail)
    if not any(state):
        state = []
    return output, state

def proc_list(elem, base, context=None, **kwds):
    if "base" in elem.attrib:
        base = elem.attrib["base"]
    output = []
    state = []
    if isinstance(elem.text,list):
        output.extend(elem.text)
    for el in elem:
        val, sub_state = proc_elem(el, base, context, **kwds)
        logger.info(f" VAL: {val.text if hasattr(val,'text') else val}")
        if "unpack" in el.attrib:
            getattr(output,el.attrib["unpack"])(val)
            getattr(state,el.attrib["unpack"])(sub_state)
        else:
            output.append(val)
            state.append(sub_state)
    if not any(state):
        state = []
    return output, state


def cli_usage(src,base_uri):
    # build_loc = os.path.join(base_uri,src)
    build_loc = norm_join(base_uri, src)
    state = {"sha1": sha1(src)}
    if build_loc[-3:] == ".py":
        try:
            text = subprocess.check_output([
                "python", os.path.expandvars(build_loc), "--help"
            ]).decode().replace("<","&lt")
        except:
            text = ""
    else:
        try:
            text = subprocess.check_output([
                os.path.expandvars(build_loc)
            ]).decode().replace("<","&lt")
        except:
            try:
                text = subprocess.check_output([
                    os.path.expandvars(build_loc), "--help"
                ]).decode().replace("<","&lt")
            except:
                text = ""

    return text, state

def proc_date(elem, base, context=None, **kwds):
    if "-" not in elem.text:
        if len(elem.text)==8:
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        else:
            logger.error(f"Unrecognized date: {elem.text}")
            return elem.text, None
    date = datetime.fromisoformat(elem.text)
    return date.astimezone().isoformat(), None

def proc_var(elem, base, context=None, **kwds):
    if context is None:
        context = {}
    ans = None
    for var in elem:
        ans, state = proc[var.tag](var,base,context=context,**kwds)
        logger.debug(f"var ans: {ans}")
        if "id" in var.attrib:
            context.update({var.attrib["id"]: ans})
        else:
            context.update({"ans": ans})

    if ans is None:
        return elem.text, None
    if "cast" in elem.attrib:
        logger.debug(f"ans precast: {ans}")
        ans = post_proc[elem.attrib["cast"]](ans)
        logger.debug(f"ans post-cast: {ans}")
    return ans, state

def proc_eval(elem, base, context, **kwds):
    context.update({
        "os": os,
        "subprocess": subprocess
    })
    if "base" in elem.attrib:
        base = elem.attrib["base"]
    return eval(elem.text,context), {"sha1": sha1(elem.text)}

def proc_path(el,base,context,relpath,**kwds):
    path = post_path(el.text, base, relpath)
    return path, None

def post_path(path, base=None, relpath=None):
    path = norm_join(base,path)
    if relpath:
        logger.debug(f"Normalizing path relative to: {relpath}")
        path = os.path.relpath(os.path.normpath(path), os.path.abspath(relpath))
    return path

# def proc_str(el, base, context, **kwds):
#     try:
#         return str(el.text.text)
#     except:
#         return str(el.text)

proc = {
    "var": proc_var,
    "str": lambda el,_,**__: (str(el.text), None),
    "int": lambda el,_,**__: (int(el.text), None),
    "flt": lambda el,_,**__: (float(el.text), None),
    "uri": lambda el,_,**__: (str(el.text), None),
    "lst": proc_list,
    "set": proc_set,
    "tag": lambda el,_,**__: (bool(el.text),None),
    "map": proc_map,
    "path": proc_path,
    "date": proc_date,
    "item": lambda el,_,**__: (el.text, None),
    "bool": lambda el,_,**__: (bool(el.text), None),
    "eval": proc_eval,
    "date": lambda el,_,**__: (str(el.text),None),
}

post_proc = {
    "lst": list,
    "map": dict,
    "int": int,
    "str": str,
    "path": post_path,
}

proc_src = {
    "aurore.cli_usage": cli_usage,
    "aurore.find_dependencies": find_dependencies
}
