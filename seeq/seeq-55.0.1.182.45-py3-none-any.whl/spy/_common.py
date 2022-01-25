import datetime
import json
import os
import re
import string
import sys
import traceback
import types
import uuid
import warnings as pywarnings
from typing import Optional

import numpy as np
import pandas as pd
import pytz
from IPython.core.display import display, clear_output
from IPython.core.getipython import get_ipython

from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy._errors import *

DEFAULT_DATASOURCE_NAME = 'Seeq Data Lab'
DEFAULT_DATASOURCE_CLASS = 'Seeq Data Lab'
DEFAULT_DATASOURCE_ID = 'Seeq Data Lab'
DEFAULT_DATASOURCE_DESCRIPTION = 'Signals, conditions and scalars from Seeq Data Lab.'
DEFAULT_WORKBOOK_PATH = 'Data Lab >> Data Lab Analysis'
DEFAULT_WORKBOOK_NAME = DEFAULT_WORKBOOK_PATH.split('>>')[-1].strip()
DEFAULT_WORKBOOK_STATE = '{"version":1, "state":{"stores":{}}}'
DEFAULT_WORKSHEET_NAME = 'From Data Lab'

DATALAB_HOME = '/home/datalab'

# Kept for backwards compatibility. Should match _folder#MY_FOLDER.
PATH_ROOT = '__My_Folder__'

DATASOURCE_MAP_ITEM_LEVEL_MAP_FILES = 'Item-Level Map Files'
DATASOURCE_MAP_REGEX_BASED_MAPS = 'RegEx-Based Maps'

EMPTY_GUID = '00000000-0000-0000-0000-000000000000'
GLOBALS_ONLY = EMPTY_GUID
GLOBALS_AND_ALL_WORKBOOKS = None

JOB_RESULTS_FOLDER_NAME = '_Job Results'
JOB_DATAFRAMES_FOLDER_NAME = '_Job DataFrames'


def present(row, column):
    return (column in row) and not (pd.api.types.is_scalar(row[column]) and pd.isnull(row[column]))


def get(row, column, default=None, assign_default=False):
    """
    Get the value in the column of a row. Can also accept dictionaries.
    Optionally define a default value/type to return and indicate if the
    default should be assigned to the row[column]. For example,

    >>> get(row, column, default=dict(), assign=False)
    if there is no value in row[column] a new dictionary will be returned

    >>> get(row, column, default=dict(), assign=True)
    if there is no value in row[column] a new dictionary will be assigned
    to row column and that dictionary will be returned

    :param row: The row object. Can be pd.Series, a single row pd.DataFrame, or dict
    :param column: The name of the column to query
    :param default: If the no value is present, the return value/type
    :param assign_default: Flag if the default should be assigned to the row[column]
    :return:
    """
    if present(row, column):
        return row[column]
    d = default
    if assign_default:
        row[column] = d
    return d


def get_timings(http_headers):
    output = dict()
    for header, cast in [('Server-Meters', int), ('Server-Timing', float)]:
        server_meters_string = http_headers[header]
        server_meters = server_meters_string.split(',')
        for server_meter_string in server_meters:
            server_meter = server_meter_string.split(';')
            if len(server_meter) < 3:
                continue

            dur_string = cast(server_meter[1].split('=')[1])
            desc_string = server_meter[2].split('=')[1].replace('"', '')

            output[desc_string] = dur_string

    return output


def raise_or_catalog(errors, status=None, df=None, index=None, column=None, e=None, exception_type=None, message=None):
    if message is not None and exception_type is None:
        exception_type = SPyException
    if exception_type is not None:
        e = exception_type(message)
    if e is None:
        _, e, _ = sys.exc_info()
    if status is not None:
        if isinstance(e, KeyboardInterrupt):
            status.df['Result'] = 'Canceled'
        elif index is None:
            status.put('Result', format_exception(e))
        else:
            status.df.at[index, 'Result'] = format_exception(e)
        status.update()
    if df is not None:
        df.at[index, column] = format_exception(e)
    if errors == 'raise':
        if status is not None:
            status.exception(e)
        raise e


