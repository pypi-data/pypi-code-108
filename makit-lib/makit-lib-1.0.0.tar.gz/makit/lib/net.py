# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import re
import socket
from typing import Optional, Union, Pattern


def free_port():
    """
    获取空闲端口
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    try:
        return s.getsockname()[1]
    finally:
        s.close()


def get_local_ip():
    """
    获取本机IP
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]


def connectable(port, host="localhost"):
    """
    Test if the host can be connected at the port.
    :param port:
    :param host:
    :return:
    """
    socket_ = None
    try:
        socket_ = socket.create_connection((host, port), 1)
        result = True
    except socket.error:
        result = False
    finally:
        if socket_:
            socket_.close()
    return result


def url_reachable(url):
    """
    Check if the url can be visited.
    :param url:
    :return:
    """
    from urllib import request as url_request

    try:
        res = url_request.urlopen(url)
        if res.getcode() == 200:
            return True
        else:
            return False
    except Exception:
        return False


def parse_host_ip(host, port=None):
    """
    解析指定主机IP地址
    :param host:
    :param port:
    :return:
    """
    try:
        addr_infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return None

    ip = None
    for family, _, _, _, sock_addr in addr_infos:
        _connectable = True
        if port:
            _connectable = connectable(port, sock_addr[0])

        if _connectable and family == socket.AF_INET:
            return sock_addr[0]
        if _connectable and not ip and family == socket.AF_INET6:
            ip = sock_addr[0]
    return ip


_ipv4_pattern = (
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
_ipv6_pattern = (
    r"^(?:(?:(?:[A-F0-9]{1,4}:){6}|(?=(?:[A-F0-9]{0,4}:){0,6}"
    r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}$)(([0-9A-F]{1,4}:){0,5}|:)"
    r"((:[0-9A-F]{1,4}){1,5}:|:)|::(?:[A-F0-9]{1,4}:){5})"
    r"(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])|(?:[A-F0-9]{1,4}:){7}"
    r"[A-F0-9]{1,4}|(?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}$)"
    r"(([0-9A-F]{1,4}:){1,7}|:)((:[0-9A-F]{1,4}){1,7}|:)|(?:[A-F0-9]{1,4}:){7}"
    r":|:(:[A-F0-9]{1,4}){7})$"
)
_ipv4_regex = re.compile(_ipv4_pattern)
_ipv6_regex = re.compile(_ipv6_pattern, flags=re.IGNORECASE)
_ipv4_regexb = re.compile(_ipv4_pattern.encode("ascii"))
_ipv6_regexb = re.compile(_ipv6_pattern.encode("ascii"), flags=re.IGNORECASE)


def _is_ip_address(
        regex: Pattern[str], regexb: Pattern[bytes], host: Optional[Union[str, bytes]]
) -> bool:
    if host is None:
        return False
    if isinstance(host, str):
        return bool(regex.match(host))
    elif isinstance(host, (bytes, bytearray, memoryview)):
        return bool(regexb.match(host))
    else:
        raise TypeError("{} [{}] is not a str or bytes".format(host, type(host)))


def is_ipv4_address(addr: Union[str, bytes]):
    return _is_ip_address(_ipv4_regex, _ipv4_regexb, addr)


def is_ipv6_address(addr: Union[str, bytes]):
    return _is_ip_address(_ipv6_regex, _ipv6_regexb, addr)


def is_ip_address(host: Optional[Union[str, bytes, bytearray, memoryview]]) -> bool:
    return is_ipv4_address(host) or is_ipv6_address(host)
