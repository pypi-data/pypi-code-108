#!/usr/bin/python
"""\
@file   commands.py
@author Nat Goodspeed
@date   2018-06-06
@brief  Automatically populate an ArgumentParser with subcommands to call any
        suitably-decorated function.

        Each of several functions in a module can be written for Python
        callers, but when decorated as described in the Commands class, it
        becomes a subcommand (with the function's name) in the generated
        ArgumentParser. Effectively, the same function can be called either by
        a Python function or by a user from the command line.
"""

from __future__ import print_function
import argparse
import functools
import inspect
import itertools
import re
import sys

class Error(Exception):
    pass

def print_non_None(value):
    """
    Default formatter for values returned by functions decorated with Commands.
    """
    # this mimics the behavior of the interactive Python interpreter
    if value is not None:
        print(value)

class Commands(object):
    """
    Each instance of Commands serves as a decorator for one or more free
    functions that can potentially be invoked as subcommands on the command
    line.

    Usage:

    _command = Commands()  # or Commands('overall help string')
    ...
    @_command
    def freefunc(arg):
        '''
        Freefuncify arg

        arg: some text
            that might wrap to an indented next line
        '''
        # ...

    @_command
    def otherfunc(required, optional=None):
        '''
        Otherfuncify required, potentially affected by optional

        required: description of required arg
        optional: description of optional arg
        '''
        # ...

    if __name__ == '__main__':
        parser = _command.get_parser()
        args = parser.parse_args()
        args.run()

    The above parse_args() call returns an ArgumentParser instance populated
    with subcommands 'freefunc' and 'otherfunc'. The 'freefunc' subcommand
    accepts a required positional argument 'arg'; the 'otherfunc' subcommand
    accepts a required positional argument 'required' and an '--optional'
    switch.

    The --help output for each subcommand describes those command-line
    arguments using text from the corresponding function's docstring.

    Moreover, the Namespace object returned by the parse_args() call has been
    enriched with a run() method. Calling run() calls the function selected by
    the user-specified subcommand, passing arguments as parsed by
    ArgumentParser.

    The freefunc() and otherfunc() functions above return None. (Either they
    print their own results, or they have only side-effects.)

    If the function you want to call returns its result, rather than printing
    it, that result is printed using print(). This may be surprising if you
    decorate a function that both prints output AND returns a value other than
    None -- None is not printed, emulating the interactive Python interpreter.

    If you want to specify a formatter for the value returned by a given
    function, you can decorate it this way instead:

    # here 'print' is the builtin Python function
    @_command.format(print)
    def returns():
        return 'Hello, world!'
    """

    def __init__(self, help=None):
        self.help = help
        # list of decorated functions
        self.commands = []

    def __call__(self, func):
        """
        The Commands instance itself is the function decorator.
        """
        self.commands.append((func, print_non_None))
        # Don't modify it or even inspect it at this time, just collect it.
        return func

    def format(self, formatter):
        """
        The effect of specifying .format(print) is that even a None return
        (the default value when a function falls out without executing
        'return' at all) is printed.

        It's worth noting that you can specify .format(pprint.pprint) to
        display structured data as pretty-printed, or .format(json.dumps).

        If your function is a generator, by default simply printing its return
        value will merely inform you that it's a generator. But specifying
        .format(functools.partial(map, print)) will print each item on a
        separate line. Alternatively, .format(functools.partial(map,
        pprint.pprint)), etc.

        For more complicated formatting, you could write a formatter function
        of your own and pass it to .format(). Any formatter function must
        accept (at least) a single value. You can discard a decorated
        function's return value by (e.g.) .format(lambda x: None).

        If you need specialized output for a particular decorated function,
        you could also write a wrapper function and decorate that instead. But
        if your wrapper accepts (*args, **kwds) and passes them through to the
        real function, the generated ArgumentParser will simply pass through
        any positional arguments on the command line.

        So a custom formatter function may be preferable: when you decorate
        the real function, the generated subcommand will know about (and parse
        command-line arguments for) its actual parameters.
        """
        # Since format(formatter) is a decorator, it must return a function
        # capable of accepting the decorated function.
        return functools.partial(self._format, formatter)

    def _format(self, formatter, func):
        """
        Actual decorator that will be passed func by the decorator mechanism.
        """
        self.commands.append((func, formatter))
        return func

    def get_parser(self, decamel=None, score='_'):
        """
        Return an argparse.ArgumentParser instance that defines a subcommand
        for each decorated function. Normally the subcommand is literally the
        name of the decorated function. The help for each subcommand is taken
        from the first paragraph of the decorated function's docstring, up to
        the first blank line.

        Special case: if exactly one function is decorated, the returned
        ArgumentParser supports that function directly, rather than accepting
        a subcommand with the name of that function. This is useful for a
        trivial script module that nonetheless should present a plausible
        command-line interface for its one (main()?) function.

        If score is overridden with (e.g.) score='-', then underscores in the
        function name produce hyphens in the subcommand name. Thus:

        @_command
        def my_func():
            # ...

        @_command
        def myCamelFunc():
            # ...

        _command.get_parser(score='-') returns a parser that supports a
        subcommand 'my-func' rather than 'my_func'.

        _command.get_parser(score='') returns a parser that supports a
        subcommand 'myfunc' rather than 'my_func'.

        If decamel is None, then a camelCase function name produces a camelCase
        subcommand name. Otherwise, a camelCase function name is split and
        rejoined with the decamel character.

        _command.get_parser(decamel='-') returns a parser that supports a
        subcommand 'my-camel-func' rather than 'myCamelFunc'.

        _command.get_parser(decamel='') returns a parser that supports a
        subcommand 'mycamelfunc' rather than 'myCamelFunc'.

        Each required function argument specifies a positional argument for
        the subcommand.

        Each optional function argument opt=None specifies an --opt switch for
        the subcommand -- unless its default value is True, in which case the
        switch will actually be --no_opt (specifically '--no' + score + opt).

        If the optional function argument has a type other than str or
        NoneType, that type will be used as the type of the switch. Naturally,
        the default value of the function argument is the default value of the
        switch, and is so reported.

        If, for any function argument arg, the decorated function's docstring
        contains a line starting with 'arg:', the rest of that line (and every
        indented line that follows) is taken as the help string for that argument.

        If the function's argument list contains a *args argument, the
        ArgumentParser will pass all unrecognized positional command-line
        arguments to that argument.

        A function **kwds argument is not supported at this time. You may specify
        such an argument for use by Python callers, but the ArgumentParser won't
        be affected by that argument.
        """
        if len(self.commands) == 1:
            # For exactly one decorated function, return a single top-level
            # ArgumentParser for that function.
            parser_holder = LazyArgumentParser(self.help)
        else:
            # The expected case is multiple decorated functions, each getting
            # a subcommand of its own.
            parser_holder = ArgumentParserWithSubparsers(self.help)

        for func, formatter in self.commands:
            # convert function name according to decamel and score
            name = func.__name__.replace('_', score)
            if decamel:
                name = self.decamel(name, decamel)

            # pull its docstring
            doc = inspect.getdoc(func)
            if not doc:
                # If no docstring, treat as empty list
                doc = []
                # no help for you, tsk tsk
                help = None
            else:
                # split docstring into individual lines (bearing in mind that
                # getdoc() already removes leading and trailing blank lines
                # and strips consistent indentation)
                doc = doc.splitlines()
                # take everything up to the first blank line as the help for
                # this subcommand
                help = list(itertools.takewhile(bool, doc))
                # remove from doc
                del doc[:len(help)]
                # and rejoin to a single string
                help = '\n'.join(help)

            # Add a (sub)parser for this (sub)command.
            subparser = parser_holder.get_subparser(name, help=help)
            # and set that parser's func attribute to the function
            # also store the desired formatter
            subparser.set_defaults(func=func, formatter=formatter)

            # query the function's formal parameter list
            args = inspect.getargspec(func)
            # Categorize arguments in args.args as required (no defaults) or
            # optional (have defaults). args.defaults is right-justified: it
            # maps to the rightmost elements of args.args.
            if not args.defaults:
                # None means all args are required
                required = args.args
                optional = []
            else:
                # split args.args into required (leftmost part)
                required = args.args[:-len(args.defaults)]
                # and optional (rightmost part matching defaults)
                optional = args.args[-len(args.defaults):]

            # Add a switch for each optional argument.
            for arg, value in zip(optional, args.defaults or ()):
                # the switch is often -- but not always -- the arg name
                switch = '--' + arg
                default = "(default {})".format(value)
                # Check the default value.
                # For True and False, use 'is' --
                # did you know that in Python, 1 == True??
                if value is False:
                    kwds = dict(action="store_true")
                elif value is True:
                    # since specifying this switch means passing False, prefix
                    # it with --no-arg or --no_arg (according to 'score')
                    switch = score.join(('--no', arg))
                    kwds = dict(dest=arg, action="store_false")
                    # It looks confusing to say that the default value for
                    # --no-something is True, when what we mean is that the
                    # default for something is True and --no-something
                    # suppresses it. In this odd case, make the meaning of the
                    # default more explicit.
                    default = "(default {}={})".format(arg, value)
                elif value is None or value.__class__ is object:
                    # Default value None means it's just optional: no other
                    # info about it.
                    # In some cases we (by convention) use a named instance of
                    # raw class 'object' as default when None is a valid value
                    # to pass explicitly, distinct from 'arg omitted.'
                    kwds = {}
                else:
                    # In all other cases, use the type of the default value as
                    # the type to which to convert the command line value.
                    kwds = dict(type=type(value))

                help = self.get_arg_help(doc, arg)
                help = ' '.join((help, default)) if help else default
                subparser.add_argument(switch, default=value, help=help, **kwds)

            # Since we have no supplemental information about required
            # arguments, assume they're all strings.
            for arg in required:
                subparser.add_argument(arg, help=self.get_arg_help(doc, arg))

            # if there's a *args argument, that will collect all the rest of
            # the positional arguments on the command line
            if args.varargs:
                subparser.add_argument(args.varargs, nargs="*",
                                       help=self.get_arg_help(doc, args.varargs))

        # Return the top-level ArgumentParser, whether or not we set it lazily.
        return parser_holder.get_parser()

    # https://codereview.stackexchange.com/a/185973
    # Recognize a capital letter followed by lowercase letters so that (e.g.)
    # "MySQLClient" splits as ["MySQL", "Client"].
    first_cap_re = re.compile(r'(.)([A-Z][a-z]+)')
    # Recognize lowercase letters followed by a capital letter so that (e.g.)
    # "MySQL" splits as ["My", "SQL"].
    sep_cap_re = re.compile(r'([a-z0-9])([A-Z])')

    def decamel(self, name, sep):
        """
        Reformat a camelCaseName as camel{sep}case{sep}name.
        """
        # Each time we recognize a split, replace it by inserting 'sep'
        # between the pieces.
        replace = sep.join((r'\1', r'\2')) # e.g. r'\1_\2'
        # split before: capital followed by lowercase
        intermediate = self.first_cap_re.sub(replace, name)
        # split between: lowercase followed by capital
        return self.sep_cap_re.sub(replace, intermediate).lower()

    def get_arg_help(self, doc, arg):
        """
        In a decorated function's docstring 'doc', passed as a list of
        individual lines without '\n', find a line starting with 'arg:' and
        any subsequent indented lines and return a (reflowed) string. If we
        can't find 'arg:', return None.
        """
        # what to search for
        argpfx = arg + ':'
        # Find a line in doc that starts with 'arg:'
        helpsearch = iter(doc)
        for line in helpsearch:
            if line.startswith(argpfx):
                # start with a list containing the text following 'arg:',
                # skipping spaces
                helplines = [line[len(argpfx):].lstrip()]
                # keep advancing through helpsearch until either we run out of
                # lines or we find one that's not indented
                try:
                    line = next(helpsearch)
                    while line.startswith(' '):
                        helplines.append(line)
                        line = next(helpsearch)
                except StopIteration:
                    pass
                # rejoin all the help for 'arg:'
                return '\n'.join(helplines)

        # didn't find 'arg:'
        return None

