import re

from bs4 import BeautifulSoup

from .elements import get_enacter_marker, get_signer_marker


def get_demarcated_data(text: str, context: str) -> dict:
    """Get three parts depending on the context.
    The context determines the classification.
    The classification determines what to use for markers of both enacter and signer clauses.

    Args:
        text (str): The full text of the law
        context (str): e.g. ra, bp, etc. Note that RAs, BPs are classified as "collegiate", EOs, PDs as "singular"

    Returns:
        dict: with the following keys
        1. raw: statute as marked
        2. enacter: the tag indicating the enacters in string format
        3. signer: the tag indicating the signers
    """

    soup = BeautifulSoup(text, "html5lib")

    flag = "singular" if context in ["pd", "eo"] else "collegiate"

    enacter_mark = get_enacter_marker(soup, flag)
    enacter_tag = None
    if enacter_mark:
        enacter_tag = soup.new_tag("p")
        enacter_tag["data-type"] = "enacter"
        enacter_mark.wrap(enacter_tag)

    signer_mark = get_signer_marker(soup, flag)
    signer_tag = None
    if signer_mark:
        signer_tag = soup.new_tag("p")
        signer_tag["data-type"] = "signer"
        signer_mark.wrap(signer_tag)

    return {
        "raw": str(soup),
        "enacter": str(enacter_tag) if enacter_tag else None,
        "signer": str(signer_tag) if signer_tag else None,
    }
