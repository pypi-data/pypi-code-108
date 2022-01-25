from fabrique_actor.actors import Processor
import json  # or another serialization lib
from typing import Optional


class Actor(Processor):
    """your custom message processor class"""
    def __init__(self):
        """here can be db connection, or query connection, or something else"""
        super().__init__()  # required init of

    def _process(self, mes_body: bytes) -> Optional[bytes]:
        """
        Your method of:
        1. Deserialization (for example json.loads())
        2. Processing
        3. Serialization (for example json.dumps())
        if returns None, nothing will be sent to TOPIC_OUT
        """
        payload = json.loads(mes_body)  # can be any binary data, here we require json

        # do some toy processing with payload
        data = payload.get('data')  # if this mes is from toy emitter {'data': random.random(), 'uid': uid}
        if data is None:
            return  # this sends nothing

        score = 0.0 if data < 0.5 else 1.0

        payload['score'] = score
        # serialize and return
        out_mes_body = json.dumps(payload)

        self.logger.debug('some debug info if needed')
        self.send_metrics(metrics={'score': score})  # will be stored in analytic db (for example clickhouse)

        return out_mes_body  # this sends serialised {'data': random.random(), 'uid': uid, 'score': score}


    def process_message(self, mes_body: bytes) -> Optional[bytes]:
        return self._process(mes_body)
