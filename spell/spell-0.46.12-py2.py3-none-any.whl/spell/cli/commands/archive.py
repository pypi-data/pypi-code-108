import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.log import logger


@click.command(name="archive", short_help="Specify one or more Run IDs to archive")
@click.argument("run_ids", required=True, type=int, nargs=-1)
@click.option("-q", "--quiet", is_flag=True, help="Suppress logging")
@click.pass_context
def archive(ctx, run_ids, quiet):
    """
    Archive one or more runs.
    Use to remove a finished or failed run by specifying its RUN_ID.

    The removed runs will no longer show up in `ps`. The outputs of removed runs
    and removed uploads will no longer appear in `ls` or be mountable on
    another run with `--mount`.
    """
    client = ctx.obj["client"]

    logger.info("Archiving runs={}".format(run_ids))
    if len(run_ids) <= 0:
        logger.info("No valid run ids specified")
    elif len(run_ids) == 1:
        run_id = run_ids[0]
        with api_client_exception_handler():
            logger.info("Archiving run {}".format(run_id))
            client.archive_run(run_id)
        logger.info("Successfully archived run {}".format(run_id))
        if not quiet:
            click.echo(run_id)
    else:
        with api_client_exception_handler():
            logger.info("Archiving runs (batch) {}".format(run_ids))
            data = client.archive_runs(run_ids)
        logger.info("Succesfully archived runs {}".format(data["successful_run_ids"]))
        if not quiet:
            for msg in data["warning_messages"]:
                click.echo(msg, err=True, color="red")
            if len(data["non_existent_run_ids"]) > 0:
                click.echo(
                    "Run ID does not exist: {}".format(" ".join([str(i) for i in data["non_existent_run_ids"]])),
                    err=True,
                    color="red",
                )
            if len(data["successful_run_ids"]) > 0:
                click.echo(
                    "Successfully archived runs: {}".format(" ".join([str(i) for i in data["successful_run_ids"]]))
                )
