from functools import wraps
from os.path import join
from os import getcwd
from datetime import datetime


def singleton(cls):
    _instance = {}

    @wraps(cls)
    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


class Time:
    def __init__(self, cls):
        wraps(cls)(self)

    def __call__(self, *args, **kwargs):
        self.__func()
        print("时间:", datetime.now())
        return self.__wrapped__(*args, **kwargs)


@singleton
class Log:
    def __init__(self, file_name):
        self.file_name = file_name

    def _write_log(self, level, msg):
        with open(self.file_name, "a", encoding="utf-8") as fp:
            fp.write("{0}  {1}\n".format(level, msg))

    def critical(self, msg):
        self._write_log("CRITICAL:", msg)

    def error(self, msg):
        self._write_log("ERROR:", msg)

    def warn(self, msg):
        self._write_log("WARN:", msg)

    def info(self, msg):
        self._write_log("INFO:", msg)

    def debug(self, msg):
        self._write_log("DEBUG:", msg)

    def __str__(self):
        return "file_name:{}".format(self.file_name)

    def call_error(self):
        print("This is a error,look {}".format(
            join(getcwd(), self.file_name))
        )


if __name__ == '__main__':
    demo = Log()
