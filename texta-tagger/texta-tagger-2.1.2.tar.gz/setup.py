import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "texta-tagger",
    version = read("VERSION"),
    author = "TEXTA",
    author_email = "info@texta.ee",
    description = ("texta-tagger"),
    license = "GPLv3",
    packages = ["texta_tagger"],
    data_files = ["VERSION", "requirements.txt", "README.md", "LICENSE"],
    long_description = read("README.md"),
    long_description_content_type = "text/markdown",
    url = "https://git.texta.ee/texta/texta-tagger-python",
    install_requires = read("requirements.txt").strip().split("\n"),
    include_package_data = True,
    extras_require = {
        'mlp': ['texta-mlp'],
        'embedding': ['texta-embedding']
    }
)
