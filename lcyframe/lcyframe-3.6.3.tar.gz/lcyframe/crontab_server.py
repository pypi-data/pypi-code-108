# coding=utf-8
import logging

import tornado.ioloop

from .libs import tornado_crontab


class crontabs():
    def __init__(self, **kwargs):
        self.task = kwargs

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        for k, obj in self.task.items():
            tornado_crontab.CronTabCallback(obj, k).start()
        tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    tornado_crontab.CronTabCallback(lambda a: a, "* * * * *").start()
    tornado.ioloop.IOLoop.instance().start()