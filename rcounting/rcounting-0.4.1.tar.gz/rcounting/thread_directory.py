import bisect
import copy
import itertools
import logging

from rcounting import models, parsing
from rcounting import side_threads as st
from rcounting import utils

printer = logging.getLogger(__name__)


def load_wiki_page(subreddit, location, kind="directory"):
    """
    Load the wiki page at reddit.com/r/subreddit/wiki/location

    Normalise the newlines, and parse it into a list of paragraphs.
    """
    wiki_page = subreddit.wiki[location]
    document = wiki_page.content_md.replace("\r\n", "\n")
    return Directory(parsing.parse_directory_page(document), kind)


def title_from_first_comment(submission):
    """
    Return the body of the first comment of the submission, appropriately normalised:

    - Markdown links are stripped.
    - Only the first line is considered.
    """
    comment = sorted(list(submission.comments), key=lambda x: x.created_utc)[0]
    body = comment.body.split("\n")[0]
    return parsing.normalise_title(parsing.strip_markdown_links(body))


class Row:
    """
    A class corresponding to a row in a markdown table in the directory.

    A row has the following information associated with it:
      - The human-readable name of the thread. E.g. 'No repeating digits'
      - The submission id of the first submission, used to identify the side thread
      - The title of the current submission in the thread
      - The id of the current submission in the thread
      - The id of the latest comment in the current submission
      - The total number of counts made in the thread

    The core of this class is the `update` method, which updates
    the last four pieces of information listed.
    """

    def __init__(self, name, first_submission, title, submission_id, comment_id, count):
        """
        Initialise a new row with all the necessary information. Associate a side
        thread object with the row.
        """
        self.archived = False
        self.name = name
        self.first_submission = first_submission
        self.title = parsing.normalise_title(title)
        self.initial_submission_id = submission_id
        self.initial_comment_id = comment_id
        self.count_string = count
        self.count = parsing.find_count_in_text(self.count_string.replace("-", "0"))
        self.is_approximate = self.count_string[0] == "~"
        self.starred_count = self.count_string[-1] == "*"
        self.thread_type = st.known_thread_ids.get(self.first_submission, fallback="default")
        self.submission = None
        self.comment = None

    def __str__(self):
        return (
            f"[{self.name}](/{self.first_submission}) | "
            f"[{self.title}]({self.link}) | {self.count_string}"
        )

    def order_tuple(self):
        """
        The order in which total counts should be compared.

        Tuple comparison works in the dictionary order, so a < b means that one
        of the following is true
          - a[0] < b[0]
          - a[0] == b[0] and a[1:] < b[1:]
        """
        return (self.count, self.starred_count, self.is_approximate)

    def __lt__(self, other):
        return self.order_tuple() < other.order_tuple()

    @property
    def submission_id(self):
        return self.submission.id if self.submission is not None else self.initial_submission_id

    @property
    def comment_id(self):
        return self.comment.id if self.comment is not None else self.initial_comment_id

    @property
    def link(self):
        """Set the full link if we have it, otherwise just link the submission."""
        if self.comment_id is not None:
            return f"/comments/{self.submission_id}/_/{self.comment_id}?context=3"
        return f"/comments/{self.submission_id}"

    def update_title(self):
        """
        Set the title of the current submission.

        If it's the first submission, set the title from the first comment.
        Otherwise, treat the submission title as a | delimited list and use all
        but the first section.

        Then normalise the title before setting it
        """
        if self.first_submission == self.submission.id:
            self.title = title_from_first_comment(self.submission)
            return
        sections = self.submission.title.split("|")
        if len(sections) > 1:
            title = "|".join(sections[1:]).strip()
        else:
            title = title_from_first_comment(self.submission)
        self.title = parsing.normalise_title(title)

    def update_count(self, chain, was_revival, side_thread):
        """
        Use the side thread get an updated tally of how many counts have been
        made in the thread, taking the revival status of each submission into account."""
        try:
            count = side_thread.update_count(self.count, chain, was_revival)
        except (ValueError, IndexError):
            count = None
        self.count_string = self.format_count(count)
        if count is not None:
            self.count = count
        else:
            self.starred_count = True

    def format_count(self, count):
        """Add asterisks and tildes to erroneous and approximate counts"""
        if count is None:
            return self.count_string + "*"
        if count == 0:
            return "-"
        if self.is_approximate:
            return f"~{count:,d}"
        return f"{count:,d}"

    def update(self, submission_tree, from_archive=False, deepest_comment=False):
        """Find the latest comment in the latest submission of the side thread
        represented by this row.

        Parameters:

        submission_tree: A models.Tree object representing which
        submissions are linked to which. If no mistakes have been made, this
        should just be a series of straight line chains

        from_archive: Whether the current side thread originally comes from the
        archive. If it does, a bit of care is needed when updating the total
        number of counts

        deepest_comment: A flag used to say that the function should find the
        deepest comment overall, rather than the leaf of the earliest valid chain.
        Earliest is defined according to the order

        a < b if a is an ancestor of b
        a < b if a and b have the same parent and a was posted before b
        a < b if π(a) < π(b), where π(a) is the oldest ancestor of a which is
        not an ancestor of b, and similarly for b.

        This is used for new threads, where non-count comments are frequently
        posted either as early top-level comments, or as replies to a top level
        comment.

        """
        side_thread = st.get_side_thread(self.thread_type)
        printer.debug("Updating side thread: %s", self.thread_type)
        if self.thread_type == "default":
            printer.warning(
                "No rule found for %s. Not validating comment contents. "
                "Assuming n=1000 and no double counting.",
                self.name,
            )

        chain = submission_tree.walk_down_tree(submission_tree.node(self.submission_id))
        self.submission = chain[-1]
        if submission_tree.is_archived(self.submission):
            self.archived = True

        if len(chain) > 1:
            self.initial_comment_id = None

        comments = models.CommentTree(reddit=submission_tree.reddit, get_missing_replies=False)
        if deepest_comment:
            for comment in self.submission.comments:
                comments.add_missing_replies(comment)
        elif self.comment_id is None:
            comment = next(filter(side_thread.looks_like_count, self.submission.comments))
            comments.add_missing_replies(comment)
        else:
            comment = submission_tree.reddit.comment(self.comment_id)
            comments.add_missing_replies(comment)
        comments.prune(side_thread, self.comment_id)
        if deepest_comment:
            comment = comments.deepest_node.walk_up_tree(limit=3)[-1]
        else:
            comment_chain = comments.walk_down_tree(comment)
            comment = comment_chain[-3 if len(comment_chain) >= 3 else 0]

        self.comment = comment
        was_revival = [parsing.is_revived(x.title) for x in chain]
        if from_archive:
            was_revival[1] = True
        if not all(was_revival[1:]):
            # If there's really a new thread, the title & count need updating
            self.update_count(chain, was_revival, side_thread)
            self.update_title()


