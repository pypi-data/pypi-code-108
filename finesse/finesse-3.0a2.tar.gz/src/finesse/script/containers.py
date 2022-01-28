"""Token and production containers for use in the tokenizer and parser."""

# Enable postponed type hint evaluation (PEP 563). This can be removed once Finesse
# requires at least Python 3.9.
from __future__ import annotations

from typing import Any, Union, List
from functools import total_ordering
import re
import abc
from dataclasses import dataclass
from ..env import INDENT


@total_ordering
@dataclass(eq=True, frozen=True)
class KatCoordinate:
    """Kat script file coordinate supporting comparison operations."""

    lineno: int
    index: int

    def __lt__(self, other):
        if self.lineno != other.lineno:
            return self.lineno < other.lineno
        return self.index < other.index

    def __add__(self, other):
        return KatCoordinate(self.lineno + other.lineno, self.index + other.index)

    def __sub__(self, other):
        return KatCoordinate(self.lineno - other.lineno, self.index - other.index)

    def __str__(self):
        return f"({self.lineno}, {self.index})"

    def compact(self):
        """Compact coordinate representation.

        Returns
        -------
        :class:`str`
            Compact coordinates.
        """
        return f"{self.lineno}:{self.index}"


@dataclass(eq=True, frozen=True)
class KatBounds:
    """Kat script start and stop bounds.

    This represents a block of text in a kat script file.
    """

    start: KatCoordinate
    stop: KatCoordinate

    def __post_init__(self):
        if self.start > self.stop:
            raise ValueError(f"start ({self.start}) must be < stop ({self.stop})")

    def __str__(self):
        return f"{self.start}:{self.stop}".replace(" ", "")

    def isempty(self):
        """Whether the contents contained within the bounds is empty.

        Returns
        -------
        :class:`bool`
            True if empty, False otherwise.
        """
        return self.start == self.stop

    def lexpand(self, newstart):
        """Expand start boundary.

        Parameters
        ----------
        newstart : :class:`.KatCoordinate`
            The new start coordinate.

        Returns
        -------
        :class:`.KatBounds`
            The expanded bounds.

        Raises
        ------
        ValueError
            If `newstart` is not <= current start coordinate.
        """
        if self.start.lineno < newstart.lineno:
            raise ValueError(
                f"New start {newstart} is not <= current start {self.start}"
            )
        return self.__class__(newstart, self.stop)

    def rexpand(self, newstop):
        """Expand stop boundary.

        Parameters
        ----------
        newstop : :class:`.KatCoordinate`
            The new stop coordinate.

        Returns
        -------
        :class:`.KatBounds`
            The expanded bounds.

        Raises
        ------
        ValueError
            If `newstop` is not >= current stop coordinate.
        """
        if self.stop.lineno > newstop.lineno:
            raise ValueError(f"New stop {newstop} is not >= current stop {self.stop}")
        return self.__class__(self.start, newstop)

    def lcontract(self, newstart):
        """Contract start boundary.

        Parameters
        ----------
        newstart : :class:`.KatCoordinate`
            The new start coordinate.

        Returns
        -------
        :class:`.KatBounds`
            The contracted bounds.

        Raises
        ------
        ValueError
            If `newstart` is not >= current start coordinate.
        """
        if self.start.lineno > newstart.lineno:
            raise ValueError(
                f"New start {newstart} is not >= current start {self.start}"
            )
        return self.__class__(newstart, self.stop)

    def rcontract(self, newstop):
        """Contract stop boundary.

        Parameters
        ----------
        newstop : :class:`.KatCoordinate`
            The new stop coordinate.

        Returns
        -------
        :class:`.KatBounds`
            The contracted bounds.

        Raises
        ------
        ValueError
            If `newstop` is not <= current stop coordinate.
        """
        if self.stop.lineno < newstop.lineno:
            raise ValueError(f"New stop {newstop} is not <= current stop {self.stop}")
        return self.__class__(self.start, newstop)


