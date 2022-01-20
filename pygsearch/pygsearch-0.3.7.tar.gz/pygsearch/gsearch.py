import requests
from bs4 import BeautifulSoup
from typing import Dict, List


class SearchResult:
    def __init__(self, title: str, link: str, description: str):
        self.title = title
        self.link = link
        self.description = description

    def prettify(self) -> str:
        return f"Link:  {self.link}\nTitle: {self.title}\nDescr: {self.description}\n"

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.link == other

        if isinstance(other, self.__class__):
            return self.link == other.link

        raise TypeError(f"Can't check equality of type '{self.__class__.__name__}' with type '{other.__class__.__name__}'")

    def __hash__(self) -> int:
        return hash(self.link)

    def __str__(self) -> str:
        return f"<SearchResult: title='{self.title}' link='{self.link}'>"

    def __repr__(self) -> str:
        return self.__str__()


class gsearch:
    def __init__(self, query: str = None, num: int = 10, lang: str = "en", headers: Dict[str, str] = None, proxies: Dict[str, str] = None):
        self.query = query
        self.num = num
        self.lang = lang
        self.headers = headers
        self.proxies = proxies
        self.results = None

        # If there is a query passed to the class, then search it and save the results
        if query:
            self.results = self.search(self.query, self.num, self.lang, self.headers, self.proxies)

    def search(self, query: str, results: int = 10, lang: str = "en", headers: dict = None, proxies: Dict[str, str] = None) -> List[SearchResult]:
        # Use default headers, if none are passed
        if not headers:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}

        # Google search url
        url = f"https://www.google.com/search?q={query}&num={results+1}&hl={lang}"
        response = requests.get(url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(response.text, "lxml")

        # Get all results
        elements = soup.find_all("div", {"class": "g"})

        # Parse each result and return the list of SearchResults
        out = []
        for element in elements:
            title = element.find("h3")
            if title:
                title = title.get_text()

            link = element.find("a")
            if link:
                link = link.get("href")

            description = element.find("div", {"data-content-feature": "1"})
            if description:
                description = description.get_text()

            out.append(SearchResult(title, link, description))

        return out
