import importlib

from nacl.signing import VerifyKey
from starlette.applications import Starlette

from discourtesy.command import Command
from discourtesy.component import Component
from discourtesy.dispatch import Dispatch
from discourtesy.http import HTTPClient
from discourtesy.routes import IndexRoute, InteractionRoute

version = "0.2.0"


class Application(Starlette):
    def __init__(self, application_id, public_key, token):
        super().__init__(
            routes=[IndexRoute(), InteractionRoute()],
            on_shutdown=[self.on_shutdown],
        )

        self.application_id = application_id
        self.public_key = bytes.fromhex(public_key)
        self.token = token

        self.verify_key = VerifyKey(self.public_key)

        self.dispatch = Dispatch()
        self.http = HTTPClient(application_id, token)

        self.add_plugin("__main__")

    def add_plugin(self, path):
        module = importlib.import_module(path)

        for name in dir(module):
            attribute = getattr(module, name)

            if isinstance(attribute, Command):
                self.dispatch.add_command(attribute)

            if isinstance(attribute, Component):
                self.dispatch.add_component(attribute)

    async def on_shutdown(self):
        await self.http.aclose()
