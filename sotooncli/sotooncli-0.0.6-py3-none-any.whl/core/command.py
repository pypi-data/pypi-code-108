from gettext import gettext as _

import click

from sotooncli import requests
from sotooncli.core.context import SotoonContext
from sotooncli.core.help_formatter import SotoonHelpFormatter
from sotooncli.core.param import SotoonArgument, SotoonParams
from sotooncli.core.response import ActionType, Response
from sotooncli.globals.config import ConfigOption
from sotooncli.globals.options import get_params_from_file_option
from sotooncli.globals.output_format import OutputFormatOption
from sotooncli.state import State


class SotoonCommand(click.Command):
    context_class = SotoonContext
    global_options = [
        ConfigOption(),
        get_params_from_file_option(),
        OutputFormatOption(),
    ]

    def __init__(
        self,
        name,
        capsule="",
        help="",
        args=None,
        opts=None,
        parent=None,
        callback=None,
    ):
        if args is None:
            args = []
        if opts is None:
            opts = []
        self.parent_opts = []
        self.parent_args = []
        if parent:
            self.parent_opts = parent.get_all_opts()
            self.parent_args = parent.get_args()
        self.args = args
        self.opts = opts
        self.capsule = capsule
        self.description = help
        self.name = name
        super().__init__(name=name, params=self.get_cli_params(), callback=callback)

    def get_cli_params(self):
        return self.args + self.get_all_opts() + self.global_options

    def get_branch_params(self):
        return self.args + self.get_all_opts() + self.parent_args

    def get_all_opts(self):
        return self.opts + self.parent_opts

    def get_args(self):
        return self.args

    def get_global_opts(self, ctx):
        opts = self.global_options
        help_option = self.get_help_option(ctx)

        if help_option is not None:
            opts.append(help_option)
        return opts

    @staticmethod
    def collect_global_options():
        return [f'[{click.style("GLOBAL OPTIONS ...", underline=True)}]']

    def format_help(self, ctx, formatter: SotoonHelpFormatter):
        self.format_name(ctx, formatter)
        self.format_synopsis(ctx, formatter)
        self.format_description(ctx, formatter)
        self.format_args(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_global_options(ctx, formatter)

    def format_name(self, ctx, formatter: SotoonHelpFormatter):
        with formatter.write_bold_heading(_("NAME")):
            formatter.write_text(f"{self.name} - {self.capsule}")

    def format_synopsis(self, ctx, formatter: SotoonHelpFormatter):
        pieces = self.collect_usage_pieces(ctx)
        formatter.write_usage(ctx.command_path, " ".join(pieces), "SYNOPSIS")

    def format_description(self, ctx, formatter: SotoonHelpFormatter):
        if self.description:
            with formatter.write_bold_heading(_("DESCRIPTION")):
                formatter.write_text(self.description)

    @staticmethod
    def _format_params(params, ctx, prefix, formatter: SotoonHelpFormatter):
        params_desc = []
        for param in params:
            rv = param.get_help_record(ctx)
            if rv is not None:
                params_desc.append(rv)

        if params_desc:
            with formatter.write_bold_heading(_(prefix)):
                formatter.write_dl(params_desc)

    def format_args(self, ctx, formatter: SotoonHelpFormatter):
        self._format_params(self.args, ctx, "ARGUMENTS", formatter)

    def format_options(self, ctx, formatter: SotoonHelpFormatter):
        self._format_params(self.get_all_opts(), ctx, "OPTIONS", formatter)

    def format_global_options(self, ctx, formatter: SotoonHelpFormatter):
        self._format_params(self.get_global_opts(ctx), ctx, "GLOBAL OPTIONS", formatter)


class GroupCommand(SotoonCommand, click.Group):
    command_class = SotoonCommand

    def __init__(self, name, help, capsule, args, opts, parent=None, execute=None):
        SotoonCommand.__init__(
            self,
            capsule=capsule,
            help=help,
            args=args,
            opts=opts,
            name=name,
            parent=parent,
            callback=execute,
        )
        click.Group.__init__(
            self, name=name, params=self.get_cli_params(), callback=execute
        )

    def collect_usage_pieces(self, ctx: SotoonContext):
        pieces = [click.style("COMMAND", underline=True)]
        for param in self.get_branch_params():
            pieces.extend(param.get_usage_pieces(ctx))
        pieces.extend(self.collect_global_options())
        return pieces

    def format_help(self, ctx, formatter: SotoonHelpFormatter):
        self.format_name(ctx, formatter)
        self.format_synopsis(ctx, formatter)
        self.format_description(ctx, formatter)
        self.format_commands(ctx, formatter)
        self.format_args(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_global_options(ctx, formatter)

    def format_commands(self, ctx, formatter: SotoonHelpFormatter):
        # This is mainly from click's code
        # TODO: check spacing

        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand, help))

            if rows:
                with formatter.write_bold_heading(_("COMMANDS")):
                    formatter.write_dl(rows)

    def command(self, *args, **kwargs):
        from .decorators import command

        if "cls" not in kwargs:
            kwargs["cls"] = ExecutableCommand

        def decorator(f):
            cmd = command(*args, **kwargs, parent=self)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        from .decorators import group

        if "cls" not in kwargs:
            kwargs["cls"] = GroupCommand

        def decorator(f):
            cmd = group(*args, **kwargs, parent=self)(f)
            self.add_command(cmd)
            return cmd

        return decorator


class ExecutableCommand(SotoonCommand):
    default_action = ActionType.OUTPUT

    def __init__(self, name, help, capsule, args, opts, parent, execute=None):
        SotoonCommand.__init__(
            self,
            capsule=capsule,
            help=help,
            args=args,
            opts=opts,
            name=name,
            parent=parent,
            callback=self.callback,
        )

        if execute:
            self.execute = execute

    def callback(self, **kwargs):
        ctx = click.get_current_context()
        state = ctx.find_object(State)
        kwargs["path"] = ctx.command_path.split(" ")[1:]
        kwargs["params"] = self._merge(state, ctx)
        kwargs["state"] = state
        kwargs["ctx"] = ctx
        self.execute(**kwargs)

    def _merge(self, state, ctx):
        merged = dict()
        for p in self.get_branch_params():
            if isinstance(p, SotoonParams):
                value = p.get_value(state, ctx)
                if p.is_required and value is None:
                    if isinstance(p, SotoonArgument):
                        cls = "Argument"
                    else:
                        cls = "Option"
                    raise click.BadParameter(f"{cls} {p.name} is required")
                merged[p.name] = value
            else:
                raise click.ClickException(f"Internal Error, type:{type(p)}")
        return merged

    def collect_usage_pieces(self, ctx: SotoonContext):
        pieces = []
        for param in self.get_branch_params():
            pieces.extend(param.get_usage_pieces(ctx))
        pieces.extend(self.collect_global_options())
        return pieces

    def execute(self, **kwargs):
        # mocked execute in tests
        result = requests.execute(kwargs["path"], kwargs["params"])
        resp = Response(result, state=kwargs["state"], ctx=kwargs["ctx"])
        resp.execute()
