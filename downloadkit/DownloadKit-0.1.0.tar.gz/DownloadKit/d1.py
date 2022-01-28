# -*- coding:utf-8 -*-
from collections import deque
from threading import Thread
from time import sleep, perf_counter


class Downloader:
    def __init__(self):
        self._size = 3
        self.missions = deque()
        self.threads = {i: None for i in range(self._size)}
        self.任务管理线程 = None
        self.线程管理线程 = None
        self.信息显示线程 = None

    def show(self):
        if self.信息显示线程 is None or not self.信息显示线程.is_alive():
            self.信息显示线程 = Thread(target=self._show)
            self.信息显示线程.start()

    def _show(self):
        # while True:
        while self.is_running():
            txt = [f'{k} {v}\n' for k, v in self.threads.items()]
            print(''.join(txt) + '\n', flush=False)
            sleep(.5)
        # print('显示进程停止', flush=False)

    def go(self):
        if self.任务管理线程 is None or not self.任务管理线程.is_alive():
            print('任务线程启动', flush=False)
            self.任务管理线程 = Thread(target=self._missions_manage)
            self.任务管理线程.start()

        if self.线程管理线程 is None or not self.线程管理线程.is_alive():
            print('管理线程启动', flush=False)
            self.线程管理线程 = Thread(target=self._threads_manage)
            self.线程管理线程.start()

    def add(self, data):
        self.missions.append(data)
        self.go()

    def _missions_manage(self):
        t1 = perf_counter()
        while self.missions or perf_counter() - t1 < 2:
            if self.missions:
                num = self._get_usable_thread()
                msg = {'thread': None,
                       'result': None,
                       'info': None,
                       'close': False,
                       'data': self.missions.popleft(),
                       'state': None}
                thread = Thread(target=self.download, args=(msg,))
                msg['thread'] = thread
                thread.start()
                self.threads[num] = msg

        print('任务管理线程停止', flush=False)

    def _get_usable_thread(self):
        """获取可用线程"""
        while True:
            for k, v in self.threads.items():
                if v is None:
                    return k

    def _threads_manage(self):
        """负责把完成的线程清除出列表"""
        t1 = perf_counter()
        while True:
            for k, v in self.threads.items():
                if isinstance(v, dict) and not v['thread'].is_alive():
                    # TODO: 保存结果
                    self.threads[k] = None

            if perf_counter() - t1 > 2 and not self.is_running():
                break

        print('管理线程停止', flush=False)

    def is_running(self):
        """检查是否有线程还在运行中"""
        return [k for k, v in self.threads.items() if v is not None]

    def download(self, args: dict):
        for i in range(5):
            args['state'] = i
            # print(args['data'])
            sleep(1)
        args['result'] = 'ok'


d = Downloader()
print('添加1', flush=False)
d.add('1')
# sleep(6)
print('添加2', flush=False)
d.add('2')
# sleep(.5)
# d.add('3')
# d.add('4')
print('添加3', flush=False)
d.add('3')
print('添加4', flush=False)
d.add('4')
# sleep(6)
print('添加5', flush=False)
d.add('5')
