# Copyright 2022 Henix, henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""opentf-ctl commons"""

import csv
import logging
import re
import sys


########################################################################
# debug


def _error(*msg):
    logging.error(*msg)


def _warning(*msg):
    logging.warning(*msg)


def _debug(*msg):
    logging.debug(*msg)


def _info(*msg):
    logging.info(*msg)


########################################################################
# sys.argv processing


def _is_command(command, args):
    """Check if args matches command.

    `_` are placeholders.

    # Examples

    ```text
    _is_command('get job _', ['', 'get', 'job', 'foo'])  -> True
    _is_command('get   job  _', ['', 'get', 'job', 'foo'])  -> True
    _is_command('GET JOB _', ['', 'get', 'job', 'foo'])  -> False
    ```

    # Required parameters

    - command: a string
    - args: a list of strings

    # Returned value

    A boolean.
    """
    if len(args) <= len(command.split()):
        return False
    for pos, item in enumerate(command.split(), start=1):
        if item not in ('_', args[pos]):
            return False
    return True


def _get_value(prefix):
    """Get value from sys.argv.

    `prefix` is a command line option prefix, such as `--foo=`.  It
    should not contain '_' symbols.

    The first found corresponding command line option is returned.

    The comparaison replaces '_' with '-' in the command line options.

    # Examples

    ```text
    _get_value('--foo=')  -> yada if sys.argv contains `--foo=yada`
                             None otherwise
    _get_value('--foo_bar=') -> baz if sys.argv contains `--foo-bar=baz`
                                or `--foo_var=baz`
    ```

    # Required parameters

    - prefix: a string

    # Returned value

    None if prefix is not found in sys.argv, the corresponding entry
    with the prefix stripped if found.
    """
    for item in sys.argv[1:]:
        if item.replace('_', '-').startswith(prefix):
            return item[len(prefix) :]
    return None


# csv processing


def _get_columns(wide, default):
    """Return requested columns.

    Returns custom-columns if specified on command line.
    If not, if wide is specified on command line, it wins.
    Else default is returned.

    Raises ValueError if command line parameters are invalid.
    """
    single = _get_value('--output=custom-columns=')
    double = _get_value('custom-columns=')
    if single or ('-o' in sys.argv and double):
        ccs = (single or double).split(',')
        if not all(':' in cc for cc in ccs):
            raise ValueError(
                'Invalid custom-columns specification.  Expecting a comma-separated'
                ' list of entries of form TITLE:path'
            )
        return ccs
    if '--output=wide' in sys.argv or ('-o' in sys.argv and 'wide' in sys.argv):
        return wide
    if double:
        raise ValueError('Missing "-o" parameter (found lone "custom-columns=")')
    return default


def _emit_csv(data, columns, file=sys.stdout):
    """Generate csv.

    `data` is an iterable.  `columns` is a columns specification
    ('title:path').

    `file` is optional, and is `sys.stdout` by default.
    """
    writer = csv.writer(file)
    writer.writerow(path.split(':')[0] for path in columns)
    for row in data:
        writer.writerow(row)


# misc. helpers


def _ensure_uuid(parameter):
    """Ensure parameter is a valid UUID.

    Abort with error code 2 if `parameter` is not a valid UUID.
    """
    if not re.match(r'^[a-f0-9-]+$', parameter):
        _error('Parameter %s is not a valid UUID.', parameter)
        sys.exit(2)
