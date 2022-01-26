import random
import time

import codefast as cf

from rss.apps.huggingface import HuggingFace
from rss.apps.leiphone import LeiPhoneAI
from rss.apps.rust import RustLangDoc
from rss.base.wechat_public import create_rss_worker
from rss.base.wechat_rss import create_rss_worker as create_wechat_rss_worker
from rss.core.tg import tcp
from rss.tracker import main as blog_main


class Schedular(object):
    def __init__(self, shift_time: int = 3600, add_disturb: bool = True):
        # Add disturb to avoid multiple updates posted at exactly the same time
        self.shift_time = shift_time + \
            (random.randint(-1800, 3600) if add_disturb else 0)
        self.timer = 0

    def run(self):
        self.timer += 1
        if self.timer >= self.shift_time:
            cf.info("schedular: %s is running" % self.__class__.__name__)
            self.timer = 0
            self.action()

    def run_worker(self, worker):
        latest, all_ = worker.pipeline()
        if not latest:
            cf.info('no new articles')
        else:
            worker.save_to_redis(all_)
            cf.info('all articles saved to redis')
            for article in latest:
                cf.info(article)
                tcp.post(article.telegram_format())


class DailyBlogTracker(Schedular):
    def __init__(self, shift_time: int = 3600 * 24):
        super().__init__(shift_time=shift_time)

    def action(self):
        cf.info("DailyBlogTracker is running")
        blog_main()


class LeiPhoneAIRss(Schedular):
    def action(self):
        self.run_worker(LeiPhoneAI())


class HuggingFaceRss(Schedular):
    def action(self):
        self.run_worker(HuggingFace())


class RustLanguageDoc(Schedular):
    def action(self):
        self.run_worker(RustLangDoc())


class WechatPublicRss(Schedular):
    def __init__(self, shift_time: int = 3600, wechat_id: str = 'almosthuman'):
        super().__init__(shift_time=shift_time)
        self.worker = create_rss_worker(wechat_id)

    def action(self):
        self.run_worker(self.worker)


class WechatRssMonitor(Schedular):
    def __init__(self, shift_time: int = 3600, wechat_id: str = 'almosthuman'):
        super().__init__(shift_time=shift_time)
        self.worker = create_wechat_rss_worker(wechat_id)

    def action(self):
        self.run_worker(self.worker)


class SchedularManager(object):
    def __init__(self):
        self.schedulars = []
        self.timer = 0

    def add_schedular(self, schedular) -> Schedular:
        self.schedulars.append(schedular)
        return self

    def run(self):
        while True:
            for schedular in self.schedulars:
                schedular.run()
            time.sleep(1)
            self.timer += 1
            if self.timer >= 60:
                cf.info("SchedularManager is running")
                self.timer = 0


def rsspy():
    manager = SchedularManager()\
        .add_schedular(LeiPhoneAIRss(shift_time=3600))\
        .add_schedular(HuggingFaceRss(shift_time=3600))\
        .add_schedular(RustLanguageDoc(shift_time=3600 * 24))\
        .add_schedular(DailyBlogTracker(shift_time=3600 * 24))\
        .add_schedular(WechatPublicRss(shift_time=3600, wechat_id='huxiu'))\

    wechat_ids = ['almosthuman', 'yuntoutiao',
                  'aifront', 'rgznnds', 'infoq', 'geekpark']
    for wechat_id in wechat_ids:
        manager.add_schedular(WechatRssMonitor(10800, wechat_id))
    manager.run()


if __name__ == '__main__':
    from rss.base.wechat_rss import create_rss_worker
    worker = create_rss_worker('almosthuman')
    worker = create_rss_worker('yuntoutiao')
    latest, all_ = worker.pipeline()
    if not latest:
        cf.info('no new articles')
    else:
        worker.save_to_redis(all_)
        cf.info('all articles saved to redis')
        for article in latest:
            cf.info(article)
            tcp.post(article.telegram_format())
