from nehushtan.httpd.NehushtanHTTPRequestController import NehushtanHTTPRequestController


class TestProcessChainB(NehushtanHTTPRequestController):
    def list(self, x: str):
        index = self._get_http_handler().parsed_query_dict.get('index', -1)
        # header_cookie=self._read_header('cookie')
        a = self._read_cookie('a')
        b = self._read_cookie(u'喵')
        self._reply_with_ok(
            {
                "index": index,
                'cookie': self._get_http_handler().parsed_cookie_dict,
                'a': a,
                'b': b,
                'x': x,
            }
        )

    def step3(self, step: float):
        x = self._get_http_handler().get_process_chain_share_data_dict().get('index', step)
        self._reply_with_ok(x)

    def mix(self, index: int, name: str, value: float, action: str):
        self._reply_with_ok({'index': index, 'name': name, 'value': value, 'action': action})

    def args(self, a: int, b: float, c: str, d: str = 'd', e: str = 'e'):
        self._reply_with_ok({'a': a, 'b': b, 'c': c, 'd': d, 'e': e})
