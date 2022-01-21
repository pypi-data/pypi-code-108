#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/12 8:08 下午
# @Author  : lance.txl
# @Site    : 
# @File    : mqpool_utils.py
# @Software: PyCharm

import threadpool
from multiprocessing import cpu_count,Pool
import random
import time

class MqProcessPool():
    def __init__(self, processnum=0):
        self.processnum = cpu_count() if not processnum else processnum
        self.func = None
        self.data = self.__example_data()
        self.callback = self.__print_result
        self.pp = Pool(processes=self.processnum)
        # self.pp = Pool()

    def set_callback(self, func):
        self.callback = func

    def set_run_func(self, func):
        self.func = func

    def set_missiondatas(self, datas):
        self.data = datas

    def __example_data(self):
        return [random.randint(1,10) for i in range(10)]

    def __print_result(self, request):
        print(request)
        # print("**** Result from request #%s: %r" % (request.requestID, result))

    def __handle_exception(self, request):
        print(request)
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        print(self_dict)
        del self_dict['pp']
        return self_dict
    def __setstate__(self, state):
        self.__dict__.update(state)

    def run(self):
        # for d in self.data:
        #     self.pp.apply(self.func,args=(d,))
        self.pp.map_async(self.func,self.data,callback=self.callback,error_callback=self.__handle_exception)
        self.pp.close()
        self.pp.join()
        print("done")
class MqThreadPool:
    def __init__(self,threadnum=0):
        self.threadnum = cpu_count() if not threadnum else threadnum
        self.single_param = False
        self.func = self.__do_something
        self.data = self.__example_data()
        self.callback = self.__print_result
        self.tp = threadpool.ThreadPool(num_workers=self.threadnum)
    def set_callback(self,func):
        self.callback = func
    def set_run_func(self,func):
        self.func = func
    def set_missiondatas(self,datas):
        self.data = datas
    def __example_data(self):
        # return [random.randint(1,10) for i in range(20)]
        return [((random.randint(1,10),), {}) for i in range(20)]
    def __do_something(self,data):
        time.sleep(random.randint(1,5))
        result = round(random.random()*data, 5)
        if result > 5:
            raise RuntimeError("Something extraordinary happened!")
        return result

    def __print_result(self,request, result):
        pass
        # print("**** Result from request #%s: %r" % (request.requestID, result))

    def __handle_exception(self,request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print(request)
            print(exc_info)
            raise SystemExit
        print("**** Exception occured in request #%s: %s" % \
          (request.requestID, exc_info))
    def run(self):

        requests = threadpool.makeRequests(self.func, self.data, self.callback, self.__handle_exception)
        for req in requests:
            self.tp.putRequest(req)
            # print("Work request #%s added." % req.requestID)
        i = 0
        while True:
            try:
                time.sleep(0.5)
                self.tp.poll()
            except KeyboardInterrupt:
                print("**** Interrupted!")
                break
            except Exception:
                break
        if self.tp.dismissedWorkers:
            self.tp.joinAllDismissedWorkers()
