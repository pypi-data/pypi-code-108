import logging
import builtins
from tornado.template import Template
from tornado import escape
from io import StringIO
import ast
import linecache
from tornado.util import ObjectDict, exec_in, unicode_type
from .datatypes import testers
from datetime import datetime


class SQLTemplateCustomError(Exception):
    def __init__(self, err, code=400):
        self.code = code
        self.err = err
        super().__init__(err)

# t = Template(""" SELECT * from test where lon between {{Float32(lon1, 0)}} and {{Float32(lon2, 0)}} """)
# names = get_var_names(t)
# print(generate(t, **{x: '' for x in names}))

# t = Template(""" SELECT * from test where lon between {{lon1}} and {{lon2}} """)
# names = get_var_names(t)
# replace_vars_smart(t)
# print(generate(t, **{x: '' for x in names}))


DEFAULT_PARAM_NAMES = ['format', 'q']

parameter_types = [
    'String',
    'Boolean',
    'DateTime',
    'Date',
    'Float32',
    'Float64',
    'Int8',
    'Int16',
    'Int32',
    'Int64',
    'UInt8',
    'UInt16',
    'UInt32',
    'UInt64',
    'Array'
]

parameter_openapi_types = {
    'String': 'string',
    'Boolean': 'boolean',
    'DateTime': 'string',
    'Date': 'string',
    'Float32': 'number',
    'Float64': 'number',
    'Int8': 'integer',
    'Int16': 'integer',
    'Int32': 'integer',
    'Int64': 'integer',
    'UInt8': 'integer',
    'UInt16': 'integer',
    'UInt32': 'integer',
    'UInt64': 'integer',
    'Array': 'array'
}


def transform_type(tester, transform, placeholder=None, required=None, description=None, enum=None, example=None, format=None):
    def _f(x, default=None, defined=True, required=None, description=None, enum=None, example=None, format=None):
        if type(x) == Placeholder:
            if default:
                x = default
            else:
                x = placeholder
        elif x is None:
            x = default
            if x is None:
                if defined:
                    raise ValueError("invalid parameter")
                else:
                    return None
        if tester == 'String':
            if x is not None:
                return transform(x)
        elif testers[tester](str(x)):
            return transform(x)
        raise ValueError(f"Error validating '{x}' to type {tester}")
    return _f


def _and(*args, **kwargs):
    operands = {'in': 'in', 'not_in': 'not in', 'gt': '>', 'lt': '<'}

    def _name(k):
        tk = k.rsplit('__', 1)
        return tk[0]

    def _op(k):
        tk = k.rsplit('__', 1)
        if len(tk) == 1:
            return '='
        else:
            if tk[1] in operands:
                return operands[tk[1]]
            raise ValueError(f"operand {tk[1]} not supported")
    return Expression(' and '.join(
        [f"{_name(k)} {_op(k)} {expression_wrapper(v, k)}" for k, v in kwargs.items() if v is not None]))


def error(s, code=400):
    raise ValueError(s)


def custom_error(s, code=400):
    raise SQLTemplateCustomError(s, code)


class Expression(str):
    pass


class Comment:
    def __init__(self, s):
        self.text = s

    def __str__(self):
        return self.text


class Placeholder:
    def __init__(self, name=None, line=None):
        self.name = name if name else '__placeholder__'
        self.line = line or 'unknown'

    def __str__(self):
        return '__placeholder__'

    def __getitem__(self, i):
        if i > 2:
            raise IndexError()
        return Placeholder()

    def __add__(self, s):
        return Placeholder()

    def __call__(self, *args, **kwargs):
        raise ValueError(f"'{self.name}' is not a valid function, line {self.line}")

    def split(self, ch):
        return [Placeholder(), Placeholder()]

    def startswith(self, c):
        return False


class Symbol:
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return self.x


def columns(x, default=None, fn=None):
    if x is None or type(x) == Placeholder:
        if default is None:
            raise ValueError("Missing columns() default value, use `columns(column_names, 'default_column_name')`")
        x = default

    _columns = [c.strip() for c in x.split(',')]

    if fn:
        return Expression(','.join(f'{fn}({str(column(c, c))}) as {c}' for c in _columns))
    else:
        return Expression(','.join(str(column(c, c)) for c in _columns))


def column(x, default=None):
    if x is None or type(x) == Placeholder:
        if default is None:
            raise ValueError("Missing column() default value, use `column(column_name, 'default_column_name')`")
        x = default
    return Symbol("`" + sqlescape(x) + "`")


