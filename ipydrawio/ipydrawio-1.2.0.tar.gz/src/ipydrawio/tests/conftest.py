"""test customizations"""

# Copyright 2022 ipydrawio contributors
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

import re
from pathlib import Path

import nbformat
import pytest

from ..constants import IPYNB_METADATA, MIMETYPE

HERE = Path(__file__).parent
FIXTURES = HERE / "fixtures"
EMPTY_DIO = FIXTURES / "empty.dio"
EMPTY_IPYNB = FIXTURES / "empty.ipynb"
FIXTURE_NAMES = [
    "dio",
    "dio.svg",
    "ipynb",
    # derived
    "no-meta.ipynb",
    "no-output.ipynb",
    "mxgraph.xml",
]


@pytest.fixture(params=FIXTURE_NAMES)
def an_empty_dio_file(request: str, tmp_path) -> Path:
    fixture = FIXTURES / f"empty.{request.param}"

    if not fixture.exists() and "ipynb" in request.param:
        nb_node = nbformat.reads(
            EMPTY_IPYNB.read_text(encoding="utf-8"), nbformat.NO_CONVERT
        )

        if "no-meta" in request.param:
            nb_node["metadata"].pop(IPYNB_METADATA, None)

        if "no-output" in request.param:
            for cell in nb_node["cells"]:
                for output in cell.get("outputs", []):
                    output.get("data", {}).pop(MIMETYPE, None)
                    output.get("metadata", {}).pop(MIMETYPE, None)

        derived = tmp_path / f"fixtures/empty.{request.param}"
        derived.parent.mkdir(exist_ok=True)
        derived.write_text(nbformat.writes(nb_node), encoding="utf-8")
        return derived

    if not fixture.exists() and "mxgraph" in request.param:
        derived = tmp_path / f"fixtures/empty.{request.param}"
        derived.parent.mkdir(exist_ok=True)
        in_xml = EMPTY_DIO.read_text(encoding="utf-8")
        out_xml = re.sub(r".*(<mxGraphModel(.*)/mxGraphModel>).*", r"\1", in_xml)
        derived.write_text(out_xml, encoding="utf-8")
        return derived

    return fixture
