from databricks_registry_webhooks.entities.job_spec import JobSpec
from databricks_registry_webhooks.entities.http_url_spec import HttpUrlSpec
from databricks_registry_webhooks.entities.registry_webhook_event import RegistryWebhookEvent
from databricks_registry_webhooks.entities.registry_webhook_status import RegistryWebhookStatus
from databricks_registry_webhooks.entities._webhooks_base_object import _WebhooksBaseObject
from databricks_registry_webhooks.exceptions import RegistryWebhooksException
from databricks_registry_webhooks.protos.webhooks_pb2 import (
    RegistryWebhook as ProtoRegistryWebhook,
    HttpUrlSpec as ProtoHttpUrlSpec,
    JobSpec as ProtoJobSpec,
)
from databricks_registry_webhooks.protos.databricks_pb2 import INVALID_PARAMETER_VALUE


class RegistryWebhook(_WebhooksBaseObject):
    """
    A Model Registry Webhook.
    """

    def __init__(
        self,
        id,
        events,
        creation_timestamp,
        last_updated_timestamp,
        status,
        http_url_spec=None,
        job_spec=None,
        model_name=None,
        description=None,
    ):
        """
        :param id: The ID of the Registry Webhook.
        :param events: A list of Model Registry events that trigger the Registry Webhook. For all
                       supported events, see
                       :py:class:`databricks_registry_webhooks.RegistryWebhookEvent.all_events()`.
        :param creation_timestamp: The time at which the Registry Webhook was created. 
        :param last_updated_timestamp: The time at which the Registry Webhook was most
                                       recently updated.
        :param status: The status of the Registry Webhook. For all supported statuses, see
                       :py:class:`databricks_registry_webhooks.RegistryWebhookStatus.all_statuses()`.
        :param http_url_spec: Attributes (e.g. URL) of an HTTPS request for the Registry Webhook to
                              send when one of the associated `events` occurs. Exactly one of
                              `http_url_spec` or `job_spec` must be specified.
        :param job_spec: Attributes of a Databricks Job (e.g. Job ID) for the Registry Webhook to
                         run when one of the associated `events` occurs. Exactly one of
                         `http_url_spec` or `job_spec` must be specified.
        :param model_name: Name of the Registered Model whose events trigger the Registry Webhook.
                           If `None`, the Registry Webhook is "registry-wide" and is triggered
                           for events occurring on any accessible model throughout the entire
                           Model Registry.
        :param description: A string description of the Registry Webhook.
        """
        if not events:
            raise RegistryWebhooksException(
                "One or more events must be specified",
                error_code=INVALID_PARAMETER_VALUE,
            )
        if not all([RegistryWebhookEvent.is_valid(event) for event in events]):
            raise RegistryWebhooksException(
                (f"One or more invalid events specified: {events}. Valid events:"
                 f" {RegistryWebhookEvent.all_events()}"),
                error_code=INVALID_PARAMETER_VALUE,
            )
        if not RegistryWebhookStatus.is_valid(status):
            raise RegistryWebhooksException(
                f"Invalid webhook status: {status}. Valid statuses:"
                f" {RegistryWebhookStatus.all_statuses()}",
                error_code=INVALID_PARAMETER_VALUE,
            )
        if (http_url_spec is None and job_spec is None) or\
                (http_url_spec is not None and job_spec is not None):
            raise RegistryWebhooksException(
                "Exactly one of http_url_spec or job_spec must be specified",
                error_code=INVALID_PARAMETER_VALUE,
            )
        if http_url_spec is not None and not isinstance(http_url_spec, HttpUrlSpec):
            raise RegistryWebhooksException(
                f"Invalid http_url_spec: {http_url_spec}",
                error_code=INVALID_PARAMETER_VALUE,
            )
        if job_spec is not None and not isinstance(job_spec, JobSpec):
            raise RegistryWebhooksException(
                f"Invalid job_spec: {job_spec}",
                error_code=INVALID_PARAMETER_VALUE,
            )

        self._id = id
        self._events = events
        self._creation_timestamp = creation_timestamp
        self._last_updated_timestamp = last_updated_timestamp
        self._description = description
        self._status = status
        self._http_url_spec = http_url_spec
        self._job_spec = job_spec
        self._model_name = model_name

    @property
    def id(self):
        """
        The ID of the Registry Webhook.
        """
        return self._id

    @property
    def events(self):
        """
        A list of Model Registry events that trigger the Registry Webhook. For all supported events,
        see :py:class:`databricks_registry_webhooks.RegistryWebhookEvent.all_events()`.
        """
        return self._events

    @property
    def creation_timestamp(self):
        """
        The time at which the Registry Webhook was created. 
        """
        return self._creation_timestamp

    @property
    def last_updated_timestamp(self):
        """
        The time at which the Registry Webhook was most recently updated.
        """
        return self._last_updated_timestamp

    @property
    def description(self):
        """
        A string description of the Registry Webhook.
        """
        return self._description

    @property
    def status(self):
        """
        The status of the Registry Webhook. For all supported statuses, see
        :py:class:`databricks_registry_webhooks.RegistryWebhookStatus.all_statuses()`.
        """
        return self._status

    @property
    def http_url_spec(self):
        """
        Attributes (e.g. URL) of an HTTPS request for the Registry Webhook to send when one of the
        associated events occurs.
        """
        return self._http_url_spec

    @property
    def job_spec(self):
        """
        Attributes of a Databricks Job (e.g. Job ID) for the Registry Webhook to run when one of
        the associated events occurs. 
        """
        return self._job_spec

    @property
    def model_name(self):
        """
        Name of the Registered Model whose events trigger the Registry Webhook. If `None`, the
        Registry Webhook is "registry-wide" and is triggered for events occurring on any accessible
        model throughout the entire Model Registry.
        """
        return self._model_name

    def to_proto(self):
        proto = ProtoRegistryWebhook()
        proto.id = self.id
        proto.events.extend([RegistryWebhookEvent.from_string(event) for event in self.events])
        proto.creation_timestamp = self.creation_timestamp
        proto.last_updated_timestamp = self.last_updated_timestamp
        proto.description = self.description
        proto.status = RegistryWebhookStatus.from_string(self.status)
        if self.http_url_spec is not None:
            proto.http_url_spec.MergeFrom(self.http_url_spec.to_proto())
        if self.job_spec is not None:
            proto.job_spec.MergeFrom(self.job_spec.to_proto())
        if self.model_name is not None:
            proto.model_name = self.model_name
        return proto

    @classmethod
    def from_proto(cls, proto):
        http_url_spec = proto.http_url_spec
        # If the http url spec corresponds to the default proto http url spec,
        # this means that the field was not set on the proto (i.e. is empty)
        # and should be represented as `None`
        if http_url_spec == ProtoHttpUrlSpec():
            http_url_spec = None
        else:
            http_url_spec = HttpUrlSpec.from_proto(http_url_spec)

        job_spec = proto.job_spec
        # If the http url spec corresponds to the default proto http url spec,
        # this means that the field was not set on the proto (i.e. is empty)
        # and should be represented as `None`
        if job_spec == ProtoJobSpec():
            job_spec = None
        else:
            job_spec = JobSpec.from_proto(job_spec)

        model_name = proto.model_name
        # If the model name is a falsy string, this means that the field was not
        # set on the proto (i.e. is empty) and should be represented as `None`
        if not model_name:
            model_name = None

        description = proto.description
        # If the description is a falsy string, this means that the field was not
        # set on the proto (i.e. is empty) and should be represented as `None`
        if not description:
            description = None

        return cls(
            id=proto.id,
            events=[RegistryWebhookEvent.to_string(event) for event in proto.events],
            creation_timestamp=proto.creation_timestamp,
            last_updated_timestamp=proto.last_updated_timestamp,
            description=description,
            status=RegistryWebhookStatus.to_string(proto.status),
            http_url_spec=http_url_spec,
            job_spec=job_spec,
            model_name=model_name,
        )