def symbol(x, quote='`'):
    if type(x) == Placeholder:
        return Symbol("`placeholder`")
    return Symbol(quote + sqlescape(x) + quote)


def table(x, quote='`'):
    if type(x) == Placeholder:
        return Symbol("placeholder")
    return Symbol(sqlescape(x))


def boolean(x, default=None):
    if x is None:
        raise ValueError('wrong value')
    if type(x) == Placeholder:
        if default is not None:
            return boolean(default)
        return True

    elif type(x) == bool:
        return x
    elif x.lower() == 'true':
        return True
    elif x.lower() == 'false':
        return False
    if testers['Integer'](x):
        return int(x)

    if '' == x:
        return False
    return True


def defined(x=None):
    if type(x) == Placeholder or x is None:
        return False
    return True


def array_type(types):  # noqa: C901
    def _f(x, _type=None, default=None, defined=True, required=None, description=None, enum=None, example=None, format=None):
        if type(x) == Placeholder:
            if default:
                x = default
            else:
                if _type and _type in types:
                    x = ','.join(map(str, [types[_type](x) for _ in range(2)]))
                else:
                    x = ','.join([f'__placeholder__{i}' for i in range(2)])
        elif x is None:
            x = default
            if x is None:
                if defined:
                    raise ValueError("invalid parameter")
                else:
                    return None
        values = []
        for i, t in enumerate(x.split(',')):
            if _type in testers:
                if testers[_type](str(t)):
                    values.append(expression_wrapper(
                        types[_type](t), f'{x}[{i}]'))
                else:
                    raise ValueError(
                        f"Error validating {x}[{i}]({t}) to type {_type}")
            else:
                values.append(expression_wrapper(
                    types.get(_type, lambda x: x)(t), f'{x}[{i}]'))
        return Expression(f"({','.join(map(str, values))})")
    return _f


def sql_unescape(x, what=''):
    """
    unescapes specific characters in a string. It allows to allow some
    special characters to be used, for example in like condictionals

    {{sql_unescape(String(like_filter), '%')}}


    >>> sql_unescape('testing%', '%')
    "'testing%'"
    >>> sql_unescape('testing%', '$')
    "'testing\\\\%'"
    """
    return Expression("'" + sqlescape(x).replace(f'\\{what}', what) + "'")


def split_to_array(x, default=''):
    if type(x) == Placeholder or x is None:
        x = default
    return [s.strip() for s in x.split(',')]


def enumerate_with_last(arr):
    """
    >>> enumerate_with_last([1, 2])
    [(False, 1), (True, 2)]
    >>> enumerate_with_last([1])
    [(True, 1)]
    """
    arr_len = len(arr)
    return [(arr_len == i + 1, x) for i, x in enumerate(arr)]


def string_type(x, default=None):
    if type(x) == Placeholder:
        if default:
            x = default
        else:
            x = '__placeholder__'
    return x


def day_diff(d0, d1, default=None):
    """
    >>> day_diff('2019-01-01', '2019-01-01')
    0
    >>> day_diff('2019-01-01', '2019-01-02')
    1
    >>> day_diff('2019-01-02', '2019-01-01')
    1
    >>> day_diff('2019-01-02', '2019-02-01')
    30
    >>> day_diff('2019-02-01', '2019-01-02')
    30
    >>> day_diff(Placeholder(), Placeholder())
    0
    >>> day_diff(Placeholder(), '')
    0
    """
    if type(d0) == Placeholder or type(d1) == Placeholder:
        if default:
            return default
        return 0
    isoformat = "%Y-%m-%d"
    try:
        return abs((datetime.strptime(d1, isoformat) - datetime.strptime(d0, isoformat)).days)
    except Exception:
        raise Exception(
            'invalid date format, it must be ISO format date, e.g. 2018-09-07')


function_list = {
    'columns': columns,
    'table': table,
    'TABLE': table,
    'error': error,
    'custom_error': custom_error,
    'sql_and': _and,
    'defined': defined,
    'column': column,
    'enumerate_with_last': enumerate_with_last,
    'split_to_array': split_to_array,
    'day_diff': day_diff,
    'sql_unescape': sql_unescape
    # 'enumerate': enumerate
}


