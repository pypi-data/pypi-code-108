import click

from spell.cli.exceptions import (
    api_client_exception_handler,
    # ExitException,
)


@click.command(name="label", short_help="Adds and remove labels from a run")
@click.argument("run_id")
@click.argument("label_name")
@click.option("--remove", is_flag=True, help="Remove input label from run")
@click.pass_context
def label(ctx, run_id, label_name, remove):
    """
    Used to add and remove labels from runs
    """

    with api_client_exception_handler():
        client = ctx.obj["client"]
        if remove:
            client.rm_label_for_run(run_id, label_name)
            click.echo("Successfully removed label {} from run {}.".format(label_name, run_id))
        else:
            client.add_label_for_run(run_id, label_name)
            click.echo("Successfully added label {} to run {}.".format(label_name, run_id))
