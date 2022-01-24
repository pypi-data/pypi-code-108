import asyncio
from ducts_client import Duct
from .controllers import ResourceController, MTurkController
from .listeners import ResourceEventListener, MTurkEventListener

class TuttiClient:
    def __init__(self):
        super()

        self._duct = Duct()
        self._opened = False

        self.account_info = {
            'user_name': None,
            'user_id': None,
            'access_token': None,
        }

    async def open(self, wsd_path):
        if not self._duct:
            self._duct = Duct()
        await self._duct.open(wsd_path)

        self.resource = ResourceManager(self._duct)
        self.mturk = MTurkManager(self._duct)

        self.on_connection = self._duct.connection_listener

        wsd = await self.resource.get_web_service_descriptor.call()
        self.ENUM = wsd['enums']
        self.ERROR = wsd['enums']['errors']

        self.resource.on('sign_in', success=self._on_sign_in)
        self.resource.on('sign_out', success=self._on_sign_out)

        self._opened = True

    async def _on_sign_in(self, data):
        self._set_account_info(data)

    async def _on_sign_out(self):
        self._delete_account_info()

    async def reconnect(self):
        await self._duct.reconnect()

    def close(self):
        self._duct.close()

    def _set_account_info(self, data):
        self.account_info['user_name'] = data['user_name']
        self.account_info['user_id'] = data['user_id']
        self.account_info['access_token'] = data['access_token']
        self.resource._access_token = self.account_info['access_token']
        self.mturk._access_token = self.account_info['access_token']

    def _delete_account_info(self):
        self.account_info.user_name = None
        self.account_info.user_id = None
        self.account_info.access_token = None

class ResourceManager(ResourceController):
    def __init__(self, duct):
        super().__init__(duct)
        self.on = ResourceEventListener(duct).on
        self._access_token = None

class MTurkManager(MTurkController):
    def __init__(self, duct):
        super().__init__(duct)
        self.on = MTurkEventListener(duct).on
        self._access_token = None
