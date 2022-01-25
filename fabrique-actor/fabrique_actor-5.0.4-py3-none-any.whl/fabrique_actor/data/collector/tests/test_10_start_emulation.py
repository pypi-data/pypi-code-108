# pytest example for boilerplate collector

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
    # set envvars
    TOPIC_IN = 'topic.in'
    monkeypatch.setenv('TOPIC_IN', TOPIC_IN)

    random.seed(1337)
    example_messages = [json.dumps({'data': random.random(), 'uid': uid}).encode() for uid in range(10)]
    actor = Actor()

    store = actor.store  # dummy actor has store - simple kafka emulator from fabrique_atelier

    # let's write messages to TOPIC_IN to emulate this
    #    (TOPIC_IN) -> [Collector] -> logs
    for msg in example_messages:
        store.produce(TOPIC_IN, msg)

    # easy logs collector
    logger = DummyLogger()
    actor.logger = logger

    # start emulation
    actor.start()

    # check logging
    assert len(logger.logs_info) == len(example_messages)