class LazyArgumentParser(object):
    """
    Instantiate one top-level ArgumentParser on demand. get_subparser() must
    be called exactly once before get_parser(). This is for use when exactly
    one function is decorated with a Commands instance.
    """
    def __init__(self, help):
        self.help = help
        self.parser = None

    def get_subparser(self, name, help):
        if self.parser is not None:
            raise Error('LazyArgumentParser.get_subparser() must be called exactly once')
        # Our caller has only just looked at this one decorated function, so
        # this is the first time we discover its help content. If Commands was
        # constructed with a help string, use that, else use the function's help.
        self.parser = ArgumentParser(description=self.help or help)
        # Let caller add argument definitions directly to this top-level
        # parser, instead of subcommand parsers.
        return self.parser

    def get_parser(self):
        if self.parser is None:
            raise Error('LazyArgumentParser.get_subparser() must be called exactly once '
                        'before get_parser()')
        return self.parser

class ArgumentParserWithSubparsers(object):
    """
    Immediately instantiate a top-level ArgumentParser, and make
    get_subparser() deliver a new subcommand parser every call. This is for
    use when multiple functions are decorated with a Commands instance.
    """
    def __init__(self, help):
        self.parser = ArgumentParser(description=help)
        self.subparsers = self.parser.add_subparsers(title="subcommands")

    def get_subparser(self, name, help):
        # Create a new subcommand parser with specified name and help. Let
        # caller add argument definitions to the subcommand parser.
        return self.subparsers.add_parser(name, help=help)

    def get_parser(self):
        return self.parser

