import json
import os
import sys

from setuptools import setup


def get_build_info_path():
    root = os.path.dirname(__file__)
    return os.path.join(root, "build_info.json")


def get_build_info_json():
    build_info_path = get_build_info_path()
    with open(build_info_path) as build_info_file:
        build_info_str = build_info_file.read().strip()
        build_info__json = json.loads(build_info_str)
    return build_info__json


def get_version():
    build_info_json = get_build_info_json()
    version = build_info_json["version"]
    return version


def update_requires():
    requires = []
    
    with open("Pipfile.lock") as lock_file:
        lock_json = json.loads(lock_file.read())
    
    for item in lock_json["default"]:
        requires.append(item + lock_json["default"][item]["version"])
    
    return requires


if sys.version_info < (3, 6):
    sys.exit('Only Python 3.6 and above is suppoorted.')


setup(
    name="cs18-api-client",
    version=get_version(),
    author="Quali",
    author_email="support@qualisystems.com",
    install_requires=update_requires(),
    packages=["gateways"],
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)
