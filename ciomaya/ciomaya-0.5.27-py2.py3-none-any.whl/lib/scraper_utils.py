
import os
import re
import sys

from ciopath.gpath import Path

import maya.api.OpenMaya as om
import pymel.core as pm

PLATFORM = sys.platform
PLACEHOLDER = "CIOPLACEHOLDER"  # Can be anything unique.
ATTR_TOKEN_REGEX = re.compile(
    r"<attr:([0-9a-zA-Z_]+)(?:\s+index:([0-9]+))?(?:\s+default:([0-9a-zA-Z_]+))?>")


def get_paths(attrs):
    """
    Get paths from attributes.

    First get the plugs and iterate. If the leaf level plug is an array, then we
    find out with isArray() and iterate over its elements.

    """
    result = []
    plug_list = _get_plugs(attrs)
    plug_iter = om.MItSelectionList(plug_list)
    while not plug_iter.isDone():
        plug = plug_iter.getPlug()
        plug_iter.next()

        if plug.isArray:
            for index in range(plug.numElements()):
                child_plug = plug.elementByPhysicalIndex(index)
                value = _get_value(child_plug)
                if value:
                    result.append(_get_value(child_plug))
        else:
            value = _get_value(plug)
            if value:
                result.append(_get_value(plug))
    return result


def _get_plugs(attrs):
    """
    Return a SelectionList that contains the actual existing plugs.

    When we get a node's plug from the att name, it may be a child of a compound
    array plug (or nested several levels). In this case the plug name will be of
    the form node_name.parentPlug[-1].childPlug This (-1) is a nonexistent plug.
    In order to get the actual plug elements, if they exist, we use a
    SelectionList. We add a wildcard name to the selectionlist to get the real
    plugs it contains.

    The [-1] indicator is only used for array parent plugs, not leaf level array
    plugs.

    [
        "someGrouping": {
            "someNodeType": [
                "topLevelAttributeName",
                "nestedAttributeName",
                "arrayTypeAttributeName",
                "childOfNestedArrayTypeAttributeName"
            ],
            ...
        },
        ...
    ]
    """
    all_node_types = pm.allNodeTypes()
    selection_list = om.MSelectionList()
    for section in attrs:
        for nodetype in attrs[section]:
            if nodetype in all_node_types:
                for node in pm.ls(type=nodetype):
                    for attr in attrs[section][nodetype]:
                        try:
                            selection_list.add(
                                node.attr(attr).name().replace("[-1]", "[*]"))
                        except (RuntimeError, pm.MayaAttributeError):
                            pass
    return selection_list


def _get_value(plug):
    value = plug.asString()
    if value:
        return {"path": value, "plug": plug.name()}


def starize_tokens(paths, *tokens):
    """
    Replace any of the given tokens with a '*'

    Accepts either a list of objects with a path property, or a list of strings.
    """
    token_rx = re.compile("|".join(tokens), re.IGNORECASE)
    for i in range(len(paths)):
        try:
            paths[i]["path"] = token_rx.sub("*", paths[i]["path"])
        except TypeError:
            paths[i] = token_rx.sub("*", paths[i])
    return paths


def expand_env_vars(paths):
    """Use Path() to resolve env vars.

    Accepts either a list of objects with a path property, or a list of strings.
    """
    for i in range(len(paths)):
        try:
            paths[i]["path"] = Path(paths[i]["path"]).fslash()
        except TypeError:
            paths[i] = Path(paths[i]).fslash()
    return paths


def expand_workspace(paths):
    """
    Expand in a non-platform-dependent way.

    Paths are either a list of strings, a list of objects with a "path" key, or
    a mix.

    Sometimes on a Mac/Linux, the user will have a scene with Windows paths in
    it. That's a mistake of course, but we want to show them the mistake. If we
    just expandName, then those windows paths will be treated as relative. The
    expandName function prepends the workspace, and to add insult to injury, it
    deletes everything after the drive letter. You end up with
    /Volumes/blah/blah/C So we check that its absolute before running through
    expandName and we leave it in tact with its drive letter so the user can
    identify it during validation.

    If any empty paths turn up here, then remove them, because whan an empty path
    gets prepended by the workspace, we end up with the whole project uploaded.
    """
    ws = pm.Workspace()
    result = []

    for p in paths:
        try:
            if p["path"]:
                if Path(p["path"]).relative:
                    p.update({"path": ws.expandName(p["path"])})
                    result.append(p)
                else:
                    result.append(p)
        except (TypeError, KeyError):
            if p:
                if Path(p).relative:
                    result.append(ws.expandName(p))
                else:
                    result.append(p)

    return result


def extend_with_tx_paths(paths):
    """
    Add the tx sister for image files

    Use glob notation around one letter in the extension (.t[x]) because when
    paths are finally resolved, the list is expanded by globbing.

    As TX files are not critical, we don't want to block the submission if they
    don't exist. Glob will ultimately expand to no files if the file does not
    exist.
    """

    image_ext_regex = re.compile(
        r"^\.(jpg|jpeg|gif|iff|psd|png|pic|tga|tif|tiff|bmp|hdr|sgi|rla|exr|ico|dpx|cin)$", re.IGNORECASE)
    txpaths = []
    for p in paths:
        root, ext = os.path.splitext(p["path"])
        if image_ext_regex.match(ext):
            txpath = "{}.t[x]".format(root)
            txpaths.append({"plug": p["plug"], "path": txpath})
    return paths+txpaths


def resolve_to_sequence(template, sequence):
    """
    Replace all the popular frame placeholders with a consistent template
    expression that specifies the padding
    """

    orig_template = template
    # replace 4 hashes with  {frame:04d}
    template = re.compile(r"(#+)", re.IGNORECASE).sub(
        lambda match: "{{frame:0{:d}d}}".format(len(match.group(1))),
        template)

    # replace $F4 with {frame:04d}
    template = re.compile(r"\$F(\d?)", re.IGNORECASE).sub(
        lambda match: "{{frame:0{:d}d}}".format(int(match.group(1) or "1")),
        template)

    # replace <f4> with {frame:04d}
    template = re.compile(r"<F(\d?)>", re.IGNORECASE).sub(
        lambda match: "{{frame:0{:d}d}}".format(int(match.group(1) or "1")),
        template)

    # replace <frame> with {frame}
    template = re.compile(r"<frame>", re.IGNORECASE).sub("{frame}", template)

    if orig_template == template:
        return [orig_template]

    return sequence.expand_format(template)


def extract_attr_token(filename):
    """   
    Find <attr: token in  paths specified like so:

    /Volumes/xtr/gd/standin_fixture//sourceimages/<attr:floormap default:alcazar>.jpg

    # https://docs.arnoldrenderer.com/pages/viewpage.action?pageId=40110953

    # REGEX TESTER
    # https://regex101.com/r/eFp4RT/1/
    # """
    match = ATTR_TOKEN_REGEX.search(filename)
    if not match:
        return

    # cant do indices
    if match.group(2) is not None:
        return

    attr_name = match.group(1)
    default_val = match.group(3)
    template = ATTR_TOKEN_REGEX.sub(PLACEHOLDER, filename)

    return template, attr_name, default_val
