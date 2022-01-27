# -*- coding: utf-8 -*-
from apistar.client.transports import HTTPTransport


class ArkindexHTTPTransport(HTTPTransport):
    def get_request_options(self, *args, **kwargs):
        options = super().get_request_options(*args, **kwargs)
        options["timeout"] = (30, 60)
        return options
