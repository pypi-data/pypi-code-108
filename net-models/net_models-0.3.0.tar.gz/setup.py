import pathlib
from setuptools import setup, find_packages

VERSION = "0.3.0"

def load_requirements():
    requirements = []
    REQS_PATH = pathlib.Path(__file__).resolve().parent.joinpath('requirements.txt')
    if REQS_PATH.exists() and REQS_PATH.is_file():
        requirements = [x for x in REQS_PATH.read_text().splitlines() if (len(x) and not x.startswith("#"))]
    return requirements

setup(
    name="net_models",
    packages=find_packages(),
    version=VERSION,
    author="Miroslav Hudec <http://github.com/mihudec>",
    description="Network Config Models",
    install_requires=load_requirements(),
    include_package_data=True
)