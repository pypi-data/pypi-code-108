# Pybfc - BranFuck compiler write in python
# Copyright (C) 2022 - Awiteb <awiteb@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import re

KEYWORD = ["pybfc", "BF", "branfuck", "branfuck_compiler", "branfuck_interprater"]

with open("./README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with open("./requirements.txt", encoding="utf-8") as require_file:
    requires = [require.strip() for require in require_file]

with open("./pybfc/version.py", "r", encoding="utf-8") as f:
    version = re.search(
        r'^version\s*=\s*"(.*)".*$', f.read(), flags=re.MULTILINE
    ).group(1)

setup(
    name="pybfc",
    version=version,
    description="BranFuck compiler write in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Awiteb",
    author_email="Awiteb@hotmail.com",
    url="https://github.com/TheAwiteb/pybfc",
    project_urls={
        "Bug Reports": "https://github.com/TheAwiteb/pybfc/issues/new?assignees=&labels=bug&template=bug.md",
        "Source Code": "https://github.com/TheAwiteb/pybfc",
    },
    packages=find_packages(),
    license="AGPLv3",
    keywords=KEYWORD,
    entry_points={"console_scripts": ["pybfc = pybfc.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requires,
)
