# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import unicode_literals
import os
from setuptools import setup

# Get information about the version (polling mercurial if possible)
version = '0.4.0'

# When building something else than a release (tag) append the job id to the version.
if os.environ.get('CI_COMMIT_TAG'):
    pass
elif os.environ.get('CI_JOB_ID'):
    version += ".{}".format(os.environ['CI_JOB_ID'])

if __name__ == '__main__':
    # Get the requirements
    with open('requirements.txt', 'r') as fh:
        _requires = fh.read().splitlines()

    # Write information to version.py
    with open('./xnat/version.py', 'w') as f_version:
        f_version.write('version = "{}"\n'.format(version))

    # Set the entry point
    entry_points = {
        "console_scripts": [
            "xnat_cp_project = xnat.scripts.copy_project:main",
            "xnat_data_integrity-check = xnat.scripts.data_integrity_check:main" ,
            "xnat = xnat.client:cli",
        ]
    }

    setup(
        name='xnat',
        version=version,
        author='H.C. Achterberg',
        author_email='hakim.achterberg@gmail.com',
        packages=[str('xnat'), str('xnat.scripts'), str('xnat.client')],
        url='https://gitlab.com/radiology/infrastructure/xnatpy',
        license='Apache 2.0',
        description='An XNAT client that exposes the XNAT REST interface as python objects. Part of the interface is automatically generated based on the servers data model as defined by the xnat schema.',
        long_description=open('README.rst').read(),
        install_requires=_requires,
        entry_points=entry_points,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Healthcare Industry",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: Apache Software License",
            "Natural Language :: English",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
            "Topic :: Scientific/Engineering :: Medical Science Apps.",
            ]

    )
