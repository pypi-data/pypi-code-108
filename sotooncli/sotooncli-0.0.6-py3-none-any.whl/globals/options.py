import click
import yaml

from sotooncli.state import State
from sotooncli.utils import get_strerror


def get_params_from_file_option():
    def call_back(ctx, param, value):
        if value is None:
            return
        state = ctx.ensure_object(State)
        try:
            with open(value) as f:
                param_data = yaml.safe_load(f)
                state.load_params(param_data)
        except Exception as e:
            raise click.BadParameter(
                f"Could not open file: {value}: {get_strerror(e)}", ctx=ctx
            )

    option = click.Option(
        ["--params-file", "-f"],
        help="Path to YAML file for reading params.",
        callback=call_back,
        metavar="YAML_FILE",
    )
    return option
