import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pygame-plus",
    version="0.0.19",
    description="Pygame with some added features for beginners",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mrdevet/PygamePlus",
    author="Casey Devet",
    author_email="cjdevet@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8"
    ],
    packages=["pygameplus", "pygameplus.demos"],
    install_requires=["pygame"],
    include_package_data=True,
    python_requires=">=3.8"
)