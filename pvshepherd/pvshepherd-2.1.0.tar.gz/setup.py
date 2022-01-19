#
# Copyright 2021 Picovoice Inc.
#
# You may not use this file except in compliance with the license. A copy of the license is located in the "LICENSE"
# file accompanying this source.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

import os

import setuptools

os.system('git clean -dfx')

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pvshepherd",
    version="2.1.0",
    author="Picovoice",
    author_email="hello@picovoice.ai",
    description="Shepherd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Picovoice/picovoice",
    packages=["pvshepherd"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio :: Speech"
    ],
    entry_points=dict(
        console_scripts=[
            'pvshepherd=pvshepherd.shepherd:main',
        ],
    ),
    python_requires='>=3.6',
    install_requires=["pyserial>=3.5", "matplotlib>=3.3.3", "bitstring>=3.1.7", "Pillow>=8.1.0"]
)
