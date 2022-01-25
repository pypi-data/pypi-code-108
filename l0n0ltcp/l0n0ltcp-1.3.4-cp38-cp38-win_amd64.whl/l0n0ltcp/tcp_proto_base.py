from asyncio.streams import StreamReader


class TcpProtoBase:
    def make_heart_msg(self) -> bytes:
        return b''

    def build_msg(self, data: bytes) -> bytes:
        return data

    async def read_msg(self, session):
        data = await session.reader.read(4096)
        if len(data) <= 0:
            session.close()
            return
        return data
