from aiohttp import ClientSession, TCPConnector
from aiohttp.test_utils import TestServer, TestClient
from aiohttp.web import Application
from heaobject.root import json_dumps
from heaserver.service import appproperty
import pytest
from aiohttp.test_utils import AioHTTPTestCase
import abc


class HEAAioHTTPTestCase(AioHTTPTestCase, abc.ABC):
    """
    Base class for HEA test cases.
    """

    def __init__(self, methodName=None, port=None):
        super().__init__(methodName=methodName)
        self._port = port

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @abc.abstractmethod
    async def get_application(self) -> Application:
        pass

    async def get_server(self, app: Application) -> TestServer:
        """
        Overrides this method to allow setting a fixed port for running aiohttp. If no port was specified in the
        constructor, a random port will be selected.

        :param app: the aiohttp application.
        :return: a new aiohttp TestServer instance.
        """
        if self._port:
            return TestServer(app, port=self._port)
        else:
            return TestServer(app)

    async def get_client(self, server: TestServer) -> TestClient:
        """Return a TestClient instance."""
        return TestClient(server, loop=self.loop, json_serialize=json_dumps)

    async def setUpAsync(self) -> None:
        await super().setUpAsync()
        self.app[appproperty.HEA_CLIENT_SESSION] = ClientSession(connector=TCPConnector(), connector_owner=True,
                                                                 json_serialize=json_dumps,
                                                                 raise_for_status=True)

    async def tearDownAsync(self) -> None:
        try:
            await super().tearDownAsync()
            if appproperty.HEA_CLIENT_SESSION in self.app:
                await self.app[appproperty.HEA_CLIENT_SESSION].close()
        finally:
            if appproperty.HEA_CLIENT_SESSION in self.app and \
                not self.app[appproperty.HEA_CLIENT_SESSION].closed:
                try:
                    await self.app[appproperty.HEA_CLIENT_SESSION].close()
                except:
                    pass
