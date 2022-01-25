from __future__ import absolute_import, division, print_function

import os
import re
import shutil
from typing import List
import zipfile

from setuptools import Distribution, find_packages, setup


# mypy: ignore-errors


def find_version(path):
    with open(path) as f:
        match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.MULTILINE,
        )
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")


def move_file(filename):
    # TODO(rkn): This feels very brittle. It may not handle all cases. See
    # https://github.com/apache/arrow/blob/master/python/setup.py for an
    # example.
    source = filename

    destination = os.path.join(os.path.dirname(__file__), filename)
    # Create the target directory if it doesn't already exist.
    parent_directory = os.path.dirname(destination)
    if not os.path.exists(parent_directory):
        os.makedirs(parent_directory)
    if not os.path.exists(destination):
        print("Copying {} to {}.".format(source, destination))
        shutil.copy(source, destination, follow_symlinks=True)


def download_and_copy_files(url: str, files_to_copy: List[str]) -> None:
    """
    Downloads an archive from S3, unzips it and then copies the file to the anyscale folder.
    """
    import io
    import tempfile

    import requests

    work_dir = tempfile.mkdtemp()
    try:
        content = requests.get(url).content
        archive = zipfile.ZipFile(io.BytesIO(content))
        archive.extractall(pwd=work_dir.encode())
        for f in files_to_copy:
            destination = os.path.join("anyscale", f)
            # Remove the file if it already exists to make sure old
            # versions get removed.
            try:
                os.remove(destination)
            except OSError:
                pass
            shutil.copy2(f, destination)
            os.chmod(destination, 0o755)
            move_file(destination)
    finally:
        shutil.rmtree(work_dir)


class BinaryDistribution(Distribution):
    def is_pure(self):
        return True

    def has_ext_modules(self):
        return True


# If adding new webterminal deps,
# Update backend/server/services/application_templates_service.py
# to prevent users from uninstalling them.
extras_require = {"backend": ["terminado==0.10.1", "tornado"]}


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


setup(
    name="anyscale",
    version=find_version("anyscale/version.py"),
    author="Anyscale Inc.",
    description=("Command Line Interface for Anyscale"),
    packages=[*find_packages(exclude="tests")],
    distclass=BinaryDistribution,
    setup_requires=["setuptools_scm"],
    package_data={
        "": [
            "*.yaml",
            "*.json",
            *package_files("anyscale/client"),
            *package_files("anyscale/sdk"),
        ],
    },
    install_requires=[
        "boto3==1.16.52",
        "aiobotocore[boto3]==1.2.2",
        "botocore==1.19.52",
        "aiohttp==3.7.4.post0",
        "aiohttp_middlewares",
        "aioredis==1.3.1",
        "certifi",
        "conda-pack",
        "Click>=7.0",
        "colorama",
        "expiringdict",
        "GitPython",
        "jinja2",
        "jsonpatch",
        "jsonschema",
        "packaging",
        "pathspec==0.8.1",
        "pydantic>=1.8.1",
        "python-dateutil",
        "ray >= 1.4.0",
        "requests",
        "sentry_sdk",
        "six >= 1.10",
        "tabulate",
        "urllib3 >= 1.15",
        "wrapt",
        "pyyaml",
    ],
    extras_require=extras_require,
    entry_points={"console_scripts": ["anyscale=anyscale.scripts:main"]},
    include_package_data=True,
    zip_safe=False,
)
