from six.moves.urllib.parse import urlparse


def verify_proxy_uri(proxy_uri):
    proxy_uri = urlparse(proxy_uri)
    proxy_type = proxy_uri.scheme
    if proxy_type.upper() not in ['HTTP', 'SOCKS4', 'SOCKS5']:
        raise ValueError("代理开头应该类似: http:// 、SOCKS4:// 或者 SOCKS5://")
    return True