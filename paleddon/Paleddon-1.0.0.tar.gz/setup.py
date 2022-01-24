import os
import sys

from setuptools import setup
from paleddon import __version__

here = os.path.abspath(os.path.dirname(__file__))

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist")
    os.system("twine upload dist/* --skip-existing")
    sys.exit()

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="Paleddon",
    version=__version__,
    description="Tool to create basic addons for Pale Moon with which to have a starting point.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jalkhov/paleddon",
    author="Pedro Torcatt",
    author_email="ing.torcattsoto.2020@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="xpi pale-moon addon uxp",
    packages=["paleddon"],
    include_package_data=True,
    python_requires=">=3.0",
    install_requires=open(
        os.path.join(here, "requirements.txt"), encoding="utf-8"
    )
    .read()
    .split("\n"),
    project_urls={
        "Bug Reports": "https://github.com/Jalkhov/paleddon/issues",
        "Source": "https://github.com/Jalkhov/paleddon/",
    },
    entry_points={"console_scripts": [
        "paleddon=paleddon.main:cli"]},
)
