import time, random
from pythreader import TaskQueue, Task
from threading import Timer

class MyTask(Task):

    def __init__(self, tid):
        Task.__init__(self)
        self.Id = tid

    def run(self):
        print (time.time(), self.Id, "started as instance")
        time.sleep(random.random()*3)
        print (self.Id, "ended")

    def failed(self, e):
        print (e)

q = TaskQueue(5, stagger=1.0, tasks=[MyTask(x) for x in range(10)])
q << MyTask(30) << MyTask(31)
MyTask(32) >> q
q += MyTask(33)


Timer(3.5, lambda q: q.addTask(MyTask(40)), (q,)).start()
Timer(3.51, lambda q: q.addTask(MyTask(41)), (q,)).start()
Timer(3.52, lambda q: q.addTask(MyTask(42)), (q,)).start()
Timer(3.53, lambda q: q.addTask(MyTask(43)), (q,)).start()
Timer(3.9, lambda q: q.addTask(MyTask(44)), (q,)).start()

q.waitUntilEmpty()


