import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf8").read()


def get_requirements(fname):
    excluded_packages = ["pytest"]
    req_string = read(fname)
    return [req.strip() for req in req_string.strip().split("\n") if req.strip() not in excluded_packages]


setup(
    name="texta-parsers",
    version=read("VERSION"),
    author="TEXTA",
    author_email="info@texta.ee",
    description=("texta-parsers"),
    license="GPLv3",
    packages=['texta_parsers', 'texta_parsers/tools'],
    data_files=["VERSION", "requirements.txt", "README.md"],
    long_description_content_type="text/markdown",
    long_description=read('README.md'),
    install_requires=get_requirements("requirements.txt"),
    extras_require={
        'mlp': ['texta-mlp'],
    }
)
