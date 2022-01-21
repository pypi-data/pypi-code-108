import queue
import threading
import logging
from traceback import format_exc

# global
thread_queue = None

class ThreadQueue(threading.Thread):
    def __init__(self, task_name, thread_size=10, queue_size=10):
        """
        多线性队列实现，FIFO先进先出
        初始化线程，并创建队列中间件queue
        thread_size：生成的线程个数
        queue_size：指定队列最大容量，当容量满时，队列将阻塞直到线程消费其中的任务

        注意：任务完成后，必须显式调用queue.join()结束线程
        :param thread_size:
        :param queue_size:
        """
        threading.Thread.__init__(self)

        self.task_name = task_name
        self.thread_size = thread_size
        global thread_queue
        if thread_queue is None:
            thread_queue = queue.Queue(queue_size)

        self.queue = thread_queue

    def run(self):
        """
        从队列里获取任务并执行
        :return:
        """
        while True:
            try:
                item = self.queue.get()  # 阻塞获取任务
                self.task_name(item)
                self.queue.task_done()   # task_name 执行完毕后，向队列发送一个信号
            except Exception as e:
                logging.error(format_exc())
                logging.error(e)
            finally:
                pass


    @classmethod
    def create_thread(cls, task_name, thread_size, queue_size):
        """
        # 返回生产者队列，只需要把任务task对象put进去即可。
        # 注意：当task含有数据库操作时，由于数据库exectuce带线程锁，资源互斥，必须确保每个task里用独立的数据库连接
        # 所有任务放进队列后，调用queue.join()挂起主线程，直到队列内所有任务完成，主线程结束，关闭所有子线程
        :param thread_size: 同时处理任务的线程数
        :param queue_size: 队列最大数量，建议设置thread_size*2，注意OOM
        :return:
        """
        for i in range(thread_size):
            t = ThreadQueue(task_name, thread_size, queue_size)
            t.setDaemon(True)
            t.start()

        return thread_queue



if __name__ == '__main__':
    # 定义任务
    def task_name(item):
        print(threading.current_thread().name)
        print(item)

    # 创建队列
    queue = ThreadQueue.create_thread(task_name, 10, 20)

    # 往队列中填数据
    for num in range(20):
        queue.put(num)

    # TODO wait on the queue until everything has been processed
    # 结束工作
    queue.join()
    print("done")