def format_exception(e=None):
    exception_type = None
    tb = None
    if e is None:
        exception_type, e, tb = sys.exc_info()

    if isinstance(e, ApiException):
        return get_api_exception_message(e)

    else:
        if tb is not None:
            return '\n'.join(traceback.format_exception(exception_type, e, tb))
        else:
            return '[%s] %s' % (type(e).__name__, str(e))


GUID_REGEX = r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}'
HTML_EQUALS_REGEX = r'(?:=|&#61;)'
HTML_AMPERSAND_REGEX = r'(?:&(?!amp;)|&amp;)'
WORKSHEET_LINK_REGEX = fr'links\?type{HTML_EQUALS_REGEX}workstep{HTML_AMPERSAND_REGEX}' \
                       fr'workbook{HTML_EQUALS_REGEX}({GUID_REGEX}){HTML_AMPERSAND_REGEX}' \
                       fr'worksheet{HTML_EQUALS_REGEX}({GUID_REGEX}){HTML_AMPERSAND_REGEX}'
WORKSTEP_LINK_REGEX = fr'{WORKSHEET_LINK_REGEX}workstep{HTML_EQUALS_REGEX}({GUID_REGEX})'
UUID_LENGTH = 36


def is_guid(s):
    """
    Determine if a string is a GUID/UUID

    Parameters
    ----------
    s : str
        The string to be tested

    Returns
    -------
    bool
        True if the string is a GUID/UUID, False otherwise
    """
    return isinstance(s, str) and len(s) == UUID_LENGTH and re.match(GUID_REGEX, sanitize_guid(s)) is not None


def sanitize_guid(g):
    return g.upper()


def new_placeholder_guid():
    return str(uuid.uuid4()).upper()


def validate_timezone_arg(tz):
    if tz is not None:
        try:
            pd.to_datetime('2019-01-01T00:00:00.000Z').tz_convert(tz)

        except pytz.exceptions.UnknownTimeZoneError:
            raise SPyValueError('Unknown timezone "%s". Acceptable timezones:\n%s' %
                                (tz, '\n'.join(pytz.all_timezones)))


def validate_errors_arg(errors):
    if errors not in ['raise', 'catalog']:
        raise SPyValueError("errors argument must be either 'raise' or 'catalog'")


def validate_unique_dataframe_index(df: Optional[pd.DataFrame], var_name: str):
    if not isinstance(df, pd.DataFrame):
        return

    if not df.index.is_unique:
        raise SPyValueError(f"The {var_name} DataFrame's index must be unique. Use reset_index(drop=True, "
                            "inplace=True) before passing it in.")


def time_abbreviation_to_ms_multiplier(abbreviation):
    """
    Given a time abbreviation, returns a multiplier that converts the time
    value to ms and the canonical version of that time abbreviation.
    For example, "6 sec", pass the "sec" to this function and it will
    return (1000, 's'). Multiplying 6 by 1000 gives the duration in ms.

    Parameters
    ----------
    abbreviation : str
        The time abbreviation.  Acceptable values are:
        s, sec, second, seconds
        min, minute, minutes
        h, hr, hour, hours
        d, day, days
        w, wk, wks, week, weeks
        m, mo, month, months
        y, yr, yrs, year, years

    Returns
    -------
    (int, str)
        The multiplier to convert from the time basis to ms and the canonical
        version of the unit
    """
    abv = get_time_abbreviation(abbreviation)

    return get_abbreviation_multiplier_map()[abv], abv


