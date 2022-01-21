#!python

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang REPL"""

import argparse
import atexit
import os
import readline
import sys
import time

import nanamilang.datatypes
import nanamilang.formatter
from nanamilang.shortcuts import truncated, aligned
from nanamilang import module, loader
from nanamilang.contrib.window import Window
from nanamilang.builtin import BuiltinFunctions, BuiltinMacros
from nanamilang.bdb import BuiltinMacrosDB, BuiltinFunctionsDB
from nanamilang import __version_string__, __author__, __project_license__

readline_history_file_path = os.path.join(
    os.path.expanduser("~"), ".nanamilang_history")
try:
    readline.set_history_length(1000)
    readline.read_history_file(readline_history_file_path)
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, readline_history_file_path)

# Initialize Builtin* DB ...
BuiltinMacrosDB.initialize(BuiltinMacros)
BuiltinFunctionsDB.initialize(BuiltinFunctions)

readline.parse_and_bind("tab: complete")
readline.parse_and_bind('set blink-matching-paren on')

exit_f_names: list = ['exit!', 'bye!', 'exit', 'bye', 'quit', 'quit!']
available_names = set(BuiltinMacrosDB.names() + BuiltinFunctionsDB.names() + exit_f_names)


def complete(t: str, s: int):
    """NanamiLang REPL, GNU Readline complete callback fn,  completes from available names"""
    return ([name for name in available_names if name.startswith(t)] + [None]).__getitem__(s)


readline.set_completer(complete)


def check_whether_user_want_to_exit(m: module.Module) -> None:
    """
    1. m.tokenized() contains only ONE token:
    2. that token is a type() of Token.Identifier
    3. that token dt().origin() is something from exit function names

    :param m: REPL module instance which used to evaluate user's inputs
    """

    tip = 'To exit the REPL: type ({0}), press a "Control+D" or "Control+C"'

    if len(m.tokenized()) == 1:
        first = m.tokenized()[0]
        if first.type() == 'Identifier':
            if first.dt().origin() in exit_f_names:
                print(aligned('', source=tip.format(first.dt().origin()), n=67))


def main():
    """NanamiLang REPL Main function"""

    parser = argparse.ArgumentParser('NanamiLang REPL')
    parser.add_argument('--no-greeting',
                        help='Greeting can be disabled',
                        action='store_true', default=False)
    parser.add_argument('--include-traceback',
                        help='Include exception traceback',
                        action='store_true', default=False)
    parser.add_argument('--show-measurements',
                        help='Show the REPL module stats.',
                        action='store_true', default=False)
    parser.add_argument('--license',
                        help='Show license of NanamiLang',
                        action='store_true', default=False)
    parser.add_argument('--version',
                        help='Show version of NanamiLang',
                        action='store_true', default=False)

    args = parser.parse_args()

    # GNU GPL v2 may require these options

    if args.version:
        print('NanamiLang', __version_string__)
        return 0

    if args.license:
        print('License is', __project_license__)
        return 0

    # Collect Python 3 version into single string
    p_ver = '.'.join([str(sys.version_info.major),
                      str(sys.version_info.minor),
                      str(sys.version_info.micro)])

    # First, good boys always should start with the greeting
    print('NanamiLang', __version_string__, 'by', __author__, 'on Python', p_ver)
    if not args.no_greeting:
        print('History path is:', readline_history_file_path)
        if not os.environ.get('NANAMILANG_PATH'):
            print('\nW: NANAMILANG_PATH environment variable has not been set!\n')
        print('History of computations is stored in *1, *2, and *3 global bindings')
        print('The most recent exception occurred (which we handle) stored in "*e"')
        print('Type (doc function-or-macro) to see function-or-macro documentation')
        print('     Since version 0.15.0: doc is a part of NanamiLang Standard Lib')
        print('     Fetch a https://nanamilang.jedi2light.moe/pkg/stdlib.nml, then')
        print('     include target directory to NANAMILANG_PATH, then do following')
        print("     (require 'stdlib)    ;; require NanamiLang Standard Lib module")
        print('     (def doc stdlib/doc) ;; make an alias to access doc as earlier')
        print('Type (exit!), (bye!), press "Control+D" or "Control+C" to exit REPL')

    # Since nanamilang.builtin.BuiltinFunctions provides install() method,
    # we can install functions to help the user to exit NanamiLang REPL in easy way!
    for exit_f_name in exit_f_names:
        BuiltinFunctions.install(
            {
                'name': exit_f_name,
                'forms': [f'({exit_f_name})'],
                'docstring': 'Exit NanamiLang REPL environment with a zero exitcode'
            },
            lambda _: sys.exit(0)
        )

    m = module.Module(name='REPL')  # <- create a nanamilang module instance and ...

    computations = Window(3)  # <- initialize a window to manage computation history

    # Update autocomplete names on environment::set event triggered
    m.on('environment::set', lambda _: (available_names.add(_[0])))  # <- add to set

    # Initialize REPL globals: *1. *2, *3, *e (like Leiningen REPL)

    e = m.environ()
    e.set('*e', nanamilang.datatypes.Nil('nil'))
    e.set('*1', nanamilang.datatypes.Nil('nil'))
    e.set('*2', nanamilang.datatypes.Nil('nil'))
    e.set('*3', nanamilang.datatypes.Nil('nil'))  # <- initialize as nils by default

    # Initialize little bit dirty NanamiLang Module Loader mechanism
    loader.Loader.initialize(module.Module,
                             loader.LocalIOLoader, includetb=args.include_traceback)

    # Here, we are finally able to start the main REPL loop, hooray!
    while True:
        try:
            # First, let the user enter some expression to evaluate!
            src = input('REPL> ')
            __repl_got_input__ = time.perf_counter()
            # Skip expression evaluation in case of the empty input.
            if not src:
                continue
            # Call m.prepare() to prepare current user's expression.
            m.prepare(src)
            # Show tips in case user want to exit NanamiLang REPL script
            check_whether_user_want_to_exit(m)
            # Iterate through results, if some of them - NException, handle it
            for dt in m.evaluate().results():
                if isinstance(dt, nanamilang.datatypes.NException):
                    e.set('*e', dt)
                    # Store a most recent NException data type in *e global variable
                    if not args.include_traceback:
                        print(truncated(dt.format(src=src), 67))
                    else:
                        print('\n\b',
                              truncated(
                                  dt.format(src=src,
                                            include_traceback=args.include_traceback), 67))
                else:
                    computations.push(dt)  # <- push computation result to computations hst
                    print(truncated(dt.format(), 67))  # <- and print a computation result!
            # Populate computations history ###############################################
            e.set('*1', computations.get(0, default=e.get('*1')))
            e.set('*2', computations.get(1, default=e.get('*2')))
            e.set('*3', computations.get(2, default=e.get('*3')))
            ###############################################################################
            # If '--show-measurements' has been passed, show all the available measurements
            if args.show_measurements:
                stats = {'[REPL]': time.perf_counter() - __repl_got_input__}
                # Sadly, we do not count dictionary update operation here as well, but okay
                stats.update(m.measurements())
                # Also, we don't count: iterating, unpacking, rounding, formatting, printing
                print('\n'.join(
                    [aligned(s, f'{t:.5f} secs.', 67, dots='.') for s, t in stats.items()]))
        except (EOFError, KeyboardInterrupt):
            print("Bye for now!")
            break

    return 0

    # Return 0 to system and exit NanamiLang REPL script after playing around with NanamiLang


if __name__ == "__main__":
    main()