def get_transform_types(placeholders=None):
    if placeholders is None:
        placeholders = {}
    types = {
        'bool': boolean,
        'Boolean': boolean,
        'DateTime': transform_type('DateTime', str, placeholders.get('DateTime', None), required=None, description=None, enum=None, example=None, format=None),
        'Date': transform_type('Date', str, placeholders.get('Date', None), required=None, description=None, enum=None, example=None, format=None),
        'Float32': transform_type('Float32', float, placeholders.get('Float32', None), required=None, description=None, enum=None, example=None, format=None),
        'Float64': transform_type('Float64', float, placeholders.get('Float64', None), required=None, description=None, enum=None, example=None, format=None),
        'Int': transform_type('Int32', int, placeholders.get('Int', None), required=None, description=None, enum=None, example=None, format=None),
        'Integer': transform_type('Int32', int, placeholders.get('Int32', None), required=None, description=None, enum=None, example=None, format=None),
        'Int8': transform_type('Int8', int, placeholders.get('Int8', None), required=None, description=None, enum=None, example=None, format=None),
        'Int16': transform_type('Int16', int, placeholders.get('Int16', None), required=None, description=None, enum=None, example=None, format=None),
        'UInt8': transform_type('UInt8', int, placeholders.get('UInt8', None), required=None, description=None, enum=None, example=None, format=None),
        'UInt16': transform_type('UInt16', int, placeholders.get('UInt16', None), required=None, description=None, enum=None, example=None, format=None),
        'UInt32': transform_type('UInt32', int, placeholders.get('UInt32', None), required=None, description=None, enum=None, example=None, format=None),
        'Int32': transform_type('Int32', int, placeholders.get('Int32', None), required=None, description=None, enum=None, example=None, format=None),
        'Int64': transform_type('Int64', int, placeholders.get('Int64', None), required=None, description=None, enum=None, example=None, format=None),
        'UInt64': transform_type('UInt64', int, placeholders.get('UInt64', None), required=None, description=None, enum=None, example=None, format=None),
        'Symbol': symbol,
        'Column': symbol,
        'String': transform_type('String', str, placeholder='__placeholder__', required=None, description=None, enum=None, example=None, format=None)
    }
    types['Array'] = array_type(types)
    types.update(function_list)
    return types


type_fns = get_transform_types()
type_fns_check = get_transform_types({
    'DateTime': '2019-01-01 00:00:00',
    'Date': '2019-01-01',
    'Float32': 0.0,
    'Float64': 0.0,
    'Int': 0,
    'Int8': 0,
    'Int16': 0,
    'UInt8': 0,
    'UInt16': 0,
    'UInt32': 0,
    'Int32': 0,
    'Int64': 0,
    'UInt64': 0,
    'Symbol': 'symbol'
})


# from https://github.com/elouajib/sqlescapy/
# MIT license
def sqlescape(str):
    return str.translate(
        str.maketrans({
            "\0": "\\0",
            "\r": "\\r",
            "\x08": "\\b",
            "\x09": "\\t",
            "\x1a": "\\z",
            "\n": "\\n",
            "\r": "\\r",
            "\"": "",
            "'": "\\'",
            "\\": "\\\\",
            "%": "\\%",
            "`": "\\`"
        }))


def expression_wrapper(x, name):
    if type(x) in (unicode_type, bytes, str):
        return "'" + sqlescape(x) + "'"
    elif type(x) == Placeholder:
        return "'__placeholder__'"
    elif type(x) == Comment:
        return "-- {x} \n"
    if x is None:
        raise ValueError(f'expression "{name}" evaluated to null')
    return x


_namespace = {
    "column": column,
    "symbol": symbol,
    "error": error,
    "custom_error": custom_error,
    "_tt_utf8": escape.utf8,  # for internal use
    "_tt_string_types": (unicode_type, bytes),
    "xhtml_escape": lambda x: x,
    "expression_wrapper": expression_wrapper,
    # disable __buildins__ and some other functions
    # they raise a pretty non undestandable error but if someone
    # is using them they know what they are trying to do
    # read https://anee.me/escaping-python-jails-849c65cf306e on how to escape from python jails
    "__buildins__": {},
    "__import__": {},
    '__debug__': {},
    '__doc__': {},
    '__name__': {},
    '__package__': {},
    "open": {},
    "close": {},
    "print": {}
}


reserved_vars = set(['_tt_tmp', '_tt_append', 'isinstance', 'str', 'error', 'custom_error'] + list(vars(builtins)))
for p in DEFAULT_PARAM_NAMES:  # we handle these in an specific manner
    reserved_vars.discard(p)  # `format` is part of builtins
