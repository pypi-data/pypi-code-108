from databricks_registry_webhooks.exceptions import RegistryWebhooksException
from databricks_registry_webhooks.protos.databricks_pb2 import INVALID_PARAMETER_VALUE 
from databricks_registry_webhooks.protos.webhooks_pb2 import (
    RegistryWebhookStatus as ProtoRegistryWebhookStatus
)


class RegistryWebhookStatus(object):
    """
    The status of a Registry Webhook.
    """
    ACTIVE = ProtoRegistryWebhookStatus.Value("ACTIVE")
    DISABLED = ProtoRegistryWebhookStatus.Value("DISABLED")
    TEST_MODE = ProtoRegistryWebhookStatus.Value("TEST_MODE")

    _STRING_TO_STATUS = {
        k: ProtoRegistryWebhookStatus.Value(k)
        for k in ProtoRegistryWebhookStatus.keys()
    }
    _STATUS_TO_STRING = {value: key for key, value in _STRING_TO_STATUS.items()}

    @staticmethod
    def from_string(status_str):
        if status_str not in RegistryWebhookStatus._STRING_TO_STATUS:
            raise RegistryWebhooksException(
                "Could not get webhook status corresponding to string %s. Valid webhook "
                "status strings: %s"
                % (status_str, list(RegistryWebhookStatus._STRING_TO_STATUS.keys())),
                error_code=INVALID_PARAMETER_VALUE,
            )
        return RegistryWebhookStatus._STRING_TO_STATUS[status_str]

    @staticmethod
    def to_string(status):
        if status not in RegistryWebhookStatus._STATUS_TO_STRING:
            raise RegistryWebhooksException(
                "Could not get string corresponding to webhook status %s. Valid webhook "
                "statuses: %s"
                % (status, list(RegistryWebhookStatus._STATUS_TO_STRING.keys())),
                error_code=INVALID_PARAMETER_VALUE,
            )
        return RegistryWebhookStatus._STATUS_TO_STRING[status]

    @classmethod
    def is_valid(cls, status):
        return status in cls._STRING_TO_STATUS.keys()

    @classmethod
    def all_statuses(cls):
        """
        :return: A list of all supported Registry Webhook Status strings.
        """
        return list(cls._STRING_TO_STATUS.keys())
