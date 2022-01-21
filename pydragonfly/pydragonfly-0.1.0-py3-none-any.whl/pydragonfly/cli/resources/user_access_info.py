import click
from rich import print as rprint

from pydragonfly import DragonflyException
from .._utils import ClickContext


@click.command(help="Get user access info")
@click.pass_context
def access_info(ctx: ClickContext):
    try:
        response = ctx.obj.UserAccessInfo.get()
        rprint(response.data)
    except DragonflyException as exc:
        ctx.obj._logger.fatal(str(exc))
