from rss.base import Article, AnyNews, DummyItem
from typing import List
import base64


class LeiPhoneAI(AnyNews):
    def __init__(self, main_url: str = 'https://leiphone.com/category/ai'):
        super().__init__(main_url)
        self.type += ':leiphone'

    def search_articles(self, soup) -> List[Article]:
        articles = []
        for div in soup.find_all('div', class_='word'):
            article = Article()
            title = div.find('a', class_='headTit') or DummyItem()
            date = div.find('div', class_='time') or DummyItem()
            author = div.find('a', class_='aut') or DummyItem()
            url = div.find('a').get('href')
            article = Article(title=title.text.strip(),
                              uid=base64.b64encode(
                                  url.encode('utf-8')).decode('utf-8'),
                              url=url,
                              author=author.text.strip(),
                              date=date.text.strip(),
                              extra_url=url)
            articles.append(article)
        return articles
