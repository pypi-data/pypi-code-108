# Copyright (c) Qotto, 2021

"""
Response record
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from eventy.record.errors import RecordAttributeTypeError, RecordAttributeValueError
from eventy.record.record import Record, RecordType

__all__ = [
    'Response',
]


class Response(Record):
    """
    Response implementation of the Record abstract base class
    """

    def __init__(
        self,
        protocol_version: str,
        namespace: str,
        name: str,
        version: str,
        source: str,
        destination: str,
        request_uuid: str,
        uuid: Optional[str] = None,
        ok: bool = True,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None,
        partition_key: Optional[str] = None,
        date: Optional[datetime] = None,
        context: Optional[Dict[str, Dict[str, Any]]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize Record attributes

        :param protocol_version: Version of the Eventy protocol in SemVer format
        :param namespace: Namespace of the record schema in URN format
        :param name: Name of the record schema
        :param version: Version of the record schema in SemVer format
        :param source: Emitter of the record in URN format
        :param destination: Destination of the response, should be source of corresponding request, in URN format
        :param request_uuid: UUID v4 of the corresponding request
        :param uuid: UUID v4 of the response. Default: auto-generated
        :param ok:
        :param error_code:
        :param error_message:
        :param correlation_id: Correlation ID, propagated. Default: auto-generated
        :param partition_key: Partition or database key. Default: None
        :param date: Date of the event. Default: now
        :param context: Context data dictionary, propagated. Default: None
        :param data: Domain data dictionary. Default: None

        :raises RecordAttributeError:
        """
        super().__init__(
            protocol_version,
            namespace,
            name,
            version,
            source,
            uuid,
            correlation_id,
            partition_key,
            date,
            context,
            data,
        )
        self.destination = destination
        self.request_uuid = request_uuid
        self.ok = ok
        self.error_code = error_code
        self.error_message = error_message

    @property
    def type(self):
        """
        Record type (RESPONSE)

        :return: Type.RESPONSE
        """
        return RecordType.RESPONSE

    @property
    def destination(self) -> str:
        return self._destination

    @destination.setter
    def destination(self, destination: str) -> None:
        if not destination.startswith('urn:'):
            raise RecordAttributeValueError('destination', destination, 'URN format should start with "urn:"')
        if '.' in destination:
            raise RecordAttributeValueError(
                'destination', destination, 'URN format should use ":" as separator and not "."'
                )
        self._destination = destination

    @property
    def request_uuid(self) -> str:
        return self._request_uuid

    @request_uuid.setter
    def request_uuid(self, request_uuid: str) -> None:
        try:
            UUID(request_uuid)
        except TypeError as e:
            raise RecordAttributeValueError('request_uuid', request_uuid, str(e)) from e
        except ValueError as e:
            raise RecordAttributeValueError('request_uuid', request_uuid, str(e)) from e
        self._request_uuid = request_uuid

    @property
    def ok(self) -> bool:
        return self._ok

    @ok.setter
    def ok(self, ok: bool) -> None:
        if not isinstance(ok, bool):
            raise RecordAttributeTypeError('ok', bool, ok)
        self._ok = ok

    @property
    def error_code(self) -> Optional[int]:
        return self._error_code

    @error_code.setter
    def error_code(self, error_code) -> None:
        # TODO: Check if ok is True? This would impose to update ok before error_code, but why not?
        if error_code is not None and not isinstance(error_code, int):
            raise RecordAttributeTypeError('error_code', 'int or None', error_code)
        self._error_code = error_code

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @error_message.setter
    def error_message(self, error_message) -> None:
        # TODO: Check if ok is True? This would impose to update ok before error_message, but why not?
        if error_message is not None and not isinstance(error_message, str):
            raise RecordAttributeTypeError('error_message', 'str or None', error_message)
        self._error_message = error_message
