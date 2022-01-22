"""
A scraper to collect paths from Arnold attributes except those on standins.

We scrape path attributes that were added to Maya nodes by Arnold, but not maya
native attributes that Arnold happensto use.
"""

from ciomaya.lib import scraper_utils
import pymel.core as pm
ATTRS = {
    "mtoa":
    {
        "aiImage": ["filename"],
        "aiPhotometricLight":  ["aiFilename"],
        "aiVolume": ["dso", "filename"]
    },
    "MayaBuiltin": {
        "mesh": ["dso"]
    }
}

# See https://docs.arnoldrenderer.com/display/A5AFMUG/Tokens
TOKENS = (r"<tile>", r"<udim>", r"<frame>", r"<f\d?>", r"<aov>", r"#+")


def run(_):

    paths = scraper_utils.get_paths(ATTRS)
    paths = scraper_utils.starize_tokens(paths, *TOKENS)
    paths = _resolve_attr_tokens(paths)
    paths = scraper_utils.expand_workspace(paths)

    paths = scraper_utils.extend_with_tx_paths(paths)
 
    return {"paths":paths, "env":[]}

def _resolve_attr_tokens(paths):
    """
    Resolve image paths specified like so:

    /Volumes/xtr/gd/standin_fixture//sourceimages/<attr:floormap default:alcazar>.jpg

    # https://docs.arnoldrenderer.com/pages/viewpage.action?pageId=40110953

    # REGEX TESTER
    # https://regex101.com/r/eFp4RT/1/
    """

    result = []
    for path in paths:
        # Don't expand if no plug info
        try:
            plug = pm.Attribute(path["plug"])
        except (pm.MayaNodeError, pm.MayaAttributeError):
            result.append(path)
            continue

        # Don't expand  if not file or aiImage
        if not plug.node().type() in [u"file", u"aiImage"]:
            result.append(path)
            continue

        # Don't expand if no <attr: ... > token
        match = scraper_utils.extract_attr_token(path["path"])
        if not match:
            result.append(path)
            continue

        template, attr_name, default_val = match

        found_paths = _expand_attr_token(
            template, plug, attr_name, default_val)
        result.extend(found_paths)
    return result


def _expand_attr_token(template, plug, attr_name, default_val):
    """
    Resolve filenames from mtoa user data attributes.

    Look downstream from the texture plug to find shading engines it affects.
    Loop through the shapes shaded by those engines, testing for the attribute
    corresponding to obj_attr_name. If found, expand the template with that
    name. Also add the shape name to the result object.
    """
    mtoa_const_attr_name = "mtoa_constant_{}".format(attr_name)
    result = []
    if default_val:
        result.append({
            "path": template.replace(scraper_utils.PLACEHOLDER, default_val),
            "plug": plug.name()
        })

    for shading_engine in [node for node in pm.listHistory(plug, future=True) if node.type() == "shadingEngine"]:
        for shape in pm.sets(shading_engine, q=True):
            try:
                replacement = shape.attr(mtoa_const_attr_name).get()
            except pm.MayaAttributeError:
                continue
            result.append({
                "path": template.replace(scraper_utils.PLACEHOLDER, replacement),
                "plug": plug.name(),
                "shape": shape.name()
            })
    return result
