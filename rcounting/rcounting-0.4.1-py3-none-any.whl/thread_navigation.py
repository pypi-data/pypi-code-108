import datetime
import logging

from rcounting import models, parsing, reddit_interface

printer = logging.getLogger(__name__)


def find_previous_get(comment, validate_get=True):
    """
    Find the get of the previous reddit submission in the chain of counts.

    There's a user-enforced convention that the previous get should be linked
    in either the body of the submission, or the first comment.

    Usually this convention is followed, but sometimes this isn't done.
    Frequently, even in those cases the get will be linked in a different
    top-level comment.

    Parameterss:

    comment: A reddit comment instance in the child submission
    validate_get: Whether or not the prorgram should check that the linked comment ends in 000,
    and if not, try to find a nearby comment that does.
    """
    reddit = reddit_interface.reddit

    try:
        submission = comment.submission
    except AttributeError:
        comment = reddit.comment(comment)
        submission = comment.submission
    urls = filter(
        lambda x: int(x[0], 36) < int(submission.id, 36),
        parsing.find_urls_in_submission(submission),
    )
    new_submission_id, new_get_id = next(urls)

    while not new_get_id:
        try:
            new_submission_id, new_get_id = next(urls)
        except StopIteration:
            break
    if not new_get_id:
        new_get_id = find_deepest_comment(new_submission_id, reddit)
    comment = reddit.comment(new_get_id)
    if validate_get:
        new_get = find_get_from_comment(comment)
    else:
        new_get = reddit.comment(new_get_id)
    printer.debug(
        "Found previous get at: http://reddit.com/comments/%s/_/%s/",
        new_get.submission,
        new_get.id,
    )
    return new_get


def find_deepest_comment(submission, reddit):
    """
    Find the deepest comment on a submission
    """
    if not hasattr(submission, "id"):
        submission = reddit.submission(submission)
        submission.comment_sort = "old"
    comments = models.CommentTree(reddit=reddit)
    for comment in submission.comments:
        comments.add_missing_replies(comment)
    return comments.deepest_node.id


def search_up_from_gz(comment, max_retries=5):
    """Look for a count up to max_retries above the linked_comment"""
    for i in range(max_retries):
        try:
            count = parsing.post_to_count(comment)
            return count, comment
        except ValueError:
            if i == max_retries:
                raise
            comment = comment.parent()
    return None


def find_get_from_comment(comment):
    """Look for the get either above or below the linked comment"""
    count, comment = search_up_from_gz(comment)
    comment.refresh()
    replies = comment.replies
    replies.replace_more(limit=None)
    while count % 1000 != 0:
        comment = comment.replies[0]
        count = parsing.post_to_count(comment)
    return comment


def fetch_comments(comment):
    """
    Fetch a chain of comments from root to the supplied leaf comment.
    """
    reddit = reddit_interface.reddit
    tree = models.CommentTree([], reddit=reddit)
    comment_id = getattr(comment, "id", comment)
    comments = tree.comment(comment_id).walk_up_tree()[::-1]
    return [x.to_dict() for x in comments]


def fetch_counting_history(subreddit, time_limit):
    """
    Fetch all submissions made to r/counting within time_limit days
    """
    now = datetime.datetime.utcnow()
    submissions = subreddit.new(limit=1000)
    tree = {}
    submissions_dict = {}
    new_submissions = []
    for count, submission in enumerate(submissions):
        submission.comment_sort = "old"
        if count % 20 == 0:
            printer.debug("Processing reddit submission %s", submission.id)
        title = submission.title.lower()
        if "tidbits" in title or "free talk friday" in title:
            continue
        submissions_dict[submission.id] = submission
        urls = parsing.find_urls_in_submission(submission)
        try:
            url = next(filter(lambda x, s=submission: int(x[0], 36) < int(s.id, 36), urls))
            tree[submission.id] = url[0]
        except StopIteration:
            new_submissions.append(submission)
        post_time = datetime.datetime.utcfromtimestamp(submission.created_utc)
        if now - post_time > time_limit:
            break
    else:  # no break
        printer.warning(
            "Threads between %s and %s have not been collected", now - time_limit, post_time
        )

    return (
        models.SubmissionTree(submissions_dict, tree, reddit_interface.reddit),
        new_submissions,
    )
