import codecs
from pathlib import Path
from typing import Optional

import httpx

from acquisition_statute_parser import parse

from .sanitizer import statute_sanitizer


def sanitize_content(raw: str):
    """Product uniform html tags

    Args:
        raw (str): Raw text fetched

    Returns:
        [type]: Raw text cleaned
    """
    return statute_sanitizer.sanitize(raw)


def raw_from_url(idx: int, statute_type: Optional[int]) -> str:
    """The supplied `idx` completes the url

    Args:
        idx (int): [description]
        statute_type (Optional[int]): If not supplied, the default is 2 for RAs

    Returns:
        str: [description]
    """
    if not statute_type:
        statute_type = 2
    base = f"https://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly"
    url = f"{base}/{statute_type}/{idx}"
    response = httpx.get(url, verify=False)
    return response.text


def get_context(statute_type: int) -> str:
    """Peculiar mapping of URL string to human readable context, used as a folder

    Args:
        statute_type (int): A number which maps to a URL path

    Returns:
        str: The local folder to use in context
    """
    if statute_type == 2:
        folder = "ra"

    elif statute_type == 3:
        folder = "const"

    elif statute_type == 26:
        folder = "pd"

    elif statute_type == 5:
        folder = "eo"

    elif statute_type == 25:
        folder = "bp"

    elif statute_type == 29:
        folder = "ca"

    elif statute_type == 28:
        folder = "act"

    return folder


def raw_to_file(idx: int, statute_type: int = 2) -> None:
    """Create an html file in a local directory determined by the parameters

    Args:
        idx (int): The identifier from the source URL
        statute_type (int, optional): [description]. Defaults to 2.
    """

    # if the path already exists, no need to create
    p = Path(".") / "tests" / "data" / f"{get_context(statute_type)}"
    if not p.exists():
        p.mkdir()

    # if the file already exists, no need to proceed
    target_file = p / f"{idx}.html"
    if target_file.exists():
        print(f"Already existing {idx}.html. No need to scrape.")
        return

    target_file.write_text(raw_from_url(idx, statute_type))


def get_content_from_file(loc: Path, idx: int, statute_type: int):
    p = loc / f"{get_context(statute_type)}"
    if not p.exists():
        print(f"Not found: {str(p)}")
        return

    # if the file already exists, no need to proceed
    target_file = p / f"{idx}.html"
    if not target_file.exists():
        print(f"Not found: {str(target_file)}")

    return target_file.read_text()


def sanitize_html_file(p: Path) -> str:
    """Get text from folder

    Args:
        p (Path): Location of the text

    Returns:
        str: The raw content
    """
    with codecs.open(str(p), "r") as f:  # codecs uses string
        return sanitize_content(f.read())


def cleaned_from_file(filename: str, context: str) -> Optional[dict]:
    """Source content from the tests / data folder to produce a data dictionary

    Args:
        filename (str): [description]

    Returns:
        [type]: [description]
    """
    p = Path(".") / "tests" / "data" / f"{filename}.html"
    if not p.exists():
        print(f"Not found: {str(p)}")
        return None
    raw = sanitize_html_file(p)
    data = parse(raw, context)
    return data
