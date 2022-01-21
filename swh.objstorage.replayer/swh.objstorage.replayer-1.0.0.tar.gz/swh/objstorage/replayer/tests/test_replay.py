# Copyright (C) 2019-2020 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import functools

from hypothesis import given, settings
from hypothesis.strategies import sets

from swh.journal.client import JournalClient
from swh.journal.writer import get_journal_writer
from swh.model.hypothesis_strategies import sha1
from swh.model.model import Content
from swh.objstorage.factory import get_objstorage
from swh.objstorage.replayer.replay import (
    is_hash_in_bytearray,
    process_replay_objects_content,
)

CONTENTS = [Content.from_data(f"foo{i}".encode()) for i in range(10)] + [
    Content.from_data(f"forbidden foo{i}".encode(), status="hidden") for i in range(10)
]


@settings(max_examples=500)
@given(
    sets(sha1(), min_size=0, max_size=500), sets(sha1(), min_size=10),
)
def test_is_hash_in_bytearray(haystack, needles):
    array = b"".join(sorted(haystack))
    needles |= haystack  # Exhaustively test for all objects in the array
    for needle in needles:
        assert is_hash_in_bytearray(needle, array, len(haystack)) == (
            needle in haystack
        )


def test_replay_content(kafka_server, kafka_prefix, kafka_consumer_group):
    objstorage1 = get_objstorage(cls="memory")
    objstorage2 = get_objstorage(cls="memory")

    writer = get_journal_writer(
        cls="kafka",
        brokers=[kafka_server],
        client_id="kafka_writer",
        prefix=kafka_prefix,
        anonymize=False,
    )

    for content in CONTENTS:
        objstorage1.add(content.data)
        writer.write_addition("content", content)

    replayer = JournalClient(
        brokers=kafka_server,
        group_id=kafka_consumer_group,
        prefix=kafka_prefix,
        stop_on_eof=True,
        # stop_after_objects=len(objects),
    )

    worker_fn = functools.partial(
        process_replay_objects_content, src=objstorage1, dst=objstorage2
    )
    replayer.process(worker_fn)
    # only content with status visible will be copied in storage2
    expected_objstorage_state = {
        c.sha1: c.data for c in CONTENTS if c.status == "visible"
    }

    assert expected_objstorage_state == objstorage2.state
