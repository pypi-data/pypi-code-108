# pylint: disable=import-outside-toplevel,too-many-arguments,too-many-locals
"""Script for logging reddit submissions to either a database or a csv file"""
import logging
from datetime import datetime
from pathlib import Path

import click
import pandas as pd

printer = logging.getLogger("rcounting")


@click.command()
@click.argument("leaf_comment_id", default="")
@click.option("--all", "-a", "all_counts", is_flag=True)
@click.option("-n", "--n-threads", default=1, help="The number of submissions to log.")
@click.option(
    "--filename",
    "-f",
    type=click.Path(path_type=Path),
    help=(
        "What file to write output to. If none is specified, counting.sqlite is used as default in"
        " sql mode, and the base count is used in csv mode."
    ),
)
@click.option(
    "-o",
    "--output-directory",
    default=".",
    type=click.Path(path_type=Path),
    help="The directory to use for output. Default is the current working directory",
)
@click.option(
    "--sql/--csv",
    default=False,
    help="Write submissions to csv files (one per thread) or to a database.",
)
@click.option(
    "--side-thread/--main",
    "-s/-m",
    default=False,
    help=(
        "Log the main thread or a side thread. Get validation is "
        "switched off for side threads, and only sqlite output is supported"
    ),
)
@click.option("--verbose", "-v", count=True, help="Print more output")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Suppress output")
def log(
    leaf_comment_id,
    all_counts,
    n_threads,
    filename,
    output_directory,
    sql,
    side_thread,
    verbose,
    quiet,
):
    """
    Log the reddit submission which ends in LEAF_COMMENT_ID.
    If no comment id is provided, use the latest completed thread found in the thread directory.
    By default, assumes that this is part of the main chain, and will attempt to
    find the true get if the gz or the assist are linked instead.
    """
    from rcounting import configure_logging
    from rcounting import thread_directory as td
    from rcounting import thread_navigation as tn
    from rcounting import utils
    from rcounting.io import ThreadLogger
    from rcounting.reddit_interface import reddit, subreddit

    t_start = datetime.now()
    utils.ensure_directory(output_directory)

    if side_thread or (
        filename is not None
        and (n_threads != 1 or all_counts or Path(filename).suffix == ".sqlite")
    ):
        sql = True

    configure_logging.setup(printer, verbose, quiet)
    directory = td.load_wiki_page(subreddit, "directory")

    if not leaf_comment_id:
        comment = tn.find_previous_get(reddit.comment(directory.rows[0].comment_id))
    else:
        comment = reddit.comment(leaf_comment_id)
    printer.debug(
        "Logging %s reddit submission%s starting at comment id %s and moving backwards",
        "all" if all_counts else n_threads,
        "s" if (n_threads > 1) or all_counts else "",
        comment.id,
    )

    threadlogger = ThreadLogger(sql, output_directory, filename)
    completed = 0

    while (not all_counts and (completed < n_threads)) or (
        all_counts and comment.submission.id != threadlogger.last_checkpoint
    ):
        printer.info("Logging %s", comment.submission.title)
        completed += 1
        if not threadlogger.is_already_logged(comment):
            df = pd.DataFrame(tn.fetch_comments(comment))
            threadlogger.log(comment, df)
        else:
            printer.info("Submission %s has already been logged!", comment.submission.title)

        if comment.submission.id in directory.first_submissions:
            break

        comment = tn.find_previous_get(comment, validate_get=not side_thread)

    if completed and (
        comment.submission.id in directory.first_submissions + [threadlogger.last_checkpoint]
    ):
        threadlogger.update_checkpoint()

    if completed == 0:
        printer.info("The database is already up to date!")
    printer.info("Running the script took %s", datetime.now() - t_start)


if __name__ == "__main__":
    log()  # pylint: disable=no-value-for-parameter
