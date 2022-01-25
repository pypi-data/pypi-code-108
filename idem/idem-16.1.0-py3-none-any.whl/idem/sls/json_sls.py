"""
This module is used to retrieve files from a json source
"""
import json
import os

__virtualname__ = "json"


async def cache(hub, cache_dir, source, loc):
    """
    Take a file from a location definition and cache it in the target location
    """
    if source.startswith("json://"):
        source = source[7:]

    data = json.loads(source)

    os.makedirs(cache_dir, exist_ok=True)

    for uuid, values in data.items():
        c_tgt = os.path.join(cache_dir, f"{uuid}.sls")
        with open(c_tgt, "w+") as fp:
            json.dump(values, fp)

        # There will only be one item in this dictionary
        return c_tgt
