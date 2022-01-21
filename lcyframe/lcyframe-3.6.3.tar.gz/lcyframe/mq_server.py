# coding=utf-8
import time, os, logging
import tornado
import tornado.ioloop
import tornadoredis
from tornado import gen
from .libs.mq_route import MqRoute
from .libs.hot_queue import key_for_name
from traceback import format_exc
import json

# 废弃
# 仅支持在tornado4.x版本工作，5.0以上删除了io_loop参数，导致报错：
# ERROR:root:TypeError("__init__() got an unexpected keyword argument 'io_loop'") waiting for 4s
# 链接池有缺陷，每次完成获取，需要手动释放：self.c.disconnect
# CONNECTION_POOL = tornadoredis.ConnectionPool(max_connections=500, wait_for_available=True)

class MqWorker(object):
    def __init__(self, **kwargs):

        self.ROOT = kwargs["ROOT"]
        self.mq_config = kwargs["mq_config"]
        self.name = self.mq_config["name"]
        self.workers_path = self.mq_config.get("workers_dir", ["works/mq"])
        self.c = tornadoredis.Client(host=self.mq_config.get("host", "127.0.0.1"),
                                     port=int(self.mq_config.get("port", 6379)),
                                     selected_db=int(self.mq_config.get("db", 0)))
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.name = key_for_name(self.name)
        self.wait = 1
        self.workers = MqRoute.get_workers(self.ROOT, self.workers_path)

    def connect(self):
        try:
            logging.debug("connect redis success!")
            self.c.connect()
            self.loop()
        except Exception as e:
            logging.error(repr(e) + " waiting for %ds" % self.wait)
            self.ioloop.add_timeout(time.time() + self.wait, self.connect)
            self.wait = min(self.wait * 2, 128)

    @gen.engine
    def loop(self):
        try:
            self.wait = 1
            res = yield gen.Task(self.c.blpop, self.name, 1)
            if res:
                msg = json.loads(str(res[self.name]))
                self.workers[msg["event"]](**msg)
                logging.debug("success finish job :%s" % repr(msg))
            self.ioloop.add_callback(self.loop)
        except Exception as e:
            logging.warning(format_exc())
            logging.error("%s loop error!" % repr(e))
            self.connect()

    def start(self):
        self.connect()
        self.ioloop.start()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    kwargs = {"mq_config": {
        "workers_dir": ["workers"],
        "host": "127.0.0.1",
        "port": 6379,
        "name": "mq"
    }}
    wk = MqWorker(**kwargs)
    wk.start()
