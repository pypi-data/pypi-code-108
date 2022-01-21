# Copyright (C) 2019-2022  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from collections import Counter
import copy
import functools
import logging
import re
from subprocess import Popen
import tempfile
from typing import Tuple
from unittest.mock import patch

from click.testing import CliRunner
from confluent_kafka import Producer
import msgpack
import pytest
import yaml

from swh.journal.serializers import key_to_kafka
from swh.model.hashutil import hash_to_hex
from swh.objstorage.backends.in_memory import InMemoryObjStorage
from swh.objstorage.replayer.cli import objstorage_cli_group
from swh.objstorage.replayer.replay import CONTENT_REPLAY_RETRIES

logger = logging.getLogger(__name__)


CLI_CONFIG = {
    "objstorage": {"cls": "mocked", "name": "src",},
    "objstorage_dst": {"cls": "mocked", "name": "dst",},
}


@pytest.fixture
def monkeypatch_retry_sleep(monkeypatch):
    from swh.objstorage.replayer.replay import get_object, obj_in_objstorage, put_object

    monkeypatch.setattr(get_object.retry, "sleep", lambda x: None)
    monkeypatch.setattr(put_object.retry, "sleep", lambda x: None)
    monkeypatch.setattr(obj_in_objstorage.retry, "sleep", lambda x: None)


def _patch_objstorages(names):
    objstorages = {name: InMemoryObjStorage() for name in names}

    def get_mock_objstorage(cls, **args):
        assert cls == "mocked", cls
        return objstorages[args["name"]]

    def decorator(f):
        @functools.wraps(f)
        @patch("swh.objstorage.factory.get_objstorage")
        def newf(get_objstorage_mock, *args, **kwargs):
            get_objstorage_mock.side_effect = get_mock_objstorage
            f(*args, objstorages=objstorages, **kwargs)

        return newf

    return decorator


def invoke(*args, env=None, **kwargs):
    config = copy.deepcopy(CLI_CONFIG)
    config.update(kwargs)

    runner = CliRunner()
    with tempfile.NamedTemporaryFile("a", suffix=".yml") as config_fd:
        yaml.dump(config, config_fd)
        config_fd.seek(0)
        args = ["-C" + config_fd.name] + list(args)
        return runner.invoke(
            objstorage_cli_group, args, obj={"log_level": logging.DEBUG}, env=env,
        )


def test_replay_help():
    result = invoke("replay", "--help",)
    expected = (
        r"^\s*Usage: objstorage replay \[OPTIONS\]\s+"
        r"Fill a destination Object Storage.*"
    )
    assert result.exit_code == 0, result.output
    assert re.match(expected, result.output, re.MULTILINE), result.output


NUM_CONTENTS = 10


def _fill_objstorage_and_kafka(kafka_server, kafka_prefix, objstorage):
    producer = Producer(
        {
            "bootstrap.servers": kafka_server,
            "client.id": "test-producer",
            "acks": "all",
        }
    )

    contents = {}
    for i in range(NUM_CONTENTS):
        content = b"\x00" * 19 + bytes([i])
        sha1 = objstorage.add(content)
        contents[sha1] = content
        producer.produce(
            topic=kafka_prefix + ".content",
            key=key_to_kafka(sha1),
            value=key_to_kafka({"sha1": sha1, "status": "visible",}),
        )

    producer.flush()

    return contents


@_patch_objstorages(["src", "dst"])
def test_replay_content(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
):
    """Check the content replayer in normal conditions"""

    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    result = invoke(
        "replay",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
    )

    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    for (sha1, content) in contents.items():
        assert sha1 in objstorages["dst"], sha1
        assert objstorages["dst"].get(sha1) == content


@_patch_objstorages(["src", "dst"])
def test_replay_content_structured_log(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
    caplog,
):
    """Check the logs produced by the content replayer in normal conditions"""

    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    caplog.set_level(logging.DEBUG, "swh.objstorage.replayer.replay")

    expected_obj_ids = set(hash_to_hex(sha1) for sha1 in contents)

    result = invoke(
        "replay",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
    )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    copied = set()
    for record in caplog.records:
        logtext = record.getMessage()
        if "stored" in logtext:
            copied.add(record.args["obj_id"])

    assert (
        copied == expected_obj_ids
    ), "Mismatched logging; see captured log output for details."


