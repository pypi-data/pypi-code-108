# pytest example for boilerplate processor

import sys
import os
import json
# noinspection PyPackageRequirements, PyUnresolvedReferences
import msgpack
# noinspection PyPackageRequirements, PyUnresolvedReferences
import fabrique_actor.dummy  # needs for automocking on import

cur_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_file_dir, '..'))

# noinspection PyPackageRequirements, PyUnresolvedReferences
from actor import Actor


def test_full_emutation(monkeypatch):
    TOPIC_OUT = 'topic.out'
    monkeypatch.setenv('TOPIC_OUT', TOPIC_OUT)

    # create child class to limit iterations
    iterations = 10
    class ActorTestChild(Actor):
        i = 0
        def create_message(self):
            self.i += 1
            if self.i > iterations:
                raise StopIteration
            return super().create_message()

    actor = ActorTestChild()
    store = actor.store  # dummy actor has store - simple kafka emulator from fabrique_atelier

    # emulate this
    #    [Emitter] -> (TOPIC_OUT)

    # start emulation
    actor.start()

    # check results in TOPIC_OUT from kafka (as store)
    results = [json.loads(r.value()) for r in store.topics[TOPIC_OUT]][::-1]
    assert len(results) == iterations
