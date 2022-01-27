"""Manipulate data to have different format or output different data."""
import traceback
import sys
import yattag
import uuid
from typing import Optional
import ast
from string import Formatter
from operator import attrgetter
import re
from email.utils import parseaddr, formataddr

from footil.tools import string_pattern_methods

PATTERN_METHODS = {
    'join_parent_attrs': {
        'method': string_pattern_methods._join_parent_attrs,
        # Key represents argument position and val method how
        # to convert argument.
        'conversion': {3: ast.literal_eval}
    }
}

ODD_REPEAT_PATTERN = r'((?<!{c}){c}({c}{c})*(?!{c}))'
EVEN_REPEAT_PATTERN = r'(?<!{c})({c}{c})+(?!{c})'


def format_list_to_html(
        line_height=1, collapse_cfg: Optional[dict] = None) -> str:
    """Format list of strings into HTML string.

    Lines are converted into HTML paragraphs. line-height attribute is
    set for all paragraphs. This is default format.

    Optionally can specify collapse_cfg to make part of text
    "togglable" (aka read more/read less). Two ways are supported:
        - bootstrap collapse (default).
        - attr_toggle on div that is "togglable".

    In both cases max_lines key is required.

    First case is used if max_lines is specified (maximum lines to
    show initially), but not attr_toggle. Optionally collapse_id can be
    passed to use it as anchor for bootstrap collapse toggle. Otherwise
    str(uuid.uuid4()) value is used.

    Second case is used if attr_toggle is used. This way only specified
    custom attribute is added on div that wraps paragraphs that should
    be hidden initially. Paragraphs toggle implementation must be done
    externally in this case.

    Args:
        line_height: paragraph height (default: {1})
        collapse_cfg: toggle show/hide part of text config
            (default: {None}) Used keys:
              - max_lines (int): number of paragraphs to show initially.
              - collapse_id (str): anchor for collapse div
                identification. If not set, will use randomly generated
                ID. Bootstrap implementation only.
              - attr_toggle (tuple): attribute used to toggle show/hide
                part of text. Custom implementation only.

    Returns:
        HTML string

    """
    def build_lines(lines):
        for line in lines:
            # Assuming that line is one paragraph, so `\n` is not needed.
            line = line.replace('\n', '')
            with tag('p'):
                text(line)

    def build_bootstrap_collapse(lines_to_hide):
        # Default to random ID if none was specified. It has
        # very low chance to run in collision, so there should
        # be no problem.
        collapse_id = (
            collapse_cfg.get('collapse_id') or str(uuid.uuid4()))
        with tag('div', id=collapse_id, klass='collapse'):
            build_lines(lines_to_hide)
        # Add button to toggle hidden lines.
        with tag(
            'a',
            ('data-toggle', 'collapse'),
            ('data-target', '#%s' % collapse_id),
                klass='btn btn-link'):
            text('Toggle More')

    def format_html(lines):
        with tag('div'):
            doc.attr(style='line-height: %s' % line_height)
            max_lines = collapse_cfg['max_lines']
            if max_lines == -1:  # Everything is showed.
                build_lines(lines)
            else:
                # Split into lines to show and to hide.
                # Lines to hide.
                lines_to_show = lines[0:max_lines]
                lines_to_hide = lines[max_lines:]
                # Build lines that will be visible all the time.
                build_lines(lines_to_show)
                # Build lines that will be hidden initially.
                if collapse_cfg.get('attr_toggle'):
                    # Using custom specified attribute that should be
                    # used to handle toggling of lines_to_hide (
                    # implementation must be done externally from this
                    # method).
                    with tag('div', collapse_cfg['attr_toggle']):
                        build_lines(lines_to_hide)
                else:
                    # Default to bootstrap implementation.
                    build_bootstrap_collapse(lines_to_hide)
        return doc.getvalue()

    if not collapse_cfg:
        collapse_cfg = {'max_lines': -1}
    doc, tag, text = yattag.Doc().tagtext()
    return format_html


def _format_exception() -> list:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return traceback.format_exception(exc_type, exc_value, exc_traceback)


def _get_formatted_exception(
        exc_lines: list, formatter=None) -> str:
    if not formatter:
        return ''.join(exc_lines)
    return formatter(exc_lines)


