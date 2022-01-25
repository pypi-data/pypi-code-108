from watchcat.filter.errors import FilterError
from .filter import Filter
import bs4


class CssSelectorFilter(Filter):
    def __init__(self, selector: str) -> None:
        self.selector = selector

    def filter(self, src: str) -> str:
        doc = bs4.BeautifulSoup(src, "html.parser")
        if element := doc.select_one(self.selector):
            return str(element)
        else:
            raise FilterError(f"element not found with this selector: {self.selector}")
