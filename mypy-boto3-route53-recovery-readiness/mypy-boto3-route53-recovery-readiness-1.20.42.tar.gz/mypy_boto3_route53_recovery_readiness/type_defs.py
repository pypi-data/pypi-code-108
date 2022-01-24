"""
Type annotations for route53-recovery-readiness service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_route53_recovery_readiness/type_defs.html)

Usage::

    ```python
    from mypy_boto3_route53_recovery_readiness.type_defs import CellOutputTypeDef

    data: CellOutputTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import ReadinessType

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "CellOutputTypeDef",
    "CreateCellRequestRequestTypeDef",
    "CreateCellResponseTypeDef",
    "CreateCrossAccountAuthorizationRequestRequestTypeDef",
    "CreateCrossAccountAuthorizationResponseTypeDef",
    "CreateReadinessCheckRequestRequestTypeDef",
    "CreateReadinessCheckResponseTypeDef",
    "CreateRecoveryGroupRequestRequestTypeDef",
    "CreateRecoveryGroupResponseTypeDef",
    "CreateResourceSetRequestRequestTypeDef",
    "CreateResourceSetResponseTypeDef",
    "DNSTargetResourceTypeDef",
    "DeleteCellRequestRequestTypeDef",
    "DeleteCrossAccountAuthorizationRequestRequestTypeDef",
    "DeleteReadinessCheckRequestRequestTypeDef",
    "DeleteRecoveryGroupRequestRequestTypeDef",
    "DeleteResourceSetRequestRequestTypeDef",
    "GetArchitectureRecommendationsRequestRequestTypeDef",
    "GetArchitectureRecommendationsResponseTypeDef",
    "GetCellReadinessSummaryRequestRequestTypeDef",
    "GetCellReadinessSummaryResponseTypeDef",
    "GetCellRequestRequestTypeDef",
    "GetCellResponseTypeDef",
    "GetReadinessCheckRequestRequestTypeDef",
    "GetReadinessCheckResourceStatusRequestRequestTypeDef",
    "GetReadinessCheckResourceStatusResponseTypeDef",
    "GetReadinessCheckResponseTypeDef",
    "GetReadinessCheckStatusRequestRequestTypeDef",
    "GetReadinessCheckStatusResponseTypeDef",
    "GetRecoveryGroupReadinessSummaryRequestRequestTypeDef",
    "GetRecoveryGroupReadinessSummaryResponseTypeDef",
    "GetRecoveryGroupRequestRequestTypeDef",
    "GetRecoveryGroupResponseTypeDef",
    "GetResourceSetRequestRequestTypeDef",
    "GetResourceSetResponseTypeDef",
    "ListCellsRequestRequestTypeDef",
    "ListCellsResponseTypeDef",
    "ListCrossAccountAuthorizationsRequestRequestTypeDef",
    "ListCrossAccountAuthorizationsResponseTypeDef",
    "ListReadinessChecksRequestRequestTypeDef",
    "ListReadinessChecksResponseTypeDef",
    "ListRecoveryGroupsRequestRequestTypeDef",
    "ListRecoveryGroupsResponseTypeDef",
    "ListResourceSetsRequestRequestTypeDef",
    "ListResourceSetsResponseTypeDef",
    "ListRulesOutputTypeDef",
    "ListRulesRequestRequestTypeDef",
    "ListRulesResponseTypeDef",
    "ListTagsForResourcesRequestRequestTypeDef",
    "ListTagsForResourcesResponseTypeDef",
    "MessageTypeDef",
    "NLBResourceTypeDef",
    "PaginatorConfigTypeDef",
    "R53ResourceRecordTypeDef",
    "ReadinessCheckOutputTypeDef",
    "ReadinessCheckSummaryTypeDef",
    "RecommendationTypeDef",
    "RecoveryGroupOutputTypeDef",
    "ResourceResultTypeDef",
    "ResourceSetOutputTypeDef",
    "ResourceTypeDef",
    "ResponseMetadataTypeDef",
    "RuleResultTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TargetResourceTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateCellRequestRequestTypeDef",
    "UpdateCellResponseTypeDef",
    "UpdateReadinessCheckRequestRequestTypeDef",
    "UpdateReadinessCheckResponseTypeDef",
    "UpdateRecoveryGroupRequestRequestTypeDef",
    "UpdateRecoveryGroupResponseTypeDef",
    "UpdateResourceSetRequestRequestTypeDef",
    "UpdateResourceSetResponseTypeDef",
)

_RequiredCellOutputTypeDef = TypedDict(
    "_RequiredCellOutputTypeDef",
    {
        "CellArn": str,
        "CellName": str,
        "Cells": List[str],
        "ParentReadinessScopes": List[str],
    },
)
_OptionalCellOutputTypeDef = TypedDict(
    "_OptionalCellOutputTypeDef",
    {
        "Tags": Dict[str, str],
    },
    total=False,
)


class CellOutputTypeDef(_RequiredCellOutputTypeDef, _OptionalCellOutputTypeDef):
    pass


_RequiredCreateCellRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCellRequestRequestTypeDef",
    {
        "CellName": str,
    },
)
_OptionalCreateCellRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCellRequestRequestTypeDef",
    {
        "Cells": Sequence[str],
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateCellRequestRequestTypeDef(
    _RequiredCreateCellRequestRequestTypeDef, _OptionalCreateCellRequestRequestTypeDef
):
    pass


CreateCellResponseTypeDef = TypedDict(
    "CreateCellResponseTypeDef",
    {
        "CellArn": str,
        "CellName": str,
        "Cells": List[str],
        "ParentReadinessScopes": List[str],
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CreateCrossAccountAuthorizationRequestRequestTypeDef = TypedDict(
    "CreateCrossAccountAuthorizationRequestRequestTypeDef",
    {
        "CrossAccountAuthorization": str,
    },
)

CreateCrossAccountAuthorizationResponseTypeDef = TypedDict(
    "CreateCrossAccountAuthorizationResponseTypeDef",
    {
        "CrossAccountAuthorization": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateReadinessCheckRequestRequestTypeDef = TypedDict(
    "_RequiredCreateReadinessCheckRequestRequestTypeDef",
    {
        "ReadinessCheckName": str,
        "ResourceSetName": str,
    },
)
_OptionalCreateReadinessCheckRequestRequestTypeDef = TypedDict(
    "_OptionalCreateReadinessCheckRequestRequestTypeDef",
    {
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateReadinessCheckRequestRequestTypeDef(
    _RequiredCreateReadinessCheckRequestRequestTypeDef,
    _OptionalCreateReadinessCheckRequestRequestTypeDef,
):
    pass


CreateReadinessCheckResponseTypeDef = TypedDict(
    "CreateReadinessCheckResponseTypeDef",
    {
        "ReadinessCheckArn": str,
        "ReadinessCheckName": str,
        "ResourceSet": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateRecoveryGroupRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRecoveryGroupRequestRequestTypeDef",
    {
        "RecoveryGroupName": str,
    },
)
_OptionalCreateRecoveryGroupRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRecoveryGroupRequestRequestTypeDef",
    {
        "Cells": Sequence[str],
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateRecoveryGroupRequestRequestTypeDef(
    _RequiredCreateRecoveryGroupRequestRequestTypeDef,
    _OptionalCreateRecoveryGroupRequestRequestTypeDef,
):
    pass


CreateRecoveryGroupResponseTypeDef = TypedDict(
    "CreateRecoveryGroupResponseTypeDef",
    {
        "Cells": List[str],
        "RecoveryGroupArn": str,
        "RecoveryGroupName": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateResourceSetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateResourceSetRequestRequestTypeDef",
    {
        "ResourceSetName": str,
        "ResourceSetType": str,
        "Resources": Sequence["ResourceTypeDef"],
    },
)
_OptionalCreateResourceSetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateResourceSetRequestRequestTypeDef",
    {
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateResourceSetRequestRequestTypeDef(
    _RequiredCreateResourceSetRequestRequestTypeDef, _OptionalCreateResourceSetRequestRequestTypeDef
):
    pass


CreateResourceSetResponseTypeDef = TypedDict(
    "CreateResourceSetResponseTypeDef",
    {
        "ResourceSetArn": str,
        "ResourceSetName": str,
        "ResourceSetType": str,
        "Resources": List["ResourceTypeDef"],
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DNSTargetResourceTypeDef = TypedDict(
    "DNSTargetResourceTypeDef",
    {
        "DomainName": str,
        "HostedZoneArn": str,
        "RecordSetId": str,
        "RecordType": str,
        "TargetResource": "TargetResourceTypeDef",
    },
    total=False,
)

DeleteCellRequestRequestTypeDef = TypedDict(
    "DeleteCellRequestRequestTypeDef",
    {
        "CellName": str,
    },
)

DeleteCrossAccountAuthorizationRequestRequestTypeDef = TypedDict(
    "DeleteCrossAccountAuthorizationRequestRequestTypeDef",
    {
        "CrossAccountAuthorization": str,
    },
)

DeleteReadinessCheckRequestRequestTypeDef = TypedDict(
    "DeleteReadinessCheckRequestRequestTypeDef",
    {
        "ReadinessCheckName": str,
    },
)

DeleteRecoveryGroupRequestRequestTypeDef = TypedDict(
    "DeleteRecoveryGroupRequestRequestTypeDef",
    {
        "RecoveryGroupName": str,
    },
)

DeleteResourceSetRequestRequestTypeDef = TypedDict(
    "DeleteResourceSetRequestRequestTypeDef",
    {
        "ResourceSetName": str,
    },
)

_RequiredGetArchitectureRecommendationsRequestRequestTypeDef = TypedDict(
    "_RequiredGetArchitectureRecommendationsRequestRequestTypeDef",
    {
        "RecoveryGroupName": str,
    },
)
_OptionalGetArchitectureRecommendationsRequestRequestTypeDef = TypedDict(
    "_OptionalGetArchitectureRecommendationsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetArchitectureRecommendationsRequestRequestTypeDef(
    _RequiredGetArchitectureRecommendationsRequestRequestTypeDef,
    _OptionalGetArchitectureRecommendationsRequestRequestTypeDef,
):
    pass


GetArchitectureRecommendationsResponseTypeDef = TypedDict(
    "GetArchitectureRecommendationsResponseTypeDef",
    {
        "LastAuditTimestamp": datetime,
        "NextToken": str,
        "Recommendations": List["RecommendationTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetCellReadinessSummaryRequestRequestTypeDef = TypedDict(
    "_RequiredGetCellReadinessSummaryRequestRequestTypeDef",
    {
        "CellName": str,
    },
)
_OptionalGetCellReadinessSummaryRequestRequestTypeDef = TypedDict(
    "_OptionalGetCellReadinessSummaryRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetCellReadinessSummaryRequestRequestTypeDef(
    _RequiredGetCellReadinessSummaryRequestRequestTypeDef,
    _OptionalGetCellReadinessSummaryRequestRequestTypeDef,
):
    pass


GetCellReadinessSummaryResponseTypeDef = TypedDict(
    "GetCellReadinessSummaryResponseTypeDef",
    {
        "NextToken": str,
        "Readiness": ReadinessType,
        "ReadinessChecks": List["ReadinessCheckSummaryTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetCellRequestRequestTypeDef = TypedDict(
    "GetCellRequestRequestTypeDef",
    {
        "CellName": str,
    },
)

GetCellResponseTypeDef = TypedDict(
    "GetCellResponseTypeDef",
    {
        "CellArn": str,
        "CellName": str,
        "Cells": List[str],
        "ParentReadinessScopes": List[str],
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReadinessCheckRequestRequestTypeDef = TypedDict(
    "GetReadinessCheckRequestRequestTypeDef",
    {
        "ReadinessCheckName": str,
    },
)

_RequiredGetReadinessCheckResourceStatusRequestRequestTypeDef = TypedDict(
    "_RequiredGetReadinessCheckResourceStatusRequestRequestTypeDef",
    {
        "ReadinessCheckName": str,
        "ResourceIdentifier": str,
    },
)
_OptionalGetReadinessCheckResourceStatusRequestRequestTypeDef = TypedDict(
    "_OptionalGetReadinessCheckResourceStatusRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetReadinessCheckResourceStatusRequestRequestTypeDef(
    _RequiredGetReadinessCheckResourceStatusRequestRequestTypeDef,
    _OptionalGetReadinessCheckResourceStatusRequestRequestTypeDef,
):
    pass


GetReadinessCheckResourceStatusResponseTypeDef = TypedDict(
    "GetReadinessCheckResourceStatusResponseTypeDef",
    {
        "NextToken": str,
        "Readiness": ReadinessType,
        "Rules": List["RuleResultTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetReadinessCheckResponseTypeDef = TypedDict(
    "GetReadinessCheckResponseTypeDef",
    {
        "ReadinessCheckArn": str,
        "ReadinessCheckName": str,
        "ResourceSet": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetReadinessCheckStatusRequestRequestTypeDef = TypedDict(
    "_RequiredGetReadinessCheckStatusRequestRequestTypeDef",
    {
        "ReadinessCheckName": str,
    },
)
_OptionalGetReadinessCheckStatusRequestRequestTypeDef = TypedDict(
    "_OptionalGetReadinessCheckStatusRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetReadinessCheckStatusRequestRequestTypeDef(
    _RequiredGetReadinessCheckStatusRequestRequestTypeDef,
    _OptionalGetReadinessCheckStatusRequestRequestTypeDef,
):
    pass


GetReadinessCheckStatusResponseTypeDef = TypedDict(
    "GetReadinessCheckStatusResponseTypeDef",
    {
        "Messages": List["MessageTypeDef"],
        "NextToken": str,
        "Readiness": ReadinessType,
        "Resources": List["ResourceResultTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetRecoveryGroupReadinessSummaryRequestRequestTypeDef = TypedDict(
    "_RequiredGetRecoveryGroupReadinessSummaryRequestRequestTypeDef",
    {
        "RecoveryGroupName": str,
    },
)
_OptionalGetRecoveryGroupReadinessSummaryRequestRequestTypeDef = TypedDict(
    "_OptionalGetRecoveryGroupReadinessSummaryRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetRecoveryGroupReadinessSummaryRequestRequestTypeDef(
    _RequiredGetRecoveryGroupReadinessSummaryRequestRequestTypeDef,
    _OptionalGetRecoveryGroupReadinessSummaryRequestRequestTypeDef,
):
    pass


GetRecoveryGroupReadinessSummaryResponseTypeDef = TypedDict(
    "GetRecoveryGroupReadinessSummaryResponseTypeDef",
    {
        "NextToken": str,
        "Readiness": ReadinessType,
        "ReadinessChecks": List["ReadinessCheckSummaryTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetRecoveryGroupRequestRequestTypeDef = TypedDict(
    "GetRecoveryGroupRequestRequestTypeDef",
    {
        "RecoveryGroupName": str,
    },
)

GetRecoveryGroupResponseTypeDef = TypedDict(
    "GetRecoveryGroupResponseTypeDef",
    {
        "Cells": List[str],
        "RecoveryGroupArn": str,
        "RecoveryGroupName": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetResourceSetRequestRequestTypeDef = TypedDict(
    "GetResourceSetRequestRequestTypeDef",
    {
        "ResourceSetName": str,
    },
)

GetResourceSetResponseTypeDef = TypedDict(
    "GetResourceSetResponseTypeDef",
    {
        "ResourceSetArn": str,
        "ResourceSetName": str,
        "ResourceSetType": str,
        "Resources": List["ResourceTypeDef"],
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListCellsRequestRequestTypeDef = TypedDict(
    "ListCellsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListCellsResponseTypeDef = TypedDict(
    "ListCellsResponseTypeDef",
    {
        "Cells": List["CellOutputTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListCrossAccountAuthorizationsRequestRequestTypeDef = TypedDict(
    "ListCrossAccountAuthorizationsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListCrossAccountAuthorizationsResponseTypeDef = TypedDict(
    "ListCrossAccountAuthorizationsResponseTypeDef",
    {
        "CrossAccountAuthorizations": List[str],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListReadinessChecksRequestRequestTypeDef = TypedDict(
    "ListReadinessChecksRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListReadinessChecksResponseTypeDef = TypedDict(
    "ListReadinessChecksResponseTypeDef",
    {
        "NextToken": str,
        "ReadinessChecks": List["ReadinessCheckOutputTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListRecoveryGroupsRequestRequestTypeDef = TypedDict(
    "ListRecoveryGroupsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListRecoveryGroupsResponseTypeDef = TypedDict(
    "ListRecoveryGroupsResponseTypeDef",
    {
        "NextToken": str,
        "RecoveryGroups": List["RecoveryGroupOutputTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListResourceSetsRequestRequestTypeDef = TypedDict(
    "ListResourceSetsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListResourceSetsResponseTypeDef = TypedDict(
    "ListResourceSetsResponseTypeDef",
    {
        "NextToken": str,
        "ResourceSets": List["ResourceSetOutputTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListRulesOutputTypeDef = TypedDict(
    "ListRulesOutputTypeDef",
    {
        "ResourceType": str,
        "RuleDescription": str,
        "RuleId": str,
    },
)

ListRulesRequestRequestTypeDef = TypedDict(
    "ListRulesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "ResourceType": str,
    },
    total=False,
)

ListRulesResponseTypeDef = TypedDict(
    "ListRulesResponseTypeDef",
    {
        "NextToken": str,
        "Rules": List["ListRulesOutputTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListTagsForResourcesRequestRequestTypeDef = TypedDict(
    "ListTagsForResourcesRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

ListTagsForResourcesResponseTypeDef = TypedDict(
    "ListTagsForResourcesResponseTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

MessageTypeDef = TypedDict(
    "MessageTypeDef",
    {
        "MessageText": str,
    },
    total=False,
)

NLBResourceTypeDef = TypedDict(
    "NLBResourceTypeDef",
    {
        "Arn": str,
    },
    total=False,
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

R53ResourceRecordTypeDef = TypedDict(
    "R53ResourceRecordTypeDef",
    {
        "DomainName": str,
        "RecordSetId": str,
    },
    total=False,
)

_RequiredReadinessCheckOutputTypeDef = TypedDict(
    "_RequiredReadinessCheckOutputTypeDef",
    {
        "ReadinessCheckArn": str,
        "ResourceSet": str,
    },
)
_OptionalReadinessCheckOutputTypeDef = TypedDict(
    "_OptionalReadinessCheckOutputTypeDef",
    {
        "ReadinessCheckName": str,
        "Tags": Dict[str, str],
    },
    total=False,
)


class ReadinessCheckOutputTypeDef(
    _RequiredReadinessCheckOutputTypeDef, _OptionalReadinessCheckOutputTypeDef
):
    pass


ReadinessCheckSummaryTypeDef = TypedDict(
    "ReadinessCheckSummaryTypeDef",
    {
        "Readiness": ReadinessType,
        "ReadinessCheckName": str,
    },
    total=False,
)

RecommendationTypeDef = TypedDict(
    "RecommendationTypeDef",
    {
        "RecommendationText": str,
    },
)

_RequiredRecoveryGroupOutputTypeDef = TypedDict(
    "_RequiredRecoveryGroupOutputTypeDef",
    {
        "Cells": List[str],
        "RecoveryGroupArn": str,
        "RecoveryGroupName": str,
    },
)
_OptionalRecoveryGroupOutputTypeDef = TypedDict(
    "_OptionalRecoveryGroupOutputTypeDef",
    {
        "Tags": Dict[str, str],
    },
    total=False,
)


class RecoveryGroupOutputTypeDef(
    _RequiredRecoveryGroupOutputTypeDef, _OptionalRecoveryGroupOutputTypeDef
):
    pass


_RequiredResourceResultTypeDef = TypedDict(
    "_RequiredResourceResultTypeDef",
    {
        "LastCheckedTimestamp": datetime,
        "Readiness": ReadinessType,
    },
)
_OptionalResourceResultTypeDef = TypedDict(
    "_OptionalResourceResultTypeDef",
    {
        "ComponentId": str,
        "ResourceArn": str,
    },
    total=False,
)


class ResourceResultTypeDef(_RequiredResourceResultTypeDef, _OptionalResourceResultTypeDef):
    pass


_RequiredResourceSetOutputTypeDef = TypedDict(
    "_RequiredResourceSetOutputTypeDef",
    {
        "ResourceSetArn": str,
        "ResourceSetName": str,
        "ResourceSetType": str,
        "Resources": List["ResourceTypeDef"],
    },
)
_OptionalResourceSetOutputTypeDef = TypedDict(
    "_OptionalResourceSetOutputTypeDef",
    {
        "Tags": Dict[str, str],
    },
    total=False,
)


class ResourceSetOutputTypeDef(
    _RequiredResourceSetOutputTypeDef, _OptionalResourceSetOutputTypeDef
):
    pass


ResourceTypeDef = TypedDict(
    "ResourceTypeDef",
    {
        "ComponentId": str,
        "DnsTargetResource": "DNSTargetResourceTypeDef",
        "ReadinessScopes": Sequence[str],
        "ResourceArn": str,
    },
    total=False,
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

RuleResultTypeDef = TypedDict(
    "RuleResultTypeDef",
    {
        "LastCheckedTimestamp": datetime,
        "Messages": List["MessageTypeDef"],
        "Readiness": ReadinessType,
        "RuleId": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Mapping[str, str],
    },
)

TargetResourceTypeDef = TypedDict(
    "TargetResourceTypeDef",
    {
        "NLBResource": "NLBResourceTypeDef",
        "R53Resource": "R53ResourceRecordTypeDef",
    },
    total=False,
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

UpdateCellRequestRequestTypeDef = TypedDict(
    "UpdateCellRequestRequestTypeDef",
    {
        "CellName": str,
        "Cells": Sequence[str],
    },
)

UpdateCellResponseTypeDef = TypedDict(
    "UpdateCellResponseTypeDef",
    {
        "CellArn": str,
        "CellName": str,
        "Cells": List[str],
        "ParentReadinessScopes": List[str],
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateReadinessCheckRequestRequestTypeDef = TypedDict(
    "UpdateReadinessCheckRequestRequestTypeDef",
    {
        "ReadinessCheckName": str,
        "ResourceSetName": str,
    },
)

UpdateReadinessCheckResponseTypeDef = TypedDict(
    "UpdateReadinessCheckResponseTypeDef",
    {
        "ReadinessCheckArn": str,
        "ReadinessCheckName": str,
        "ResourceSet": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateRecoveryGroupRequestRequestTypeDef = TypedDict(
    "UpdateRecoveryGroupRequestRequestTypeDef",
    {
        "Cells": Sequence[str],
        "RecoveryGroupName": str,
    },
)

UpdateRecoveryGroupResponseTypeDef = TypedDict(
    "UpdateRecoveryGroupResponseTypeDef",
    {
        "Cells": List[str],
        "RecoveryGroupArn": str,
        "RecoveryGroupName": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateResourceSetRequestRequestTypeDef = TypedDict(
    "UpdateResourceSetRequestRequestTypeDef",
    {
        "ResourceSetName": str,
        "ResourceSetType": str,
        "Resources": Sequence["ResourceTypeDef"],
    },
)

UpdateResourceSetResponseTypeDef = TypedDict(
    "UpdateResourceSetResponseTypeDef",
    {
        "ResourceSetArn": str,
        "ResourceSetName": str,
        "ResourceSetType": str,
        "Resources": List["ResourceTypeDef"],
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)
