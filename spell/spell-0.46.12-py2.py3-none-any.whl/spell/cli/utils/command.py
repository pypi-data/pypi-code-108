from collections import OrderedDict
import shlex
import click
from click.parser import OptionParser, ParsingState
import yaml
from spell.cli.exceptions import ExitException, CLICK_CLI_USAGE_ERROR

CMD_FILE_PARAM_NAME = "--from-file"
WRITE_CMD_FILE_PARAM_NAME = "--save-command"
CMD_FILE_PARAM = CMD_FILE_PARAM_NAME.lstrip("-").replace("-", "_").lower()
WRITE_CMD_FILE_PARAM = WRITE_CMD_FILE_PARAM_NAME.lstrip("-").replace("-", "_").lower()


def command(*args, **kwargs):
    def wrapper(func):
        kwargs.setdefault("cls", CommandWithCmdFile)
        return click.command(
            *args,
            **kwargs,
        )(func)

    return wrapper


def group(name=None, **attrs):
    attrs.setdefault("cls", GroupWithCmdFile)
    return command(name, **attrs)


def docs_option(docs):
    def show_docs(ctx, param, value):
        if value:
            click.launch(docs)
            ctx.exit()

    return click.option(
        "--docs",
        help="Open documentation in the browser and exit",
        is_flag=True,
        expose_value=False,
        is_eager=True,
        callback=show_docs,
    )


def _longest_name(param, secondary=False):
    opts = param.opts if not secondary else param.secondary_opts
    return max(opts, key=len)


class CmdFileUsageException(ExitException):
    def __init__(self, message):
        super(CmdFileUsageException, self).__init__(message, exit_code=CLICK_CLI_USAGE_ERROR)


class CmdFileArgumentException(CmdFileUsageException):
    def __init__(self):
        message = "All positional arguments must either be specified in the command file or the command line"
        super(CmdFileArgumentException, self).__init__(message)


class ParameterLookup:
    """
    A class which contains various dictionaries to help retrieving parameters
    by name or command line option
    """

    def __init__(self, params):
        self.opts = {}
        # Use an ordered dict to ensure that the positions of the arguments are preserved
        self.args = OrderedDict()
        self.names = {}
        self.num_arguments = 0
        for param in params:
            self.names[param.name] = param
            if isinstance(param, click.Option):
                for opt in param.opts + param.secondary_opts:
                    self.opts[opt] = param
            else:
                self.num_arguments += 1
                self.args[param.human_readable_name] = param

    def __getitem__(self, key):
        param = self.get_option("--" + key, "-" + key)
        if param is None:
            # In the help docs, an argument such as @click.argument("my-arg")
            # is represented as "MY_ARG", but will be stored in self.args as "my_arg", so
            # for ease of use we will allow argument keys to be case-insensitive
            param = self.get_argument(key, key.upper())
        if param is None:
            self.raise_not_found(key)
        return param

    def get_option(self, *keys):
        return self._sequential_lookup(self.opts, *keys)

    def get_argument(self, *keys):
        return self._sequential_lookup(self.args, *keys)

    def get_name(self, key):
        return self.names[key]

    def raise_not_found(self, key):
        possibilities = [p for p in self.opts if p.startswith("-" + key) or p.startswith("--" + key)]
        possibilities += [p for p in self.args if p.startswith(key)]
        raise click.NoSuchOption(key, possibilities=possibilities)

    @staticmethod
    def _sequential_lookup(lookup, *keys):
        keys = list(keys)
        ret = None
        while ret is None and keys:
            ret = lookup.get(keys.pop(), None)
        return ret


