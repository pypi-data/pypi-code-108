# Copyright 2021 Cegal AS
# All rights reserved


class _AuthException(Exception):
    def __init__(self):
        super().__init__(self)


class NotRespondingException(_AuthException):
    def __init__(self, provider, response):
        self.message = f"Identity provider: ({provider}) did not respond."
        self.response = response

    def __str__(self):
        return f"{self.message} [{self.response.status_code}: {self.response.read()}]"


class NotReachableException(_AuthException):
    def __init__(self, provider, ex):
        self.message = f"Identity provider: ({provider}). Please check your network configuration and firewall settings."
        self.ex = ex

    def __str__(self):
        return f"{self.message} [{self.ex}]"
