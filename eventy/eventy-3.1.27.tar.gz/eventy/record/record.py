# Copyright (c) Qotto, 2021

"""
Record abstract base class
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from semver import VersionInfo

from eventy.record.errors import RecordAttributeTypeError, RecordAttributeValueError
from eventy.trace_id import correlation_id_var
from eventy.trace_id.generator import gen_trace_id

__all__ = [
    'Record',
    'RecordType',
]


class RecordType(Enum):
    @classmethod
    def list(cls):
        return [type.value for type in cls]

    EVENT = 'EVENT'
    REQUEST = 'REQUEST'
    RESPONSE = 'RESPONSE'


class Record:
    """
    Common Record interface

    This class is a base for Event, Request, and Response. It should not be instantiated.
    """

    def __init__(
        self,
        protocol_version: str,
        namespace: str,
        name: str,
        version: str,
        source: str,
        uuid: Optional[str] = None,
        correlation_id: Optional[str] = None,
        partition_key: Optional[str] = None,
        date: Optional[datetime] = None,
        context: Optional[Dict[str, Dict[str, Any]]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize Record attributes

        :param protocol_version: Version of the Eventy protocol in SemVer format
        :param namespace: Namespace of the record schema in URN format
        :param name: Name of the record schema
        :param version: Version of the record schema in SemVer format
        :param source: Emitter of the record in URN format
        :param uuid: UUID v4 of the record. Default: auto-generated
        :param correlation_id: Correlation ID, propagated. Default: auto-generated
        :param partition_key: Partition or database key. Default: None
        :param date: Date of the event. Default: now
        :param context: Context data dictionary, propagated. Default: None
        :param data: Domain data dictionary. Default: None

        :raises RecordAttributeError:
        """
        self.protocol_version = protocol_version
        self.namespace = namespace
        self.name = name
        self.version = version
        self.source = source
        if uuid is None:
            uuid = str(uuid4())
        self.uuid = uuid
        if correlation_id is None:
            correlation_id = correlation_id_var.get()
            if not correlation_id:
                correlation_id = gen_trace_id(self.name)
        self.correlation_id = correlation_id
        # partition_key can be None
        self.partition_key = partition_key
        if date is None:
            date = datetime.now(tz=timezone.utc)
        self.date = date
        if context is None:
            context = {}
        self.context = context
        if data is None:
            data = {}
        self.data = data

    @property
    def type(self) -> RecordType:
        """
        Type of the record: EVENT | REQUEST | RESPONSE
        """
        raise NotImplementedError

    @property
    def protocol_version(self) -> str:
        """
        Eventy protocol version (SemVer)
        """
        return self._protocol_version

    @protocol_version.setter
    def protocol_version(self, protocol_version: str) -> None:
        try:
            VersionInfo.parse(protocol_version)
        except ValueError:
            raise RecordAttributeValueError('protocol_version', protocol_version, 'Not in SemVer format')
        self._protocol_version = protocol_version

    @property
    def qualified_name(self) -> str:
        return f'{self.namespace}:{self.name}'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def namespace(self) -> str:
        return self._namespace

    @namespace.setter
    def namespace(self, namespace: str) -> None:
        if not namespace.startswith('urn:'):
            raise RecordAttributeValueError('namespace', namespace, 'URN format should start with "urn:"')
        self._namespace = namespace

    @property
    def version(self) -> str:
        """
        Record schema version (SemVer)
        """
        return self._version

    @version.setter
    def version(self, version: str) -> None:
        try:
            VersionInfo.parse(version)
        except ValueError:
            raise RecordAttributeValueError('version', version, 'Not in SemVer format')
        self._version = version

    @property
    def source(self) -> str:
        """
        Record source (URN)
        """
        return self._source

    @source.setter
    def source(self, source: str) -> None:
        if not source.startswith('urn:'):
            raise RecordAttributeValueError('source', source, 'URN format should start with "urn:"')
        self._source = source

    @property
    def uuid(self) -> str:
        """
        Record unique identifier (UUID v4)
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        try:
            UUID(uuid)
        except TypeError as e:
            raise RecordAttributeValueError('uuid', uuid, str(e)) from e
        except ValueError as e:
            raise RecordAttributeValueError('uuid', uuid, str(e)) from e
        self._uuid = uuid

    @property
    def correlation_id(self) -> str:
        """
        Record correlation_id to be propagated
        """
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, correlation_id: str) -> None:
        if isinstance(correlation_id, str):
            self._correlation_id = correlation_id
        else:
            raise RecordAttributeTypeError('correlation_id', str, correlation_id)

    @property
    def partition_key(self) -> Optional[str]:
        """
        Key for partitioned states, e.g. Kafka topics partitions
        """
        return self._partition_key

    @partition_key.setter
    def partition_key(self, partition_key: Optional[str]):
        if partition_key is None or isinstance(partition_key, str):
            self._partition_key = partition_key
        else:
            raise RecordAttributeTypeError('partition_key', str, partition_key)

    @property
    def date(self) -> datetime:
        """
        Date of the event (unrelated to event production)
        """
        return self._date

    @date.setter
    def date(self, date: datetime) -> None:
        """
        Set the date, keeping a millisecond precision.

        :param date: record date, as a datetime, or iso str, or timestamp int
        """
        if isinstance(date, datetime):
            ts = int(date.timestamp() * 1000) / 1000
            date = datetime.fromtimestamp(ts, timezone.utc)
            self._date = date
        else:
            raise RecordAttributeTypeError('date', datetime, date)

    @property
    def context(self) -> Dict[str, Dict[str, Any]]:
        """
        Execution context to be propagated
        """
        return self._context

    @context.setter
    def context(self, context: Dict[str, Dict[str, Any]]) -> None:
        if not isinstance(context, Dict):
            raise RecordAttributeTypeError('context', Dict, context)
        for key, val in context.items():
            if not isinstance(key, str):
                raise RecordAttributeTypeError(f'context key', str, key)
            if not isinstance(val, Dict):
                raise RecordAttributeTypeError(f'value for key {key}', 'Dict', val)
        self._context = context

    @property
    def data(self) -> Dict[str, Any]:
        """
        Actual record payload
        """
        return self._data

    @data.setter
    def data(self, data) -> None:
        if not isinstance(data, Dict):
            raise RecordAttributeTypeError('data', Dict, data)
        for key in data:
            if not isinstance(key, str):
                raise RecordAttributeTypeError('data key', 'str', key)
        self._data = data

    def __str__(self) -> str:
        return f"{self.qualified_name} ({self.type.value}) v{self.version} [CID:{self.correlation_id}] #{self.uuid} ${self.partition_key}"

    def _debug_str(self) -> str:
        """
        With data and context content. For debug purposes.
        """
        return self.__str__() + f"\n      CONTEXT={self.context}\n      DATA={self.data}"
