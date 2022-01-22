import re
from typing import Any, Match, Optional, Union

import arrow
from bs4 import BeautifulSoup, NavigableString, PageElement


def lapse_date_mark(
    elem: PageElement,
) -> Union[bool, Match[Any], None]:
    LAPSE = r"Lapsed\s+into\s+law"
    return (
        isinstance(elem.next_element, NavigableString)
        and elem.next_element is not None
        and re.search(LAPSE, elem.next_element)
    )


def get_lapse_date_line(raw: str) -> Optional[str]:
    soup = BeautifulSoup(raw, "html5lib")
    mark = soup.find(lapse_date_mark)
    return str(mark.next_element) if mark else None
