from fabrique_actor.actors import Collector

# 0. import your dependencies

class Actor(Collector):
    def __init__(self):
        super().__init__()

        # 1. here can be db connection, or query connection, or something else

    def _collect(self, mes_bodies: list) -> None:

        # 2. your custom method for collecting message, returns nothing
   
    def process_raw_messages_list(self, msgs2process: list) -> None:
        self._collect(msgs2process)