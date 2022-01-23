
import re
import sys
from contextlib import contextmanager

import pymel.core as pm
from ciomaya.lib import scraper_utils
from ciomaya.lib.ae import AEcommon
from ciopath.gpath import Path


DRIVE_LETTER_RX = re.compile(r"^([a-zA-Z]):.*")

ATTRS = {
    "Renderman_for_Maya": {
        "PxrBump": ["filename"],
        "PxrCookieLightFilter": ["map"],
        "PxrDiskLight": ["iesProfile"],
        "PxrDomeLight": ["lightColorMap"],
        "PxrGobo": ["map"],
        "PxrGoboLightFilter": ["map"],
        "PxrLayeredTexture": ["maskTexture", "filename"],
        "PxrMultiTexture": [
            "filename0",
            "filename1",
            "filename2",
            "filename3",
            "filename4",
            "filename5",
            "filename6",
            "filename7",
            "filename8",
            "filename9",
        ],
        "PxrNormalMap": ["filename"],
        "PxrOSL": ["shadername"],
        "PxrProjectionLayer": ["channelsFilenames", "filename"],
        "PxrPtexture": ["filename"],
        "PxrRectLight": ["lightColorMap", "iesProfile"],
        "PxrSphereLight": ["iesProfile"],
        "PxrStdAreaLight": ["profileMap", "rman__EmissionMap", "iesProfile", "barnDoorMap"],
        "PxrStdEnvMapLight": ["rman__EnvMap"],
        "PxrTexture": ["filename"],
        "PxrVisualizer": ["matCap"],
        "RenderManArchive": ["filename"],
        "rmanImageFile": ["File"],
        "rmanTexture3d": ["File"],
        "RMSAreaLight": ["mapname"],
        "RMSCausticLight": ["causticPhotonMap"],
        "RMSEnvLight": ["rman__EnvMap"],
        "RMSGPSurface": [
            "SpecularMapB",
            "SpecularMap",
            "RoughnessMap",
            "MaskMap",
            "SurfaceMap",
            "DisplacementMap",
        ],
        "RMSGeoAreaLight": ["profilemap", "iesprofile", "lightcolormap", "barnDoorMap"],
        "RMSGeoLightBlocker": ["Map"],
        "RMSGlass": ["roughnessMap", "surfaceMap", "specularMap", "displacementMap"],
        "RMSLightBlocker": ["Map"],
        "RMSMatte": ["SurfaceMap", "MaskMap", "DisplacementMap"],
        "RMSOcean": ["roughnessMap", "surfaceMap", "specularMap", "displacementMap"],
    }
}


@contextmanager
def strip_drive():

    if not sys.platform == "win32":
        yield
        return
        
    rx = re.compile(r"^([a-zA-Z]):.*")

    path_dicts = scraper_utils.get_paths(ATTRS)

    some_changed = False
    for p in path_dicts:

        if not DRIVE_LETTER_RX.match(p["path"]):
            continue
        try:
            pm.Attribute(p["plug"]).set(Path(p["path"]).fslash(with_drive=False))
            AEcommon.print_setAttr_cmd(p["plug"])
            some_changed = True

        except (ValueError, TypeError):
            pm.displayWarning(
                "Can't make the plug/path relative '{}'/'{}'".format(p["plug"], p["path"])
            )
            continue
    try:
        yield
    finally:
        if not some_changed:
            return
        pm.displayInfo( "Reverting...")
        for p in path_dicts:
            if not DRIVE_LETTER_RX.match(p["path"]):
                continue
            try:
                pm.Attribute(p["plug"]).set(p["path"])
                AEcommon.print_setAttr_cmd(p["plug"])
            except (ValueError, TypeError):
                pm.displayWarning(
                    "Can't revert the plug/path '{}'/'{}'".format(p["plug"], p["path"])
                )
                continue