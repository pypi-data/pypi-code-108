"""
Type annotations for macie2 service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_macie2 import Macie2Client
    from mypy_boto3_macie2.paginator import (
        DescribeBucketsPaginator,
        GetUsageStatisticsPaginator,
        ListClassificationJobsPaginator,
        ListCustomDataIdentifiersPaginator,
        ListFindingsPaginator,
        ListFindingsFiltersPaginator,
        ListInvitationsPaginator,
        ListMembersPaginator,
        ListOrganizationAdminAccountsPaginator,
        SearchResourcesPaginator,
    )

    client: Macie2Client = boto3.client("macie2")

    describe_buckets_paginator: DescribeBucketsPaginator = client.get_paginator("describe_buckets")
    get_usage_statistics_paginator: GetUsageStatisticsPaginator = client.get_paginator("get_usage_statistics")
    list_classification_jobs_paginator: ListClassificationJobsPaginator = client.get_paginator("list_classification_jobs")
    list_custom_data_identifiers_paginator: ListCustomDataIdentifiersPaginator = client.get_paginator("list_custom_data_identifiers")
    list_findings_paginator: ListFindingsPaginator = client.get_paginator("list_findings")
    list_findings_filters_paginator: ListFindingsFiltersPaginator = client.get_paginator("list_findings_filters")
    list_invitations_paginator: ListInvitationsPaginator = client.get_paginator("list_invitations")
    list_members_paginator: ListMembersPaginator = client.get_paginator("list_members")
    list_organization_admin_accounts_paginator: ListOrganizationAdminAccountsPaginator = client.get_paginator("list_organization_admin_accounts")
    search_resources_paginator: SearchResourcesPaginator = client.get_paginator("search_resources")
    ```
"""
from typing import Generic, Iterator, Mapping, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .literals import TimeRangeType
from .type_defs import (
    BucketCriteriaAdditionalPropertiesTypeDef,
    BucketSortCriteriaTypeDef,
    DescribeBucketsResponseTypeDef,
    FindingCriteriaTypeDef,
    GetUsageStatisticsResponseTypeDef,
    ListClassificationJobsResponseTypeDef,
    ListCustomDataIdentifiersResponseTypeDef,
    ListFindingsFiltersResponseTypeDef,
    ListFindingsResponseTypeDef,
    ListInvitationsResponseTypeDef,
    ListJobsFilterCriteriaTypeDef,
    ListJobsSortCriteriaTypeDef,
    ListMembersResponseTypeDef,
    ListOrganizationAdminAccountsResponseTypeDef,
    PaginatorConfigTypeDef,
    SearchResourcesBucketCriteriaTypeDef,
    SearchResourcesResponseTypeDef,
    SearchResourcesSortCriteriaTypeDef,
    SortCriteriaTypeDef,
    UsageStatisticsFilterTypeDef,
    UsageStatisticsSortByTypeDef,
)

__all__ = (
    "DescribeBucketsPaginator",
    "GetUsageStatisticsPaginator",
    "ListClassificationJobsPaginator",
    "ListCustomDataIdentifiersPaginator",
    "ListFindingsPaginator",
    "ListFindingsFiltersPaginator",
    "ListInvitationsPaginator",
    "ListMembersPaginator",
    "ListOrganizationAdminAccountsPaginator",
    "SearchResourcesPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeBucketsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.DescribeBuckets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#describebucketspaginator)
    """

    def paginate(
        self,
        *,
        criteria: Mapping[str, "BucketCriteriaAdditionalPropertiesTypeDef"] = ...,
        sortCriteria: "BucketSortCriteriaTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeBucketsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.DescribeBuckets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#describebucketspaginator)
        """


class GetUsageStatisticsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.GetUsageStatistics)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#getusagestatisticspaginator)
    """

    def paginate(
        self,
        *,
        filterBy: Sequence["UsageStatisticsFilterTypeDef"] = ...,
        sortBy: "UsageStatisticsSortByTypeDef" = ...,
        timeRange: TimeRangeType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetUsageStatisticsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.GetUsageStatistics.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#getusagestatisticspaginator)
        """


class ListClassificationJobsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListClassificationJobs)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listclassificationjobspaginator)
    """

    def paginate(
        self,
        *,
        filterCriteria: "ListJobsFilterCriteriaTypeDef" = ...,
        sortCriteria: "ListJobsSortCriteriaTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListClassificationJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListClassificationJobs.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listclassificationjobspaginator)
        """


class ListCustomDataIdentifiersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListCustomDataIdentifiers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listcustomdataidentifierspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListCustomDataIdentifiersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListCustomDataIdentifiers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listcustomdataidentifierspaginator)
        """


class ListFindingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListFindings)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listfindingspaginator)
    """

    def paginate(
        self,
        *,
        findingCriteria: "FindingCriteriaTypeDef" = ...,
        sortCriteria: "SortCriteriaTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListFindingsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListFindings.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listfindingspaginator)
        """


class ListFindingsFiltersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListFindingsFilters)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listfindingsfilterspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListFindingsFiltersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListFindingsFilters.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listfindingsfilterspaginator)
        """


class ListInvitationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListInvitations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listinvitationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListInvitationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListInvitations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listinvitationspaginator)
        """


class ListMembersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListMembers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listmemberspaginator)
    """

    def paginate(
        self, *, onlyAssociated: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListMembersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListMembers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listmemberspaginator)
        """


class ListOrganizationAdminAccountsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListOrganizationAdminAccounts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listorganizationadminaccountspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListOrganizationAdminAccountsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.ListOrganizationAdminAccounts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#listorganizationadminaccountspaginator)
        """


class SearchResourcesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.SearchResources)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#searchresourcespaginator)
    """

    def paginate(
        self,
        *,
        bucketCriteria: "SearchResourcesBucketCriteriaTypeDef" = ...,
        sortCriteria: "SearchResourcesSortCriteriaTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[SearchResourcesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.39/reference/services/macie2.html#Macie2.Paginator.SearchResources.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/paginators.html#searchresourcespaginator)
        """
