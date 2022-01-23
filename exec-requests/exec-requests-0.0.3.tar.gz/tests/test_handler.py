from execrequests import RequestsHandler, RequestsConf
from random import choice


def proxy_generator_():
    return choice(['user:password@0.0.0.0:00000', 'user:password@0.0.0.1:00000'])


# RequestsConf.headers.reset()
RequestsConf.proxies.extend(['user:password@1.1.1.0:11111', 'user:password@1.1.1.1:11111'])


class WebberHandler(RequestsHandler):
    def __init__(self, puser=None, set_proxy=True, proxy_generator=[None, proxy_generator_][0]):
        super(WebberHandler, self).__init__(puser, set_proxy, proxy_generator)


puser_ = {
    'proxy': 'puser_user:password@1.1.1.1:1111',
    'cookies': {'cookies': 'puser_cookies1'},
    'headers': {'headers': "puser_headers1"}
}


if __name__ == '__main__':
    webber = WebberHandler(set_proxy=False)
    # webber = RequestsHandler()
    # webber.puser_update(puser_)
    webber.puser_reset(puser_)
    print(webber.headers)
    print(webber.cookies.get_dict())
    print(webber.proxies)
    # res = webber.get('https://httpbin.org/get')
    # print(res.status_code, res.json())
