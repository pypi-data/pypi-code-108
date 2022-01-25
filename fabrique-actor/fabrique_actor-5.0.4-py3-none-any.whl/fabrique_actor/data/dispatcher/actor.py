from fabrique_actor.actors import Dispatcher
import json  # or another serialization lib
from typing import Tuple, Union

DESTINATIONS = ['bad', 'big_scores', 'small_scores']  # example of your dispatcher destination names


# TOPIC_OUT_DICT in this example must be json which looks like
# """
# {
#       "bad": "your.bad.values.topic",
#       "big_scores": "your.big_scores.values.topic",
#       "small_scores": "your.small_scores.values.topic"
# }
# """


class Actor(Dispatcher):
    """your custom message dispatcher class"""

    def __init__(self):
        """here can be db connection, or query connection, or something else"""
        super().__init__()

        # let's check if all destination values in TOPIC_OUT_DICT
        for destination in DESTINATIONS:
            if destination not in self.topic_out_dict:
                raise Exception(f'{destination} not in your TOPIC_OUT_DICT env variable!')

        # self.dest = namedtuple('destinations', DESTINATIONS)(*DESTINATIONS)  # fancy enum-like with dot notation

    def _dispatch(self, mes_body: bytes) -> Tuple[Union[bytes, None], Union[str, None]]:
        """
        Your method of:
        1. Deserialization (for example json.loads())
        2. Processing
        3. Serialization (for example json.dumps())
        4. Pick destination
        if returns (None, None), (None, str), (bytes, None) nothing will be sent to output topics
        your TOPIC_OUT_DICT env looks like json string {"destination_id1": "dest_topic1",
        "destination_id2": "dest_topic2", ...}

        :param mes_body: serialized message body in bytes
        :return: (serialized message body in bytes, destination_id str)
        """
        payload = {}
        dst = self.destinations

        try:
            payload = json.loads(mes_body)  # can be any binary data, here we require json
            score = payload['score']
        except KeyError:
            payload['reason'] = 'Score is not computed'
            return json.dumps(payload), dst.bad
        except Exception:
            payload['reason'] = 'Parse error'
            return json.dumps(payload), dst.bad

        if score > 0.5:
            topic_out = dst.big_scores
            reason = 'The score is big enough'
            self.logger.debug(f'{reason} {score} > 0.5, send in big_scores topic ( {dst.big_scores} )')
        else:
            topic_out = dst.small_scores
            reason = 'The score is too small'
            self.logger.debug(f'{reason}  {score} <= 0.5, send in small_scores topic ({dst.small_scores})')
        payload['reason'] = reason

        # your TOPIC_OUT_DICT value for this example must
        return json.dumps(payload), topic_out

    def process_message(self, mes_body: bytes) -> Tuple[Union[bytes, None], Union[str, None]]:
        return self._dispatch(mes_body)
