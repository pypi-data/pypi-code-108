"""
A basic scraper to collect paths from Bifrost nodes.
"""

import os
import pymel.core as pm
from ciomaya.lib import scraper_utils
from cioseq.sequence import Sequence

################## LEAVE HERE ###################
# Investigate how these attributes work before implementing them.
# ATTRS = {
    # "bifrostGraph": {
    #     "bifShape": ["aiFilename"]
    # },
    # "bifmeshio": { "BifMeshImportNode": ["bifMeshDirectory"] }
    # "Boss": {
    #     "BossEXRInfluence": ["exrFilename"],
    #     "BossGeoProperties": ["cacheName", "cacheFolder"],
    #     "BossSpectralWave": ["velocityCacheName", "cacheName", "cacheFolder", "foamCacheName"],
    #     "BossWaveSolver": ["velocityCacheName", "cacheName", "foamCacheName", "cacheFolder", "remappedInputCacheName"]
    # }
# }

def run(node):
    """
    Find paths in Bifrost nodes.
    """
    paths = scraper_utils.get_paths({"bifmeshio": { "BifMeshImportNode": ["bifMeshDirectory"] }})

    # we want to add all files in the directory for an explicit list of frames,
    # which we evaluate from the time attribute in the  BifMeshImportNode node.
    result = []
    for path in paths:
        cache_node =  pm.Attribute(path["plug"]).node()
        time_plug = cache_node.attr("time")
        start_time_plug = cache_node.attr("startFrame")
        end_time_plug = cache_node.attr("endFrame")
        frames = [int(round(time_plug.get(time=x))) for x in Sequence.create(pm.PyNode(node).attr("frameSpec").get())]
        seq = Sequence.create(frames).intersection(Sequence.create(start_time_plug.get(),end_time_plug.get()))
        template = os.path.join(path["path"], "*.{frame:04d}.bif")
        result.extend([{"path": p, "plug": path["plug"]} for p in seq.expand_format(template)])

    result = scraper_utils.expand_workspace(result)

    return {"paths":result, "env":[]}