class CmdFileParser:
    """Parses a command file
    A command file can support both full and abbreviated options, but do not include the
    "--" prefix
    """

    def __init__(self, path, param_lookup):
        self.path = path
        self.param_lookup = param_lookup

    def parse(self):
        try:
            with open(self.path) as f:
                cmd_opts = yaml.safe_load(f)
        except FileNotFoundError:
            raise ExitException("File {} provided to {} does not exist".format(self.path, CMD_FILE_PARAM_NAME))
        options = {}
        arguments = {}
        for key, value in cmd_opts.items():
            param = self.param_lookup[key]
            if isinstance(param, click.Argument):
                # Use the human-readable name to account for metavar
                arguments[param.human_readable_name] = self._parse_argument(value, param)
            elif isinstance(param, click.Option):
                options[param.name] = self._parse_option(key, value, param)
        if arguments and len(arguments) != self.param_lookup.num_arguments:
            raise CmdFileArgumentException()
        return options, self.order_arguments(arguments)

    def order_arguments(self, arguments):
        # Arguments are not guaranteed to ordered appropriately in the command file,
        # so the order must be reconstructed from the args in the param lookup
        ret = []
        for reference_arg in self.param_lookup.args:
            arg = arguments.get(reference_arg, None)
            if isinstance(arg, list):
                ret += arg
            elif arg is not None:
                ret.append(arg)
        return ret

    def _parse_argument(self, value, param):
        if param.nargs != 1 and isinstance(value, str):
            return shlex.split(value)  # Use the shlex library to mimic shell parsing
        elif isinstance(value, list):
            return [str(v) for v in self._parse_nargs_list(value)]
        else:
            return str(value)

    def _parse_option(self, key, value, param):
        if param.is_flag:
            return self._parse_flag(key, value, param)
        elif param.nargs != 1 or param.multiple:
            if isinstance(value, str):
                return shlex.split(value)  # Use the shlex library to mimic shell parsing
            elif isinstance(value, list):
                return self._parse_nargs_list(value)
        else:
            return value

    @staticmethod
    def _parse_nargs_list(value):
        returned_val = []
        for elem in value:
            if isinstance(elem, str):
                returned_val.extend(shlex.split(elem))
            else:
                returned_val.append(elem)
        return returned_val

    @staticmethod
    def _parse_flag(key, value, param):
        """Parses both standard --flag and --on/--off switch style of flags
        This is complicated by the fact that the following values are accepted in the command file:
        - flag: False
        - flag: True
        - on: True
        - on: False
        - off: True
        - off: False
        This creates semantic difficulties.

        For a standard flag, the behavior depends on the default value. In click a flag with a
        default value of True becomes False when the flag is used, and a flag with a default value
        of False becomes True when the flag is used. In the command file, a value of True is
        interpreted to mean that the user wants to pass the flag into the command, which leads to
        the following truth table:

        Default | Value | Result
        -------------------------
        True    | True  | False
        True    | False | True
        False   | True  | True
        False   | False | False

        For switch-style flags, the behavior does not depend on the default value of the flag.
        Instead, using the --on/--off example, --on always results in True, and --off always
        results in False. Therefore, an "on: False" value in the command file is equivalent to
        "off: True", and an "off: False" value in the command file is equivalent to "on: True".
        The secondary name in this example is --off.
        This yields the following truth table (using the --on/--off example):

        Name | Secondary | Value | Result
        ---------------------------------
        on   | False     | True  | True
        on   | False     | False | False
        off  | True      | True  | False
        off  | True      | False | True
        """
        is_switch_flag = bool(param.secondary_opts)
        if not is_switch_flag:
            return value != param.default
        else:
            is_using_secondary = "--" + key in param.secondary_opts or "-" + key in param.secondary_opts
            return value != is_using_secondary


