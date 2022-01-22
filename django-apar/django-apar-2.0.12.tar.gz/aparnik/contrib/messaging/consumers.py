from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_lazy as _

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection

import json

class MessagingConsumer(AsyncJsonWebsocketConsumer):
    user = AnonymousUser()

    def __init__(self, *args, **kwargs):
        super(MessagingConsumer, self).__init__( *args, **kwargs)

    async def connect(self):
        self.user = self.scope['user']
        if self.user == AnonymousUser():
            raise DenyConnection(_("Invalid User"))

        await self.accept()

        # add to room
        rooms = self.add_to_rooms()
        rooms = await rooms
        rooms.add('broadcast')
        rooms.add(self.user.username)
        for room_id in list(rooms):
            await self.channel_layer.group_add(
                room_id,
                self.channel_name,
            )

        # Store which rooms the user has send on this connection

    async def receive_json(self, content, **kwargs):
        # await self.send_json({"ty": "test"})
        # await self.send_json(content)
        pass

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        # for room_id in list(self.rooms):
        #     self.rooms.discard(room_id)
        #     await self.channel_layer.group_discard(
        #         room_id,
        #         self.channel_name,
        #     )
        pass

    ##### Command helper methods called by receive_json

    # These helper methods are named by the types we send - so chat.join becomes chat_join
    """
    format event:
    :type
    :data
    """
    async def send_data(self, event):
        """
        Called when someone has send data.
        """
        # Send a message down to the client
        params = event['data']
        await self.send_json(
            params,
        )

    # add to room
    @database_sync_to_async
    def add_to_rooms(self):
        l = set()
        from aparnik.contrib.chats.models import ChatSession
        for room_id in ChatSession.objects.user_session(user=self.user).values_list('uri', flat=True):
            l.add(room_id)
        return l


# class MessagingConsumer(AsyncConsumer):
#     def __init__(self, *args, **kwargs):
#         super(MessagingConsumer, self).__init__(*args, **kwargs)
#         self.user = None
#
#     async def websocket_connect(self, event):
#         self.user = self.scope['user']
#         if self.scope['user'] == AnonymousUser():
#             raise DenyConnection(_("Invalid User"))
#
#         await self.send({
#             'type': 'websocket.accept',
#         })
#         # other = None
#         # # other = self.scope['url_route']['kwargs']['username']
#         # print(me, other)
#
#     async def websocket_receive(self, event):
#         print('receive', event)
#         data = await self.deserialize(event)
#         # bar asas data pasokh monaseb
#
#     async def websocket_disconnect(self, event):
#         print('disconnect', event)
#
#
#     async def deserialize(self, data):
#         client_text = data.get('text', None)
#         if client_text is not None:
#             loaded_dict_data = json.loads(client_text)
#             return loaded_dict_data
#         return {}
#
#     @database_sync_to_async
#     def get_thread(self, user, other_username):
#         # return get_or_new(user, other_username)[0]
#         return 1