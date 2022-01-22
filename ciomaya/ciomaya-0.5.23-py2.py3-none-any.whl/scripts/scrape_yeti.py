"""
A scraper to collect paths from Yeti nodes.
"""

import pymel.core as pm
import re

from ciopath.gpath_list import GLOBBABLE_REGEX,PathList
from ciopath.gpath import Path
from ciomaya.lib import scraper_utils
from ciomaya.lib import software
import os


YETI_INTERNAL_NODE_TYPES = {
    "texture": ["file_name"],
    "reference": ["reference_file"]
}

PADDED_PRINTF_REGEX = r"%0\d+d"

def run(_):

    if not software.detect_yeti():
        return

    paths = sum([_scrape_yeti_graph_node(yeti_graph_node)
                 for yeti_graph_node in pm.ls(type="pgYetiMaya")], [])

    paths = scraper_utils.starize_tokens(paths, PADDED_PRINTF_REGEX)
    return {"paths":paths, "env":[]}


def _scrape_yeti_graph_node(graph_node):
    """
    Get the files
    """
    paths = []
    is_caching = graph_node.attr("fileMode").get()
    if is_caching:
        plug = graph_node.attr("cacheFileName")
        cache_path = plug.get()
        if cache_path:
            paths.append({"path": cache_path, "plug": plug})

    search_paths = _get_search_paths(graph_node)
    for yeti_node_type in YETI_INTERNAL_NODE_TYPES:
        attrs = YETI_INTERNAL_NODE_TYPES[yeti_node_type]
        yeti_nodes = pm.pgYetiGraph(
            graph_node, listNodes=True, type=yeti_node_type)
        for yeti_node in yeti_nodes:
            for attr in attrs:

                possible_paths = _possible_asset_paths(graph_node,
                                               yeti_node, attr, search_paths)

                paths+= possible_paths

    return paths


def _possible_asset_paths(graph_node, yeti_node, attr, search_paths):

    asset_path = pm.pgYetiGraph(
        graph_node, node=yeti_node, getParamValue=True, param=attr)

    paths = []
    yeti_metadata = {
        "yeti_plug": "{}.{}".format(yeti_node, attr),
        "yeti_graph_node": graph_node
    }

    if asset_path:
        # THIS NEEDS AN EXPLANATION! 
        # Firstly, the absolute path may exist, but its also possible that it
        # doesn't and that instead the file exists in one of the search paths.
        # Therefore, we may as well treat it like a relative path and simply add
        # the directory portion to the list of search paths.
        asset_path = Path(asset_path)
        if asset_path.absolute:
            search_paths.append(os.path.dirname(asset_path.fslash()))
        relpath = os.path.basename(asset_path.fslash())

        # Now we are searching for a relative path in a list of search paths.

        # We prefer to avoid hitting the filesystem. Therefore we simply
        # generate a path for every combination of searchpath/relpath.

        # What happens when some of them (as expected) are eventually not found?
        # Well the policy for all scrapers is that the result of the scrape may
        # contain some explicit paths and some paths with glob characters. Glob
        # characters cause a path to be silently ignored if it is not found when
        # globbed. 
        
        # Explicit paths that are not found on the other hand will cause a
        # warning on submission.
        
        # You are thinking, how will the customer know if the file is really
        # missing by accident? Well, YETI complains if it can't find a file, so
        # the customer will already know.

        # GLOBBABLE is defined as: it contains some characters that
        # indicate it can be globbed. e.g. "[", "*", "?"
        
        # We can exploit this and make sure that all paths are
        # globbable. To do that, we wrap the last letter of each path in square
        # brackets. It will be globbed, but there can only be one path that
        # matches, similar to the way we find tx files.

        # In other words /path/to/file.01.ex[r] is the same as saying
        # /path/to/file.01.exr if it's there (fail silently).

        # If the path already contains a YETI frame number pattern, then we
        # don't need to make the path globbable here, since the pattern will be
        # replaced with a "*" anyway.


        for search_path in search_paths:
            possible_path = os.path.join(
                search_path, relpath)
            if not re.search(PADDED_PRINTF_REGEX, possible_path):
                possible_path = "{}[{}]".format(
                    possible_path[:-1], possible_path[-1])
                pathobj = {"path": possible_path}
                pathobj.update(yeti_metadata)
            paths.append(pathobj)
    return paths


def _get_search_paths(yeti_graph_node):
    path_list = PathList()
    search_paths = os.pathsep.join(
        list(filter(None, 
        [yeti_graph_node.attr("imageSearchPath").get() or None,  os.environ.get("PG_IMAGE_PATH")]
    )))
    
    if search_paths:
        path_list.add(*[p.strip() for p in search_paths.split(os.pathsep)])
    return [p.fslash() for p in path_list]

