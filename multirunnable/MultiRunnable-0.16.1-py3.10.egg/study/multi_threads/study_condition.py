import threading
import random
import time



class Producer(threading.Thread):

    """
    向列表中生产随机整数
    """

    def __init__(self, integers, condition):
        """
        构造器

        @param integers 整数列表
        @param condition 条件同步对象
        """
        threading.Thread.__init__(self)
        self.integers = integers
        self.condition = condition

    def run(self):
        """
        实现Thread的run方法。在随机时间向列表中添加一个随机整数
        """
        while True:
            integer = random.randint(0, 256)
            # 获取条件锁
            self.condition.acquire()
            print('condition acquired by %s' % self.name)
            self.integers.append(integer)
            print('%d appended to list by %s' % (integer, self.name))
            print('condition notified by %s' % self.name)
            # 唤醒消费者线程
            self.condition.notify()
            print('condition released by %s' % self.name)
            # 释放条件锁
            self.condition.release()
            # 暂停1秒钟
            time.sleep(1)




class Consumer(threading.Thread):
    """
    从列表中消费整数
    """

    def __init__(self, integers, condition):
        """
        构造器

        @param integers 整数列表
        @param condition 条件同步对象
        """
        threading.Thread.__init__(self)
        self.integers = integers
        self.condition = condition

    def run(self):
        """
        实现Thread的run()方法，从列表中消费整数
        """
        while True:
            # 获取条件锁
            self.condition.acquire()
            print('condition acquired by %s' % self.name)
            while True:
                # 判断是否有整数
                if self.integers:
                    integer = self.integers.pop()
                    print('%d popped from list by %s' % (integer, self.name))
                    break
                print('condition wait by %s' % self.name)
                # 等待商品，并且释放资源
                self.condition.wait()
            print('condition released by %s' % self.name)
            # 最后释放条件锁
            self.condition.release()



def main():
    integers = []
    condition = threading.Condition()
    t1 = Producer(integers, condition)
    t2 = Consumer(integers, condition)
    t1.start()
    t2.start()
    t1.join()
    t2.join()



if __name__ == '__main__':
    main()

