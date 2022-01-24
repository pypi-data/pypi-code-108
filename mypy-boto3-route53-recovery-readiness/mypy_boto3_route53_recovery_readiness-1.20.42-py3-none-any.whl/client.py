"""
Type annotations for route53-recovery-readiness service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_route53_recovery_readiness import Route53RecoveryReadinessClient

    client: Route53RecoveryReadinessClient = boto3.client("route53-recovery-readiness")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

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
from .type_defs import (
    CreateCellResponseTypeDef,
    CreateCrossAccountAuthorizationResponseTypeDef,
    CreateReadinessCheckResponseTypeDef,
    CreateRecoveryGroupResponseTypeDef,
    CreateResourceSetResponseTypeDef,
    GetArchitectureRecommendationsResponseTypeDef,
    GetCellReadinessSummaryResponseTypeDef,
    GetCellResponseTypeDef,
    GetReadinessCheckResourceStatusResponseTypeDef,
    GetReadinessCheckResponseTypeDef,
    GetReadinessCheckStatusResponseTypeDef,
    GetRecoveryGroupReadinessSummaryResponseTypeDef,
    GetRecoveryGroupResponseTypeDef,
    GetResourceSetResponseTypeDef,
    ListCellsResponseTypeDef,
    ListCrossAccountAuthorizationsResponseTypeDef,
    ListReadinessChecksResponseTypeDef,
    ListRecoveryGroupsResponseTypeDef,
    ListResourceSetsResponseTypeDef,
    ListRulesResponseTypeDef,
    ListTagsForResourcesResponseTypeDef,
    ResourceTypeDef,
    UpdateCellResponseTypeDef,
    UpdateReadinessCheckResponseTypeDef,
    UpdateRecoveryGroupResponseTypeDef,
    UpdateResourceSetResponseTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("Route53RecoveryReadinessClient",)


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
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class Route53RecoveryReadinessClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        Route53RecoveryReadinessClient exceptions.
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#can_paginate)
        """

    def create_cell(
        self, *, CellName: str, Cells: Sequence[str] = ..., Tags: Mapping[str, str] = ...
    ) -> CreateCellResponseTypeDef:
        """
        Creates a cell in an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.create_cell)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#create_cell)
        """

    def create_cross_account_authorization(
        self, *, CrossAccountAuthorization: str
    ) -> CreateCrossAccountAuthorizationResponseTypeDef:
        """
        Creates a cross-account readiness authorization.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.create_cross_account_authorization)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#create_cross_account_authorization)
        """

    def create_readiness_check(
        self, *, ReadinessCheckName: str, ResourceSetName: str, Tags: Mapping[str, str] = ...
    ) -> CreateReadinessCheckResponseTypeDef:
        """
        Creates a readiness check in an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.create_readiness_check)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#create_readiness_check)
        """

    def create_recovery_group(
        self, *, RecoveryGroupName: str, Cells: Sequence[str] = ..., Tags: Mapping[str, str] = ...
    ) -> CreateRecoveryGroupResponseTypeDef:
        """
        Creates a recovery group in an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.create_recovery_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#create_recovery_group)
        """

    def create_resource_set(
        self,
        *,
        ResourceSetName: str,
        ResourceSetType: str,
        Resources: Sequence["ResourceTypeDef"],
        Tags: Mapping[str, str] = ...
    ) -> CreateResourceSetResponseTypeDef:
        """
        Creates a resource set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.create_resource_set)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#create_resource_set)
        """

    def delete_cell(self, *, CellName: str) -> None:
        """
        Delete a cell.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.delete_cell)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#delete_cell)
        """

    def delete_cross_account_authorization(
        self, *, CrossAccountAuthorization: str
    ) -> Dict[str, Any]:
        """
        Deletes cross account readiness authorization.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.delete_cross_account_authorization)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#delete_cross_account_authorization)
        """

    def delete_readiness_check(self, *, ReadinessCheckName: str) -> None:
        """
        Deletes a readiness check.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.delete_readiness_check)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#delete_readiness_check)
        """

    def delete_recovery_group(self, *, RecoveryGroupName: str) -> None:
        """
        Deletes a recovery group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.delete_recovery_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#delete_recovery_group)
        """

    def delete_resource_set(self, *, ResourceSetName: str) -> None:
        """
        Deletes a resource set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.delete_resource_set)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#delete_resource_set)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#generate_presigned_url)
        """

    def get_architecture_recommendations(
        self, *, RecoveryGroupName: str, MaxResults: int = ..., NextToken: str = ...
    ) -> GetArchitectureRecommendationsResponseTypeDef:
        """
        Gets recommendations about architecture designs for improving resiliency for an
        application, based on a recovery group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_architecture_recommendations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_architecture_recommendations)
        """

    def get_cell(self, *, CellName: str) -> GetCellResponseTypeDef:
        """
        Gets information about a cell including cell name, cell Amazon Resource Name
        (ARN), ARNs of nested cells for this cell, and a list of those cell ARNs with
        their associated recovery group ARNs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_cell)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_cell)
        """

    def get_cell_readiness_summary(
        self, *, CellName: str, MaxResults: int = ..., NextToken: str = ...
    ) -> GetCellReadinessSummaryResponseTypeDef:
        """
        Gets readiness for a cell.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_cell_readiness_summary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_cell_readiness_summary)
        """

    def get_readiness_check(self, *, ReadinessCheckName: str) -> GetReadinessCheckResponseTypeDef:
        """
        Gets details about a readiness check.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_readiness_check)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_readiness_check)
        """

    def get_readiness_check_resource_status(
        self,
        *,
        ReadinessCheckName: str,
        ResourceIdentifier: str,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> GetReadinessCheckResourceStatusResponseTypeDef:
        """
        Gets individual readiness status for a readiness check.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_readiness_check_resource_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_readiness_check_resource_status)
        """

    def get_readiness_check_status(
        self, *, ReadinessCheckName: str, MaxResults: int = ..., NextToken: str = ...
    ) -> GetReadinessCheckStatusResponseTypeDef:
        """
        Gets the readiness status for an individual readiness check.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_readiness_check_status)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_readiness_check_status)
        """

    def get_recovery_group(self, *, RecoveryGroupName: str) -> GetRecoveryGroupResponseTypeDef:
        """
        Gets details about a recovery group, including a list of the cells that are
        included in it.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_recovery_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_recovery_group)
        """

    def get_recovery_group_readiness_summary(
        self, *, RecoveryGroupName: str, MaxResults: int = ..., NextToken: str = ...
    ) -> GetRecoveryGroupReadinessSummaryResponseTypeDef:
        """
        Displays a summary of information about a recovery group's readiness status.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_recovery_group_readiness_summary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_recovery_group_readiness_summary)
        """

    def get_resource_set(self, *, ResourceSetName: str) -> GetResourceSetResponseTypeDef:
        """
        Displays the details about a resource set, including a list of the resources in
        the set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.get_resource_set)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#get_resource_set)
        """

    def list_cells(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListCellsResponseTypeDef:
        """
        Lists the cells for an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_cells)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_cells)
        """

    def list_cross_account_authorizations(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListCrossAccountAuthorizationsResponseTypeDef:
        """
        Lists the cross-account readiness authorizations that are in place for an
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_cross_account_authorizations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_cross_account_authorizations)
        """

    def list_readiness_checks(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListReadinessChecksResponseTypeDef:
        """
        Lists the readiness checks for an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_readiness_checks)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_readiness_checks)
        """

    def list_recovery_groups(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListRecoveryGroupsResponseTypeDef:
        """
        Lists the recovery groups in an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_recovery_groups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_recovery_groups)
        """

    def list_resource_sets(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListResourceSetsResponseTypeDef:
        """
        Lists the resource sets in an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_resource_sets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_resource_sets)
        """

    def list_rules(
        self, *, MaxResults: int = ..., NextToken: str = ..., ResourceType: str = ...
    ) -> ListRulesResponseTypeDef:
        """
        Lists all readiness rules, or lists the readiness rules for a specific resource
        type.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_rules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_rules)
        """

    def list_tags_for_resources(self, *, ResourceArn: str) -> ListTagsForResourcesResponseTypeDef:
        """
        Lists the tags for a resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.list_tags_for_resources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#list_tags_for_resources)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds a tag to a resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> None:
        """
        Removes a tag from a resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#untag_resource)
        """

    def update_cell(self, *, CellName: str, Cells: Sequence[str]) -> UpdateCellResponseTypeDef:
        """
        Updates a cell to replace the list of nested cells with a new list of nested
        cells.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.update_cell)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#update_cell)
        """

    def update_readiness_check(
        self, *, ReadinessCheckName: str, ResourceSetName: str
    ) -> UpdateReadinessCheckResponseTypeDef:
        """
        Updates a readiness check.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.update_readiness_check)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#update_readiness_check)
        """

    def update_recovery_group(
        self, *, Cells: Sequence[str], RecoveryGroupName: str
    ) -> UpdateRecoveryGroupResponseTypeDef:
        """
        Updates a recovery group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.update_recovery_group)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#update_recovery_group)
        """

    def update_resource_set(
        self, *, ResourceSetName: str, ResourceSetType: str, Resources: Sequence["ResourceTypeDef"]
    ) -> UpdateResourceSetResponseTypeDef:
        """
        Updates a resource set.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Client.update_resource_set)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/client.html#update_resource_set)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["get_cell_readiness_summary"]
    ) -> GetCellReadinessSummaryPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.GetCellReadinessSummary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#getcellreadinesssummarypaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["get_readiness_check_resource_status"]
    ) -> GetReadinessCheckResourceStatusPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.GetReadinessCheckResourceStatus)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#getreadinesscheckresourcestatuspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["get_readiness_check_status"]
    ) -> GetReadinessCheckStatusPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.GetReadinessCheckStatus)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#getreadinesscheckstatuspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["get_recovery_group_readiness_summary"]
    ) -> GetRecoveryGroupReadinessSummaryPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.GetRecoveryGroupReadinessSummary)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#getrecoverygroupreadinesssummarypaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_cells"]) -> ListCellsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.ListCells)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#listcellspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_cross_account_authorizations"]
    ) -> ListCrossAccountAuthorizationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.ListCrossAccountAuthorizations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#listcrossaccountauthorizationspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_readiness_checks"]
    ) -> ListReadinessChecksPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.ListReadinessChecks)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#listreadinesscheckspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_recovery_groups"]
    ) -> ListRecoveryGroupsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.ListRecoveryGroups)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#listrecoverygroupspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_resource_sets"]
    ) -> ListResourceSetsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.ListResourceSets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#listresourcesetspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_rules"]) -> ListRulesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness.Paginator.ListRules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/paginators.html#listrulespaginator)
        """
