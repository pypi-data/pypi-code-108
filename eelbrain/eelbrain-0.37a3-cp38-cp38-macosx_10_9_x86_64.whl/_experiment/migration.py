# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Migrate cache structures from older versions"""
from itertools import chain
import os
from pathlib import Path


def squeeze_spaces_in_paths(root: Path):
    "Remove double spaces and trailing spaces in path structure"
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for old in chain(filenames, dirnames):
            new = ' '.join(old.split())
            if new != old:
                src = os.path.join(dirpath, old)
                dst = os.path.join(dirpath, new)
                if os.path.exists(dst):
                    src_rel = os.path.relpath(src, root)
                    raise RuntimeError(f"Trying to rename {src_rel} to {new}, which already exists")
                os.rename(src, dst)
