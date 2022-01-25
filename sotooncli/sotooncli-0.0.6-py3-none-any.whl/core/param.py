import click

from sotooncli.core.context import SotoonContext
from sotooncli.state import State, StatefulParam

DEFAULT_PARAM_MSG = " This parameter is required."


class SotoonParams(StatefulParam):
    def __init__(self, name, placeholder, description, is_required, default_value):
        StatefulParam.__init__(self, name=name, type=self.type)
        self.metavar = placeholder
        self.callback = self.save_to_state
        self.expose_value = True

        # Added:
        self.is_required = is_required
        self.description = (
            f"{description}{'' if default_value is None else f' [default:  {default_value}]'}"
            f"{'' if not self.is_required else f' {DEFAULT_PARAM_MSG}'}"
        )
        self.help = self.description
        self._default = default_value

    def save_to_state(self, ctx, _, value):
        state = ctx.ensure_object(State)
        self.add_converted_to_state(state, value)
        return value

    def get_value(self, state, ctx):
        if self.name in state.params:
            return self.get_param_value_from_state(state, ctx)
        elif state.config and self.name in state.config:
            return self.get_config_value_from_state(state, ctx)
        else:
            return self._default

    def make_metavar(self):
        raise NotImplementedError

    def get_usage_pieces(self, ctx):
        return [self.make_metavar()]

    def get_help_record(self, ctx: SotoonContext):
        return ", ".join(self.param_dcl[1:]), self.description


class SotoonArgument(SotoonParams, click.Argument):
    def __init__(
        self,
        name,
        placeholder,
        param_type=click.STRING,
        description="",
        is_required=False,
        default_value=None,
    ):
        # make sure that Argument is shown in usage
        if placeholder == "":
            placeholder = name.upper()
        click.Argument.__init__(self, [name], required=False, type=param_type)
        SotoonParams.__init__(
            self, name, placeholder, description, is_required, default_value
        )

    def make_metavar(self):
        metavar = f"{click.style(self.metavar, underline=True)}"
        if not self.is_required:
            return f"[{metavar}]"
        return metavar

    def get_help_record(self, ctx: SotoonContext):
        return self.make_metavar(), self.description


class SotoonOption(SotoonParams, click.Option):
    def __init__(
        self,
        name,
        placeholder,
        description,
        is_required,
        default_value,
        param_type,
        short_name=None,
    ):
        self.param_dcl = [name, f"--{name}"]
        self.param_dcl.append(f"-{short_name}") if short_name else None
        click.Option.__init__(self, self.param_dcl, type=param_type)
        SotoonParams.__init__(
            self, name, placeholder, description, is_required, default_value
        )

    def make_metavar(self):
        metavar = f"{click.style(self.param_dcl[1], bold=True)}={click.style(self.metavar, underline=True)}"
        if not self.is_required:
            return f"[{metavar}]"
        return metavar


class SotoonBooleanFlag(click.Option, SotoonParams):
    def __init__(
        self,
        name,
        placeholder,
        description,
        is_required,
        default_value,
        short_name=None,
    ):
        self.param_dcl = [name, f"--{name}/--no-{name}"]
        self.param_dcl.append(f"-{short_name}") if short_name else None
        # No type needed for this kind of bool option, this is fixed in click 8.0 (issue no.: #1287)
        click.Option.__init__(self, self.param_dcl, help=description)
        SotoonParams.__init__(
            self, name, placeholder, description, is_required, default_value
        )

    def get_default(self, _):
        # Override this from click.Option to prevent casting None to False for boolean options without default value.
        # Default value overwriting is handled in SotoonParam.
        return None

    def make_metavar(self):
        metavar = click.style(self.param_dcl[1], bold=True)
        if not self.is_required:
            return f"[{metavar}]"
        return metavar
