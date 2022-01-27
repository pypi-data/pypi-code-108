# Copyright (c) Qotto, 2021

from __future__ import annotations

from datetime import datetime
from time import sleep
from typing import Iterable, Optional, Union

from eventy.messaging.errors import MessagingError
from eventy.messaging.store import RecordStore, Cursor
from eventy.record import Record

__all__ = [
    'MemoryStore',
]

from eventy.serialization import RecordSerializer
from eventy.serialization.dummy import DummySerializer


class _ReadTopic:
    """
    Topic that can be read from.

    Records are: [0..acked_offset..read_offset..len(records)]
    - 0..acked_offset: messages that have been acknowledged
    - acked_offset..read_offset: messages that have been read
    - read_offset..len(records): messages that have not been read yet
    """

    def __init__(
        self,
        topic: str,
        record_serializer: RecordSerializer,
    ) -> None:
        self.serializer = record_serializer
        self.topic = topic
        self.encoded_records: list[bytes] = []
        self.read_offset = 0
        self.acked_offset = 0

    def add(
        self,
        records: Union[Record, Iterable[Record]],
    ) -> None:
        if not isinstance(records, Iterable):
            records = [records]
        self.encoded_records.extend(map(self.serializer.encode, records))

    def read(
        self,
        max_count: int = 1,
    ) -> list[Record]:
        read_records_encoded = self.encoded_records[self.read_offset:self.read_offset + max_count]
        read_records = list(map(self.serializer.decode, read_records_encoded))
        self.read_offset += len(read_records)
        return read_records

    def ack(self, count: int = None) -> None:
        if count is None:
            self.acked_offset = self.read_offset
        else:
            if (self.acked_offset + count) > self.read_offset:
                raise MessagingError('Cannot ack more than read.')
            self.acked_offset += count

    def get_acked(self, pop: bool = False) -> list[bytes]:
        acked = self.encoded_records[:self.acked_offset]
        if pop:
            self.encoded_records = self.encoded_records[self.acked_offset:]
            self.read_offset -= len(acked)
            self.acked_offset -= len(acked)
        return list(acked)

    def get_read_unacked(self, pop: bool = False) -> list[bytes]:
        read_unacked = self.encoded_records[self.acked_offset:self.read_offset]
        if pop:
            self.encoded_records = list(
                self.encoded_records[0:self.acked_offset]
                + self.encoded_records[self.acked_offset:self.read_offset]
            )
            self.read_offset -= len(read_unacked)
        return list(read_unacked)

    def get_unread(self, pop: bool = False) -> list[bytes]:
        unread = self.encoded_records[self.read_offset:]
        if pop:
            self.encoded_records = self.encoded_records[0:self.read_offset]
        return list(unread)

    def remove_acked_records(self):
        self.encoded_records = self.encoded_records[self.acked_offset:]
        self.read_offset -= self.acked_offset
        self.acked_offset = 0

    def reset_to_acked(self):
        self.read_offset = self.acked_offset

    def clear(self) -> None:
        self.encoded_records = []
        self.read_offset = 0
        self.acked_offset = 0


class _WriteTopic:
    """
    Topic that can be written to.

    - records 0..committed_offset are committed.
    - records committed_offset..len(records) are not committed.
    """

    def __init__(
        self,
        topic: str,
        record_serializer: RecordSerializer,
    ) -> None:
        self.serializer = record_serializer
        self.topic = topic
        self.encoded_records: list[bytes] = []
        self.committed_offset = 0

    def write_committed(
        self,
        record: Record,
    ) -> None:
        self.encoded_records.insert(self.committed_offset, self.serializer.encode(record))
        self.committed_offset += 1

    def write_uncommitted(
        self,
        record: Record,
    ) -> None:
        self.encoded_records.append(self.serializer.encode(record))

    def commit(self, count: int = None) -> None:
        if count is None:
            self.committed_offset = len(self.encoded_records)
        else:
            if (self.committed_offset + count) > len(self.encoded_records):
                raise MessagingError("Cannot commit more than written.")
            self.committed_offset += count

    def get_committed(self, pop: bool = False) -> list[bytes]:
        committed = self.encoded_records[:self.committed_offset]
        if pop:
            self.encoded_records = self.encoded_records[self.committed_offset:]
            self.committed_offset -= len(committed)
        return list(committed)

    def get_uncommitted(self, pop: bool = False) -> list[bytes]:
        uncommitted = self.encoded_records[self.committed_offset:]
        if pop:
            self.encoded_records = self.encoded_records[0:self.committed_offset]
        return list(uncommitted)

    def reset_to_committed(self) -> None:
        self.encoded_records = self.encoded_records[:self.committed_offset]

    def remove_committed_records(self):
        self.encoded_records = self.encoded_records[self.committed_offset:]
        self.committed_offset = 0

    def clear(self) -> None:
        self.encoded_records = []
        self.committed_offset = 0


