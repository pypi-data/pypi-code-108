"""
Type annotations for codeguru-reviewer service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_codeguru_reviewer/type_defs.html)

Usage::

    ```python
    from mypy_boto3_codeguru_reviewer.type_defs import AssociateRepositoryRequestRequestTypeDef

    data: AssociateRepositoryRequestRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AnalysisTypeType,
    EncryptionOptionType,
    JobStateType,
    ProviderTypeType,
    ReactionType,
    RecommendationCategoryType,
    RepositoryAssociationStateType,
    SeverityType,
    TypeType,
    VendorNameType,
)

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AssociateRepositoryRequestRequestTypeDef",
    "AssociateRepositoryResponseTypeDef",
    "BranchDiffSourceCodeTypeTypeDef",
    "CodeArtifactsTypeDef",
    "CodeCommitRepositoryTypeDef",
    "CodeReviewSummaryTypeDef",
    "CodeReviewTypeDef",
    "CodeReviewTypeTypeDef",
    "CommitDiffSourceCodeTypeTypeDef",
    "CreateCodeReviewRequestRequestTypeDef",
    "CreateCodeReviewResponseTypeDef",
    "DescribeCodeReviewRequestRequestTypeDef",
    "DescribeCodeReviewResponseTypeDef",
    "DescribeRecommendationFeedbackRequestRequestTypeDef",
    "DescribeRecommendationFeedbackResponseTypeDef",
    "DescribeRepositoryAssociationRequestRequestTypeDef",
    "DescribeRepositoryAssociationResponseTypeDef",
    "DisassociateRepositoryRequestRequestTypeDef",
    "DisassociateRepositoryResponseTypeDef",
    "EventInfoTypeDef",
    "KMSKeyDetailsTypeDef",
    "ListCodeReviewsRequestRequestTypeDef",
    "ListCodeReviewsResponseTypeDef",
    "ListRecommendationFeedbackRequestRequestTypeDef",
    "ListRecommendationFeedbackResponseTypeDef",
    "ListRecommendationsRequestRequestTypeDef",
    "ListRecommendationsResponseTypeDef",
    "ListRepositoryAssociationsRequestRequestTypeDef",
    "ListRepositoryAssociationsResponseTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "MetricsSummaryTypeDef",
    "MetricsTypeDef",
    "PaginatorConfigTypeDef",
    "PutRecommendationFeedbackRequestRequestTypeDef",
    "RecommendationFeedbackSummaryTypeDef",
    "RecommendationFeedbackTypeDef",
    "RecommendationSummaryTypeDef",
    "RepositoryAnalysisTypeDef",
    "RepositoryAssociationSummaryTypeDef",
    "RepositoryAssociationTypeDef",
    "RepositoryHeadSourceCodeTypeTypeDef",
    "RepositoryTypeDef",
    "RequestMetadataTypeDef",
    "ResponseMetadataTypeDef",
    "RuleMetadataTypeDef",
    "S3BucketRepositoryTypeDef",
    "S3RepositoryDetailsTypeDef",
    "S3RepositoryTypeDef",
    "SourceCodeTypeTypeDef",
    "TagResourceRequestRequestTypeDef",
    "ThirdPartySourceRepositoryTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "WaiterConfigTypeDef",
)

_RequiredAssociateRepositoryRequestRequestTypeDef = TypedDict(
    "_RequiredAssociateRepositoryRequestRequestTypeDef",
    {
        "Repository": "RepositoryTypeDef",
    },
)
_OptionalAssociateRepositoryRequestRequestTypeDef = TypedDict(
    "_OptionalAssociateRepositoryRequestRequestTypeDef",
    {
        "ClientRequestToken": str,
        "Tags": Mapping[str, str],
        "KMSKeyDetails": "KMSKeyDetailsTypeDef",
    },
    total=False,
)


class AssociateRepositoryRequestRequestTypeDef(
    _RequiredAssociateRepositoryRequestRequestTypeDef,
    _OptionalAssociateRepositoryRequestRequestTypeDef,
):
    pass


AssociateRepositoryResponseTypeDef = TypedDict(
    "AssociateRepositoryResponseTypeDef",
    {
        "RepositoryAssociation": "RepositoryAssociationTypeDef",
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

BranchDiffSourceCodeTypeTypeDef = TypedDict(
    "BranchDiffSourceCodeTypeTypeDef",
    {
        "SourceBranchName": str,
        "DestinationBranchName": str,
    },
)

_RequiredCodeArtifactsTypeDef = TypedDict(
    "_RequiredCodeArtifactsTypeDef",
    {
        "SourceCodeArtifactsObjectKey": str,
    },
)
_OptionalCodeArtifactsTypeDef = TypedDict(
    "_OptionalCodeArtifactsTypeDef",
    {
        "BuildArtifactsObjectKey": str,
    },
    total=False,
)


class CodeArtifactsTypeDef(_RequiredCodeArtifactsTypeDef, _OptionalCodeArtifactsTypeDef):
    pass


CodeCommitRepositoryTypeDef = TypedDict(
    "CodeCommitRepositoryTypeDef",
    {
        "Name": str,
    },
)

CodeReviewSummaryTypeDef = TypedDict(
    "CodeReviewSummaryTypeDef",
    {
        "Name": str,
        "CodeReviewArn": str,
        "RepositoryName": str,
        "Owner": str,
        "ProviderType": ProviderTypeType,
        "State": JobStateType,
        "CreatedTimeStamp": datetime,
        "LastUpdatedTimeStamp": datetime,
        "Type": TypeType,
        "PullRequestId": str,
        "MetricsSummary": "MetricsSummaryTypeDef",
        "SourceCodeType": "SourceCodeTypeTypeDef",
    },
    total=False,
)

CodeReviewTypeDef = TypedDict(
    "CodeReviewTypeDef",
    {
        "Name": str,
        "CodeReviewArn": str,
        "RepositoryName": str,
        "Owner": str,
        "ProviderType": ProviderTypeType,
        "State": JobStateType,
        "StateReason": str,
        "CreatedTimeStamp": datetime,
        "LastUpdatedTimeStamp": datetime,
        "Type": TypeType,
        "PullRequestId": str,
        "SourceCodeType": "SourceCodeTypeTypeDef",
        "AssociationArn": str,
        "Metrics": "MetricsTypeDef",
        "AnalysisTypes": List[AnalysisTypeType],
    },
    total=False,
)

_RequiredCodeReviewTypeTypeDef = TypedDict(
    "_RequiredCodeReviewTypeTypeDef",
    {
        "RepositoryAnalysis": "RepositoryAnalysisTypeDef",
    },
)
_OptionalCodeReviewTypeTypeDef = TypedDict(
    "_OptionalCodeReviewTypeTypeDef",
    {
        "AnalysisTypes": Sequence[AnalysisTypeType],
    },
    total=False,
)


class CodeReviewTypeTypeDef(_RequiredCodeReviewTypeTypeDef, _OptionalCodeReviewTypeTypeDef):
    pass


CommitDiffSourceCodeTypeTypeDef = TypedDict(
    "CommitDiffSourceCodeTypeTypeDef",
    {
        "SourceCommit": str,
        "DestinationCommit": str,
        "MergeBaseCommit": str,
    },
    total=False,
)

_RequiredCreateCodeReviewRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCodeReviewRequestRequestTypeDef",
    {
        "Name": str,
        "RepositoryAssociationArn": str,
        "Type": "CodeReviewTypeTypeDef",
    },
)
_OptionalCreateCodeReviewRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCodeReviewRequestRequestTypeDef",
    {
        "ClientRequestToken": str,
    },
    total=False,
)


class CreateCodeReviewRequestRequestTypeDef(
    _RequiredCreateCodeReviewRequestRequestTypeDef, _OptionalCreateCodeReviewRequestRequestTypeDef
):
    pass


CreateCodeReviewResponseTypeDef = TypedDict(
    "CreateCodeReviewResponseTypeDef",
    {
        "CodeReview": "CodeReviewTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeCodeReviewRequestRequestTypeDef = TypedDict(
    "DescribeCodeReviewRequestRequestTypeDef",
    {
        "CodeReviewArn": str,
    },
)

DescribeCodeReviewResponseTypeDef = TypedDict(
    "DescribeCodeReviewResponseTypeDef",
    {
        "CodeReview": "CodeReviewTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDescribeRecommendationFeedbackRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeRecommendationFeedbackRequestRequestTypeDef",
    {
        "CodeReviewArn": str,
        "RecommendationId": str,
    },
)
_OptionalDescribeRecommendationFeedbackRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeRecommendationFeedbackRequestRequestTypeDef",
    {
        "UserId": str,
    },
    total=False,
)


class DescribeRecommendationFeedbackRequestRequestTypeDef(
    _RequiredDescribeRecommendationFeedbackRequestRequestTypeDef,
    _OptionalDescribeRecommendationFeedbackRequestRequestTypeDef,
):
    pass


DescribeRecommendationFeedbackResponseTypeDef = TypedDict(
    "DescribeRecommendationFeedbackResponseTypeDef",
    {
        "RecommendationFeedback": "RecommendationFeedbackTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeRepositoryAssociationRequestRequestTypeDef = TypedDict(
    "DescribeRepositoryAssociationRequestRequestTypeDef",
    {
        "AssociationArn": str,
    },
)

DescribeRepositoryAssociationResponseTypeDef = TypedDict(
    "DescribeRepositoryAssociationResponseTypeDef",
    {
        "RepositoryAssociation": "RepositoryAssociationTypeDef",
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DisassociateRepositoryRequestRequestTypeDef = TypedDict(
    "DisassociateRepositoryRequestRequestTypeDef",
    {
        "AssociationArn": str,
    },
)

DisassociateRepositoryResponseTypeDef = TypedDict(
    "DisassociateRepositoryResponseTypeDef",
    {
        "RepositoryAssociation": "RepositoryAssociationTypeDef",
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

EventInfoTypeDef = TypedDict(
    "EventInfoTypeDef",
    {
        "Name": str,
        "State": str,
    },
    total=False,
)

KMSKeyDetailsTypeDef = TypedDict(
    "KMSKeyDetailsTypeDef",
    {
        "KMSKeyId": str,
        "EncryptionOption": EncryptionOptionType,
    },
    total=False,
)

_RequiredListCodeReviewsRequestRequestTypeDef = TypedDict(
    "_RequiredListCodeReviewsRequestRequestTypeDef",
    {
        "Type": TypeType,
    },
)
_OptionalListCodeReviewsRequestRequestTypeDef = TypedDict(
    "_OptionalListCodeReviewsRequestRequestTypeDef",
    {
        "ProviderTypes": Sequence[ProviderTypeType],
        "States": Sequence[JobStateType],
        "RepositoryNames": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListCodeReviewsRequestRequestTypeDef(
    _RequiredListCodeReviewsRequestRequestTypeDef, _OptionalListCodeReviewsRequestRequestTypeDef
):
    pass


ListCodeReviewsResponseTypeDef = TypedDict(
    "ListCodeReviewsResponseTypeDef",
    {
        "CodeReviewSummaries": List["CodeReviewSummaryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListRecommendationFeedbackRequestRequestTypeDef = TypedDict(
    "_RequiredListRecommendationFeedbackRequestRequestTypeDef",
    {
        "CodeReviewArn": str,
    },
)
_OptionalListRecommendationFeedbackRequestRequestTypeDef = TypedDict(
    "_OptionalListRecommendationFeedbackRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "UserIds": Sequence[str],
        "RecommendationIds": Sequence[str],
    },
    total=False,
)


class ListRecommendationFeedbackRequestRequestTypeDef(
    _RequiredListRecommendationFeedbackRequestRequestTypeDef,
    _OptionalListRecommendationFeedbackRequestRequestTypeDef,
):
    pass


ListRecommendationFeedbackResponseTypeDef = TypedDict(
    "ListRecommendationFeedbackResponseTypeDef",
    {
        "RecommendationFeedbackSummaries": List["RecommendationFeedbackSummaryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListRecommendationsRequestRequestTypeDef = TypedDict(
    "_RequiredListRecommendationsRequestRequestTypeDef",
    {
        "CodeReviewArn": str,
    },
)
_OptionalListRecommendationsRequestRequestTypeDef = TypedDict(
    "_OptionalListRecommendationsRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)


class ListRecommendationsRequestRequestTypeDef(
    _RequiredListRecommendationsRequestRequestTypeDef,
    _OptionalListRecommendationsRequestRequestTypeDef,
):
    pass


ListRecommendationsResponseTypeDef = TypedDict(
    "ListRecommendationsResponseTypeDef",
    {
        "RecommendationSummaries": List["RecommendationSummaryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListRepositoryAssociationsRequestRequestTypeDef = TypedDict(
    "ListRepositoryAssociationsRequestRequestTypeDef",
    {
        "ProviderTypes": Sequence[ProviderTypeType],
        "States": Sequence[RepositoryAssociationStateType],
        "Names": Sequence[str],
        "Owners": Sequence[str],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListRepositoryAssociationsResponseTypeDef = TypedDict(
    "ListRepositoryAssociationsResponseTypeDef",
    {
        "RepositoryAssociationSummaries": List["RepositoryAssociationSummaryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

MetricsSummaryTypeDef = TypedDict(
    "MetricsSummaryTypeDef",
    {
        "MeteredLinesOfCodeCount": int,
        "FindingsCount": int,
    },
    total=False,
)

MetricsTypeDef = TypedDict(
    "MetricsTypeDef",
    {
        "MeteredLinesOfCodeCount": int,
        "FindingsCount": int,
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

PutRecommendationFeedbackRequestRequestTypeDef = TypedDict(
    "PutRecommendationFeedbackRequestRequestTypeDef",
    {
        "CodeReviewArn": str,
        "RecommendationId": str,
        "Reactions": Sequence[ReactionType],
    },
)

RecommendationFeedbackSummaryTypeDef = TypedDict(
    "RecommendationFeedbackSummaryTypeDef",
    {
        "RecommendationId": str,
        "Reactions": List[ReactionType],
        "UserId": str,
    },
    total=False,
)

RecommendationFeedbackTypeDef = TypedDict(
    "RecommendationFeedbackTypeDef",
    {
        "CodeReviewArn": str,
        "RecommendationId": str,
        "Reactions": List[ReactionType],
        "UserId": str,
        "CreatedTimeStamp": datetime,
        "LastUpdatedTimeStamp": datetime,
    },
    total=False,
)

RecommendationSummaryTypeDef = TypedDict(
    "RecommendationSummaryTypeDef",
    {
        "FilePath": str,
        "RecommendationId": str,
        "StartLine": int,
        "EndLine": int,
        "Description": str,
        "RecommendationCategory": RecommendationCategoryType,
        "RuleMetadata": "RuleMetadataTypeDef",
        "Severity": SeverityType,
    },
    total=False,
)

RepositoryAnalysisTypeDef = TypedDict(
    "RepositoryAnalysisTypeDef",
    {
        "RepositoryHead": "RepositoryHeadSourceCodeTypeTypeDef",
        "SourceCodeType": "SourceCodeTypeTypeDef",
    },
    total=False,
)

RepositoryAssociationSummaryTypeDef = TypedDict(
    "RepositoryAssociationSummaryTypeDef",
    {
        "AssociationArn": str,
        "ConnectionArn": str,
        "LastUpdatedTimeStamp": datetime,
        "AssociationId": str,
        "Name": str,
        "Owner": str,
        "ProviderType": ProviderTypeType,
        "State": RepositoryAssociationStateType,
    },
    total=False,
)

RepositoryAssociationTypeDef = TypedDict(
    "RepositoryAssociationTypeDef",
    {
        "AssociationId": str,
        "AssociationArn": str,
        "ConnectionArn": str,
        "Name": str,
        "Owner": str,
        "ProviderType": ProviderTypeType,
        "State": RepositoryAssociationStateType,
        "StateReason": str,
        "LastUpdatedTimeStamp": datetime,
        "CreatedTimeStamp": datetime,
        "KMSKeyDetails": "KMSKeyDetailsTypeDef",
        "S3RepositoryDetails": "S3RepositoryDetailsTypeDef",
    },
    total=False,
)

RepositoryHeadSourceCodeTypeTypeDef = TypedDict(
    "RepositoryHeadSourceCodeTypeTypeDef",
    {
        "BranchName": str,
    },
)

RepositoryTypeDef = TypedDict(
    "RepositoryTypeDef",
    {
        "CodeCommit": "CodeCommitRepositoryTypeDef",
        "Bitbucket": "ThirdPartySourceRepositoryTypeDef",
        "GitHubEnterpriseServer": "ThirdPartySourceRepositoryTypeDef",
        "S3Bucket": "S3RepositoryTypeDef",
    },
    total=False,
)

RequestMetadataTypeDef = TypedDict(
    "RequestMetadataTypeDef",
    {
        "RequestId": str,
        "Requester": str,
        "EventInfo": "EventInfoTypeDef",
        "VendorName": VendorNameType,
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

RuleMetadataTypeDef = TypedDict(
    "RuleMetadataTypeDef",
    {
        "RuleId": str,
        "RuleName": str,
        "ShortDescription": str,
        "LongDescription": str,
        "RuleTags": List[str],
    },
    total=False,
)

_RequiredS3BucketRepositoryTypeDef = TypedDict(
    "_RequiredS3BucketRepositoryTypeDef",
    {
        "Name": str,
    },
)
_OptionalS3BucketRepositoryTypeDef = TypedDict(
    "_OptionalS3BucketRepositoryTypeDef",
    {
        "Details": "S3RepositoryDetailsTypeDef",
    },
    total=False,
)


class S3BucketRepositoryTypeDef(
    _RequiredS3BucketRepositoryTypeDef, _OptionalS3BucketRepositoryTypeDef
):
    pass


S3RepositoryDetailsTypeDef = TypedDict(
    "S3RepositoryDetailsTypeDef",
    {
        "BucketName": str,
        "CodeArtifacts": "CodeArtifactsTypeDef",
    },
    total=False,
)

S3RepositoryTypeDef = TypedDict(
    "S3RepositoryTypeDef",
    {
        "Name": str,
        "BucketName": str,
    },
)

SourceCodeTypeTypeDef = TypedDict(
    "SourceCodeTypeTypeDef",
    {
        "CommitDiff": "CommitDiffSourceCodeTypeTypeDef",
        "RepositoryHead": "RepositoryHeadSourceCodeTypeTypeDef",
        "BranchDiff": "BranchDiffSourceCodeTypeTypeDef",
        "S3BucketRepository": "S3BucketRepositoryTypeDef",
        "RequestMetadata": "RequestMetadataTypeDef",
    },
    total=False,
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "Tags": Mapping[str, str],
    },
)

ThirdPartySourceRepositoryTypeDef = TypedDict(
    "ThirdPartySourceRepositoryTypeDef",
    {
        "Name": str,
        "ConnectionArn": str,
        "Owner": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "TagKeys": Sequence[str],
    },
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": int,
        "MaxAttempts": int,
    },
    total=False,
)
