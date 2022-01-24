"""dynamic setup information for setuptools, also see package.json and setup.cfg"""

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

import json
from pathlib import Path

HERE = Path(__file__).parent

JS = HERE / "src/ipydrawio_widgets/js"

__js__ = json.loads((JS / "package.json").read_text(encoding="utf-8"))

if __name__ == "__main__":
    import setuptools

    setuptools.setup(version=__js__["version"])
