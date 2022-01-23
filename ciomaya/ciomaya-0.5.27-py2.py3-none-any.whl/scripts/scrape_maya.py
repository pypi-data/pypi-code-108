"""
A basic scraper to collect paths from Maya nodes.

Maya Attributes may contain token substitution patterns that are only valid in
other renderers. We have to resolve them because the policy of each scraper is
to scrape only those custom attributes that it implements. Other scrapers do NOT
scape their tokens in attributes they do not implement, including Maya's
file.computedFileTextureNamePattern.

"""
import pymel.core as pm
import re
from ciomaya.lib import scraper_utils


ATTRS = {
    "AbcImport": {"AlembicNode": ["abc_File"]},
    "MayaBuiltin": {
        "file": ["computedFileTextureNamePattern"],
        "cacheFile": ["cachePath"],
        "gpuCache": ["cacheFileName"],
        "assemblyReference": ["definition"],
    },
}

TOKENS = (
    r"#+",  # image.####.exr - hash
    r"_MAPID_",  # image_MAPID_.exr - mapid
    r"%0\d+d",  # image.%04d.exr - percent
    r"<UDIM>",  # image.<UDIM>.exr - udim_mari
    r"<UVTILE>",  # image.<UVTILE>.exr - udim_mudbox
    r"<TileRef>",  # Vray
    r"<tile>",  # Arnold tile
    r"<aov>",  # Arnold AOV
    r"\$\d*U.*\$\d*V",  # image.u$2U_v$2V.exr or image.u$Uv$V.exr, etc - udim_vray
    r"u<U>_v<V>",  # image.u<U>_v<V>.exr - udim_zbrush
    r"u<U>_v<V>_<f>",  # image.u<U>_v<V>_<f>.exr - udim_zbrush_f
    r"<f\d?>",  # image.<f>.exr or image.<f4>.exr - frame_seq
    r"<FrameNum>",  # image.<FrameNum>.ext - Redshift
    r"<Frame>",  # image.<Frame>.ext - Redshift
)


def run(_):
    """
    Find paths in Maya attributes on Maya nodes.

    * Replace any of the above tokens with a "*"
    * Add workspace.mel ([] signifies not required)
    * Make relativbe paths absolute.
    * Add tx equivalents of image files ([] signifies not required)
    * Add the main Maya file and references.

    Image file textures may have a sibling ".tx file".
    """

    paths = scraper_utils.get_paths(ATTRS)
    paths.extend(_get_assembly_assets())
    paths = scraper_utils.starize_tokens(paths, *TOKENS)
    paths.append({"path": "workspace.me[l]"})
    paths = scraper_utils.expand_workspace(paths)
    paths = scraper_utils.extend_with_tx_paths(paths)
    paths.extend(_get_scene_files())

    return {"paths": paths, "env": []}


def _get_scene_files():
    result = []
    for ref in pm.listReferences(recursive=True):
        result.append({"path": str(ref.path), "refNode": ref.refNode})

    scene_name = str(pm.sceneName())
    if scene_name:
        result.append({"path": scene_name})
    return result


def _get_assembly_assets():
    """
    Get assets definied in assemblyDefinition and assemblyReference nodes.

    Something strange with the representations array attribute type. Means we can't use
    scraper_utils.get_paths()

    We make the value globbabl[e] so that if it's missing it doesn't complain.

    Returns: list(dict): list of (path/plug) pairs
    """
    result = []
    for node in pm.ls(type=("assemblyDefinition", "assemblyReference")):
        data_plugs = [
            node.attr(p) for p in pm.PyNode(node).attr("rep").elements() if p.endswith("repData")
        ]
        for plug in data_plugs:
            value = plug.get()
            if value:
                value = "{}[{}]".format(value[:-1], value[-1])
                result.append({"path": value, "plug": plug.name()})
    return result
