# Copyright 2019 BMW Group
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import logging
import threading
import traceback

import gear

from zuul.lib.config import get_default


class ZuulGearWorker:

    def __init__(self, name, logger_name, thread_name, config, jobs,
                 worker_class=gear.TextWorker, worker_args=None):
        self.log = logging.getLogger(logger_name)

        self._running = True
        self.name = name
        self.worker_class = worker_class
        self.worker_args = worker_args if worker_args is not None else []

        self.server = config.get('gearman', 'server')
        self.port = get_default(config, 'gearman', 'port', 4730)
        self.ssl_key = get_default(config, 'gearman', 'ssl_key')
        self.ssl_cert = get_default(config, 'gearman', 'ssl_cert')
        self.ssl_ca = get_default(config, 'gearman', 'ssl_ca')

        self.gearman = None
        self.jobs = jobs

        self.thread = threading.Thread(target=self._run, name=thread_name)
        self.thread.daemon = True

    def start(self):
        gear_args = self.worker_args + [self.name]
        self.gearman = self.worker_class(*gear_args)
        self.log.debug('Connect to gearman')
        self.gearman.addServer(self.server, self.port, self.ssl_key,
                               self.ssl_cert, self.ssl_ca,
                               keepalive=True, tcp_keepidle=60,
                               tcp_keepintvl=30, tcp_keepcnt=5)
        self.log.debug('Waiting for gearman')
        self.gearman.waitForServer()
        self.register()
        self.thread.start()

    def register(self):
        self.log.debug('Registering %s jobs' % len(self.jobs))
        for job in self.jobs:
            self.gearman.registerFunction(job)

    def unregister(self):
        self.log.debug('Unregistering all jobs (%s)' % len(self.jobs))
        for job in self.jobs:
            try:
                self.gearman.unRegisterFunction(job)
            except KeyError:
                self.log.debug("Job %s already unregistered", job)

    def stop(self):
        self._running = False
        self.gearman.stopWaitingForJobs()
        self.thread.join()
        self.gearman.shutdown()

    def join(self):
        self.thread.join()

    def _run(self):
        while self._running:
            try:
                job = self.gearman.getJob()
                try:
                    if job.name not in self.jobs:
                        self.log.exception("Exception while running job")
                        job.sendWorkException(
                            traceback.format_exc().encode('utf8'))
                        continue
                    self.jobs[job.name](job)
                except Exception:
                    self.log.exception('Exception while running job')
                    job.sendWorkException(
                        traceback.format_exc().encode('utf-8'))
            except gear.InterruptedError:
                pass
            except Exception:
                self.log.exception('Exception while getting job')
