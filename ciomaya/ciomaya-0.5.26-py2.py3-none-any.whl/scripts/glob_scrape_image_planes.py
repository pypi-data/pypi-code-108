"""
A scraper to collect image plane movies, stills, and sequences.
"""

import os
import re
import pymel.core as pm
 
IMAGE_PLANE_FILENAME_REGEX = re.compile(r"^(.*)\.(\d+)\.([a-z0-9]+$)")
 

def run(_):
    """
    Find image_plane sequences.
    """
    result = []

    for ip in pm.ls(type="imagePlane"):
        iptype = ip.attr("type").get()
        if iptype == 1: #texture
            continue
        plug = ip.attr("imageName")
        path = plug.get().strip()
        if path:
            # movie or still or sequence
            if iptype == 0 and  ip.attr("useFrameExtension").get():
                #sequence - replace frameExt with *
                match = IMAGE_PLANE_FILENAME_REGEX.match(path)
                if match:
                    root, _, ext = match.groups()
                    path = "{}.*.{}".format(root, ext)

            result.append({
                "plug":plug.name(),
                "path":path
            })

    return result
