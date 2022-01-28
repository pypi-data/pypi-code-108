from finesse.model import Model
from finesse.script.spec import KatSpec


_MODEL = Model()
_SPEC = KatSpec()

# Supported kat script operators.
BINARY_OPERATORS = _SPEC.binary_operators
UNARY_OPERATORS = _SPEC.unary_operators
CONSTANTS = _SPEC.constants
EXPRESSION_FUNCTIONS = _SPEC.expression_functions
