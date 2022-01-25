"""Utils."""

from yaml import safe_load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper  # noqa:F401
import pathlib
from typing import Dict

PARAMS_FILE = "params.yaml"


def read_params(params_file: str) -> Dict:
    """Read pipeline arguments from a yaml file."""
    data = safe_load(pathlib.Path(params_file).read_text())
    return data["args"]


def serialise_params(data: Dict) -> str:
    """Serialise params to format required by $ kfp run submit."""
    out = ""
    for k in data:
        out += f"{k}={data[k]} "
    return out.rstrip()
