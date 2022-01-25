"""Copyright Alpine Intuition Sàrl team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re

from setuptools import find_packages, setup

with open("archipel_utils/__init__.py") as f:
    version = re.search(r"\d.\d.\d", f.read()).group(0)  # type: ignore

setup(
    name="archipel-utils",
    version=version,
    license="Apache License 2.0",
    description="Small utils for Archipel plateform",
    author="alpineintuition",
    author_email="contact@alpineintuition.ch",
    url="https://github.com/alpineintuition/archipel-utils",
    download_url=f"https://github.com/alpineintuition/archipel-utils/archive/v{version}.tar.gz",
    keywords=["archipel-utils", "archipel"],
    install_requires=[
        "msgpack>=1.0",
        "numpy>=1.21",
        "pytest>=6.2",
        "pytest-cov>=2.11",
        "pytest-mock>=3.5",
    ],
    packages=find_packages(),
)
