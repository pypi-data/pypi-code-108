import re
import itertools
from collections import deque
from typing import List, Tuple


def _sprit(s, delim):
    return [x.lstrip().rstrip() for x in s.split(delim)]


def _parse_list(lst_str):
    lst_str = lst_str.lstrip().rstrip()
    assert lst_str[0] == "[" and lst_str[-1] == "]"
    contents = _sprit(lst_str[1:-1], ",")
    return contents


_kwarg_pattern = re.compile("([^(=|,|\(|\))]+)=(\[[^(=|\(|\))]+\])")
_exec_line_pattern = re.compile("^\[\[.*\],\[.*\]\]$")
_directive_pattern = re.compile("^[a-zA-Z]+\(.*\)")


def outer_split(contents, sep=","):
    """
    Used to parse expressions of the form
    (A, B, C, ...)
    where A, B, C as expressions can themselves contain brackets and commas within these brackets.

    The point is that we do not want to split at commas within brackets, just at commas that are on the
    outermost layer.
    """

    OPENING_BRACKETS = {"(": ")", "{": "}", "[": "]"}

    CLOSING_BRACKETS = {value: key for key, value in OPENING_BRACKETS.items()}

    brackets = deque()  # for pushing open brackets onto a stack
    buf = []  # for buffering all characters of one outer split element
    split_result = []
    for char in contents:
        if len(brackets) == 0:
            if char == sep:
                split_result.append("".join(buf).lstrip().rstrip())
                buf = []
            else:
                assert (
                    char not in CLOSING_BRACKETS
                ), "Found %s but there is no %s left to close." % (
                    char,
                    CLOSING_BRACKETS[char],
                )
                buf.append(char)
                if char in OPENING_BRACKETS:
                    brackets.append(char)
        else:
            buf.append(char)
            if char in OPENING_BRACKETS:
                brackets.append(char)
            elif char in CLOSING_BRACKETS:
                opener = brackets.pop()
                expected_closer = OPENING_BRACKETS[opener]
                assert (
                    char == expected_closer
                ), "Expected %s to be closed with %s, but found %s instead." % (
                    opener,
                    expected_closer,
                    char,
                )

    assert (
        len(brackets) == 0
    ), "Unexpected end of expression, not all brackets (%s) closed in:\n%s." % (
        ",".join(b for b in brackets),
        contents,
    )

    split_result.append("".join(buf).lstrip().rstrip())
    return split_result


class Expression:
    def __init__(self):
        self.needs_compilation = True

    def resolve(self, *args, **kwargs) -> Tuple[List[str], bool]:
        raise NotImplementedError()

    def _match(self, line: str) -> bool:
        raise NotImplementedError()

    def match(self, line) -> bool:
        if self._match(line):
            self._line = line
            return True
        else:
            return False

    @property
    def line(self) -> str:
        return self._line


class ExecLine(Expression):
    def __init__(self):
        self.needs_compilation = False

    def _match(self, line: str) -> bool:
        match = _exec_line_pattern.match(line)
        if match:
            self._line = line
            return True
        else:
            return False

    def resolve(self, line: str) -> Tuple[List[str], bool]:
        return [self.line], False

    @property
    def line(self) -> str:
        return self._line


class Directive(Expression):
    def __init__(self, identifier):
        self.identifier = identifier
        self.pattern = re.compile("^%s\((.*)\)$" % self.identifier)

    def _match(self, line: str) -> bool:
        match = self.pattern.match(line)
        if match == None:
            return False
        else:
            self.contents = match.group(1)
            self.contents = outer_split(self.contents)
            return True

    def resolve(self):
        raise NotImplementedError()

    def initial_parse(self, exec_line):

        kwargs = [_kwarg_pattern.match(itm) for itm in self.contents]

        args = [self.contents[i] for i, kwarg in enumerate(kwargs) if kwarg is None]
        assert len(args) >= 1

        kwargs = [(itm.group(1), itm.group(2)) for itm in kwargs if itm is not None]
        kwargs = {key.lstrip().rstrip(): _parse_list(val) for key, val in kwargs}
        return args, kwargs


