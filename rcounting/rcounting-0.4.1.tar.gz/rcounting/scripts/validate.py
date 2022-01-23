# pylint: disable=import-outside-toplevel
"""Validate the thread ending at COMMENT_ID according to the specified rule."""
import click

rule_dict = {
    "default": "default",
    "wait2": "wait 2",
    "wait3": "wait 3",
    "wait9": "wait 9",
    "wait10": "wait 10",
    "once_per_thread": "once per thread",
    "slow": "slow",
    "slower": "slower",
    "slowestest": "slowestest",
    "only_double_counting": "only double counting",
}


@click.command(no_args_is_help=True)
@click.option(
    "--rule",
    help="Which rule to apply. Default is no double counting",
    default="default",
    type=click.Choice(rule_dict.keys(), case_sensitive=False),
)
@click.argument("comment_id")
def validate(comment_id, rule):
    """Validate the thread ending at COMMENT_ID according to the specified rule."""
    import pandas as pd

    from rcounting import side_threads as st
    from rcounting import thread_navigation as tn
    from rcounting.reddit_interface import reddit

    comment = reddit.comment(comment_id)
    print(f"Validating thread: '{comment.submission.title}' according to rule {rule}")
    comments = pd.DataFrame(tn.fetch_comments(comment))
    side_thread = st.get_side_thread(rule_dict[rule])
    result = side_thread.is_valid_thread(comments)
    if result[0]:
        print("All counts were valid")
    else:
        print(f"Invalid count found at http://reddit.com{reddit.comment(result[1]).permalink}!")


if __name__ == "__main__":
    validate()  # pylint: disable=no-value-for-parameter
