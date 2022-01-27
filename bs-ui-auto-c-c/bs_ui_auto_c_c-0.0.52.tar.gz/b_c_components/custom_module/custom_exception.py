
class Configuration_file_error(Exception):
    """
    自定义异常类，用于配置文件空值等错误
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
