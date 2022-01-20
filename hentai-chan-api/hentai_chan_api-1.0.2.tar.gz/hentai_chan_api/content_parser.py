import json
import re
import requests
from bs4 import BeautifulSoup


class MangaContent:
    def __init__(self, session: requests.Session, manga_url: str):
        self._session = session
        self._url = manga_url

    @property
    def images(self) -> list[str]:
        raw_html = self._session.get(self._url, params={'development_access': 'true'}).content
        raw_js = BeautifulSoup(raw_html, 'html.parser').find_all('script')[2].text

        var_data = raw_js.replace('createGallery(data)', '').replace('    ', '').replace('\n', '').replace("'", '"')
        pattern = re.compile(r"var data = (\{.*?\})$", re.MULTILINE | re.DOTALL)

        if var_data:
            obj = pattern.search(var_data).group(1)
            obj = json.loads(obj)
            return obj['fullimg']
        else:
            return []
