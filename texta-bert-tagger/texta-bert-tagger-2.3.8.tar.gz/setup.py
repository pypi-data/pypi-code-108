import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "texta-bert-tagger",
    version = read("VERSION"),
    author = "TEXTA",
    author_email = "info@texta.ee",
    description = ("texta-bert-tagger"),
    license = "GPLv3",
    packages = [
        "texta_bert_tagger"
    ],
    data_files = ["VERSION", "requirements.txt", "README.md"],
    long_description = read("README.md"),
    long_description_content_type="text/markdown",
    url="https://git.texta.ee/texta/texta-bert-tagger-python",
    install_requires = read("requirements.txt").split("\n"),
    include_package_data = True
)
