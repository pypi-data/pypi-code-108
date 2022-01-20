from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "Pls don't use this."
LONG_DESCRIPTION = "just made this and can't be bothered copying over a bunch"

setup(
    name="yamm_library",
    version=VERSION,
    author="Yamm Elnekave",
    author_email="elnekave.yamm@gmail.com",
    license="MIT",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires=">=3.0",
)