class Addressable(metaclass=abc.ABCMeta):
    """Mixin defining interface to retrieve strings containing script lines."""

    def script(self, bounds=None):
        """Get the script in the interval [start, stop) defined by `bounds`.

        Lines between `start` and `stop` with no tokens are yielded as empty lines. Gaps
        between the columns spanned by tokens on the same line are yielded as spaces.

        Parameters
        ----------
        bounds : :class:`.KatBounds`, optional
            Bounds within which to retrieve script. Defaults to the whole script.

        Returns
        -------
        :class:`str`
            The script.
        """
        if bounds is None:
            bounds = self.bounds
        return self._script(bounds)

    def script_lines(self, bounds):
        """The script within `bounds` by line.

        Parameters
        ----------
        bounds : :class:`.KatBounds`
            The bounds to retrieve script between.

        Returns
        -------
        :class:`list`
            Lines within `bounds`. Where `bounds` starts or stops mid-way through a
            line, only the part of the line that falls within `bounds` is contained in
            the corresponding line.
        """
        return self.script(bounds).splitlines()

    @abc.abstractmethod
    def _script(self, bounds):
        raise NotImplementedError

    @property
    def start(self):
        """Start coordinate.

        :getter: The start :class:`.KatCoordinate`.
        """
        return self.bounds.start

    @property
    def stop(self):
        """Stop coordinate.

        :getter: The stop :class:`.KatCoordinate`.
        """
        return self.bounds.stop

    @property
    @abc.abstractmethod
    def bounds(self):
        """Container bounds.

        :getter: :class:`.KatBounds` for this container.
        """
        raise NotImplementedError


class TokenContainer(Addressable, metaclass=abc.ABCMeta):
    """Container with concrete token instances."""

    @property
    @abc.abstractmethod
    def tokens(self):
        """Tokens contained in the container.

        :getter: :class:`list` of :class:`.KatToken` objects within this container.
        """
        return []

    @property
    def sorted_tokens(self):
        """Tokens contained in the container, in ascending coordinate order.

        :getter: sorted :class:`list` of :class:`.KatToken` objects within this
                 container.
        """
        return sorted(self.tokens, key=lambda item: item.start)

    @property
    def first_token(self):
        """First container token by coordinate.

        :getter: first :class:`.KatToken` within this container.
        """
        return self.sorted_tokens[0]

    @property
    def last_token(self):
        """Last container token by coordinate.

        :getter: last :class:`.KatToken` within this container.
        """
        return self.sorted_tokens[-1]

    @property
    def bounds(self):
        return KatBounds(self.first_token.start, self.last_token.stop)

    def _script(self, bounds):
        script = ""

        for token in self.sorted_tokens:
            # The code here can't cope with tokens spanning lines. All tokens created by
            # the tokenizer are single-lined, including newline characters (just like
            # Python's tokenizer).
            assert token.start.lineno == token.stop.lineno

            # Tokens are in order, so we can do some simple exit checks.
            if token.stop < bounds.start:
                continue
            if token.start >= bounds.stop:
                break

            value = token.display_value

            if (
                token.lineno == bounds.start.lineno
                and token.start.index < bounds.start.index
            ):
                startindex = bounds.start.index - token.start.index
            else:
                startindex = 0
            if (
                token.lineno == bounds.stop.lineno
                and token.stop.index >= bounds.stop.index
            ):
                stopindex = bounds.stop.index - token.start.index
            else:
                stopindex = None

            script += value[startindex:stopindex]

        return script


@dataclass(eq=True)
class KatFile(Addressable):
    """Container with kat script lines (no concrete tokens)."""

    text: str

    @property
    def _text_lines(self):
        if not self.text:
            # Empty line.
            return [""]
        lines = self.text.splitlines(True)
        if self.text.endswith("\n"):
            # Add a last empty line because splitlines() ignores it, but it affects the
            # file's stop position. See
            # https://docs.python.org/3/library/stdtypes.html#str.splitlines.
            lines.append("")
        return lines

    def _script(self, bounds):
        script = ""
        for lineno, line in enumerate(self._text_lines, start=1):
            if lineno < bounds.start.lineno:
                continue
            if lineno > bounds.stop.lineno:
                break

            if lineno == bounds.start.lineno:
                # Convert column to list index.
                startindex = max(bounds.start.index - 1, 0)
            else:
                startindex = 0
            if lineno == bounds.stop.lineno:
                # Convert column to list index.
                stopindex = max(bounds.stop.index - 1, 0)
            else:
                stopindex = None

            script += line[startindex:stopindex]

        return script

    @property
    def bounds(self):
        start = KatCoordinate(1, 1)
        stop = KatCoordinate(len(self._text_lines), 1 + len(self._text_lines[-1]))
        return KatBounds(start, stop)

    def add(self, string):
        """Add string to end of file.

        Parameters
        ----------
        string : :class:`str`
            The string to add to the end of the file.
        """
        self.text += string


@dataclass(eq=True)
class KatMetaToken(TokenContainer):
    """A token that may not map to a real token.

    Meta tokens are employed by :class:`.KatTokenizer` when converting whitespace and
    newline tokens (provided by :class:`.KatRawTokenizer`) used as delimiters into
    DELIMITER. The use of a single meta token for DELIMITER in this case simplifies the
    parser rules.

    By definition, the value of a meta token does not matter so the class doesn't
    support having one. Similarly, to help prevent bugs, an exception is raised if the
    token is attempted to be displayed.
    """

    lineno: int
    start_index: int
    stop_index: int
    type: str

    @property
    def tokens(self):
        return super().tokens + [self]

    @property
    def bounds(self):
        return KatBounds(
            KatCoordinate(self.lineno, self.start_index),
            KatCoordinate(self.lineno, self.stop_index),
        )