class Paragraph:
    """A class to hold either a text paragraph, or a markdown table"""

    def __init__(self, tagged_text, kind="directory"):
        self.tag, self.contents = tagged_text
        if self.tag == "table":
            if not self.contents:
                self.contents = []
            self.contents = [Row(*x) if hasattr(x, "__iter__") else x for x in self.contents]
        self.kind = kind

    def update(self, tree):
        if self.tag == "text":
            return
        for row in self.contents:
            try:
                row.update(tree)
            except Exception:  # pylint: disable=broad-except
                printer.warning("Unable to update thread %s", row.title)
                raise

    def sort(self, *args, **kwargs):
        if self.tag != "text":
            self.contents.sort(*args, **kwargs)

    def __str__(self):
        if self.tag == "text":
            return self.contents
        labels = {"directory": "Current", "archive": "Last"}
        header = [
            "⠀" * 10 + "Name &amp; Initial Thread" + "⠀" * 10,
            "⠀" * 10 + f"{labels[self.kind]} Thread" + "⠀" * 10,
            "⠀" * 3 + "# of Counts" + "⠀" * 3,
        ]
        header = [" | ".join(header), ":--:|:--:|--:"]
        rows = self.contents
        if self.kind == "directory":
            rows = [x for x in self.contents if not x.archived]
        return "\n".join(header + [str(x) for x in rows])

    def is_misc_table_heading(self):
        return "new" in self.contents.lower() and "revived" in self.contents.lower()


