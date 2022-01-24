import json
import random
from typing import Dict, List, Tuple

import codefast as cf

from rss.apps.data import BLOG_SOURCES
from rss.base.urlparser import TextBody, UrlParser
from rss.core.tg import tcp

from rss.core import Initiator


class BlogTracker(object):
    def __init__(self, parser: UrlParser):
        self.parser = parser
        self.redis = Initiator.redis()

    def _query_new(self) -> Dict:
        soup = self.parser.fetch_soup()
        results = self.parser.parse(soup)
        return dict((key, value.dict()) for key, value in results.items())

    def _query_old(self) -> Dict:
        return json.loads(self.redis.get_key('rss_{}'.format(
            self.parser.name)))

    def _query_digest(self, old: Dict, new: Dict) -> List[Tuple]:
        # Get to be posted contents.
        diff = new.keys() - old.keys()
        if not diff:
            return random.sample([(k, v) for k, v in new.items()], 1)
        redis_key = 'rss_{}'.format(self.parser.name)
        cf.info('found new blog', str(diff))
        cf.info('results stored in redis', redis_key)
        new.update(old)
        self.redis.set_key(redis_key, json.dumps(new), ex=86400 * 30)
        return [(key, new[key]) for key in diff]

    def track(self) -> List[Dict]:
        q_new = self._query_new()
        q_old = self._query_old()
        digest = self._query_digest(q_old, q_new)
        return [d[1] for d in digest]

    def format(self, dict_: Dict) -> str:
        tb = TextBody(**dict_)
        return str(tb)


def main():
    for _, v in BLOG_SOURCES.items():
        parser = v['parser'](v['host'], v['url'])
        bt = BlogTracker(parser)

        for digest in bt.track():
            cf.info(bt.format(digest))
            tcp.post(bt.format(digest))
