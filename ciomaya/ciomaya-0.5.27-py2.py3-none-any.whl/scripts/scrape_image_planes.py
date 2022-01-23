"""
A scraper to collect image plane movies, stills, and sequences.

It demonstrates how to use attr.get(time=t) to evaluate a sequence for a frame
range without evaluating the whole DG. It means that if an image plane uses 10
files from a folder of 5000, we only upload the 10 files.
"""

import re
import glob
import pymel.core as pm
from cioseq.sequence import Sequence
from ciomaya.lib import scraper_utils

IMAGE_PLANE_FILENAME_REGEX = re.compile(r"^(.*)\.(\d+)\.([a-z0-9]+$)")

def run(node):
    """
    Find image_plane sequences.
    """

    paths = []
    sequence = Sequence.create(pm.PyNode(node).attr("frameSpec").get())

    for image_plane in pm.ls(type="imagePlane"):
        paths.extend(paths_for_image_plane(image_plane, sequence))
    
    paths = scraper_utils.expand_workspace(paths)
    return {"paths":paths, "env":[]}

def paths_for_image_plane(image_plane, sequence):
    """
    image_plane type may be image (possibly sequence), procedural textur, or movie

    If it's a movie, or sequence is off, return the path.
    For textures, there's no file so return empty list.

    For sequences,
    1. evaluate the imagePlane.frameExtension for the conductorRender node
       range.
    2. Determine padding from the sequence on disk.
    3. Compute the filenames we need for the rendered range.
    """

    ws = pm.Workspace()
    iptype = image_plane.attr("type").get()
    if iptype == 1:  # texture
        return []

    plug = image_plane.attr("imageName")
    plug_name = plug.name()
    path = ws.expandName(plug.get().strip())

    match = IMAGE_PLANE_FILENAME_REGEX.match(path)

    if iptype == 2 or (not image_plane.attr("useFrameExtension").get()) or (not match):
        # not sequence
        return [{
            "plug": plug_name,
            "path": path
        }]

    root, _, ext = match.groups()
    existing = glob.glob("{}.*.{}".format(root, ext))
    if not existing:
        return []
    padding = min([len(fn.split(".")[-2]) for fn in existing])

    # By evaluating, we account for expressions. offsets, driven keys, timewarps etc.
    frame_seq =  Sequence.create([image_plane.attr(
        "frameExtension").get(time=f) for f in sequence])
    path = "{}.<f{}>.{}".format(root, padding, ext)
    pathnames = scraper_utils.resolve_to_sequence(path, frame_seq)
    return [{"plug": plug_name, "path": p} for p in pathnames ]