error_vars = ['error', 'custom_error']


def generate(self, template_execution_results=None, **kwargs):
    """Generate this template with the given arguments."""
    if template_execution_results is None:
        template_execution_results = {}
    namespace = {}

    def set_max_threads(x):
        try:
            template_execution_results['max_threads'] = int(x)
            return Expression(f'-- max_threads {x}\n')
        except Exception:
            return Expression(f'-- max_threads: wrong argument {x}\n')

    def set_backend_hint(hint):
        template_execution_results['backend_hint'] = hint
        return Expression(f'-- backend_hint {hint}\n')

    namespace.update(_namespace)
    namespace.update(kwargs)
    namespace.update({
        # __name__ and __loader__ allow the traceback mechanism to find
        # the generated source code.
        "__name__": self.name.replace('.', '_'),
        "__loader__": ObjectDict(get_source=lambda name: self.code),
        "max_threads": set_max_threads,
        "backend_hint": set_backend_hint,
    })

    exec_in(self.compiled, namespace)
    execute = namespace["_tt_execute"]
    # Clear the traceback module's cache of source data now that
    # we've generated a new template (mainly for this module's
    # unittests, where different tests reuse the same name).
    linecache.clearcache()

    try:
        return execute()
    except SQLTemplateCustomError as e:
        raise e
    except Exception as e:
        if 'x' in namespace and namespace['x'] and hasattr(namespace['x'], 'line') and namespace['x'].line:
            line = namespace['x'].line
            raise ValueError(f'{e}, line {line}')
        raise e


class CodeWriter(object):
    def __init__(self, file, template):
        self.file = file
        self.current_template = template
        self.apply_counter = 0
        self._indent = 0

    def indent_size(self):
        return self._indent

    def indent(self):
        class Indenter(object):
            def __enter__(_):
                self._indent += 1
                return self

            def __exit__(_, *args):
                assert self._indent > 0
                self._indent -= 1

        return Indenter()

    def write_line(self, line, line_number, indent=None):
        if indent is None:
            indent = self._indent
        line_comment = '  # %s:%d' % ('<generated>', line_number)
        print("    " * indent + line + line_comment, file=self.file)


def get_var_names(t):
    def _n(chunks, v):
        for x in chunks:
            line_number = x.line
            if type(x).__name__ == '_ChunkList':
                _n(x.chunks, v)
            elif type(x).__name__ == "_Expression":
                c = compile(x.expression, "<string>", "exec", dont_inherit=True)
                variable_names = [x for x in c.co_names if x not in _namespace and x not in reserved_vars]
                v += list(map(lambda variable: {'line': line_number, 'name': variable}, variable_names))
            elif type(x).__name__ == '_ControlBlock':
                from io import StringIO
                buffer = StringIO()
                writer = CodeWriter(buffer, t)
                x.generate(writer)
                c = compile(buffer.getvalue(), "<string>", "exec", dont_inherit=True)
                variable_names = [x for x in c.co_names if x not in _namespace and x not in reserved_vars]
                v += list(map(lambda variable: {'line': line_number, 'name': variable}, variable_names))
                _n(x.body.chunks, v)

    var = []
    _n(t.file.body.chunks, var)
    return var


