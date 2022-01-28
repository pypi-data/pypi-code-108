"""Kat script exceptions.

These are special exceptions that add extra context-specific information when errors
occur during parsing or unparsing.
"""

from itertools import chain
from collections import defaultdict
from ..exceptions import FinesseException
from ..utilities import ngettext, option_list, add_linenos
from .containers import KatCoordinate, KatBounds
from .util import index_ranges, scriptsorted


class KatParsingError(FinesseException):
    """An error during the parsing process.

    This handles errors raised by the tokenizer, parser and builder. These are,
    confusingly, collectively referred to as the "parser".
    """


class KatScriptError(KatParsingError):
    """Detailed kat script error.

    Parameters
    ----------
    error : str or :py:class:`Exception`
        The error or error message.

    container : :class:`.Addressable`
        The kat script container, used to show lines before/after error lines if
        requested.

    error_items : sequence of sequences of :class:`.Addressable`
        The error(s) to show. Each item of the topmost sequence should itself be an
        ordered sequence of :class:`.Addressable` objects in increasing order of depth.
        The last item is considered to be where the error occurred, but the start and
        end lines (plus optional buffer) of each of the other items are also shown.

    syntax : :class:`str`, optional
        Syntax suggestion to display to the user.
    """

    # Maximum number of unrelated lines to show before and after show items.
    # TODO: expose this as a user setting somehow.
    MAX_BUFFER_LINES = 1

    def __init__(self, error, container, error_items, syntax=None):
        # Store passed data as attributes in case another exception wants to grab it.
        self.error_msg = error
        self.container = container
        self.error_items = error_items
        self.syntax = syntax
        super().__init__(self.message())

    def _dedup_bounds(self, bounds):
        """Sequence of bounds without overlapping intervals.

        Assumes `bounds` are sorted.
        """
        dedup_bounds = [bounds[0]]

        for current in bounds[1:]:
            previous = dedup_bounds[-1]
            if current.start <= previous.stop:
                dedup_bounds[-1] = previous.rexpand(current.stop)
            else:
                dedup_bounds.append(current)

        return dedup_bounds

    @property
    def _marker_items(self):
        return [items[-1] for items in self.error_items]

    def _marker_bounds(self):
        """Sequence of sorted marker coordinates without overlapping intervals.

        The marker bounds are those of the final item in each item of
        :attr:`.error_items`.
        """
        return self._dedup_bounds(
            scriptsorted(set(item.bounds for item in self._marker_items))
        )

    @property
    def _flattened_error_items(self):
        return chain.from_iterable(self.error_items)

    def _flattened_error_bounds(self):
        return self._dedup_bounds(
            scriptsorted(set([item.bounds for item in self._flattened_error_items]))
        )

    @property
    def error_lines(self):
        lines = set()
        for bounds in self._flattened_error_bounds():
            lines.add(bounds.start.lineno)
            lines.add(bounds.stop.lineno)
        return list(lines)

    def _show_error_bounds(self):
        """Error items with extra lines before and after."""
        show_bounds = []

        for bounds in self._flattened_error_bounds():
            # Some buffer before and after the error, if available in the container.
            start = max(
                KatCoordinate(bounds.start.lineno - self.MAX_BUFFER_LINES, 1),
                self.container.start,
            )
            stop = min(
                KatCoordinate(bounds.stop.lineno + self.MAX_BUFFER_LINES + 1, 0),
                self.container.stop,
            )

            show_bounds.append(bounds.lexpand(start).rexpand(stop))

        return self._dedup_bounds(show_bounds)

    def items_to_linemarkers(self, items):
        linemarkers = defaultdict(lambda: defaultdict(lambda: False))

        for item in items:
            if item.start.lineno != item.stop.lineno:
                raise NotImplementedError(
                    "cannot draw markers on error items spanning multiple lines"
                )

            for index in range(item.start.index, item.stop.index):
                linemarkers[item.start.lineno][index] = True

        return linemarkers

    def rubric(self):
        if not (error_msg := self.error_msg):
            error_msg = ""
        error_msg = str(error_msg)

        lines = self.error_lines

        if len(lines) == 1:
            rubric = f"line {lines[0]}: {error_msg}"
        else:
            rubric = f"lines {option_list(index_ranges(lines), 'and')}: {error_msg}"

        return rubric.strip()

    def message(self):
        msglines = defaultdict(str)
        markers = defaultdict(lambda: defaultdict(lambda: False))

        for lineno, linechunks in self.chunkify().items():
            for bounds, is_error in linechunks:
                if bounds.isempty():
                    # Skip empty bounds, which might otherwise cause an empty extra line
                    # to appear at the end of the error.
                    continue

                # Grab the first line (excluding newline character) since the bounds
                # don't cross lines.
                script = self.container.script_lines(bounds)
                assert len(script) < 2
                if script:
                    msglines[lineno] += script[0]

                if is_error:
                    for index in range(bounds.start.index, bounds.stop.index):
                        markers[lineno][index] = True

        msgwithlines = add_linenos(msglines.keys(), msglines.values())
        lines = []
        if msgwithlines:
            # Work out how wide the line column is. There is +3 for the prefix.
            lcolbuf = len(msgwithlines[0]) - len(next(iter(msglines.values()))) + 3

            # Add arrows on the error lines and markers under the errors.
            lastlineno = None
            for lineno, line in zip(msglines, msgwithlines):
                if lastlineno:
                    diff = lineno - lastlineno
                    if diff > 1:
                        missingmsg = ngettext(
                            diff - 1, "{n} skipped line", "{n} skipped lines"
                        )
                        lines.append(f"{' ' * lcolbuf}*** {missingmsg} ***")

                prefix = "-->" if markers[lineno] else "   "
                lines.append(prefix + line)
                linemarks = ""
                if markers[lineno]:
                    for index in range(1, len(line) + 1):
                        if markers[lineno][index]:
                            linemarks += "^"
                        else:
                            linemarks += " "
                    linemarks = linemarks.rstrip()
                    if linemarks:
                        lines.append(f"{' ' * lcolbuf}{linemarks}")

                lastlineno = lineno

        lines.insert(0, self.rubric())

        if self.syntax:
            lines.append(f"Syntax: {self.syntax}")

        return "\n".join(lines)

    def chunkify(self):
        """Convert the error script into a dict of line numbers to (str, is_error)
        sequences.

        Each (str, is_error) chunk contains a piece of the script specified in
        `error_items`, with the `is_error` flag set depending on whether each error item
        appeared last in a `error_items` sequence, which specifies that it is an error
        as opposed to just useful related code.

        Returns
        -------
        :class:`dict`
            Mapping of line numbers to lists of (:class:`str`, :class:`bool`) tuples
            indicating script chunks and whether they contain an error.
        """
        # Merge the error and marker bounds by starting coordinate, adding an extra flag
        # to remember the type.
        bounds = sorted(
            [(bound, False) for bound in self._show_error_bounds()]
            + [(bound, True) for bound in self._marker_bounds()],
            key=lambda chunk: chunk[0].start,
        )

        merged = [bounds[0]]

        for current_bound, current_flag in bounds[1:]:
            previous_bound, previous_flag = merged[-1]

            # Merge bounds if necessary, with marker intervals taking priority.
            if current_bound == previous_bound:
                # Bounds entirely overlap.
                merged[-1] = (previous_bound, previous_flag or current_flag)
            elif current_bound.start < previous_bound.stop:
                # Bounds overlap.
                inner1 = current_bound.start
                merged[-1] = (previous_bound.rcontract(inner1), previous_flag)

                if current_bound.stop <= previous_bound.stop:
                    inner2 = current_bound.stop
                    merged.append((KatBounds(inner1, inner2), current_flag))
                    merged.append((previous_bound.lcontract(inner2), previous_flag))
                else:
                    merged.append((previous_bound.lcontract(inner1), current_flag))
            else:
                merged.append((current_bound, current_flag))

        linebounds = defaultdict(list)

        # Split any chunks spanning multiple lines.
        for bound, flag in merged:
            if bound.start.lineno == bound.stop.lineno:
                linebounds[bound.start.lineno].append((bound, flag))
            else:
                laststart = bound.start
                for lineno in range(bound.start.lineno, bound.stop.lineno):
                    newstop = KatCoordinate(laststart.lineno + 1, 0)
                    chunk = (KatBounds(laststart, newstop), flag)
                    linebounds[laststart.lineno].append(chunk)
                    laststart = newstop

                # Last line, if not empty.
                last_start = KatCoordinate(bound.stop.lineno, 0)
                last_stop = bound.stop
                if last_start != last_stop:
                    chunk = (KatBounds(last_start, last_stop), flag)
                    linebounds[bound.stop.lineno].append(chunk)

        return linebounds


class KatSyntaxError(KatScriptError):
    """Error with kat syntax."""

    def __init__(self, message, script, token):
        super().__init__(message, script, [[token]])


class KatMissingAfterDirective(KatSyntaxError):
    """Error for when an element name or function '(' is missing."""

    def __init__(self, container, directive):
        self.directive = directive
        super().__init__("missing '(' or element name", container, directive)
