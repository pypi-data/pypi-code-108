from nehushtan.httpd.NehushtanHTTPRequestController import NehushtanHTTPRequestController


class TestProcessChainA(NehushtanHTTPRequestController):
    def read(self, index: int):
        # self.get_http_handler().log_message('emmm')
        # self._get_http_handler().send_response(200)
        # self._get_http_handler().send_header('content-type', 'text/plain')
        # self._get_http_handler().end_headers()
        # self._get_http_handler().wfile.write(f'READ INDEX [{index}]'.encode())
        self._reply_with_ok({'index': index})

    def step1(self, index: str):
        self._get_http_handler().get_process_chain_share_data_dict()['index'] = int(index)

    def step2(self):
        x = self._get_http_handler().get_process_chain_share_data_dict().get('index', 0)
        self._get_http_handler().get_process_chain_share_data_dict()['index'] = (x + 1)