@_patch_objstorages(["src", "dst"])
def test_replay_content_static_group_id(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
    caplog,
):
    """Check the content replayer in normal conditions

    with KAFKA_GROUP_INSTANCE_ID set
    """

    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    # Setup log capture to fish the consumer settings out of the log messages
    caplog.set_level(logging.DEBUG, "swh.journal.client")

    result = invoke(
        "replay",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        env={"KAFKA_GROUP_INSTANCE_ID": "static-group-instance-id"},
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
    )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    consumer_settings = None
    for record in caplog.records:
        if "Consumer settings" in record.message:
            consumer_settings = record.args
            break

    assert consumer_settings is not None, (
        "Failed to get consumer settings out of the consumer log. "
        "See log capture for details."
    )
    assert consumer_settings["group.instance.id"] == "static-group-instance-id"
    assert consumer_settings["session.timeout.ms"] == 60 * 10 * 1000
    assert consumer_settings["max.poll.interval.ms"] == 90 * 10 * 1000

    for (sha1, content) in contents.items():
        assert sha1 in objstorages["dst"], sha1
        assert objstorages["dst"].get(sha1) == content


@_patch_objstorages(["src", "dst"])
def test_replay_content_exclude(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
):
    """Check the content replayer in normal conditions

    with a exclusion file (--exclude-sha1-file)
    """

    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    excluded_contents = list(contents)[0::2]  # picking half of them
    with tempfile.NamedTemporaryFile(mode="w+b") as fd:
        fd.write(b"".join(sorted(excluded_contents)))

        fd.seek(0)

        result = invoke(
            "replay",
            "--stop-after-objects",
            str(NUM_CONTENTS),
            "--exclude-sha1-file",
            fd.name,
            journal_client={
                "cls": "kafka",
                "brokers": kafka_server,
                "group_id": kafka_consumer_group,
                "prefix": kafka_prefix,
            },
        )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    for (sha1, content) in contents.items():
        if sha1 in excluded_contents:
            assert sha1 not in objstorages["dst"], sha1
        else:
            assert sha1 in objstorages["dst"], sha1
            assert objstorages["dst"].get(sha1) == content


NUM_CONTENTS_DST = 5


@_patch_objstorages(["src", "dst"])
@pytest.mark.parametrize(
    "check_dst,expected_copied,expected_in_dst",
    [
        (True, NUM_CONTENTS - NUM_CONTENTS_DST, NUM_CONTENTS_DST),
        (False, NUM_CONTENTS, 0),
    ],
)
def test_replay_content_check_dst(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
    check_dst: bool,
    expected_copied: int,
    expected_in_dst: int,
    caplog,
):
    """Check the content replayer in normal conditions

    with some objects already in the dst objstorage.

    When check_dst is True, expect those not to be neither retrieved from the
    src objstorage nor pushed in the dst objstorage.
    """

    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    # add some objects in the dst objstorage
    for i, (sha1, content) in enumerate(contents.items()):
        if i >= NUM_CONTENTS_DST:
            break
        objstorages["dst"].add(content, obj_id=sha1)

    caplog.set_level(logging.DEBUG, "swh.objstorage.replayer.replay")

    result = invoke(
        "replay",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        "--check-dst" if check_dst else "--no-check-dst",
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
    )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    retrieved = 0
    stored = 0
    in_dst = 0
    for record in caplog.records:
        logtext = record.getMessage()
        if "retrieved" in logtext:
            retrieved += 1
        elif "stored" in logtext:
            stored += 1
        elif "in dst" in logtext:
            in_dst += 1

    assert (
        retrieved == expected_copied
        and stored == expected_copied
        and in_dst == expected_in_dst
    ), "Unexpected amount of objects copied, see the captured log for details"

    for (sha1, content) in contents.items():
        assert sha1 in objstorages["dst"], sha1
        assert objstorages["dst"].get(sha1) == content


