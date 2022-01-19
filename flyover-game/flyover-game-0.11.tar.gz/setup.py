import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "readme.md").read_text()

# This call to setup() does all the work
setup(
    name="flyover-game",
    version="0.11",
    description="Shoot as many enemy planes as you can before they get you!",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/stevetasticsteve/Flyover",
    author="Stephen Stanley",
    author_email="stevetasticsteve@gmail.com",
    license="GPL version 3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pygame"],
    entry_points={
        "console_scripts": [
            "flyover=flyover.__main__:main",
        ]
    },
)
