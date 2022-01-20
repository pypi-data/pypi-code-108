#!/usr/bin/env python3
"""
TZNAME.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python script to print the local timezone name.
"""

import os

from plib.stdlib.tztools import (
    local_tzname,
    ETC_TIMEZONE,
    ETC_LOCALTIME_LINK,
    ETC_LOCALTIME_FILE,
    LOCAL_TZINFO,
    local_tz_methods
)

method_names = {
    ETC_TIMEZONE: "/etc/timezone",
    ETC_LOCALTIME_LINK: "/etc/localtime link",
    ETC_LOCALTIME_FILE: "/etc/localtime file",
    LOCAL_TZINFO: "dynamic local tzinfo"
}


def tzname_result(result, method):
    return "{} (method: {})".format(result, method_names[method])


def local_tzname_all(show_all=False):
    return os.linesep.join([
        tzname_result(local_tzname(method, show_all=show_all), method)
        for method in sorted(local_tz_methods.keys())
    ])


if __name__ == '__main__':
    import sys
    from plib.stdlib.options import parse_options
    
    optlist = (
        ('-a', '--all', {
            'action': 'store_true',
            'dest': 'all_methods', 'default': False,
            'help': "display results for all methods"
        }),
        ('-f', '--etc-localtime-file', {
            'action': 'store_const', 'const': ETC_LOCALTIME_FILE,
            'dest': 'method', 'default': 0,
            'help': "compare /etc/localtime file to available tzinfo files"
        }),
        ('-i', '--local-tzinfo', {
            'action': 'store_const', 'const': LOCAL_TZINFO,
            'dest': 'method', 'default': 0,
            'help': "compare local timezone dynamic info to available tzinfo files"
        }),
        ('-l', '--etc-localtime-link', {
            'action': 'store_const', 'const': ETC_LOCALTIME_LINK,
            'dest': 'method', 'default': 0,
            'help': "follow /etc/localtime symlink"
        }),
        ('-m', '--print-method', {
            'action': 'store_true',
            'dest': 'print_method', 'default': False,
            'help': "print method used if not specified by an option"
        }),
        ('-s', '--show-all', {
            'action': 'store_true',
            'dest': 'show_all', 'default': False,
            'help': "show all matches for methods that compare to tzinfo files"
        }),
        ('-t', '--etc-timezone', {
            'action': 'store_const', 'const': ETC_TIMEZONE,
            'dest': 'method', 'default': 0,
            'help': "read /etc/timezone"
        }),
        ('-v', '--verbose', {
            'action': 'store_true',
            'dest': 'verbose', 'default': False,
            'help': "print output if no match is found"
        })
    )
    
    opts, args = parse_options(optlist)
    
    if opts.all_methods:
        result = output = local_tzname_all(opts.show_all)
    elif opts.method in local_tz_methods:
        result = output = local_tzname(opts.method, show_all=opts.show_all)
    else:
        result, method = local_tzname(return_method=True, show_all=opts.show_all)
        output = result if not opts.print_method else tzname_result(result, method) if result else None
    
    if result or opts.verbose:
        print(output or "No match found for local timezone!")
    sys.exit(0 if result else 1)
