"""Kat parser to convert tokens to productions.

This is a recursive descent parser, providing unlimited lookahead capabilities to allow
arbitrary context-free grammars to be parsed. The implementation of memoization makes it
a *packrat* parser which runs in linear time at the expense of potentially unlimited
memory use. In practice memory use is limited by the simplicity of typical kat scripts
(e.g. expressions don't tend to have many subexpressions).

This is inspired by Python's PEG parser, used as of 3.9. Some introductory information
can be found in `this series of blog posts
<https://medium.com/@gvanrossum_83706/peg-parsing-series-de5d41b2ed60>`__.

Sean Leavey <sean.leavey@ligo.org>
"""

# NOTE: do not run black on this file!

import logging
from io import StringIO
from .containers import (
    KatScript,
    KatElement,
    KatFunction,
    KatKwarg,
    KatExpression,
    KatGroupedExpression,
    KatArray,
    KatNumericalArray
)
from .tokenizer import KatTokenizer
from .memoize import memoize, memoize_left_rec
from .exceptions import KatSyntaxError, KatMissingAfterDirective

LOGGER = logging.getLogger(__name__)


class KatParser:
    """Kat script parser.

    This uses so-called *packrat* parsing to reduce, via productions, tokens yielded
    from a token stream generated from an input file or string to
    :class:`.KatScriptItem` objects containing the associated :class:`tokens
    <.KatToken>`.
    """

    def __init__(self):
        self.tokens = None
        self.pos = None
        self.memos = None
        self._tokenizer = None
        self._token_stream = None

    @property
    def script(self):
        return self._tokenizer.script

    def parse(self, string):
        """Parse the contents of `string`.

        Parameters
        ----------
        string : :class:`str`
            The string to parse kat script from.

        Returns
        -------
        :class:`.KatScript`
            The parsed kat script.
        """
        return self.parse_file(StringIO(string))

    def parse_file(self, fobj):
        """Parse the contents of the specified file.

        Parameters
        ----------
        fobj : :class:`io.FileIO`
            The file object to parse kat script from. This should be opened in text
            mode.

        Returns
        -------
        :class:`.KatScript`
            The parsed kat script.
        """
        # Reset parser state.
        self.tokens = []
        self.pos = 0
        self.memos = {}
        self._log_stack = []

        # Perform parse.
        self._tokenizer = KatTokenizer()
        self._token_stream = self._tokenizer.tokenize_file(fobj)

        if (script := self.expect_production("start")) is not None:
            return script

        # There was an error.
        self._diagnose_error()

    def _diagnose_error(self):
        if not self.tokens:
            error_token = self.peek_token()
        else:
            error_token = self.tokens[-1]

        raise KatSyntaxError("syntax error", self.script, error_token)

    def mark(self):
        return self.pos

    def reset(self, pos):
        if pos == self.pos:
            return
        self.pos = pos

    def get_token(self):
        token = self.peek_token()
        self.pos += 1
        return token

    def peek_token(self):
        if self.pos == len(self.tokens):
            self.tokens.append(next(self._token_stream))
        return self.tokens[self.pos]

    def positive_lookahead(self, token_type):
        pos = self.mark()
        token = self.peek_token()
        self.reset(pos)
        return token.type == token_type

    def negative_lookahead(self, token_type):
        return not self.positive_lookahead(token_type)

    def maybe_whitespace(self, multiline, whitespace):
        """Expect zero or more whitespace if enabled, else return []."""
        if not whitespace:
            return []
        return self.loop("empty", False, multiline)

    def maybe_trailing_comma(self, multiline):
        pos = self.mark()
        if (
            True
            and (empty := self.loop("empty", False, multiline)) is not None
            and (COMMA := self.expect_token("COMMA")) is not None
        ):
            return [*empty, COMMA]
        self.reset(pos)
        return []

    @memoize
    def expect_token(self, arg):
        self._log_stack.append(arg)
        path = "->".join(self._log_stack)
        # path = arg
        LOGGER.debug(f"{path}?")
        token = self.peek_token()

        if token.type == arg:
            LOGGER.debug(f"{path} = {token!r}!")
            result = self.get_token()
            self._log_stack.pop()
            return result

        LOGGER.debug(f"{arg} not found")
        self._log_stack.pop()

    def expect_production(self, production, *args, **kwargs):
        self._log_stack.append(production)
        path = "->".join(self._log_stack)
        # path = production
        LOGGER.debug(f"{path}?")

        result = getattr(self, production)(*args, **kwargs)

        if result is not None:
            LOGGER.debug(f"{path} = {result!r}!")
            self._log_stack.pop()
            return result

        LOGGER.debug(f"{production} not found")

        self._log_stack.pop()

    def loop(self, production, nonempty, *args, **kwargs):
        mark = self.mark()
        nodes = []
        while (node := self.expect_production(production, *args, **kwargs)) is not None:
            nodes.append(node)
        if len(nodes) >= nonempty:
            return nodes
        self.reset(mark)

    def start(self):
        pos = self.mark()

        if (
            True
            and (script_lines := self.loop("script_line", True)) is not None
            and self.expect_token("ENDMARKER") is not None
        ):
            statements = []
            extra = []
            for statement, line_extra in script_lines:
                if statement:
                    statements.append(statement)
                extra.extend(line_extra)

            return KatScript(arguments=statements, extra=extra)

        self.reset(pos)

        # Empty file.
        if self.expect_token("ENDMARKER") is not None:
            return KatScript(arguments=[], extra=[])

        self.reset(pos)

    @memoize
    def script_line(self):
        pos = self.mark()

        # script_line -> script_line_empty* statement script_line_empty* NEWLINE
        if (
            True
            and (script_line_empty1 := self.loop("script_line_empty", False)) is not None
            and (statement := self.expect_production("statement")) is not None
            and (script_line_empty2 := self.loop("script_line_empty", False)) is not None
            and (NEWLINE := self.expect_token("NEWLINE")) is not None
        ):
            extra = [*script_line_empty1, *script_line_empty2]
            # Ignore implicit newlines, which are metatokens.
            if hasattr(NEWLINE, "value"):
                extra.append(NEWLINE)
            return statement, extra

        self.reset(pos)

        # script_line -> script_line_empty* NEWLINE
        if (
            True
            and (script_line_empty := self.loop("script_line_empty", False)) is not None
            and (NEWLINE := self.expect_token("NEWLINE")) is not None
        ):
            extra = [*script_line_empty]
            if hasattr(NEWLINE, "value"):
                # Newline is a real token.
                extra.append(NEWLINE)
            return None, extra

        self.reset(pos)

        if (error := self.expect_production("invalid_script_line")) is not None:
            raise error

    @memoize
    def script_line_empty(self):
        pos = self.mark()

        # script_line_empty -> WHITESPACE
        if (WHITESPACE := self.expect_token("WHITESPACE")) is not None:
            return WHITESPACE

        self.reset(pos)

        # script_line_empty -> COMMENT
        if (COMMENT := self.expect_token("COMMENT")) is not None:
            return COMMENT

        self.reset(pos)

    @memoize
    def empty(self, multiline):
        pos = self.mark()

        # empty -> WHITESPACE
        if (WHITESPACE := self.expect_token("WHITESPACE")) is not None:
            return WHITESPACE

        self.reset(pos)

        if multiline:
            # empty -> COMMENT
            if (COMMENT := self.expect_token("COMMENT")) is not None:
                return COMMENT

            self.reset(pos)

            # empty -> NEWLINE
            if (NEWLINE := self.expect_token("NEWLINE")) is not None:
                return NEWLINE

            self.reset(pos)

    @memoize
    def statement(self):
        pos = self.mark()

        # statement -> element
        if (element := self.expect_production("element")) is not None:
            return element

        self.reset(pos)

        # statement -> function
        if (function := self.expect_production("function", True)) is not None:
            return function

        self.reset(pos)

    @memoize
    def element(self):
        pos = self.mark()

        # element -> NAME WHITESPACE NAME WHITESPACE element_params
        if (
            True
            and (DIRECTIVE := self.expect_token("NAME")) is not None
            and (WHITESPACE1 := self.expect_token("WHITESPACE")) is not None
            and (NAME := self.expect_token("NAME")) is not None
            and (WHITESPACE2 := self.expect_token("WHITESPACE")) is not None
            and (element_params := self.expect_production("element_params")) is not None
        ):
            arguments, params_extra = element_params
            return KatElement(
                directive=DIRECTIVE,
                name=NAME,
                arguments=arguments,
                extra=[WHITESPACE1, WHITESPACE2, *params_extra]
            )

        self.reset(pos)

        # element -> NAME WHITESPACE NAME
        if (
            True
            and (DIRECTIVE := self.expect_token("NAME")) is not None
            and (WHITESPACE := self.expect_token("WHITESPACE")) is not None
            and (NAME := self.expect_token("NAME")) is not None
        ):
            return KatElement(
                directive=DIRECTIVE, name=NAME, arguments=[], extra=[WHITESPACE]
            )

        self.reset(pos)

    @memoize
    def element_params(self):
        pos = self.mark()

        # element_params -> element_value_list empty+ element_key_value_list
        if (
            True
            and (element_value_list := self.expect_production("element_value_list")) is not None
            and (empty := self.loop("empty", True, False)) is not None
            and (element_key_value_list := self.expect_production("element_key_value_list")) is not None
        ):
            values, value_extra = element_value_list
            key_values, key_value_extra = element_key_value_list
            return ([*values, *key_values], [*value_extra, *empty, *key_value_extra])

        self.reset(pos)

        # element_params -> element_value_list
        if (element_value_list := self.expect_production("element_value_list")) is not None:
            return element_value_list

        self.reset(pos)

        # element_params -> element_key_value_list
        if (element_key_value_list := self.expect_production("element_key_value_list")) is not None:
            return element_key_value_list

        self.reset(pos)

    @memoize
    def element_value_list(self):
        pos = self.mark()

        # element_value_list -> positional_value empty+ element_value_list
        if (
            True
            and (positional_value := self.expect_production("positional_value", False, False)) is not None
            and (empty := self.loop("empty", True, False)) is not None
            and (element_value_list := self.expect_production("element_value_list")) is not None
        ):
            values, value_extra = element_value_list
            return ([positional_value, *values], [*empty, *value_extra])

        self.reset(pos)

        # element_value_list -> positional_value
        if (positional_value := self.expect_production("positional_value", False, False)) is not None:
            return [positional_value], []

        self.reset(pos)

    @memoize_left_rec
    def element_key_value_list(self):
        pos = self.mark()

        # element_key_value_list -> element_key_value_list empty+ element_key_value_list
        if (
            True
            and (element_key_value_list1 := self.expect_production("element_key_value_list")) is not None
            and (empty := self.loop("empty", True, False)) is not None
            and (element_key_value_list2 := self.expect_production("element_key_value_list")) is not None
        ):
            key_values1, key_value_extra1 = element_key_value_list1
            key_values2, key_value_extra2 = element_key_value_list2
            return (
                [*key_values1, *key_values2],
                [*key_value_extra1, *empty, *key_value_extra2]
            )

        self.reset(pos)

        # element_key_value_list -> key_value
        if (key_value := self.expect_production("key_value", False, False)) is not None:
            return [key_value], []

        self.reset(pos)

    @memoize
    def function(self, multiline):
        pos = self.mark()

        # function -> NAME '(' empty* function_params empty* ')'
        if (
            True
            and (FUNCTION := self.expect_token("NAME")) is not None
            and (LPAREN := self.expect_token("LPAREN")) is not None
            and (empty1 := self.loop("empty", False, multiline)) is not None
            and (function_params := self.expect_production("function_params", multiline)) is not None
            and (empty2 := self.loop("empty", False, multiline)) is not None
            and (RPAREN := self.expect_token("RPAREN")) is not None
        ):
            args, extra = function_params
            return KatFunction(
                directive=FUNCTION,
                arguments=args,
                extra=[LPAREN, *empty1, *extra, *empty2, RPAREN]
            )

        self.reset(pos)

        # function -> NAME '(' empty* ')'
        if (
            True
            and (FUNCTION := self.expect_token("NAME")) is not None
            and (LPAREN := self.expect_token("LPAREN")) is not None
            and (empty := self.loop("empty", False, multiline)) is not None
            and (RPAREN := self.expect_token("RPAREN")) is not None
        ):
            return KatFunction(
                directive=FUNCTION, arguments=[], extra=[LPAREN, *empty, RPAREN]
            )

        self.reset(pos)

    @memoize
    def function_params(self, multiline):
        pos = self.mark()

        # function_params -> function_value_list empty* ',' empty* function_key_value_list (empty* ',')?
        if (
            True
            and (function_value_list := self.expect_production("function_value_list", multiline)) is not None
            and (empty1 := self.loop("empty", False, multiline)) is not None
            and (COMMA := self.expect_token("COMMA")) is not None
            and (empty2 := self.loop("empty", False, multiline)) is not None
            and (function_key_value_list := self.expect_production("function_key_value_list", multiline)) is not None
            and (trailing_comma := self.maybe_trailing_comma(multiline)) is not None
        ):
            values, value_extra = function_value_list
            key_values, key_value_extra = function_key_value_list
            return (
                [*values, *key_values],
                [
                    *value_extra,
                    *empty1,
                    COMMA,
                    *empty2,
                    *key_value_extra,
                    *trailing_comma
                ]
            )

        self.reset(pos)

        # function_params -> function_value_list (empty* ',')?
        if (
            True
            and (function_value_list := self.expect_production("function_value_list", multiline)) is not None
            and (trailing_comma := self.maybe_trailing_comma(multiline)) is not None
        ):
            values, value_extra = function_value_list
            return values, [*value_extra, *trailing_comma]

        self.reset(pos)

        # function_params -> function_key_value_list (empty* ',')?
        if (
            True
            and (function_key_value_list := self.expect_production("function_key_value_list", multiline)) is not None
            and (trailing_comma := self.maybe_trailing_comma(multiline)) is not None
        ):
            key_values, key_value_extra = function_key_value_list
            return key_values, [*key_value_extra, *trailing_comma]

        self.reset(pos)

    @memoize
    def function_value_list(self, multiline):
        pos = self.mark()

        # function_value_list -> positional_value empty* ',' empty* function_value_list
        if (
            True
            and (positional_value := self.expect_production("positional_value", multiline, True)) is not None
            and (empty1 := self.loop("empty", False, multiline)) is not None
            and (COMMA1 := self.expect_token("COMMA")) is not None
            and (empty2 := self.loop("empty", False, multiline)) is not None
            and (function_value_list := self.expect_production("function_value_list", multiline)) is not None
        ):
            values, value_extra = function_value_list
            return (
                [positional_value, *values],
                [*empty1, COMMA1, *empty2, *value_extra]
            )

        self.reset(pos)

        # function_value_list -> positional_value
        if (positional_value := self.expect_production("positional_value", multiline, True)) is not None:
            return [positional_value], []

        self.reset(pos)

    @memoize_left_rec
    def function_key_value_list(self, multiline):
        pos = self.mark()

        # function_key_value_list -> function_key_value_list empty* ',' empty* function_key_value_list
        if (
            True
            and (function_key_value_list1 := self.expect_production("function_key_value_list", multiline)) is not None
            and (empty1 := self.loop("empty", False, multiline)) is not None
            and (COMMA := self.expect_token("COMMA")) is not None
            and (empty2 := self.loop("empty", False, multiline)) is not None
            and (function_key_value_list2 := self.expect_production("function_key_value_list", multiline)) is not None
        ):
            key_values1, key_value_extra1 = function_key_value_list1
            key_values2, key_value_extra2 = function_key_value_list2
            return (
                [*key_values1, *key_values2],
                [*key_value_extra1, *empty1, COMMA, *empty2, *key_value_extra2]
            )

        self.reset(pos)

        # function_key_value_list -> key_value
        if (key_value := self.expect_production("key_value", multiline, True)) is not None:
            return [key_value], []

        self.reset(pos)

    @memoize
    def positional_value(self, multiline, whitespace):
        pos = self.mark()

        # Don't match values followed by '=', which are kwarg keys.
        if (
            True
            and (value := self.expect_production("value", multiline, whitespace)) is not None
            and self.negative_lookahead("EQUALS")
        ):
            return value

        self.reset(pos)

    @memoize
    def value(self, multiline, whitespace):
        pos = self.mark()

        # value -> array
        # Should be above `expr` so arrays that aren't part of expressions stay as lists
        # instead of get converted into ndarrays.
        if (array := self.expect_production("array", multiline)) is not None:
            return array

        self.reset(pos)

        # value -> expr
        if (expr := self.expect_production("expr", multiline, whitespace)) is not None:
            return expr

        self.reset(pos)

        # value -> function
        if (function := self.expect_production("function", multiline)) is not None:
            return function

        self.reset(pos)

        # value -> NONE / BOOLEAN / STRING
        for token_type in ("NONE", "BOOLEAN", "STRING"):
            if (TOKEN := self.expect_token(token_type)) is not None:
                return TOKEN

            self.reset(pos)

    @memoize
    def key_value(self, multiline, whitespace):
        pos = self.mark()

        # key_value -> NAME '=' value
        if (
            True
            and (NAME := self.expect_token("NAME")) is not None
            and (EQUALS := self.expect_token("EQUALS")) is not None
            and (value := self.expect_production("value", multiline, whitespace))
            is not None
        ):
            return KatKwarg(key=NAME, value=value, extra=[EQUALS])

        self.reset(pos)

        if (
            True
            and (NAME := self.expect_token("NAME")) is not None
            and (EQUALS := self.expect_token("EQUALS")) is not None
            and self.expect_production("value", multiline, whitespace) is None  # !
        ):
            raise KatSyntaxError("missing value", self.script, EQUALS)

        self.reset(pos)

    @memoize_left_rec
    def expr(self, multiline, whitespace):
        pos = self.mark()

        # NOTE: operator precedence is set by defining productions within productions.
        # expr -> expr ( '+' / '-' ) expr1
        for operator in ("PLUS", "MINUS"):
            if (
                True
                and (lhs := self.expect_production("expr", multiline, whitespace)) is not None
                and (whitespace1 := self.maybe_whitespace(multiline, whitespace)) is not None
                and (operator := self.expect_token(operator)) is not None
                and (whitespace2 := self.maybe_whitespace(multiline, whitespace)) is not None
                and (rhs := self.expect_production("expr1", multiline, whitespace)) is not None
            ):
                return KatExpression(
                    operator=operator,
                    arguments=[lhs, rhs],
                    extra=[*whitespace1, *whitespace2]
                )

            self.reset(pos)

        # expr -> expr1
        if (expr1 := self.expect_production("expr1", multiline, whitespace)) is not None:
            return expr1

        self.reset(pos)

    @memoize_left_rec
    def expr1(self, multiline, whitespace):
        """Times, divide and floordivide operators."""
        pos = self.mark()

        # expr1 -> expr1 ( '*' / '/' / '//' ) expr2
        for operator in ("TIMES", "DIVIDE", "FLOORDIVIDE"):
            if (
                True
                and (lhs := self.expect_production("expr1", multiline, whitespace)) is not None
                and (whitespace1 := self.maybe_whitespace(multiline, whitespace)) is not None
                and (operator := self.expect_token(operator)) is not None
                and (whitespace2 := self.maybe_whitespace(multiline, whitespace)) is not None
                and (rhs := self.expect_production("expr2", multiline, whitespace)) is not None
            ):
                return KatExpression(
                    operator=operator,
                    arguments=[lhs, rhs],
                    extra=[*whitespace1, *whitespace2]
                )

            self.reset(pos)

        # expr1 -> expr2
        if (expr2 := self.expect_production("expr2", multiline, whitespace)) is not None:
            return expr2

        self.reset(pos)

    @memoize
    def expr2(self, multiline, whitespace):
        """Unary operators."""
        pos = self.mark()

        # expr2 -> ( '+' / '-' ) expr2
        for unary_operator in ("PLUS", "MINUS"):
            if (
                True
                and (unary_operator := self.expect_token(unary_operator)) is not None
                and (expr2 := self.expect_production("expr2", multiline, whitespace)) is not None
            ):
                return KatFunction(
                    directive=unary_operator, arguments=[expr2], extra=[]
                )

            self.reset(pos)

        # expr2 -> expr3
        if (expr3 := self.expect_production("expr3", multiline, whitespace)) is not None:
            return expr3

        self.reset(pos)

    @memoize
    def expr3(self, multiline, whitespace):
        """Power operator."""
        pos = self.mark()

        # expr3 -> expr4 '**' expr2
        if (
            True
            and (expr4 := self.expect_production("expr4", multiline, whitespace)) is not None
            and (whitespace1 := self.maybe_whitespace(multiline, whitespace)) is not None
            and (power := self.expect_token("POWER")) is not None
            and (whitespace2 := self.maybe_whitespace(multiline, whitespace)) is not None
            and (expr2 := self.expect_production("expr2", multiline, whitespace)) is not None
        ):
            return KatExpression(
                operator=power,
                arguments=[expr4, expr2],
                extra=[*whitespace1, *whitespace2]
            )

        self.reset(pos)

        # expr3 -> expr4
        if (expr4 := self.expect_production("expr4", multiline, whitespace)) is not None:
            return expr4

        self.reset(pos)

    @memoize
    def expr4(self, multiline, whitespace):
        """Parentheses, functions, references, names and numbers.

        Names are allowed here to support keywords and copy-/read-by-value parameters
        like l1.P.
        """
        pos = self.mark()

        # expr4 -> '(' empty* expr empty* ')'
        if (
            True
            and (LPAREN := self.expect_token("LPAREN")) is not None
            and (whitespace1 := self.maybe_whitespace(multiline, True)) is not None
            and (expr := self.expect_production("expr", multiline, True)) is not None
            and (whitespace2 := self.maybe_whitespace(multiline, True)) is not None
            and (RPAREN := self.expect_token("RPAREN")) is not None
        ):
            return KatGroupedExpression(
                arguments=[expr], extra=[LPAREN, *whitespace1, *whitespace2, RPAREN]
            )

        self.reset(pos)

        # expr4 -> function
        if (function := self.expect_production("function", multiline)) is not None:
            return function

        self.reset(pos)

        # expr4 -> array
        if (array := self.expect_production("array", multiline)) is not None:
            LOGGER.debug("converting array expression operand to numerical array")
            return KatNumericalArray.from_array(array)

        self.reset(pos)

        # expr4 -> NUMBER
        # Disallow matching of subsequent numbers, which indicates the tokenizer failed
        # to group two numbers together, and therefore a syntax error (handled later).
        if (
            True
            and (TOKEN := self.expect_token("NUMBER")) is not None
            and self.negative_lookahead("NUMBER")
        ):
            return TOKEN

        self.reset(pos)

        # expr4 -> NAME / REFERENCE
        for token_type in ("NAME", "REFERENCE"):
            if (TOKEN := self.expect_token(token_type)) is not None:
                return TOKEN

            self.reset(pos)

        if (error := self.expect_production("invalid_expr4", multiline)) is not None:
            raise error

        self.reset(pos)

    @memoize
    def array(self, multiline):
        pos = self.mark()

        # array -> '[' empty* array_values empty* ']'
        if (
            True
            and (LBRACKET := self.expect_token("LBRACKET")) is not None
            and (empty1 := self.loop("empty", False, False)) is not None
            and (array_values := self.expect_production("array_values", multiline)) is not None
            and (empty2 := self.loop("empty", False, False)) is not None
            and (RBRACKET := self.expect_token("RBRACKET")) is not None
        ):
            values, value_extra = array_values
            return KatArray(
                arguments=values,
                extra=[LBRACKET, *empty1, *value_extra, *empty2, RBRACKET]
            )

        self.reset(pos)

        # array -> '[' empty* ']'
        if (
            True
            and (LBRACKET := self.expect_token("LBRACKET")) is not None
            and (empty := self.loop("empty", False, False)) is not None
            and (RBRACKET := self.expect_token("RBRACKET")) is not None
        ):
            return KatArray(arguments=[], extra=[LBRACKET, *empty, RBRACKET])

        self.reset(pos)

        if (error := self.expect_production("invalid_array", multiline)) is not None:
            raise error

        self.reset(pos)

    @memoize
    def array_values(self, multiline):
        pos = self.mark()

        # array_values -> array_value empty* ',' empty* array_values (empty* ',')?
        if (
            True
            and (array_value := self.expect_production("array_value", multiline)) is not None
            and (empty1 := self.loop("empty", False, multiline)) is not None
            and (COMMA := self.expect_token("COMMA")) is not None
            and (empty2 := self.loop("empty", False, multiline)) is not None
            and (array_values := self.expect_production("array_values", multiline)) is not None
            and (trailing_comma := self.maybe_trailing_comma(multiline)) is not None
        ):
            values, value_extra = array_values
            return (
                [array_value, *values],
                [*empty1, COMMA, *empty2, *value_extra, *trailing_comma]
            )

        self.reset(pos)

        # array_values -> array_value (empty* ',')?
        if (
            True
            and (array_value := self.expect_production("array_value", multiline)) is not None
            and (trailing_comma := self.maybe_trailing_comma(multiline)) is not None
        ):
            return [array_value], trailing_comma

        self.reset(pos)

    @memoize
    def array_value(self, multiline):
        pos = self.mark()

        # array_value -> array
        # Should be above `expr` so arrays that aren't part of expressions stay as lists
        # instead of get converted into ndarrays.
        if (array := self.expect_production("array", multiline)) is not None:
            return array

        self.reset(pos)

        # array_value -> expr
        if (expr := self.expect_production("expr", multiline, True)) is not None:
            return expr

        self.reset(pos)

        # array_value -> NONE / NUMBER / NAME / BOOLEAN / REFERENCE / STRING
        for token_type in ("NONE", "NUMBER", "NAME", "BOOLEAN", "REFERENCE", "STRING"):
            if (TOKEN := self.expect_token(token_type)) is not None:
                return TOKEN

            self.reset(pos)

    @memoize
    def invalid_script_line(self):
        pos = self.mark()

        # Check for positional arguments specified after keyword arguments in inline
        # statements. Multiline statements are checked elsewhere.
        if (
            True
            and self.loop("script_line_empty", False) is not None
            and self.expect_production("statement") is not None
            and self.loop("script_line_empty", True) is not None
            and (element_value_list := self.expect_production("element_value_list")) is not None
        ):
            values, _ = element_value_list

            return KatSyntaxError(
                "positional argument follows keyword argument", self.script, values[0]
            )

        self.reset(pos)

        # Invalid parameter.
        # This has to be located here because we want the above rules to first check for
        # NEWLINE, to avoid matching valid elements.
        if (
            True
            and self.expect_token("NAME") is not None
            and self.expect_token("WHITESPACE") is not None
            and self.expect_token("NAME") is not None
            and self.expect_token("WHITESPACE") is not None
            and self.expect_production("element_params") is not None
            and (element_params := self.expect_production("element_params")) is not None
        ):
            arguments, _ = element_params
            return KatSyntaxError("syntax error", self.script, arguments[0])

        self.reset(pos)

        # Invalid element (no name) or function (no opening parenthesis).
        if (
            True
            and (DIRECTIVE := self.expect_token("NAME")) is not None
            and self.expect_token("WHITESPACE") is not None
            and self.expect_production("element_params") is not None
            and self.expect_token("NEWLINE") is not None
        ):
            return KatMissingAfterDirective(self.script, DIRECTIVE)

        self.reset(pos)

        # Invalid function: space before parentheses (non-empty parameters).
        if (
            True
            and self.expect_token("NAME") is not None
            and (WHITESPACE := self.expect_token("WHITESPACE")) is not None
            and self.expect_token("LPAREN") is not None
            and self.loop("empty", False, True) is not None
            and self.expect_production("function_params", True) is not None
            and self.loop("empty", False, True) is not None
            and self.expect_token("RPAREN") is not None
        ):
            return KatSyntaxError("space not allowed here", self.script, WHITESPACE)

        self.reset(pos)

        # Invalid function: space before parentheses (empty parameters).
        if (
            True
            and self.expect_token("NAME") is not None
            and (WHITESPACE := self.expect_token("WHITESPACE")) is not None
            and self.expect_token("LPAREN") is not None
            and self.loop("empty", False, True) is not None
            and self.expect_token("RPAREN") is not None
        ):
            return KatSyntaxError("space not allowed here", self.script, WHITESPACE)

        self.reset(pos)

    @memoize
    def invalid_expr4(self, multiline):
        pos = self.mark()

        # Invalid number: two numbers tokenized in a row, indicating a failure to match
        # the number with the tokenizer's regex.
        if (
            True
            and (NUMBER1 := self.expect_token("NUMBER"))
            and (NUMBER2 := self.expect_token("NUMBER"))
        ):
            if isinstance(NUMBER1.value, int) and isinstance(NUMBER2.value, int):
                # Leading zeros (as per the to-number operation of the IBM
                # specification; same behaviour as Python itself, see
                # https://docs.python.org/3/library/decimal.html).
                return KatSyntaxError(
                    "leading zeros in integers are not permitted", self.script, NUMBER1
                )

            # Some other run-together, e.g. `0.1.1`.
            return KatSyntaxError("invalid number syntax", self.script, NUMBER2)

        self.reset(pos)

    @memoize
    def invalid_array(self, multiline):
        pos = self.mark()

        # Invalid: no comma as a delimiter.
        if (
            True
            and self.expect_token("LBRACKET") is not None
            and self.expect_production("array_values", multiline) is not None
            and (empty := self.loop("empty", False, False)) is not None
            and self.expect_production("array_values", multiline) is not None
        ):
            return KatSyntaxError(
                "array values should be delimited by ','", self.script, empty[0]
            )

        self.reset(pos)