class Directory:
    """A class to hold the state associated with the thread directory.

    At its core, the directory is a collection of paragraphs, each of which is
    either a table with information about side threads, or a text paragraph.

    Updating the directory means updating each paragraph, then checking for new
    submissions, and finally checking for revived submissions. There's a fair
    bit of fiddling to keep track of, which is why the whole thing is
    encapsulated in this class.

    """

    def __init__(self, paragraphs, kind="directory", archive=None):
        self.paragraphs = [Paragraph(x, kind) for x in paragraphs]
        self.known_submissions = {x.submission_id for x in self.rows}
        if archive is None:
            archive = {}
        self.archive = archive
        self.updated_archive = False
        self.header = paragraphs[0][1]

    @property
    def rows(self):
        return utils.flatten([x.contents for x in self.paragraphs if x.tag == "table"])

    @property
    def first_submissions(self):
        return [x.first_submission for x in self.rows]

    def __str__(self):
        return "\n\n".join(str(x) for x in self.paragraphs)

    def set_archive(self, archive):
        archive = {x.submission_id: x for x in archive.rows}
        self.archive = archive

    def update(self, tree, new_submission_ids):
        printer.info("Updating tables")
        self.update_existing_rows(tree)
        self.add_last_table()
        printer.info("Updating new threads")
        new_submissions = self.find_new_submissions(tree, new_submission_ids)
        printer.info("Finding revived threads")
        revived_submissions = self.find_revived_submissions(tree, new_submission_ids)
        self.paragraphs[-2].contents += new_submissions + revived_submissions
        self.paragraphs[-2].sort(key=lambda x: parsing.name_sort(x.name))
        for row in revived_submissions:
            del self.archive[row.submission_id]
            self.updated_archive = True
        archived_rows = [row for row in self.rows if row.archived]
        if archived_rows:
            self.updated_archive = True
            self.archive.update({row.submission_id: row for row in archived_rows})

    def update_existing_rows(self, tree):
        """Update every row in the main directory page and sort the second table"""
        table_counter = 0
        for paragraph in self.paragraphs:
            paragraph.update(tree)
            if paragraph.tag != "text":
                table_counter += 1
            if table_counter == 2:
                paragraph.sort(reverse=True)

    def add_last_table(self):
        if not self.paragraphs[-3].is_misc_table_heading():
            self.paragraphs = (
                self.paragraphs[:-1]
                + [Paragraph(["text", "\n## New and Revived Threads"]), Paragraph(["table", []])]
                + self.paragraphs[-1:]
            )

    def find_new_submissions(self, tree, new_submission_ids):
        """
        Make a list of update rows corresponding to new submissions

        If a row cannot be updated or, don't include it.
        The same goes for new submissions with only a few comments on them.
        """
        result = []
        for submission_id in new_submission_ids - self.known_submissions:
            first_submission = tree.walk_up_tree(submission_id)[-1]
            name = f'**{first_submission.title.split("|")[0].strip()}**'
            try:
                title = title_from_first_comment(first_submission)
            except IndexError:
                continue
            row = Row(name, first_submission.id, title, first_submission.id, None, "-")
            try:
                row.update(tree, deepest_comment=True)
            except Exception:  # pylint: disable=broad-except
                printer.warning("Unable to update new thread %s", row.title)
                raise
            n_authors = len(set(x.author for x in row.comment.walk_up_tree()))
            is_long_chain = row.comment.depth >= 50 and n_authors >= 5
            if is_long_chain or row.submission_id != first_submission.id:
                result.append(row)
        return result

    def find_revived_submissions(self, tree, new_submission_ids):
        """
        Make a list of updated rows corresponding to revived threads.

        If a row cannot be updated or, don't include it.
        The same goes for new submissions with only a few comments on them.
        """
        revivals = []
        revived_threads = {x.id for x in tree.leaves} - new_submission_ids - self.known_submissions
        for thread in revived_threads:
            chain = tree.walk_up_tree(thread)
            for submission in chain:
                if submission.id in self.archive:
                    row = copy.copy(self.archive[submission.id])
                    try:
                        row.update(tree, from_archive=True, deepest_comment=True)
                    except Exception:  # pylint: disable=broad-except
                        printer.warning("Unable to update revived thread %s", row.title)
                        raise
                    if row.comment.depth >= 20 or len(chain) > 2:
                        revivals.append(row)
                    break
        return revivals

    def archive2string(self):
        archived_rows = list(self.archive.values())
        printer.info("Updating archive at /r/counting/wiki/directory/archive")
        archived_rows.sort(key=lambda x: parsing.name_sort(x.name))
        splits = ["A", "D", "I", "P", "T", "["]
        titles = [f"\n### {splits[idx]}-{chr(ord(x) - 1)}" for idx, x in enumerate(splits[1:])]
        keys = [parsing.name_sort(x.name) for x in archived_rows]
        indices = [bisect.bisect_left(keys, (split.lower(),)) for split in splits[1:-1]]
        parts = [
            str(Paragraph(["table", x], kind="archive"))
            for x in utils.partition(archived_rows, indices)
        ]
        archive = list(itertools.chain.from_iterable(zip(titles, parts)))
        return "\n\n".join(archive[1:])
