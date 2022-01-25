"""
Common code patterns for use with the `mast` AST matching module.

patterns.py
"""


#-------------------#
# Pattern constants #
#-------------------#

# Common mast pattern for a for loop.
FOR_PATTERN = '''
for _ in _:
    ___
'''
"""
`potluck.mast` pattern for simple `for` loop.
"""


# For loop w/ else (above pattern doesn't match this).
FOR_ELSE_PATTERN = '''
for _ in _:
    ___
else:
    ___
'''
"""
`potluck.mast` pattern for a `for` loop with an `else` clause.
"""


# Both of the above...
ALL_FOR_PATTERNS = [ FOR_PATTERN, FOR_ELSE_PATTERN ]
"""
`potluck.mast` patterns for all `for` loop variants.
"""


# Pattern for a while loop.
WHILE_PATTERN = '''
while _:
    ___
'''
"""
A `potluck.mast` pattern for a simple `while` loop.
"""


# While loop with an else.
WHILE_ELSE_PATTERN = '''
while _:
    ___
else:
    ___
'''
"""
A `potluck.mast` pattern for `while`/`else`.
"""


# Both of the above...
ALL_WHILE_PATTERNS = [ WHILE_PATTERN, WHILE_ELSE_PATTERN ]
"""
`potluck.mast` patterns for all `while` loop variants.
"""


# List comprehensions
SIMPLE_COMPREHENSION_PATTERN = '''
[ _ for _ in _ ]
'''
"""
A `potluck.mast` pattern for a single for loop comprehension without a filter.
"""


FILTER_COMPREHENSION_PATTERN = '''
[ _ for _ in _ if _ ]
'''
"""
A `potluck.mast` pattern for a single for loop comprehension with a filter.
"""


DOUBLE_COMPREHENSION_PATTERN = '''
[ _ for _ in _ for _ in _ ]
'''
"""
A `potluck.mast` pattern for a double for loop comprehension without a filter.
"""


DOUBLE_FILTER_COMPREHENSION_PATTERN = '''
[ _ for _ in _ for _ in _ if _ ]
'''
"""
A `potluck.mast` pattern for a double for loop comprehension with a filter.
"""


TRIPLE_COMPREHENSION_PATTERN = '''
[ _ for _ in _ for _ in _ for _ in _ ]
'''
"""
A `potluck.mast` pattern for a triple for loop comprehension without a filter.
"""


TRIPLE_FILTER_COMPREHENSION_PATTERN = '''
[ _ for _ in _ for _ in _ for _ in _ if _ ]
'''
"""
A `potluck.mast` pattern for a triple for loop comprehension with a filter.
"""


ALL_REASONABLE_COMPREHENSION_PATTERNS = [
    SIMPLE_COMPREHENSION_PATTERN,
    FILTER_COMPREHENSION_PATTERN,
    DOUBLE_COMPREHENSION_PATTERN,
    DOUBLE_FILTER_COMPREHENSION_PATTERN,
    TRIPLE_COMPREHENSION_PATTERN,
    TRIPLE_FILTER_COMPREHENSION_PATTERN,
]
"""
`potluck.mast` patterns for single, double, and triple list comprehensions
with and without filtering.

Note: does not include dictionary comprehensions (TODO: that?)

We will simply hope that students do not use quadruple comprehensions...
"""


# Combination patterns for loops and loops + comprehensions
ALL_FOR_AND_WHILE_LOOP_PATTERNS = ALL_FOR_PATTERNS + ALL_WHILE_PATTERNS
"""
`potluck.mast` patterns for all while/for loop variants.
"""
ALL_LOOP_AND_COMPREHENSION_PATTERNS = (
    ALL_FOR_AND_WHILE_LOOP_PATTERNS
  + ALL_REASONABLE_COMPREHENSION_PATTERNS
)
"""
`potluck.mast` patterns for all reasonable loop/comprehension types,
although highly-nested comprehensions are not included.
"""
ALL_SINGLE_LOOP_AND_COMPREHENSION_PATTERNS = (
    ALL_FOR_AND_WHILE_LOOP_PATTERNS + [
        SIMPLE_COMPREHENSION_PATTERN,
        FILTER_COMPREHENSION_PATTERN
    ]
)
"""
`potluck.mast` patterns for all loop/comprehension patterns that are
single loops.
"""


IF_PATTERN = '''
if _:
    ___
else:
    ___
'''
"""
Common mast pattern for an if statement (matches even ifs that don't have
an else, we think; note this also matches elifs, which Python treats as
nested ifs).
"""


