from databricks_registry_webhooks.exceptions import RegistryWebhooksException
from databricks_registry_webhooks.protos.webhooks_pb2 import RegistryWebhookEvent as ProtoRegistryWebhookEvent
from databricks_registry_webhooks.protos.databricks_pb2 import INVALID_PARAMETER_VALUE 


class RegistryWebhookEvent(object):
    """
    A trigger event associated with a Registry Webhook.
    """
    MODEL_VERSION_CREATED = ProtoRegistryWebhookEvent.Value("MODEL_VERSION_CREATED")
    MODEL_VERSION_TRANSITIONED_STAGE =\
        ProtoRegistryWebhookEvent.Value("MODEL_VERSION_TRANSITIONED_STAGE")
    TRANSITION_REQUEST_CREATED = ProtoRegistryWebhookEvent.Value("TRANSITION_REQUEST_CREATED")
    COMMENT_CREATED = ProtoRegistryWebhookEvent.Value("COMMENT_CREATED")
    REGISTERED_MODEL_CREATED = ProtoRegistryWebhookEvent.Value("REGISTERED_MODEL_CREATED")
    MODEL_VERSION_TAG_SET = ProtoRegistryWebhookEvent.Value("MODEL_VERSION_TAG_SET")
    MODEL_VERSION_TRANSITIONED_TO_STAGING =\
        ProtoRegistryWebhookEvent.Value("MODEL_VERSION_TRANSITIONED_TO_STAGING")
    MODEL_VERSION_TRANSITIONED_TO_PRODUCTION =\
        ProtoRegistryWebhookEvent.Value("MODEL_VERSION_TRANSITIONED_TO_PRODUCTION")
    MODEL_VERSION_TRANSITIONED_TO_ARCHIVED =\
        ProtoRegistryWebhookEvent.Value("MODEL_VERSION_TRANSITIONED_TO_ARCHIVED")
    TRANSITION_REQUEST_TO_STAGING_CREATED =\
        ProtoRegistryWebhookEvent.Value("TRANSITION_REQUEST_TO_STAGING_CREATED")
    TRANSITION_REQUEST_TO_PRODUCTION_CREATED =\
        ProtoRegistryWebhookEvent.Value("TRANSITION_REQUEST_TO_PRODUCTION_CREATED")
    TRANSITION_REQUEST_TO_ARCHIVED_CREATED =\
        ProtoRegistryWebhookEvent.Value("TRANSITION_REQUEST_TO_ARCHIVED_CREATED")

    _STRING_TO_STATUS = {
        k: ProtoRegistryWebhookEvent.Value(k)
        for k in ProtoRegistryWebhookEvent.keys()
    }
    _STATUS_TO_STRING = {value: key for key, value in _STRING_TO_STATUS.items()}

    @staticmethod
    def from_string(event_str):
        if event_str not in RegistryWebhookEvent._STRING_TO_STATUS:
            raise RegistryWebhooksException(
                "Could not get webhook event corresponding to string %s. Valid webhook "
                "event strings: %s"
                % (event_str, list(RegistryWebhookEvent._STRING_TO_STATUS.keys())),
                error_code=INVALID_PARAMETER_VALUE,
            )
        return RegistryWebhookEvent._STRING_TO_STATUS[event_str]

    @staticmethod
    def to_string(event):
        if event not in RegistryWebhookEvent._STATUS_TO_STRING:
            raise RegistryWebhooksException(
                "Could not get string corresponding to webhook event %s. Valid webhook "
                "events: %s"
                % (event, list(RegistryWebhookEvent._STATUS_TO_STRING.keys())),
                error_code=INVALID_PARAMETER_VALUE,
            )
        return RegistryWebhookEvent._STATUS_TO_STRING[event]

    @classmethod
    def is_valid(cls, status):
        return status in cls._STRING_TO_STATUS.keys()

    @classmethod
    def all_events(cls):
        """
        :return: A list of all supported Registry Webhook trigger event strings.
        """
        return list(cls._STRING_TO_STATUS.keys())