class _Transaction:
    def __init__(self):
        self.reads: dict[str, int] = {}
        self.writes: dict[str, int] = {}

    def add_read(self, topic: str, count: int = 1) -> None:
        if topic not in self.reads:
            self.reads[topic] = 0
        self.reads[topic] += count

    def add_write(self, topic: str, count: int = 1) -> None:
        if topic not in self.writes:
            self.writes[topic] = 0
        self.writes[topic] += count


class MemoryStore(RecordStore):
    """
    In-memory record store, essentially for testing and debug purposes
    """

    def __init__(
        self,
        record_serializer: RecordSerializer = None,
    ) -> None:
        """
        Initialize an empty store.

        :param record_serializer: Serializer to use for encoding and decoding records.
        """
        super().__init__()

        self.record_serializer = record_serializer or DummySerializer()
        self.read_topics: dict[str, _ReadTopic] = {}
        self.write_topics: dict[str, _WriteTopic] = {}
        self.transaction: Optional[_Transaction] = None

    def register_topic(self, topic: str, cursor: Cursor = Cursor.ACKNOWLEDGED) -> None:
        if cursor != Cursor.ACKNOWLEDGED:
            raise MessagingError(f"Only ACKNOWLEDGED cursors are supported.")
        super().register_topic(topic, cursor)
        self.read_topics[topic] = _ReadTopic(topic, record_serializer=self.record_serializer)

    def read(
        self,
        max_count: int = 1,
        timeout_ms: Optional[int] = None,
        auto_ack: bool = False
    ) -> list[Record]:
        if auto_ack:
            raise MessagingError(f"Auto-ack is not supported.")
        records: list[Record] = []
        for topic, topic_read in self.read_topics.items():
            reads = topic_read.read(max_count - len(records))
            records.extend(reads)
        return records

    def ack(self, timeout_ms=None) -> None:
        for topic, topic_read in self.read_topics.items():
            if self.transaction:
                self.transaction.add_read(topic, topic_read.read_offset - topic_read.acked_offset)
            else:
                topic_read.ack()

    def write(self, record: Record, topic: str, timeout_ms=None) -> None:
        if topic not in self.write_topics:
            self.write_topics[topic] = _WriteTopic(topic, record_serializer=self.record_serializer)
        write_topic = self.write_topics[topic]
        if self.transaction:
            self.transaction.add_write(topic)
            write_topic.write_uncommitted(record)
        else:
            write_topic.write_committed(record)

    def write_now(self, record: Record, topic: str, timeout_ms=None) -> None:
        if topic not in self.write_topics:
            self.write_topics[topic] = _WriteTopic(topic, record_serializer=self.record_serializer)
        write_topic = self.write_topics[topic]
        write_topic.write_committed(record)

    def start_transaction(self) -> None:
        if self.transaction:
            raise MessagingError(f"Already in a transaction.")
        self.transaction = _Transaction()

    def commit(self, timeout_ms: Optional[int] = None) -> None:
        if not self.transaction:
            raise MessagingError(f"Not in a transaction.")
        for topic, read_count in self.transaction.reads.items():
            self.read_topics[topic].ack(read_count)
        for topic, write_count in self.transaction.writes.items():
            self.write_topics[topic].commit(write_count)
        self.transaction = None

    def abort(self, timeout_ms: Optional[int] = None) -> None:
        if not self.transaction:
            raise MessagingError(f"Not in a transaction.")
        for topic, read_count in self.transaction.reads.items():
            self.read_topics[topic].reset_to_acked()
        for topic, write_count in self.transaction.writes.items():
            self.write_topics[topic].reset_to_committed()
        self.transaction = None

    def add_record(self, records: Union[Record, Iterable[Record]], topic: str) -> None:
        """
        Add one or multiple records to be read.

        :param records: record(s) to be added
        :param topic: topic the record(s) should be added to
        """
        if topic not in self.read_topics:
            raise MessagingError(f"Topic {topic} not registered.")
        self.read_topics[topic].add(records)

    def get_encoded(
        self,
        # options
        topic: str = None,
        pop: bool = False,
        # written
        committed: bool = False,
        uncommitted: bool = False,
        # read or available
        acked: bool = False,
        unacked: bool = False,
        unread: bool = False,
    ) -> list[bytes]:
        records: list = self.get(
            decode=False,
            topic=topic,
            pop=pop,
            committed=committed,
            uncommitted=uncommitted,
            acked=acked,
            unacked=unacked,
            unread=unread,
        )
        return records

    def get_records(
        self,
        # options
        topic: str = None,
        pop: bool = False,
        # written
        committed: bool = False,
        uncommitted: bool = False,
        # read or available
        acked: bool = False,
        unacked: bool = False,
        unread: bool = False,
    ) -> list[Record]:
        records: list = self.get(
            decode=True,
            topic=topic,
            pop=pop,
            committed=committed,
            uncommitted=uncommitted,
            acked=acked,
            unacked=unacked,
            unread=unread,
        )
        return records

    def get(
        self,
        # options
        topic: str = None,
        decode: bool = True,
        pop: bool = False,
        # written
        committed: bool = False,
        uncommitted: bool = False,
        # read or available
        acked: bool = False,
        unacked: bool = False,
        unread: bool = False,
    ) -> Union[list[Record], list[bytes]]:
        """
        Get one or multiple records from the store or a specific topic.

        :param topic: Topic, default: all topics
        :param decode: Decode (deserialize) the record(s)
        :param pop: Remove the record(s) from the store
        :param committed: Get the committed written records
        :param uncommitted: Get the uncommitted written records
        :param acked: Get the acknowledged read records
        :param unacked: Get the unacknowledged read records
        :param unread: Get the unread available records
        :return: A list of records or a list of encoded records
        """
        if topic:
            topics = [topic]
        else:
            topics = list(self.write_topics.keys()) + list(self.read_topics.keys())
        records: list = []

        for topic in topics:
            read_topic = self.read_topics.get(topic)
            if read_topic:
                if acked:
                    records.extend(read_topic.get_acked(pop=pop))
                if unacked:
                    records.extend(read_topic.get_read_unacked(pop=pop))
                if unread:
                    records.extend(read_topic.get_unread(pop=pop))
            write_topic = self.write_topics.get(topic)
            if write_topic:
                if committed:
                    records.extend(write_topic.get_committed(pop=pop))
                if uncommitted:
                    records.extend(write_topic.get_uncommitted(pop=pop))

        if decode:
            return list(map(self.record_serializer.decode, records))
        else:
            return list(records)

    def get_committed_records(self, topic: str = None, pop: bool = False) -> list[Record]:
        return self.get_records(topic=topic, pop=pop, committed=True)

    def get_all_written_records(self, topic: str = None, pop: bool = False) -> list[Record]:
        return self.get_records(topic=topic, pop=pop, committed=True, uncommitted=True)

    def get_acked_records(self, topic: str = None, pop: bool = False) -> list[Record]:
        return self.get_records(topic=topic, pop=pop, acked=True)

    def get_all_read_records(self, topic: str = None, pop: bool = False) -> list[Record]:
        return self.get_records(topic=topic, pop=pop, acked=True, unacked=True)

    def get_non_acked_records(self, topic: str = None, pop: bool = False) -> list[Record]:
        return self.get_records(topic=topic, pop=pop, unread=True, unacked=True)

    def wait_all_acked(self, timeout_ms: int = None) -> bool:
        """
        Wait until all records are acked.

        :param timeout_ms: Timeout in milliseconds
        :return: True if all records are acked, False if timeout
        """

        begin_time = datetime.now().timestamp()
        while self.get_non_acked_records():
            if timeout_ms and datetime.now().timestamp() > begin_time + timeout_ms / 1000.0:
                return False
            sleep(0.1)
        return True

    def clear(self) -> None:
        """
        Completely clear the store (remove all data).
        """
        for write_topic in self.write_topics.values():
            write_topic.clear()
        for read_topic in self.read_topics.values():
            read_topic.clear()
        self.transaction = None

    def reset(self) -> None:
        """
        Reset the store to the last committed state.
        """
        for write_topic in self.write_topics.values():
            write_topic.reset_to_committed()
        for read_topic in self.read_topics.values():
            read_topic.reset_to_acked()
        self.transaction = None

    def debug_topics(self, topic: str = None) -> str:
        result = ""
        if topic:
            topics = [topic]
        else:
            topics = list(self.read_topics.keys()) + list(self.write_topics.keys())
        max_len = max(map(len, topics))
        for topic in topics:
            if topic in self.write_topics:
                result += "READ  " + topic + (' ' * (max_len - len(topic))) + ": "
                result += ("X" * len(self.get(topic, acked=True)))
                result += ("0" * len(self.get(topic, unacked=True)))
                result += ("-" * len(self.get(topic, unread=True)))
                result += "\n"
            if topic in self.read_topics:
                result += "WRITE " + topic + (' ' * (max_len - len(topic))) + ": "
                result += ("X" * len(self.get(topic, committed=True)))
                result += ("O" * len(self.get(topic, uncommitted=True)))
                result += "\n"
        return result
