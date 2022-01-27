"""
Type annotations for connect service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_connect import ConnectClient
    from mypy_boto3_connect.paginator import (
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
        ListInstanceStorageConfigsPaginator,
        ListInstancesPaginator,
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

    client: ConnectClient = boto3.client("connect")

    get_metric_data_paginator: GetMetricDataPaginator = client.get_paginator("get_metric_data")
    list_agent_statuses_paginator: ListAgentStatusesPaginator = client.get_paginator("list_agent_statuses")
    list_approved_origins_paginator: ListApprovedOriginsPaginator = client.get_paginator("list_approved_origins")
    list_bots_paginator: ListBotsPaginator = client.get_paginator("list_bots")
    list_contact_flow_modules_paginator: ListContactFlowModulesPaginator = client.get_paginator("list_contact_flow_modules")
    list_contact_flows_paginator: ListContactFlowsPaginator = client.get_paginator("list_contact_flows")
    list_contact_references_paginator: ListContactReferencesPaginator = client.get_paginator("list_contact_references")
    list_default_vocabularies_paginator: ListDefaultVocabulariesPaginator = client.get_paginator("list_default_vocabularies")
    list_hours_of_operations_paginator: ListHoursOfOperationsPaginator = client.get_paginator("list_hours_of_operations")
    list_instance_attributes_paginator: ListInstanceAttributesPaginator = client.get_paginator("list_instance_attributes")
    list_instance_storage_configs_paginator: ListInstanceStorageConfigsPaginator = client.get_paginator("list_instance_storage_configs")
    list_instances_paginator: ListInstancesPaginator = client.get_paginator("list_instances")
    list_integration_associations_paginator: ListIntegrationAssociationsPaginator = client.get_paginator("list_integration_associations")
    list_lambda_functions_paginator: ListLambdaFunctionsPaginator = client.get_paginator("list_lambda_functions")
    list_lex_bots_paginator: ListLexBotsPaginator = client.get_paginator("list_lex_bots")
    list_phone_numbers_paginator: ListPhoneNumbersPaginator = client.get_paginator("list_phone_numbers")
    list_prompts_paginator: ListPromptsPaginator = client.get_paginator("list_prompts")
    list_queue_quick_connects_paginator: ListQueueQuickConnectsPaginator = client.get_paginator("list_queue_quick_connects")
    list_queues_paginator: ListQueuesPaginator = client.get_paginator("list_queues")
    list_quick_connects_paginator: ListQuickConnectsPaginator = client.get_paginator("list_quick_connects")
    list_routing_profile_queues_paginator: ListRoutingProfileQueuesPaginator = client.get_paginator("list_routing_profile_queues")
    list_routing_profiles_paginator: ListRoutingProfilesPaginator = client.get_paginator("list_routing_profiles")
    list_security_keys_paginator: ListSecurityKeysPaginator = client.get_paginator("list_security_keys")
    list_security_profile_permissions_paginator: ListSecurityProfilePermissionsPaginator = client.get_paginator("list_security_profile_permissions")
    list_security_profiles_paginator: ListSecurityProfilesPaginator = client.get_paginator("list_security_profiles")
    list_use_cases_paginator: ListUseCasesPaginator = client.get_paginator("list_use_cases")
    list_user_hierarchy_groups_paginator: ListUserHierarchyGroupsPaginator = client.get_paginator("list_user_hierarchy_groups")
    list_users_paginator: ListUsersPaginator = client.get_paginator("list_users")
    search_vocabularies_paginator: SearchVocabulariesPaginator = client.get_paginator("search_vocabularies")
    ```
"""
from datetime import datetime
from typing import Generic, Iterator, Sequence, TypeVar, Union

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import (
    AgentStatusTypeType,
    ContactFlowModuleStateType,
    ContactFlowTypeType,
    GroupingType,
    InstanceStorageResourceTypeType,
    IntegrationTypeType,
    LexVersionType,
    PhoneNumberCountryCodeType,
    PhoneNumberTypeType,
    QueueTypeType,
    QuickConnectTypeType,
    ReferenceTypeType,
    VocabularyLanguageCodeType,
    VocabularyStateType,
)
from .type_defs import (
    FiltersTypeDef,
    GetMetricDataResponseTypeDef,
    HistoricalMetricTypeDef,
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
    ListUseCasesResponseTypeDef,
    ListUserHierarchyGroupsResponseTypeDef,
    ListUsersResponseTypeDef,
    PaginatorConfigTypeDef,
    SearchVocabulariesResponseTypeDef,
)

