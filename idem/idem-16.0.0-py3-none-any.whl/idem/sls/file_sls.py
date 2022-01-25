"""
This module is used to retrive files from a local source
"""
import os
import shutil


__virtualname__ = "file"


async def cache(hub, cache_dir, source, loc):
    """
    Take a file from a location definition and cache it in the target location
    """
    full = os.path.join(source, loc)
    if full.startswith("file://"):
        full = full[7:]
    c_tgt = os.path.join(cache_dir, full.lstrip(os.sep))
    c_dir = os.path.dirname(c_tgt)
    os.makedirs(c_dir, exist_ok=True)
    if not os.path.isfile(full):
        return None
    shutil.copy(full, c_tgt)
    return c_tgt
