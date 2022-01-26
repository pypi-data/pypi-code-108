# coding: utf-8
import datetime
import time
import logging
import os
from logging.handlers import BaseRotatingHandler

log_level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

log_color = {
    "debug": 32,
    "info": 37,
    "warning": 33,
    "error": 31,
    "critical": 35
}


def get_now_time():
    """
    获取日期{YYYY-mm-dd}
    """
    now_time = datetime.datetime.now()
    year = now_time.year
    month = now_time.month
    day = now_time.day
    if month < 10:
        month = f"0{month}"
    if day < 10:
        day = f"0{day}"
    # minute = now_time.minute
    # return f"{year}-{month}-{minute}"  # debug用
    return f"{year}-{month}-{day}"


class MyFormatter(logging.Formatter):
    """
    重写format类
    1、重置默认的时间格式
    2、把包路径改到3层路径
    Attribute:
        default_time_format: 除了毫秒的时间格式
        default_msec_format: 毫秒的时间格式，这里时区写死+0800
        with_color: 是否带上颜色，输出系统的format可以带颜色，输出到文件的不能带颜色
    """

    def __init__(self, with_color=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_time_format = "%Y-%m-%dT%H:%M:%S"
        self.default_msec_format = "%s.%03d+0800"
        self.with_color = with_color
        if with_color:
            self.color_template = "\033[1;%dm%s\033[0m"

    def format(self, record):
        pathname = record.pathname
        # 不确定windows的路径，暂时只使用os包进行路径划分
        dir_list = []
        if pathname:
            file_name = os.path.basename(pathname)
            dir_list.append(file_name)
            base_path = pathname
            while len(dir_list) < 3:
                base_path = os.path.dirname(base_path)
                base_name = os.path.basename(base_path)
                if base_name:
                    dir_list.append(base_name)
                else:
                    break
        dir_list = dir_list[::-1]
        new_path = "/".join(dir_list)
        record.pathname = new_path
        result_without_color = super().format(record)
        if not self.with_color:  # 不带颜色
            return result_without_color
        else:
            record_log_level = record.levelname.lower()
            result = self.color_template % (log_color[record_log_level], result_without_color)
            return result

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = time.strftime(self.default_time_format, ct)
        s = self.default_msec_format % (t, record.msecs)
        return s


class MyHandler(BaseRotatingHandler):
    """
    重写的日志流转类
    需要重写：
        shouldRollover: 什么时候流转日志。在日期跨一天和原文件大小到达上限的时候。
        doRollover: 如何流转日志。
    Attribute:
        log_module: 同Logger类中的MODULE
        log_type: 同Logger类中的TYPE
        max_bytes: 最大日志大小，Byte
        backup_count: 每天最大日志数量
        dateNow: 当前的时间，{YYYY-mm-dd}
        stream: 文件流
        baseFilename: 当前日志流向的位置
    """

    def __init__(self, log_module=None, log_type=None, max_bytes=None, backup_count=100, date_now=None, *args,
                 **kwargs):
        super(MyHandler, self).__init__(*args, **kwargs)
        self.log_module = log_module
        self.log_type = log_type
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.dateNow = date_now
        self.dir_name = os.path.dirname(self.baseFilename)

    def shouldRollover(self, record):
        """
        判断是否需要流转文件
        """
        if self.stream is None:
            self.stream = self._open()
        if self.max_bytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.max_bytes:
                return 1
        if get_now_time() != self.dateNow:
            return 1
        return 0

    def doRollover(self):
        """
        只要进来了，就必须流转日志
        再进行一次判断，如果是日期变了，那就不需要再考虑日志顺序了。
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        now_time = get_now_time()
        if self.dateNow != now_time:
            # 新的一天的日志
            self.dateNow = now_time
            # 万一出现存在意外日志就删除。保证新的一天没有新日期的日志。
            # XX-xx.2022-01-25
            new_day_template = os.path.join(self.dir_name, f'{self.log_module}-{self.log_type}.{self.dateNow}')
            cmd = f"rm -rf f {new_day_template}.*.log"
            os.system(cmd)
            self.baseFilename = new_day_template + ".0.log"
        else:
            # 文件容量达到预设值，需要新增一个当天的日志文件
            base_file_name = os.path.basename(self.baseFilename)
            template_list = base_file_name.split(".")
            template_ = ".".join(template_list[:-2]) + "."
            template_file_name = template_ + "%d.log"
            now_index = int(template_list[-2])  # 当前日志的下标
            exists_log_file_list = []
            for fn in os.listdir(self.dir_name):  # 遍历日志文件下已有的文件
                if fn.startswith(template_) and fn.endswith(".log"):
                    try:
                        log_index = int(fn.replace(template_, "").replace(".log", ""))  # 日志的下标
                        exists_log_file_list.append(log_index)
                    except ValueError:  # 如果异常说明该文件下标位置存在非数字，如triton-main.11-47-2022.0的副本.log
                        continue
            # 如果当前的日志是99.log满了，需要流转到100.log，那么就要删除0.log保证该天的日志文件只有100个
            assert len(exists_log_file_list) > 0, "当前日志数量一定是大于0的"
            exists_log_file_list.sort()  # 对已有的日志下标进行排序
            max_index = exists_log_file_list[-1]  # 当前已有日志的下标
            assert max_index == now_index, "当前日志下标一定是最大的"
            self.baseFilename = os.path.join(self.dir_name, template_file_name % (now_index + 1))
            exists_log_file_list.append(now_index + 1)
            if len(exists_log_file_list) > self.backup_count:
                for i in exists_log_file_list[:len(exists_log_file_list) - self.backup_count]:
                    delete_path = os.path.join(self.dir_name, template_file_name % i)
                    if os.path.exists(delete_path):
                        os.remove(delete_path)
        if not self.delay:
            self.stream = self._open()


class Logger:
    """
    日志工具
    日志的具体路径如：log_dir/{log_module}-{log_type}.{YYYY-MM-DD}.{N}.log
    {N}：日志文件序列号，数字从0开始。比如2020年11月6日vcm组件自身日志输出两个日志文件，则日志文件如下vcm-main.20201126.0.log（大小>=100MB）和vcm-main.2020-11-26.1.log（大小<100MB）
    Args:
        log_module: 组件/模块名。如vcm
        log_type: 日志类型。如组件业务流水日志vcm-water；如组件自身日志类型vcm-main 。如果组件没有业务流水等日志，则命名为{MODULE}-main
        log_dir: 日志所在的文件夹
    """

    def __init__(self, log_module=None, log_type=None, log_dir=None, level="info"):
        if log_dir and (not log_module) and (not log_type):
            raise ValueError("if log_dir is not none, log_module and log_type muse have value")
        self.log_module = log_module
        self.log_type = log_type
        self.log_dir = log_dir
        self.date_now = get_now_time()  # 当前时间的年月日
        self.max_bytes = 500  # 最大100M日志
        self.backup_count = 5  # 每天最多100个日志文件
        self.logger = logging.getLogger(os.path.realpath(__file__))
        self.logger.setLevel(log_level[level.lower()])
        self.logger.propagate = False
        self.fmt_str = "%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)d | %(process)d/%(thread)d | %(message)s"
        # 用于输出系统
        self.sh = logging.StreamHandler()
        self.sh.setLevel(log_level[level.lower()])
        self.sh.setFormatter(MyFormatter(fmt=self.fmt_str, with_color=True))
        self.logger.addHandler(self.sh)
        if log_dir:
            log_file_now_path = self.build_log()
            # 用于输出文件
            self.handler = MyHandler(log_module=self.log_module,
                                     log_type=self.log_type,
                                     max_bytes=self.max_bytes,
                                     backup_count=self.backup_count,
                                     date_now=self.date_now,
                                     filename=log_file_now_path,
                                     mode="a",
                                     delay=False,
                                     encoding="utf-8")
            self.handler.setLevel(log_level[level.lower()])
            self.handler.setFormatter(MyFormatter(fmt=self.fmt_str))
            self.logger.addHandler(self.handler)

    def build_log(self):
        """
        找到最新的日志文件
        """
        exists_log_file_list = []
        template_ = f"{self.log_module}-{self.log_type}.{get_now_time()}."
        template_file_name = template_ + "%d.log"
        for fn in os.listdir(self.log_dir):  # 遍历日志文件下已有的文件
            if fn.startswith(template_) and fn.endswith(".log"):
                log_index = int(fn.replace(template_, "").replace(".log", ""))  # 日志的下标
                exists_log_file_list.append(log_index)
        # 根据已有的日志去判读当前的日志序号是多少
        if len(exists_log_file_list) > 0:
            if len(exists_log_file_list) > self.backup_count:  # 如果出了意外导致最大数量超过了100个，那就删了以前的
                exists_log_file_list.sort()
                for i in exists_log_file_list[:len(exists_log_file_list) - self.backup_count]:
                    delete_path = os.path.join(self.log_dir, template_file_name % i)
                    if os.path.exists(delete_path):
                        os.remove(delete_path)
            now_index = max(exists_log_file_list)
            file_path = os.path.join(self.log_dir, template_file_name % now_index)
            if os.path.getsize(file_path) < self.max_bytes:  # 如果最近的文件还没有满，继续往里面写
                return file_path
            else:  # 如果满了，就新建下一个序号
                if len(exists_log_file_list) >= self.backup_count:
                    # 如果超出了每天最大的文件数量(100)，删除当天最早的日志，保证当天的日志总数不大于100
                    min_index = min(exists_log_file_list)
                    os.remove(template_file_name % min_index)
                file_path = os.path.join(self.log_dir, template_file_name % (now_index + 1))
                return file_path
        else:
            file_path = os.path.join(self.log_dir, template_file_name % 0)
            return file_path

    def debug(self, message):
        self.logger.debug(" | " + str(message))

    def info(self, message):
        self.logger.info(" | " + str(message))

    def warning(self, message):
        self.logger.warning(" | " + str(message))

    def error(self, message, error_code=-1):
        self.logger.error(str(error_code) + " | " + str(message))

    def critical(self, message):
        self.logger.critical(" | " + str(message))


# logger = Logger(log_module="triton", log_type="main", log_dir="./", level="info")