class FlakyObjStorage(InMemoryObjStorage):
    """Flaky objstorage

    Any 'get', 'add' or 'in' (i.e. '__contains__()') operation will fail
    according to configured 'failures'.

    'failures' is expected to be a dict which keys are couples (operation,
    obj_id) and values are the number of time the operation 'operation' is
    expected to fail for object 'obj_id' before being performed successfully.

    An optional state ('state') can be also given as argument (see
    InMemoryObjStorage).

    """

    def __init__(self, *args, **kwargs):
        state = kwargs.pop("state")
        self.failures_left = Counter(kwargs.pop("failures"))
        super().__init__(*args, **kwargs)
        if state:
            self.state = state

    def flaky_operation(self, op, obj_id):
        if self.failures_left[op, obj_id] > 0:
            self.failures_left[op, obj_id] -= 1
            raise RuntimeError("Failed %s on %s" % (op, hash_to_hex(obj_id)))

    def get(self, obj_id):
        self.flaky_operation("get", obj_id)
        return super().get(obj_id)

    def add(self, data, obj_id=None, check_presence=True):
        self.flaky_operation("add", obj_id)
        return super().add(data, obj_id=obj_id, check_presence=check_presence)

    def __contains__(self, obj_id):
        self.flaky_operation("in", obj_id)
        return super().__contains__(obj_id)


@_patch_objstorages(["src", "dst"])
def test_replay_content_check_dst_retry(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
    monkeypatch_retry_sleep,
    caplog,
    redis_proc,
    redisdb,
):
    """Check the content replayer with a flaky dst objstorage

    for 'in' operations.
    """
    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    # build a flaky dst objstorage in which the 'in' operation for the first
    # NUM_CONTENT_DST objects will fail once
    failures = {}
    for i, (sha1, content) in enumerate(contents.items()):
        if i >= NUM_CONTENTS_DST:
            break
        objstorages["dst"].add(content, obj_id=sha1)
        failures["in", sha1] = 1
    orig_dst = objstorages["dst"]
    objstorages["dst"] = FlakyObjStorage(state=orig_dst.state, failures=failures)

    caplog.set_level(logging.DEBUG, "swh.objstorage.replayer.replay")
    result = invoke(
        "replay",
        "--check-dst",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
        replayer={
            "error_reporter": {"host": redis_proc.host, "port": redis_proc.port},
        },
    )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    # check that exactly NUM_CONTENTS_DST 'in' operations have failed once
    failed_in = 0
    for record in caplog.records:
        logtext = record.getMessage()
        if "Retry operation obj_in_objstorage" in logtext:
            failed_in += 1
        elif "Retry operation" in logtext:
            assert False, "No other failure expected than 'in' operations"
    assert failed_in == NUM_CONTENTS_DST

    # check nothing has been reported in redis
    assert not redisdb.keys()

    # in the end, the replay process should be OK
    for (sha1, content) in contents.items():
        assert sha1 in objstorages["dst"], sha1
        assert objstorages["dst"].get(sha1) == content


