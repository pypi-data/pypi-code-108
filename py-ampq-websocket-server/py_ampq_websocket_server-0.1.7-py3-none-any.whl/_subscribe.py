import json
import logging

from ampq_websockets._token import Token


class Subscribe:

    def __init__(self, secret_key: str, uid: str, server) -> None:
        self.uid = uid
        self.conn = server.connections[uid]
        self.server = server
        self.logger = logging.getLogger(__name__)
        self.redis = server.redis_client
        self.host = self.get_host()
        self.secret_key = secret_key

    def get_host(self) -> None:
        return self.server.queue

    def _compat_transform(self, obj: dict) -> None:
        data = obj['data']
        if 'room' not in data and 'channel' in data:
            data['room'] = data['channel']

    def add(self, data: str) -> None:
        try:
            obj = json.loads(data)
            token = Token(self.secret_key)
            self._compat_transform(obj)
            room = obj['data']['room']

            token.get_data(obj['token'], room)

            uid = self.uid
            self.server.add_subscriber_room(
                room, self.conn
            )
            self.logger.debug(
                f"sockjs (Subscribe): Subscribe to channel {room}")
            self.redis.lpush(
                room,
                json.dumps({'host': self.host, 'id': uid})
            )
        except (KeyError, TypeError):
            pass

    def remove(self) -> None:
        for room in self.server.subscribers[self.uid]:
            self.redis.lrem(
                room,
                0,
                json.dumps({'id': self.uid, 'host': self.host})
            )
        self.server.remove_subscriber(self.uid)
        self.logger.debug(
            f"sockjs (Subscirbe):Unsubscribe from connection {self.uid}")
