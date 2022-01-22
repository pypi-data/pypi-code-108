import re

import arrow
from bs4 import BeautifulSoup


def clean(text: str) -> str:
    translation = str.maketrans({"\n": "", "\t": ""})
    return text.translate(translation).strip()


def slice_extra(soup: BeautifulSoup) -> str:
    body = str(soup)
    title = str(soup.find("h3"))
    idx = body.find(title) + len(title)
    raw_text = body[idx:]
    return clean(raw_text)


def get_numeral(numeric_title: str) -> str:

    parts = numeric_title.strip().split()

    candidate = parts[-1]

    if candidate == "[*]":
        numeral = parts[-2]

    elif candidate == "[1]":
        numeral = parts[-2]

    elif match := re.search(r"\d+\[\*\]", candidate):
        numeral = candidate.removesuffix("[*]")

    else:
        numeral = candidate

    return numeral


def get_date(text: str) -> str:
    date_found = arrow.get(text, "MMMM DD, YYYY")
    date_format = date_found.format("MMMM DD, YYYY")
    return date_format


def get_item(title_text: str, date_text: str) -> str:
    """The first h2 element in the soup is the numeric title of the law
    e.g. [ PRESIDENTIAL DECREE NO. 1458-A, June 11, 1978 ]

    Args:
        title_text (str): The title text, see example above
        date_text (str): The formatted date string found

    Returns:
        str: The title_text without other details, i.e. Presidential Decree No. 1458-A
    """
    text = clean(title_text)
    text_without_date = re.sub(date_text, "", text)
    return text_without_date.strip("[*], ").title()


def get_title_data(text: str) -> dict:
    """Given a the header portion of the text, get the necessary fields.

    Args:
        text (str): The text containing the title elements

    Returns:
        dict: With item, law_title, date, extra keys.
    """
    soup = BeautifulSoup(text, "html5lib")
    numeric_title = soup.find("h2").get_text()
    return {
        "law_title": soup.find("h3").get_text().title(),
        "date": (date_pub := get_date(numeric_title)),
        "item": (item := get_item(numeric_title, date_pub)),
        "numeral": (item := get_numeral(item)),
        "extra": slice_extra(soup),
    }
