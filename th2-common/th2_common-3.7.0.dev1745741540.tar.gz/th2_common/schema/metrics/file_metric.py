#   Copyright 2021-2021 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import tempfile
from pathlib import Path

from th2_common.schema.metrics.abstract_metric import AbstractMetric


class FileMetric(AbstractMetric):

    def __init__(self, filename: str) -> None:
        self.filename = Path(tempfile.gettempdir()) / filename
        self.filename.unlink(missing_ok=True)

    def on_value_change(self, value: bool):
        if value:
            try:
                self.filename.touch()
            except Exception as e:
                raise OSError(f'Can not create metric file with path = {self.filename}', e)
        else:
            self.filename.unlink(missing_ok=True)