def get_formatted_exception(formatter=None) -> str:
    """Convert exception lines into formatter string.

    How string is formatted, depends on formatter function passed.
    Formatter acts as constructor, so it needs to be executed where its
    closure function can take specified arguments (if there are any) and
    do actual formatting.

    Args:
        formatter: logic how to format (default: {None}). If not
        specified will default to ''.join(exc_lines).

    Returns:
        formatted exception lines string

    """
    exc_lines = _format_exception()
    return _get_formatted_exception(exc_lines, formatter=formatter)


def _parse_pattern_methods(pattern: str, obj: object) -> str:
    def convert_args(args, conversion_map):
        new_args = []
        for index, arg in enumerate(args):
            new_args.append(
                conversion_map[index](arg) if index in conversion_map else
                arg)
        return new_args

    # Catch all methods and their content.
    for key, dct in PATTERN_METHODS.items():
        method = dct['method']
        for match in re.findall(r'\$%s\(.*?\)' % key, pattern):
            args = re.findall(r'\"(.*?)\"', match)
            if dct.get('conversion'):
                args = convert_args(args, dct['conversion'])
            parsed = method(obj, *args)
            pattern = pattern.replace(match, parsed)
    return pattern


def generate_name(pattern: str, obj: object, strip_falsy: bool = True) -> str:
    """Generate name by pattern, using attributes specified by it.

    Object is used to get required attributes values. If object does
    not have truthy value for attribute, it can be stripped using
    keyword argument strip_falsy.

    Args:
        pattern (str): pattern to generate name by. e.g.
            'test {a.b} / {c}'
        obj (object): object to retrieve attributes from.
        strip_falsy (bool): whether to strip away falsy attribute
            values or not. If stripped away, then leading string is
            also stripped away for next attribute to not look like
            '/ attr_value'. It instead just looks like 'attr_value'
            (default: {True}).

    Returns:
        Generated name using pattern and obj attributes.
        str

    """
    def prepare_val(idx):
        literal_text, attr_val = fname_vals[idx]
        if attr_val or not strip_falsy:
            attr_val_str = str(attr_val)
            # Edge case, when first item was false and we don't want to
            # keep leading string hanging.
            if idx == 1 and not fname_vals[0][1] and strip_falsy:
                return attr_val_str
            return literal_text + attr_val_str
        return ''

    # First parse pattern methods if there are any defined on a
    # pattern.
    pattern = _parse_pattern_methods(pattern, obj)
    name = ''
    # To track previous attribute value.
    fname_vals = {}
    for idx, item in enumerate(Formatter().parse(pattern)):
        # If no attribute to use, we can simply add next part of string
        # to name.
        if not item[1]:
            name += item[0]
            continue
        # Get attribute value from attr key. We use attrgetter from
        # operator module to be able to access n-depth attributes.
        # In Other words access attribute of objects that are
        # related with another object.
        f = attrgetter(item[1])  # item[1] is attribute key.
        attr_val = f(obj)
        fname_vals[idx] = (item[0], attr_val)
        name += prepare_val(idx)
    return name


def generate_names(cfg: dict) -> list:
    """Wrap generate_name and reuse for multiple objects.

    cfg keys:
        pattern (str): pattern to generate name by. e.g.
            'test {a.b} / {c}'
        objects (iterable): iterable of objects to use.
        strip_falsy (bool): whether to strip away falsy attribute
            values or not. If stripped away, then leading string is
            also stripped away for next attribute to not look like
            '/ attr_value'. It instead just looks like 'attr_value'
            (default: {True})
        key (str): attribute name to put its value into tuple
            (default: {'id'})

    Returns:
        list of tuple pairs, where first item is identifier, second
        generated name string.

    """
    try:
        pattern = cfg['pattern']
        objects = cfg['objects']
    except KeyError as e:
        raise ValueError("cfg is missing required key '%s'" % e)
    # strip falsy values is True on default.
    strip_falsy = cfg.get('strip_falsy', True)
    # Default key is 'id' attribute.
    key = cfg.get('key', 'id')
    return [
        (
            getattr(obj, key),
            generate_name(pattern, obj, strip_falsy=strip_falsy)
        )
        for obj in objects
    ]


# Email formatting utilities.

def replace_email_name(name: str, old_email: str) -> str:
    """Replace email name with new one."""
    _, email_part = parseaddr(old_email)
    return formataddr((name, email_part))


