import click
from rich import print as rprint

from pydragonfly import DragonflyException, TParams
from .._utils import (
    ClickContext,
    json_flag_option,
    add_options,
)
from ._renderables import _paginate_table, _generate_rule_table


@click.group("rule")
def rule():
    """
    Rule Management\n
    >>> [API] https://dragonfly.certego.net/api/rule\n
    >>> [GUI] https://dragonfly.certego.net/dashboard/rules
    """


@rule.command("list", help="List all rules")
@add_options(json_flag_option)
@click.pass_context
def rule_list(ctx: ClickContext, as_json: bool):
    ctx.obj._logger.info("Requesting list of rules..")
    ctx.obj._logger.info(f"[+] GUI: {ctx.obj._server_url}/dashboard/rules")
    params = TParams(ordering=["-created_at"])
    try:
        if as_json:
            response = ctx.obj.Rule.list(params=params)
            rprint(response.data)
        else:
            generator = ctx.obj.Rule.auto_paging_iter(params=params)
            _paginate_table(generator, _generate_rule_table)
    except DragonflyException as exc:
        ctx.obj._logger.fatal(str(exc))


@rule.command("retrieve", help="Retrieve rule object")
@click.argument("rule_id", type=int)
@click.pass_context
def rule_retrieve(ctx: ClickContext, rule_id: int):
    ctx.obj._logger.info(f"Requesting rule [underline blue]#{rule_id}[/]..")
    try:
        response = ctx.obj.Rule.retrieve(
            object_id=rule_id, params=TParams(expand=["user"])
        )
        rprint(response.data)
    except DragonflyException as exc:
        ctx.obj._logger.fatal(str(exc))
