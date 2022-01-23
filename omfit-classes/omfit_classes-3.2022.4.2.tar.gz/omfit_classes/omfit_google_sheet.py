"""
Tools for interfacing with Google sheets

Compared to SQL tables, Google sheets allow for formatting and other conveniences
that make them easier to update by hand (appropriate for some columns like labels,
comments, etc.), but the API for Google sheets is relatively simple. This file
is meant to provide tools for looking up data by column header instead of column
number/letter and by shot instead of row number. That is, the user should not have
to know which row holds shot 123456 or which column holds density in order to get
the average density for shot 123456.

In this script, the purely numeric way to refer to cell 'A1' is (0, 0). Do not
allow any reference  to A1 as (1, 1) to creep into this code or it will ruin
everything. Referring to ('A', 1) is fine; there's a function for interpreting
cell references, but it uses the presence of a letter in the column as a cue that
the row should be counted from 1, so it can't handle counting columns from 1.
Some packages DO use numbers (from 1) instead of indices (from 0) internally. If
one of these packages is used, its returned values must be converted immediately.
YOU WON'T LIKE WHAT HAPPENS IF YOU FAIL TO MAINTAIN THIS DISCIPLINE.
"""

# OMFIT imports
try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

# Basic imports
import copy
import string
import numpy as np
import matplotlib
import re

# OMFIT class imports
from omfit_classes.omfit_mds import OMFITmdsValue
from omfit_classes.omfit_base import OMFITtmp, OMFITtree

# Import modules for interfacing with google sheets
try:
    # This is an optional dependency. If it isn't installed, we can't do much except
    # explain the problem.
    import pygsheets
except ImportError:
    pygsheets = None


setup_help = '''
How to prepare a Google Sheet for use with these tools:
-------------------------------------------------------
Most of these steps are described with screen shots in the pygsheets documentation
(use the service account version):
https://pygsheets.readthedocs.io/en/stable/authorization.html

1: Make a sheet in Google drive
2: Make a project at https://console.developers.google.com/
3: Add and enable both Google drive API and Google sheets API
4: Add credentials: create credentials for a service account. Give it the Project: editor role.
5. Add a JSON key to the service account, download it, and place it somewhere accessible to this script.
6: Note the service account's email address (the form is <SERVICE-NAME>@<PROJECT>.iam.gserviceaccount.com)
7: Share the sheet with the service account using the email address it gets (ending in iam.gserviceaccount.com)

Connection should then be possible if OMFITgoogleSheet or subclass is initialized
with the right keyfile and sheet_name.
'''

__all__ = ['OMFITgoogleSheet', 'OMFITexperimentTable']


# List of column letters (A, B, ... Z, AA, AB, ... AZ, BA, ... ZZ)
string_ascii_uppercase = list(map(chr, range(ord('A'), ord('Z') + 1)))
col_letters = [] + string_ascii_uppercase
for first_letter in string_ascii_uppercase:
    for second_letter in string_ascii_uppercase:
        col_letters.append(first_letter + second_letter)


def interpret_row_col(*args):
    """
    Interprets row number and column name or row index and column index and returns indices

    Either provide row number and column letter as in google sheet as in args = ('A', 1) or args = ('A1', )
    or provide the row and column indices starting from 0 as in args = (0, 0).

    That is, give the input the way google displays it or the way python tracks it internally. No mixing.

    Large column letters, like AA, AB, CX, etc. are supported up to ZZ.

    This function is useful because we are dealing with a mixture of methods that try to index arrays from 0 and
    methods that try to communicate with the spreadsheet and its cell addresses. It is very convenient to hand this
    thing a valid address from some source and let it figure out how to interpret it. Just make sure you DO NOT let
    cell references like (1, 1) for A1 into the code. Convert them on the way in into (0, 0) or ('A', 1).

    :param args: One or two input arguments.
        One argument should be an address like 'A1'
        Two arguments should be a column followed by a row.
            If the column is int, both it and the row as interpreted as indices starting from 0.
            If the column is in the list of recognized column letters (A, B, ... ZZ), the row is interpreted as a
                row number, starting from 1.
            So, args of (0, 0), ('A', 1) and 'A1' all mean the same thing.

    :return: (int, int, str)
        (column_index, row_index, address)
        The indices start from 0 and the address.
    """

    # Assign the input arguments to column, row, and address_in
    if len(args) == 1:
        address_in = args[0]
        column, row = re.findall(r'[A-Za-z]+|\d+', address_in)  # https://stackoverflow.com/a/28290501/6605826
        row = int(row)
    elif len(args) == 2:
        address_in = None
        column, row = args[0:2]
    else:
        raise ValueError('Too many arguments')

    # Decide what the indices for column and row are based on what's been given
    if isinstance(column, int):
        column_index = column
        row_index = int(row)
    elif column in col_letters:
        row_index = int(row) - 1
        column_index = int(np.where(col_letters == np.array(column))[0][0])
    else:
        raise ValueError(f'Could not understand column index {column}')

    # Check and then return results
    address = f'{col_letters[column_index]}{row_index+1}'
    if address_in is not None:
        assert address_in == address, 'Did not recover the right address'
    assert row_index >= 0, 'Row index must not be negative.'
    return column_index, row_index, address


