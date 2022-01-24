# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #


def dao_by_name(dao_name: str, dao_path: str = 'dao'):
    """
    Loads a dao object by name:

    :param dao_name: The dao library to load.
    :param dao_path: Optionally provide an alternate dao path
    :return: The dao library.
    """
    from bs_lib import common

    mpath = 'bs_audit.db.%s.%s' % (dao_path, dao_name)

    res, exc = common.import_dyn_pluggin(mpath, True, False)

    if exc:
        raise Exception('DAO not found [%s] - Error: %s' % (mpath, str(exc)))

    return res


def get_table_sql(db_name: str) -> str:
    """
    Gets the creat tables sql for the targetted database.

    :param db_name: The database to get for, note the equivalent sql file should exist in the package sql folder.
    :returns: The sql file text.
    """
    import importlib.resources as pkg_resources

    from . import sql

    return pkg_resources.read_text(sql, f'{db_name.lower()}.sql')


def _cli_show_usage():
    print()
    print('usage: bs-audit [--getsql] DBNAME')
    print()
    print('required arguments:')
    print('  DBNAME          The target database to get for [eg: postgresql]')
    print()
    print('optional arguments:')
    print('  -g, --getsql    Gets the sql to generate the audit tables')
    print('  -?, -h, --help  Show this help message and exit')
    print()


def _cli_read_args(args: list) -> dict:
    import getopt

    try:
        optlist, gargs = getopt.getopt(args, '?hg', [ 'help', 'getsql' ])
    except getopt.GetoptError as err:
        print(err)
        return _cli_show_usage()

    aobj = { 'db'  : None, 'cmd' : None }

    for o, a in optlist:
        if o in ('-?', '-h', '--help'):
            return _cli_show_usage()

        if o in ('-g', '--getsql'):
            aobj['cmd'] = 'get'
            continue

        print('\n ... unrecognized arguments: %s' % o)
        return _cli_show_usage()

    if not gargs:
        print('\n ... target database not specified')
        return _cli_show_usage()

    if not aobj['cmd']:
        print('\n ... command not specified')
        return _cli_show_usage()


    aobj['db'] = gargs[0]

    return aobj


def main(args: list = None) -> int:
    import sys

    aobj = _cli_read_args(sys.argv[1:])

    if not aobj:
        return 2

    if aobj['cmd'] == 'get':
        print()
        print(get_table_sql(aobj['db']))
        print()

    return 0


__all__ = [ 'dao_by_name', 'get_table_sql' ]
