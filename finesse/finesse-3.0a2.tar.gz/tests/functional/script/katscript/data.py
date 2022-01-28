from ..util import (
    BINARY_OPERATORS as _BINOP,
    CONSTANTS as _CONSTANTS,
    EXPRESSION_FUNCTIONS as _FUNCTIONS,
)


# Some macros.
_ADD = _BINOP["+"]
_SUB = _BINOP["-"]
_MUL = _BINOP["*"]
_DIV = _BINOP["/"]
_FLOORDIV = _BINOP["//"]
_POW = _BINOP["**"]
_POS = _FUNCTIONS["pos"]
_NEG = _FUNCTIONS["neg"]
_ABS = _FUNCTIONS["abs"]
_COS = _FUNCTIONS["cos"]
_SIN = _FUNCTIONS["sin"]
_TAN = _FUNCTIONS["tan"]
_ACOS = _FUNCTIONS["arccos"]
_ASIN = _FUNCTIONS["arcsin"]
_ATAN2 = _FUNCTIONS["arctan2"]
_EXP = _FUNCTIONS["exp"]
_SQRT = _FUNCTIONS["sqrt"]
_PI = _CONSTANTS["pi"]

# Constants.
CONSTANTS = tuple(_CONSTANTS.items())

# Unary literals are eagerly evaluated.
UNARY_INTEGERS = (
    ("+0", +0),
    ("-0", +0),
    ("+15", +15),
    ("-15", -15),
    ("+50505", +50505),
    ("-50505", -50505),
)
UNARY_FLOATS = (
    ("+0.", +0.0),
    ("-0.", -0.0),
    ("+0.0", +0.0),
    ("-0.0", -0.0),
    ("+50505.0112", +50505.0112),
    ("-50505.0112", -50505.0112),
    # Scientific.
    ("+0.e7", +0e7),
    ("+0.0e7", +0e7),
    ("-0.e7", -0e7),
    ("-0.0e7", -0e7),
    ("+1.23e7", +1.23e7),
    ("+1.23e+7", +1.23e7),
    ("+1.23e-7", +1.23e-7),
    ("-1.23e7", -1.23e7),
    ("-1.23e+7", -1.23e7),
    ("-1.23e-7", -1.23e-7),
    # Infinities.
    ("+inf", float("+inf")),
    ("-inf", float("-inf")),
)
UNARY_IMAGINARIES = (
    ("+0j", +0j),
    ("+0.j", +0j),
    ("+0.0j", +0j),
    ("-0j", -0j),
    ("-0.j", -0j),
    ("-0.0j", -0j),
    ("+1.32j", +1.32j),
    ("-1.32j", -1.32j),
    # Scientific.
    ("+0e7j", +0e7j),
    ("+0.e7j", +0e7j),
    ("+0.0e7j", +0e7j),
    ("-0e7j", -0e7j),
    ("-0.e7j", -0e7j),
    ("-0.0e7j", -0e7j),
    ("+1.23e7j", +1.23e7j),
    ("+1.23e+7j", +1.23e7j),
    ("+1.23e-7j", +1.23e-7j),
    ("-1.23e7j", -1.23e7j),
    ("-1.23e+7j", -1.23e7j),
    ("-1.23e-7j", -1.23e-7j),
    # Infinities.
    ("+infj", complex("+infj")),
    ("-infj", complex("-infj")),
)
UNARY_COMPLEX = (
    ("+0+0j", +0 + 0j),
    ("+0-0j", +0 - 0j),
    ("+0+1.23j", +0 + 1.23j),
    ("+0-1.23j", +0 - 1.23j),
    ("+0.+0j", +0.0 + 0j),
    ("+0.-0j", +0.0 - 0j),
    ("+0.+1.23j", +0.0 + 1.23j),
    ("+0.-1.23j", +0.0 - 1.23j),
    ("+0.0+0j", +0.0 + 0j),
    ("+0.0-0j", +0.0 - 0j),
    ("+0.0+1.23j", +0.0 + 1.23j),
    ("+0.0-1.23j", +0.0 - 1.23j),
    ("-0+0j", -0 + 0j),
    ("-0-0j", -0 - 0j),
    ("-0+1.23j", -0 + 1.23j),
    ("-0-1.23j", -0 - 1.23j),
    ("-0.+0j", -0.0 + 0j),
    ("-0.-0j", -0.0 - 0j),
    ("-0.+1.23j", -0.0 + 1.23j),
    ("-0.-1.23j", -0.0 - 1.23j),
    ("-0.0+0j", -0.0 + 0j),
    ("-0.0-0j", -0.0 - 0j),
    ("-0.0+1.23j", -0.0 + 1.23j),
    ("-0.0-1.23j", -0.0 - 1.23j),
    ("+1.23+10j", +1.23 + 10j),
    ("+1.23-10j", +1.23 - 10j),
    ("+1.23+1.23j", +1.23 + 1.23j),
    ("+1.23-1.23j", +1.23 - 1.23j),
    ("-1.23+10j", -1.23 + 10j),
    ("-1.23-10j", -1.23 - 10j),
    ("-1.23+1.23j", -1.23 + 1.23j),
    ("-1.23-1.23j", -1.23 - 1.23j),
    # Scientific.
    ("+1.23e7+10j", +1.23e7 + 10j),
    ("+1.23e+7+10j", +1.23e7 + 10j),
    ("+1.23e-7+10j", +1.23e-7 + 10j),
    ("+1.23e7-10j", +1.23e7 - 10j),
    ("+1.23e+7-10j", +1.23e7 - 10j),
    ("+1.23e-7-10j", +1.23e-7 - 10j),
    ("+1.23e7+1.23j", +1.23e7 + 1.23j),
    ("+1.23e+7+1.23j", +1.23e7 + 1.23j),
    ("+1.23e-7+1.23j", +1.23e-7 + 1.23j),
    ("+1.23e7-1.23j", +1.23e7 - 1.23j),
    ("+1.23e+7-1.23j", +1.23e7 - 1.23j),
    ("+1.23e-7-1.23j", +1.23e-7 - 1.23j),
    ("-1.23e7+10j", -1.23e7 + 10j),
    ("-1.23e+7+10j", -1.23e7 + 10j),
    ("-1.23e-7+10j", -1.23e-7 + 10j),
    ("-1.23e7-10j", -1.23e7 - 10j),
    ("-1.23e+7-10j", -1.23e7 - 10j),
    ("-1.23e-7-10j", -1.23e-7 - 10j),
    ("-1.23e7+1.23j", -1.23e7 + 1.23j),
    ("-1.23e+7+1.23j", -1.23e7 + 1.23j),
    ("-1.23e-7+1.23j", -1.23e-7 + 1.23j),
    ("-1.23e7-1.23j", -1.23e7 - 1.23j),
    ("-1.23e+7-1.23j", -1.23e7 - 1.23j),
    ("-1.23e-7-1.23j", -1.23e-7 - 1.23j),
    # Infinities.
    ("+1.23+infj", +1.23 + complex("infj")),
    ("+1.23-infj", -1.23 - complex("infj")),
    ("-1.23+infj", -1.23 + complex("infj")),
    ("-1.23-infj", -1.23 - complex("infj")),
    ("+inf+infj", float("+inf") + complex("infj")),
    ("+inf-infj", float("+inf") - complex("infj")),
    ("-inf+infj", float("-inf") + complex("infj")),
    ("-inf-infj", float("-inf") - complex("infj")),
    # Infinities with scientific.
    ("+1.23e7+infj", +1.23e7 + complex("infj")),
    ("+1.23e7-infj", +1.23e7 - complex("infj")),
    ("+1.23e+7+infj", +1.23e7 + complex("infj")),
    ("+1.23e+7-infj", +1.23e7 + complex("infj")),
    ("+1.23e-7+infj", +1.23e-7 + complex("infj")),
    ("+1.23e-7-infj", +1.23e-7 - complex("infj")),
    ("-1.23e7+infj", -1.23e7 + complex("infj")),
    ("-1.23e7-infj", -1.23e7 - complex("infj")),
    ("-1.23e+7+infj", -1.23e7 + complex("infj")),
    ("-1.23e+7-infj", -1.23e7 - complex("infj")),
    ("-1.23e-7+infj", -1.23e-7 + complex("infj")),
    ("-1.23e-7-infj", -1.23e-7 - complex("infj")),
    ("+inf+1.23e7j", float("+inf") + 1.23e7j),
    ("+inf-1.23e7j", float("+inf") - 1.23e7j),
    ("+inf+1.23e+7j", float("+inf") + 1.23e7j),
    ("+inf-1.23e+7j", float("+inf") - 1.23e7j),
    ("+inf+1.23e-7j", float("+inf") + 1.23e-7j),
    ("+inf-1.23e-7j", float("+inf") - 1.23e-7j),
    ("-inf+1.23e7j", float("-inf") + 1.23e7j),
    ("-inf-1.23e7j", float("-inf") - 1.23e7j),
    ("-inf+1.23e+7j", float("-inf") + 1.23e7j),
    ("-inf-1.23e+7j", float("-inf") - 1.23e7j),
    ("-inf+1.23e-7j", float("-inf") + 1.23e-7j),
    ("-inf-1.23e-7j", float("-inf") - 1.23e-7j),
)