def list_to_array_type(list_in, type_out=None, fill_value=np.NaN, int_truncation_allowed=False):
    """
    Forces a list to be an array with a specified type.

    Values that can't be forced to the type are replaced with a fill_value.
    Special: can be set to consider floats like 5.2 to be unrepresentable as ints instead of truncating them.

    :param list_in: list
        These would normally be the values read from a column or row.
        If formatted values are obtained, they will be strings, even if the strings just hold numbers.

    :param type_out: type
        This is just the type you would like each element to be in the output.

    :param fill_value: object matching type_out
        Elements that can't be forced to type_out will be replaced with this.

    :param int_truncation_allowed: bool
        Allow floats to be cast as int by truncation, so 26.945 becomes 26 instead of fill_value

    :return: array matching type_out
    """
    numeric_types = [int, float, complex]

    type_out = type_out or float
    try:
        type_out(fill_value)
    except Exception as excp:
        raise excp.__class__(f'fill_value {fill_value} is inconsistent with type_out {type_out}!')

    def try_type(x):
        """Tries to force x to be type and returns it; returns fill_value on failure"""
        # noinspection PyBroadException
        try:
            if type_out in numeric_types:
                the_thing = type_out(float(x))
            else:
                the_thing = type_out(x)
        except Exception as exc:
            printd(f'      failed to cast {type_out}({x}) because {exc}')
            return type_out(fill_value)
        else:
            if (not int_truncation_allowed) and (type_out == int) and (float(x) != the_thing):
                printd(f'    Casting to int would change {x} to {the_thing} and is not allowed. FAIL!')
                return type_out(fill_value)
            else:
                return the_thing

    # fromiter : https://stackoverflow.com/a/28526475/6605826
    return np.fromiter(map(try_type, list_in), type_out)


def operate_on_data(data, operation):
    """
    Handles mean/median/etc. operations for clients such as OMFITexperimentTable(...).write_mds_data_to_table()

    :param data: 1D float array
        Data to process

    :param operation: str
        Description of operation

    :return: float
        Result of operation on data
    """
    if operation == 'mean':
        value = np.nanmean(data)
    elif operation == 'median':
        value = np.nanmedian(data)
    elif operation == 'max':
        value = np.nanmax(data)
    elif operation == 'min':
        value = np.nanmin(data)
    else:
        raise ValueError(f'Unrecognized operation passed to operate_on_data(): {operation}')
    return value


def get_definition_from_docstring(theobject, return_kw=False):
    """
    Reads example code from the docstring of a class or function and uses it to define some variables

    :param theobject: class or function
        The docstring should contain statements like '>> the_variable = the_value'.
        They can be multi-line.
        Each statement should be separated from others by lines not starting with >> .

    :param return_kw: bool
        Instead of evaluating expressions as written (e.g. var = ClassName(**kw)),
        replace class or method name with dict and append _kw to var, to instead get
        var_kw = dict(**kw). This will fail if the statements in the docstring aren't
        don't follow the form a = b(keywords=values, keywords2=values2, ...).

    :return: dict
        Keys are the variables being defined (on the left side of the first =)
        Values are evaluated expressions taken from the right side of the first =.
    """
    fn_doc = theobject.__doc__.split('\n')
    is_example = np.array([doc_line.strip().startswith('>> ') for doc_line in fn_doc])
    exmp_changes = np.append(0, np.diff(is_example.astype(int)))
    starts = np.where(exmp_changes == 1)[0]
    ends = np.where(exmp_changes == -1)[0]
    docstring_definitions = {}
    for start, end in zip(starts, ends):
        var_name = fn_doc[start].split('=')[0].strip().split('>> ')[1]
        def_start = '='.join(fn_doc[start].split('=')[1:]).strip()
        def_rest = [d.split('>> ')[1] for d in fn_doc[start + 1 : end]]
        definition = '\n'.join([def_start] + def_rest)
        if return_kw:
            # noinspection PyBroadException
            try:
                class_or_func_name = definition.split('(')[0]
                replaced_with_dict = 'dict' + definition[len(class_or_func_name) :]
                docstring_definitions[var_name + '_kw'] = eval(replaced_with_dict)
            except Exception:
                docstring_definitions[var_name + '_kw'] = None
        else:
            docstring_definitions[var_name] = eval(definition)
    return docstring_definitions


class OMFITgoogleSheetSetupError(ValueError):
    pass


class OMFITgoogleSheetBadKeyfileError(OMFITgoogleSheetSetupError):
    pass


class OMFITexperimentTableSetupError(OMFITgoogleSheetSetupError):
    pass


