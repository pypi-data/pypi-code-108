"""
Type annotations for macie2 service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_macie2 import Macie2Client

    client: Macie2Client = boto3.client("macie2")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    FindingPublishingFrequencyType,
    FindingsFilterActionType,
    FindingTypeType,
    GroupByType,
    JobStatusType,
    JobTypeType,
    MacieStatusType,
    ManagedDataIdentifierSelectorType,
    TimeRangeType,
)
from .paginator import (
    DescribeBucketsPaginator,
    GetUsageStatisticsPaginator,
    ListClassificationJobsPaginator,
    ListCustomDataIdentifiersPaginator,
    ListFindingsFiltersPaginator,
    ListFindingsPaginator,
    ListInvitationsPaginator,
    ListMembersPaginator,
    ListOrganizationAdminAccountsPaginator,
    SearchResourcesPaginator,
)
from .type_defs import (
    AccountDetailTypeDef,
    BatchGetCustomDataIdentifiersResponseTypeDef,
    BucketCriteriaAdditionalPropertiesTypeDef,
    BucketSortCriteriaTypeDef,
    ClassificationExportConfigurationTypeDef,
    CreateClassificationJobResponseTypeDef,
    CreateCustomDataIdentifierResponseTypeDef,
    CreateFindingsFilterResponseTypeDef,
    CreateInvitationsResponseTypeDef,
    CreateMemberResponseTypeDef,
    DeclineInvitationsResponseTypeDef,
    DeleteInvitationsResponseTypeDef,
    DescribeBucketsResponseTypeDef,
    DescribeClassificationJobResponseTypeDef,
    DescribeOrganizationConfigurationResponseTypeDef,
    FindingCriteriaTypeDef,
    FindingStatisticsSortCriteriaTypeDef,
    GetAdministratorAccountResponseTypeDef,
    GetBucketStatisticsResponseTypeDef,
    GetClassificationExportConfigurationResponseTypeDef,
    GetCustomDataIdentifierResponseTypeDef,
    GetFindingsFilterResponseTypeDef,
    GetFindingsPublicationConfigurationResponseTypeDef,
    GetFindingsResponseTypeDef,
    GetFindingStatisticsResponseTypeDef,
    GetInvitationsCountResponseTypeDef,
    GetMacieSessionResponseTypeDef,
    GetMasterAccountResponseTypeDef,
    GetMemberResponseTypeDef,
    GetUsageStatisticsResponseTypeDef,
    GetUsageTotalsResponseTypeDef,
    JobScheduleFrequencyTypeDef,
    ListClassificationJobsResponseTypeDef,
    ListCustomDataIdentifiersResponseTypeDef,
    ListFindingsFiltersResponseTypeDef,
    ListFindingsResponseTypeDef,
    ListInvitationsResponseTypeDef,
    ListJobsFilterCriteriaTypeDef,
    ListJobsSortCriteriaTypeDef,
    ListManagedDataIdentifiersResponseTypeDef,
    ListMembersResponseTypeDef,
    ListOrganizationAdminAccountsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    PutClassificationExportConfigurationResponseTypeDef,
    S3JobDefinitionTypeDef,
    SearchResourcesBucketCriteriaTypeDef,
    SearchResourcesResponseTypeDef,
    SearchResourcesSortCriteriaTypeDef,
    SecurityHubConfigurationTypeDef,
    SeverityLevelTypeDef,
    SortCriteriaTypeDef,
    TestCustomDataIdentifierResponseTypeDef,
    UpdateFindingsFilterResponseTypeDef,
    UsageStatisticsFilterTypeDef,
    UsageStatisticsSortByTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("Macie2Client",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class Macie2Client(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        Macie2Client exceptions.
        """

    def accept_invitation(
        self, *, invitationId: str, administratorAccountId: str = ..., masterAccount: str = ...
    ) -> Dict[str, Any]:
        """
        Accepts an Amazon Macie membership invitation that was received from a specific
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.accept_invitation)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#accept_invitation)
        """

    def batch_get_custom_data_identifiers(
        self, *, ids: Sequence[str] = ...
    ) -> BatchGetCustomDataIdentifiersResponseTypeDef:
        """
        Retrieves information about one or more custom data identifiers.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.batch_get_custom_data_identifiers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#batch_get_custom_data_identifiers)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#can_paginate)
        """

    def create_classification_job(
        self,
        *,
        clientToken: str,
        jobType: JobTypeType,
        name: str,
        s3JobDefinition: "S3JobDefinitionTypeDef",
        customDataIdentifierIds: Sequence[str] = ...,
        description: str = ...,
        initialRun: bool = ...,
        managedDataIdentifierIds: Sequence[str] = ...,
        managedDataIdentifierSelector: ManagedDataIdentifierSelectorType = ...,
        samplingPercentage: int = ...,
        scheduleFrequency: "JobScheduleFrequencyTypeDef" = ...,
        tags: Mapping[str, str] = ...
    ) -> CreateClassificationJobResponseTypeDef:
        """
        Creates and defines the settings for a classification job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.create_classification_job)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#create_classification_job)
        """

    def create_custom_data_identifier(
        self,
        *,
        name: str,
        regex: str,
        clientToken: str = ...,
        description: str = ...,
        ignoreWords: Sequence[str] = ...,
        keywords: Sequence[str] = ...,
        maximumMatchDistance: int = ...,
        severityLevels: Sequence["SeverityLevelTypeDef"] = ...,
        tags: Mapping[str, str] = ...
    ) -> CreateCustomDataIdentifierResponseTypeDef:
        """
        Creates and defines the criteria and other settings for a custom data
        identifier.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.create_custom_data_identifier)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#create_custom_data_identifier)
        """

    def create_findings_filter(
        self,
        *,
        action: FindingsFilterActionType,
        findingCriteria: "FindingCriteriaTypeDef",
        name: str,
        clientToken: str = ...,
        description: str = ...,
        position: int = ...,
        tags: Mapping[str, str] = ...
    ) -> CreateFindingsFilterResponseTypeDef:
        """
        Creates and defines the criteria and other settings for a findings filter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.create_findings_filter)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#create_findings_filter)
        """

    def create_invitations(
        self, *, accountIds: Sequence[str], disableEmailNotification: bool = ..., message: str = ...
    ) -> CreateInvitationsResponseTypeDef:
        """
        Sends an Amazon Macie membership invitation to one or more accounts.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.create_invitations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#create_invitations)
        """

    def create_member(
        self, *, account: "AccountDetailTypeDef", tags: Mapping[str, str] = ...
    ) -> CreateMemberResponseTypeDef:
        """
        Associates an account with an Amazon Macie administrator account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.create_member)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#create_member)
        """

    def create_sample_findings(
        self, *, findingTypes: Sequence[FindingTypeType] = ...
    ) -> Dict[str, Any]:
        """
        Creates sample findings.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.create_sample_findings)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#create_sample_findings)
        """

    def decline_invitations(
        self, *, accountIds: Sequence[str]
    ) -> DeclineInvitationsResponseTypeDef:
        """
        Declines Amazon Macie membership invitations that were received from specific
        accounts.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.decline_invitations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#decline_invitations)
        """

    def delete_custom_data_identifier(self, *, id: str) -> Dict[str, Any]:
        """
        Soft deletes a custom data identifier.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.delete_custom_data_identifier)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#delete_custom_data_identifier)
        """

    def delete_findings_filter(self, *, id: str) -> Dict[str, Any]:
        """
        Deletes a findings filter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.delete_findings_filter)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#delete_findings_filter)
        """

    def delete_invitations(self, *, accountIds: Sequence[str]) -> DeleteInvitationsResponseTypeDef:
        """
        Deletes Amazon Macie membership invitations that were received from specific
        accounts.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.delete_invitations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#delete_invitations)
        """

    def delete_member(self, *, id: str) -> Dict[str, Any]:
        """
        Deletes the association between an Amazon Macie administrator account and an
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.delete_member)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#delete_member)
        """

    def describe_buckets(
        self,
        *,
        criteria: Mapping[str, "BucketCriteriaAdditionalPropertiesTypeDef"] = ...,
        maxResults: int = ...,
        nextToken: str = ...,
        sortCriteria: "BucketSortCriteriaTypeDef" = ...
    ) -> DescribeBucketsResponseTypeDef:
        """
        Retrieves (queries) statistical data and other information about one or more S3
        buckets that Amazon Macie monitors and analyzes.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.describe_buckets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#describe_buckets)
        """

    def describe_classification_job(
        self, *, jobId: str
    ) -> DescribeClassificationJobResponseTypeDef:
        """
        Retrieves the status and settings for a classification job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.describe_classification_job)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#describe_classification_job)
        """

    def describe_organization_configuration(
        self,
    ) -> DescribeOrganizationConfigurationResponseTypeDef:
        """
        Retrieves the Amazon Macie configuration settings for an organization in
        Organizations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.describe_organization_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#describe_organization_configuration)
        """

    def disable_macie(self) -> Dict[str, Any]:
        """
        Disables Amazon Macie and deletes all settings and resources for a Macie
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.disable_macie)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#disable_macie)
        """

    def disable_organization_admin_account(self, *, adminAccountId: str) -> Dict[str, Any]:
        """
        Disables an account as the delegated Amazon Macie administrator account for an
        organization in Organizations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.disable_organization_admin_account)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#disable_organization_admin_account)
        """

    def disassociate_from_administrator_account(self) -> Dict[str, Any]:
        """
        Disassociates a member account from its Amazon Macie administrator account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.disassociate_from_administrator_account)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#disassociate_from_administrator_account)
        """

    def disassociate_from_master_account(self) -> Dict[str, Any]:
        """
        (Deprecated) Disassociates a member account from its Amazon Macie administrator
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.disassociate_from_master_account)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#disassociate_from_master_account)
        """

    def disassociate_member(self, *, id: str) -> Dict[str, Any]:
        """
        Disassociates an Amazon Macie administrator account from a member account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.disassociate_member)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#disassociate_member)
        """

    def enable_macie(
        self,
        *,
        clientToken: str = ...,
        findingPublishingFrequency: FindingPublishingFrequencyType = ...,
        status: MacieStatusType = ...
    ) -> Dict[str, Any]:
        """
        Enables Amazon Macie and specifies the configuration settings for a Macie
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.enable_macie)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#enable_macie)
        """

    def enable_organization_admin_account(
        self, *, adminAccountId: str, clientToken: str = ...
    ) -> Dict[str, Any]:
        """
        Designates an account as the delegated Amazon Macie administrator account for an
        organization in Organizations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.enable_organization_admin_account)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#enable_organization_admin_account)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#generate_presigned_url)
        """

    def get_administrator_account(self) -> GetAdministratorAccountResponseTypeDef:
        """
        Retrieves information about the Amazon Macie administrator account for an
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_administrator_account)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_administrator_account)
        """

    def get_bucket_statistics(self, *, accountId: str = ...) -> GetBucketStatisticsResponseTypeDef:
        """
        Retrieves (queries) aggregated statistical data about S3 buckets that Amazon
        Macie monitors and analyzes.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_bucket_statistics)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_bucket_statistics)
        """

    def get_classification_export_configuration(
        self,
    ) -> GetClassificationExportConfigurationResponseTypeDef:
        """
        Retrieves the configuration settings for storing data classification results.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_classification_export_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_classification_export_configuration)
        """

    def get_custom_data_identifier(self, *, id: str) -> GetCustomDataIdentifierResponseTypeDef:
        """
        Retrieves the criteria and other settings for a custom data identifier.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_custom_data_identifier)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_custom_data_identifier)
        """

    def get_finding_statistics(
        self,
        *,
        groupBy: GroupByType,
        findingCriteria: "FindingCriteriaTypeDef" = ...,
        size: int = ...,
        sortCriteria: "FindingStatisticsSortCriteriaTypeDef" = ...
    ) -> GetFindingStatisticsResponseTypeDef:
        """
        Retrieves (queries) aggregated statistical data about findings.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_finding_statistics)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_finding_statistics)
        """

    def get_findings(
        self, *, findingIds: Sequence[str], sortCriteria: "SortCriteriaTypeDef" = ...
    ) -> GetFindingsResponseTypeDef:
        """
        Retrieves the details of one or more findings.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_findings)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_findings)
        """

    def get_findings_filter(self, *, id: str) -> GetFindingsFilterResponseTypeDef:
        """
        Retrieves the criteria and other settings for a findings filter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_findings_filter)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_findings_filter)
        """

    def get_findings_publication_configuration(
        self,
    ) -> GetFindingsPublicationConfigurationResponseTypeDef:
        """
        Retrieves the configuration settings for publishing findings to Security Hub.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_findings_publication_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_findings_publication_configuration)
        """

    def get_invitations_count(self) -> GetInvitationsCountResponseTypeDef:
        """
        Retrieves the count of Amazon Macie membership invitations that were received by
        an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_invitations_count)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_invitations_count)
        """

    def get_macie_session(self) -> GetMacieSessionResponseTypeDef:
        """
        Retrieves the current status and configuration settings for an Amazon Macie
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_macie_session)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_macie_session)
        """

    def get_master_account(self) -> GetMasterAccountResponseTypeDef:
        """
        (Deprecated) Retrieves information about the Amazon Macie administrator account
        for an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_master_account)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_master_account)
        """

    def get_member(self, *, id: str) -> GetMemberResponseTypeDef:
        """
        Retrieves information about an account that's associated with an Amazon Macie
        administrator account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_member)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_member)
        """

    def get_usage_statistics(
        self,
        *,
        filterBy: Sequence["UsageStatisticsFilterTypeDef"] = ...,
        maxResults: int = ...,
        nextToken: str = ...,
        sortBy: "UsageStatisticsSortByTypeDef" = ...,
        timeRange: TimeRangeType = ...
    ) -> GetUsageStatisticsResponseTypeDef:
        """
        Retrieves (queries) quotas and aggregated usage data for one or more accounts.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_usage_statistics)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_usage_statistics)
        """

    def get_usage_totals(self, *, timeRange: str = ...) -> GetUsageTotalsResponseTypeDef:
        """
        Retrieves (queries) aggregated usage data for an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.get_usage_totals)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#get_usage_totals)
        """

    def list_classification_jobs(
        self,
        *,
        filterCriteria: "ListJobsFilterCriteriaTypeDef" = ...,
        maxResults: int = ...,
        nextToken: str = ...,
        sortCriteria: "ListJobsSortCriteriaTypeDef" = ...
    ) -> ListClassificationJobsResponseTypeDef:
        """
        Retrieves a subset of information about one or more classification jobs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_classification_jobs)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_classification_jobs)
        """

    def list_custom_data_identifiers(
        self, *, maxResults: int = ..., nextToken: str = ...
    ) -> ListCustomDataIdentifiersResponseTypeDef:
        """
        Retrieves a subset of information about all the custom data identifiers for an
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_custom_data_identifiers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_custom_data_identifiers)
        """

    def list_findings(
        self,
        *,
        findingCriteria: "FindingCriteriaTypeDef" = ...,
        maxResults: int = ...,
        nextToken: str = ...,
        sortCriteria: "SortCriteriaTypeDef" = ...
    ) -> ListFindingsResponseTypeDef:
        """
        Retrieves a subset of information about one or more findings.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_findings)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_findings)
        """

    def list_findings_filters(
        self, *, maxResults: int = ..., nextToken: str = ...
    ) -> ListFindingsFiltersResponseTypeDef:
        """
        Retrieves a subset of information about all the findings filters for an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_findings_filters)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_findings_filters)
        """

    def list_invitations(
        self, *, maxResults: int = ..., nextToken: str = ...
    ) -> ListInvitationsResponseTypeDef:
        """
        Retrieves information about the Amazon Macie membership invitations that were
        received by an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_invitations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_invitations)
        """

    def list_managed_data_identifiers(
        self, *, nextToken: str = ...
    ) -> ListManagedDataIdentifiersResponseTypeDef:
        """
        Retrieves information about all the managed data identifiers that Amazon Macie
        currently provides.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_managed_data_identifiers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_managed_data_identifiers)
        """

    def list_members(
        self, *, maxResults: int = ..., nextToken: str = ..., onlyAssociated: str = ...
    ) -> ListMembersResponseTypeDef:
        """
        Retrieves information about the accounts that are associated with an Amazon
        Macie administrator account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_members)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_members)
        """

    def list_organization_admin_accounts(
        self, *, maxResults: int = ..., nextToken: str = ...
    ) -> ListOrganizationAdminAccountsResponseTypeDef:
        """
        Retrieves information about the delegated Amazon Macie administrator account for
        an organization in Organizations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_organization_admin_accounts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_organization_admin_accounts)
        """

    def list_tags_for_resource(self, *, resourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Retrieves the tags (keys and values) that are associated with a classification
        job, custom data identifier, findings filter, or member account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#list_tags_for_resource)
        """

    def put_classification_export_configuration(
        self, *, configuration: "ClassificationExportConfigurationTypeDef"
    ) -> PutClassificationExportConfigurationResponseTypeDef:
        """
        Creates or updates the configuration settings for storing data classification
        results.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.put_classification_export_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#put_classification_export_configuration)
        """

    def put_findings_publication_configuration(
        self,
        *,
        clientToken: str = ...,
        securityHubConfiguration: "SecurityHubConfigurationTypeDef" = ...
    ) -> Dict[str, Any]:
        """
        Updates the configuration settings for publishing findings to Security Hub.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.put_findings_publication_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#put_findings_publication_configuration)
        """

    def search_resources(
        self,
        *,
        bucketCriteria: "SearchResourcesBucketCriteriaTypeDef" = ...,
        maxResults: int = ...,
        nextToken: str = ...,
        sortCriteria: "SearchResourcesSortCriteriaTypeDef" = ...
    ) -> SearchResourcesResponseTypeDef:
        """
        Retrieves (queries) statistical data and other information about Amazon Web
        Services resources that Amazon Macie monitors and analyzes.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.search_resources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#search_resources)
        """

    def tag_resource(self, *, resourceArn: str, tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds or updates one or more tags (keys and values) that are associated with a
        classification job, custom data identifier, findings filter, or member account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#tag_resource)
        """

    def test_custom_data_identifier(
        self,
        *,
        regex: str,
        sampleText: str,
        ignoreWords: Sequence[str] = ...,
        keywords: Sequence[str] = ...,
        maximumMatchDistance: int = ...
    ) -> TestCustomDataIdentifierResponseTypeDef:
        """
        Tests a custom data identifier.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.test_custom_data_identifier)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#test_custom_data_identifier)
        """

    def untag_resource(self, *, resourceArn: str, tagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes one or more tags (keys and values) from a classification job, custom
        data identifier, findings filter, or member account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#untag_resource)
        """

    def update_classification_job(self, *, jobId: str, jobStatus: JobStatusType) -> Dict[str, Any]:
        """
        Changes the status of a classification job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.update_classification_job)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#update_classification_job)
        """

    def update_findings_filter(
        self,
        *,
        id: str,
        action: FindingsFilterActionType = ...,
        description: str = ...,
        findingCriteria: "FindingCriteriaTypeDef" = ...,
        name: str = ...,
        position: int = ...,
        clientToken: str = ...
    ) -> UpdateFindingsFilterResponseTypeDef:
        """
        Updates the criteria and other settings for a findings filter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.update_findings_filter)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#update_findings_filter)
        """

    def update_macie_session(
        self,
        *,
        findingPublishingFrequency: FindingPublishingFrequencyType = ...,
        status: MacieStatusType = ...
    ) -> Dict[str, Any]:
        """
        Suspends or re-enables Amazon Macie, or updates the configuration settings for a
        Macie account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.update_macie_session)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#update_macie_session)
        """

    def update_member_session(self, *, id: str, status: MacieStatusType) -> Dict[str, Any]:
        """
        Enables an Amazon Macie administrator to suspend or re-enable Macie for a member
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.update_member_session)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#update_member_session)
        """

    def update_organization_configuration(self, *, autoEnable: bool) -> Dict[str, Any]:
        """
        Updates the Amazon Macie configuration settings for an organization in
        Organizations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Client.update_organization_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/client.html#update_organization_configuration)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_buckets"]
    ) -> DescribeBucketsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.DescribeBuckets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#describebucketspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["get_usage_statistics"]
    ) -> GetUsageStatisticsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.GetUsageStatistics)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#getusagestatisticspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_classification_jobs"]
    ) -> ListClassificationJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListClassificationJobs)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listclassificationjobspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_custom_data_identifiers"]
    ) -> ListCustomDataIdentifiersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListCustomDataIdentifiers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listcustomdataidentifierspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_findings"]) -> ListFindingsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListFindings)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listfindingspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_findings_filters"]
    ) -> ListFindingsFiltersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListFindingsFilters)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listfindingsfilterspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_invitations"]
    ) -> ListInvitationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListInvitations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listinvitationspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_members"]) -> ListMembersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListMembers)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listmemberspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_organization_admin_accounts"]
    ) -> ListOrganizationAdminAccountsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListOrganizationAdminAccounts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listorganizationadminaccountspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["search_resources"]
    ) -> SearchResourcesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.SearchResources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#searchresourcespaginator)
        """
