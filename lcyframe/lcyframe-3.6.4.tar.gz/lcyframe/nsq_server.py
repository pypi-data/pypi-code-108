# coding=utf-8
import time, os, logging
import tornado.ioloop
from tornado.ioloop import IOLoop, PeriodicCallback
import nsq
from lcyframe.libs.nsq_route import NsqTask

class NsqWorker(object):
    def __init__(self, **kwargs):

        self.ROOT = kwargs["ROOT"]
        self.nsq_config = kwargs["nsq_config"]
        self.workers_path = self.nsq_config.get("workers_dir", ["works/nsq"])

        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.wait = 1
        self.workers = NsqTask.get_workers(self.ROOT, self.workers_path)
        self.has_start_works = {}

    def connect(self, workers):
        for name, work in workers.items():
            self.has_start_works[name] = work

            logging.info("%s [topic %s, channel %s] listen success!" % (name, work.topic, work.channel))
            nsq.Reader(message_handler=work.message_handler,
                       nsqd_tcp_addresses=self.nsq_config["nsqd_tcp_addresses"],
                       topic=work.topic,
                       channel=work.channel,
                       lookupd_poll_interval=self.nsq_config.get("lookupd_poll_interval", 15))

    def _reload_work(self):
        """

        :return:
        """
        print("auto load working..")
        NsqTask.get_workers(self.ROOT, self.workers_path)
        new_works = {}
        for name, work in self.workers.items():
            if name not in self.has_start_works:
                new_works[name] = work

        if new_works:
            self.connect(new_works)

    def start(self):
        self.connect(self.workers)
        # PeriodicCallback(self._reload_work, 1*1000, io_loop=self.ioloop).start()
        self.ioloop.start()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    kwargs = {"nsq_config": {
        "workers": ["workers"],
        "host": "127.0.0.1",
        "port": 6379,
        "name": "mq"
    }}
    wk = NsqWorker(**kwargs)
    wk.start()