class OMFITgoogleSheet(OMFITtree):
    """
    Connects to Google sheets and provides some convenience features

    * Lookup columns by column header name instead of column number

    * Local caching to allow repeated read operations without too many connections to the remote sheet.

    * Throttle to avoid throwing an exception due to hitting Google's rate limiter,
      or pygsheet's heavy-handed rate limit obedience protocol.

    An example sheet that is compatible with the assumptions made by this class may be found here:
    https://docs.google.com/spreadsheets/d/1MJ8cFjFZ2pkt4OHWWIciWT3sM2hSADqzG78NDiqKgkU/edit?usp=sharing

    A sample call that should work to start up an OMFITgoogleSheet instance is:
    >> gsheet = OMFITgoogleSheet(
    >>     keyfile=os.sep.join([OMFITsrc, '..', 'samples', 'omfit-test-gsheet_key.json']),
    >>     sheet_name='OmfitDataSheetTestsheet',
    >>     subsheet_name='Sheet1',  # Default: lookup first subsheet
    >>     column_header_row_idx=5,  # Default: try to guess
    >>     units_row_idx=6,  # Default: None
    >>     data_start_row_idx=7,  # Default: header row + 1 (no units row) or + 2 (if units row specified)
    >> )
    This call should connect to the example sheet. This is more than an example; this is a functional call
    that is read out of the docstring by the regression test and testing will fail if it doesn't work properly.
    """

    def __init__(
        self,
        filename='',
        keyfile=None,
        sheet_name=None,
        subsheet_name=None,
        column_header_row_idx=None,
        column_header_row_number=None,
        units_row_idx=None,
        units_row_number=None,
        data_start_row_idx=None,
        data_start_row_number=None,
        **kw,
    ):
        """
        :param filename: str
            Not used, but apparently required when subclassing from OMFITtree.

        :param keyfile: str or dict-like
            Filename with path of the file with authentication information,
            or dict-like object with the parsed file contents (OMFITjson should work well).
            See setup_help for help setting this up.

        :param sheet_name: str
            Name of the Google sheets file/object/whatever to access

        :param subsheet_name: str
            Sheet within the sheet (the tabs at the bottom). Defaults to the first tab.

        :param column_header_row_idx: int
            Index (from 0) of the row with column headers. If not specified, we will try to guess for you.
            Indices like this are stored internally.

        :param column_header_row_number: int
            Number (from 1) of the row with column headers, as it appears in the sheet.
            Ignored if column_header_row_idx is specified. If neither is specified, we will try to guess for you.
            This will be converted into an index (from 0) for internal use.

        :param units_row_idx: int or None
            Index (from 0) of the row with the units, if there is one, or None if there isn't a row for units.

        :param units_row_number: int or None
            Number (from 1) of the units row. See description of column_header_row_number.

        :param data_start_row_idx: int
            Index (from 0) of the row where data start.
            Defaults to column_header_row + 1 if units_row is None or +2 if units_row is not None.

        :param data_start_row_idx: int
            Number (from 1) of the first row of data after the header.
            See description of column_header_row_number.

        :param kw: additional keywords passed to super class's __init__
        """
        self.OMFITproperties = {}
        super().__init__(filename=filename, **kw)

        # Make a scratch space for objects that don't need to be / can't be saved
        self['scratch'] = OMFITtmp()
        self['scratch']['client'] = None
        self['scratch']['sheet_connection'] = None

        # Cache setup
        self['__cache__'] = OMFITtmp()
        self['cache_expiration'] = 30  # seconds

        # Throttle setup
        self['previous_write_times'] = np.array([])
        self['throttle_interval_s'] = 100.0
        self['throttle_requests_in_interval'] = 100

        # Interpret input keywords
        self['keyfile'] = keyfile
        self['sheet_name'] = sheet_name
        self['subsheet_name'] = subsheet_name
        if column_header_row_idx is None and column_header_row_number is not None:
            column_header_row_idx = column_header_row_number - 1
        self['column_header_row'] = column_header_row_idx
        if units_row_idx is None and units_row_number is not None:
            units_row_idx = units_row_number - 1
        self['units_row'] = units_row_idx
        if data_start_row_idx is None and data_start_row_number is not None:
            data_start_row_idx = data_start_row_number - 1
        self['data_start_row'] = data_start_row_idx

    def __tree_repr__(self):
        if pygsheets is None:
            return 'Import failed: pygsheets. No connection possible.', []
        if isinstance(self['scratch'].get('sheet_connection', None), pygsheets.Worksheet):
            connection_status = 'connected'
        else:
            connection_status = '(NOT connected)'
        subsheet = self.get('subsheet_name', None)
        if subsheet is None:
            subsheet = 'TBD'
        description = (
            f"{self.get('sheet_name', '')}/{subsheet} {connection_status} "
            f"{self['column_header_row']}|{self['units_row']}|{self['data_start_row']}"
        )
        return description, []

    def __call__(self):
        """This seems like a useful thing to do"""
        self.connect()

    def record_request(self):
        """Logs a request to the Google API so the rate can be avoided by local throttling"""
        self['previous_write_times'] = np.append(self['previous_write_times'], time.time())

    def self_check(self, essential_only=False):
        """
        Makes sure setup is acceptable and raises AssertionError otherwise

        :param essential_only: bool
            Skip checks that aren't essential to initializing the class and its connection.
            This avoids spamming warnings about stuff that might get resolved later in setup.
        """
        problems = []
        issues = []

        # noinspection PyBroadException
        try:
            # Essential checks
            if self['keyfile'] is None:
                problems += ['keyfile missing: Need filename (with path) of the key for accessing Google sheets.']
            if self['sheet_name'] is None:
                problems += ['sheet_name missing: Please specify the name of the sheet to access.']

            # More checks
            if not essential_only:
                if self['column_header_row'] is None:
                    issues += ['column_header_row missing: required for most operations.']
        except Exception as excp:
            problems += [f'Encountered exception while trying to check stuff: {excp}']
        # Report problems
        if len(issues):
            fissues = '\n'.join(issues)
            print(f'Warning: there were {len(issues)} issues that may prevent full functionality:\n{fissues}')
        fproblems = '\n'.join(problems)
        if problems:
            self.help()
        assert len(problems) == 0, f'There were some setup problems:\n{fproblems}'

    def authorize_client(self):
        """
        Deal with keyfile being allowed to be either a string or a dict-like

        :return: pygsheets.client.Client instance
        """
        if is_string(self['keyfile']):
            return pygsheets.authorize(service_account_file=self['keyfile'])
        elif isinstance(self['keyfile'], dict):
            from google.oauth2 import service_account

            clean_keyfile = dict(self['keyfile'])  # Things get weird if keyfile is an OMFITjson; simplify to dict
            scopes = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
            creds = service_account.Credentials.from_service_account_info(clean_keyfile, scopes=scopes)
            return pygsheets.authorize(custom_credentials=creds)
        else:
            raise OMFITgoogleSheetBadKeyfileError(
                f"Could not use keyfile of type {type(self['keyfile'])}; should be either a str or dict-like"
            )

    def connect(self, attempt=0):
        """Establishes connection to google sheet"""
        self.self_check(essential_only=True)

        if pygsheets is None:
            exc = AssertionError("Failed to import required packages: can't connect to google.")
            self['scratch']['sheet_connection'] = exc
            printe('Unable to connect because of missing packages')
            return

        print('Connecting to google sheets...')
        try:
            self['scratch']['client'] = self.authorize_client()
            # .open() here is not the same as file.open(). Do not put in `with`.
            opened_client = self['scratch']['client'].open(self['sheet_name'])
            self['subsheet_name'] = self['subsheet_name'] or opened_client.worksheets()[0].title
            self['scratch']['sheet_connection'] = (
                self['scratch']['client'].open(self['sheet_name']).worksheet_by_title(self['subsheet_name'])
            )
        except Exception as exc:
            self['scratch']['sheet_connection'] = exc
            if attempt < 1:
                wait_time = 2.0
                printw(f'First attempt to connect failed; waiting {wait_time} seconds and trying again. ({exc})')
                time.sleep(wait_time)
                self.connect(attempt=attempt + 1)
            else:
                printe(f'Failed to connect ({exc})')
                self['scratch']['sheet_connection'] = exc
        else:
            self.record_request()
            self.post_connect()

    def sheet_connection(self):
        """
        Attempt to connect on demand and return a Worksheet object

        :return: Worksheet instance
        """
        if self['scratch'].get('sheet_connection', None) is None:
            self.connect()
        return self['scratch'].get('sheet_connection', None)

    def post_connect(self):
        """Fill in some handy information; usually desired after connecting"""
        if self['column_header_row'] is None:
            self.guess_header_row()
        default_data_row = self['column_header_row'] + 1 + (self['units_row'] is not None)
        self['data_start_row'] = self['data_start_row'] or default_data_row
        self.get_columns()

    @staticmethod
    def help():
        """Prints help"""
        print(setup_help)

    def direct_write(self, value, *args):
        """
        Writes data to a single cell in the remote sheet

        :param value: numeric or string
            This will be written to the cell

        :param args: address information, such as (column, row) or address string.
            Examples: ('A', 1), (0, 0), 'A1'.
            See interpret_row_col() for more information about how to specify row and column.
        """
        from omas.omas_core import force_imas_type

        column_index, row_index, address = interpret_row_col(*args)
        self.sheet_connection().update_value(address, force_imas_type(value))
        self.record_request()
        self['__cache__']['changed'] = True

    def direct_read(self, *args, formatted=False):
        """
        Reads data from a single cell in the remote sheet

        :param args: passed to interpret_row_col
            Provide address information here, like ('A', 1), (0, 0), or 'A1'

        :param formatted: bool
            Get the formatted value (floats will be rounded according to sheet display settings)

        :return: str or number
            If formatted = True: str
                Might contain something that can be trivial cast as int or float, but it's always in a string
            If formatted = False: str or number
                With formatting off, numbers may be returned
        """
        column_index, row_index, address = interpret_row_col(*args)
        self.obey_rate_limit()
        cell = self.sheet_connection().cell(address)
        self.record_request()
        if formatted:
            return cell.value
        else:
            return cell.value_unformatted

    def time_until_throttle_okay(self):
        """Checks history of previous requests and decides how long we must wait before making a new request"""
        # pygsheets has a seconds_per_quota setting, but all it does is wait that long if it hits an exception.
        # It won't be smart and figure out that you only have to wait N seconds to be under the rate again.
        t0 = time.time()
        self['scratch']['t0'] = t0
        recent_requests = np.sum((t0 - self['previous_write_times']) < self['throttle_interval_s'])
        if recent_requests < self['throttle_requests_in_interval']:
            printd(f'Number of recent requests is only {recent_requests}, so there is no need to wait.')
            wait_time = 0
        else:
            while np.max((t0 - self['previous_write_times']) - self['throttle_interval_s']) > 0:
                # Remove old values that are past timeout
                self['previous_write_times'] = self['previous_write_times'][1:]
            # How long did that stuff take? I don't know, let's update t0 just in case we wasted time
            t0 = time.time()
            since = t0 - self['previous_write_times']
            since_interval = since - self['throttle_interval_s']
            possible_wait_times = np.arange(self['throttle_interval_s'] + 1)
            since_interval_after_wait = since_interval[:, np.newaxis] + possible_wait_times[np.newaxis, :]
            in_interval_after_wait = np.sum(since_interval_after_wait <= 0, axis=0)
            acceptable = in_interval_after_wait < self['throttle_requests_in_interval']
            wait_time = possible_wait_times[np.where(acceptable)[0][0]]
            self['scratch']['since'] = since_interval
            self['scratch']['since_interval'] = since_interval
            self['scratch']['since_interval_after_wait'] = since_interval_after_wait
            self['scratch']['in_interval_after_wait'] = in_interval_after_wait
            self['scratch']['acceptable'] = acceptable

        return wait_time

    def obey_rate_limit(self):
        """Waits as needed to avoid rate limit"""
        wait_time = self.time_until_throttle_okay()
        if wait_time > 0:
            printw('Connections are being throttled to avoid an error due to too many requests to Google')
            print(f'Waiting {wait_time} seconds before making another request...')
            time.sleep(wait_time)

    def throttled_write(self, value, *args):
        """
        Checks whether it's okay to make a request and waits if necessary to avoid an error

        :param value: numeric or string

        :param args: arguments to pass to direct_read()
        """
        self.obey_rate_limit()
        self.direct_write(value, *args)

    def throttled_read(self, *args, **kw):
        """
        Checks whether it's okay to make a request and waits if necessary to avoid an error

        :param args: arguments to pass to direct_read()

        :param kw: keywords to pass to direct_read()

        :return: value returned from direct_read()
        """
        self.obey_rate_limit()
        self.direct_read(*args, **kw)

    def guess_header_row(self):
        """
        Tries to determine which row holds column headers based on the presence of likely column names
        """
        from collections import OrderedDict

        print(
            'Attempting to guess which row has the column headers. '
            'This process is slow and it is better to supply this information at initialization.'
        )
        candidates = dict()
        occurrences = 0

        keywords = OrderedDict(shot=10, device=0.1, id=1, comments=0.01)

        for keyword, value in keywords.items():
            print(f'Checking for {keyword}')
            self.obey_rate_limit()
            cells = self.sheet_connection().find(keyword, matchEntireCell=True, matchCase=False)
            self.record_request()
            if len(cells) == 1:
                row = cells[0].row
                candidates[row] = candidates.get(row, 0) + value
            if len(candidates) > 0:
                best_row = max(candidates, key=candidates.get)
                high_score = candidates[best_row]
                occurrences = sum([v == high_score for v in candidates.values()])
                if occurrences == 1:
                    self['column_header_row'] = best_row - 1
                    print(f'Assigned column_header_row = {best_row - 1}')
                    return

        if len(candidates) == 0:
            print('Could not find any of the keywords that would help guess which row had the headers.')
            print('Failed to guess header row.')
            return

        if occurrences > 1:
            print('More than one row seemed like it might have column headers. No rule for dealing with this.')
            print('Failed to guess header row.')
            return

    def get_columns(self):
        """Gets a list of column names from the header row"""
        if self['column_header_row'] is not None:
            self.obey_rate_limit()
            self['columns'] = self.sheet_connection().get_row(self['column_header_row'] + 1)
            self.record_request()
        else:
            print('Cannot get columns until column_header_row is specified')

    def find_column(self, column_name, quiet=False):
        """
        Finds the column index corresponding to a column name

        :param column_name: str
            Column header name (should be in row given by column_header_row)

        :param quiet: bool
            No printing

        :return: int (success) or None (failed to find column)
            Column index (from 0; not number from 1)
        """
        indices = np.where(np.array(self['columns']) == column_name)[0]
        if len(indices) > 1:
            print(f'WARNING! More than one column matches {column_name}! They are: {indices}')
            return [idx for idx in indices]
        elif len(indices) == 0:
            if not quiet:
                print(f"Error! Column {repr(column_name)} not found in {self['columns']}")
            return None
        else:
            return int(indices[0])

    def update_cache(self, force=True):
        """
        Updates the cached representation if forced or if it seems like it's a good idea

        If it's been a while since the cache was updated, do another update.
        If we know there was a write operation since the last update, do another update.
        If the cache is missing, grab the data and make the cache.
        If force=True, do another update.

        :param force: bool
            Force an update, even if other indicators would lead to skipping the update
        """
        dt = time.time() - self['__cache__'].get('time', 0)
        update_needed = (
            force
            or self['__cache__'].get('changed', True)
            or (dt > self['cache_expiration'])
            or (self['__cache__'].get('values', None) is None)
        )
        if not update_needed:
            return
        self.obey_rate_limit()
        self['__cache__']['values'] = self.sheet_connection().get_all_values(
            returnas='matrix',
            majdim='COLS',
            include_tailing_empty=True,
            include_tailing_empty_rows=True,
            value_render='UNFORMATTED_VALUE',
            date_time_render_option='SERIAL_NUMBER',
        )
        self.record_request()
        self['__cache__']['time'] = time.time()
        self['__cache__']['changed'] = False

    def get_column(self, column, force_update_cache=False, disable_cache=False):
        """
        Gets data from a column

        By default, the local cache will be checked & updated if needed and then data will be read from the cache.
        Caching can be disabled, which will result in more connections to the remote sheet. Some other methods have
        been programmed assuming that local caching done here will save them from otherwise inefficient layout of
        calls to this function.

        :param column: int or str
            Column index (from 0) or column letter (like 'A', 'B', ... 'ZZ')

        :param force_update_cache: bool
            Force the cache to update before reading

        :param disable_cache: bool
            Don't go through the local cache; read the remote column directly

        :return: list
            Data from the column
        """
        col_idx = interpret_row_col(column, 1)[0]
        if disable_cache:
            self.obey_rate_limit()
            tmp = self.sheet_connection().get_col(col_idx + 1)
            self.record_request()
            return tmp
        self.update_cache(force=force_update_cache)
        return self['__cache__']['values'][col_idx]

    def get_column_by_name(self, column_name, **kw):
        """
        Gets data from a column by name

        :param column_name: str
            Name of the column in the header row

        :param kw: additional parameters passed to get_column

        :return: list
            Data from the column
        """
        return self.get_column(self.find_column(column_name), **kw)

    def get_row(self, row_idx, force_update_cache=False, disable_cache=False):
        """
        Gets data from a row

        By default, cached results are used after updating the local cache as needed (see get_column for details).

        :param row_idx: int
            Row index (from 0)

        :param force_update_cache: bool
            Force the cache to update before reading

        :param disable_cache: bool
            Don't go through the local cache; read the remote row directly

        :return: array
            Data from the row
        """
        if disable_cache:
            self.obey_rate_limit()
            tmp = self.sheet_connection().get_row(row_idx + 1)
            self.record_request()
            return np.array(tmp)
        self.update_cache(force=force_update_cache)
        return np.array(self['__cache__']['values']).T[row_idx]

    # End of class OMFITgoogleSheet


