import functools

from .exception import NeedLoginException

# __all__ = ['need_login']

# 音源后缀
SOURCE_SUFFIX = ['.wav', '.mp3', '.ape', '.flac', '.dts', ]
# 图片后缀
PICTURE_SUFFIX = ['.jpg', '.png', '.gif', '.jpeg', ]
# 歌词后缀
LYRIC_SUFFIX = ['.txt']
# 忽略后缀
IGNORE_FILES = ['Thumbs.db']


def need_login(func):
    """
    装饰器。作用于 :class:`.TmeCms` 中的某些方法，
    强制它们必须在登录状态下才能被使用。
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.is_login():
            return func(self, *args, **kwargs)
        else:
            raise NeedLoginException(func.__name__)

    return wrapper


def check_interface_data(response, data):
    """
    检查接口是否有增删字段

    例子：
    check_interface_data(QuerySongResponses, {"list": [{"id": "717090", }], "page": 1, "total": 1})
    """
    response_data = {}
    response = response(**data)

    if hasattr(response, 'list'):
        if response.list:
            response_data = response.list[0].__dict__
            data = data['list'][0]
    else:
        response_data = response.__dict__

    a = {}
    b = {}
    for k, v in response_data.items():
        if k in data:
            ...
        else:
            a[k] = v

    for k, v in data.items():
        if k in response_data:
            ...
        else:
            b[k] = v
    print('删除的字段内容', a)
    print('增加的字段内容', b)