@dataclass(eq=True)
class KatToken(KatMetaToken):
    """A real token with the corresponding text's location, type and value."""

    raw_value: Any

    @property
    def value(self):
        return self.raw_value

    @property
    def display_value(self):
        return self.raw_value

    @classmethod
    def with_new_type(cls, tok, new_type):
        """Convert token to a different type.

        Parameters
        ----------
        tok : :class:`.KatToken`
            The token to convert.

        new_type : :class:`str`
            The new token type.

        Returns
        -------
        :class:`.KatToken`
            The kat token, copied from `tok`, with type `new_type`.
        """
        return cls(
            lineno=tok.lineno,
            start_index=tok.start_index,
            stop_index=tok.stop_index,
            type=new_type,
            raw_value=tok.raw_value,
        )

    def to_new_position(self, start):
        """Copy token, updating its start (and stop) position.

        Parameters
        ----------
        start : :class:`KatCoordinate`
            The token's new start position.

        Returns
        -------
        :class:`.KatToken`
            New copy of `self`, with updated start position.
        """
        length = self.stop_index - self.start_index

        return self.__class__(
            lineno=start.lineno,
            start_index=start.index,
            stop_index=start.index + length,
            type=self.type,
            raw_value=self.raw_value,
        )

    def to_meta(self):
        """Convert token to a meta token.

        Returns
        -------
        :class:`.KatMetaToken`
            The current token, as a meta token.
        """
        return KatMetaToken(self.lineno, self.start_index, self.stop_index, self.type)

    def __str__(self):
        return repr(self.display_value)


@dataclass(eq=True)
class BaseCustomToken(KatToken, metaclass=abc.ABCMeta):
    """A custom token."""

    def __post_init__(self):
        # Ensure the value is valid. Ensures errors in determining the token's value get
        # thrown on instantiation rather than when later read.
        try:
            self.value
        except ValueError as e:
            # NOTE: the actual syntax that's incorrect will be added by the tokenizer
            # when it catches this.
            raise SyntaxError("syntax error") from e


@dataclass(eq=True)
class KatWhitespaceToken(BaseCustomToken):
    """A whitespace token."""

    @property
    def display_value(self):
        # Convert tabs into the same number of spaces assumed by the tokenizer. This
        # avoids issues when displaying script inside error messaages.
        return self.raw_value.replace("\t", "~" * len(INDENT))


@dataclass(eq=True)
class KatBooleanToken(BaseCustomToken):
    """A boolean token."""

    @property
    def value(self):
        return self.raw_value == "True" or self.raw_value == "true"


@dataclass(eq=True)
class KatReferenceToken(BaseCustomToken):
    """A reference token."""

    @property
    def value(self):
        return self.raw_value.lstrip("&")


@dataclass(eq=True)
class KatNumberToken(BaseCustomToken):
    """A number token."""

    SI_NUMBER_PATTERN = re.compile(r".*[pnumkMGT]$")

    @property
    def value(self):
        value = self.raw_value

        if "j" in value:
            return complex(value)

        if self.SI_NUMBER_PATTERN.match(value):
            value = value.replace("p", "e-12")
            value = value.replace("n", "e-9")
            value = value.replace("u", "e-6")
            value = value.replace("m", "e-3")
            value = value.replace("k", "e3")
            value = value.replace("M", "e6")
            value = value.replace("G", "e9")
            value = value.replace("T", "e12")

        try:
            return int(value)
        except ValueError:
            return float(value)


@dataclass(eq=True)
class KatStringToken(BaseCustomToken):
    """A string token."""

    @property
    def value(self):
        value = self.raw_value

        # Get rid of escape characters.
        value = value.replace("\\n", "\n")
        value = value.replace("\\r", "\r")
        value = value.replace("\\", "")
        # Get rid of the quotes.
        value = value[1:-1]

        return value


@dataclass(eq=True)
class KatNoneToken(BaseCustomToken):
    """A null token."""

    @property
    def value(self):
        return None


@dataclass(eq=True)
class ArgumentContainer(TokenContainer, metaclass=abc.ABCMeta):
    """Mixin for containers that contain arguments."""

    arguments: List[TokenContainer]

    @property
    def tokens(self):
        tokens = super().tokens
        for argument in self.arguments:
            tokens.extend(argument.tokens)
        return tokens


@dataclass(eq=True)
class ExtraTokenContainer(TokenContainer, metaclass=abc.ABCMeta):
    """Mixin for containers that contain extra tokens."""

    extra: List[KatToken]

    @property
    def tokens(self):
        return super().tokens + self.extra