def get_time_abbreviation(abbreviation):
    abv = abbreviation.lower()
    if abv in ['s', 'sec', 'second', 'seconds']:
        return 's'
    if abv in ['m', 'min', 'minute', 'minutes']:
        return 'min'
    if abv in ['h', 'hr', 'hour', 'hours']:
        return 'h'
    if abv in ['d', 'day', 'days']:
        return 'day'
    if abv in ['w', 'wk', 'wks', 'week', 'weeks']:
        return 'week'
    if abv in ['m', 'mo', 'month', 'months']:
        return 'month'
    if abv in ['y', 'yr', 'yrs', 'year', 'years']:
        return 'year'

    raise SPyValueError(f'Unrecognized time abbreviation "{abv}". Valid abbreviations: "sec", "min", "hr", "day", '
                        f'"wk", "mo", "yr"')


def get_abbreviation_multiplier_map():
    return {
        's': 1000,
        'min': 60000,
        'h': 3.6e6,
        'day': 8.64e7,
        'week': 6.048e8,
        'month': 2.628e9,
        'year': 3.154e10
    }


def parse_str_time_to_ms(str_time):
    """
    Given a string time like 5min, 3hr, 2d, 7mo, etc, get the numeric and unit
    portions and calculate the number of milliseconds. Time units will be
    converted to the Seeq canonical versions, eg, 'sec' will yield 's'
    :param str_time: A string representing a time. Eg, 3min
    :return: tuple (numeric portion, string unit, milliseconds)
    For example '5min' returns (5, 'min', 300000)
    """
    match = re.match(r'([+-]?[\d.]+)\s*(\w+)', str_time)
    if not match:
        raise SPyValueError('Duration string not parseable: "%s"' % str_time)

    value = float(match.group(1))
    unit = match.group(2)
    multiplier, unit_name = time_abbreviation_to_ms_multiplier(unit)
    return value, unit_name, value * multiplier


def parse_str_time_to_timedelta(str_time):
    _, _, milliseconds = parse_str_time_to_ms(str_time)
    return datetime.timedelta(milliseconds=milliseconds)


def test_and_set(target, target_key, source, source_key, apply_func=None, default_value=None, retain_target=True):
    """
    If the source has source_key and it's not NaN, set it as the value for target[target_key]

    Optionally, apply a function to the value in source[source_key]. Must be a function that
    takes a single input, such as lambda x: str.lower( x) or lambda x: str.upper(x) or

    Optionally, set a default input for target[target_key] if source[source_key] is NaN. Note that
    the default is only applied if source_key is in source, but the source value is NaN

    Parameters
    ----------
    target : dict
        The dictionary that the value is to be inserted into
    target_key : str
        The key in target for the value
    source : dict
        The source dictionary
    source_key : str
        The key in the source dict to look for the value
    apply_func : function
        A function to apply to the source[source_key] value, if it's not NaN
    default_value : obj
        If source[source_key] is NaN, the value for target[target_key]. See "retain_default" for
        additional functionality
    retain_target : bool
        If true and source_key not in source, do not assign the default - retain the current target value
        If false and source_key not in source, overwrite the current target value with the default
    """
    if source_key in source:
        if pd.notna(source[source_key]):
            if apply_func is not None:
                target[target_key] = next(map(apply_func, [source[source_key]]))
            else:
                target[target_key] = source[source_key]
            return
        elif default_value is not None:
            target[target_key] = default_value
        return
    elif not retain_target:
        target[target_key] = default_value


def validate_argument_types(expected_types):
    for _value, _name, _types in expected_types:
        if _value is None:
            continue

        if not isinstance(_value, _types):
            if isinstance(_types, tuple):
                acceptable_types = ' or '.join([_t.__name__ for _t in _types])
            else:
                acceptable_types = _types.__name__

            raise SPyTypeError("Argument '%s' should be type %s, but is type %s" % (_name, acceptable_types,
                                                                                    type(_value).__name__))

    return {_name: _value for _value, _name, _types in expected_types}


def none_to_nan(v):
    return np.nan if v is None else v


def ensure_unicode(o):
    if isinstance(o, bytes):
        return str(o, 'utf-8', errors='replace')
    else:
        return o


def timer_start():
    return datetime.datetime.now()


def timer_elapsed(timer):
    return datetime.datetime.now() - timer