def get_var_data(content):  # noqa: C901
    def node_to_value(x):
        if type(x) in (ast.Bytes, ast.Str):
            return x.s
        elif type(x) == ast.Num:
            return x.n
        elif type(x) == ast.NameConstant:
            return x.value
        elif type(x) == ast.Name:
            return x.id
        elif type(x) == ast.List:
            return [elem.s for elem in x.elts]
        elif type(x) == ast.BinOp:
            # in this case there could be several variables
            # if that's the case the left one is the main
            r = node_to_value(x.left)
            if not r:
                r = node_to_value(x.right)
            return r
        elif type(x) == ast.Constant:
            return x.value
        else:
            try:
                return x.id
            except Exception:
                # don't let this ruin the parsing
                pass
        return None

    def _w(parsed):
        vars = {}
        for node in ast.walk(parsed):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                try:
                    func = node.func.id
                    # parse function args
                    args = []
                    for x in node.args:
                        if type(x) == ast.Call:
                            vars.update(_w(x))
                        else:
                            args.append(node_to_value(x))

                    kwargs = {}
                    for x in node.keywords:
                        kwargs[x.arg] = node_to_value(x.value)

                    if func == 'defined':
                        # define it as string and if it's used later it'll become something else
                        if len(args) > 0 and args[0] not in vars:
                            vars[args[0]] = {"type": 'String', "default": None}
                    elif func == 'Array':
                        if 'default' not in kwargs:
                            default = kwargs.get('default', args[2] if len(args) > 2 and args[2] else None)
                            kwargs['default'] = default
                        vars[args[0]] = {
                            "type": f'Array({args[1]})' if len(args) > 1 else 'Array(String)',
                            **kwargs
                        }
                    elif func in parameter_types:
                        # avoid variable names to be None
                        if args[0] is not None:
                            # if this is a cast use the function name to get the type
                            if 'default' not in kwargs:
                                default = kwargs.get('default', args[1] if len(args) > 1 else None)
                                kwargs['default'] = default
                            vars[args[0]] = {"type": func, **kwargs}
                except Exception as e:
                    # if we find a problem parsing, let the parsing continue
                    logging.error(f"pipe parsing problem {content}:  {e}")
            elif isinstance(node, ast.Name):
                # when parent node is a call it means it's managed by the Call workflow (see above)
                is_cast = isinstance(node.parent, ast.Call) and isinstance(node.parent.func, ast.Name) and node.parent.func.id in parameter_types
                is_reserved_name = node.id in reserved_vars or node.id in function_list or node.id in _namespace
                if (not isinstance(node.parent, ast.Call) or not is_cast) and not is_reserved_name:
                    vars[node.id] = {"type": 'String', 'default': None}

        return vars

    parsed = ast.parse(content)
    # calculate parents for each node for later checks
    for node in ast.walk(parsed):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    vars = _w(parsed)

    return [dict(name=k, **v) for k, v in vars.items()]


def get_var_names_and_types(t):  # noqa: C901
    """
    >>> get_var_names_and_types(Template("SELECT * FROM filter_value WHERE description = {{String(d, 'test_1')}} AND value = {{Int8(v, 3)}}"))
    [{'name': 'd', 'type': 'String', 'default': 'test_1'}, {'name': 'v', 'type': 'Int8', 'default': 3}]
    >>> get_var_names_and_types(Template("select * from test {% if defined(testing) and defined(testing2) %} where 1 {%end %}"))
    [{'name': 'testing', 'type': 'String', 'default': None}, {'name': 'testing2', 'type': 'String', 'default': None}]
    >>> get_var_names_and_types(Template("select {{Array(cod_stock_source_type,'Int16', defined=False)}}"))
    [{'name': 'cod_stock_source_type', 'type': 'Array(Int16)', 'defined': False, 'default': None}]
    >>> get_var_names_and_types(Template("select {{Array(cod_stock_source_type, defined=False)}}"))
    [{'name': 'cod_stock_source_type', 'type': 'Array(String)', 'defined': False, 'default': None}]
    >>> get_var_names_and_types(Template("select {{cod_stock_source_type}}"))
    [{'name': 'cod_stock_source_type', 'type': 'String', 'default': None}]
    >>> get_var_names_and_types(Template("select {{String(cod_stock_source_type, 'test')}}"))
    [{'name': 'cod_stock_source_type', 'type': 'String', 'default': 'test'}]
    >>> get_var_names_and_types(Template("select {{split_to_array(test)}}"))
    [{'name': 'test', 'type': 'String', 'default': None}]
    >>> get_var_names_and_types(Template("select {{'pepe'.startswith('p')}}"))
    []
    >>> get_var_names_and_types(Template("select {{String(test + 'abcd', 'default_value')}}"))
    [{'name': 'test', 'type': 'String', 'default': None}]
    >>> get_var_names_and_types(Template("SELECT * FROM filter_value WHERE description = {{String(d, 'test_1', description='test', required=True)}} AND value = {{Int8(v, 3, format='number', example='1')}}"))
    [{'name': 'd', 'type': 'String', 'description': 'test', 'required': True, 'default': 'test_1'}, {'name': 'v', 'type': 'Int8', 'format': 'number', 'example': '1', 'default': 3}]
    >>> get_var_names_and_types(Template("SELECT * FROM filter_value WHERE description = {{String(d, default='test_1', description='test')}}"))
    [{'name': 'd', 'type': 'String', 'default': 'test_1', 'description': 'test'}]
    >>> get_var_names_and_types(Template("select {{Array(cod_stock_source_type, 'Int16', default='1', defined=False)}}"))
    [{'name': 'cod_stock_source_type', 'type': 'Array(Int16)', 'default': '1', 'defined': False}]
    >>> get_var_names_and_types(Template('select {{symbol(split_to_array(attr, "amount_net")[0] + "_intermediate" )}}'))
    [{'name': 'attr', 'type': 'String', 'default': None}]
    >>> get_var_names_and_types(Template("SELECT * FROM filter_value WHERE description = {{Float32(with_value, 0.1)}} AND description = {{Float32(zero, 0)}} AND value = {{Float32(no_default)}}"))
    [{'name': 'with_value', 'type': 'Float32', 'default': 0.1}, {'name': 'zero', 'type': 'Float32', 'default': 0}, {'name': 'no_default', 'type': 'Float32', 'default': None}]
    >>> get_var_names_and_types(Template('''SELECT * FROM abcd WHERE hotel_id <> 0 {% if defined(date_from) %} AND script_created_at > {{DateTime(date_from, '2020-09-09 10:10:10', description="This is a description", required=True)(date_from, '2020-09-09', description="Filter script alert creation date", required=False)}} {% end %}'''))
    [{'name': 'date_from', 'type': 'String', 'default': None}, {'name': 'date_from', 'type': 'String', 'default': None}]

    """

    def _n(chunks, v):
        for x in chunks:
            if type(x).__name__ == '_ChunkList':
                _n(x.chunks, v)
            elif type(x).__name__ == "_Expression":
                var_data = get_var_data(x.expression)
                if var_data:
                    v += var_data
            elif type(x).__name__ == '_ControlBlock':
                buffer = StringIO()
                writer = CodeWriter(buffer, t)
                x.generate(writer)
                var_data = get_var_data(buffer.getvalue())
                if var_data:
                    v += var_data
                _n(x.body.chunks, v)
    var = []
    _n(t.file.body.chunks, var)
    return var


