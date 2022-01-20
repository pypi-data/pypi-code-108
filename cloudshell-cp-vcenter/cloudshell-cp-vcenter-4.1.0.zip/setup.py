import os

from setuptools import find_packages, setup
from setuptools.version import __version__ as setuptools_version

if tuple(map(int, setuptools_version.split("."))) < (40, 0):
    import sys

    python = sys.executable
    try:
        s = os.system(f'{python} -m pip install "setuptools>=40"')
        if s != 0:
            raise Exception
    except Exception:
        raise Exception("Setuptools>40 have to be installed")

    os.execl(python, python, *sys.argv)


with open(os.path.join("version.txt")) as version_file:
    version_from_file = version_file.read().strip()

with open("requirements.txt") as f_required:
    required = f_required.read().splitlines()

with open("test_requirements.txt") as f_tests:
    required_for_tests = f_tests.read().splitlines()

setup(
    name="cloudshell-cp-vcenter",
    url="http://www.qualisystems.com/",
    author="QualiSystems",
    author_email="info@qualisystems.com",
    packages=find_packages(),
    description=(
        "This Shell enables setting up vCenter as a cloud provider in CloudShell. It "
        "supports connectivity, and adds new deployment types for apps which can be "
        "used in CloudShell sandboxes."
    ),
    install_requires=required,
    tests_require=required_for_tests,
    python_requires="~=3.7",
    version=version_from_file,
    package_data={"": ["*.txt"]},
    include_package_data=True,
)
