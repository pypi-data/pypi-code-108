# coding=utf-8
import sys
import json, logging
import tornado
import tornado.ioloop
from .libs.singleton import BeanstalkCon
from .libs.beanstalk_route import BsRoute
from traceback import format_exc


class BeanstalkWorker(object):
    def __init__(self, **kwargs):
        self.ROOT = kwargs["ROOT"]
        self.beanstalk_config = kwargs["beanstalk_config"]
        self.workers_path = self.beanstalk_config.get("workers_dir", ["works/beanstalk"])
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.workers = BsRoute.get_workers(self.ROOT, self.workers_path)

        # 监听的tube的优先级：命令行参数>配置文件指定>消费者指定的所有tube（默认）
        if self.beanstalk_config.get("watch", []):
            self.watch = [watch for watch in self.beanstalk_config["watch"] if watch]
        else:
            self.watch = [event.tube for event in self.workers.values() if hasattr(event, "tube")]
        self.beanstalk_config["watch"] = self.watch
        self.beanstalk = BeanstalkCon.get_connection(**self.beanstalk_config)

    def watching(self):
        for i in self.watch: self.beanstalk.watch(i)
        logging.warning("current watching tubes: %s" % json.dumps(self.beanstalk.watching()))
        logging.warning("Beanstalk Client Running")


    def loop(self):
        job = self.beanstalk.reserve()
        try:
            body = json.loads(job.body)
        except Exception as e:
            logging.warning(format_exc())
            logging.error("event fail job: id=%s, body=%s" % (job.id, job.body))
        else:
            event = body.pop("__event__", None)
            classname, func = event.split(".")
            if classname not in self.workers:
                logging.error("event name %s not found!" % event)
                self.beanstalk.delete(job)
            else:
                try:
                    getattr(self.workers[classname], func)(body)
                except Exception as e:
                    logging.warning(format_exc())
                    logging.error("event fail job: id=%s, event=%s, body=%s" % (job.id, event, job.body))
                else:
                    logging.debug("success finish job: id=%s, event=%s, body=%s" % (job.id, event, job.body))
        finally:
            self.beanstalk.delete(job)

        self.ioloop.add_callback(self.loop)

    def start(self):
        self.watching()
        self.loop()
        self.ioloop.start()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    kwargs = {
        "ROOT": '/Users/lcylln/www/lcyframepy3/lcyframe3-demo',
        "beanstalk_config": {
            "host": "127.0.0.1",
            "port": 11300,
            "workers_dir": "/Users/lcylln/www/lcyframepy3/lcyframe3-demo/works/beanstalk"
        }}
    wk = BeanstalkWorker(**kwargs)
    wk.start()
