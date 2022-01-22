
"""
A scraper to return paths used by XGen.

This scraper searches description files contained in xgmPalette files.
"""
import maya.api.OpenMaya as om
import pymel.core as pm
import os


def run(_):
    """
    Find paths related to xgen.

    This is currently a stub.
    """
    result = []
    scene_dir = os.path.dirname(pm.sceneName())
    for node in pm.ls(type="xgmPalette"):
        for att in ["xgFileName", "xgBaseFile", "xgDeltaFiles"]:
            attr = node.attr(att)
            path = attr.get()
            if path:
                path = path if os.path.isabs(path) else os.path.join(scene_dir, path)
                result.append({"path": path, "plug":attr.name()})
    return result
 