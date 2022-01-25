from fabrique_actor.actors import Emitter
import json  # or another serialization lib
import random


class Actor(Emitter):
    def _emit(self):
        uid = random.randint(0, 10000)
        value = json.dumps({'data': random.random(), 'uid': uid}).encode()  # message payload example
        key = str(uid).encode()  # kafka key, None if not needed
        return value, key

    def create_message(self):
        return self._emit()
