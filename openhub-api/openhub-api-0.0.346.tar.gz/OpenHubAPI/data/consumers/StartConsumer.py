# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer, WebsocketConsumer
import asyncio


class StartConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(StartConsumer, self).__init__(*args, **kwargs)

    # groups = ["broadcast"]

    async def connect(self):
        await self.accept()
        self.reader, self.writer = await asyncio.open_connection(
            '127.0.0.1', 8888)
        # Called on connection.
        # To accept the connection call:

    async def send_to_core(self, text_data):
        print(f'Send: {text_data!r}')
        self.writer.write((text_data+'\n').encode())
        await self.writer.drain()

        data = await self.reader.readline()
        self.send(text_data=data.decode())

        print(f'Received: {data.decode()!r}')

    async def receive(self, text_data=None, bytes_data=None):
        print('receive')
        await self.send_to_core(text_data)

    async def disconnect(self, close_code):
        print('Close the connection')
        self.writer.close()
        await self.writer.wait_closed()
        self.close()
