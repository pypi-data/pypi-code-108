#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016-2021 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import re
import json
import pprint
import logging
import collections

from diffoscope.difference import Difference
from diffoscope.tools import python_module_missing

from .utils.file import File

logger = logging.getLogger(__name__)

try:
    import jsondiff
except ImportError:  # noqa
    python_module_missing("jsondiff")
    jsondiff = None


class JSONFile(File):
    DESCRIPTION = "JSON files"
    FILE_TYPE_RE = re.compile(r"^JSON (?:text )?data")  # Requires file 5.35+

    @classmethod
    def recognizes(cls, file):
        if not super().recognizes(file):
            return False

        with open(file.path, "rb") as f:
            try:
                file.parsed = json.loads(
                    f.read().decode("utf-8", errors="ignore"),
                    object_pairs_hook=collections.OrderedDict,
                )
            except ValueError:
                return False

        return True

    def compare_details(self, other, source=None):
        difference = Difference.from_text(
            self.dumps(self),
            self.dumps(other),
            self.path,
            other.path,
            source="Pretty-printed",
        )

        if difference:
            self.compare_with_jsondiff(difference, other)

            return [difference]

        difference = Difference.from_text(
            self.dumps(self, sort_keys=False),
            self.dumps(other, sort_keys=False),
            self.path,
            other.path,
            source="Pretty-printed",
            comment="ordering differences only",
        )

        return [difference]

    def compare_with_jsondiff(self, difference, other):
        if jsondiff is None:
            return

        logger.debug(f"Comparing using jsondiff {jsondiff.__version__}")

        a = getattr(self, "parsed", {})
        b = getattr(other, "parsed", {})

        try:
            diff = {repr(x): repr(y) for x, y in jsondiff.diff(a, b).items()}
        except Exception:
            return

        similarity = jsondiff.similarity(a, b)
        if similarity:
            difference.add_comment(f"Similarity: {similarity}%")

        differences = pprint.pformat(diff, width=100)
        if len(differences) > 512:
            differences = f"{differences[:512]} […]"
        difference.add_comment(f"Differences: {differences}")

    @staticmethod
    def dumps(file, sort_keys=True):
        if not hasattr(file, "parsed"):
            return ""
        return json.dumps(file.parsed, indent=4, sort_keys=sort_keys)
