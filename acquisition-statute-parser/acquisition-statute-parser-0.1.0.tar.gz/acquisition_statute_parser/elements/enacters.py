import re
from typing import Any, Match, Optional, Union

from bs4 import BeautifulSoup, NavigableString, PageElement


def pre_singular_enacter_mark(
    elem: PageElement,
) -> Union[bool, Match[Any], None]:
    """Get elements before the phrase 'NOW, THEREFORE, I'

    Args:
        elem (PageElement): [description]

    Returns:
        Optional[PageElement]: [description]
    """
    NOW_THEREFORE_MARK = r"NOW\,\s*THEREFORE\,\s*I\,"
    return (
        isinstance(elem.next_element, NavigableString)
        and elem.next_element is not None
        and re.search(NOW_THEREFORE_MARK, elem.next_element)
    )


def pre_collegiate_enacter_mark(
    elem: PageElement,
) -> Union[bool, Match[Any], None]:
    """Get elements before the phrase 'Be it enacted', etc.

    Args:
        elem (PageElement): [description]

    Returns:
        Optional[PageElement]: [description]
    """
    GENERAL_ENACTING_MARK = (
        r"^(Be\s+it\s+enacted)|(By\s+authority\s+of\s+the\s+United\s+States)"
    )
    return (
        isinstance(elem.next_element, NavigableString)
        and elem.next_element is not None
        and re.search(GENERAL_ENACTING_MARK, elem.next_element)
    )


def get_enacter_marker(
    soup: BeautifulSoup, classification: str
) -> Optional[PageElement]:
    """Get the element which marks the start of the 'enacters' of the law.

    Args:
        soup (BeautifulSoup): The html markup of the whole statute
        classification (str): Flag which is either "collegiate" or "singular"

    Returns:
        Optional[PageElement]: The page element (representing the enacter) to be used by the calling function
    """
    pre_marker = None

    if classification == "collegiate":
        pre_marker = soup.find(pre_collegiate_enacter_mark)

    elif classification == "singular":
        pre_marker = soup.find(pre_singular_enacter_mark)

    else:
        return None

    return pre_marker.next_element if pre_marker else None
