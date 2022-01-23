import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Union
from datalogue.errors import DtlError
from datalogue.dtl_utils import _parse_string_list


class ShardIterator(ABC):
    """
    Abstract class containing the five subclasses:
      TrimHorizon, for beginning at the beginning of the stream
      Latest, for beginning at the most recent record
      AtTimestamp, for beginning at a specified time
      AtSequenceNumber, for beginning at a specified sequence number
      AfterSequenceNumber, for beginning just after a specified sequence number
    """

    type_field = "type"

    type_str = ""

    def __init__(self, type: str):
        self.type = type
        super().__init__()

    def _base_payload(self) -> dict:
        base = [(ShardIterator.type_field, self.type_str)]
        return dict(base)

    @abstractmethod
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        pass

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "ShardIterator"]:
        type_field = d.get(ShardIterator.type_field)
        if not isinstance(type_field, str):
            return DtlError("The type is missing from JSON")
        elif type_field == TrimHorizon.type_str:
            return TrimHorizon()
        elif type_field == Latest.type_str:
            return Latest()
        elif type_field == AtSequenceNumber.type_str:
            return AtSequenceNumber._from_payload(d)
        elif type_field == AfterSequenceNumber.type_str:
            return AfterSequenceNumber._from_payload(d)
        elif type_field == AtTimestamp.type_str:
            return AtTimestamp._from_payload(d)
        else:
            return DtlError("The object %s is not a ShardIterator definition" % str(d))


class TrimHorizon(ShardIterator):
    """
      Begins reading stream from the beginning
    """

    type_str = "TrimHorizon"

    def __init__(self):
        super().__init__(TrimHorizon.type_str)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        return base


class Latest(ShardIterator):
    """
      Begins reading stream from the beginning
    """

    type_str = "Latest"

    def __init__(self):
        super().__init__(Latest.type_str)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        return base


class AtSequenceNumber(ShardIterator):
    """
      Begins reading stream starting from element of specified sequence number
    """

    type_str = "AtSequenceNumber"

    def __init__(self, sequence_number: str):
        self.sequence_number = sequence_number
        super().__init__(AtSequenceNumber.type_str)

    def __repr__(self):
        return f"{self.__class__.__name__}(sequence_number= {self.sequence_number})"

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["sequenceNumber"] = self.sequence_number
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "AtSequenceNumber"]:
        sequence_number = d.get("sequenceNumber")
        if sequence_number is None:
            return DtlError("The `sequenceNumber` is missing from JSON")
        return AtSequenceNumber(sequence_number)


class AfterSequenceNumber(ShardIterator):
    """
      Begins reading stream starting immediately after element of specified sequence number
    """

    type_str = "AfterSequenceNumber"

    def __init__(self, sequence_number: str):
        self.sequence_number = sequence_number
        super().__init__(AfterSequenceNumber.type_str)

    def __repr__(self):
        return f"{self.__class__.__name__}(sequence_number= {self.sequence_number})"

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["sequenceNumber"] = self.sequence_number
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "AfterSequenceNumber"]:
        sequence_number = d.get("sequenceNumber")
        if sequence_number is None:
            return DtlError("The `sequenceNumber` is missing from JSON")
        return AfterSequenceNumber(sequence_number)


class AtTimestamp(ShardIterator):
    """
      Begins reading stream from specified timestamp
    """

    type_str = "AtTimestamp"

    def __init__(self, timestamp: int):
        self.timestamp = timestamp
        super().__init__(AtTimestamp.type_str)

    def __repr__(self):
        return f"{self.__class__.__name__}(timestamp= {self.timestamp})"

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["timestamp"] = self.timestamp
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "AtTimestamp"]:
        timestamp = d.get("timestamp")
        if timestamp is None:
            return DtlError("The `timestamp` is missing from JSON")
        timestamp = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        if not isinstance(timestamp, datetime.datetime):
            return DtlError("The `timestamp` parsed from JSON is not a datetime format.")

        return AtTimestamp(timestamp)


class ShardAttributes(object):
    """
    Configures the shard attributes for the streaming source
    :param partition_keys can be used to specify to read from a specific partition key or partition keys. If unspecified, reads from all partition keys (consequently, all shards) of the stream
    :param shard_iterator: iterator type used for this source, as a subclass of ShardIterator
    :param refresh_interval: time between requests for data loads, in milliseconds
    :param limit: maximum number of transactions ingested from stream per second (for Kinesis, max supported is 5 and each transaction can contain 10k records)
    """

    def __init__(
        self, shard_iterators: Dict[str, ShardIterator] = {}, refresh_interval: float = 1, limit: int = 5,
    ):
        self.shard_iterators = shard_iterators
        self.refresh_interval = refresh_interval
        self.limit = limit

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(shard_iterators= {self.shard_iterators}, "
            f"refresh_interval= {self.refresh_interval}, limit= {self.limit})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        json = {}
        json["shardIterators"] = {
            shard_id: ShardIterator._as_payload(shard_iter) for shard_id, shard_iter in self.shard_iterators.items()
        }
        json["refreshInterval"] = self.refresh_interval
        json["limit"] = self.limit
        return json

    @staticmethod
    def _from_payload(shard_attributes: dict) -> Union[DtlError, "ShardAttributes"]:
        shard_iterators = {
            shard_id: ShardIterator._from_payload(shard_iter)
            for shard_id, shard_iter in shard_attributes.get("shardIterators", {}).items()
        }
        refresh_interval = shard_attributes["refreshInterval"]
        limit = shard_attributes["limit"]
        return ShardAttributes(shard_iterators, refresh_interval, limit)
