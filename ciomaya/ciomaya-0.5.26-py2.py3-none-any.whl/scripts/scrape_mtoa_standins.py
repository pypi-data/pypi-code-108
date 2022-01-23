"""
A scraper to recursively collect paths from Arnold standin nodes.
"""
from ciomaya.lib import scraper_utils
import re
import arnold
import pymel.core as pm
from cioseq.sequence import Sequence
from contextlib import contextmanager


@contextmanager
def arnold_context():
    """Perform some ops between arnold begin end tags"""
    arnold.AiBegin()
    arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_ALL)
    try:
        yield
    finally:
        arnold.AiEnd()
        
# See https://docs.arnoldrenderer.com/display/A5AFMUG/Tokens
TOKENS = (r"<tile>", r"<udim>", r"<frame>", r"<f\d?>", r"<aov>", r"#+")


def run(node):
    """
    Recursive ass scrape.

    Can be slow, so we optimize as much as possible.
    """
    paths = []
    for path in list(set(
        [p["path"] for p in scraper_utils.get_paths({"mtoa": {"aiStandIn": ["dso"]}})]
    )):

        # Since scanning ass files recursively is expensive, we try to use only
        # those reelevant for the frame range.
        sequence = Sequence.create(pm.PyNode(node).attr("frameSpec").get())
        resolved_ass_filenames = scraper_utils.resolve_to_sequence(
            path, sequence)

        paths.extend(resolved_ass_filenames)

    paths = scraper_utils.expand_workspace(paths)

    # maintain a list of filenames to skip
    seen = set()
    found_files = []
    for path in paths:
        found_files.extend(_files_in(path, seen))

    found_files.extend(paths)
    found_files = list(set(found_files))

    found_files = scraper_utils.starize_tokens(found_files, *TOKENS)

    result_paths = [{"path": p} for p in found_files]
    
    return {"paths":result_paths, "env":[]}

def _files_in(ass_file, seen, depth=0):

    if ass_file in seen:
        return []
    seen.add(ass_file)

    found_ass_files = []
    found_leaf_files = []
    with arnold_context():
        arnold.AiASSLoad(ass_file, arnold.AI_NODE_ALL)
        iterator = arnold.AiUniverseGetNodeIterator(
            arnold.AI_NODE_SHAPE | arnold.AI_NODE_SHADER)
        while not arnold.AiNodeIteratorFinished(iterator):
            node = arnold.AiNodeIteratorGetNext(iterator)
            node_entry = arnold.AiNodeGetNodeEntry(node)
            node_entry_name = arnold.AiNodeEntryGetName(node_entry)

            if node_entry_name == "procedural":
                fn = arnold.AiNodeGetStr(node, "filename")
                if fn:
                    if fn.endswith(".ass"):
                        found_ass_files.append(fn)
                    else:
                        found_leaf_files.append(fn)
            elif node_entry_name == "image":
                fn = arnold.AiNodeGetStr(node, "filename")
                if fn:
                    paths = list(set(_expand_attr_token(fn)))
                    found_leaf_files.extend(paths)

        arnold.AiNodeIteratorDestroy(iterator)

    result = found_ass_files + found_leaf_files

    # recurse
    depth += 1
    for found_ass_file in found_ass_files:
        result += _files_in(found_ass_file, seen, depth)

    return result


def _expand_attr_token(filename):
    """
    Resolve filenames from mtoa user data attributes.

    Find shapes that have the attribute in the token. Get the value and expand
    the template with that name. Also expand with the default val.
    """
    result = []
    match = scraper_utils.extract_attr_token(filename)
    if not match:
        return [filename]

    template, attr_name, default_val = match

    if default_val:
        result.append(template.replace(scraper_utils.PLACEHOLDER, default_val))

    iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_SHAPE)
    while not arnold.AiNodeIteratorFinished(iterator):
        node = arnold.AiNodeIteratorGetNext(iterator)
        node_entry = arnold.AiNodeGetNodeEntry(node)
        node_entry_name = arnold.AiNodeEntryGetName(node_entry)

        if node_entry_name == "polymesh":
            attr_val = arnold.AiNodeGetStr(node, attr_name)
            result.append(template.replace(
                scraper_utils.PLACEHOLDER, attr_val))

    arnold.AiNodeIteratorDestroy(iterator)

    return result