@dataclass(eq=True)
class KatScript(ArgumentContainer, ExtraTokenContainer, TokenContainer):
    """Represents a kat script."""


@dataclass(eq=True)
class KatScriptItem(TokenContainer, metaclass=abc.ABCMeta):
    """Represents a top level kat script item."""

    directive: KatToken

    @property
    @abc.abstractmethod
    def node_name(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unique_name_token(self):
        raise NotImplementedError

    @property
    def tokens(self):
        return super().tokens + [self.directive]

    @abc.abstractmethod
    def missing_argument_meta_token(self):
        """A meta token at one position after that of the last argument token.

        This is used to create error markers pointing to the location of missing
        parameters.
        """
        raise NotImplementedError


@dataclass(eq=True)
class KatElement(ArgumentContainer, ExtraTokenContainer, KatScriptItem):
    """Represents a parsed element statement and any corresponding arguments."""

    name: KatToken

    @property
    def tokens(self):
        return super().tokens + [self.name]

    @property
    def node_name(self):
        return self.name.display_value

    @property
    def unique_name_token(self):
        return self.name

    def missing_argument_meta_token(self):
        if not self.arguments:
            # Put the meta token one space after the name.
            token = self.sorted_tokens[-1].to_meta()
        else:
            token = self.arguments[-1].last_token.to_meta()
        token.start_index = token.stop_index + 1
        token.stop_index = token.start_index + 1
        return token

    def __str__(self):
        name = f"{self.directive.display_value} {self.name.display_value}"
        args = f"{', '.join([str(arg) for arg in self.arguments])}"
        return f"{name} ( {args} )"


@dataclass(eq=True)
class KatFunction(ArgumentContainer, ExtraTokenContainer, KatScriptItem):
    """Represents a parsed kat function statement and any corresponding arguments."""

    @property
    def name(self):
        """The token that represents the function name.

        This is used by the error handler for invalid keyword arguments, for example.
        """
        return self.directive

    @property
    def node_name(self):
        return f"{self.directive.display_value}[{self.directive.start.compact()}]"

    @property
    def unique_name_token(self):
        return self.directive

    def missing_argument_meta_token(self):
        if not self.arguments:
            # Put the meta token at the last token (which should be the closing ")").
            token = self.sorted_tokens[-1].to_meta()
        else:
            token = self.arguments[-1].last_token.to_meta()
            token.start_index = token.stop_index
        token.stop_index = token.start_index + 1
        return token

    def __str__(self):
        return f"{self.directive}({', '.join([str(argument) for argument in self.arguments])})"


@dataclass(eq=True)
class KatKwarg(ExtraTokenContainer, TokenContainer):
    """Represents a kat argument containing a key, value and '='."""

    key: KatToken
    value: Union[KatToken, KatFunction, KatExpression, KatGroupedExpression, KatArray]

    @property
    def tokens(self):
        tokens = super().tokens
        if self.key:
            tokens.append(self.key)
        tokens.extend(self.value.tokens)
        return tokens

    @property
    def is_positional(self):
        return self.key is None

    @property
    def is_keyword(self):
        return self.key is not None

    def __str__(self):
        if self.is_keyword:
            return f"{self.key}={self.value}"
        return f"{self.value}"


@dataclass(eq=True)
class KatExpression(ArgumentContainer, ExtraTokenContainer, TokenContainer):
    """Represents a kat script expression."""

    operator: KatToken

    @property
    def tokens(self):
        return super().tokens + [self.operator]

    @property
    def lhs(self):
        return self.arguments[0]

    @property
    def rhs(self):
        return self.arguments[1]

    def __str__(self):
        return f"{self.lhs}{self.operator}{self.rhs}"


@dataclass(eq=True)
class KatGroupedExpression(ArgumentContainer, ExtraTokenContainer, TokenContainer):
    """Represents a kat script expression group, i.e. `(<expression>)`."""

    @property
    def expression(self):
        return self.arguments[0]

    def __str__(self):
        return f"({self.expression})"


@dataclass(eq=True)
class KatArray(ArgumentContainer, ExtraTokenContainer, TokenContainer):
    """Represents a kat script array."""

    def __str__(self):
        return f"[{', '.join([str(argument) for argument in self.arguments])}]"


@dataclass(eq=True)
class KatNumericalArray(KatArray):
    """Represents a kat script numerical array."""

    def __str__(self):
        return f"ndarray([{', '.join([str(argument) for argument in self.arguments])}])"

    @classmethod
    def from_array(cls, array):
        """Convert array to numerical array."""
        return cls(arguments=array.arguments, extra=array.extra)
