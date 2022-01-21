#!/usr/bin/env python
#encoding=utf-8

class BeanStalk:
    def __init__(self, host="localhost", port=11300, encoding='utf-8', watch='default'):
        try:
            import greenstalk
            self.conn = greenstalk.Client((host, port), encoding=encoding, watch=watch)
        except ImportError as e:
            import beanstalkc
            self.conn = beanstalkc.Connection(host, port)
            # self.conn.use(use)
            self.conn.watch(watch)
            # self.conn.ignore("default")

    def put(self, body, priority=65536, delay=0, ttr=60, tube='default'):
        """
        生产者
        :param body: job 类型为bytes或者str
        :param priority: 优先级 0-2^32 0优先级最大
        :param delay: 延迟
        :param ttr: time-to-run 超时重发
        :param tube: 向指定tube写入消息
        :return: job id
        """
        self.use(tube)
        return self.conn.put(body, priority, delay, ttr)

    def reserve(self, timeout=None):
        """
        消费者
        :param timeout: 一直处于阻塞状态 将等待多长时间来接收这个job。如果这个reserve的timeout时间到了，它将返回TimedOutError
        :return: Job类型
        """
        return self.conn.reserve(timeout)

    def delete(self, job):
        """
        删除一个job
        :param job: job或者jobId
        :return: None
        """
        self.conn.delete(job)

    def release(self, job, priority=65536, delay=0):
        """
        将一个被消费的任务重新加入队列
        :param job: 任务
        :param priority: 优先级
        :param delay: 延迟
        :return: None
        """
        self.conn.release(job, priority, delay)

    def bury(self, job, priority=65536):
        """
        把job转为buried状态
        将job放到一个特殊的FIFO队列中，之后不能被reserve命令获取，但可以用kick命令扔回工作队列中，之后就能被消费了（相当于“逻辑删除”）
        :param job: 任务
        :param priority: 优先级
        :return: None
        """
        self.conn.bury(job, priority)

    def kick(self, bound):
        """
        把一个job从buried转为ready状态
        :param bound: 一次kick的任务数，顺序从前置后
        :return: 返回受影响任务的数量
        """
        return self.conn.kick(bound)

    def kick_job(self, job):
        """
        把delayed 或者 buried 的任务转换为ready状态
        :param job: job或者id
        :return: None
        """
        self.conn.kick_job(job)

    def touch(self, job):
        """
        让任务重新计算任务超时重发ttr时间,相当于给任务延长寿命
        :param job: 任务
        :return: None
        """
        self.conn.touch(job)

    def use(self, tube='default'):
        """
        切换当前使用的tube
        每个tube都是一个独立的queue，可以使用use命令切换tube，如果切换的tube不存在，会自动创建一个
        :param tube: 管道名称 str
        :return: None
        """
        self.conn.use(tube)

    def watch(self, tube):
        """
        watch一个管道，相当于多监听一个新的tube，如果不存在，会被自动创建，可以用ignore命令取消关注tube
        当监控多个tube时，只要有一个tube有数据到来，reserve会返回
        watch和use是两个独立的动作，use一个tube不代表watching它，反之watch一个tube也不代表using它
        :param tube: 管道
        :return: 返回监听管道的数量
        """
        return self.conn.watch(tube)

    def ignore(self, tube):
        """
        取消监听指定的管道
        :param tube: 管道
        :return: 返回监听管道的数量
        """
        return self.conn.ignore(tube)

    def peek(self, jobid):
        """
        查看job的信息
        :param jobid:
        :return: 返回job类型
        """
        return self.conn.peek(jobid)

    def peek_ready(self):
        """
        获取当前管道下一个处于ready状态的任务
        :return: Job
        """
        return self.conn.peek_ready()

    def peek_delayed(self):
        """
        获取当前管道下一个处于delay状态的任务
        :return: Job
        """
        return self.conn.peek_delayed()

    def peek_buried(self):
        """
        获取当前管道最早处于buried状态的任务
        :return: Job
        """
        return self.conn.peek_buried()

    def stats_job(self, job):
        """
        查看任务的状态 job有四种状态
        ready，需要立即处理的任务，当延时 (delayed) 任务到期后会自动成为当前任务；
        delayed，延迟执行的任务, 当消费者处理任务后，可以用将消息再次放回 delayed 队列延迟执行；
        reserved，已经被消费者获取, 正在执行的任务，Beanstalkd 负责检查任务是否在 TTR(time-to-run) 内完成；
        buried，保留的任务: 任务不会被执行，也不会消失，除非有人把它 "踢" 回队列；
        :param job: job id
        :return: dict
        """
        return self.conn.stats_job(job)

    def stats_tube(self, tube):
        """
        查看管道的状态
        :param tube: 管道名称
        :return: dict
        """
        return self.conn.stats_tube(tube)

    def stats(self):
        """
        返回系统的状态
        :return: dict
        """
        return self.conn.stats()

    def tubes(self):
        """
        返回所有的管道名称
        :return list
        """
        return self.conn.tubes()

    def using(self):
        """
        返回正在使用的管道名称
        :return: str 管道名称
        """
        return self.conn.using()

    def watching(self):
        """
        返回监听的所有管道名称
        :return: list 管道名称列表
        """
        return self.conn.watching()

    def pause_tube(self, tube, delay):
        """
        暂停一个管道，delay期间的job无法使用
        :param tube: str 管道名称
        :param delay: 延迟
        :return: None
        """
        self.conn.pause_tube(tube, delay)

    def close(self):
        """
        关闭连接
        """
        self.conn.close()

if __name__ == "__main__":
    # producer
    client = BeanStalk('127.0.0.1', 11300)
    id = client.put(b'hello', delay=10)
    client.close()

    # # worker: work进程只能监听它指定的一个或多个tube通道,无论指定与否，任何work都会自动把默认的tube（default）加入监听
    # # 实现监听（watch）多个tube的方式
    # # 1：可以启动多个work进程，每个work监听七个tube
    # # 2、启动一个work，监听多个tube
    while True:
        client = BeanStalk('127.0.0.1', 11300, watch="default")
        client.watch("new")         # 新增一个监听的tube
        print(client.watching())    # 当前客户端监听的所有tube

        job = client.reserve()      # 只要一个tube有消息，消息将被获取
        print(job.id)
        print(job.body)
        client.delete(job)          # 处理完成后，收到删除消息