class CommandFormatter:
    """Formatter to convert a dictionary of {param_name: value} into equivalent
    command line arguments
    """

    def __init__(self, param_lookup):
        self.param_lookup = param_lookup

    def format_cli_options(self, options):
        args = []
        for arg, value in options.items():
            if value is None:
                continue
            param = self.param_lookup.get_name(arg)
            name = _longest_name(param)  # We do not use abbreviated options for aesthetic reasons
            if param.count:
                shortest_name = min(param.opts, key=len)
                stripped_name = shortest_name.lstrip("-")
                prefix = "-" * (len(shortest_name) - len(stripped_name))
                args.append(prefix + stripped_name * value)
            elif param.is_flag:
                self.format_flag(param, name, value, args)
            elif param.multiple:
                for m in value:
                    args += [name, m]
            elif param.nargs > 1:
                args.append(name)
                args += value
            else:
                args += [name, value]
        return args

    @staticmethod
    def format_flag(param, name, value, args):
        secondary_available = bool(param.secondary_opts)
        if not secondary_available:
            # Simple flags are only included in the command line arguments
            # when their value is different than the default.
            if value != param.default:
                args.append(name)
        else:  # We are using switch-style flags
            if not value:
                # If the value is False, then the secondary option was passed
                name = _longest_name(param, secondary=True)
            args.append(name)


class CmdFileOptionParser(OptionParser):
    """
    Modifies the click's OptionParser to merge in the args from the command file. To do this, we
    1. Use the original OptionParser to parse the options
    2. Extract the --from-file parameter
    3. If a command file is used:
      a. Parse the command file
      b. Merge the arguments from the command line with the arguments in the command file with the
         command line overriding the command file
      c. Reformat a new command line args from the merged params
    4. Use the original OptionParser to parse the new command line args
    """

    def __init__(self, param_lookup, ctx=None):
        self.param_lookup = param_lookup
        self.used_options = set()
        OptionParser.__init__(self, ctx=ctx)

    def parse_args(self, args):
        # _process_args_for_options modifies the arguments, so we need to make a copy of them so we
        # can use the original values later
        state = ParsingState(args[:])
        try:
            self._process_args_for_options(state)
        except click.UsageError:  # Copied from click
            if self.ctx is None or not self.ctx.resilient_parsing:
                raise

        cmd_file_path = state.opts.get(CMD_FILE_PARAM, None)
        write_cmd = state.opts.get(WRITE_CMD_FILE_PARAM, None)
        if write_cmd and not cmd_file_path:
            self.used_options = set(state.opts.keys())
        if cmd_file_path:
            cmd_file_opts, cmd_file_args = self.parse_cmd_file(cmd_file_path, state)
            opts, args = self.merge_params(cmd_file_opts, cmd_file_args, state)
            self.used_options = set(opts.keys())
            formatter = CommandFormatter(self.param_lookup)
            args = formatter.format_cli_options(opts) + ["--"] + args
        return OptionParser.parse_args(self, args)

    def parse_cmd_file(self, cmd_file_path, state):
        cmd_file_parser = CmdFileParser(cmd_file_path, self.param_lookup)
        cmd_file_opts, cmd_file_args = cmd_file_parser.parse()
        if cmd_file_args and (state.largs or state.rargs):
            # Arguments remaining in the command line after parsing the options are stored in
            # state.largs and state.rargs. We do not support args in both location because it
            # isn't possible to do partial overriding of positional arguments.
            raise CmdFileArgumentException()
        return cmd_file_opts, cmd_file_args

    def merge_params(self, cmd_file_opts, cmd_file_args, state):
        opts = cmd_file_opts
        opts.update(state.opts)
        args = (state.largs + state.rargs) or cmd_file_args
        return opts, args


class CmdFileOption(click.Option):
    def handle_parse_result(self, ctx, opts, args):
        value, args = super(CmdFileOption, self).handle_parse_result(ctx, opts, args)
        if not hasattr(ctx, "cmd_file_params"):
            ctx.cmd_file_params = {}
        ctx.cmd_file_params[self.name] = value
        return value, args


