import abc

import click
from rich.console import Console
from rich.table import Table


class Formatable(abc.ABC):
    @abc.abstractmethod
    def as_table(self) -> Table:
        pass

    @abc.abstractmethod
    def as_json(self) -> str:
        pass


def print_to_console(ctx: click.Context, formatable: Formatable):
    obj = ctx.obj or {}
    if 'console' not in obj:
        console = Console()
        obj['console'] = console
    console: Console = obj['console']
    output_format = obj.get('output', 'console')
    if output_format == "json":
        console.print(formatable.as_json(), highlight=False)
    elif output_format == "console":
        console.print(formatable.as_table())
    else:
        raise ValueError(f"unknown output format {output_format}")
