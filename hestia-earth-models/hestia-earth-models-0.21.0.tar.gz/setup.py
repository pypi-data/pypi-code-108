import pathlib
from setuptools import find_packages, setup

from hestia_earth.models.version import VERSION

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

REQUIRES = (HERE / "requirements.txt").read_text().splitlines()

# This call to setup() does all the work
setup(
    name='hestia-earth-models',
    version=VERSION,
    description="Hestia's set of modules for filling gaps in the activity data using external datasets (e.g. "
                "populating soil properties with a geospatial dataset using provided coordinates) and internal lookups "
                "(e.g. populating machinery use from fuel use). Includes rules for when gaps should be filled versus "
                "not (e.g. never gap fill yield, gap fill crop residue if yield provided etc.).",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/hestia-earth/hestia-engine-models",
    author="Hestia Team",
    author_email="guillaumeroyer.mail@gmail.com",
    license="GPL",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=("tests", "scripts")),
    include_package_data=True,
    install_requires=REQUIRES
)
