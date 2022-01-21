import setuptools
from distutils.util import convert_path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

main_ns = {}
ver_path = convert_path('rohub/_version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setuptools.setup(
    name="rohub",
    version=main_ns["__version__"],
    author="Bogusz Janiak",
    author_email="bjaniak@man.poznan.pl",
    description="Rohub is a high-level, user-friendly Python API for working with Research Objects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.man.poznan.pl/stash/projects/ROHUB/repos/rohub-api/browse?at=refs%2Fheads%2Fmaster",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['requests', 'pandas']
)