def convert_to_timestamp(unix_timestamp_in_ns, tz):
    return convert_timestamp_timezone(none_to_nan(pd.Timestamp(unix_timestamp_in_ns)), tz)


def convert_timestamp_timezone(timestamp, tz):
    if pd.isna(timestamp):
        return timestamp

    timestamp = timestamp.tz_localize('UTC')
    return timestamp.tz_convert(tz) if tz else timestamp


def display_supports_html():
    # noinspection PyBroadException
    try:
        # noinspection PyUnresolvedReferences
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str:
            return True
        if 'terminal' in ipy_str:
            return False

    except BaseException:
        return False


def ipython_clear_output(wait=False):
    clear_output(wait)


def ipython_display(*objs, include=None, exclude=None, metadata=None, transient=None, display_id=None, **kwargs):
    display(*objs, include=include, exclude=exclude, metadata=metadata, transient=transient,
            display_id=display_id, **kwargs)


def get_data_lab_datasource_input():
    datasource_input = DatasourceInputV1()
    datasource_input.name = DEFAULT_DATASOURCE_CLASS
    datasource_input.description = DEFAULT_DATASOURCE_DESCRIPTION
    datasource_input.datasource_class = DEFAULT_DATASOURCE_CLASS
    datasource_input.datasource_id = DEFAULT_DATASOURCE_ID
    datasource_input.stored_in_seeq = True
    datasource_input.additional_properties = [ScalarPropertyV1(name='Expect Duplicates During Indexing', value=True)]
    return datasource_input


def regex_from_query_fragment(query_fragment, contains=True):
    if query_fragment.startswith('/') and query_fragment.endswith('/'):
        regex = query_fragment[1:-1]
    else:
        regex = re.escape(query_fragment).replace(r'\?', '.').replace(r'\*', '.*')

        if contains and not regex.startswith('.*') and not regex.endswith('.*'):
            regex = '.*' + regex + '.*'

    return regex


CONSPICUOUS_TOKEN_REPRESENTING_A_SPACE = '>>>>>!SPACE!<<<<<'


def escape_regex(pattern):
    # re.escape() adds escapes to spaces, which makes for ugly Datasource Maps. We don't need spaces escaped because
    # we're not going to be dealing with verbose RegExes.
    # See https://stackoverflow.com/questions/32419837/why-re-escape-escapes-space
    pattern = pattern.replace(' ', CONSPICUOUS_TOKEN_REPRESENTING_A_SPACE)

    pattern = re.escape(pattern)

    pattern = pattern.replace(CONSPICUOUS_TOKEN_REPRESENTING_A_SPACE, ' ')

    return pattern


def get_signal_rollup_function_map():
    return {
        'average': 'average',
        'maximum': 'max',
        'minimum': 'min',
        'sum': 'sum'
    }


class RollUpFunction:
    def __init__(self, statistic, function, input_type, output_type, style):
        self.statistic = statistic
        self.function = function
        self.input_type = input_type
        self.output_type = output_type
        self.style = style


ROLL_UP_FUNCTIONS = [
    # Conditions
    RollUpFunction('union', 'union', 'Condition', 'Condition', 'union'),
    RollUpFunction('intersect', 'intersect', 'Condition', 'Condition', 'intersect'),
    RollUpFunction('counts', 'countOverlaps', 'Condition', 'Signal', 'vararg'),
    RollUpFunction('count overlaps', 'countOverlaps', 'Condition', 'Signal', 'vararg'),
    RollUpFunction('combine with', 'combineWith', 'Condition', 'Condition', 'vararg'),

    # Signals
    RollUpFunction('average', 'average', 'Signal', 'Signal', 'vararg'),
    RollUpFunction('maximum', 'max', 'Signal', 'Signal', 'fluent'),
    RollUpFunction('minimum', 'min', 'Signal', 'Signal', 'fluent'),
    RollUpFunction('range', 'range', 'Signal', 'Signal', 'vararg'),
    RollUpFunction('sum', 'add', 'Signal', 'Signal', 'vararg'),
    RollUpFunction('multiply', 'multiply', 'Signal', 'Signal', 'vararg'),

    # Scalars
    RollUpFunction('average', 'average', 'Scalar', 'Scalar', 'vararg'),
    RollUpFunction('maximum', 'max', 'Scalar', 'Scalar', 'fluent'),
    RollUpFunction('minimum', 'min', 'Scalar', 'Scalar', 'fluent'),
    RollUpFunction('range', 'range', 'Scalar', 'Scalar', 'vararg'),
    RollUpFunction('sum', 'add', 'Scalar', 'Scalar', 'vararg'),
    RollUpFunction('multiply', 'multiply', 'Scalar', 'Scalar', 'vararg')
]


