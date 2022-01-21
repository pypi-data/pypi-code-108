import operator
import re

from momotor.options.task_id import ID_RE_STR

MOD_RE = re.compile(
    r"^\s*"
    r"(?:%(?P<mod>[\w-]+))?"
)

VALUE_ATTR = {
    'file': 'name',
    'prop': 'value',
    'opt': 'value',
    'result': 'outcome',
    None: 'step_id',  # Outcome types
}

REFERENCE_RE = re.compile(
    r"^\s*"
    r"(?P<type>[\w-]+)"
    r"\s*"
    r"(?P<opt>\[([^]]*)])?"
)

REF_OPTION_RE = re.compile(
    r'^(?:'
        r'@(?P<provider>[\w-]+)'
    r')?'
    r'\s*'
    r'(?:'
        rf'#\s*(?P<ids>{ID_RE_STR}(?:\s*,\s*{ID_RE_STR})*)'
    r')?'
    r'\s*'
    r'(?:'
        r':\s*(?P<name>(?:[^\'",\s]+|"[^"]*"|\'[^\']*\')*)'
    r')?'
)

# All operators and functions to check them
OPERATIONS = {
    None: lambda prop_value, value: True,
    '?': lambda prop_value, value: bool(prop_value),
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le
}

# These operators should have no value
OPERATIONS_WITHOUT_VALUE = {None, '?'}

OPERATORS = sorted(
    (op for op in OPERATIONS.keys() if op),
    key=lambda op: (len(op), op),
    reverse=True
)

CONDITION_RE = re.compile(
    r"(?P<oper>" + '|'.join(re.escape(op) for op in OPERATORS) + r")?"  # operator
    r"(?(oper)(?P<value>"
        r"[+-]?(?:0|[123456789][\d_]*)(?:\.(?:0|[123456789][\d_]*))?(?:e[+-]?(?:0|[123456789][\d_]*))?"  # int or float
        r"|'[^']*'"  # single-quoted string
        r'|"[^"]*"'  # double-quoted string
        r'|'  # empty                                                         
    r"))"  # value, only if an oper group exists
)


