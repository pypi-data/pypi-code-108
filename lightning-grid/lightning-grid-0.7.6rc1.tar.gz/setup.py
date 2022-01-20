#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Original solution from
#
#      https://github.com/navdeep-G/setup.py
#
#  Original license notice:
#
#  Copyright 2020 navdeep-G & GitHub contributors
#
#  Permission is hereby granted, free of charge, to any
#  person obtaining a copy of this software and associated
#  documentation files (the "Software"), to deal in the
#  Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute,
#  sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall
#  be included in all copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

#  NOTE: To use the 'upload' functionality of this file, you must:
#    $ pip install twine

import os
from pathlib import Path
from shutil import rmtree
import sys
import atexit

from setuptools import Command, find_packages, setup
from setuptools.command.install import install


def read_grid_metadata_file(variable_name: str):
    """Reads the values from the grid metadata.py file without importing it.

    This will read the value associated with a line in the metadata.py file
    which has the format:

        foo_variable = 'bar_value'

    returning the python <string> ``foo_value`` if called with f("foo_variable").

    Note: This will only work for assignments that occur on a single line.
    """
    metadata_file = Path(__file__).parent.joinpath("grid", "metadata.py")
    with metadata_file.open("rt") as f:
        for line in f.readlines():
            if line.startswith(variable_name):
                val = line.split("=", maxsplit=1)[-1]  # don't split at second "=" char in case it is in the value.
                val = val.strip()  # remove leading and trailing whitespace
                val = val.strip("'")  # remove ' char from beginning and end (value is already a string)
                val = val.strip('"')  # remove " char from beginning and end (value is already a string)
                return val
    return ""


#   Package meta-data.
NAME = 'grid'
PACKAGE_NAME = read_grid_metadata_file("__package_name__")
DESCRIPTION = 'Grid Python SDK.'
URL = 'https://grid.ai'
EMAIL = 'grid-eng@grid.ai'
AUTHOR = 'Grid AI Engineering'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = os.getenv("VERSION", read_grid_metadata_file("__version__"))

#  What packages are required for this module to be executed?
REQUIRED = []
with open('requirements.txt') as f:
    for line in f.readlines():
        REQUIRED.append(line.replace('\n', ''))

#  What packages are optional?
EXTRAS = {}

#  The rest you shouldn't have to touch too much :)
#  ------------------------------------------------
#  Except, perhaps the License and Trove Classifiers!
#  If you do change the License, remember to
#  the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

#  Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


def check_environment_variables(variables: list) -> bool:
    """
    Check that environment variables have been
    set, raising an error if they have not.

    Parameters
    ----------
    variables: list
        List of environment variables to check.
    Returns
    -------
    bool
        Returns True if all environment variables
        have been set correctly.
    """
    for variable in variables:
        if not os.getenv(variable):
            raise ValueError(f'Environment variable `{variable}` has not been set.')

    return True


class GCPStorage:  # pragma: no cover
    """
    Google Cloud Platform Storage wrapper for uploading
    objects to GCP.
    """
    def __init__(self):
        from google.cloud import storage
        self.storage_client = storage.Client()

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))

    def delete_blob(self, bucket_name, blob_name):
        """Deletes a blob from the bucket."""
        # bucket_name = "your-bucket-name"
        # blob_name = "your-object-name"
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

        print("Blob {} deleted.".format(blob_name))

    def delete_blobs(self, bucket_name, prefix=''):
        """ Deletes all blobs with a specific prefix from a bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob.name.startswith(prefix):
                blob.delete()

    def list_blobs(self, bucket_name, prefix='', delimiter=None):
        """Lists all the blobs in the bucket."""
        blobs = self.storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)

        names = []
        for blob in blobs:
            names.append(blob.name)
        return names

    def download_blob(self, bucket_name, source_blob_name, destination_file_name, source_blob_prefix=''):
        """Downloads a blob from the bucket."""
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob.name.startswith(source_blob_prefix):
                print("downloading")
                blob.download_to_filename(destination_file_name)


def upload_gcp_wheel(gcp_storage, version, bucket_name, blob_path):
    """
    Uploads lightning wheel to it's designated GCP bucket.
    """
    whl_exists = False
    for file in os.listdir('dist'):
        if '.whl' in file:
            wheel = file
            whl_exists = True

    if whl_exists:
        lastest_path = Path(blob_path) / "latest" / wheel
        version_path = Path(blob_path) / version / wheel

        # delete existing object in "latest" directory
        gcp_storage.delete_blobs(bucket_name=bucket_name, prefix=f'{blob_path}/latest/')

        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=lastest_path
        )
        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=version_path
        )
    else:
        raise ValueError("You did not build a wheel for this project.")


class UploadCommandPyPi(Command):
    """Support setup.py upload-pypi."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        # skipcq: BAN-B605
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        # skipcq: BAN-B605
        os.system('twine upload dist/*')

        sys.exit()


class UploadCommandGCP(Command):
    """Support setup.py upload-gcp."""

    description = 'Build and publish the package to GCP.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Checking environment variables…')
        check_environment_variables(['GOOGLE_APPLICATION_CREDENTIALS', 'GCP_GRID_BUCKET', 'GCP_BLOB_PATH'])

        self.status('Building Source and Wheel (universal) distribution…')
        # skipcq: BAN-B605
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading to GCP…')
        gcp_storage = GCPStorage()
        upload_gcp_wheel(
            gcp_storage=gcp_storage,
            version=VERSION,
            bucket_name=os.getenv('GCP_GRID_BUCKET'),
            blob_path=os.getenv('GCP_BLOB_PATH')
        )

        sys.exit()


class Install(install):
    """
    Override setup tools `install` command to do any pre/post install logic.
    """
    def run(self):
        def _post_install():
            def find_module_path():
                for p in sys.path:
                    if os.path.isdir(p) and "grid" in os.listdir(p):
                        return os.path.join(p, "grid")

            install_path = find_module_path()

            from grid.cli.utilities import install_autocomplete
            install_autocomplete()

        atexit.register(_post_install)
        install.run(self)


#  Where the magic happens:
setup(
    name=PACKAGE_NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests', 'tests.*')),
    entry_points={
        'console_scripts': ['grid=grid.cli.__main__:main'],
    },
    long_description="Grid AI Command Line Interface",
    long_description_content_type="text/x-rst",
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    #  $ setup.py publish support.
    cmdclass={
        'pypi': UploadCommandPyPi,
        'gcp': UploadCommandGCP,
        'install': Install
    },
)