def get_signal_statistic_function_map():
    return {
        'average': 'average',
        'count': 'count',
        'delta': 'delta',
        'maximum': 'maxValue',
        'median': 'median',
        'minimum': 'minValue',
        'percentile': 'percentile',
        'range': 'range',
        'rate': 'rate',
        'standard deviation': 'stddev',
        'sum': 'sum',
        'totalized': 'totalized',
        'value at end': 'endValue',
        'value at start': 'startValue'
    }


def get_variable_number_statistic_function(statistic):
    match = re.match(r'^\w+\(([0-9]*.?[0-9]+|[0-9]+|[0-9]+.?[0-9]*)\)$', statistic)
    # matches numbers with decimal at beginning, end, or within
    if match is not None:
        # in Seeq, percentiles must be in the closed interval [0, 100].
        if 0 <= float(match.group(1)) <= 100:
            return statistic


def get_variable_time_unit_statistic_function(statistic):
    if re.match(r'^[\w ]+(\([\'"](s|min|h|day)[\'"]\))?$', statistic) is not None:
        return re.sub("'", '"', statistic)


def make_camel_case(string_, leading_upper=False):
    """
    Finds spaces or underscores and removes them, making the following letter
    upper case. If leading_upper=True, the first letter of the word will be
    made upper case too.

    leading_upper = False examples:
    "total duration" -> "totalDuration"
    "total_duration" -> "totalDuration"

    leading_upper = True examples:
    "total duration" -> "TotalDuration"
    "total_duration" -> "TotalDuration"
    """

    def camel(match):
        return match.group(1) + match.group(2).upper()

    snake_re = '(.*?)[_ ]([a-zA-Z])'
    new_string_ = re.sub(snake_re, camel, string_)
    return new_string_ if not leading_upper else new_string_[0].upper() + new_string_[1:]


def get_condition_statistic_function_map():
    return {
        'count ends': 'countEnds',
        'count starts': 'countStarts',
        'percent duration': 'percentDuration',
        'total duration': 'totalDuration'
    }


def statistic_to_aggregation_function(statistic, *, allow_condition_stats=True):
    statistic = statistic.lower()
    fns = get_signal_statistic_function_map()

    if allow_condition_stats:
        fns.update(get_condition_statistic_function_map())

    if 'percentile' in statistic and get_variable_number_statistic_function(statistic) is not None:
        return make_camel_case(get_variable_number_statistic_function(statistic))
    elif any([s in statistic for s in ['rate', 'total duration']]) and \
            get_variable_time_unit_statistic_function(statistic) is not None:
        return make_camel_case(get_variable_time_unit_statistic_function(statistic))
    elif statistic not in fns:
        raise SPyValueError('Statistic "%s" not recognized. Valid statistics:\n%s.\nNote that Rate can have '
                            'conversion keys of "s", "min", "h", or "day", eg, \'Rate("min")\', and Percentile '
                            'requires a number to specify the desired percentile, eg, "Percentile(25)"' %
                            (statistic.capitalize(), '\n'.join([string.capwords(s) for s in fns.keys()])))

    return fns[statistic] + '()'


def does_query_fragment_match(query_fragment, _string, contains=True):
    regex = regex_from_query_fragment(query_fragment, contains=contains)
    match = re.fullmatch(regex, _string, re.IGNORECASE)
    return match is not None


