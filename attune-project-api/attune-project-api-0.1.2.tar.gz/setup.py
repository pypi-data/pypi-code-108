from setuptools import find_packages
from setuptools import setup

pip_package_name = "attune-project-api"
package_version = '0.1.2'

requirements = [
    "twisted",
    "pygit2",
    "vortexpy==2.5.6",
    "pytz",
    "pathvalidate",
    # Support for inspecting 7z archives
    "py7zr",
]


doc_requirements = [
    "sphinx",
    "sphinx-rtd-theme",
    "sphinx-autobuild",
    "pytmpdir",
]

requirements.extend(doc_requirements)

setup(
    name=pip_package_name,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=requirements,
    zip_safe=False,
    version=package_version,
    description="",
    author="ServerTribe",
    author_email="support@servertribe.com",
    classifiers=["Programming Language :: Python :: 3.9"],
)