class OMFITexperimentTable(OMFITgoogleSheet):
    """
    Extends OMFITgoogleSheet by assuming each row corresponds to a shot, allowing more features to be provided.

    This is less general (now Shot must exist), but it may be more convenient
    to look up data by shot this way. With more assumptions about the structure
    of the sheet, more methods can be implemented.

    Many methods go further to assume that there is a column named 'Device' and
    that there are two columns that can be used to determine a time range. Parts
    of the class should work on sheets without this structure, but others will
    fail.

    An example sheet that is compatible with the assumptions made by this class may be found here:
    https://docs.google.com/spreadsheets/d/1MJ8cFjFZ2pkt4OHWWIciWT3sM2hSADqzG78NDiqKgkU/edit?usp=sharing

    A sample call that should work to start up an OMFITgoogleSheet instance is:
    >> xtable = OMFITexperimentTable(
    >>     keyfile=os.sep.join([OMFITsrc, '..', 'samples', 'omfit-test-gsheet_key.json']),
    >>     sheet_name='OmfitDataSheetTestsheet',
    >>     subsheet_name='Sheet1',  # Default: lookup first subsheet
    >>     column_header_row_idx=5,  # Default: try to guess
    >>     units_row_idx=6,  # Default: search for units row
    >>     data_start_row_idx=7,  # Default: find first number after the header row in the shot column
    >> )
    This call should connect to the example sheet. These data are used in regression tests and should be updated
    If the test sheet is changed.
    """

    def __init__(self, *args, **kw):
        """
        :param kw: passed to parent class: OMFITgoogleSheet
        """
        self.OMFITproperites = {}
        data_start_row_idx = kw.get('data_start_row_idx', None)
        if data_start_row_idx is None and kw.get('data_start_row_number', None) is not None:
            data_start_row_idx = kw['data_start_row_number'] - 1
        self.input_data_start_row_idx = data_start_row_idx
        super().__init__(*args, **kw)
        self.shots_raw = None

    def post_connect(self):
        """
        Do some inspection on the sheet after connecting to it
        """
        super().post_connect()
        shot_col_idx = self.find_column('Shot')
        if shot_col_idx is None:
            raise OMFITexperimentTableSetupError(
                f"The sheet must contain a \"Shot\" column:\n"
                f"one cell in the header row must contain the exact text \"Shot\".\n"
                f"Was the header row specified correctly?\n"
                f"column_header_row_idx (currently {self['column_header_row']}) counts from 0,\n"
                f"while column_header_row_number (currently {self['column_header_row'] + 1}) counts from 1. "
                f"({self['column_header_row'] + 1} is what appears in Google's interface)"
            )
        self.shots_raw = self.get_column(shot_col_idx)
        self['units_row'] = self['units_row'] or self.find_units_row()
        self['data_start_row'] = self.input_data_start_row_idx or self.find_data_start_row()
        self['shots'] = self.shots_raw[self['data_start_row'] :]
        # Ensure there are no trailing blank entries in the list of shots
        notblank = np.where([len(str(shot)) > 0 for shot in self['shots']])[0]
        if len(notblank):
            self['shots'] = self['shots'][: notblank[-1] + 1]

    def self_check(self, essential_only=False):
        # Add additional checks here
        super().self_check(essential_only=essential_only)

    def guess_header_row(self):
        """
        Tries to determine which row holds column headers

        This is a simplification of the parent class's methods, because here we explicitly require a 'Shot' column.
        It should be faster and more reliable this way.
        """
        print('Attempting to guess which row has the column headers.')
        key_value = 'Shot'
        self.obey_rate_limit()
        cells = self.sheet_connection().find(key_value, matchEntireCell=True)
        self.record_request()

        assert len(cells) == 1, 'There should only be one cell that contains exactly "Shot"'
        self['column_header_row'] = cells[0].row - 1
        print(f"Assigned column_header_row = {self['column_header_row']}")

    def find_units_row(self):
        """
        Recommended: put a row of units under the column headers (data won't start on the next row after headers)

        Were recommendations followed? See if 1st row under headers has "units" under a
        column named Shot, id, or ID. In this case, data start on the row after units.

        This function is easier to implement under OMFITexperimentTable instead of
        OMFITgoogleSheet because we are allowed to make additional assumptions about the
        content of the table.

        If there is no cell containing just 'units', 'Units', or 'UNITS', but you do
        have a row for units, you should specify units_row at init.

        :return: int
            Index (from 0) of the row with units
        """
        if self.shots_raw is None:
            self.connect()

        # If one of the entries under "Shot" is just 'units', this is easy. Just find it.
        units_names = ['units', 'Units', 'UNITS']
        for uu in units_names:
            if uu in self.shots_raw:
                return np.where(np.array(self.shots_raw) == uu)[0][0]

        # So 'units' wasn't written under 'Shot'. Maybe under 'id' or something?
        col_names = ['id', 'ID', 'Device']
        for col_name in col_names:
            col_idx = self.find_column(col_name, quiet=True)
            if col_idx is None:
                continue
            self.obey_rate_limit()
            raw_col_values = self.sheet_connection().get_col(col_idx + 1)
            self.record_request()
            for uu in units_names:
                if uu in raw_col_values:
                    return np.where(np.array(raw_col_values) == uu)[0][0]

        # Still didn't find it? Maybe a "units" row wasn't included.
        return None

    def find_data_start_row(self):
        """
        Determine the first row of data.

        Allowing this to be different from header + 1 means meta data can be inserted under the column headers.

        Since this class imposes the requirement that the "Shot" column exists & has shot numbers, we can find the
        first valid number in that column, after the header row, and be safe in assuming that the data start there.

        To allow for nonstandard configurations of blank cells, please specify data_start_row manually in init.

        :return: int
            Index (from 0) of the row where data start.
        """
        if self.shots_raw is None:
            self.connect()
        for i, val in enumerate(self.shots_raw[self['column_header_row'] :]):
            if i == 0:
                continue  # Just skip the header row
            try:
                int(val)
            except ValueError:
                pass
            else:
                return self['column_header_row'] + i
        # Didn't find a value that could be cast as int after the header
        return self['column_header_row'] + (self['units_row'] is not None) + 1

    def extract_column(self, column, pad_with='', force_type=None, fill_value=np.NaN, fill_if_not_found='not found'):
        """
        Downloads data for a given column and returns them with units

        :param column: str or int
            str: Name of the column; index will be looked up
            int: Index of the column, from 0. Name of the column can be looked up easily.

        :param pad_with: str
            Value to fill in to extend the column if it is too short.
            Truncation of results to the last non-empty cell is possible, meaning columns
            can have inconsistent lengths if some have more empty cells than others.

        :param force_type: type [optional]
            If provided, pass col_values through list_to_array_type() to force them to match force_type.

        :param fill_value: object
            Passed to list_to_array_type(), if used; used to fill in cells that can't be forced to force_type.
            It probably would make sense if this were the same as pad_with, but it doesn't have to be.
            It does have to be of type force_type, though.

        :param fill_if_not_found: str
            Value to fill in if data are not found, such as if column_name is None.

        :return: (array, str or None)
            values in the column, padded or cut to match the number of shots
                replaced by `fill_if_not_found` in case of bad column specifications
                replaced by `fill_value` for individual cells that can't be forced to type `force_type`
                extended by `pad_with` as needed
            units, if available or None otherwise
        """
        if 'shots' not in self:
            self.connect()
        ns = len(self['shots'])

        if is_string(column):
            column_name = column
            column_idx = self.find_column(column_name)
        elif isinstance(column, (int, np.integer)):
            column_idx = column
            column_name = self['columns'][column_idx]
        else:
            raise ValueError('Invalid column specification; should be string (column_name) or int (column_index)')

        if column_name is None:
            return np.array([fill_if_not_found] * ns), None

        col_values0 = self.get_column(column_idx)
        deficit = (ns + self['data_start_row']) - len(col_values0)
        if deficit > 0:
            col_values0 += [pad_with] * deficit
        elif deficit < 0:
            col_values0 = col_values0[:deficit]
        if self.get('units_row', None) is not None:
            units = col_values0[self['units_row']]
        else:
            units = None
        col_values = col_values0[self['data_start_row'] :]
        # print(f'units of {column_name} are listed as {repr(units)}')
        if force_type is not None:
            col_values = list_to_array_type(col_values, type_out=force_type, fill_value=fill_value)
        else:
            col_values = np.array(col_values)
        return col_values, units

    def interpret_timing(self, **signal):
        """
        Interprets timing information in the signal dictionary for write_mds_data_to_table().

        Either tmin and tmax or time and dt are required to be in the dictionary as keys.
        See write_mds_data_to_table() documentation for more information.

        :param signal: Just pass in one of the dictionaries in the list of signals.

        :return: (float array, float array)
            Array of start times and array of end times in ms. One entry per row.
        """
        tmin = signal.get('tmin', None)
        tmax = signal.get('tmax', None)
        t = signal.get('time', None)
        dt = signal.get('dt', None)
        if tmin is not None and tmax is not None:
            if is_string(tmin):
                tmin_name = tmin
                tmin, _ = self.extract_column(tmin, force_type=float)
            else:
                tmin_name = None
                tmin = np.zeros(len(self['shots'])) + float(tmin)
            if is_string(tmax):
                tmax_name = tmax
                tmax, _ = self.extract_column(tmax, force_type=float)
            else:
                tmax_name = None
                tmax = np.zeros(len(self['shots'])) + float(tmax)
            print(f'Got timing from tmin (column {tmin_name}) and tmax (column {tmax_name})')
        elif t is not None and dt is not None:
            if is_string(t):
                time_name = t
                t, _ = self.extract_column(t, force_type=float)
            else:
                time_name = None
                t = np.zeros(len(self['shots'])) + float(t)
            if is_string(dt):
                dt_name = dt
                dt, _ = self.extract_column(dt, force_type=float)
            else:
                dt_name = None
                dt = np.zeros(len(self['shots'])) + float(dt)
            tmin = t - dt
            tmax = t + dt
            print(f'Got timing from time (column {time_name}) and dt (column {dt_name})')
        else:
            raise ValueError('Need a valid pair of tmin & tmax or time & dt')
        return tmin, tmax

    def interpret_signal(self, i, device_servers, **signal):
        """
        Interprets signal specification data for write_mds_data_to_table()

        :param i: int
            Row / shot index

        :param device_servers: dict-like
            Dictionary listing alternative servers for different devices, like {'EAST': 'EAST_US'}

        :param signal: Just pass in one of the dictionaries in the list of signals.

        :return: tuple containing:
            server: str
            tree: str or None
            tdi: str
            factor: float
            tfactor: float
            device: str
        """
        devices = self.extract_column('Device')[0]
        column_name = signal['column_name']  # str, required
        server = device_servers.get(devices[i], devices[i])
        # Device-specific TDIs and treenames are possible if these are set as dictionaries.
        # Universal TDIs and treenames are easy; just don't put in a dictionary.
        # treename of None means PTDATA (d3d only).
        # TDI of None means re-use column_name (so you can put pointnames in as column_names and type this in once)

        def get_the_thing(name, default):
            info = signal.get(name, default)
            if isinstance(info, dict):
                thingy = info.get(devices[i], default)
            else:
                thingy = info
            return thingy

        tree = get_the_thing('treename', None)
        tdi = get_the_thing('TDI', column_name)
        tdi = tdi or column_name
        factor = get_the_thing('factor', 1.0)
        tfactor = get_the_thing('tfactor', 1.0)

        return server, tree, tdi, factor, tfactor, devices[i]

    def write_mds_data_to_table(self, signals, overwrite=False, device_servers=None):
        """
        Gets MDSplus data for a list of signals, performs operations on specified time ranges, & saves results.

        This sample signal can be used as an instructional example or as an input for testing
        >> sample_signal_request = dict(
        >>     column_name='density',  # The sheet must have this column (happens to be a valid d3d ptname)
        >>     TDI=dict(EAST=r'\dfsdev'),  # d3d's TDI isn't listed b/c TDI defaults to column_name
        >>     treename=dict(EAST='PCS_EAST'),  # DIII-D isn't listed b/c default is None, which goes to PTDATA
        >>     factor={'DIII-D': 1e-13},  # This particular EAST pointname doesn't require a factor; defaults to 1
        >>     tfactor=dict(EAST=1e3),  # d3d times are already in ms
        >>     tmin='t min',  # str means read timing values from column w header exactly matching this string
        >>     tmax='t max',
        >> )
        This sample should work with the example/test sheet.

        If the sheet in question had ONLY DIII-D data, the same signal request could be accomplished via:
        >> simple_sample_signal_request = dict(column_name='density', factor=1e-13, tmin='t min', tmax='t max')
        This sample won't work with the test sheet; it will fail on the EAST shots.
        We are exploiting the shortcut that we've used a valid pointname (valid for d3d at least)
        as the column header. If you want fancy column names, you have to specify TDIs.
        We are also relying on the defaults working for this case.

        The sample code in this docstring is interpreted and used by the regression test, so don't break it.
        Separate different samples with non-example lines (that don't start with >>)

        :param signals: list of dict-likes
            Each item in this list should be a dict-like that contains information needed to fetch & process data.
            SIGNAL SPECIFICATION
            - column_name: str (hard requirement)
                Name of the column within the sheet
            - TDI: None, str, or dict-like (optional if default behavior (reuse column_name) is okay)
                None: reuse column_name as the TDI for every row
                str: use this str as the pointname/TDI for every row
                dict-like: keys should be devices. Each device can have its own pointname/TDI.
                The sheet must have a Device row. If a device is missing, it will inherit the column_name.
            - treename: None, str, or dict-like (optional if default behavior (d3d ptdata) is okay)
                None: PTDATA (DIII-D only)
                str: use this string as the treename for every row
                dict-like: device specific treenames. The sheet must have a Device row.
            - factor: float or dict-like (defaults to 1.0)
                float: multiply results by this number before writing
                dict-like: multiply results by a device specific number before writing (unspecified devices get 1)
            - tfactor: float or dict-like (defaults to 1.0)
                float: multiply times by this number to get ms
                dict-like: each device gets a different factor used to put times in ms (unspecified devices get 1)

            PROCESSING
            - operation: str (defaults to 'mean')
                Operation to perform on the gathered data. Options are:
                - 'mean'
                - 'median'
                - 'max'
                - 'min'
            - tmin: float or str
                Start of the time range in ms; used for processing operations like average.
                Must be paired with tmax.
                A usable tmin/tmax pair takes precedence over time+dt.
                A float is used directly. A string triggers lookup of a column in the sheet; then every row gets
                its own number determined by its entry in the specified column.
            - tmax: float or str
                End of the time range in ms. Must be paired with tmin.
            - time: float or str
                Center of a time range in ms. Ignored if tmin and tmax are supplied. Must be paired with dt.
            - dt: float or str
                Half-width of time window in ms. Must be paired with time.

        :param overwrite: bool
            Update the target cell even if it's not empty?

        :param device_servers: dict-like [optional]
            Provide alternative MDS servers for some devices. A common entry might be {'EAST': 'EAST_US'}
            to use the 'EAST_US' (eastdata.gat.com) server with the 'EAST' device.
        """

        # I'm assuming that caching in get_column() will save me from inefficient organization of read operations
        # In order to be good without caching, this function should figure out all the data it needs and read them
        # all up-front. That is, it should build its own temporary cache instead of relying on external caching.
        # But doing that adds a lot of development work and increases the maintenance burden, so I'm going to rely
        # on external caching instead.

        dserv = device_servers or {}

        if self.get('shots', None) is None:
            self.connect()
        shots = self['shots']

        for signal in signals:
            column_name = signal['column_name']
            column_idx = self.find_column(column_name)
            column_values, column_units = self.extract_column(column_name)
            tmin, tmax = self.interpret_timing(**signal)
            for i, shot in enumerate(shots):
                if (not overwrite) and len(str(column_values[i])) > 0:
                    print(f'Cell {column_name} {shot} already has a value and overwrite is off; skipping')
                    continue
                server, tree, tdi, factor, tf, _ = self.interpret_signal(i, device_servers=dserv, **signal)
                mds = OMFITmdsValue(server, shot=shot, treename=tree, TDI=tdi)
                if not mds.check():
                    print(f'Bad MDS connection for {server}#{shot} {tree} / {tdi}; skipping')
                    continue
                sel = ((mds.dim_of(0) * tf) >= tmin[i]) & ((mds.dim_of(0) * tf) <= tmax[i])
                data = mds.data()[sel] * factor
                value = operate_on_data(data, signal.get('operation', 'mean'))
                self.throttled_write(value, column_idx, self['data_start_row'] + i)

    def write_efit_result(self, pointnames=None, **kw):
        r"""
        Wrapper for write_mds_data_to_table for quickly setting up EFIT signals.

        Assumes that device-specific variations on EFIT pointnames and  primary trees
        are easy to guess, and that you have named your columns to exactly  match EFIT
        pointnames in their "pure" form (no leading \).

        Basically, it can build the signal dictionaries for you given a list of
        pointnames and some timing instructions.

        Here is a set of sample keywords that could be passed to this function:
        >> sample_kw = dict(
        >>     pointnames=['betan'],
        >>     tmin='t min',  # Can supply a constant float instead of a string
        >>     tmax='t max',
        >>     overwrite=True,
        >>     device_servers=dict(EAST='EAST_US'),  # Probably only needed for EAST
        >> )
        These should work in xtable.write_efit_result where xtable is an
        OMFITexperimentTable instance connected to a google sheet that contains columns
        with headers 'betan', 't min', and 't max'

        :param pointnames; list of strings
            Use names like betan, etc. This function will figure out whether you really need \betan instead.

        :param kw: more settings, including signal setup customizations.
            * MUST INCLUDE tmin & tmax OR time & dt!!!!!!!!!              <---- don't forget to include timing data
            * Optional signal customization: operation, factor
            * Remaining keywords (other than those listed so far) will be passed to write_mds_data_to_table
            * Do not include column_name, TDI, treename, or tfactor, as these are determined by this function.
                If you need this level of customization, just use write_mds_data_to_table() directly.
        """

        signal_details = {tmp: kw.pop(tmp, None) for tmp in ['tmin', 'tmax', 'time', 'dt', 'operation', 'factor']}
        for sd in list(signal_details):
            if signal_details[sd] is None:
                signal_details.pop(sd)
        signals = [
            dict(
                column_name=pointname,
                TDI={'DIII-D': pointname, 'EAST': rf'\{pointname}'},
                treename=dict(EAST='EFIT_EAST'),
                tfactor=dict(EAST=1e3),
                **signal_details,
            )
            for pointname in pointnames
        ]
        self.write_mds_data_to_table(signals, **kw)

    # End of class OMFITexperimentTable


############################################
if __name__ == '__main__':
    # Basic class import test
    if pygsheets is not None:
        test_classes_main_header()
        test_sheet_data = get_definition_from_docstring(OMFITexperimentTable, return_kw=True)['xtable_kw']
        et = OMFITexperimentTable(
            keyfile=os.sep.join([OMFITsrc, '..', 'samples', 'omfit-test-gsheet_key.json']),
            sheet_name=test_sheet_data['sheet_name'],
            column_header_row_idx=test_sheet_data['column_header_row_idx'],
            units_row_idx=test_sheet_data['units_row_idx'],
            data_start_row_idx=test_sheet_data['data_start_row_idx'],
        )
