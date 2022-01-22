from typing import Optional

from bs4 import BeautifulSoup, Tag

from acquisition_ruling_phrase.utils import (
    PATTERN,
    non_lowered_tagged_text_short,
)


def tagged_acquisition_ruling_phrases(t: Tag):
    """Short, no lower case, tag next to string"""
    return (
        non_lowered_tagged_text_short(t)
        and [inside for inside in (c for c in t.children) if inside.string]
        and PATTERN.search(t.get_text())
    )


def words_inside(tag: Tag) -> Optional[Tag]:
    """
    Some tags with rulings have words that disqualify it from becoming the
    start index. Remove these tags from the list based on looking for words
    that do not fall under the common style # see https://stackoverflow.com/a/25346119
    """
    words_in_tag = tag.get_text().lower().split()
    proper = [
        "ruling",
        "our",
        "this",
        "court",
        "court’s",
        "court's",
        "the",
        "of",
    ]  # note "courts"
    flagged_as_improper = [w for w in words_in_tag if w not in proper]
    return tag if not flagged_as_improper else None


def proper_words(html: BeautifulSoup) -> Optional[str]:
    """
    Get phrase to use as start of slice
    1. first check: does tag qualify?
    2. second check: does it contain only the proper words?
    """
    qualified = html(tagged_acquisition_ruling_phrases)
    if not qualified:
        return None

    proper = [tag for tag in qualified if words_inside(tag)]
    if not proper:
        return None

    return str(proper[0])