def replace_email(email_part: str, old_email: str) -> str:
    """Replace email part with new one.

    Email name is kept the same if one was present.

    Args:
        email_part: new email to replace with.
        old_email: email to replace to.

    """
    name, _ = parseaddr(old_email)
    return formataddr((name, email_part))


def email_to_alias_and_domain(email: str):
    """Extract alias and domain part from email.

    If can't extract alias/domain, tuple with empty strings is returned
    instead.

    Args:
        email: email to extract alias with domain from.

    Returns:
        email's alias with domain.
        tuple

    """
    email = parseaddr(email)[1]  # Falsy value returns `('', '')`
    if email:
        email_parts = email.split('@', 1)
        # Assuming that alias and domain are separated by @.
        if len(email_parts) == 2:
            return email_parts
    return ('', '')


def email_to_domain(email: str) -> str:
    """Extract domain part from email.

    If can't extract domain, empty string is returned instead.

    Args:
        email: email to extract domain from.

    Returns:
        email's domain part.
        str

    """
    return email_to_alias_and_domain(email)[1]


def email_to_alias(email: str) -> str:
    """Extract alias part from email.

    If can't extract alias, empty string is returned instead.

    Args:
        email: email to extract alias from.

    Returns:
        email's alias part.
        str

    """
    return email_to_alias_and_domain(email)[0]


# String formatting


def __to_new_format(fmt: str, named=True):
    def to_named_fmt(fmt):
        pattern = rf'{odd_perc_pattern}\((.*?)\)s'
        match = re.search(pattern, fmt)
        while match:
            # Only care about placeholder group here.
            __, __, placeholder = match.groups()
            fmt = fmt.replace(
                f'%({placeholder})s',
                f'{{{placeholder}}}'
            )
            match = re.search(pattern, fmt)
        return fmt

    def to_pos_fmt(fmt):
        even_perc_pattern = EVEN_REPEAT_PATTERN.format(c='%')
        pattern = rf'{even_perc_pattern}s'
        # When positional placeholder has even amount of percents, it
        # will be treated as not having enough arguments passed.
        if re.search(pattern, fmt):
            raise TypeError(
                'not all arguments converted during string formatting'
            )
        return fmt.replace('%s', '{}')

    odd_perc_pattern = ODD_REPEAT_PATTERN.format(c='%')
    # Escape `{` and `}`, because new formatting uses it.
    fmt = fmt.replace('{', '{{').replace('}', '}}')
    fmt = to_named_fmt(fmt) if named else to_pos_fmt(fmt)
    # If we find odd number of occurring percentage symbols, it means
    # those were not escaped and we can't finish conversion.
    if re.search(odd_perc_pattern, fmt):
        raise ValueError('incomplete format')
    return fmt.replace('%%', '%')


def to_new_named_format(fmt: str) -> str:
    """Convert old style named formatting to new style formatting.

    For example: '%(x)s - %%%(y)s' -> '{x} - %{y}'

    Args:
        fmt: old style formatting to convert.

    Returns:
        new style formatting.

    """
    return __to_new_format(fmt, named=True)


def to_new_pos_format(fmt: str) -> str:
    """Convert old style positional formatting to new style formatting.

    For example: '%s - %%%s' -> '{} - %{}'

    Args:
        fmt: old style formatting to convert.

    Returns:
        new style formatting.

    """
    return __to_new_format(fmt, named=False)


def replace_ic(
    term: str,
    to_replace: str,
        replace_with: Optional[str] = '') -> str:
    """Replace fragment in term with other fragment (ignore case).

    This is case-insensitive replacement, e.g. words 'Hello' and
    'heLLo' will be replaced if key to replace is 'HELLO', 'HeLlo'
    and etc.

    Args:
        term (str): term where fragment to replace will be searched
            for and replaced with new fragment.
        to_replace (str): fragment to be replaced (old fragment).
        replace_with (str): fragment to be replaced with
            (new fragment) (default: {''}).

    Returns:
        new term where old fragment (to_replace) in term is replaced
        with new fragment (to_replace).
        str

    """
    insensitive_fragment = re.compile(to_replace, re.IGNORECASE)
    return insensitive_fragment.sub(replace_with, term)


