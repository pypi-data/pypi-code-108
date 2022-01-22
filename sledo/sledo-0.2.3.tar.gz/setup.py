import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sledo",
    version="0.2.3",
    description="A simple demodata generator for the command-line.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/luxbe/sledo",
    author="luxbe, Jakob, Ammar, Melli, Deniz, Larissa",
    author_email="luxbe@tutanota.com, jakobjonathan@aol.com, ammar@begovic.eu, melina.petersen99@web.de, denizcan.1999er@gmail.com, larissac0504@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=[
        'click',
        'pyyaml',
        'schema'
    ],
    entry_points={
        "console_scripts": [
            "sledo=sledo:cli"
        ]
    },
)
