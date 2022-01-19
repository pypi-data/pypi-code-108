import os
import threading
import time

from flask import request

CGROUP_ROOT = '/sys/fs/cgroup'
CGROUP_MEM = os.path.join(CGROUP_ROOT, 'memory/memory.usage_in_bytes')
CGROUP_CPU = os.path.join(CGROUP_ROOT, 'cpuacct/cpuacct.usage')
RESOURCE_FETCH_INTERVAL = 1

def enabled():
    return os.path.exists(CGROUP_MEM) and os.path.exists(CGROUP_CPU) and 'AML_DBG_RESOURCE_INFO' in os.environ

class WSGIRequest(object):
    def __init__(self, logger, inner_app):
        if not inner_app:
            raise Exception('WSGI application was required but not provided')
        self._inner_app = inner_app
        self.logger = logger
        self.lock = threading.Lock()
        self.usage_store = {'memory': 0, 'cpu': (0, 0), 'sample_time': (0, 1)}
        self.init_daemon_thread()

    def usage_fetcher(self):
        """
            memory: usage in MB
            cpu: tuple of accumulated cpu time in nanosecond for now and previous sample
        """

        cpu, sample_time = (0, 0), (0, time.time() * 1e9)
        while True:
            with open(CGROUP_MEM) as fin:
                memory = int(fin.read()) / 1e6
            with open(CGROUP_CPU) as fin:
                cpu_now = int(fin.read())
                cpu = (cpu[1], cpu_now)
                sample_time = (sample_time[1], time.time() * 1e9)
            with self.lock:
                self.usage_store.update({'cpu': cpu, 'memory': memory, 'sample_time': sample_time})
            time.sleep(RESOURCE_FETCH_INTERVAL)

    def init_daemon_thread(self):
        thread = threading.Thread(name='resource_usage_fetcher', target=self.usage_fetcher)
        thread.setDaemon(True)
        thread.start()

    def __call__(self, environ, start_response):

        def request_start_response(status_string, headers_array, exc_info=None):
            if 'isDebug' in request.headers:
                with self.lock:
                    cpu, memory, sample_time = self.usage_store['cpu'], self.usage_store['memory'], self.usage_store['sample_time']
                headers_array.append(('x-ms-aml-cpu-utilization', '{:.2%}'.format((cpu[1] - cpu[0]) / (sample_time[1] - sample_time[0]))))
                headers_array.append(('x-ms-aml-memory-footprint', '{:.2f} MB'.format(memory)))
            start_response(status_string, headers_array, exc_info)

        return self._inner_app(environ, request_start_response)