def strip_space(s: str) -> str:
    r"""Replace all spaces from string.

    Removes space like ' ', '\t', '\n' or '\r'. It will remove between
    chars too.

    Args:
        s: string to remove white space for.

    Returns:
        New string with all spaces removed.

    """
    return ''.join(s.split())


def split_force(
    s: str,
    sep: Optional[str] = None,
    maxsplit: int = -1,
        default: any = None) -> list:
    """Force split string into specified number of parts.

    Always splits into specified maxsplit parts. If string can't be
    split into that many parts, default value will be used to fill up
    remaining parts.

    maxsplit=-1 or 0 acts same way as builtin string `split`.

    Args:
        s: string to split
        sep: the delimiter according which to split the string. None
            means split according to any whitespace, and discard empty
            strings from the result. (default: {None})
        maxsplit: maximum number of splits to do. -1 means no limit.
            (default: {-1})
        default: value to use in filling splits that could not be done.
            (default: {None})

    Returns:
        list of split string parts.

    """
    parts = s.split(sep=sep, maxsplit=maxsplit)
    if maxsplit <= 0:  # matches builtin s.split
        return parts
    to_split_count = maxsplit - len(parts) + 1
    return parts + [default] * to_split_count


def format_digits(s: str) -> str:
    """Keep only digits in a string."""
    return re.sub(r'\D', '', s)


def format_func_input(
    func_name: str,
    command: bool = False,
    no_first_arg: bool = False,
    prefix: str = '',
    args: tuple = None,
        kwargs: dict = None) -> tuple:
    """Format function input for logging/printing.

    Can create reproducible string to look like it was called as
    function or command from shell.

    Args:
        func_name: function name to format it.
        command: whether to format it as shell call. E.g.
            func arg1 arg2. Otherwise its formatter as
            func(arg1, arg2)
        no_first_arg: whether to not include first argument in
            formatting.
        prefix: prefix to be added before format string.
        args: function used argument.
        kwargs: function used keyword arguments.

    Returns:
        tuple containing pattern string and arguments for it.

    """
    def get_options(command, have_args_kwargs):
        if command:
            sep = ' '
            # If there are no args and kwargs, we dont need to start
            # with space, cause there is nothing to separate from.
            wrap_start = ' ' if have_args_kwargs else ''
            wrap_end = ''
            formatter_ = str
        else:
            sep = ', '
            wrap_start = '('
            wrap_end = ')'
            formatter_ = repr
        return sep, wrap_start, wrap_end, formatter_

    def get_base_input(prefix, func_name):
        return '%s%s' % (prefix, func_name)

    def get_args_input_str(args):
        return sep.join([formatter_(arg) for arg in args])

    def get_kwargs_input_str(kwargs):
        return sep.join(['{}={}'.format(
            k, formatter_(v)) for k, v in kwargs.items()])

    def combine_args_kwargs_input_str(
            args_input_str, kwargs_input_str):
        args_kwargs_input = []
        if args_input_str:
            args_kwargs_input.append(args_input_str)
        kwargs_input_str = get_kwargs_input_str(kwargs)
        if kwargs_input_str:
            args_kwargs_input.append(kwargs_input_str)
        return sep.join(args_kwargs_input)

    if not args:
        args = ()
    if no_first_arg and args:
        args = args[1:]
    if not kwargs:
        kwargs = {}
    sep, wrap_start, wrap_end, formatter_ = get_options(
        command, bool(args or kwargs))
    base_input = get_base_input(prefix, func_name)
    args_input_str = get_args_input_str(args)
    kwargs_input_str = get_kwargs_input_str(kwargs)
    args_kwargs_input_str = combine_args_kwargs_input_str(
        args_input_str, kwargs_input_str)
    return (
        '%s%s%s%s', (base_input, wrap_start, args_kwargs_input_str, wrap_end)
    )


def format_same_type_vals(
        dct: dict,
        keys: list,
        method_name: str,
        args=None,
        kwargs=None) -> None:
    """Update values having same type.

    Args:
        dct: dictionary to update.
        keys: keys to update their values.
        method_name: method to call from retrieved value.
        args: positional arguments to call for method_name (default: {None}).
        kwargs: keyword arguments to call for method_name (default: {None}).
    """
    if not args:
        args = ()
    if not kwargs:
        kwargs = {}
    for key in keys:
        old_val = dct[key]
        method = getattr(old_val, method_name)
        dct[key] = method(*args, **kwargs)
