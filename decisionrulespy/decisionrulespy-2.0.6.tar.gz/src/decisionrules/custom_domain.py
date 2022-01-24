from .enums import Protocols


class CustomDomain:
    _custom_domain_url = None
    _custom_domain_protocol: Protocols = None

    def __init__(self, custom_domain_url, custom_domain_protocol: Protocols):
        self._custom_domain_url = custom_domain_url
        self._custom_domain_protocol = custom_domain_protocol

    @property
    def custom_domain_url(self):
        return self._custom_domain_url

    @property
    def custom_domain_protocol(self):
        return self._custom_domain_protocol
