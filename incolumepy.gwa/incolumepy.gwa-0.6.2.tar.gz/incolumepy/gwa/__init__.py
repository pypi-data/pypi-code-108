"""
Principal Module.

Update metadata from version by semver
"""
from pathlib import Path

import toml

__root__ = Path(__file__).parents[0]
version_file = __root__.joinpath("version.txt")
version_file.write_text(f"{toml.load(Path(__file__).parents[2].joinpath('pyproject.toml'))['tool']['poetry']['version']}\n")
__version__ = version_file.read_text().strip()


if __name__ == "__main__":  # pragma: no cover
    print(__root__)
    print(__version__)
