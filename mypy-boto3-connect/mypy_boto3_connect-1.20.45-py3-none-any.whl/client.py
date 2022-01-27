"""
Type annotations for connect service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_connect import ConnectClient

    client: ConnectClient = boto3.client("connect")
    ```
"""
import sys
from datetime import datetime
from typing import Any, Dict, Mapping, Sequence, Type, Union, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    AgentStatusStateType,
    AgentStatusTypeType,
    ContactFlowModuleStateType,
    ContactFlowStateType,
    ContactFlowTypeType,
    DirectoryTypeType,
    GroupingType,
    InstanceAttributeTypeType,
    InstanceStorageResourceTypeType,
    IntegrationTypeType,
    LexVersionType,
    PhoneNumberCountryCodeType,
    PhoneNumberTypeType,
    QueueStatusType,
    QueueTypeType,
    QuickConnectTypeType,
    ReferenceTypeType,
    SourceTypeType,
    TrafficTypeType,
    UseCaseTypeType,
    VocabularyLanguageCodeType,
    VocabularyStateType,
)
from .paginator import (
    GetMetricDataPaginator,
    ListAgentStatusesPaginator,
    ListApprovedOriginsPaginator,
    ListBotsPaginator,
    ListContactFlowModulesPaginator,
    ListContactFlowsPaginator,
    ListContactReferencesPaginator,
    ListDefaultVocabulariesPaginator,
    ListHoursOfOperationsPaginator,
    ListInstanceAttributesPaginator,
    ListInstancesPaginator,
    ListInstanceStorageConfigsPaginator,
    ListIntegrationAssociationsPaginator,
    ListLambdaFunctionsPaginator,
    ListLexBotsPaginator,
    ListPhoneNumbersPaginator,
    ListPromptsPaginator,
    ListQueueQuickConnectsPaginator,
    ListQueuesPaginator,
    ListQuickConnectsPaginator,
    ListRoutingProfileQueuesPaginator,
    ListRoutingProfilesPaginator,
    ListSecurityKeysPaginator,
    ListSecurityProfilePermissionsPaginator,
    ListSecurityProfilesPaginator,
    ListUseCasesPaginator,
    ListUserHierarchyGroupsPaginator,
    ListUsersPaginator,
    SearchVocabulariesPaginator,
)
from .type_defs import (
    AnswerMachineDetectionConfigTypeDef,
    AssociateInstanceStorageConfigResponseTypeDef,
    AssociateSecurityKeyResponseTypeDef,
    ChatMessageTypeDef,
    ChatStreamingConfigurationTypeDef,
    CreateAgentStatusResponseTypeDef,
    CreateContactFlowModuleResponseTypeDef,
    CreateContactFlowResponseTypeDef,
    CreateHoursOfOperationResponseTypeDef,
    CreateInstanceResponseTypeDef,
    CreateIntegrationAssociationResponseTypeDef,
    CreateQueueResponseTypeDef,
    CreateQuickConnectResponseTypeDef,
    CreateRoutingProfileResponseTypeDef,
    CreateSecurityProfileResponseTypeDef,
    CreateUseCaseResponseTypeDef,
    CreateUserHierarchyGroupResponseTypeDef,
    CreateUserResponseTypeDef,
    CreateVocabularyResponseTypeDef,
    CurrentMetricTypeDef,
    DeleteVocabularyResponseTypeDef,
    DescribeAgentStatusResponseTypeDef,
    DescribeContactFlowModuleResponseTypeDef,
    DescribeContactFlowResponseTypeDef,
    DescribeContactResponseTypeDef,
    DescribeHoursOfOperationResponseTypeDef,
    DescribeInstanceAttributeResponseTypeDef,
    DescribeInstanceResponseTypeDef,
    DescribeInstanceStorageConfigResponseTypeDef,
    DescribeQueueResponseTypeDef,
    DescribeQuickConnectResponseTypeDef,
    DescribeRoutingProfileResponseTypeDef,
    DescribeSecurityProfileResponseTypeDef,
    DescribeUserHierarchyGroupResponseTypeDef,
    DescribeUserHierarchyStructureResponseTypeDef,
    DescribeUserResponseTypeDef,
    DescribeVocabularyResponseTypeDef,
    FiltersTypeDef,
    GetContactAttributesResponseTypeDef,
    GetCurrentMetricDataResponseTypeDef,
    GetFederationTokenResponseTypeDef,
    GetMetricDataResponseTypeDef,
    HierarchyStructureUpdateTypeDef,
    HistoricalMetricTypeDef,
    HoursOfOperationConfigTypeDef,
    InstanceStorageConfigTypeDef,
    LexBotTypeDef,
    LexV2BotTypeDef,
    ListAgentStatusResponseTypeDef,
    ListApprovedOriginsResponseTypeDef,
    ListBotsResponseTypeDef,
    ListContactFlowModulesResponseTypeDef,
    ListContactFlowsResponseTypeDef,
    ListContactReferencesResponseTypeDef,
    ListDefaultVocabulariesResponseTypeDef,
    ListHoursOfOperationsResponseTypeDef,
    ListInstanceAttributesResponseTypeDef,
    ListInstancesResponseTypeDef,
    ListInstanceStorageConfigsResponseTypeDef,
    ListIntegrationAssociationsResponseTypeDef,
    ListLambdaFunctionsResponseTypeDef,
    ListLexBotsResponseTypeDef,
    ListPhoneNumbersResponseTypeDef,
    ListPromptsResponseTypeDef,
    ListQueueQuickConnectsResponseTypeDef,
    ListQueuesResponseTypeDef,
    ListQuickConnectsResponseTypeDef,
    ListRoutingProfileQueuesResponseTypeDef,
    ListRoutingProfilesResponseTypeDef,
    ListSecurityKeysResponseTypeDef,
    ListSecurityProfilePermissionsResponseTypeDef,
    ListSecurityProfilesResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListUseCasesResponseTypeDef,
    ListUserHierarchyGroupsResponseTypeDef,
    ListUsersResponseTypeDef,
    MediaConcurrencyTypeDef,
    OutboundCallerConfigTypeDef,
    ParticipantDetailsTypeDef,
    QuickConnectConfigTypeDef,
    ReferenceTypeDef,
    RoutingProfileQueueConfigTypeDef,
    RoutingProfileQueueReferenceTypeDef,
    SearchVocabulariesResponseTypeDef,
    StartChatContactResponseTypeDef,
    StartContactStreamingResponseTypeDef,
    StartOutboundVoiceContactResponseTypeDef,
    StartTaskContactResponseTypeDef,
    UserIdentityInfoTypeDef,
    UserPhoneConfigTypeDef,
    VoiceRecordingConfigurationTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("ConnectClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ContactFlowNotPublishedException: Type[BotocoreClientError]
    ContactNotFoundException: Type[BotocoreClientError]
    DestinationNotAllowedException: Type[BotocoreClientError]
    DuplicateResourceException: Type[BotocoreClientError]
    IdempotencyException: Type[BotocoreClientError]
    InternalServiceException: Type[BotocoreClientError]
    InvalidContactFlowException: Type[BotocoreClientError]
    InvalidContactFlowModuleException: Type[BotocoreClientError]
    InvalidParameterException: Type[BotocoreClientError]
    InvalidRequestException: Type[BotocoreClientError]
    LimitExceededException: Type[BotocoreClientError]
    OutboundContactNotPermittedException: Type[BotocoreClientError]
    ResourceConflictException: Type[BotocoreClientError]
    ResourceInUseException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    UserNotFoundException: Type[BotocoreClientError]


class ConnectClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        ConnectClient exceptions.
        """

    def associate_approved_origin(self, *, InstanceId: str, Origin: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_approved_origin)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_approved_origin)
        """

    def associate_bot(
        self, *, InstanceId: str, LexBot: "LexBotTypeDef" = ..., LexV2Bot: "LexV2BotTypeDef" = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_bot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_bot)
        """

    def associate_default_vocabulary(
        self, *, InstanceId: str, LanguageCode: VocabularyLanguageCodeType, VocabularyId: str = ...
    ) -> Dict[str, Any]:
        """
        Associates an existing vocabulary as the default.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_default_vocabulary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_default_vocabulary)
        """

    def associate_instance_storage_config(
        self,
        *,
        InstanceId: str,
        ResourceType: InstanceStorageResourceTypeType,
        StorageConfig: "InstanceStorageConfigTypeDef"
    ) -> AssociateInstanceStorageConfigResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_instance_storage_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_instance_storage_config)
        """

    def associate_lambda_function(self, *, InstanceId: str, FunctionArn: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_lambda_function)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_lambda_function)
        """

    def associate_lex_bot(self, *, InstanceId: str, LexBot: "LexBotTypeDef") -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_lex_bot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_lex_bot)
        """

    def associate_queue_quick_connects(
        self, *, InstanceId: str, QueueId: str, QuickConnectIds: Sequence[str]
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_queue_quick_connects)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_queue_quick_connects)
        """

    def associate_routing_profile_queues(
        self,
        *,
        InstanceId: str,
        RoutingProfileId: str,
        QueueConfigs: Sequence["RoutingProfileQueueConfigTypeDef"]
    ) -> None:
        """
        Associates a set of queues with a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_routing_profile_queues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_routing_profile_queues)
        """

    def associate_security_key(
        self, *, InstanceId: str, Key: str
    ) -> AssociateSecurityKeyResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.associate_security_key)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#associate_security_key)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#can_paginate)
        """

    def create_agent_status(
        self,
        *,
        InstanceId: str,
        Name: str,
        State: AgentStatusStateType,
        Description: str = ...,
        DisplayOrder: int = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateAgentStatusResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_agent_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_agent_status)
        """

    def create_contact_flow(
        self,
        *,
        InstanceId: str,
        Name: str,
        Type: ContactFlowTypeType,
        Content: str,
        Description: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateContactFlowResponseTypeDef:
        """
        Creates a contact flow for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_contact_flow)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_contact_flow)
        """

    def create_contact_flow_module(
        self,
        *,
        InstanceId: str,
        Name: str,
        Content: str,
        Description: str = ...,
        Tags: Mapping[str, str] = ...,
        ClientToken: str = ...
    ) -> CreateContactFlowModuleResponseTypeDef:
        """
        Creates a contact flow module for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_contact_flow_module)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_contact_flow_module)
        """

    def create_hours_of_operation(
        self,
        *,
        InstanceId: str,
        Name: str,
        TimeZone: str,
        Config: Sequence["HoursOfOperationConfigTypeDef"],
        Description: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateHoursOfOperationResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_hours_of_operation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_hours_of_operation)
        """

    def create_instance(
        self,
        *,
        IdentityManagementType: DirectoryTypeType,
        InboundCallsEnabled: bool,
        OutboundCallsEnabled: bool,
        ClientToken: str = ...,
        InstanceAlias: str = ...,
        DirectoryId: str = ...
    ) -> CreateInstanceResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_instance)
        """

    def create_integration_association(
        self,
        *,
        InstanceId: str,
        IntegrationType: IntegrationTypeType,
        IntegrationArn: str,
        SourceApplicationUrl: str = ...,
        SourceApplicationName: str = ...,
        SourceType: SourceTypeType = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateIntegrationAssociationResponseTypeDef:
        """
        Creates an Amazon Web Services resource association with an Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_integration_association)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_integration_association)
        """

    def create_queue(
        self,
        *,
        InstanceId: str,
        Name: str,
        HoursOfOperationId: str,
        Description: str = ...,
        OutboundCallerConfig: "OutboundCallerConfigTypeDef" = ...,
        MaxContacts: int = ...,
        QuickConnectIds: Sequence[str] = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateQueueResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_queue)
        """

    def create_quick_connect(
        self,
        *,
        InstanceId: str,
        Name: str,
        QuickConnectConfig: "QuickConnectConfigTypeDef",
        Description: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateQuickConnectResponseTypeDef:
        """
        Creates a quick connect for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_quick_connect)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_quick_connect)
        """

    def create_routing_profile(
        self,
        *,
        InstanceId: str,
        Name: str,
        Description: str,
        DefaultOutboundQueueId: str,
        MediaConcurrencies: Sequence["MediaConcurrencyTypeDef"],
        QueueConfigs: Sequence["RoutingProfileQueueConfigTypeDef"] = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateRoutingProfileResponseTypeDef:
        """
        Creates a new routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_routing_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_routing_profile)
        """

    def create_security_profile(
        self,
        *,
        SecurityProfileName: str,
        InstanceId: str,
        Description: str = ...,
        Permissions: Sequence[str] = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateSecurityProfileResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_security_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_security_profile)
        """

    def create_use_case(
        self,
        *,
        InstanceId: str,
        IntegrationAssociationId: str,
        UseCaseType: UseCaseTypeType,
        Tags: Mapping[str, str] = ...
    ) -> CreateUseCaseResponseTypeDef:
        """
        Creates a use case for an integration association.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_use_case)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_use_case)
        """

    def create_user(
        self,
        *,
        Username: str,
        PhoneConfig: "UserPhoneConfigTypeDef",
        SecurityProfileIds: Sequence[str],
        RoutingProfileId: str,
        InstanceId: str,
        Password: str = ...,
        IdentityInfo: "UserIdentityInfoTypeDef" = ...,
        DirectoryUserId: str = ...,
        HierarchyGroupId: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateUserResponseTypeDef:
        """
        Creates a user account for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_user)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_user)
        """

    def create_user_hierarchy_group(
        self, *, Name: str, InstanceId: str, ParentGroupId: str = ..., Tags: Mapping[str, str] = ...
    ) -> CreateUserHierarchyGroupResponseTypeDef:
        """
        Creates a new user hierarchy group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_user_hierarchy_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_user_hierarchy_group)
        """

    def create_vocabulary(
        self,
        *,
        InstanceId: str,
        VocabularyName: str,
        LanguageCode: VocabularyLanguageCodeType,
        Content: str,
        ClientToken: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateVocabularyResponseTypeDef:
        """
        Creates a custom vocabulary associated with your Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.create_vocabulary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#create_vocabulary)
        """

    def delete_contact_flow(self, *, InstanceId: str, ContactFlowId: str) -> None:
        """
        Deletes a contact flow for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_contact_flow)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_contact_flow)
        """

    def delete_contact_flow_module(
        self, *, InstanceId: str, ContactFlowModuleId: str
    ) -> Dict[str, Any]:
        """
        Deletes the specified contact flow module.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_contact_flow_module)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_contact_flow_module)
        """

    def delete_hours_of_operation(self, *, InstanceId: str, HoursOfOperationId: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_hours_of_operation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_hours_of_operation)
        """

    def delete_instance(self, *, InstanceId: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_instance)
        """

    def delete_integration_association(
        self, *, InstanceId: str, IntegrationAssociationId: str
    ) -> None:
        """
        Deletes an Amazon Web Services resource association from an Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_integration_association)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_integration_association)
        """

    def delete_quick_connect(self, *, InstanceId: str, QuickConnectId: str) -> None:
        """
        Deletes a quick connect.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_quick_connect)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_quick_connect)
        """

    def delete_security_profile(self, *, InstanceId: str, SecurityProfileId: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_security_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_security_profile)
        """

    def delete_use_case(
        self, *, InstanceId: str, IntegrationAssociationId: str, UseCaseId: str
    ) -> None:
        """
        Deletes a use case from an integration association.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_use_case)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_use_case)
        """

    def delete_user(self, *, InstanceId: str, UserId: str) -> None:
        """
        Deletes a user account from the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_user)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_user)
        """

    def delete_user_hierarchy_group(self, *, HierarchyGroupId: str, InstanceId: str) -> None:
        """
        Deletes an existing user hierarchy group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_user_hierarchy_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_user_hierarchy_group)
        """

    def delete_vocabulary(
        self, *, InstanceId: str, VocabularyId: str
    ) -> DeleteVocabularyResponseTypeDef:
        """
        Deletes the vocabulary that has the given identifier.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.delete_vocabulary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#delete_vocabulary)
        """

    def describe_agent_status(
        self, *, InstanceId: str, AgentStatusId: str
    ) -> DescribeAgentStatusResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_agent_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_agent_status)
        """

    def describe_contact(
        self, *, InstanceId: str, ContactId: str
    ) -> DescribeContactResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_contact)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_contact)
        """

    def describe_contact_flow(
        self, *, InstanceId: str, ContactFlowId: str
    ) -> DescribeContactFlowResponseTypeDef:
        """
        Describes the specified contact flow.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_contact_flow)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_contact_flow)
        """

    def describe_contact_flow_module(
        self, *, InstanceId: str, ContactFlowModuleId: str
    ) -> DescribeContactFlowModuleResponseTypeDef:
        """
        Describes the specified contact flow module.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_contact_flow_module)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_contact_flow_module)
        """

    def describe_hours_of_operation(
        self, *, InstanceId: str, HoursOfOperationId: str
    ) -> DescribeHoursOfOperationResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_hours_of_operation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_hours_of_operation)
        """

    def describe_instance(self, *, InstanceId: str) -> DescribeInstanceResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_instance)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_instance)
        """

    def describe_instance_attribute(
        self, *, InstanceId: str, AttributeType: InstanceAttributeTypeType
    ) -> DescribeInstanceAttributeResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_instance_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_instance_attribute)
        """

    def describe_instance_storage_config(
        self, *, InstanceId: str, AssociationId: str, ResourceType: InstanceStorageResourceTypeType
    ) -> DescribeInstanceStorageConfigResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_instance_storage_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_instance_storage_config)
        """

    def describe_queue(self, *, InstanceId: str, QueueId: str) -> DescribeQueueResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_queue)
        """

    def describe_quick_connect(
        self, *, InstanceId: str, QuickConnectId: str
    ) -> DescribeQuickConnectResponseTypeDef:
        """
        Describes the quick connect.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_quick_connect)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_quick_connect)
        """

    def describe_routing_profile(
        self, *, InstanceId: str, RoutingProfileId: str
    ) -> DescribeRoutingProfileResponseTypeDef:
        """
        Describes the specified routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_routing_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_routing_profile)
        """

    def describe_security_profile(
        self, *, SecurityProfileId: str, InstanceId: str
    ) -> DescribeSecurityProfileResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_security_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_security_profile)
        """

    def describe_user(self, *, UserId: str, InstanceId: str) -> DescribeUserResponseTypeDef:
        """
        Describes the specified user account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_user)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_user)
        """

    def describe_user_hierarchy_group(
        self, *, HierarchyGroupId: str, InstanceId: str
    ) -> DescribeUserHierarchyGroupResponseTypeDef:
        """
        Describes the specified hierarchy group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_user_hierarchy_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_user_hierarchy_group)
        """

    def describe_user_hierarchy_structure(
        self, *, InstanceId: str
    ) -> DescribeUserHierarchyStructureResponseTypeDef:
        """
        Describes the hierarchy structure of the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_user_hierarchy_structure)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_user_hierarchy_structure)
        """

    def describe_vocabulary(
        self, *, InstanceId: str, VocabularyId: str
    ) -> DescribeVocabularyResponseTypeDef:
        """
        Describes the specified vocabulary.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.describe_vocabulary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#describe_vocabulary)
        """

    def disassociate_approved_origin(self, *, InstanceId: str, Origin: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_approved_origin)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_approved_origin)
        """

    def disassociate_bot(
        self, *, InstanceId: str, LexBot: "LexBotTypeDef" = ..., LexV2Bot: "LexV2BotTypeDef" = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_bot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_bot)
        """

    def disassociate_instance_storage_config(
        self, *, InstanceId: str, AssociationId: str, ResourceType: InstanceStorageResourceTypeType
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_instance_storage_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_instance_storage_config)
        """

    def disassociate_lambda_function(self, *, InstanceId: str, FunctionArn: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_lambda_function)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_lambda_function)
        """

    def disassociate_lex_bot(self, *, InstanceId: str, BotName: str, LexRegion: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_lex_bot)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_lex_bot)
        """

    def disassociate_queue_quick_connects(
        self, *, InstanceId: str, QueueId: str, QuickConnectIds: Sequence[str]
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_queue_quick_connects)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_queue_quick_connects)
        """

    def disassociate_routing_profile_queues(
        self,
        *,
        InstanceId: str,
        RoutingProfileId: str,
        QueueReferences: Sequence["RoutingProfileQueueReferenceTypeDef"]
    ) -> None:
        """
        Disassociates a set of queues from a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_routing_profile_queues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_routing_profile_queues)
        """

    def disassociate_security_key(self, *, InstanceId: str, AssociationId: str) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.disassociate_security_key)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#disassociate_security_key)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#generate_presigned_url)
        """

    def get_contact_attributes(
        self, *, InstanceId: str, InitialContactId: str
    ) -> GetContactAttributesResponseTypeDef:
        """
        Retrieves the contact attributes for the specified contact.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.get_contact_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#get_contact_attributes)
        """

    def get_current_metric_data(
        self,
        *,
        InstanceId: str,
        Filters: "FiltersTypeDef",
        CurrentMetrics: Sequence["CurrentMetricTypeDef"],
        Groupings: Sequence[GroupingType] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> GetCurrentMetricDataResponseTypeDef:
        """
        Gets the real-time metric data from the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.get_current_metric_data)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#get_current_metric_data)
        """

    def get_federation_token(self, *, InstanceId: str) -> GetFederationTokenResponseTypeDef:
        """
        Retrieves a token for federation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.get_federation_token)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#get_federation_token)
        """

    def get_metric_data(
        self,
        *,
        InstanceId: str,
        StartTime: Union[datetime, str],
        EndTime: Union[datetime, str],
        Filters: "FiltersTypeDef",
        HistoricalMetrics: Sequence["HistoricalMetricTypeDef"],
        Groupings: Sequence[GroupingType] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> GetMetricDataResponseTypeDef:
        """
        Gets historical metric data from the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.get_metric_data)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#get_metric_data)
        """

    def list_agent_statuses(
        self,
        *,
        InstanceId: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        AgentStatusTypes: Sequence[AgentStatusTypeType] = ...
    ) -> ListAgentStatusResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_agent_statuses)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_agent_statuses)
        """

    def list_approved_origins(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListApprovedOriginsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_approved_origins)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_approved_origins)
        """

    def list_bots(
        self,
        *,
        InstanceId: str,
        LexVersion: LexVersionType,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListBotsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_bots)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_bots)
        """

    def list_contact_flow_modules(
        self,
        *,
        InstanceId: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        ContactFlowModuleState: ContactFlowModuleStateType = ...
    ) -> ListContactFlowModulesResponseTypeDef:
        """
        Provides information about the contact flow modules for the specified Amazon
        Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_contact_flow_modules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_contact_flow_modules)
        """

    def list_contact_flows(
        self,
        *,
        InstanceId: str,
        ContactFlowTypes: Sequence[ContactFlowTypeType] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListContactFlowsResponseTypeDef:
        """
        Provides information about the contact flows for the specified Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_contact_flows)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_contact_flows)
        """

    def list_contact_references(
        self,
        *,
        InstanceId: str,
        ContactId: str,
        ReferenceTypes: Sequence[ReferenceTypeType],
        NextToken: str = ...
    ) -> ListContactReferencesResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_contact_references)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_contact_references)
        """

    def list_default_vocabularies(
        self,
        *,
        InstanceId: str,
        LanguageCode: VocabularyLanguageCodeType = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListDefaultVocabulariesResponseTypeDef:
        """
        Lists the default vocabularies for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_default_vocabularies)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_default_vocabularies)
        """

    def list_hours_of_operations(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListHoursOfOperationsResponseTypeDef:
        """
        Provides information about the hours of operation for the specified Amazon
        Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_hours_of_operations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_hours_of_operations)
        """

    def list_instance_attributes(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListInstanceAttributesResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_instance_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_instance_attributes)
        """

    def list_instance_storage_configs(
        self,
        *,
        InstanceId: str,
        ResourceType: InstanceStorageResourceTypeType,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListInstanceStorageConfigsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_instance_storage_configs)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_instance_storage_configs)
        """

    def list_instances(
        self, *, NextToken: str = ..., MaxResults: int = ...
    ) -> ListInstancesResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_instances)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_instances)
        """

    def list_integration_associations(
        self,
        *,
        InstanceId: str,
        IntegrationType: IntegrationTypeType = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListIntegrationAssociationsResponseTypeDef:
        """
        Provides summary information about the Amazon Web Services resource associations
        for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_integration_associations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_integration_associations)
        """

    def list_lambda_functions(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListLambdaFunctionsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_lambda_functions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_lambda_functions)
        """

    def list_lex_bots(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListLexBotsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_lex_bots)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_lex_bots)
        """

    def list_phone_numbers(
        self,
        *,
        InstanceId: str,
        PhoneNumberTypes: Sequence[PhoneNumberTypeType] = ...,
        PhoneNumberCountryCodes: Sequence[PhoneNumberCountryCodeType] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListPhoneNumbersResponseTypeDef:
        """
        Provides information about the phone numbers for the specified Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_phone_numbers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_phone_numbers)
        """

    def list_prompts(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListPromptsResponseTypeDef:
        """
        Provides information about the prompts for the specified Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_prompts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_prompts)
        """

    def list_queue_quick_connects(
        self, *, InstanceId: str, QueueId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListQueueQuickConnectsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_queue_quick_connects)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_queue_quick_connects)
        """

    def list_queues(
        self,
        *,
        InstanceId: str,
        QueueTypes: Sequence[QueueTypeType] = ...,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListQueuesResponseTypeDef:
        """
        Provides information about the queues for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_queues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_queues)
        """

    def list_quick_connects(
        self,
        *,
        InstanceId: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        QuickConnectTypes: Sequence[QuickConnectTypeType] = ...
    ) -> ListQuickConnectsResponseTypeDef:
        """
        Provides information about the quick connects for the specified Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_quick_connects)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_quick_connects)
        """

    def list_routing_profile_queues(
        self, *, InstanceId: str, RoutingProfileId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListRoutingProfileQueuesResponseTypeDef:
        """
        Lists the queues associated with a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_routing_profile_queues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_routing_profile_queues)
        """

    def list_routing_profiles(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListRoutingProfilesResponseTypeDef:
        """
        Provides summary information about the routing profiles for the specified Amazon
        Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_routing_profiles)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_routing_profiles)
        """

    def list_security_keys(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListSecurityKeysResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_security_keys)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_security_keys)
        """

    def list_security_profile_permissions(
        self,
        *,
        SecurityProfileId: str,
        InstanceId: str,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListSecurityProfilePermissionsResponseTypeDef:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_security_profile_permissions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_security_profile_permissions)
        """

    def list_security_profiles(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListSecurityProfilesResponseTypeDef:
        """
        Provides summary information about the security profiles for the specified
        Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_security_profiles)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_security_profiles)
        """

    def list_tags_for_resource(self, *, resourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Lists the tags for the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_tags_for_resource)
        """

    def list_use_cases(
        self,
        *,
        InstanceId: str,
        IntegrationAssociationId: str,
        NextToken: str = ...,
        MaxResults: int = ...
    ) -> ListUseCasesResponseTypeDef:
        """
        Lists the use cases for the integration association.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_use_cases)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_use_cases)
        """

    def list_user_hierarchy_groups(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListUserHierarchyGroupsResponseTypeDef:
        """
        Provides summary information about the hierarchy groups for the specified Amazon
        Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_user_hierarchy_groups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_user_hierarchy_groups)
        """

    def list_users(
        self, *, InstanceId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> ListUsersResponseTypeDef:
        """
        Provides summary information about the users for the specified Amazon Connect
        instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.list_users)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#list_users)
        """

    def resume_contact_recording(
        self, *, InstanceId: str, ContactId: str, InitialContactId: str
    ) -> Dict[str, Any]:
        """
        When a contact is being recorded, and the recording has been suspended using
        SuspendContactRecording, this API resumes recording the call.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.resume_contact_recording)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#resume_contact_recording)
        """

    def search_vocabularies(
        self,
        *,
        InstanceId: str,
        MaxResults: int = ...,
        NextToken: str = ...,
        State: VocabularyStateType = ...,
        NameStartsWith: str = ...,
        LanguageCode: VocabularyLanguageCodeType = ...
    ) -> SearchVocabulariesResponseTypeDef:
        """
        Searches for vocabularies within a specific Amazon Connect instance using
        `State` , `NameStartsWith` , and `LanguageCode` .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.search_vocabularies)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#search_vocabularies)
        """

    def start_chat_contact(
        self,
        *,
        InstanceId: str,
        ContactFlowId: str,
        ParticipantDetails: "ParticipantDetailsTypeDef",
        Attributes: Mapping[str, str] = ...,
        InitialMessage: "ChatMessageTypeDef" = ...,
        ClientToken: str = ...,
        ChatDurationInMinutes: int = ...
    ) -> StartChatContactResponseTypeDef:
        """
        Initiates a contact flow to start a new chat for the customer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.start_chat_contact)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#start_chat_contact)
        """

    def start_contact_recording(
        self,
        *,
        InstanceId: str,
        ContactId: str,
        InitialContactId: str,
        VoiceRecordingConfiguration: "VoiceRecordingConfigurationTypeDef"
    ) -> Dict[str, Any]:
        """
        Starts recording the contact when the agent joins the call.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.start_contact_recording)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#start_contact_recording)
        """

    def start_contact_streaming(
        self,
        *,
        InstanceId: str,
        ContactId: str,
        ChatStreamingConfiguration: "ChatStreamingConfigurationTypeDef",
        ClientToken: str
    ) -> StartContactStreamingResponseTypeDef:
        """
        Initiates real-time message streaming for a new chat contact.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.start_contact_streaming)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#start_contact_streaming)
        """

    def start_outbound_voice_contact(
        self,
        *,
        DestinationPhoneNumber: str,
        ContactFlowId: str,
        InstanceId: str,
        ClientToken: str = ...,
        SourcePhoneNumber: str = ...,
        QueueId: str = ...,
        Attributes: Mapping[str, str] = ...,
        AnswerMachineDetectionConfig: "AnswerMachineDetectionConfigTypeDef" = ...,
        CampaignId: str = ...,
        TrafficType: TrafficTypeType = ...
    ) -> StartOutboundVoiceContactResponseTypeDef:
        """
        Places an outbound call to a contact, and then initiates the contact flow.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.start_outbound_voice_contact)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#start_outbound_voice_contact)
        """

    def start_task_contact(
        self,
        *,
        InstanceId: str,
        ContactFlowId: str,
        Name: str,
        PreviousContactId: str = ...,
        Attributes: Mapping[str, str] = ...,
        References: Mapping[str, "ReferenceTypeDef"] = ...,
        Description: str = ...,
        ClientToken: str = ...,
        ScheduledTime: Union[datetime, str] = ...
    ) -> StartTaskContactResponseTypeDef:
        """
        Initiates a contact flow to start a new task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.start_task_contact)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#start_task_contact)
        """

    def stop_contact(self, *, ContactId: str, InstanceId: str) -> Dict[str, Any]:
        """
        Ends the specified contact.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.stop_contact)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#stop_contact)
        """

    def stop_contact_recording(
        self, *, InstanceId: str, ContactId: str, InitialContactId: str
    ) -> Dict[str, Any]:
        """
        Stops recording a call when a contact is being recorded.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.stop_contact_recording)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#stop_contact_recording)
        """

    def stop_contact_streaming(
        self, *, InstanceId: str, ContactId: str, StreamingId: str
    ) -> Dict[str, Any]:
        """
        Ends message streaming on a specified contact.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.stop_contact_streaming)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#stop_contact_streaming)
        """

    def suspend_contact_recording(
        self, *, InstanceId: str, ContactId: str, InitialContactId: str
    ) -> Dict[str, Any]:
        """
        When a contact is being recorded, this API suspends recording the call.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.suspend_contact_recording)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#suspend_contact_recording)
        """

    def tag_resource(self, *, resourceArn: str, tags: Mapping[str, str]) -> None:
        """
        Adds the specified tags to the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#tag_resource)
        """

    def untag_resource(self, *, resourceArn: str, tagKeys: Sequence[str]) -> None:
        """
        Removes the specified tags from the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#untag_resource)
        """

    def update_agent_status(
        self,
        *,
        InstanceId: str,
        AgentStatusId: str,
        Name: str = ...,
        Description: str = ...,
        State: AgentStatusStateType = ...,
        DisplayOrder: int = ...,
        ResetOrderNumber: bool = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_agent_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_agent_status)
        """

    def update_contact(
        self,
        *,
        InstanceId: str,
        ContactId: str,
        Name: str = ...,
        Description: str = ...,
        References: Mapping[str, "ReferenceTypeDef"] = ...
    ) -> Dict[str, Any]:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact)
        """

    def update_contact_attributes(
        self, *, InitialContactId: str, InstanceId: str, Attributes: Mapping[str, str]
    ) -> Dict[str, Any]:
        """
        Creates or updates user-defined contact attributes associated with the specified
        contact.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_attributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_attributes)
        """

    def update_contact_flow_content(
        self, *, InstanceId: str, ContactFlowId: str, Content: str
    ) -> None:
        """
        Updates the specified contact flow.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_flow_content)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_flow_content)
        """

    def update_contact_flow_metadata(
        self,
        *,
        InstanceId: str,
        ContactFlowId: str,
        Name: str = ...,
        Description: str = ...,
        ContactFlowState: ContactFlowStateType = ...
    ) -> None:
        """
        Updates metadata about specified contact flow.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_flow_metadata)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_flow_metadata)
        """

    def update_contact_flow_module_content(
        self, *, InstanceId: str, ContactFlowModuleId: str, Content: str
    ) -> Dict[str, Any]:
        """
        Updates specified contact flow module for the specified Amazon Connect instance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_flow_module_content)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_flow_module_content)
        """

    def update_contact_flow_module_metadata(
        self,
        *,
        InstanceId: str,
        ContactFlowModuleId: str,
        Name: str = ...,
        Description: str = ...,
        State: ContactFlowModuleStateType = ...
    ) -> Dict[str, Any]:
        """
        Updates metadata about specified contact flow module.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_flow_module_metadata)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_flow_module_metadata)
        """

    def update_contact_flow_name(
        self, *, InstanceId: str, ContactFlowId: str, Name: str = ..., Description: str = ...
    ) -> None:
        """
        The name of the contact flow.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_flow_name)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_flow_name)
        """

    def update_contact_schedule(
        self, *, InstanceId: str, ContactId: str, ScheduledTime: Union[datetime, str]
    ) -> Dict[str, Any]:
        """
        Updates the scheduled time of a task contact that is already scheduled.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_contact_schedule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_contact_schedule)
        """

    def update_hours_of_operation(
        self,
        *,
        InstanceId: str,
        HoursOfOperationId: str,
        Name: str = ...,
        Description: str = ...,
        TimeZone: str = ...,
        Config: Sequence["HoursOfOperationConfigTypeDef"] = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_hours_of_operation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_hours_of_operation)
        """

    def update_instance_attribute(
        self, *, InstanceId: str, AttributeType: InstanceAttributeTypeType, Value: str
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_instance_attribute)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_instance_attribute)
        """

    def update_instance_storage_config(
        self,
        *,
        InstanceId: str,
        AssociationId: str,
        ResourceType: InstanceStorageResourceTypeType,
        StorageConfig: "InstanceStorageConfigTypeDef"
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_instance_storage_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_instance_storage_config)
        """

    def update_queue_hours_of_operation(
        self, *, InstanceId: str, QueueId: str, HoursOfOperationId: str
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_queue_hours_of_operation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_queue_hours_of_operation)
        """

    def update_queue_max_contacts(
        self, *, InstanceId: str, QueueId: str, MaxContacts: int = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_queue_max_contacts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_queue_max_contacts)
        """

    def update_queue_name(
        self, *, InstanceId: str, QueueId: str, Name: str = ..., Description: str = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_queue_name)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_queue_name)
        """

    def update_queue_outbound_caller_config(
        self, *, InstanceId: str, QueueId: str, OutboundCallerConfig: "OutboundCallerConfigTypeDef"
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_queue_outbound_caller_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_queue_outbound_caller_config)
        """

    def update_queue_status(
        self, *, InstanceId: str, QueueId: str, Status: QueueStatusType
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_queue_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_queue_status)
        """

    def update_quick_connect_config(
        self,
        *,
        InstanceId: str,
        QuickConnectId: str,
        QuickConnectConfig: "QuickConnectConfigTypeDef"
    ) -> None:
        """
        Updates the configuration settings for the specified quick connect.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_quick_connect_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_quick_connect_config)
        """

    def update_quick_connect_name(
        self, *, InstanceId: str, QuickConnectId: str, Name: str = ..., Description: str = ...
    ) -> None:
        """
        Updates the name and description of a quick connect.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_quick_connect_name)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_quick_connect_name)
        """

    def update_routing_profile_concurrency(
        self,
        *,
        InstanceId: str,
        RoutingProfileId: str,
        MediaConcurrencies: Sequence["MediaConcurrencyTypeDef"]
    ) -> None:
        """
        Updates the channels that agents can handle in the Contact Control Panel (CCP)
        for a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_routing_profile_concurrency)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_routing_profile_concurrency)
        """

    def update_routing_profile_default_outbound_queue(
        self, *, InstanceId: str, RoutingProfileId: str, DefaultOutboundQueueId: str
    ) -> None:
        """
        Updates the default outbound queue of a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_routing_profile_default_outbound_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_routing_profile_default_outbound_queue)
        """

    def update_routing_profile_name(
        self, *, InstanceId: str, RoutingProfileId: str, Name: str = ..., Description: str = ...
    ) -> None:
        """
        Updates the name and description of a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_routing_profile_name)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_routing_profile_name)
        """

    def update_routing_profile_queues(
        self,
        *,
        InstanceId: str,
        RoutingProfileId: str,
        QueueConfigs: Sequence["RoutingProfileQueueConfigTypeDef"]
    ) -> None:
        """
        Updates the properties associated with a set of queues for a routing profile.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_routing_profile_queues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_routing_profile_queues)
        """

    def update_security_profile(
        self,
        *,
        SecurityProfileId: str,
        InstanceId: str,
        Description: str = ...,
        Permissions: Sequence[str] = ...
    ) -> None:
        """
        This API is in preview release for Amazon Connect and is subject to change.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_security_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_security_profile)
        """

    def update_user_hierarchy(
        self, *, UserId: str, InstanceId: str, HierarchyGroupId: str = ...
    ) -> None:
        """
        Assigns the specified hierarchy group to the specified user.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_hierarchy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_hierarchy)
        """

    def update_user_hierarchy_group_name(
        self, *, Name: str, HierarchyGroupId: str, InstanceId: str
    ) -> None:
        """
        Updates the name of the user hierarchy group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_hierarchy_group_name)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_hierarchy_group_name)
        """

    def update_user_hierarchy_structure(
        self, *, HierarchyStructure: "HierarchyStructureUpdateTypeDef", InstanceId: str
    ) -> None:
        """
        Updates the user hierarchy structure: add, remove, and rename user hierarchy
        levels.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_hierarchy_structure)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_hierarchy_structure)
        """

    def update_user_identity_info(
        self, *, IdentityInfo: "UserIdentityInfoTypeDef", UserId: str, InstanceId: str
    ) -> None:
        """
        Updates the identity information for the specified user.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_identity_info)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_identity_info)
        """

    def update_user_phone_config(
        self, *, PhoneConfig: "UserPhoneConfigTypeDef", UserId: str, InstanceId: str
    ) -> None:
        """
        Updates the phone configuration settings for the specified user.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_phone_config)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_phone_config)
        """

    def update_user_routing_profile(
        self, *, RoutingProfileId: str, UserId: str, InstanceId: str
    ) -> None:
        """
        Assigns the specified routing profile to the specified user.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_routing_profile)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_routing_profile)
        """

    def update_user_security_profiles(
        self, *, SecurityProfileIds: Sequence[str], UserId: str, InstanceId: str
    ) -> None:
        """
        Assigns the specified security profiles to the specified user.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Client.update_user_security_profiles)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/client.html#update_user_security_profiles)
        """

    @overload
    def get_paginator(self, operation_name: Literal["get_metric_data"]) -> GetMetricDataPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.GetMetricData)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#getmetricdatapaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_agent_statuses"]
    ) -> ListAgentStatusesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListAgentStatuses)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listagentstatusespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_approved_origins"]
    ) -> ListApprovedOriginsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListApprovedOrigins)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listapprovedoriginspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_bots"]) -> ListBotsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListBots)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listbotspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_contact_flow_modules"]
    ) -> ListContactFlowModulesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactFlowModules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactflowmodulespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_contact_flows"]
    ) -> ListContactFlowsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactFlows)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactflowspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_contact_references"]
    ) -> ListContactReferencesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactReferences)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactreferencespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_default_vocabularies"]
    ) -> ListDefaultVocabulariesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListDefaultVocabularies)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listdefaultvocabulariespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_hours_of_operations"]
    ) -> ListHoursOfOperationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListHoursOfOperations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listhoursofoperationspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_instance_attributes"]
    ) -> ListInstanceAttributesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstanceAttributes)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstanceattributespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_instance_storage_configs"]
    ) -> ListInstanceStorageConfigsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstanceStorageConfigs)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstancestorageconfigspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_instances"]) -> ListInstancesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstances)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstancespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_integration_associations"]
    ) -> ListIntegrationAssociationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListIntegrationAssociations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listintegrationassociationspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_lambda_functions"]
    ) -> ListLambdaFunctionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListLambdaFunctions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listlambdafunctionspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_lex_bots"]) -> ListLexBotsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListLexBots)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listlexbotspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_phone_numbers"]
    ) -> ListPhoneNumbersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListPhoneNumbers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listphonenumberspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_prompts"]) -> ListPromptsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListPrompts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listpromptspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_queue_quick_connects"]
    ) -> ListQueueQuickConnectsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQueueQuickConnects)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listqueuequickconnectspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_queues"]) -> ListQueuesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQueues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listqueuespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_quick_connects"]
    ) -> ListQuickConnectsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQuickConnects)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listquickconnectspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_routing_profile_queues"]
    ) -> ListRoutingProfileQueuesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListRoutingProfileQueues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listroutingprofilequeuespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_routing_profiles"]
    ) -> ListRoutingProfilesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListRoutingProfiles)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listroutingprofilespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_security_keys"]
    ) -> ListSecurityKeysPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityKeys)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecuritykeyspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_security_profile_permissions"]
    ) -> ListSecurityProfilePermissionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityProfilePermissions)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecurityprofilepermissionspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_security_profiles"]
    ) -> ListSecurityProfilesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityProfiles)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecurityprofilespaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_use_cases"]) -> ListUseCasesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUseCases)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listusecasespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_user_hierarchy_groups"]
    ) -> ListUserHierarchyGroupsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUserHierarchyGroups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listuserhierarchygroupspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_users"]) -> ListUsersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUsers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listuserspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["search_vocabularies"]
    ) -> SearchVocabulariesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.SearchVocabularies)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#searchvocabulariespaginator)
        """
