from execrequests import RequestsConf


headers = [{'User-Agent': 'header1', 'content_type': 'json'}]
cookies = [{'cookies': 1}, {'cookies': 2, 'session': 2}][:10]
proxies = ['user:password@1.1.1.1:11111', 'user:password@2.2.2.2:11111'][:10]
proxy_ = 'user:password@3.3.3.3:11111'
header_ = {'User-Agent': 'header2'}
cookie_ = {'cookies': 3}


def test_headers(func):
    func(headers)
    print(RequestsConf.headers)
    print(RequestsConf.headers.random())


def test_cookies(func):
    func(cookies)
    print(RequestsConf.cookies)
    print(RequestsConf.cookies.random({}))


def test_proxies(func):
    func(proxies)
    print(RequestsConf.proxies)
    print(RequestsConf.proxies.random())


def test_random_headers(func, header=None, set_new=True):
    test_headers(func)
    print(RequestsConf.random_headers(headers=header, set_new=set_new))


def test_random_cookies(func, cookie=None, set_new=True):
    test_cookies(func)
    print(RequestsConf.random_cookies(cookies=cookie, set_new=set_new))


def test_random_proxy(func, proxy=None, proxy_type: tuple = None):
    test_proxies(func)
    print(RequestsConf.random_proxy(proxy=proxy, proxy_type=proxy_type))


if __name__ == '__main__':
    # test_headers(RequestsConf.headers.reset)
    # test_cookies(RequestsConf.cookies.reset)
    # test_proxies(RequestsConf.proxies.reset)
    # test_random_headers(RequestsConf.headers.extend, header=[None, header_][0], set_new=False)
    # test_random_cookies(RequestsConf.cookies.extend, cookie=[None, cookie_][1], set_new=False)
    test_random_proxy(RequestsConf.proxies.reset, proxy=[None, proxy_][1])
