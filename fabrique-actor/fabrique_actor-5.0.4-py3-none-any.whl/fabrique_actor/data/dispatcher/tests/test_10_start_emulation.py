import sys
import os
import json
import random

from fabrique_actor.dummy import DummyLogger

cur_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_file_dir, '..'))

# noinspection PyPackageRequirements, PyUnresolvedReferences
from actor import Actor


def test_full_emutation(monkeypatch):
    random.seed(1337)
    TOPIC_IN = 'topic.in'
    topic_out_dict = {"bad": "bad_values.topic",
                      "big_scores": "big_scores.topic",
                      "small_scores": "small_scores.topic"}

    monkeypatch.setenv('TOPIC_IN', TOPIC_IN)
    monkeypatch.setenv('TOPIC_OUT_DICT', json.dumps(topic_out_dict))

    example_messages = [json.dumps({'uid': uid, 'score': random.random()}).encode() for uid in range(10)]
    actor = Actor()

    store = actor.store  # dummy actor has store - simple kafka emulator from fabrique_atelier

    # let's write messages to TOPIC_IN to emulate this
    #    (TOPIC_IN) -> [Dispatcher] -> (topic_out_dict["bad" or "big_scores" or "small_scores"])
    for msg in example_messages:
        store.produce(TOPIC_IN, msg)

    # easy logs collector
    logger = DummyLogger()
    actor.logger = logger

    # start emulation
    actor.start()

    # check results in output topics
    topic2msgs = lambda topic: [json.loads(r.value()) for r in store.topics.get(topic, [])][::-1]
    res_bad, res_big, res_small = [topic2msgs(topic_out_dict[destination])
                                   for destination in ['bad', 'big_scores', 'small_scores']]
    assert len(res_big) + len(res_small) == len(example_messages)
    assert len(res_bad) == 0
    assert len(res_big) > 0
    assert len(res_small) > 0

    # check logging
    assert len(logger.logs_debug) == len(example_messages)
