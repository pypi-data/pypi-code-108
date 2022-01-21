from bs4.element import ResultSet
from bs4 import BeautifulSoup
import requests
import os
import tqdm


class WikiDumpDownloader:
    def __init__(
        self,
        dir: str,
        base: str = "https://dumps.wikimedia.org",
        url: str = "https://dumps.wikimedia.org/enwiki/",
    ) -> None:
        """
        Wikipedia dump downloader for current page version
        (including Articles, templates, media/file descriptions,
        and primary meta-pages) in multiple bz2 streams(100 pages per stream)

            Parameters:
                base : str     Base URL to wikipedia dumps
                url  : str     URL to language-based wikipedia dumps
                dir  : str     Wikipedia dump directory  (example '20170701')

            Returns:
                None
        """
        self.DOWNLOAD_URL = url
        self.BASE_URL = base
        self.DUMP_DIRECTORY = dir

    def __str__(self) -> str:
        return "WikiDumpDownloader"

    def __repr__(self):
        return self.__str__()

    def get_page(self):
        """
        Fetch the webpage of the DUMP_DIRECTORY
        """
        # Retrieve the html
        try:
            dump_html = requests.get(self.DOWNLOAD_URL + self.DUMP_DIRECTORY).text
        except requests.exceptions.ConnectionError as e:
            print(f"[bold red] {e}")
            return
        return dump_html

    def parse_latest_links(self, page) -> list:
        """
        Parse the webpage of the dumps directory to look out
        for the multistream, current version dumps
        """
        # Convert to a soup
        if page is None:
            return
        soup_dump = BeautifulSoup(page, "html.parser")
        # Find list/'li' elements with the class 'done'.
        # In webpage, each section is a list element with class 'done'
        try:
            section = soup_dump.find_all("li", {"class": "done"})[1]
        except IndexError:
            return None
        # Inside section 1(for multistream current version),
        # find all 'li' elements which have anchor tags
        lists: ResultSet = section.find_all("li", {"class": "file"})
        links = []
        for item in lists:
            a = item.find("a")
            links.append(self.BASE_URL + a.get("href"))
        return links

    def fetch_dumps(self, num_files: int = None) -> None:
        """
        Fetch the dumps from the wikipedia dumps collection
        """
        page = self.get_page()
        links = self.parse_latest_links(page)
        if links is None or type(links) is not list or len(links) == 0:
            print("[yellow] Unable to find any link for downloading the dump\n")
            quit()

        link_total = len(links) if not num_files else num_files

        print(f"[blue] Total {link_total} files will be downloaded\n")

        for i, link in enumerate(links):
            if i > link_total:
                break
            filename = link.split("/")[-1]
            if not os.path.exists(filename):
                with open(filename, "wb") as f:
                    response = requests.get(link, stream=True)
                    total = response.headers.get("content-length")
                    if total is None:
                        f.write(response.content)
                    else:
                        total = int(total)

                        with tqdm.tqdm(
                            unit="B",
                            unit_scale=True,
                            desc=f"[{i+1}/{link_total}]: {filename}",
                            total=total,
                            dynamic_ncols=True,
                        ) as bar:
                            for data in response.iter_content(chunk_size=1000000):
                                f.write(data)
                                bar.update(len(data))