@_patch_objstorages(["src", "dst"])
def test_replay_content_failed_copy_retry(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
    caplog,
    monkeypatch_retry_sleep,
    redis_proc,
    redisdb,
):
    """Check the content replayer with a flaky src and dst objstorages

    for 'get' and 'add' operations, and a few non-recoverable failures (some
    objects failed to be replayed).

    """
    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    add_failures = {}
    get_failures = {}
    definitely_failed = set()

    # We want to generate operations failing 1 to CONTENT_REPLAY_RETRIES times.
    # We generate failures for 2 different operations, get and add.
    num_retry_contents = 2 * CONTENT_REPLAY_RETRIES

    assert (
        num_retry_contents < NUM_CONTENTS
    ), "Need to generate more test contents to properly test retry behavior"

    for i, sha1 in enumerate(contents):
        if i >= num_retry_contents:
            break

        # This generates a number of failures, up to CONTENT_REPLAY_RETRIES
        num_failures = (i % CONTENT_REPLAY_RETRIES) + 1

        # This generates failures of add for the first CONTENT_REPLAY_RETRIES
        # objects, then failures of get.
        if i < CONTENT_REPLAY_RETRIES:
            add_failures["add", sha1] = num_failures
        else:
            get_failures["get", sha1] = num_failures

        # Only contents that have CONTENT_REPLAY_RETRIES or more are
        # definitely failing
        if num_failures >= CONTENT_REPLAY_RETRIES:
            definitely_failed.add(hash_to_hex(sha1))

    assert add_failures
    assert get_failures
    assert definitely_failed
    objstorages["dst"] = FlakyObjStorage(
        state=objstorages["dst"].state, failures=add_failures,
    )
    objstorages["src"] = FlakyObjStorage(
        state=objstorages["src"].state, failures=get_failures,
    )

    caplog.set_level(logging.DEBUG, "swh.objstorage.replayer.replay")

    result = invoke(
        "replay",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
        replayer={
            "error_reporter": {"host": redis_proc.host, "port": redis_proc.port},
        },
    )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    # check the logs looks as expected
    copied = 0
    failed_put = set()
    failed_get = set()
    for record in caplog.records:
        logtext = record.getMessage()
        if "stored" in logtext:
            copied += 1
        elif "Failed operation" in logtext:
            assert record.levelno == logging.ERROR
            assert record.args["retries"] == CONTENT_REPLAY_RETRIES
            assert record.args["operation"] in ("get_object", "put_object")
            if record.args["operation"] == "get_object":
                failed_get.add(record.args["obj_id"])
            else:
                failed_put.add(record.args["obj_id"])
    assert (
        failed_put | failed_get == definitely_failed
    ), "Unexpected object copy failures; see captured log for details"

    # check failed objects are referenced in redis
    assert set(redisdb.keys()) == {
        f"blob:{objid}".encode() for objid in definitely_failed
    }
    # and have a consistent error report in redis
    for key in redisdb.keys():
        report = msgpack.loads(redisdb[key])
        assert report["operation"] in ("get_object", "put_object")
        if report["operation"] == "get_object":
            assert report["obj_id"] in failed_get
        else:
            assert report["obj_id"] in failed_put

    # check valid object are in the dst objstorage, but
    # failed objects are not.
    for (sha1, content) in contents.items():
        if hash_to_hex(sha1) in definitely_failed:
            assert sha1 not in objstorages["dst"]
            continue

        assert sha1 in objstorages["dst"], sha1
        assert objstorages["dst"].get(sha1) == content


@_patch_objstorages(["src", "dst"])
def test_replay_content_objnotfound(
    objstorages,
    kafka_prefix: str,
    kafka_consumer_group: str,
    kafka_server: Tuple[Popen, int],
    caplog,
):
    """Check the ContentNotFound is not considered a failure to retry"""

    contents = _fill_objstorage_and_kafka(
        kafka_server, kafka_prefix, objstorages["src"]
    )

    # delete a few objects from the src objstorage
    num_contents_deleted = 5
    contents_deleted = set()
    for i, sha1 in enumerate(contents):
        if i >= num_contents_deleted:
            break
        del objstorages["src"].state[sha1]
        contents_deleted.add(hash_to_hex(sha1))

    caplog.set_level(logging.DEBUG, "swh.objstorage.replayer.replay")

    result = invoke(
        "replay",
        "--stop-after-objects",
        str(NUM_CONTENTS),
        journal_client={
            "cls": "kafka",
            "brokers": kafka_server,
            "group_id": kafka_consumer_group,
            "prefix": kafka_prefix,
        },
    )
    expected = r"Done.\n"
    assert result.exit_code == 0, result.output
    assert re.fullmatch(expected, result.output, re.MULTILINE), result.output

    copied = 0
    not_in_src = set()
    for record in caplog.records:
        logtext = record.getMessage()
        if "stored" in logtext:
            copied += 1
        elif "object not found" in logtext:
            # Check that the object id can be recovered from logs
            assert record.levelno == logging.ERROR
            not_in_src.add(record.args["obj_id"])
        elif "Retry operation" in logtext:
            assert False, "Not found objects should not be retried"

    assert (
        copied == NUM_CONTENTS - num_contents_deleted
    ), "Unexpected number of contents copied"

    assert (
        not_in_src == contents_deleted
    ), "Mismatch between deleted contents and not_in_src logs"

    for (sha1, content) in contents.items():
        if sha1 not in objstorages["src"]:
            continue
        assert sha1 in objstorages["dst"], sha1
        assert objstorages["dst"].get(sha1) == content
