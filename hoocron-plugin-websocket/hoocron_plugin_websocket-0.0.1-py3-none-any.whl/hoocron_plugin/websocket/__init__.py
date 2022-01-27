import sys
import os
import time
from hoocron_plugin import HoocronHookBase
from threading import Thread
from queue import Queue, Empty

import socketio

# standard Python
sio = socketio.Client()

class WebsocketHook(HoocronHookBase):
    def __init__(self):
        self.th = None
        self.timeout = 2
        self.jobs = list()
        self.q = None
        self.execute_q = None
        self.name = 'websocket'
        
        
    def add_argument_group(self, parser):

        def_wsurl = os.getenv('WSURL') or 'http://localhost:8899/'
        def_jobs = os.getenv('WS','').split(' ')
        def_secret = os.getenv("WSSECRET", None)
        def_wsroom = os.getenv("WSROOM")

        g = parser.add_argument_group('Websocket hook')
        g.add_argument('--ws', metavar='JOB', nargs='+', action='store', default=def_jobs, 
            help='Jobs to bind with websocket')
        g.add_argument('--wsurl', metavar='WSURL', default=def_wsurl, 
            help=f'Websocket server URL def: {def_wsurl}')
        g.add_argument('--wsroom', metavar='ROOM', default=def_wsroom, 
            help=f'name of websocket room to trigger jobs. def: {def_wsroom}')
        g.add_argument('--wssecret', metavar='SECRET', default=def_secret, 
            help=f'name of websocket room to trigger jobs. def: {def_secret}')

    def configure(self, jobs, args):
        self.wsurl = args.wsurl
        self.wsroom = args.wsroom
        self.wssecret = args.wssecret

        if args.ws:
            for name in args.ws:
                if not name:
                    continue

                try:
                    j = jobs[name]
                except KeyError:
                    print("ERROR: Not found job", name)
                    sys.exit(1)
                self.jobs.append(j)

    def empty(self):
        return not bool(self.jobs)

    def thread(self):


        @sio.on('update')
        def on_update(data):
            for j in self.jobs:
                if j.name == data:
                    self.execute_q.put((j, 'websocket'))

        @sio.event
        def connect():
            print(f"Websocket connected to {self.wsurl}")
            sio.emit('join', {'room': self.wsroom, 'secret': self.wssecret})

        @sio.on('*')
        def catch_all(event, data):
            print(f"catch all event {event} data {data}")
            
        sio.connect(self.wsurl)

        while True:
            try:
                cmd = self.q.get_nowait()
                if cmd == 'stop':
                    print("websocket hook stopped")
                    return
            except Empty:
                time.sleep(1)
                pass
            



            """
            request = self.redis.lpop(self.redis_list)
            if request is None:
                time.sleep(self.sleep)
            else:
                for j in self.jobs:
                    if j.name == request:
                        self.execute_q.put((j, 'redis'))
            """

        
    def running(self):
        return bool(self.th)

    def start(self, execute_q):
        if self.jobs:
            self.q = Queue()
            self.execute_q = execute_q
            self.th = Thread(target = self.thread, args = () )
            self.th.start()
            print(f"started websocket thread, watch room {self.wsroom!r} on {self.wsurl}")
            
        else:
            print("Warning: do not start cron because no jobs assigned")


    def stop(self):
        print("stop websocket hook")
        self.q.put('stop')




hooks = [ WebsocketHook() ]
