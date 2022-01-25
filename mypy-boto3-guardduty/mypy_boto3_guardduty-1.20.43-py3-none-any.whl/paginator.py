"""
Type annotations for guardduty service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_guardduty import GuardDutyClient
    from mypy_boto3_guardduty.paginator import (
        ListDetectorsPaginator,
        ListFiltersPaginator,
        ListFindingsPaginator,
        ListIPSetsPaginator,
        ListInvitationsPaginator,
        ListMembersPaginator,
        ListOrganizationAdminAccountsPaginator,
        ListThreatIntelSetsPaginator,
    )

    client: GuardDutyClient = boto3.client("guardduty")

    list_detectors_paginator: ListDetectorsPaginator = client.get_paginator("list_detectors")
    list_filters_paginator: ListFiltersPaginator = client.get_paginator("list_filters")
    list_findings_paginator: ListFindingsPaginator = client.get_paginator("list_findings")
    list_ip_sets_paginator: ListIPSetsPaginator = client.get_paginator("list_ip_sets")
    list_invitations_paginator: ListInvitationsPaginator = client.get_paginator("list_invitations")
    list_members_paginator: ListMembersPaginator = client.get_paginator("list_members")
    list_organization_admin_accounts_paginator: ListOrganizationAdminAccountsPaginator = client.get_paginator("list_organization_admin_accounts")
    list_threat_intel_sets_paginator: ListThreatIntelSetsPaginator = client.get_paginator("list_threat_intel_sets")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    FindingCriteriaTypeDef,
    ListDetectorsResponseTypeDef,
    ListFiltersResponseTypeDef,
    ListFindingsResponseTypeDef,
    ListInvitationsResponseTypeDef,
    ListIPSetsResponseTypeDef,
    ListMembersResponseTypeDef,
    ListOrganizationAdminAccountsResponseTypeDef,
    ListThreatIntelSetsResponseTypeDef,
    PaginatorConfigTypeDef,
    SortCriteriaTypeDef,
)

__all__ = (
    "ListDetectorsPaginator",
    "ListFiltersPaginator",
    "ListFindingsPaginator",
    "ListIPSetsPaginator",
    "ListInvitationsPaginator",
    "ListMembersPaginator",
    "ListOrganizationAdminAccountsPaginator",
    "ListThreatIntelSetsPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListDetectorsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListDetectors)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listdetectorspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListDetectorsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListDetectors.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listdetectorspaginator)
        """


class ListFiltersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListFilters)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listfilterspaginator)
    """

    def paginate(
        self, *, DetectorId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListFiltersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListFilters.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listfilterspaginator)
        """


class ListFindingsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListFindings)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listfindingspaginator)
    """

    def paginate(
        self,
        *,
        DetectorId: str,
        FindingCriteria: "FindingCriteriaTypeDef" = ...,
        SortCriteria: "SortCriteriaTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListFindingsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListFindings.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listfindingspaginator)
        """


class ListIPSetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListIPSets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listipsetspaginator)
    """

    def paginate(
        self, *, DetectorId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListIPSetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListIPSets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listipsetspaginator)
        """


class ListInvitationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListInvitations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listinvitationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListInvitationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListInvitations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listinvitationspaginator)
        """


class ListMembersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListMembers)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listmemberspaginator)
    """

    def paginate(
        self,
        *,
        DetectorId: str,
        OnlyAssociated: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListMembersResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListMembers.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listmemberspaginator)
        """


class ListOrganizationAdminAccountsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListOrganizationAdminAccounts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listorganizationadminaccountspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListOrganizationAdminAccountsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListOrganizationAdminAccounts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listorganizationadminaccountspaginator)
        """


class ListThreatIntelSetsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListThreatIntelSets)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listthreatintelsetspaginator)
    """

    def paginate(
        self, *, DetectorId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListThreatIntelSetsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.43/reference/services/guardduty.html#GuardDuty.Paginator.ListThreatIntelSets.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_guardduty/paginators.html#listthreatintelsetspaginator)
        """
