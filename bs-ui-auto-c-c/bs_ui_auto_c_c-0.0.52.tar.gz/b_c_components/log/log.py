# 日志等级:
# [00]NOTICE  : 收集所有日志
# [10]DEBUG   : 最详细的日志信息，典型应用场景是 问题诊断
# [20]INFO    : 信息详细程度仅次于DEBUG，通常只记录关键节点信息，用于确认一切都是按照我们预期的那样进行工作
# [30]WARNING : 当某些不期望的事情发生时记录的信息（如，磁盘可用空间较低），但是此时应用程序还是正常运行的
# [40]ERROR   : 由于一个更严重的问题导致某些功能不能正常运行时记录的信息
# [50]CRITICAL: 当发生严重错误，导致应用程序不能继续运行时记录的信息

import logging
import logging.handlers


class Logging:
    """
    使用时，生成一个Logging对象，对象的logger对象调用对应的日志级别的方法，生成这个对象要在最外层，传入地址以及日志消息的最低严重级别。

    """

    def __init__(self, log_path, loh_Level="INFO"):
        self.logging = logging
        self.logger = self.logging.getLogger('日志信息')
        self.logger.setLevel(loh_Level)
        self.fh = self.logging.handlers.TimedRotatingFileHandler(
            log_path, encoding='utf-8', when='D', interval=1, backupCount=0)
        self.fh.setLevel(loh_Level)
        self.formatter = self.logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s: %(pathname)s:%(lineno)d - '
            '%(funcName)s  %(message)s')
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)


if __name__ == '__main__':
    # 例： 传入路径、级别
    def a():
        log1 = Logging(
            "/Users/sijunji/文件/PY工作目录/UIBeisen/b_c_components/log/log.txt",
            'DEBUG')
        try:
            int("asdsad")
        except Exception as e:
            log1.logger.log(log1.logger.level, msg=e)
        pass
    a()
