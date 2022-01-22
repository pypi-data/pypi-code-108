import re

from bs4 import NavigableString, Tag

RULING_TEXT = r"""
    ^
    \s*
    (
        (Our\s+)?Ruling|
        (OUR\s+)?RULING|
        (The\s+)?Ruling\s+of\s+the\s+Court|
        RULING\s+OF\s+THE\s+COURT|
        The\s+Court[’']s\s+Ruling
    )
    \.?
    \s*
    $
"""

PATTERN = re.compile(RULING_TEXT, re.X)


def non_lowered_tagged_text_short(t: Tag) -> bool:
    """
    Used in both Ruling and Phrases to determine whether or not a tag looks like a section header
    1. <b>'s next elemnt is "So Ordered", the next element is a string rather than a tag
    2. "So Ordered" is more than 8 characters, less than 50, the navigable string is short
    3. "so ordered" is excluded; exclude cases like: (1) '<u>ruling</u> '; (2) <i>decision, order, or ruling</i>
    """
    text = t.get_text()
    count = len(text)
    return (
        isinstance(t.next_element, NavigableString)
        and (count > 5 and count < 50)
        and not text.islower()
    )
