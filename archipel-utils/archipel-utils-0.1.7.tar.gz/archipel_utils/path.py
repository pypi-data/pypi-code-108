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

import os
from pathlib import Path
from typing import Union


class cd:
    """Context manager for changing the current working directory."""

    def __init__(self, new_path: Union[Path, str]):
        self.new_path = Path(new_path).resolve()

    def __enter__(self):
        """Save current working dir and change to new one."""
        self.saved_path = Path.cwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        """Change current dir to saved one."""
        os.chdir(self.saved_path)
