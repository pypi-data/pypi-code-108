#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2020 Chris Lamb <lamby@debian.org>
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

import heapq
import io
import logging
import subprocess

from . import feeders
from .exc import RequiredToolNotFound
from .diff import diff, reverse_unified_diff, diff_split_lines
from .excludes import operation_excluded

logger = logging.getLogger(__name__)


class Difference:
    def __init__(
        self,
        path1,
        path2,
        source=None,
        comment=None,
        has_internal_linenos=False,
        details=None,
        visuals=None,
        unified_diff=None,
    ):
        self._unified_diff = unified_diff

        self._comments = []
        if comment:
            if type(comment) is list:
                self._comments.extend(comment)
            else:
                self._comments.append(comment)

        # Allow to override declared file paths, useful when comparing
        # tempfiles
        if source:
            if type(source) is list:
                self._source1, self._source2 = source
            else:
                self._source1 = source
                self._source2 = source
        else:
            self._source1 = path1
            self._source2 = path2

        # Ensure renderable types
        if not isinstance(self._source1, str):
            raise TypeError("path1/source[0] is not a string")
        if not isinstance(self._source2, str):
            raise TypeError("path2/source[1] is not a string")

        # Whether the unified_diff already contains line numbers inside itself
        self._has_internal_linenos = has_internal_linenos
        self._details = details or []
        self._visuals = visuals or []
        self._size_cache = None

    def __repr__(self):
        return (
            f"<Difference {self._source1} -- {self._source2} {self._details}>"
        )

    def map_lines(self, f_diff, f_comment):
        unified_diff = self.unified_diff
        if unified_diff is not None:
            unified_diff = "".join(map(f_diff, diff_split_lines(unified_diff)))
        return self.__class__(
            self.source1,
            self.source2,
            comment=[
                "".join(map(f_comment, diff_split_lines(comment)))
                for comment in self._comments
            ],
            has_internal_linenos=self.has_internal_linenos,
            details=self._details[:],
            visuals=self._visuals[:],
            unified_diff=unified_diff,
        )

    def fmap(self, f):
        return f(
            self.__class__(
                self.source1,
                self.source2,
                comment=self._comments[:],
                has_internal_linenos=self.has_internal_linenos,
                details=[d.fmap(f) for d in self._details],
                visuals=self._visuals[:],
                unified_diff=self.unified_diff,
            )
        )

    def _reverse_self(self):
        # assumes we're being called from get_reverse()
        if self._visuals:
            raise NotImplementedError(
                "_reverse_self on VisualDifference is not yet implemented"
            )
        unified_diff = (
            reverse_unified_diff(self.unified_diff)
            if self.unified_diff is not None
            else None
        )
        return self.__class__(
            self.source2,
            self.source1,
            comment=self._comments,  # already copied by fmap in get_reverse
            has_internal_linenos=self.has_internal_linenos,
            details=self._details,  # already reversed by fmap in get_reverse, no need to copy
            unified_diff=unified_diff,
        )

    def get_reverse(self):
        logger.debug("Reverse orig %s %s", self.source1, self.source2)
        return self.fmap(Difference._reverse_self)

    def equals(self, other):
        return self == other or (
            self.unified_diff == other.unified_diff
            and self.source1 == other.source1
            and self.source2 == other.source2
            and self._comments == other._comments
            and self.has_internal_linenos == other.has_internal_linenos
            and all(x.equals(y) for x, y in zip(self._details, other._details))
            and all(x.equals(y) for x, y in zip(self._visuals, other._visuals))
        )

    def size(self):
        if self._size_cache is None:
            self._size_cache = sum(
                d.size_self() for d in self.traverse_depth()
            )
        return self._size_cache

    def size_self(self):
        """Size, excluding children."""
        return (
            (len(self.unified_diff) if self.unified_diff else 0)
            + (len(self.source1) if self.source1 else 0)
            + (len(self.source2) if self.source2 else 0)
            + sum(map(len, self.comments))
            + sum(v.size() for v in self._visuals)
        )

    def has_visible_children(self):
        """
        Whether there are visible children.

        Useful for e.g. choosing whether to display [+]/[-] controls.
        """
        return (
            self._unified_diff is not None
            or self._comments
            or self._details
            or self._visuals
        )

    def traverse_depth(self, depth=-1):
        yield self
        if depth != 0:
            for d in self._details:
                yield from d.traverse_depth(depth - 1)

    def traverse_breadth(self, queue=None):
        queue = queue if queue is not None else [self]
        if queue:
            top = queue.pop(0)
            yield top
            queue.extend(top._details)
            yield from self.traverse_breadth(queue)

    def traverse_heapq(self, scorer, yield_score=False, queue=None):
        """Traverse the difference tree using a priority queue, where each node
        is scored according to a user-supplied function, and nodes with smaller
        scores are traversed first (after they have been added to the queue).

        The function `scorer` takes two arguments, a node to score and the
        score of its parent node (or None if there is no parent). It should
        return the score of the input node.
        """
        queue = queue if queue is not None else [(scorer(self, None), self)]
        while queue:
            val, top = heapq.heappop(queue)
            prune_descendants = yield ((top, val) if yield_score else top)
            if not prune_descendants:
                for d in top._details:
                    heapq.heappush(queue, (scorer(d, val), d))

    @staticmethod
    def from_feeder(
        feeder1, feeder2, path1, path2, source=None, comment=None, **kwargs
    ):
        try:
            unified_diff = diff(feeder1, feeder2)
            if not unified_diff:
                return None
            return Difference(
                path1,
                path2,
                source,
                comment,
                unified_diff=unified_diff,
                **kwargs,
            )
        except RequiredToolNotFound:
            difference = Difference(path1, path2, source)
            difference.add_comment("diff is not available")
            if comment:
                difference.add_comment(comment)
            return difference

    @staticmethod
    def from_text(content1, content2, *args, **kwargs):
        """
        Works for both bytes and str objects.
        """
        # Avoid spawning diff if buffers have same contents
        if content1 == content2:
            return None
        return Difference.from_feeder(
            feeders.from_text(content1),
            feeders.from_text(content2),
            *args,
            **kwargs,
        )

    @staticmethod
    def from_raw_readers(file1, file2, *args, **kwargs):
        return Difference.from_feeder(
            feeders.from_raw_reader(file1),
            feeders.from_raw_reader(file2),
            *args,
            **kwargs,
        )

    @staticmethod
    def from_text_readers(file1, file2, *args, **kwargs):
        return Difference.from_feeder(
            feeders.from_text_reader(file1),
            feeders.from_text_reader(file2),
            *args,
            **kwargs,
        )

    @staticmethod
    def from_operation(klass, path1, path2, *args, **kwargs):
        return Difference.from_operation_exc(
            klass, path1, path2, *args, **kwargs
        )[0]

    @staticmethod
    def from_operation_exc(klass, path1, path2, *args, **kwargs):
        operation_args = kwargs.pop("operation_args", [])
        ignore_returncodes = kwargs.pop("ignore_returncodes", ())

        def operation_and_feeder(path):
            operation = None
            if path == "/dev/null":
                feeder = feeders.empty()
            else:
                operation = klass(path, *operation_args)
                feeder = feeders.from_operation(operation)
                if operation_excluded(operation.full_name()):
                    return None, None, True
                operation.start()
            return feeder, operation, False

        feeder1, operation1, excluded1 = operation_and_feeder(path1)
        feeder2, operation2, excluded2 = operation_and_feeder(path2)
        if not feeder1 or not feeder2:
            assert excluded1 or excluded2
            return None, True

        if "source" not in kwargs:
            source_op = operation1 or operation2
            kwargs["source"] = source_op.full_name(truncate=120)

        try:
            short = kwargs.pop("short", False)
            # If the outputs are expected to be short, store them in memory
            # and do a direct comparison, and only spawn diff if needed.
            if short:
                memfile1 = io.BytesIO()
                feeder1(memfile1)
                memfile2 = io.BytesIO()
                feeder2(memfile2)
                bytes1 = memfile1.getbuffer().tobytes()
                bytes2 = memfile2.getbuffer().tobytes()
                # Check if the buffers are the same before invoking diff
                if bytes1 == bytes2:
                    return None, True
                difference = Difference.from_text(
                    bytes1, bytes2, path1, path2, *args, **kwargs
                )
            else:
                difference = Difference.from_feeder(
                    feeder1, feeder2, path1, path2, *args, **kwargs
                )
        except subprocess.CalledProcessError as exc:
            if exc.returncode in ignore_returncodes:
                return None, False
            raise

        if not difference:
            return None, False

        if (
            operation1
            and operation1.error_string
            and operation2
            and operation2.error_string
            and operation1.full_name() == operation2.full_name()
        ):
            # Output is the same, so don't repeat the output
            difference.add_comment(
                "error from `{}`:".format(operation1.full_name())
            )
            difference.add_comment(operation1.error_string)
        else:
            if operation1 and operation1.error_string:
                difference.add_comment(
                    "error from `{}` (a):".format(operation1.full_name())
                )
                difference.add_comment(operation1.error_string)
            if operation2 and operation2.error_string:
                difference.add_comment(
                    "error from `{}` (b):".format(operation2.full_name())
                )
                difference.add_comment(operation2.error_string)

        return difference, False

    @property
    def comment(self):
        return "\n".join(self._comments)

    @property
    def comments(self):
        return self._comments

    def add_comment(self, comment):
        for line in comment.splitlines():
            self._comments.append(line)
        self._size_cache = None

    @property
    def source1(self):
        return self._source1

    @property
    def source2(self):
        return self._source2

    @property
    def unified_diff(self):
        return self._unified_diff

    @unified_diff.setter
    def unified_diff(self, value):
        self._unified_diff = value

    @property
    def has_internal_linenos(self):
        return self._has_internal_linenos

    @property
    def details(self):
        return self._details

    @property
    def visuals(self):
        return self._visuals

    def add_details(self, differences):
        if len([d for d in differences if type(d) is not Difference]) > 0:
            raise TypeError("'differences' must contains Difference objects'")
        self._details.extend(differences)
        self._size_cache = None

    def add_visuals(self, visuals):
        if any([type(v) is not VisualDifference for v in visuals]):
            raise TypeError("'visuals' must contain VisualDifference objects'")
        self._visuals.extend(visuals)
        self._size_cache = None

    def has_ordering_differences_only(self):
        """
        Check if difference is only in line ordering.
        """

        if not self.unified_diff:
            return False

        diff_lines = self.unified_diff.splitlines()

        added_lines = [line[1:] for line in diff_lines if line.startswith("+")]
        removed_lines = [
            line[1:] for line in diff_lines if line.startswith("-")
        ]

        # Faster check: does number of lines match?
        if len(added_lines) != len(removed_lines):
            return False

        if added_lines == removed_lines:
            return False

        return sorted(added_lines) == sorted(removed_lines)

    def check_for_ordering_differences(self):
        if self.has_ordering_differences_only():
            self.add_comment("Ordering differences only")


class VisualDifference:
    def __init__(self, data_type, content, source):
        self._data_type = data_type
        self._content = content
        self._source = source

    @property
    def data_type(self):
        return self._data_type

    @property
    def content(self):
        return self._content

    @property
    def source(self):
        return self._source

    def size(self):
        return len(self.data_type) + len(self.content) + len(self.source)

    def equals(self, other):
        return self == other or (
            self._data_type == other._data_type
            and self._content == other._content
            and self._source == other._source
        )
