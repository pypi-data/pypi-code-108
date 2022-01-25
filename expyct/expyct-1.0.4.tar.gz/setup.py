import sys
from pathlib import Path

from setuptools import setup

with open(Path(__file__).parent / "expyct" / "__version__.py") as file:
    VERSION = file.readline().split(" ")[2].rstrip().strip('"')

if (3, 6) <= sys.version_info < (3, 7):
    INSTALL_REQUIRES = ["dataclasses", "types-dataclasses", "backports-datetime-fromisoformat"]
else:
    INSTALL_REQUIRES = []

if __name__ == "__main__":
    setup(version=VERSION, install_requires=INSTALL_REQUIRES)
