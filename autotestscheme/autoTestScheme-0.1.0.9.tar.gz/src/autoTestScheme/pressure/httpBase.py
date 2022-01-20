from locust import HttpUser
from .case import Case
from base.base import TestBase


class HttpCase(HttpUser, Case, TestBase):

    def __init__(self, *args, **kwargs):
        super(HttpCase, self).__init__(*args, **kwargs)
        Case.__init__(self)

    def start(self, *args, **kwargs):
        self.singleton.run()
        super().start(*args, **kwargs)

    def on_locust_setup(self):
        super().on_locust_setup()
        self.session.catch_response = True
        self.session.session = self.client
