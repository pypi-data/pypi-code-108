import sys
import logging
import traceback


class Logger():
    """
    Functions:
        - 自定义封装的Logger日志对象
        - 可以自定义打印格式, 自定义打印级别 (自由度高)

    Usages:
        l = Logger("l1", pure=True)
        l = Logger("l2")

    """

    def __init__(self, name="kw", formatter_str=None, pure=False):
        """
        Args:
            name: Logger Name <str>
                - 项目中不能有重名的logger对象 (否则会出现重复打印的bug)
            formatter_str: 日志打印格式 <str>
                - 必须包含 '%(message)s'
            pure: 是否为纯净版本的logger对象 <bool>
                - 纯净版: 指没有任何额外的logger相关的信息输出, 仅有打印内容 (即: 只利用logger级别的过滤功能)
                - 默认为None, 即`非纯净版`;
        """
        # 1. 创建logger和handler
        logger = logging.getLogger(name)
        stream_handler = logging.StreamHandler()
        # file_handler = logging.FileHandler(filename=f"{FILE_PATH_FOR_HOME}/log/test.log")

        # 2. 设置level
            # 默认: DEBUG, INFO, WARNING, ERROR, CRITICAL (分别是10, 20, 30, 40, 50)
        # logger.setLevel(logging.DEBUG) # 最低支持打印的输出级别
        # stream_handler.setLevel(logging.DEBUG)
        logger.setLevel(1) # 最低支持打印的输出级别是1; 若输入0, 默认是"WARNING"级别
        stream_handler.setLevel(1)
        logging.addLevelName(5, "VERBOSE") # // 新增: VERBOSE (5分)
        logging.addLevelName(25, "IMPORTANT") # // 新增: IMPORTANT (25分)
        logging.addLevelName(35, "EXCEPTION") # // 新增: EXCEPTION (35分)
        logging.addLevelName(60, "TMP") # // 新增: TMP (60分)

        # 3. 设置log的输出格式
        if pure:
            self.pure = True
            formatter_str = ""
        else:
            self.pure = False
            if formatter_str is None:
                formatter_str = ">>> [%(asctime)s] %(message)s"
        formatter = logging.Formatter(formatter_str) # 其他格式见上面的url
        stream_handler.setFormatter(formatter)
        # file_handler.setFormatter(formatter)

        # 4. 把handler添加进logger
        logger.addHandler(stream_handler)
        # logger.addHandler(file_handler)

        self.logger = logger
        self.ban_levels = [] # 需要屏蔽的日志级别


    def _log(self, msg_header, *args, **kwargs):
        _log_msg = msg_header
        for l in args:
            if type(l) == tuple:
                ps = str(l)
            else:
                try:
                    ps = "%r" % l
                except:
                    ps = str(l)
            if type(l) == str:
                _log_msg += ps[1:-1] + " "
            else:
                _log_msg += ps + " "
        if len(kwargs) > 0:
            _log_msg += str(kwargs)
        return _log_msg


    def _log_msg_header(self, *args, **kwargs):
        """Fetch log message header.
        """
        cls_name = ""
        func_name = sys._getframe().f_back.f_back.f_code.co_name
        try:
            _caller = kwargs.get("caller", None)
            if _caller:
                if not hasattr(_caller, "__name__"):
                    _caller = _caller.__class__
                cls_name = _caller.__name__
                del kwargs["caller"]
        except:
            pass
        finally:
            msg_header = "[{cls_name}.{func_name}]:  ".format(cls_name=cls_name, func_name=func_name)
            return msg_header, kwargs


    def _join_args(self, *args):
        s = ""
        for arg in args:
            s += f"{str(arg)} "
        return s


    def log(self, level, *args, **kwargs):
        """
        Functions: 通过level来分流执行不同的日志输出
        """
        if level == 5 or level.upper() == "VERBOSE":
            self.verbose(*args, **kwargs)
        elif level == 10 or level.upper() == "DEBUG":
            self.debug(*args, **kwargs)
        elif level == 20 or level.upper() == "INFO":
            self.info(*args, **kwargs)
        elif level == 25 or level.upper() == "IMP":
            self.imp(*args, **kwargs)
        elif level == 30 or level.upper() == "WARNING":
            self.warning(*args, **kwargs)
        elif level == 35 or level.upper() == "EXCEPTION":
            self.exception(*args, **kwargs)
        elif level == 40 or level.upper() == "ERROR":
            self.error(*args, **kwargs)
        elif level == 50 or level.upper() == "CRITICAL":
            self.critical(*args, **kwargs)
        elif level == 60 or level.upper() == "TMP":
            self.tmp(*args, **kwargs)
        else:
            self.info(*args, **kwargs)


    def verbose(self, *args, **kwargs):
        """
        Function: 偏底层的debug内容
        """
        if 5 not in self.ban_levels:
            if self.pure:
                self.logger.log(5, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.log(5, "[VERBOSE] " + self._log(msg_header, *args, **kwargs))


    def debug(self, *args, **kwargs):
        """
        Function: 业务层面的debug内容
        """
        if 10 not in self.ban_levels:
            if self.pure:
                self.logger.log(10, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.debug("[DEBUG] " + self._log(msg_header, *args, **kwargs))


    def info(self, *args, **kwargs):
        """
        Function: 业务层面的info内容 (提示各种项目状态)
        """
        if 20 not in self.ban_levels:
            if self.pure:
                self.logger.log(20, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.info("[INFO] " + self._log(msg_header, *args, **kwargs))


    def imp(self, *args, **kwargs):
        """
        Function: 打印比'info'级别更重要一些的日志输出
        """
        if 25 not in self.ban_levels:
            if self.pure:
                self.logger.log(25, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.log(25, "[IMPORTANT] " + self._log(msg_header, *args, **kwargs))


    def warn(self, *args, **kwargs):
        """
        Notes: warning的别名 (最好使用行业规范的'warning')
        """
        if 30 not in self.ban_levels:
            if self.pure:
                self.logger.log(30, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.warn("[WARN] " + self._log(msg_header, *args, **kwargs))


    def warning(self, *args, **kwargs):
        """
        Function: 提示一些小警告 (对系统正常运行影响不大的内容)
        """
        if 30 not in self.ban_levels:
            if self.pure:
                self.logger.log(30, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.warning("[WARNING] " + self._log(msg_header, *args, **kwargs))


    def exception(self, *args, **kwargs):
        """
        Function: 提示一些异常错误 (可能会对系统正常运行造成影响) (会打印捕获到的异常)
                (该方法常常配合 try..except.. 使用, 所以级别定位比'error'稍微轻一些)

        Notes:
            - 封装过的exception: 无需传参, 也会自动打印捕获到的异常
        """
        if 35 not in self.ban_levels:
            if self.pure:
                self.logger.log(35, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.log(45, f"[EXCEPTION] >>> ###############################################################################")
                self.logger.log(45, "[EXCEPTION] " + self._log(msg_header, *args, **kwargs))
                e = traceback.format_exc(limit=10)
                self.logger.log(45, "[EXCEPTION] " + e)
                self.logger.log(45, f"[EXCEPTION] <<< ###############################################################################")


    def error(self, *args, **kwargs):
        """
        Function: 提示一些异常错误 (可能会对系统正常运行造成影响)
        """
        if 40 not in self.ban_levels:
            if self.pure:
                self.logger.log(40, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.error(f"[ERROR] >>> ###############################################################################")
                self.logger.error("[ERROR] " + self._log(msg_header, *args, **kwargs))
                self.logger.error(f"[ERROR] <<< ###############################################################################")


    def critical(self, *args, **kwargs):
        """
        Function: 严重错误 (一定会对系统运行造成影响) (会打印异常, 并继续抛出异常) [慎用]

        Notes:
            - 封装过的exception: 无需传参, 也会自动打印捕获到的异常; 并且继续raise抛出异常
        """
        if 50 not in self.ban_levels:
            if self.pure:
                self.logger.log(50, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                print("\n")
                self.logger.critical(f"[CRITICAL] >>> ###############################################################################")
                self.logger.critical("[CRITICAL] " + self._log(msg_header, *args, **kwargs))
                e = traceback.format_exc(limit=10)
                self.logger.critical("[CRITICAL] " + e)
                self.logger.critical(f"[CRITICAL] <<< ###############################################################################")
                print("\n")
                raise Exception(e)


    def tmp(self, *args, **kwargs):
        """
        Function: 临时使用的最高级别的打印 (主要用于debug, 后面一定会关掉!)
        """
        if 60 not in self.ban_levels:
            if self.pure:
                self.logger.log(60, self._join_args(*args))
            else:
                msg_header, kwargs = self._log_msg_header(*args, **kwargs)
                self.logger.log(60, "[TMP] " + "------------------->>")
                self.logger.log(60, "[TMP] " + self._log(msg_header, *args, **kwargs))
                self.logger.log(60, "[TMP] " + "<<-------------------")


    def setLevel(self, *args):
        self.logger.setLevel(*args)


    def banLevel(self, level):
        self.ban_levels.append(level)


    def level(self):
        level = self.logger.level
        return level

logger = Logger("kw")




if __name__ == "__main__":
    logger.debug(999, caller=99)
    logger.info(999, caller=99)
    logger.warning(999, caller=99)
    logger.error(999, caller=99)
    logger.exception(999, caller=99)
    logger.tmp(999, caller=99)
    logger.critical(999, caller=99)
