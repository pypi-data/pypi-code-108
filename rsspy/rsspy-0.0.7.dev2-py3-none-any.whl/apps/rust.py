from rss.base import Article, AnyNews
from typing import List
from rss.data.rust_doc_chapters import CHAPTERS
import random


class RustLangDoc(AnyNews):
    # Read, hopefully, two chapters each day
    def __init__(self,
                 main_url: str = 'https://doc.rust-lang.org/book/'):
        super().__init__(main_url)
        self.type += ':rustlang'

    def search_articles(self, _soup) -> List[Article]:
        return []

    def pipeline(self) -> List[Article]:
        two_chapters = random.sample(CHAPTERS, 2)
        articles = [
            Article(url=self.main_url + chapter, uid=chapter)
            for chapter in two_chapters
        ]
        return articles, articles
