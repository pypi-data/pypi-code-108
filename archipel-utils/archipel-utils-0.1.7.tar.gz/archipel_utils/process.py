"""Copyright Alpine Intuition Sàrl team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import subprocess
from typing import Dict, List, Union


def get_vram_usages(pids: Union[int, List[int]]) -> Dict[int, int]:
    """Get GPU VRAM usage (in MB) for one or more pids.

    Args:
        pids: a pid or a list of pids.

    Returns:
        usages: a dictionnary of VRAM usage for the each given pids.

    Raises:
        None.
    """

    if isinstance(pids, int):
        pids = [pids]

    cmd = [
        "nvidia-smi",
        "--query-compute-apps=used_memory,pid",
        "--format=csv,noheader,nounits",
    ]
    outputs = subprocess.run(cmd, check=True, capture_output=True, text=True)

    # Clean nvidia-smi outputs
    lines = outputs.stdout.strip().split("\n")
    lines = [line for line in lines if line != ""]

    usages = {}
    for line in lines:
        gpu_mem, pid = map(int, line.split(", "))
        if pid not in pids:
            continue
        usages[pid] = gpu_mem

    for pid in pids:
        if pid not in usages:
            usages[pid] = 0

    return usages


def get_ram_usages(pids: Union[int, List[int]]) -> Dict[int, Dict[str, int]]:
    """Get RAM memory usage (in MB) for one or more pids.

    Args:
        pids: a pid or a list of pids.

    Returns:
        usage: A list of RAM usage for the input PID list.

    Raises:
        None.
    """

    if isinstance(pids, int):
        pids = [pids]

    cmd = "ps -eo vsize,rss,pid".split()
    outputs = subprocess.run(cmd, check=True, capture_output=True, text=True)
    lines = outputs.stdout.split("\n")

    usages = {}
    for line in lines[1:-1]:
        line = re.sub(r"\s+", " ", line)
        virt_ram_mem, used_ram_mem, pid = map(int, line.strip().split(" "))
        if pid not in pids:
            continue
        usages[pid] = {
            "virt": int(virt_ram_mem / 1024),
            "used": int(used_ram_mem / 1024),
        }

    for pid in pids:
        if pid not in usages:
            usages[pid] = {"virt": 0, "used": 0}

    return usages
