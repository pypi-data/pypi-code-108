import re
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

from .demarcator import get_demarcated_data
from .elements import get_lapse_date_line, get_publication_data, get_title_data
from .sanitizer import statute_sanitizer
from .sections import list_sections


def cull_footer(text: str) -> str:
    """Remove dividing text that are unnecessary for parsing the law

    Args:
        text (str): the full content

    Returns:
        str: the stringified html markup with the unnnecessary parts removed
    """
    soup = BeautifulSoup(text, "html5lib")
    for ender in soup("hr"):  # see cases like 86448
        [i.decompose() for i in ender.next_siblings if isinstance(i, Tag)]
        ender.decompose()

    return str(soup)


def set_data(data: dict) -> Optional[dict]:
    """Presumes previous demarcation function has been applied, resulting in a data dictionary.
    The data dictionary can be used in the `acquisition` library.

    Args:
        data (dict): Consists of demarcations for: (1) raw text, (2) enacter text, and (3) signer text.

    Returns:
        Optional[dict]: If processed properly, a dictionary of fields.
    """

    # initialize
    content = data["raw"]
    header_portion = None
    enacting_clause = None
    signing_clause = None
    lapse_date_line = None
    units = []

    # since content has been demarcated, get the enacter phrase, if it exists
    # the text until the enacter phase is the header portion
    if enacter := data["enacter"]:
        enacter_start_idx = content.find(enacter)
        enacter_end_idx = enacter_start_idx + len(enacter)
        header_portion = content[:enacter_start_idx]
        enacting_clause = content[enacter_start_idx:enacter_end_idx]

    # since content has been demarcated, get the signer phrase, if it exists
    # the text may include the "lapse into law line"
    if signer := data["signer"]:
        signer_idx = content.find(signer)
        signing_clause = content[signer_idx:]
        lapse_date_line = get_lapse_date_line(signing_clause)

    # if the main clauses are found in the content, can remove these to get the gist
    # the gist is necessary to secure unit "sections"
    if enacting_clause and signing_clause:
        start = content.find(enacting_clause) + len(enacting_clause)
        end = content.find(signing_clause)
        content = content[start:end]
        units = list_sections(content)

    if not header_portion:
        return None

    return {
        "publications": get_publication_data(header_portion),
        "statute_gist": content,
        "enacting_clause": enacting_clause,
        "signers_of_law": signing_clause,
        "lapse_into_law_clause": lapse_date_line,
        "units": units,
    } | get_title_data(header_portion)
