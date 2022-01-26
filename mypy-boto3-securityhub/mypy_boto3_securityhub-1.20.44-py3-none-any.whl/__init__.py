"""
Main interface for securityhub service.

Usage::

    ```python
    import boto3
    from mypy_boto3_securityhub import (
        Client,
        DescribeActionTargetsPaginator,
        DescribeProductsPaginator,
        DescribeStandardsControlsPaginator,
        DescribeStandardsPaginator,
        GetEnabledStandardsPaginator,
        GetFindingsPaginator,
        GetInsightsPaginator,
        ListEnabledProductsForImportPaginator,
        ListFindingAggregatorsPaginator,
        ListInvitationsPaginator,
        ListMembersPaginator,
        ListOrganizationAdminAccountsPaginator,
        SecurityHubClient,
    )

    session = boto3.Session()

    client: SecurityHubClient = boto3.client("securityhub")
    session_client: SecurityHubClient = session.client("securityhub")

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
from .client import SecurityHubClient
from .paginator import (
    DescribeActionTargetsPaginator,
    DescribeProductsPaginator,
    DescribeStandardsControlsPaginator,
    DescribeStandardsPaginator,
    GetEnabledStandardsPaginator,
    GetFindingsPaginator,
    GetInsightsPaginator,
    ListEnabledProductsForImportPaginator,
    ListFindingAggregatorsPaginator,
    ListInvitationsPaginator,
    ListMembersPaginator,
    ListOrganizationAdminAccountsPaginator,
)

Client = SecurityHubClient


__all__ = (
    "Client",
    "DescribeActionTargetsPaginator",
    "DescribeProductsPaginator",
    "DescribeStandardsControlsPaginator",
    "DescribeStandardsPaginator",
    "GetEnabledStandardsPaginator",
    "GetFindingsPaginator",
    "GetInsightsPaginator",
    "ListEnabledProductsForImportPaginator",
    "ListFindingAggregatorsPaginator",
    "ListInvitationsPaginator",
    "ListMembersPaginator",
    "ListOrganizationAdminAccountsPaginator",
    "SecurityHubClient",
)
