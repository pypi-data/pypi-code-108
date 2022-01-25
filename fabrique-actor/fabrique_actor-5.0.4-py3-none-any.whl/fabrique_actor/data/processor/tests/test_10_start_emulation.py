# pytest example for boilerplate processor

import sys
import os
import json
import random
# noinspection PyPackageRequirements
import msgpack
from fabrique_actor.dummy import DummyLogger, DUMMY_FABRIQUE_METRIC_COLLECTOR_TOPIC

cur_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_file_dir, '..'))

# noinspection PyPackageRequirements, PyUnresolvedReferences
from actor import Actor


def test_full_emutation(monkeypatch):
    random.seed(1337)
    TOPIC_IN = 'topic.in'
    TOPIC_OUT = 'topic.out'
    monkeypatch.setenv('TOPIC_IN', TOPIC_IN)
    monkeypatch.setenv('TOPIC_OUT', TOPIC_OUT)

    example_messages = [json.dumps({'data': random.random(), 'uid': uid}).encode() for uid in range(10)]
    actor = Actor()

    store = actor.store  # dummy actor has store - simple kafka emulator from fabrique_atelier

    # let's write messages to TOPIC_IN to emulate this
    #    (TOPIC_IN) -> [Processor] -> (TOPIC_OUT)
    for msg in example_messages:
        store.produce(TOPIC_IN, msg)

    # easy logs collector
    logger = DummyLogger()
    actor.logger = logger

    # start emulation
    actor.start()

    # check results in TOPIC_OUT from kafka (as store)
    results = [json.loads(r.value()) for r in store.topics[TOPIC_OUT]][::-1]
    assert len(results) == len(example_messages)

    # check processor logic
    get_score = lambda value: 0.0 if value < 0.5 else 1.0
    for result in results:
        expected_score = get_score(result['data'])
        happened_score = result['score']
        assert expected_score == happened_score, f'invalid result in {result}'

    # check logging
    assert len(logger.logs_debug) == len(results)

    # check "score" metrics
    metric_name = 'score'
    metrics_msg_list = [msgpack.loads(m.value(), raw=False)
                        for m in store.topics[DUMMY_FABRIQUE_METRIC_COLLECTOR_TOPIC]][::-1]

    mes_scores = [msg for msg in metrics_msg_list if msg['body']['metrics'].get(metric_name) is not None]
    assert len(mes_scores) == len(example_messages), f'all your metric messages should have {metric_name}'
