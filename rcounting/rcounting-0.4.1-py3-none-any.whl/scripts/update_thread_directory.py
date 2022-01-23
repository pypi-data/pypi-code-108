# pylint: disable=import-outside-toplevel
"""A script to update the thread directory"""
import datetime
import logging

import click

from rcounting import configure_logging

printer = logging.getLogger("rcounting")

incorrect_edges = [("r2h98h", "nyg22w")]


@click.command()
@click.option(
    "--dry-run", is_flag=True, help="Write results to files instead of updating the wiki pages"
)
@click.option("-v", "--verbose", count=True, help="Print more output")
@click.option("-q", "--quiet", is_flag=True)
def update_directory(quiet, verbose, dry_run):
    """
    Update the thread directory located at reddit.com/r/counting/wiki/directory.
    """

    from rcounting import thread_directory as td
    from rcounting import thread_navigation as tn
    from rcounting.reddit_interface import subreddit

    configure_logging.setup(printer, verbose, quiet)
    start = datetime.datetime.now()
    printer.info("Getting history")
    tree, new_submissions = tn.fetch_counting_history(subreddit, datetime.timedelta(days=187))
    for edge in incorrect_edges:
        tree.delete_edge(*edge)

    new_submission_ids = {tree.walk_down_tree(submission)[-1].id for submission in new_submissions}

    directory = td.load_wiki_page(subreddit, "directory")
    archive = td.load_wiki_page(subreddit, "directory/archive", kind="archive")
    directory.set_archive(archive)
    directory.update(tree, new_submission_ids)

    if not dry_run:
        subreddit.wiki["directory"].edit(str(directory), reason="Ran the update script")
    else:
        with open("directory.md", "w", encoding="utf8") as f:
            print(directory, file=f)

    if directory.updated_archive:
        archive = "\n\n".join([archive.header, directory.archive2string()])
        if not dry_run:
            subreddit.wiki["directory/archive"].edit(archive, reason="Ran the update script")
        else:
            with open("archive.md", "w", encoding="utf8") as f:
                print(archive, file=f)
    end = datetime.datetime.now()
    printer.info("Running the script took %s", end - start)


if __name__ == "__main__":
    update_directory()  # pylint: disable=no-value-for-parameter
