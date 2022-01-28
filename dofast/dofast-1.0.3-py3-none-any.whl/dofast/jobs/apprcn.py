# -- coding:UTF-8
from contextlib import suppress

import codefast as cf
import joblib
import requests
from bs4 import BeautifulSoup

from dofast.network import Twitter
from dofast.toolkits.telegram import Channel


class AppRcn(Twitter):
    def __init__(self):
        super().__init__()
        self.web = requests.Session()
        self.web.headers.update({'User-Agent': "Chrome 79.0"})
        self.url = 'http://free.apprcn.com'
        self.cache = set()
        with suppress(FileNotFoundError):
            self.cache = joblib.load('/tmp/apprcn.joblib')

    def get_item_url(self, item_id: int = 0) -> str:
        '''Get id-th item from front page.
		return url of the item'''
        resp = self.web.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')
        url = soup.findAll('h2',
                           {'class': 'entry-title'})[item_id].a.attrs['href']
        return url

    def parse_text_from_item(self, url: str) -> str:
        soup = BeautifulSoup(self.web.get(url).text, 'lxml')
        text = ""
        article = soup.findAll('div', {'class': 'format_text'})[0]
        for p in article.findAll('p'):
            if '反斗限免' in p.text or 'apprcn' in p.text:
                break
            text += p.text + "\n"
            download_url = p.findAll('a')
            if download_url:
                href = download_url[0].attrs['href']
                if href not in text and 'apprcn' not in href:
                    text += href + "\n"
        return text

    def pick_first_item(self, item_id: int = 0):
        '''Parse the first free item and get text.'''
        url = self.get_item_url(item_id)
        if url in self.cache:
            cf.info('URL already parsed.')
            return ''
        self.cache.add(url)
        joblib.dump(self.cache, '/tmp/apprcn.joblib')
        text = self.parse_text_from_item(url)
        return text

    def get_text(self):
        return self.pick_first_item(0)

    def post_to_channel(self, text: str):
        Channel('cccache').post(text + '\n%23限免APP')

    @staticmethod
    def pipe():
        cli = AppRcn()
        text = cli.pick_first_item(0)
        cf.info('apprcn text:\n', text)
        if not text: return
        # cli.post_to_channel(text)
        cli.post_status(text + '\n#限免')


if __name__ == "__main__":
    AppRcn.pipe()