NUMBER_EXPRESSIONS = (
    ("2+3", 2 + 3),
    ("2-3", 2 - 3),
    ("2*3", 2 * 3),
    ("2/3", 2 / 3),
    ("2//3", 2 // 3),
    ("2**3", 2 ** 3),
    ("2+3*4", 2 + 3 * 4),
    ("3*4+2", 3 * 4 + 2),
    ("3+5**2", 3 + 5 ** 2),
    ("3*5**2", 3 * 5 ** 2),
    ("sqrt(1+3)+5", (_SQRT(1 + 3) + 5).eval()),
    ("4**3**2", 4 ** 3 ** 2),
    ("10/5/2", 10 / 5 / 2),
)


COMPLEX_NUMBER_EXPRESSIONS = (
    ("0+0j", 0 + 0j),
    ("0-0j", 0 - 0j),
    ("0+1.23j", 0 + 1.23j),
    ("0-1.23j", 0 - 1.23j),
    ("0.+0j", 0.0 + 0j),
    ("0.-0j", 0.0 - 0j),
    ("0.+1.23j", 0.0 + 1.23j),
    ("0.-1.23j", 0.0 - 1.23j),
    ("0.0+0j", 0.0 + 0j),
    ("0.0-0j", 0.0 - 0j),
    ("0.0+1.23j", 0.0 + 1.23j),
    ("0.0-1.23j", 0.0 - 1.23j),
    ("1.23+10j", 1.23 + 10j),
    ("1.23-10j", 1.23 - 10j),
    ("1.23+1.23j", 1.23 + 1.23j),
    ("1.23-1.23j", 1.23 - 1.23j),
    # Scientific.
    ("1.23e7+10j", 1.23e7 + 10j),
    ("1.23e+7+10j", 1.23e7 + 10j),
    ("1.23e-7+10j", 1.23e-7 + 10j),
    ("1.23e7-10j", 1.23e7 - 10j),
    ("1.23e+7-10j", 1.23e7 - 10j),
    ("1.23e-7-10j", 1.23e-7 - 10j),
    ("1.23e7+1.23j", 1.23e7 + 1.23j),
    ("1.23e+7+1.23j", 1.23e7 + 1.23j),
    ("1.23e-7+1.23j", 1.23e-7 + 1.23j),
    ("1.23e7-1.23j", 1.23e7 - 1.23j),
    ("1.23e+7-1.23j", 1.23e7 - 1.23j),
    ("1.23e-7-1.23j", 1.23e-7 - 1.23j),
    # Infinities.
    ("1.23+infj", 1.23 + complex("infj")),
    ("1.23-infj", 1.23 - complex("infj")),
    ("inf+infj", float("inf") + complex("infj")),
    ("inf-infj", float("inf") - complex("infj")),
    # Infinities with scientific.
    ("1.23e7+infj", 1.23e7 + complex("infj")),
    ("1.23e7-infj", 1.23e7 - complex("infj")),
    ("1.23e+7+infj", 1.23e7 + complex("infj")),
    ("1.23e+7-infj", 1.23e7 - complex("infj")),
    ("1.23e-7+infj", 1.23e-7 + complex("infj")),
    ("1.23e-7-infj", 1.23e-7 - complex("infj")),
    ("inf+1.23e7j", float("inf") + 1.23e7j),
    ("inf-1.23e7j", float("inf") - 1.23e7j),
    ("inf+1.23e+7j", float("inf") + 1.23e7j),
    ("inf-1.23e+7j", float("inf") - 1.23e7j),
    ("inf+1.23e-7j", float("inf") + 1.23e-7j),
    ("inf-1.23e-7j", float("inf") - 1.23e-7j),
)


FUNCTION_EXPRESSIONS_EAGER = (
    # Single argument.
    ("cos(0)", _COS(0).eval()),
    ("cos(3.141)", _COS(3.141).eval()),
    (
        "cos(1.8446744073709552923592595329252523523e+19)",
        _COS(1.8446744073709552923592595329252523523e19).eval(),
    ),
    # Multiple arguments.
    ("arctan2(0, 0)", _ATAN2(0, 0).eval()),
    ("arctan2(1, 1)", _ATAN2(1, 1).eval()),
    ("arctan2(1.23e-5, 6.43e-7)", _ATAN2(1.23e-5, 6.43e-7).eval(),),
    # Nested functions.
    ("(1-cos(2*8.8))/2", ((1 - _COS(2 * 8.8)) / 2).eval(),),
    # Compound expressions.
    ("3.141*sin(3.141)", (3.141 * _SIN(3.141)).eval()),
    ("-3.141*tan(3.141)", (-3.141 * _TAN(3.141)).eval()),
    ("-10*abs(1.82)*pos(3.141)", (-10 * _ABS(1.82) * 3.141).eval()),
)


FUNCTION_EXPRESSIONS_LAZY = (
    # Single argument.
    ("cos(pi)", _COS(_PI)),
    ("cos(pi/2)", _COS(_PI / 2)),
    ("cos(3*pi/2)", _COS(3 * _PI / 2)),
    ("exp(1j*pi)", _EXP(1j * _PI)),
    # Multiple arguments.
    ("arctan2(pi, pi)", _ATAN2(_PI, _PI)),
    # Nested functions.
    ("arccos(cos(pi))", _ACOS(_COS(_PI)),),
    ("arcsin(sin(pi/2))", _ASIN(_SIN(_PI / 2))),
)


PARENTHESISED_EXPRESSIONS_EAGER = (
    ("(3*5)**2", (3 * 5) ** 2),
    ("(2+3)*4", (2 + 3) * 4),
    ("(4**3)**2", (4 ** 3) ** 2),
    ("10/(5/2)", 10 / (5 / 2)),
    # With whitespace.
    ("(1 + 1)", (1 + 1)),
    ("((1 + 1))", ((1 + 1))),
    ("(((1 + 1)))", (((1 + 1)))),
    ("(1+ 1)", (1 + 1)),
    ("(1 +1)", (1 + 1)),
    ("( 1 + 1)", (1 + 1)),
    ("(1 + 1 )", (1 + 1)),
    ("( 1 + 1 )", (1 + 1)),
    ("(1   +  1 )", (1 + 1)),
    ("( 1   +  1)", (1 + 1)),
    ("(  (1 + (2 - 3) ) * 5)", ((1 + (2 - 3)) * 5)),
)


PARENTHESISED_EXPRESSIONS_LAZY = (
    # The 10//4 branch gets eagerly evaluated, but the rest is left as symbolic because of `pi`.
    ("(cos(pi)+(10//4)-3)*5", _MUL(_SUB(_ADD(_COS(_PI), 2), 3), 5)),
    # With whitespace.
    ("((( cos(  pi ) + (10//4) - 3) ) * 5)", _MUL(_SUB(_ADD(_COS(_PI), 2), 3), 5),),
)


# Expressions that are eagerly evaluated by the compiler.
# Note: we separate out complex/imaginary numbers here; they're not allowed as model element values
# so we apply a separate test.
EAGER_EXPRESSIONS = (
    UNARY_INTEGERS
    + UNARY_FLOATS
    + NUMBER_EXPRESSIONS
    + FUNCTION_EXPRESSIONS_EAGER
    + PARENTHESISED_EXPRESSIONS_EAGER
)
EAGER_EXPRESSIONS_COMPLEX = (
    UNARY_IMAGINARIES + UNARY_COMPLEX + COMPLEX_NUMBER_EXPRESSIONS
)

# Expressions that are kept as symbols due to dependencies on other symbols.
LAZY_EXPRESSIONS = (
    CONSTANTS + FUNCTION_EXPRESSIONS_LAZY + PARENTHESISED_EXPRESSIONS_LAZY
)
