#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
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

import logging
import operator

from diffoscope.config import Config

try:
    import tlsh
except ImportError:  # noqa
    tlsh = None

logger = logging.getLogger(__name__)


def perform_fuzzy_matching(members1, members2):
    threshold = Config().fuzzy_threshold

    if tlsh is None or threshold == 0:
        return

    # Create local copies because they will be modified by consumer
    members1 = dict(members1)
    members2 = dict(members2)

    seen = set()
    for name1, (file1, _) in members1.items():
        if file1.is_directory() or not file1.fuzzy_hash:
            continue

        comparisons = []
        for name2, (file2, _) in members2.items():
            if name2 in seen or file2.is_directory() or not file2.fuzzy_hash:
                continue
            comparisons.append(
                (tlsh.diff(file1.fuzzy_hash, file2.fuzzy_hash), name2)
            )

        if not comparisons:
            continue

        comparisons.sort(key=operator.itemgetter(0))
        score, name2 = comparisons[0]

        suffix = "will not compare files"
        if score < threshold:
            seen.add(name2)
            yield name1, name2, score
            suffix = "will compare files"

        logger.debug(
            "Fuzzy matching %s %s (score: %d/400): %s",
            name1,
            name2,
            score,
            suffix,
        )
