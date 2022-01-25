import io
import pathlib
import re
import setuptools

# version load courtesy:
# https://stackoverflow.com/questions/17583443/what-is-the-correct-way-to-share-package-version-with-setup-py-and-the-package
here = pathlib.Path(__file__).parent
__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open(here / 'contourheightmap' / '__init__.py', encoding='utf_8_sig').read()
    ).group(1)


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="contourheightmap",
    version=__version__,
    author="Luke Miller",
    author_email="dodgyville@gmail.com",
    description="A fast python library for generating topographic contour maps from heightmaps and images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/dodgyville/contourheightmap",
    packages=setuptools.find_packages(),
    install_requires=[
        "dataclasses;python_version>='3.6'",
    ],
    python_requires=">=3.3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)
