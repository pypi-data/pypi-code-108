import re
from typing import Optional

import arrow
from arrow.arrow import Arrow
from arrow.parser import ParserMatchError
from bs4 import BeautifulSoup


def match_date(text: str) -> tuple[Optional[Arrow], Optional[str]]:
    date_found = None
    date_format = None

    try:  # with comma
        date_found = arrow.get(text, "MMMM D, YYYY")
        date_format = date_found.format("MMMM D, YYYY")

    except ParserMatchError:
        pass

    try:  # without comma
        date_found = arrow.get(text, "MMMM D YYYY")
        date_format = date_found.format("MMMM D YYYY")

    except ParserMatchError:
        pass

    return date_found, date_format


def process(raw: str):
    formatted_date = None
    item = raw.strip().title()

    date_found, original_format = match_date(raw)
    if date_found and original_format:
        formatted_date = date_found.format("MMMM D, YYYY")
        item = re.sub(original_format, "", raw)

    return {
        "publication": item.strip("(), ").title(),
        "date_of_publication": formatted_date,
    }


def parse_publications(raw: Optional[str]) -> list:
    if raw and ";" in raw:
        return [process(pub) for pub in raw.split(";")]
    elif raw and ";" not in raw:
        return [process(raw)]
    return []


def slice_publication_content(raw: str) -> str:
    """Get the first line found in the body, usually the publication string

    Args:
        raw (str): heading text,

    Returns:
        str: Possible publication string; can be an empty string since some laws do not have this filled out

    Example:
        >>> raw_html = "S. No. 61 H. No. 7090; 106 OG No. 34, 4661 (August 23, 2010); Philippine Star; Business Mirror, August 16, 2010<BR><BR><CENTER><H2 style='background-color:#cccccc;padding-top:10px;padding-bottom:10px;'>[ REPUBLIC ACT NO. 10142, July 18, 2010 ]</H2><H3>AN ACT PROVIDING FOR THE REHABILITATION OR LIQUIDATION OF FINANCIALLY DISTRESSED ENTERPRISES AND INDIVIDUALS</H3></CENTER>"
        >>> get_publications(raw_html)
        'S. No. 61 H. No. 7090; 106 OG No. 34, 4661 (August 23, 2010); Philippine Star; Business Mirror, August 16, 2010'
    """
    soup = BeautifulSoup(raw, "html5lib")

    # create a marker for slicing
    center_elem = soup.find("center")
    center_elem["id"] = "title-law"
    target_markup = str(center_elem)

    # convert soup to string
    html_markup = str(soup)

    # get the start index
    pre = "E-Library - Information At Your Fingertips: Printer Friendly"
    match = re.search(pre, html_markup)
    s = match.end() if match else 0

    # get the end index
    e = html_markup.index(target_markup)

    # get the slice based on the index
    sliced_text = html_markup[s:e]

    # convert slice back to soup and strip; note this can be empty
    html = BeautifulSoup(sliced_text, "html5lib")
    text = html.get_text().strip()

    return text


def get_publication_data(raw: str):
    text = slice_publication_content(raw)
    return parse_publications(text)
