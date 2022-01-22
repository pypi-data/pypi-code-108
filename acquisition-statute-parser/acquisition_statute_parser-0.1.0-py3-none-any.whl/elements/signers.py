import re
from typing import Any, Match, Optional, Union

from bs4 import BeautifulSoup, NavigableString, PageElement


def pre_singular_signer_mark(
    elem: PageElement,
) -> Union[bool, Match[Any], None]:
    """Get elements before the phrase 'Done in the City of Manila,'

    Args:
        elem (PageElement): bs4 required element placeholder, see docs

    Returns:
        bool: True for all elements matching the criteria
    """
    MANILA_INDICATOR = r"Done\s+in\s+the\s+City\s+of\s+Manila\,"
    return (
        isinstance(elem.next_element, NavigableString)
        and elem.next_element is not None
        and re.search(MANILA_INDICATOR, elem.next_element)
    )


def pre_collegiate_signer_mark(
    elem: PageElement,
) -> Union[bool, Match[Any], None]:
    """Get elements before the phrase 'Approved,'

    Args:
        elem (PageElement): bs4 required element placeholder, see docs

    Returns:
        bool: True for all elements matching the criteria
    """
    APPROVED_INDICATOR = r"Approved\,"
    return (
        isinstance(elem.next_element, NavigableString)
        and elem.next_element is not None
        and re.search(APPROVED_INDICATOR, elem.next_element)
    )


def get_signer_marker(
    soup: BeautifulSoup, classification: str
) -> Optional[PageElement]:
    """Get the element which marks the start of the 'signers' of the law.

    Args:
        soup (BeautifulSoup): The html markup of the whole statute
        classification (str): Flag which is either "collegiate" or "singular"

    Returns:
        Optional[PageElement]: The page element (representing the signer) to be used by the calling function
    """
    pre_marker = None

    if classification == "collegiate":
        pre_marker = soup.find(pre_collegiate_signer_mark)

    elif classification == "singular":
        pre_marker = soup.find(pre_singular_signer_mark)

    else:
        return None

    return pre_marker.next_element if pre_marker else None