def get_workbook_type(arg):
    data: Optional[str] = None
    if isinstance(arg, WorkbookOutputV1):
        if arg.type in ['Analysis', 'Topic']:
            return arg.type

        if hasattr(arg, 'data'):
            data = arg.data
    else:
        data = arg

    if not data:
        return 'Analysis'

    if not isinstance(data, dict):
        # noinspection PyBroadException
        try:
            data = json.loads(data)
        except BaseException:
            return 'Analysis'

    if 'isReportBinder' in data and data['isReportBinder']:
        return 'Topic'
    else:
        return 'Analysis'


def safe_json_dumps(dictionary):
    if dictionary is None:
        return None

    def _nan_to_none(v):
        return None if isinstance(v, float) and np.isnan(v) else v

    def _nan_to_none_in_dict(d):
        d = d.copy()
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = _nan_to_none_in_dict(v)
            elif isinstance(v, list):
                d[k] = [_nan_to_none_in_dict(i) if isinstance(i, dict) else _nan_to_none(i) for i in v]
            else:
                d[k] = _nan_to_none(v)

        return d

    clean_dict = _nan_to_none_in_dict(dictionary)

    return json.dumps(clean_dict, skipkeys=True, allow_nan=False, indent=2, default=lambda o: '<not serializable>')


def path_string_to_list(path_string):
    return re.split(r'\s*>>\s*', path_string.strip())


def path_list_to_string(path_list):
    return ' >> '.join(path_list)


def sanitize_path_string(path):
    return path_list_to_string(path_string_to_list(path))


def string_to_formula_literal(s):
    if not isinstance(s, str):
        raise ValueError('Argument must be a string')

    s = re.sub(r"(['\\])", r"\\\1", s)
    return f"'{s}'"


def get_image_file(workbook_folder, image_id_tuple):
    return os.path.join(workbook_folder, 'Image_%s_%s' % image_id_tuple)


def save_image_files(image_dict: dict, folder: str):
    for image_id_tuple, content in image_dict.items():
        image_file = get_image_file(folder, image_id_tuple)
        with open(image_file, 'wb') as f:
            f.write(content)


def get_html_attr(fragment, attribute):
    attr_match = re.findall(r'\s+%s="(.*?)"' % attribute, fragment)
    return attr_match[0] if len(attr_match) > 0 else None


DATAFRAME_METADATA_CONTAINER_NAME = 'spy'


def put_properties_on_df(output_df, properties):
    """
    Adds the specified properties as metadata on output_df, under the "spy" attribute.

    Parameters
    ----------
    output_df : DataFrame
        DataFrame to which the properties will be attached. Typically, this is
        the output DataFrame of 'spy.search()' or 'spy.pull()'
    properties : types.SimpleNamespace
        Properties that will be added to the output_df.

    Returns
    -------
    {DataFrame}
        Original output_df, but now with the properties in "spy" attribute
    """
    if not isinstance(properties, types.SimpleNamespace):
        raise TypeError('properties argument must be a types.SimpleNamespace object')

    with pywarnings.catch_warnings():
        pywarnings.simplefilter('ignore', UserWarning)
        # Pandas issues a UserWarning in case the user is trying to add columns to the DataFrame as attributes which
        # is not allowed. We are not trying to add columns here though, it's a normal property

        setattr(output_df, DATAFRAME_METADATA_CONTAINER_NAME, properties)
        # noinspection PyProtectedMember
        if DATAFRAME_METADATA_CONTAINER_NAME not in output_df._metadata:
            # noinspection PyProtectedMember
            output_df._metadata.append(DATAFRAME_METADATA_CONTAINER_NAME)


def clear_properties_on_df(output_df):
    if hasattr(output_df, DATAFRAME_METADATA_CONTAINER_NAME):
        # noinspection PyBroadException
        try:
            delattr(output_df, DATAFRAME_METADATA_CONTAINER_NAME)
        except BaseException:
            pass
