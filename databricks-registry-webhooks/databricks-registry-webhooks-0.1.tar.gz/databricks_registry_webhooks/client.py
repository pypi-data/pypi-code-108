from typing import List

from databricks_registry_webhooks.entities import (
    RegistryWebhook,
    RegistryWebhookEvent,
    RegistryWebhookStatus,
    HttpUrlSpec,
    JobSpec,
    TestWebhookResponse,
)
from databricks_registry_webhooks.utils.rest_utils import (
    call_endpoint,
    extract_api_info_for_service,
    _REST_API_PATH_PREFIX,
)
from databricks_registry_webhooks.utils.databricks_utils import get_databricks_host_creds
from databricks_registry_webhooks.utils.proto_json_utils import message_to_json
from databricks_registry_webhooks.protos.webhooks_pb2 import (
    CreateRegistryWebhook,
    DeleteRegistryWebhook,
    ListRegistryWebhooks,
    ModelRegistryWebhooksService,
    TestRegistryWebhook,
    UpdateRegistryWebhook,
)


_METHOD_TO_INFO = extract_api_info_for_service(ModelRegistryWebhooksService, _REST_API_PATH_PREFIX)


class RegistryWebhooksClient:
    """
    A client with APIs for creating, listing, and operating on Model Registry Webhooks.
    """

    def __init__(self, registry_uri="databricks"):
        """
        :param registry_uri: Address of Model Registry server. Defaults to "databricks", which
                             refers to the Model Registry server in the Databricks Workspace where
                             the client is running or in the Databricks Workspace referenced by the
                             current Databricks CLI configuration.
        """
        self.registry_uri = registry_uri

    def _call_endpoint(self, api, json_body):
        endpoint, method = _METHOD_TO_INFO[api]
        response_proto = api.Response()
        host_creds = get_databricks_host_creds(self.registry_uri)
        return call_endpoint(host_creds, endpoint, method, json_body, response_proto)

    def create_webhook(
        self,
        events: List[str],
        http_url_spec: HttpUrlSpec = None,
        job_spec: JobSpec = None,
        model_name: str = None,
        description: str = None,
        status: str = "ACTIVE",
    ):
        """
        Create a Model Registry Webhook.

        :param events: A list of Model Registry events that trigger the Registry Webhook. Supported
                       events are:

                       - `MODEL_VERSION_CREATED`: A new Model Version was created for an associated
                                                  Registered Model.
                       - `MODEL_VERSION_TRANSITIONED_STAGE`: A Model Version’s stage was changed.
                       - `TRANSITION_REQUEST_CREATED`: A user requested a Model Version’s stage be
                                                       transitioned.
                       - `COMMENT_CREATED`: A user wrote a comment on a Registered Model.
                       - `REGISTERED_MODEL_CREATED`: A new Registered Model was created. This event
                                                     type can only be specified for a registry-wide
                                                     webhook where `model_name` is `None`.
                       - `MODEL_VERSION_TAG_SET`: A user set a tag on the Model Version.
                       - `MODEL_VERSION_TRANSITIONED_TO_STAGING`: A Model Version was transitioned
                                                                  to Staging.
                       - `MODEL_VERSION_TRANSITIONED_TO_PRODUCTION`: A Model Version was
                                                                     transitioned to Production.
                       - `MODEL_VERSION_TRANSITIONED_TO_ARCHIVED`: A Model Version was transitoned
                                                                   to Archived.
                       - `TRANSITION_REQUEST_TO_STAGING_CREATED`: A user requested that a Model
                                                                  Version be transitioned to
                                                                  Staging.
                       - `TRANSITION_REQUEST_TO_PRODUCTION_CREATED`: A user requested that a Model
                                                                     Version be transitioned to
                                                                     Production.
                       - `TRANSITION_REQUEST_TO_ARCHIVED_CREATED`: A user requested that a Model
                                                                   Version be transitioned to
                                                                   Archived.

        :param http_url_spec: Attributes (e.g. URL) of an HTTPS request for the Registry Webhook to
                              send when one of the specified `events` occurs. Exactly one of
                              `http_url_spec` or `job_spec` must be specified.
        :param job_spec: Attributes of a Databricks Job (e.g. Job ID) for the Registry Webhook to
                         run when one of the specified `events` occurs. Exactly one of
                         `http_url_spec` or `job_spec` must be specified.
        :param model_name: Name of the Registered Model whose events trigger the Registry Webhook.
                           If unspecified, the Registry Webhook is "registry-wide" and is triggered
                           for events occurring on any accessible model throughout the entire
                           Model Registry.
        :param description: A string description of the Registry Webhook.
        :param status: The status of the Registry Webhook. Supported statuses are:

                       - `ACTIVE`: The Registry Webhook is triggered when an associated event
                                   occurs.
                       - `DISABLED`: The Registry Webhook is never triggered.
                       - `TEST_MODE`: The Registry Webhook can be triggered through the Registry
                                      Webhook Test API, but it is never triggered on a real event.
        """
        proto = CreateRegistryWebhook()
        proto.events.extend([RegistryWebhookEvent.from_string(event) for event in events])
        proto.status = RegistryWebhookStatus.from_string(status)
        if http_url_spec is not None:
            proto.http_url_spec.MergeFrom(http_url_spec.to_proto())
        if job_spec is not None:
            proto.job_spec.MergeFrom(job_spec.to_proto())
        if model_name is not None:
            proto.model_name = model_name
        if description is not None:
            proto.description = description

        req_body = message_to_json(proto)
        response_proto = self._call_endpoint(CreateRegistryWebhook, req_body)
        return RegistryWebhook.from_proto(response_proto.webhook)


    def delete_webhook(
        self,
        id: str = None,
    ):
        """
        Delete a Model Registry Webhook.

        :param id: The id of the webhook to delete.
        """
        proto = DeleteRegistryWebhook()
        if id is not None:
            proto.id = id

        req_body = message_to_json(proto)
        self._call_endpoint(DeleteRegistryWebhook, req_body)


    def test_webhook(
        self,
        id: str = None,
        event: str = None,
    ):
        """
        Test a Model Registry Webhook.

        :param id: The ID of the webhook to test.
        :param event: A Model Registry event to trigger. If not specified, the test trigger event is
                      randomly chosen from the list of configured trigger events for the webhook.
                      Supported events are:

                      - `MODEL_VERSION_CREATED`: A new Model Version was created for an associated
                                                 Registered Model.
                      - `MODEL_VERSION_TRANSITIONED_STAGE`: A Model Version’s stage was changed.
                      - `TRANSITION_REQUEST_CREATED`: A user requested a Model Version’s stage be
                                                      transitioned.
                      - `COMMENT_CREATED`: A user wrote a comment on a Registered Model.
                      - `REGISTERED_MODEL_CREATED`: A new Registered Model was created. This event
                                                    type can only be specified for a registry-wide
                                                    webhook where `model_name` is `None`.
                      - `MODEL_VERSION_TAG_SET`: A user set a tag on the Model Version.
                      - `MODEL_VERSION_TRANSITIONED_TO_STAGING`: A Model Version was transitioned
                                                                 to Staging.
                      - `MODEL_VERSION_TRANSITIONED_TO_PRODUCTION`: A Model Version was
                                                                    transitioned to Production.
                      - `MODEL_VERSION_TRANSITIONED_TO_ARCHIVED`: A Model Version was transitoned
                                                                  to Archived.
                      - `TRANSITION_REQUEST_TO_STAGING_CREATED`: A user requested that a Model
                                                                 Version be transitioned to
                                                                 Staging.
                      - `TRANSITION_REQUEST_TO_PRODUCTION_CREATED`: A user requested that a Model
                                                                    Version be transitioned to
                                                                    Production.
                      - `TRANSITION_REQUEST_TO_ARCHIVED_CREATED`: A user requested that a Model
                                                                  Version be transitioned to
                                                                  Archived.
        """
        proto = TestRegistryWebhook()
        if id is not None:
            proto.id = id
        if event is not None:
            proto.event = RegistryWebhookEvent.from_string(event)

        req_body = message_to_json(proto)
        response_proto = self._call_endpoint(TestRegistryWebhook, req_body)
        return TestWebhookResponse.from_proto(response_proto)


    def list_webhooks(
        self,
        model_name: str = None,
        events: List[str] = None,
        max_results=10000,
    ):
        """
        List Model Registry Webhooks.

        :param model_name: The model name for which to list Registry Webhooks. If unspecified,
                           Registry Webhooks for all models in the Model Registry are listed.
        :param events: A list of Model Registry events with which the listed Registry Webhooks must
                       be associated. If a Registry Webhook is triggered by any event in the list,
                       it is included in the results. Supported events are:

                       - `MODEL_VERSION_CREATED`: A new Model Version was created for an associated
                                                  Registered Model.
                       - `MODEL_VERSION_TRANSITIONED_STAGE`: A Model Version’s stage was changed.
                       - `TRANSITION_REQUEST_CREATED`: A user requested a Model Version’s stage be
                                                       transitioned.
                       - `COMMENT_CREATED`: A user wrote a comment on a Registered Model.
                       - `REGISTERED_MODEL_CREATED`: A new Registered Model was created. This event
                                                     type can only be specified for a registry-wide
                                                     webhook where `model_name` is `None`.
                       - `MODEL_VERSION_TAG_SET`: A user set a tag on the Model Version.
                       - `MODEL_VERSION_TRANSITIONED_TO_STAGING`: A Model Version was transitioned
                                                                  to Staging.
                       - `MODEL_VERSION_TRANSITIONED_TO_PRODUCTION`: A Model Version was
                                                                     transitioned to Production.
                       - `MODEL_VERSION_TRANSITIONED_TO_ARCHIVED`: A Model Version was transitoned
                                                                   to Archived.
                       - `TRANSITION_REQUEST_TO_STAGING_CREATED`: A user requested that a Model
                                                                  Version be transitioned to
                                                                  Staging.
                       - `TRANSITION_REQUEST_TO_PRODUCTION_CREATED`: A user requested that a Model
                                                                     Version be transitioned to
                                                                     Production.
                       - `TRANSITION_REQUEST_TO_ARCHIVED_CREATED`: A user requested that a Model
                                                                   Version be transitioned to
                                                                   Archived.

        :param max_results: The maximum number of Registry Webhooks to return. 
        """
        per_page_max_results = min(1000, max_results)
        page_token = None
        results = []

        while True:
            proto = ListRegistryWebhooks()
            proto.max_results = per_page_max_results
            if model_name is not None:
                proto.model_name = model_name
            if events is not None:
                proto.events.extend([RegistryWebhookEvent.from_string(event) for event in events])
            if page_token is not None:
                proto.page_token = page_token

            req_body = message_to_json(proto)
            response_proto = self._call_endpoint(ListRegistryWebhooks, req_body)
            results.extend([
                RegistryWebhook.from_proto(webhook_proto)
                for webhook_proto in response_proto.webhooks
            ])

            if len(results) >= max_results:
                break

            if response_proto.next_page_token:
                page_token = response_proto.next_page_token
            else:
                break

        return results[:max_results]

    def update_webhook(
        self,
        id: str,
        events: List[str] = None,
        http_url_spec: HttpUrlSpec = None,
        job_spec: JobSpec = None,
        description: str = None,
        status: str = "ACTIVE",
    ):
        """
        Update a Model Registry Webhook.

        :param id: The ID of the webhook to update.
        :param events: A list of Model Registry events that trigger the Registry Webhook. If
                       specified, all existing events are replaced with the specified events.
                       Supported events are:

                       - `MODEL_VERSION_CREATED`: A new Model Version was created for an associated
                                                  Registered Model.
                       - `MODEL_VERSION_TRANSITIONED_STAGE`: A Model Version’s stage was changed.
                       - `TRANSITION_REQUEST_CREATED`: A user requested a Model Version’s stage be
                                                       transitioned.
                       - `COMMENT_CREATED`: A user wrote a comment on a Registered Model.
                       - `REGISTERED_MODEL_CREATED`: A new Registered Model was created. This event
                                                     type can only be specified for a registry-wide
                                                     webhook where `model_name` is `None`.
                       - `MODEL_VERSION_TAG_SET`: A user set a tag on the Model Version.
                       - `MODEL_VERSION_TRANSITIONED_TO_STAGING`: A Model Version was transitioned
                                                                  to Staging.
                       - `MODEL_VERSION_TRANSITIONED_TO_PRODUCTION`: A Model Version was
                                                                     transitioned to Production.
                       - `MODEL_VERSION_TRANSITIONED_TO_ARCHIVED`: A Model Version was transitoned
                                                                   to Archived.
                       - `TRANSITION_REQUEST_TO_STAGING_CREATED`: A user requested that a Model
                                                                  Version be transitioned to
                                                                  Staging.
                       - `TRANSITION_REQUEST_TO_PRODUCTION_CREATED`: A user requested that a Model
                                                                     Version be transitioned to
                                                                     Production.
                       - `TRANSITION_REQUEST_TO_ARCHIVED_CREATED`: A user requested that a Model
                                                                   Version be transitioned to
                                                                   Archived.

        :param http_url_spec: Attributes (e.g. URL) of an HTTPS request for the Registry Webhook to
                              send when one of the specified `events` occurs. If specified, the
                              existing HTTP URL Spec is replaced with the specified HTTP URL Spec. 
        :param job_spec: Attributes of a Databricks Job (e.g. Job ID) for the Registry Webhook to
                         run when one of the specified `events` occurs. If specified, the existing 
                         Job Spec is replaced with the specified Job Spec.
        :param description: A string description of the Registry Webhook. If specified, the
                            existing description is replaced with the specified description.
        :param status: The status of the Registry Webhook. If specified, the existing status is
                       replaced with the specified status. Supported statuses are:

                       - `ACTIVE`: The Registry Webhook is triggered when an associated event
                                   occurs.
                       - `DISABLED`: The Registry Webhook is never triggered.
                       - `TEST_MODE`: The Registry Webhook can be triggered through the Registry
                                      Webhook Test API, but it is never triggered on a real event.
        """
        proto = UpdateRegistryWebhook()
        proto.id = id
        proto.status = RegistryWebhookStatus.from_string(status)
        if events is not None:
            proto.events.extend([RegistryWebhookEvent.from_string(event) for event in events])
        if http_url_spec is not None:
            proto.http_url_spec.MergeFrom(http_url_spec.to_proto())
        if job_spec is not None:
            proto.job_spec.MergeFrom(job_spec.to_proto())
        if description is not None:
            proto.description = description

        req_body = message_to_json(proto)
        response_proto = self._call_endpoint(UpdateRegistryWebhook, req_body)
        return RegistryWebhook.from_proto(response_proto.webhook)
