import os
import re
from typing import Dict


def recursive_update(base: Dict, update: Dict) -> Dict:
    for k, v in update.items():
        if isinstance(v, dict) and k in base:
            base[k] = recursive_update(base[k], v)
        else:
            base[k] = v
    return base


def expand_environment_variables(d: str) -> str:
    result = []
    finditer = re.finditer(r"\$\{\{(?P<varname>[^${}]+)\}\}", d)
    prev_start = 0
    for match in finditer:
        start, end = match.span()
        result.append(d[prev_start:start])

        varname = match.group("varname")
        if var := os.environ.get(varname):
            result.append(var)
        else:
            raise RuntimeError(f"failed to get env var `{varname}`")

        prev_start = end

    result.append(d[prev_start : len(d)])
    return "".join(result)
