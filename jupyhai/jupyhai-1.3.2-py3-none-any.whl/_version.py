import json
from contextlib import suppress
from pathlib import Path
from typing import Optional

__all__ = ["__version__"]


def _retrieve_version() -> Optional[str]:
    HERE = Path(__file__).parent.resolve()

    for settings in HERE.rglob("package.json"):
        with suppress(FileNotFoundError), settings.open() as f:
            version = json.load(f)["version"]
            return version.replace("-alpha.", "a").replace("-beta.", "b").replace("-rc.", "rc")
    return None


# No package.json within this tree means we must be in devel mode
__version__ = (_retrieve_version() or "0.0.0+devel")
