# Copyright (C) 2021 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import functools
import re

import pytest

from swh.journal.client import JournalClient
from swh.journal.writer import get_journal_writer
from swh.model.model import Content
from swh.objstorage.factory import get_objstorage
from swh.objstorage.replayer import replay
from swh.objstorage.replayer.replay import process_replay_objects_content


@pytest.fixture
def statsd(monkeypatch, statsd):
    monkeypatch.setattr(replay, "statsd", statsd)
    yield statsd


def test_replay_statsd(kafka_server, kafka_prefix, kafka_consumer_group, statsd):
    objstorage1 = get_objstorage(cls="memory")
    objstorage2 = get_objstorage(cls="memory")

    writer = get_journal_writer(
        cls="kafka",
        brokers=[kafka_server],
        client_id="kafka_writer",
        prefix=kafka_prefix,
        anonymize=False,
    )

    # Fill the source objstorage with a bunch of content object. In the end,
    # there should be 2 content objects for each possible replaying decision
    # (aka. skipped, excluded, in_dst, not_in_src, failed and copied):
    # contents[0:2] are properly copied
    # contents[2:4] are excluded
    # contents[4:6] are in dst
    # contents[6:8] are hidden
    contents = [
        Content.from_data(
            f"foo{i}".encode(), status="hidden" if 6 <= i < 8 else "visible"
        )
        for i in range(8)
    ]

    for content in contents:
        objstorage1.add(content.data)
        writer.write_addition("content", content)
    excluded = [c.sha1 for c in contents[2:4]]

    def exclude_fn(cnt_d):
        return cnt_d["sha1"] in excluded

    for content in contents[4:6]:
        objstorage2.add(content.data)

    replayer = JournalClient(
        brokers=kafka_server,
        group_id=kafka_consumer_group,
        prefix=kafka_prefix,
        stop_on_eof=True,
        # stop_after_objects=len(objects),
    )

    worker_fn = functools.partial(
        process_replay_objects_content,
        src=objstorage1,
        dst=objstorage2,
        exclude_fn=exclude_fn,
    )
    replayer.process(worker_fn)

    # We cannot expect any order from replayed objects, so statsd reports won't
    # be sorted according to contents, so we just count the expected occurrence
    # of each statsd message.
    prefix = "swh_content_replayer"
    expected_reports = {
        # 4 because 2 for the copied objects + 2 for the in_dst ones
        f"^{prefix}_retries_total:1[|]c[|]#attempt:1,operation:obj_in_objstorage$": 4,
        f"^{prefix}_retries_total:1[|]c[|]#attempt:1,operation:get_object$": 2,
        f"^{prefix}_retries_total:1[|]c[|]#attempt:1,operation:put_object$": 2,
        f"^{prefix}_duration_seconds:[0-9]+[.][0-9]+[|]ms[|]#request:get$": 2,
        f"^{prefix}_duration_seconds:[0-9]+[.][0-9]+[|]ms[|]#request:put$": 2,
        f"^{prefix}_bytes:4[|]c$": 2,
    }
    decisions = ("copied", "skipped", "excluded", "in_dst", "not_in_src", "failed")
    decision_re = (
        "^swh_content_replayer_operations_total:1[|]c[|]#decision:(?P<decision>"
        + "|".join(decisions)
        + ")(?P<extras>,.+)?$"
    )

    operations = dict.fromkeys(decisions, 0)
    reports = dict.fromkeys(expected_reports, 0)

    for report in (r.decode() for r in statsd.socket.payloads):
        m = re.match(decision_re, report)
        if m:
            operations[m.group("decision")] += 1
        else:
            for expected in expected_reports:
                m = re.match(expected, report)
                if m:
                    reports[expected] += 1

    assert reports == expected_reports

    assert operations["skipped"] == 2
    assert operations["excluded"] == 2
    assert operations["in_dst"] == 2
    assert operations["copied"] == 2
    # TODO:
    assert operations["not_in_src"] == 0
    assert operations["failed"] == 0
