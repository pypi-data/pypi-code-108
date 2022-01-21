# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class CeleryWorker(object):
    app = None

    def __init__(self, **kwargs):
        """
        消费者守护进程
        :param kwargs:
        """

        celery_config = kwargs.get("celery_config")
        if not celery_config or not celery_config.get("run", True):
            raise Exception("celery_config not found")
        self.name = celery_config.get("work_name_prefix", "celery_works_name")
        self.loglevel = celery_config.get("loglevel", "DEBUG")
        self.queue = celery_config.get("queue", "")    # q1,q2,q3
        self.concurrency = celery_config.get("concurrency")
        self.pool = celery_config.get("pool")

    def start(self):
        """
        Global Options:
          -A APP, --app APP
          -b BROKER, --broker BROKER
          --result-backend RESULT_BACKEND
          --loader LOADER
          --config CONFIG
          --workdir WORKDIR
          --no-color, -C
          --quiet, -q

        :param app:
        :return:
        """
        argv = [
            'worker',
            '--loglevel=%s' % self.loglevel,
            '-n=%s' % self.name,
        ]
        if self.queue:
            argv.append('-Q%s' % self.queue)
        if self.concurrency:
            argv.append('--concurrency=%s' % int(self.concurrency))
        if self.pool:
            argv.append('--pool=%s' % self.pool)
        if self.app is None:
            raise
        self.app.worker_main(argv)



if __name__ == "__main__":
    """
    每个CPU一个主进程，每个主进程开启8个线程并发执行。理论并发数量：CPU * 8。
    设定单个主进程单位时间内的允许执行的任务: --concurrency=10
    celery -A app worker -l info
    """

    CeleryWorker().start()