def wrap_vars(t):
    def _n(chunks, v):
        for x in chunks:
            if type(x).__name__ == '_ChunkList':
                _n(x.chunks, v)
            elif type(x).__name__ == "_Expression":
                x.expression = 'expression_wrapper(' + x.expression + \
                    ',"""' + x.expression.replace('"', '\\"') + '""")'
            elif type(x).__name__ == '_ControlBlock':
                _n(x.body.chunks, v)

    var = []
    _n(t.file.body.chunks, var)
    t.code = t._generate_python(t.loader)
    try:
        t.compiled = compile(
            escape.to_unicode(t.code),
            "%s.generated.py" % t.name.replace('.', '_'),
            "exec", dont_inherit=True)
    except Exception:
        # formatted_code = _format_code(t.code).rstrip()
        # app_log.error("%s code:\n%s", t.name, formatted_code)
        raise

    return var


def get_used_tables_in_template(sql):
    """
    >>> get_used_tables_in_template("select * from {{table('test')}}")
    ['test']
    >>> get_used_tables_in_template("select * from {%if x %}{{table('test')}}{%else%}{{table('test2')}}{%end%}")
    ['test', 'test2']
    >>> get_used_tables_in_template("select * from {{table('my.test')}}")
    ['my.test']
    >>> get_used_tables_in_template("select * from {{table('my.test')}}, another_table")
    ['my.test']
    >>> get_used_tables_in_template("select * from another_table")
    []
    >>> get_used_tables_in_template("select * from {{table('my.test')}}, {{table('another.one')}}")
    ['my.test', 'another.one']
    """
    t = Template(sql)

    def _n(chunks, tables):
        for x in chunks:
            if type(x).__name__ == "_Expression":
                c = compile(x.expression, "<string>",
                            "exec", dont_inherit=True)
                v = [
                    x.lower() for x in c.co_names if x not in _namespace and x not in reserved_vars]
                if 'table' in v:
                    def _t(*args, **kwargs):
                        return str(args[0])
                    n = {'table': _t, 'TABLE': _t}
                    e = "_tt_tmp = %s" % x.expression
                    exec_in(e, n)
                    tables += [n['_tt_tmp']]
            elif type(x).__name__ == '_ControlBlock':
                _n(x.body.chunks, tables)

    tables = []
    _n(t.file.body.chunks, tables)
    return tables


