
class TcpCallbackBase:
    async def on_connect(self, session):
        pass

    async def on_close(self, session):
        pass

    async def on_msg(self, session, data: bytes):
        pass