__all__ = (
    "GetMetricDataPaginator",
    "ListAgentStatusesPaginator",
    "ListApprovedOriginsPaginator",
    "ListBotsPaginator",
    "ListContactFlowModulesPaginator",
    "ListContactFlowsPaginator",
    "ListContactReferencesPaginator",
    "ListDefaultVocabulariesPaginator",
    "ListHoursOfOperationsPaginator",
    "ListInstanceAttributesPaginator",
    "ListInstanceStorageConfigsPaginator",
    "ListInstancesPaginator",
    "ListIntegrationAssociationsPaginator",
    "ListLambdaFunctionsPaginator",
    "ListLexBotsPaginator",
    "ListPhoneNumbersPaginator",
    "ListPromptsPaginator",
    "ListQueueQuickConnectsPaginator",
    "ListQueuesPaginator",
    "ListQuickConnectsPaginator",
    "ListRoutingProfileQueuesPaginator",
    "ListRoutingProfilesPaginator",
    "ListSecurityKeysPaginator",
    "ListSecurityProfilePermissionsPaginator",
    "ListSecurityProfilesPaginator",
    "ListUseCasesPaginator",
    "ListUserHierarchyGroupsPaginator",
    "ListUsersPaginator",
    "SearchVocabulariesPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class GetMetricDataPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.GetMetricData)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#getmetricdatapaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        StartTime: Union[datetime, str],
        EndTime: Union[datetime, str],
        Filters: "FiltersTypeDef",
        HistoricalMetrics: Sequence["HistoricalMetricTypeDef"],
        Groupings: Sequence[GroupingType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetMetricDataResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.GetMetricData.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#getmetricdatapaginator)
        """


class ListAgentStatusesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListAgentStatuses)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listagentstatusespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        AgentStatusTypes: Sequence[AgentStatusTypeType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListAgentStatusResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListAgentStatuses.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listagentstatusespaginator)
        """


class ListApprovedOriginsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListApprovedOrigins)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listapprovedoriginspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListApprovedOriginsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListApprovedOrigins.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listapprovedoriginspaginator)
        """


class ListBotsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListBots)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listbotspaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        LexVersion: LexVersionType,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListBotsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListBots.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listbotspaginator)
        """


class ListContactFlowModulesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactFlowModules)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactflowmodulespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        ContactFlowModuleState: ContactFlowModuleStateType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListContactFlowModulesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactFlowModules.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactflowmodulespaginator)
        """


class ListContactFlowsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactFlows)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactflowspaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        ContactFlowTypes: Sequence[ContactFlowTypeType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListContactFlowsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactFlows.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactflowspaginator)
        """


class ListContactReferencesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactReferences)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactreferencespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        ContactId: str,
        ReferenceTypes: Sequence[ReferenceTypeType],
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListContactReferencesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListContactReferences.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listcontactreferencespaginator)
        """


class ListDefaultVocabulariesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListDefaultVocabularies)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listdefaultvocabulariespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        LanguageCode: VocabularyLanguageCodeType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListDefaultVocabulariesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListDefaultVocabularies.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listdefaultvocabulariespaginator)
        """


class ListHoursOfOperationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListHoursOfOperations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listhoursofoperationspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListHoursOfOperationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListHoursOfOperations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listhoursofoperationspaginator)
        """


class ListInstanceAttributesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstanceAttributes)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstanceattributespaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListInstanceAttributesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstanceAttributes.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstanceattributespaginator)
        """


class ListInstanceStorageConfigsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstanceStorageConfigs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstancestorageconfigspaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        ResourceType: InstanceStorageResourceTypeType,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListInstanceStorageConfigsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstanceStorageConfigs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstancestorageconfigspaginator)
        """


class ListInstancesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstances)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstancespaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListInstancesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListInstances.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listinstancespaginator)
        """


class ListIntegrationAssociationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListIntegrationAssociations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listintegrationassociationspaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        IntegrationType: IntegrationTypeType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListIntegrationAssociationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListIntegrationAssociations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listintegrationassociationspaginator)
        """


class ListLambdaFunctionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListLambdaFunctions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listlambdafunctionspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListLambdaFunctionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListLambdaFunctions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listlambdafunctionspaginator)
        """


class ListLexBotsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListLexBots)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listlexbotspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListLexBotsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListLexBots.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listlexbotspaginator)
        """


class ListPhoneNumbersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListPhoneNumbers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listphonenumberspaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        PhoneNumberTypes: Sequence[PhoneNumberTypeType] = ...,
        PhoneNumberCountryCodes: Sequence[PhoneNumberCountryCodeType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPhoneNumbersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListPhoneNumbers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listphonenumberspaginator)
        """


class ListPromptsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListPrompts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listpromptspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPromptsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListPrompts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listpromptspaginator)
        """


class ListQueueQuickConnectsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQueueQuickConnects)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listqueuequickconnectspaginator)
    """

    def paginate(
        self, *, InstanceId: str, QueueId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListQueueQuickConnectsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQueueQuickConnects.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listqueuequickconnectspaginator)
        """


class ListQueuesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQueues)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listqueuespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        QueueTypes: Sequence[QueueTypeType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListQueuesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQueues.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listqueuespaginator)
        """


class ListQuickConnectsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQuickConnects)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listquickconnectspaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        QuickConnectTypes: Sequence[QuickConnectTypeType] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListQuickConnectsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListQuickConnects.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listquickconnectspaginator)
        """


class ListRoutingProfileQueuesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListRoutingProfileQueues)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listroutingprofilequeuespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        RoutingProfileId: str,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRoutingProfileQueuesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListRoutingProfileQueues.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listroutingprofilequeuespaginator)
        """


class ListRoutingProfilesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListRoutingProfiles)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listroutingprofilespaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRoutingProfilesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListRoutingProfiles.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listroutingprofilespaginator)
        """


class ListSecurityKeysPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityKeys)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecuritykeyspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListSecurityKeysResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityKeys.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecuritykeyspaginator)
        """


class ListSecurityProfilePermissionsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityProfilePermissions)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecurityprofilepermissionspaginator)
    """

    def paginate(
        self,
        *,
        SecurityProfileId: str,
        InstanceId: str,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListSecurityProfilePermissionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityProfilePermissions.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecurityprofilepermissionspaginator)
        """


class ListSecurityProfilesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityProfiles)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecurityprofilespaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListSecurityProfilesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListSecurityProfiles.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listsecurityprofilespaginator)
        """


class ListUseCasesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUseCases)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listusecasespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        IntegrationAssociationId: str,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListUseCasesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUseCases.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listusecasespaginator)
        """


class ListUserHierarchyGroupsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUserHierarchyGroups)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listuserhierarchygroupspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListUserHierarchyGroupsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUserHierarchyGroups.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listuserhierarchygroupspaginator)
        """


class ListUsersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUsers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listuserspaginator)
    """

    def paginate(
        self, *, InstanceId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListUsersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.ListUsers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#listuserspaginator)
        """


class SearchVocabulariesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.SearchVocabularies)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#searchvocabulariespaginator)
    """

    def paginate(
        self,
        *,
        InstanceId: str,
        State: VocabularyStateType = ...,
        NameStartsWith: str = ...,
        LanguageCode: VocabularyLanguageCodeType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[SearchVocabulariesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.45/reference/services/connect.html#Connect.Paginator.SearchVocabularies.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_connect/paginators.html#searchvocabulariespaginator)
        """
