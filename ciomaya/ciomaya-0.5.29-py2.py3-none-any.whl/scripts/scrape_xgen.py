"""
A scraper to collect xgen paths.

This scraper deals with Xgen Description, not Xgen Interactive.
"""
import os
import re
from ciomaya.lib import scraper_utils
import pymel.core as pm
from ciopath.gpath import Path


# Extract values we are interested in from a collection file.
COLLECTION_FIELD_RX = re.compile(
    r"^\s+(xgDataPath|xgDataPath|cacheFileName|mask|pointDir)\s+(.*)$")

# Match the name value from a collection file.
COLLECTION_NAME_RX = re.compile(r"^\s+name\s+(.*)$")

# Match a value in quotes.
QUOTED_REGEX = re.compile(r'[^"^\']*["\'](.*?)["\'][^"^\']*')

ATTRS = {
    "xgen": {
        "xgmSplineCache": ["fileName"],
        "xgmPalette": ["xgFileName"]
    }
}


def run(node):
    """
    Query xgmPalette nodes for xgen collection files.

    Scan those collection files for resources.

    Return the union of all paths found and the collection files themselves.
    """
    scene_dir = os.path.dirname(pm.sceneName())
    paths = scraper_utils.get_paths(ATTRS)
    # Make scene relative paths are absolute.
    for path in paths:
        path["path"] = os.path.join(scene_dir, path["path"])
    collection_files = [p["path"] for p in paths]

    for collection_file in collection_files:
        paths += _paths_from_collection_file(collection_file)

    return {"paths":paths, "env":[]}



def _paths_from_collection_file(collection_file):
    """
    Scan the collection file for resources.

    The following fields are considered to potentially hold paths:

    [xgDataPath, xgDataPath, cacheFileName, mask, pointDir]

    The paths may contain environment variables, most likely:
    # User: ${HOME}/xgen
    # Local: ${XGEN_ROOT}
    # Global: ${XGEN_LOCATION}
    But possibly others

    They may also (and do by default) contain xgen context variables: DESC and
    PROJECT
    """

    try:
        collection_name = _get_collection_name(collection_file)
    except ValueError as e:
        pm.displayWarning(str(e))
        return []

    results = []

    project = pm.workspace(query=True, rootDirectory=True)
    desc = os.path.join(project, "xgen", "collections", collection_name)
    context = {"DESC": desc, "PROJECT": project}

    with open(collection_file) as fp:
        for line in fp.readlines():
            matches = COLLECTION_FIELD_RX.match(line)
            if matches:
                key, value = matches.groups()
                qmatches = QUOTED_REGEX.match(value)
                if qmatches:
                    value = qmatches.groups()[0]

                path = _prepare_unrequired_path(
                    collection_name, key, value, context)
                results.append(path)

    abc_path = _abc_sibling_path(collection_name, collection_file)
    results.append(abc_path)

    return results


def _abc_sibling_path(collection_name, collection_file):
    """Return alembic files that are siblings of the collection files."""
    base, _ = os.path.splitext(collection_file)
    filename = "{}.abc".format(base)
    return _prepare_unrequired_path(collection_name, "abc", filename)


def _prepare_unrequired_path(collection_name, key, value, context=None):
    """
    Create a dict with path and some fields to help identify it's source.

    Paths found in a collection file may not (and probably don't) exist.
    Therefore we wrap the last letter in square brackets. This ensures they are
    resolved by globbing, and therefore not flagged as missing files.
    """
    value = Path(value, context=context).fslash()
    value = value.rstrip("/")
    value = "{}[{}]".format(value[:-1], value[-1])
    return {
        "path": value,
        "collection": collection_name,
        "key": key
    }


def _get_collection_name(collection_file):
    """Get the value from the name field in a collection file."""
    with open(collection_file) as fp:
        for line in fp.readlines():
            name_match = COLLECTION_NAME_RX.match(line)
            if name_match:
                return name_match.groups()[0]
    msg = "No name field in collection file: {}".format(collection_file)
    raise ValueError(msg)
