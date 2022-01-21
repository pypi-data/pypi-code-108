class InvalidArguments(Exception):
    def __init__(self, message='some arguments are invalid'):
        super(InvalidArguments, self).__init__()
        self.message = message
    
    def __str__(self, *args, **kwargs):
        return self.message


class AnyLearnException(Exception):
    """AnyLearnSDK通用异常类"""

    def __init__(self, msg):
        """
        :param msg: 错误信息
        """
        self.msg = msg

    def __str__(self):
        s = f"错误信息: {self.msg}"
        return s

    def __repr__(self):
        __repr = f"[{self.__class__.__name__}] {self.msg}"
        return __repr


class AnyLearnAuthException(AnyLearnException):
    """AnyLearnSDK鉴权异常类"""

    def __init__(self, msg="无效的用户身份信息或令牌"):
        super().__init__(msg)


class AnyLearnMissingParamException(AnyLearnException):
    """AnyLearnSDK接口调用参数缺失异常类"""

    def __init__(self, msg="缺少参数或参数格式不正确"):
        super().__init__(msg)


class AnyLearnNotSupportedException(AnyLearnException):
    """AnyLearnSDK接口不支持异常类"""

    def __init__(self, msg="暂不支持该操作"):
        super().__init__(msg)


class AnylearnRequiredLocalCommitException(AnyLearnException):
    """本地算法目录有未主动提交的变更"""

    DEFAULT_MESSAGE = (
        "Algorithm dir is not clean, "
        "please commit your changes first"
    )

    def __init__(self, msg=DEFAULT_MESSAGE):
        super().__init__(msg)