class ArgumentParser(argparse.ArgumentParser):
    """
    This subclass of argparse.ArgumentParser overrides parse_args() to return
    a Namespace object that includes a run() method.
    """
    def parse_args(self, *args, **kwds):
        # forward the call to base class
        parsed = super(ArgumentParser, self).parse_args(*args, **kwds)
        # bind the run() method to the returned object
        parsed.run = functools.partial(run, parsed)
        # return it
        return parsed

class _NeverRaised(Exception):
    """
    Dummy exception so we can write 'except _NeverRaised:' and have code
    equivalent to no try/except wrapper.
    """
    pass

def run(self, exceptions=_NeverRaised):
    """
    We monkey-patch this 'method' into the Namespace object returned by
    argparse.parse_args().

    If you pass exceptions= either a single exception or a tuple of exceptions
    (in other words, the variants supported by the 'except' clause), then
    run() will catch that/those exception(s) and terminate by calling
    sys.exit(str(e)). Otherwise, exceptions propagate to the caller.
    """
    # The Namespace object onto which we patch this object should have exactly
    # the following attributes:
    # - the 'dest' attributes from each add_argument() call
    # - the 'func' from the selected subparser
    # - the 'formatter' from the selected subparser
    # - this 'run' method.
    # We very specifically perform add_argument() calls for each of 'func's
    # arguments. So once we remove the other attributes we've forced in, we
    # should be able to call func with the rest.
    kwds = vars(self)
    # just discard this method
    kwds.pop("run")
    # capture func and formatter
    func = kwds.pop("func")
    formatter = kwds.pop("formatter")
    try:
        return formatter(func(**kwds))
    except exceptions as err:
        sys.exit(str(err))