def render_sql_template(sql, variables=None, test_mode=False, template_execution_results=None):
    """
    >>> render_sql_template("select * from table where str = {{foo}}", { 'foo': 'test' })
    "select * from table where str = 'test'"
    >>> render_sql_template("select * from table where f = {{foo}}", { 'foo': 1.0 })
    'select * from table where f = 1.0'
    >>> render_sql_template("select * from table where f = {{Float32(foo)}}", { 'foo': 1 })
    'select * from table where f = 1.0'
    >>> render_sql_template("select * from table where f = {{foo}}", { 'foo': "';drop table users;" })
    "select * from table where f = '\\\\';drop table users;'"
    >>> render_sql_template("select * from {{symbol(foo)}}", { 'foo': 'table-name' })
    'select * from `table-name`'
    >>> render_sql_template("select * from {{Int32(foo)}}", { 'foo': 'non_int' })
    Traceback (most recent call last):
    ...
    ValueError: Error validating 'non_int' to type Int32
    >>> render_sql_template("select * from table where f = {{Float32(foo)}}", test_mode=True)
    'select * from table where f = 0.0'
    >>> render_sql_template("SELECT * FROM query_log__dev where a = {{test}}", test_mode=True)
    "SELECT * FROM query_log__dev where a = '__placeholder__'"
    >>> render_sql_template("SELECT {{test}}", {'token':'testing'})
    Traceback (most recent call last):
    ...
    ValueError: expression "test" evaluated to null
    >>> render_sql_template('{% if test %}SELECT 1{% else %} select 2 {% end %}')
    ' select 2 '
    >>> render_sql_template('{% if Int32(test, 1) %}SELECT 1{% else %} select 2 {% end %}')
    'SELECT 1'
    >>> render_sql_template('{% for v in test %}SELECT {{v}} {% end %}',test_mode=True)
    "SELECT '__placeholder__' SELECT '__placeholder__' SELECT '__placeholder__' "
    >>> render_sql_template("select {{Int32(foo, 1)}}", test_mode=True)
    'select 1'
    >>> render_sql_template("SELECT count() c FROM test_table where a > {{Float32(myvar)}} {% if defined(my_condition) %} and c = Int32({{my_condition}}){% end %}", {'myvar': 1.0})
    'SELECT count() c FROM test_table where a > 1.0 '
    >>> render_sql_template("SELECT count() c FROM where {{sql_and(a=a, b=b)}}", {'a': '1', 'b': '2'})
    "SELECT count() c FROM where a = '1' and b = '2'"
    >>> render_sql_template("SELECT count() c FROM where {{sql_and(a=a, b=b)}}", {'b': '2'})
    "SELECT count() c FROM where b = '2'"
    >>> render_sql_template("SELECT count() c FROM where {{sql_and(a=Int(a, defined=False), b=Int(b, defined=False))}}", {'b': '2'})
    'SELECT count() c FROM where b = 2'
    >>> render_sql_template("SELECT count() c FROM where {{sql_and(a__in=Array(a), b=b)}}", {'a': 'a,b,c','b': '2'})
    "SELECT count() c FROM where a in ('a','b','c') and b = '2'"
    >>> render_sql_template("SELECT count() c FROM where {{sql_and(a__not_in=Array(a), b=b)}}", {'a': 'a,b,c','b': '2'})
    "SELECT count() c FROM where a not in ('a','b','c') and b = '2'"
    >>> render_sql_template("SELECT c FROM where a > {{Date(start)}}", test_mode=True)
    "SELECT c FROM where a > '2019-01-01'"
    >>> render_sql_template("SELECT c FROM where a > {{DateTime(start)}}", test_mode=True)
    "SELECT c FROM where a > '2019-01-01 00:00:00'"
    >>> render_sql_template("SELECT c FROM where a > {{DateTime(start)}}", {'start': '2018-09-07 23:55:00'})
    "SELECT c FROM where a > '2018-09-07 23:55:00'"
    >>> render_sql_template('SELECT * FROM tracker {% if defined(start) %} {{DateTime(start)}} and {{DateTime(end)}} {% end %}', {'start': '2019-08-01 00:00:00', 'end': '2019-08-02 00:00:00'})
    "SELECT * FROM tracker  '2019-08-01 00:00:00' and '2019-08-02 00:00:00' "
    >>> render_sql_template('SELECT * from test limit {{Int(limit)}}', test_mode=True)
    'SELECT * from test limit 0'
    >>> render_sql_template('SELECT {{symbol(attr)}} from test', test_mode=True)
    'SELECT `placeholder` from test'
    >>> render_sql_template('SELECT {{Array(foo)}}', {'foo': 'a,b,c,d'})
    "SELECT ('a','b','c','d')"
    >>> render_sql_template("SELECT {{Array(foo, 'Int32')}}", {'foo': '1,2,3,4'})
    'SELECT (1,2,3,4)'
    >>> render_sql_template("SELECT {{Array(foo, 'Int32')}}", test_mode=True)
    'SELECT (0,0)'
    >>> render_sql_template("SELECT {{Array(foo)}}", test_mode=True)
    "SELECT ('__placeholder__0','__placeholder__1')"
    >>> res = {}
    >>> render_sql_template("{{max_threads(2)}} SELECT 1", template_execution_results=res)
    '-- max_threads 2\\n SELECT 1'
    >>> res
    {'max_threads': 2}
    >>> render_sql_template("SELECT {{String(foo)}}", test_mode=True)
    "SELECT '__placeholder__'"
    >>> render_sql_template("SELECT {{String(foo, 'test')}}", test_mode=True)
    "SELECT 'test'"
    >>> render_sql_template("SELECT {{String(foo, 'test')}}", {'foo': 'tt'})
    "SELECT 'tt'"
    >>> render_sql_template("SELECT {{String(format, 'test')}}", {'format': 'tt'})
    Traceback (most recent call last):
    ...
    ValueError: "format" can not be used as a variable name, line 1
    >>> render_sql_template("SELECT {{format}}", {'format': 'tt'})
    Traceback (most recent call last):
    ...
    ValueError: "format" can not be used as a variable name, line 1
    >>> render_sql_template("SELECT {{String(q, 'test')}}", {'q': 'tt'})
    Traceback (most recent call last):
    ...
    ValueError: "q" can not be used as a variable name, line 1
    >>> render_sql_template("SELECT {{column(agg)}}", {})
    Traceback (most recent call last):
    ...
    ValueError: Missing column() default value, use `column(column_name, 'default_column_name')`
    >>> render_sql_template("SELECT {{column(agg)}}", {'agg': 'foo'})
    'SELECT `foo`'
    >>> render_sql_template('{% if not defined(test) %}error("This is an error"){% end %}', {})
    'error("This is an error")'
    >>> render_sql_template('{% if not defined(test) %}custom_error({error: "This is an error"}){% end %}', {})
    'custom_error({error: "This is an error"})'
    >>> render_sql_template("SELECT {{String(foo + 'abcd')}}", test_mode=True)
    "SELECT '__placeholder__'"
    >>> render_sql_template("SELECT {{columns(agg)}}", {})
    Traceback (most recent call last):
    ...
    ValueError: Missing columns() default value, use `columns(column_names, 'default_column_name')`
    >>> render_sql_template("SELECT {{columns(agg, 'a,b,c')}} FROM table", {})
    'SELECT `a`,`b`,`c` FROM table'
    >>> render_sql_template("SELECT {{columns(agg, 'a,b,c')}} FROM table", {'agg': 'foo'})
    'SELECT `foo` FROM table'
    >>> render_sql_template("SELECT {{columns('a,b,c')}} FROM table", {})
    'SELECT `a`,`b`,`c` FROM table'
    >>> render_sql_template("% {% if whatever(passenger_count) %}{% end %}", test_mode=True)
    Traceback (most recent call last):
    ...
    ValueError: 'whatever' is not a valid function, line 1
    >>> render_sql_template("% {% if defined((passenger_count) %}{% end %}", test_mode=True)
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax
    >>> render_sql_template("SELECT * FROM dim_fecha_evento where foo like {{sql_unescape(String(pepe), '%')}}", {"pepe": 'raul_el_bueno_es_un_tikismikis_%'})
    "SELECT * FROM dim_fecha_evento where foo like 'raul_el_bueno_es_un_tikismikis_%'"
    """

    t = Template(sql)

    template_variables = get_var_names(t)

    for variable in template_variables:
        if variable['name'] in DEFAULT_PARAM_NAMES:
            name = variable['name']
            line = variable['line']
            raise ValueError(f'"{name}" can not be used as a variable name, line {line}')

    if test_mode:
        def dummy(*args, **kwargs):
            return Comment('error launched')
        v = {x['name']: Placeholder(x['name'], x['line']) for x in template_variables}

        if variables:
            v.update(variables)

        v.update(type_fns_check)
        v.update({
            # disable error throws on check
            'error': dummy,
            'custom_error': dummy
        })

    else:
        v = {x['name']: None for x in template_variables}
        if variables:
            v.update(variables)
        v.update(type_fns)

    wrap_vars(t)

    return generate(t, template_execution_results, **v).decode()
