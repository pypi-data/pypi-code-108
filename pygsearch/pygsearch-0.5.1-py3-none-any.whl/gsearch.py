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
        self.results = []

        # If there is a query passed to the class, then search it and save the results
        if query:
            self.results = list(self.search(self.query, self.num, self.lang, self.headers, self.proxies))

    def search(self, query: str, results: int = 10, lang: str = "en", headers: dict = None, proxies: Dict[str, str] = None) -> List[SearchResult]:
        cleaned_query = query.replace(" ", "+")

        # Use default headers, if none are passed
        if not headers:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}

        # Google search url
        url = f"https://www.google.com/search?q={cleaned_query}&num={results*2+1}&hl={lang}"
        response = requests.get(url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(response.text, "lxml")

        # Get all results
        elements = soup.find_all("div", {"class": "g"})

        seen = []
        counter = 0
        for element in elements:
            if counter == results:
                break

            has_content = element.find_all("div", {"class": "g"})
            if has_content:
                element = has_content[0]

            title = element.find("h3")
            if title:
                title = title.get_text()

            link = element.find("a", href=True)
            if link:
                link = link.get("href")

            if not link.startswith("http"):
                continue

            description = element.find("div", {"data-content-feature": "1"})
            descr2 = element.find("div", {"class": "IsZvec"})
            if description:
                description = description.get_text()
            elif descr2:
                description = descr2.get_text()

            if not link in seen:
                yield SearchResult(title, link, description)
                counter += 1

            seen.append(link)

    def __iter__(self):
        self.index = 0
        self.max = len(self.results) - 1
        return self

    def __next__(self):
        if self.index <= self.max:
            out = self.results[self.index]
            self.index += 1
            return out

        raise StopIteration

    def __str__(self) -> str:
        return f"<gsearch: query='{self.query}' results={len(self.results)} lang='{self.lang}'>"

    def __repr__(self) -> str:
        return self.__str__()
