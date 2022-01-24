"""constants for ipydrawio"""

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

#: The XML namespace of an SVG
SVG_NS_TAG = "{http://www.w3.org/2000/svg}svg"

#: The root XML tag of a diagram
MX_FILE_TAG = "mxfile"

#: The XML tag of a graph model
MX_GRAPH_TAG = "mxGraphModel"

#: XML extensions we know how to clean
XML_EXTENSIONS = [".drawio", ".dio", ".svg", ".xml"]

#: XML tag attributes to clean from diagram XML
MX_CLEAN_ATTRS = ["host", "modified", "agent", "etag"]

#: XML entities to preserve in diagraml XML
MX_PRESERVE_ENTITIES = dict(
    ATTR_NEWLINE="&#10;",
)

#: Key set in notebook.ipynb#/metadata/
IPYNB_METADATA = "@deathbeds/ipydrawio"

#: Notebook extensions we know how to clean
NOTEBOOK_EXTENSIONS = [".ipynb"]

#: The MIME type used for diagram notebook outputs
MIMETYPE = "application/x-drawio"
