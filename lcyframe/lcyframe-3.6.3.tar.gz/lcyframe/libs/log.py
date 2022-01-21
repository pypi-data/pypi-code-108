import os
import logging
from logging import handlers

"""
https://www.cnblogs.com/nancyzhu/p/8551506.html
https://www.cnblogs.com/xianyulouie/p/11041777.html

参数：作用
 
%(levelno)s：打印日志级别的数值
%(levelname)s：打印日志级别的名称
%(pathname)s：打印当前执行程序的路径，其实就是sys.argv[0]
%(filename)s：打印当前执行程序名
%(funcName)s：打印日志的当前函数
%(lineno)d：打印日志的当前行号
%(asctime)s：打印日志的时间
%(thread)d：打印线程ID
%(threadName)s：打印线程名称
%(process)d：打印进程ID
%(message)s：打印日志信息

"""

level_mp = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

default_fmt = '%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s: %(message)s'
lcy_format = '[{name}] %(levelname)s\n[{name}] path: %(pathname)s:%(lineno)d\n[{name}] time: %(asctime)s\n[{name}] message: %(message)s'

class Logger(object):
    instance = {}

    def __init__(self, name, level='info', when='D', backCount=10, fmt=None, save_path=None, propagate=True):
        if not fmt:
            fmt = lcy_format.format(name=name)
        else:
            fmt = default_fmt
        self.propagate = propagate
        self.logger = logging.getLogger(name)
        self.logger.propagate = self.propagate           # 输出的信息不推送给上级的logger，即root
        self.format_str = logging.Formatter(fmt)
        self.logger.setLevel(level_mp[level])

        # redirct to console
        console = logging.StreamHandler()
        console.setFormatter(self.format_str)
        self.logger.addHandler(console)

        if save_path and not os.path.isabs(save_path):
            logging.error("save_path require a path like this '/root/my_project/out.log'")
            exit()

        # wirte to file
        if save_path:
            handler = handlers.TimedRotatingFileHandler(filename=save_path,       # 保存路径
                                                        when=when,              # 间隔的时间单位，单位有: S秒，M 分，H 小时，D 天，W 每星期（interval==0时代表星期一），midnight 每天凌晨
                                                        backupCount=backCount,  # 文件的个数，如果超过这个个数，就会自动删除
                                                        encoding='utf-8')
            handler.setFormatter(self.format_str)
            self.logger.addHandler(handler)


    @classmethod
    def get_instance(cls, name="Lcyframe", **kwargs):
        if name not in cls.instance:
            cls.instance[name] = Logger(name, **kwargs)
        return cls.instance[name]

if __name__ == '__main__':
    # app 专用log
    app = Logger.get_instance(name="Lcyframe", level='debug')
    app.logger.debug('debug')
    app.logger.info('info')
    app.logger.warning('警告')
    app.logger.error('报错')
    app.logger.critical('严重')
    #
    # 数据库专用log
    # db = Logger('db', level='error', fmt=default_fmt)
    # db.logger.error('error')