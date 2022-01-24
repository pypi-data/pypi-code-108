"""
Main interface for route53-recovery-readiness service.

Usage::

    ```python
    import boto3
    from mypy_boto3_route53_recovery_readiness import (
        Client,
        GetCellReadinessSummaryPaginator,
        GetReadinessCheckResourceStatusPaginator,
        GetReadinessCheckStatusPaginator,
        GetRecoveryGroupReadinessSummaryPaginator,
        ListCellsPaginator,
        ListCrossAccountAuthorizationsPaginator,
        ListReadinessChecksPaginator,
        ListRecoveryGroupsPaginator,
        ListResourceSetsPaginator,
        ListRulesPaginator,
        Route53RecoveryReadinessClient,
    )

    session = boto3.Session()

    client: Route53RecoveryReadinessClient = boto3.client("route53-recovery-readiness")
    session_client: Route53RecoveryReadinessClient = session.client("route53-recovery-readiness")

    get_cell_readiness_summary_paginator: GetCellReadinessSummaryPaginator = client.get_paginator("get_cell_readiness_summary")
    get_readiness_check_resource_status_paginator: GetReadinessCheckResourceStatusPaginator = client.get_paginator("get_readiness_check_resource_status")
    get_readiness_check_status_paginator: GetReadinessCheckStatusPaginator = client.get_paginator("get_readiness_check_status")
    get_recovery_group_readiness_summary_paginator: GetRecoveryGroupReadinessSummaryPaginator = client.get_paginator("get_recovery_group_readiness_summary")
    list_cells_paginator: ListCellsPaginator = client.get_paginator("list_cells")
    list_cross_account_authorizations_paginator: ListCrossAccountAuthorizationsPaginator = client.get_paginator("list_cross_account_authorizations")
    list_readiness_checks_paginator: ListReadinessChecksPaginator = client.get_paginator("list_readiness_checks")
    list_recovery_groups_paginator: ListRecoveryGroupsPaginator = client.get_paginator("list_recovery_groups")
    list_resource_sets_paginator: ListResourceSetsPaginator = client.get_paginator("list_resource_sets")
    list_rules_paginator: ListRulesPaginator = client.get_paginator("list_rules")
    ```
"""
from .client import Route53RecoveryReadinessClient
from .paginator import (
    GetCellReadinessSummaryPaginator,
    GetReadinessCheckResourceStatusPaginator,
    GetReadinessCheckStatusPaginator,
    GetRecoveryGroupReadinessSummaryPaginator,
    ListCellsPaginator,
    ListCrossAccountAuthorizationsPaginator,
    ListReadinessChecksPaginator,
    ListRecoveryGroupsPaginator,
    ListResourceSetsPaginator,
    ListRulesPaginator,
)

Client = Route53RecoveryReadinessClient


__all__ = (
    "Client",
    "GetCellReadinessSummaryPaginator",
    "GetReadinessCheckResourceStatusPaginator",
    "GetReadinessCheckStatusPaginator",
    "GetRecoveryGroupReadinessSummaryPaginator",
    "ListCellsPaginator",
    "ListCrossAccountAuthorizationsPaginator",
    "ListReadinessChecksPaginator",
    "ListRecoveryGroupsPaginator",
    "ListResourceSetsPaginator",
    "ListRulesPaginator",
    "Route53RecoveryReadinessClient",
)