class Zip(Directive):
    def __init__(self):
        super().__init__("ZIP")

    def resolve(self, exec_line: str) -> Tuple[List[str], bool]:
        args, kwargs = self.initial_parse(exec_line)

        assert len(args) > 0

        lengths = [len(lst) for lst in kwargs.values()]
        assert len(set(lengths)) == 1, "All ZIP-argument lists must be of same length"
        lst_len = lengths[0]

        lines = []
        filling = lambda idx, formatters: {
            fs: kwargs[fs][idx] if fs in kwargs else "{%s}" % fs for fs in formatters
        }
        for arg in args:
            formatters = set(re.findall("\{([a-zA-Z]+)\}", arg))
            lines.extend(
                [arg.format(**filling(idx, formatters)) for idx in range(lst_len)]
            )

        del self.contents
        return lines, True


class Prod(Directive):
    def __init__(self):
        super().__init__("PROD")

    def resolve(self, exec_line: str) -> Tuple[List[str], bool]:
        args, kwargs = self.initial_parse(exec_line)

        assert len(args) > 0

        kwargs = [[(name, val) for val in kwargs[name]] for name in kwargs]

        lines = []
        for arg in args:
            lines.extend(
                [
                    arg.format(**{name: val for name, val in comb})
                    for comb in itertools.product(*kwargs)
                ]
            )

        del self.contents
        return lines, True


class InlineComment(Expression):
    def __init__(self, flags: List[str] = ["#", "//"]):
        super().__init__()
        self.flags = flags

    def _match(self, line) -> bool:
        for flag in self.flags:
            idx = line.find(flag)
            match = idx != -1
            if match:
                self.matched_flag = flag
                self.matched_idx = idx
                return True
        return False

    def resolve(self, line: str) -> Tuple[List[str], bool]:
        if self.matched_idx == 0:
            return [], False
        else:
            start = self.matched_idx
            return [self.line[:start].rstrip()], True


class _Directives(list):
    def __init__(self):
        super().__init__([InlineComment(), ExecLine(), Prod(), Zip()])

    def resolve(self, exec_line: str) -> Tuple[List[str], bool]:
        for i, expr in enumerate(self):
            if expr.match(exec_line):
                assert not any(
                    [other_expr.match(exec_line) for other_expr in self[(i + 1) :]]
                )
                return expr.resolve(exec_line)
        # no match
        return [exec_line], False


ExecDirectives = _Directives()

if __name__ == "__main__":
    test = "// ZIP([[./test.py, -alpha {a}, -beta {b}],[-ca test.py]], [[./foo.py, -alpha {a}, -beta {b}],[-ca foo.py]], a=[0.05, 0.01, 0.1], b=[100, 500, 1000])"
    IC = InlineComment()
    assert IC.match(test)
    lines, _ = IC.resolve(test)
    print("IC", test, lines)

    test = "ZIP([[./test.py, -alpha {a}, -beta {b}],[-ca test.py]], [[./foo.py, -alpha {a}, -beta {b}],[-ca foo.py]], a=[0.05, 0.01, 0.1], b=[100, 500, 1000])"
    ZIP = Zip()
    assert ZIP.match(test)
    lines, _ = ZIP.resolve(test)
    [print("ZIP", line) for line in lines]

    test = "PROD([[./test.py, -alpha {a}, -beta {b}],[-ca test.py]], a=[0.05, 0.01, 0.1], b=[100, 500])"
    PROD = Prod()
    assert PROD.match(test)
    lines, _ = PROD.resolve(test)
    [print("PROD", line) for line in lines]

    test = "ZIP([[./test.py, -a {a}, -b {b}],[-ca test.py]], [[./foo.py, -a {a}, -b {b}],[-ca foo.py]], a=[0.05, 0.01], b=[100, 500])"
    test = "ZIP(PROD([[./test.py, -a {a}, -b {b} --seed {seed}],[-ca test.py]], [[./foo.py, -a {a}, -b {b}, --seed {seed}],[-ca foo.py]], a=[0.05, 0.01], b=[100, 500]), seed=[0,1,2])"
    assert ZIP.match(test)

    for x in ZIP.contents:
        print(x)

    lines, _ = ZIP.resolve(test)
    [print("ZIP 2", line) for line in lines]

    for i, line in enumerate(lines):
        assert PROD.match(line)
        print("PROD 2.%d" % i)
        prod_lines, _ = PROD.resolve(line)
        [print(pl) for pl in prod_lines]
