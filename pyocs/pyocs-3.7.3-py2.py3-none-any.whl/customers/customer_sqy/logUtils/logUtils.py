# coding: utf-8
 
import logging.handlers
import logging
import os
import sys
 
# 提供日志功能
class logUtils():
    def __init__(self,name):
        # 初始化logger
        self.log = logging.getLogger(name)
        # 设置日志文件保存路径，common同级目录中的logs文件夹
        self.logpath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs/" + name))
        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)
        # 日志文件的绝对路径
        self.logname = os.path.join(self.logpath, 'log') 
        #print(f"日志保存路径{logpath}")
        # 设置日志文件容量，转换为字节
        self.logsize = 1024*1024*int(8) # 8M
        # 设置日志文件保存个数
        self.lognum = int(3)
        # 日志格式，可以根据需要设置
        self.fmt = logging.Formatter('[%(asctime)s]-[%(levelname)s]-[%(filename)s]-[line:%(lineno)d]: %(message)s', '%Y-%m-%d %H:%M:%S')
        
        # 日志输出到文件，设置日志名称，大小，保存个数,编码
        # self.handle1 = logging.handlers.RotatingFileHandler(self.logname, maxBytes=self.logsize, backupCount=self.lognum,encoding='utf-8')
        # self.handle1.setFormatter(self.fmt)
        # self.log.addHandler(self.handle1)

        # 日志输出到文件，一天一个日志文件
        self.handle1 = logging.handlers.TimedRotatingFileHandler(self.logname, when="midnight",encoding='utf-8')
        self.handle1.setFormatter(self.fmt)
        self.log.addHandler(self.handle1)
 
        # 日志输出到屏幕，便于实时观察
        # self.handle2 = logging.StreamHandler(stream=sys.stdout)
        # self.handle2.setFormatter(self.fmt)
        # self.log.addHandler(self.handle2)
 
        # 设置日志等级，这里设置为DEBUG，表示只有INFO级别及以上的会打印
        self.log.setLevel(logging.DEBUG)
 
    # 日志接口，可根据需要定义更多接口
    @classmethod
    def info(cls, msg):
        cls.log.info(msg)
        return
 
    @classmethod
    def warning(cls, msg):
        cls.log.warning(msg)
        return
 
    @classmethod
    def error(cls, msg):
        cls.log.error(msg)
        return
 
    @classmethod
    def debug(cls, msg):
        cls.log.debug(msg)
        return