import websockets
from . import message_crypt


class Sender:
    def __init__(self, uri, key=None):
        self.uri = uri
        self.key = key
        self.conn = None
        if self.key:
            self.crypt = message_crypt.MessageCrypt(self.key)

    async def connect(self):
        if (not self.conn) or self.conn.closed:
            self.conn = await websockets.connect(self.uri)

    async def send(self, message):
        await self.connect()
        send_message = message if not self.key\
            else self.crypt.json_encrypt(message)
        await self.conn.send(send_message)
