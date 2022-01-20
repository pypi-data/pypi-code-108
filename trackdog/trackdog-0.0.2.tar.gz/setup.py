import os
import re

from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

packages = find_packages()
package_dir = "."


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__), "trackdog", "__init__.py")
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        raise RuntimeError("Cannot find version in {}".format(init_py))


setup(
    name="trackdog",
    version=read_version(),
    description="Experiment tracking tool for machine learning",
    license="Apache 2.0",
    long_description=long_description,
    author="Ce Gao",
    author_email="gaocegege@hotmail.com",
    url="",
    packages=packages,
    package_dir={"": package_dir},
    install_requires=["varname", "click", "plotext", "terminaltables"],
    entry_points={
        "console_scripts": [
            "trackdog = trackdog.script.cli:cli",
        ],
    },
)
