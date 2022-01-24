from nehushtan.httpd.NehushtanHTTPRequestFilter import NehushtanHTTPRequestFilter


class TestFilter(NehushtanHTTPRequestFilter):
    def should_accept_request(self) -> bool:
        """
        Sample
        ------
        URL: http://localhost:4466/api/TestApi/hi/there?limit=0

        print(self.get_http_handler().parsed_path) # /api/TestApi/hi/there
        print(self.get_http_handler().parsed_query_dict) # {'limit': '0'}
        print(self.get_http_handler().parsed_body_data) # None -> Not Parsed
        """
        if self.get_http_handler().parsed_query_dict.get('limit') == '0':
            return False
        return True
