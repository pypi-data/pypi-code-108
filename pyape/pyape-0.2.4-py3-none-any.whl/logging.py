import logging 
from logging.handlers import WatchedFileHandler
from pathlib import Path

import zmq
import redis
from pythonjsonlogger import jsonlogger


TEXT_LOG_FORMAT = """
[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s [%(pathname)s:%(lineno)d]:
%(message)s"""
JSON_LOG_FORMAT = r'%(levelname)s %(module)s %(funcName)s %(pathname)s %(lineno) %(threadName) %(processName) %(created) %(asctime) %(message)s'


class ZeroMQHandler(logging.Handler):
    """基于 ZeroMQ 的 ROUTER-DEALER 模式来发布 log

    范例::

        sock = context.socket(zmq.DEALER)
        sock.connect('tcp://192.168.0.1:5050')
        handler = ZeroMQHandler(sock)

    或者::

        handler = ZeroMQHandler('tcp://192.168.1:5050')

    These are equivalent.
    """
    socket = None
    ctx = None
    socket_type = None
    
    def __init__(self, interface_or_socket, context=None, socket_type=zmq.DEALER):
        """ 创建 ZeroMQ context 和 socket
        :param interface_or_socket: 提供一个 socket 或者协议字符串
        :param context: 提供 ZeroMQ 的上下文
        :param socket_type: 提供 ZeroMQ 模式
        """
        logging.Handler.__init__(self)
        if isinstance(interface_or_socket, zmq.Socket):
            self.socket = interface_or_socket
            self.ctx = self.socket.context
            self.socket_type = self.socket.socket_type
        else:
            self.ctx = context or zmq.Context()
            self.socket = self.ctx.socket(socket_type)
            self.socket.connect(interface_or_socket)
            self.socket_type = socket_type

    def emit(self, record):
        """Emit a log message on my socket."""
        msg = self.format(record)
        try:
            self.socket.send_string(msg)
        except TypeError:
            raise
        except (ValueError, zmq.ZMQError):
            self.handleError(record)


class RedisHandler(logging.Handler):
    """基于 Redis 的 publish 命令来发布 log
    """
    # redis 实例
    r = None

    # publish 频道
    channel = None
    
    def __init__(self, url, channel, **kwargs):
        logging.Handler.__init__(self)
        self.channel = channel
        self.r = redis.from_url(url, **kwargs)

    def emit(self, record):
        """Emit a log message on redis."""
        msg = self.format(record)
        self.r.publish(self.channel, msg)


def _create_file_handler(target, filename, chmod=False):
    """ 创建一个基于文件的 logging handler
    :param target: 一个 Path 对象，或者一个 path 字符串
    """
    logsdir = None
    if isinstance(target, Path):
        logsdir = target
    else:
        logsdir = Path(target)
    # 如果是创建文件夹，权限就是 777，如果文件夹存在，又没有调用 chmod，则使用原来的权限
    # 创建或者设置 logs 文件夹的权限，让其他 user 也可以写入（例如nginx）
    # 注意，要设置 777 权限，需要使用 0o40777 或者先设置 os.umask(0)
    # 0o40777 是根据 os.stat() 获取到的 st_mode 得到的
    if not logsdir.exists():
        logsdir.mkdir(mode=0o40777)
    if chmod:
        logsdir.chmod(0o40777)
    logfile = logsdir.joinpath(filename + '.log')
    if not logfile.exists():
        logfile.touch()
    # 使用 WatchedFileHandler 在文件改变的时候自动打开新的流，配合 logrotate 使用
    return WatchedFileHandler(logfile, encoding='utf8')


def _create_zmq_handler(target):
    """ 创建一个基于 zeromq 的 logging handler
    :param target: 一个字符串，形如： tcp://127.0.0.1:8334
    """
    return ZeroMQHandler(target)


def _create_redis_handler(target, channel):
    """ 创建一个基于 zeromq 的 logging handler
    :param target: redis_url 字符串，形如： 
        redis://[[username]:[password]]@localhost:6379/0
        rediss://[[username]:[password]]@localhost:6379/0
        unix://[[username]:[password]]@/path/to/socket.sock?db=0
        详见： http://www.iana.org/assignments/uri-schemes/prov/redis
    :param channel: publish 通道
    """
    return RedisHandler(target, channel)


def get_logging_handler(type_, fmt, level=logging.INFO, target=None, name=None) :
    """ 获取一个 logger handler

    :param type_: stream/file/zmq
    :param fmt: text/json
    :param level: logging 的 level 级别
    :param target: 项目主目录的的 path 字符串或者 Path 对象，也可以是 tcp://127.0.0.1:8334 这样的地址
    :param name: logger 的名称，不要带扩展名
    """
    handler = None
    if type_ == 'zmq':
        if target is None:
            raise TypeError('target is necessary if type is zmq!')
        handler = _create_zmq_handler(target)
    elif type_ == 'file':
        if target is None or name is None:
            raise TypeError('target and name is necessary if type is file!')
        handler = _create_file_handler(target, name)
    elif type_ == 'redis':
        if name is None:
            raise TypeError('name is necessary if type is redis!')
        handler = _create_redis_handler(target, name)
    else:
        handler = logging.StreamHandler()
    if fmt == 'raw':
        formatter = logging.Formatter()
    elif fmt == 'text':
        formatter = logging.Formatter(TEXT_LOG_FORMAT)
    else:
        formatter = jsonlogger.JsonFormatter(JSON_LOG_FORMAT, timestamp=False, json_ensure_ascii=False)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def get_pyzog_handler(name, config_dict, target_dir, level=logging.INFO):
    """ 获取一个 pyzog handler
    如果不存在 pyzog 配置，那么会返回一个 file handler
    :param name: logger 的名称
    :param config_dict: config.json 配置文件的 dict
    :param target_dir: file handler 的目标文件夹
    :param level: handler 级别
    """
    # 如果存在 pyzog 配置，则使用它
    pyzog_conf = None
    if isinstance(config_dict.get('LOGGER'), dict):
        pyzog_conf = config_dict['LOGGER'].get('pyzog')

    if pyzog_conf is None:
        return get_logging_handler('file', 'json', level, target=target_dir, name=name)
    return get_logging_handler(pyzog_conf['type'], 'json', level, target=pyzog_conf['target'], name=name)


def get_logger(name, target, type_='file', fmt='text', level=logging.INFO):
    """ 基于 target 创建一个 logger

    :param name: logger 的名称，不要带扩展名
    :param target: 项目主目录的的 path 字符串或者 Path 对象，也可以是 tcp://127.0.0.1:8334 这样的地址
    :param type_: stream/file/zmq/pyzog 若使用 pyzog ，则调用 get_pyzog_handler，fmt 参数必须为 config_dict
    :param fmt: text/json/config_dict 如果 type_ 参数为 pyzog，则必须为 config_dict
    :param level: logging 的 level 级别
    """
    hdr = None
    if type_ == 'pyzog':
        if not isinstance(fmt, dict):
            raise ValueError('pyzog need a config_dict!')
        hdr = get_pyzog_handler(name, fmt, target, level)
    else:
        hdr = get_logging_handler(type_, fmt, level, target, name)

    log = logging.getLogger(name)
    log.addHandler(hdr)
    log.setLevel(level)
    return log

