import click
import yaml

from sotooncli.config_utils import get_active_config_path
from sotooncli.state import State, StatefulParam
from sotooncli.utils import get_strerror


class ConfigOption(click.Option, StatefulParam):
    def __init__(self):
        click.Option.__init__(
            self,
            ["config", "--config"],
            help="Path to config file. [default: currently active config path]",
            callback=self.get_config,
            metavar="CONFIG_PATH",
        )
        StatefulParam.__init__(self, "config", self.type)
        self.active_config_path = None
        try:
            self.active_config_path = get_active_config_path()
        except Exception:
            return

    def get_config(self, ctx, param, config_path):
        state = ctx.ensure_object(State)
        if param.name in state.params and state.params[param.name] == config_path:
            return config_path
        elif param.name in state.params and config_path is None:
            return state.params[param.name]
        elif config_path is None and self.active_config_path:
            config_path = self.active_config_path
        elif config_path is None and self.active_config_path is None:
            return
        self.add_converted_to_state(state, config_path)
        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
                state.config = config_data
        except Exception as e:
            raise click.BadParameter(
                f"Could not open file: {config_path}: {get_strerror(e)}", ctx=ctx
            )
        return config_path
