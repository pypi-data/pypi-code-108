# Copyright (c) Qotto, 2021

from __future__ import annotations

from typing import Optional

__all__ = [
    'Service',
]

from eventy.record import RecordType


class Service:
    def __init__(
        self,
        name: str,
        namespace: Optional[str] = None,
        event_topic: Optional[str] = None,
        request_topic: Optional[str] = None,
        response_topic: Optional[str] = None,
    ):
        """
        Initialize a service

        :param name: Name of the service
        :param namespace: Namespace URN of the service. Default: 'urn:<name>'
        :param event_topic: EVENT topic. Default: '<name>-events'
        :param request_topic: REQUEST topic. Default: '<name>-requests'
        :param response_topic: RESPONSE topic. Default: '<name>-responses'
        """
        self._name = name

        if namespace is None:
            namespace = f'urn:{name}'
        self._namespace = namespace

        if event_topic is None:
            event_topic = f'{name}-events'
        self._event_topic = event_topic

        if request_topic is None:
            request_topic = f'{name}-requests'
        self._request_topic = request_topic

        if response_topic is None:
            response_topic = f'{name}-responses'
        self._response_topic = response_topic

    @property
    def event_topic(self) -> str:
        return self._event_topic

    @property
    def request_topic(self) -> str:
        return self._request_topic

    @property
    def response_topic(self) -> str:
        return self._response_topic

    def topic_for(self, record_type: RecordType) -> str:
        if record_type == RecordType.EVENT:
            return self.event_topic
        elif record_type == RecordType.REQUEST:
            return self.request_topic
        elif record_type == RecordType.RESPONSE:
            return self.response_topic
        raise ValueError(f"No topic for record type {record_type}.")

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def name(self) -> str:
        return self._name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return (
            other is not None
            and isinstance(other, Service)
            and self.name == other.name
            and self.namespace == other.namespace
            and self.request_topic == other.request_topic
            and self.response_topic == other.response_topic
            and self.event_topic == other.event_topic
        )

    def __str__(self) -> str:
        return f'<Service {self.name} ({self.namespace})>'
