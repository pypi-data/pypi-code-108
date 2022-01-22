from bs4 import NavigableString, Tag

from acquisition_ruling_phrase.utils import PATTERN


def center_next_tag(t: Tag):
    return (
        t.name == "center"
        and isinstance(t.next_element, Tag)
        and PATTERN.search(t.text)
        and (t.next_element.name == "strong" or t.next_element.name == "em")
        and len(t.text.strip()) < 25  # text is short
    )


def center_next_string(t: Tag):
    return (
        t.name == "center"
        and isinstance(t.next_element, NavigableString)
        and PATTERN.search(t.text)
        and len(t.text.strip()) < 25
    )


def p_strong(t: Tag):
    # re: center in attrs... this deals with odd <p align="“center”">
    return (
        t.name == "p"
        and t.attrs.get("align")
        and "center" in t.attrs.get("align")
        and isinstance(t.next_element, Tag)
        and t.next_element.name == "strong"
        and PATTERN.search(t.text)
        and len(t.text.strip()) < 25
    )


def p_space_strong(t: Tag):
    # re: center in attrs... this deals with odd <p align="“center”">
    return (
        t.name == "p"
        and t.attrs.get("align")
        and "center" in t.attrs.get("align")
        and isinstance(t.next_element, NavigableString)
        and len(str(t.next_element).strip()) == 0
        and isinstance(t.next_element.next_element, Tag)
        and t.next_element.next_element.name == "strong"
        and PATTERN.search(t.text)
        and len(t.text.strip()) < 25
    )
