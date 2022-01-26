import redis
import sys
import os
import time
from hoocron_plugin import HoocronHookBase
from threading import Thread
from queue import Queue, Empty

class RedisHook(HoocronHookBase):
    def __init__(self):
        self.th = None
        self.redis_path = None
        self.redis_list = None
        self.redis = None # Redis connection
        self.sleep = 1
        self.jobs = list()
        self.q = None
        self.execute_q = None
        
        


    def add_argument_group(self, parser):

        def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'
        def_redis_list = 'hook'
        g = parser.add_argument_group('Redis hook')
        g.add_argument('--redis-job', '--rj', metavar='JOB', nargs='+', action='store', help='Jobs to bind with redis hook')
        g.add_argument('--redis', metavar='REDIS_URL', default=def_redis, help=f'Path to redis def: {def_redis}')
        g.add_argument('--redis-list', metavar='KEY', default=def_redis_list, help=f'name of redis key to trigger jobs. def: {def_redis_list}')

    def configure(self, jobs, args):
        self.redis = args.redis
        self.redis_list = args.redis_list
        self.sleep = args.sleep

        if args.redis_job:
            for name in args.redis_job:
                try:
                    j = jobs[name]
                except KeyError:
                    print("ERROR: Not found job", name)
                    sys.exit(1)
                self.jobs.append(j)

    def empty(self):
        return not bool(self.jobs)

    def thread(self):

        while True:

            try:
                cmd = self.q.get_nowait()
                if cmd == 'stop':
                    print("redis hook stopped")
                    return
            except Empty:
                pass

            request = self.redis.lpop(self.redis_list)
            if request is None:
                time.sleep(self.sleep)
            else:
                for j in self.jobs:
                    if j.name == request:
                        self.execute_q.put((j, 'redis'))

        
    def running(self):
        return bool(self.th)

    def start(self, execute_q):
        if self.jobs:
            self.redis = self.get_redis()
            self.q = Queue()
            self.execute_q = execute_q
            self.th = Thread(target = self.thread, args = () )
            self.th.start()
            print(f"started redis thread, watch list {self.redis_list!r}")
            
        else:
            print("Warning: do not start cron because no jobs assigned")


    def stop(self):
        print("stop redis hook")
        self.q.put('stop')


    def get_redis(self):
        return redis.Redis.from_url(self.redis, decode_responses=True)



hooks = [ RedisHook() ]
