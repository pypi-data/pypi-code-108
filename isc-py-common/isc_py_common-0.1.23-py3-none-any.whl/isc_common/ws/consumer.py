from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        kwargs = self.scope['url_route']['kwargs']
        channel = kwargs.get('channel')

        self.group = f'group_{channel}'

        # Join room group
        await self.channel_layer.group_add(self.group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.channel_layer.group_send(
                self.group,
                {
                    'type': 'common',
                    'text_data': text_data
                }
            )
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    # Receive message from room group
    async def common(self, event):
        text_data = event['text_data']

        # Send message to WebSocket
        await self.send(text_data=text_data)