ALL_DEF_PATTERNS = [
    "def _f_(___):\n  ___",
    "def _f_(___, ___=_):\n  ___",
    "def _f_(___=_):\n  ___",
]
"""
Patterns for function definitions (without keyword variables, with both,
and with only keyword variables). These patterns bind 'f' as the name of
the function that's defined.
"""


FUNCTION_CALL_PATTERNS = [
    "_f_(___)",
    "_f_(___, ___=_)",
    "_f_(___=_)",
]
"""
Patterns for function calls. These bind 'f' as the function (possibly a
function expression).
"""


METHOD_CALL_PATTERNS = [
    "_._f_(___)",
    "_._f_(___, ___=_)",
    "_._f_(___=_)",
]
"""
Patterns for method calls specifically. Note that the
`FUNCTION_CALL_PATTERNS` will find method calls too, but will bind 'f' as
the entire object + method expression, whereas these patterns will bind
'f' as the method name (multiple bindings will result from chained method
calls).
"""


#-----------------------------#
# Pattern-producing functions #
#-----------------------------#

def function_def_patterns(fn_name, params_pattern=None):
    """
    Returns a list of mast pattern strings for definitions of functions
    with the given name (or list of names). If an args pattern is given,
    it should be a string containing mast code that goes between the
    parentheses of a function definition. For example:

    - `"_, _"`
        There must be exactly two arguments.
    - `"___, x=3"`
        There may be any number of positional arguments, and there must
        be a single keyword argument named 'x' with default value 3.
    - `"one, two"`
        There must be exactly two arguments and they must be named 'one'
        and 'two'.

    The params_pattern may also be a list of strings and any of those
    alternatives will be accepted, or it may be an integer, in which case
    that many blank slots will be inserted.
    """
    patterns = []

    if isinstance(fn_name, str):
        names = [fn_name]
    else:
        names = list(fn_name)

    if isinstance(params_pattern, int):
        params_pattern = ', '.join('_' for _ in range(params_pattern))

    for name in names:
        if params_pattern is None:
            # kwargs not allowed by default
            patterns.append("def {}(___):\n  ___".format(name))
        else:
            if isinstance(params_pattern, str):
                patterns.append(
                    "def {}({}):\n  ___".format(name, params_pattern)
                )
            elif not isinstance(params_pattern, (list, tuple)):
                raise TypeError(
                    "params_pattern must be either a string or a"
                    " sequence of strings."
                )
            else:
                patterns.extend(
                    [
                        "def {}({}):\n  ___".format(name, params_pat)
                        for params_pat in params_pattern
                    ]
                )

    return patterns


def function_call_patterns(fn_name, args_pattern, is_method=False):
    """
    Works like function_def_patterns, but produces patterns for calls to
    a function rather than definitions of it. In this context the args
    spec is specifying arguments given to the function rather than what
    parameters it defines.

    If is_method is true, the patterns generated use '_.' to ensure that
    the function call is as a method of some object.
    """
    patterns = []
    if isinstance(fn_name, str):
        names = [fn_name]
    else:
        names = list(fn_name)

    if isinstance(args_pattern, int):
        args_pattern = ', '.join('_' for _ in range(args_pattern))

    for name in names:
        if args_pattern is None:
            if is_method:
                patterns.extend(
                    [
                        "_.{}(___)".format(name),
                        "_.{}(___,___=_)".format(name),
                        "_.{}(___=_)".format(name),
                    ]
                )
            else:
                patterns.extend(
                    [
                        "{}(___)".format(name),
                        "{}(___,___=_)".format(name),
                        "{}(___=_)".format(name),
                    ]
                )
        else:
            if isinstance(args_pattern, str):
                if is_method:
                    patterns.append("_.{}({})".format(name, args_pattern))
                else:
                    patterns.append("{}({})".format(name, args_pattern))
            elif not isinstance(args_pattern, (list, tuple)):
                raise TypeError(
                    "args_pattern must be either a string or a sequence of "
                  + "strings."
                )
            else:
                if is_method:
                    patterns.extend(
                        [
                            "_.{}({})".format(name, args_pat)
                            for args_pat in args_pattern
                        ]
                    )
                else:
                    patterns.extend(
                        [
                            "{}({})".format(name, args_pat)
                            for args_pat in args_pattern
                        ]
                    )

    return patterns
