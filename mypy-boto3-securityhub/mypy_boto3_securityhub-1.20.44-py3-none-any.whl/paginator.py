"""
Type annotations for securityhub service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_securityhub import SecurityHubClient
    from mypy_boto3_securityhub.paginator import (
        DescribeActionTargetsPaginator,
        DescribeProductsPaginator,
        DescribeStandardsPaginator,
        DescribeStandardsControlsPaginator,
        GetEnabledStandardsPaginator,
        GetFindingsPaginator,
        GetInsightsPaginator,
        ListEnabledProductsForImportPaginator,
        ListFindingAggregatorsPaginator,
        ListInvitationsPaginator,
        ListMembersPaginator,
        ListOrganizationAdminAccountsPaginator,
    )

    client: SecurityHubClient = boto3.client("securityhub")

    describe_action_targets_paginator: DescribeActionTargetsPaginator = client.get_paginator("describe_action_targets")
    describe_products_paginator: DescribeProductsPaginator = client.get_paginator("describe_products")
    describe_standards_paginator: DescribeStandardsPaginator = client.get_paginator("describe_standards")
    describe_standards_controls_paginator: DescribeStandardsControlsPaginator = client.get_paginator("describe_standards_controls")
    get_enabled_standards_paginator: GetEnabledStandardsPaginator = client.get_paginator("get_enabled_standards")
    get_findings_paginator: GetFindingsPaginator = client.get_paginator("get_findings")
    get_insights_paginator: GetInsightsPaginator = client.get_paginator("get_insights")
    list_enabled_products_for_import_paginator: ListEnabledProductsForImportPaginator = client.get_paginator("list_enabled_products_for_import")
    list_finding_aggregators_paginator: ListFindingAggregatorsPaginator = client.get_paginator("list_finding_aggregators")
    list_invitations_paginator: ListInvitationsPaginator = client.get_paginator("list_invitations")
    list_members_paginator: ListMembersPaginator = client.get_paginator("list_members")
    list_organization_admin_accounts_paginator: ListOrganizationAdminAccountsPaginator = client.get_paginator("list_organization_admin_accounts")
    ```
"""
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    AwsSecurityFindingFiltersTypeDef,
    DescribeActionTargetsResponseTypeDef,
    DescribeProductsResponseTypeDef,
    DescribeStandardsControlsResponseTypeDef,
    DescribeStandardsResponseTypeDef,
    GetEnabledStandardsResponseTypeDef,
    GetFindingsResponseTypeDef,
    GetInsightsResponseTypeDef,
    ListEnabledProductsForImportResponseTypeDef,
    ListFindingAggregatorsResponseTypeDef,
    ListInvitationsResponseTypeDef,
    ListMembersResponseTypeDef,
    ListOrganizationAdminAccountsResponseTypeDef,
    PaginatorConfigTypeDef,
    SortCriterionTypeDef,
)

__all__ = (
    "DescribeActionTargetsPaginator",
    "DescribeProductsPaginator",
    "DescribeStandardsPaginator",
    "DescribeStandardsControlsPaginator",
    "GetEnabledStandardsPaginator",
    "GetFindingsPaginator",
    "GetInsightsPaginator",
    "ListEnabledProductsForImportPaginator",
    "ListFindingAggregatorsPaginator",
    "ListInvitationsPaginator",
    "ListMembersPaginator",
    "ListOrganizationAdminAccountsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeActionTargetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeActionTargets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describeactiontargetspaginator)
    """

    def paginate(
        self,
        *,
        ActionTargetArns: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeActionTargetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeActionTargets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describeactiontargetspaginator)
        """


class DescribeProductsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeProducts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describeproductspaginator)
    """

    def paginate(
        self, *, ProductArn: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeProductsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeProducts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describeproductspaginator)
        """


class DescribeStandardsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeStandards)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describestandardspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeStandardsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeStandards.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describestandardspaginator)
        """


class DescribeStandardsControlsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeStandardsControls)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describestandardscontrolspaginator)
    """

    def paginate(
        self, *, StandardsSubscriptionArn: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeStandardsControlsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.DescribeStandardsControls.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#describestandardscontrolspaginator)
        """


class GetEnabledStandardsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.GetEnabledStandards)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#getenabledstandardspaginator)
    """

    def paginate(
        self,
        *,
        StandardsSubscriptionArns: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetEnabledStandardsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.GetEnabledStandards.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#getenabledstandardspaginator)
        """


class GetFindingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.GetFindings)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#getfindingspaginator)
    """

    def paginate(
        self,
        *,
        Filters: "AwsSecurityFindingFiltersTypeDef" = ...,
        SortCriteria: Sequence["SortCriterionTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetFindingsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.GetFindings.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#getfindingspaginator)
        """


class GetInsightsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.GetInsights)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#getinsightspaginator)
    """

    def paginate(
        self, *, InsightArns: Sequence[str] = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetInsightsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.GetInsights.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#getinsightspaginator)
        """


class ListEnabledProductsForImportPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListEnabledProductsForImport)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listenabledproductsforimportpaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListEnabledProductsForImportResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListEnabledProductsForImport.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listenabledproductsforimportpaginator)
        """


class ListFindingAggregatorsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListFindingAggregators)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listfindingaggregatorspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListFindingAggregatorsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListFindingAggregators.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listfindingaggregatorspaginator)
        """


class ListInvitationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListInvitations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listinvitationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListInvitationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListInvitations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listinvitationspaginator)
        """


class ListMembersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListMembers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listmemberspaginator)
    """

    def paginate(
        self, *, OnlyAssociated: bool = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListMembersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListMembers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listmemberspaginator)
        """


class ListOrganizationAdminAccountsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListOrganizationAdminAccounts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listorganizationadminaccountspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListOrganizationAdminAccountsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.44/reference/services/securityhub.html#SecurityHub.Paginator.ListOrganizationAdminAccounts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_securityhub/paginators.html#listorganizationadminaccountspaginator)
        """