class CmdFileMixin:
    """Mixin used for both Commands and Groups to enable parsing command files"""

    def __init__(self):
        self.param_lookup = None
        self.convert_metavars()

    def convert_metavars(self):
        for param in self.params:
            if isinstance(param, click.Argument) and "_" in param.human_readable_name:
                if param.metavar is not None:
                    raise CmdFileUsageException("Cannot use '_'-delimited arguments. Use '-' and set metavar")
                else:
                    param.metavar = param.name.upper().replace("_", "-")

    def add_cmd_file_options(self):
        if self.params:
            click.option(
                CMD_FILE_PARAM_NAME,
                type=click.File(),
                help="A path to a YAML or JSON file to load the arguments and options from",
                expose_value=False,
                cls=CmdFileOption,
            )(self)
            click.option(
                WRITE_CMD_FILE_PARAM_NAME,
                type=click.Path(dir_okay=False, writable=True, readable=False),
                help="Save the arguments and options to this command to a file",
                expose_value=False,
                cls=CmdFileOption,
            )(self)

    def add_docs_option(self, docs):
        docs_option(docs)(self)

    def make_parser(self, ctx):
        self.param_lookup = ParameterLookup(self.params)
        self.cmd_parser = CmdFileOptionParser(
            self.param_lookup,
            ctx=ctx,
        )
        for param in self.get_params(ctx):
            param.add_to_parser(self.cmd_parser, ctx)
        return self.cmd_parser

    def write_cmd_file(self, ctx):
        cmd_file_params = getattr(ctx, "cmd_file_params", {})
        write_file = cmd_file_params.get(WRITE_CMD_FILE_PARAM, None)
        if write_file:
            self.write_params(ctx, write_file)

    def write_params(self, ctx, write_file):
        ret = {}
        for name, value in ctx.params.items():
            if value is None and not self.param_lookup.get_name(name).required:
                continue
            value = getattr(value, "name", value)  # Handles opened files click types
            param = self.param_lookup.get_name(name)
            if isinstance(param, click.Option):
                name = _longest_name(param).lstrip("-")
                if param.name not in self.cmd_parser.used_options:
                    continue
            else:
                name = param.human_readable_name.lower()
            if isinstance(value, str) and value[-1] == ":":
                # Add explicit quoting to avoid being misinterpreted as an object key
                value = '"{}"'.format(value)
            if isinstance(value, tuple):
                # By this point nargs and multiple params are tuples which makes
                # the generated YAML look strange when dumped
                value = list(value)
            ret[name] = value
        with open(write_file, "w") as f:
            yaml.dump(ret, f)


class CommandWithCmdFile(CmdFileMixin, click.Command):
    def __init__(self, *args, docs=None, **kwargs):
        click.Command.__init__(self, *args, **kwargs)
        CmdFileMixin.__init__(self)
        self.add_cmd_file_options()
        if docs:
            self.add_docs_option(docs)

    def parse_args(self, ctx, args):
        ret = click.Command.parse_args(self, ctx, args)
        self.write_cmd_file(ctx)
        return ret


class GroupWithCmdFile(CmdFileMixin, click.Group):
    def __init__(self, *args, use_cmd_file_params=True, docs=None, **kwargs):
        click.Group.__init__(self, *args, **kwargs)
        CmdFileMixin.__init__(self)
        self.validate_params(use_cmd_file_params)
        if use_cmd_file_params:
            self.add_cmd_file_options()
        if docs:
            self.add_docs_option(docs)

    def validate_params(self, use_cmd_file_params):
        for param in self.params:
            if param.nargs == -1:
                raise CmdFileUsageException("Cannot use nargs < 1 as an option or argument when using command files")
            if use_cmd_file_params and isinstance(param, click.Argument):
                raise CmdFileUsageException("Cannot use arguments in groups and enable command files")

    def parse_args(self, ctx, args):
        ret = click.Group.parse_args(self, ctx, args)
        self.write_cmd_file(ctx)
        return ret

    def command(self, *args, **kwargs):
        # identical to click implementation with command function swapped
        def decorator(f):
            cmd = command(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        # Identical to click implementation with group function swapped
        def decorator(f):
            cmd = group(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator
