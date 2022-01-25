from .filter import Filter
import bs4


class TextContentFilter(Filter):
    def filter(self, src: str) -> str:
        return bs4.BeautifulSoup(src, "html.parser").text
