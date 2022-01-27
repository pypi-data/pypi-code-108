"""
Type annotations for amplify service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_amplify/type_defs.html)

Usage::

    ```python
    from mypy_boto3_amplify.type_defs import AppTypeDef

    data: AppTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import DomainStatusType, JobStatusType, JobTypeType, StageType

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AppTypeDef",
    "ArtifactTypeDef",
    "AutoBranchCreationConfigTypeDef",
    "BackendEnvironmentTypeDef",
    "BranchTypeDef",
    "CreateAppRequestRequestTypeDef",
    "CreateAppResultTypeDef",
    "CreateBackendEnvironmentRequestRequestTypeDef",
    "CreateBackendEnvironmentResultTypeDef",
    "CreateBranchRequestRequestTypeDef",
    "CreateBranchResultTypeDef",
    "CreateDeploymentRequestRequestTypeDef",
    "CreateDeploymentResultTypeDef",
    "CreateDomainAssociationRequestRequestTypeDef",
    "CreateDomainAssociationResultTypeDef",
    "CreateWebhookRequestRequestTypeDef",
    "CreateWebhookResultTypeDef",
    "CustomRuleTypeDef",
    "DeleteAppRequestRequestTypeDef",
    "DeleteAppResultTypeDef",
    "DeleteBackendEnvironmentRequestRequestTypeDef",
    "DeleteBackendEnvironmentResultTypeDef",
    "DeleteBranchRequestRequestTypeDef",
    "DeleteBranchResultTypeDef",
    "DeleteDomainAssociationRequestRequestTypeDef",
    "DeleteDomainAssociationResultTypeDef",
    "DeleteJobRequestRequestTypeDef",
    "DeleteJobResultTypeDef",
    "DeleteWebhookRequestRequestTypeDef",
    "DeleteWebhookResultTypeDef",
    "DomainAssociationTypeDef",
    "GenerateAccessLogsRequestRequestTypeDef",
    "GenerateAccessLogsResultTypeDef",
    "GetAppRequestRequestTypeDef",
    "GetAppResultTypeDef",
    "GetArtifactUrlRequestRequestTypeDef",
    "GetArtifactUrlResultTypeDef",
    "GetBackendEnvironmentRequestRequestTypeDef",
    "GetBackendEnvironmentResultTypeDef",
    "GetBranchRequestRequestTypeDef",
    "GetBranchResultTypeDef",
    "GetDomainAssociationRequestRequestTypeDef",
    "GetDomainAssociationResultTypeDef",
    "GetJobRequestRequestTypeDef",
    "GetJobResultTypeDef",
    "GetWebhookRequestRequestTypeDef",
    "GetWebhookResultTypeDef",
    "JobSummaryTypeDef",
    "JobTypeDef",
    "ListAppsRequestRequestTypeDef",
    "ListAppsResultTypeDef",
    "ListArtifactsRequestRequestTypeDef",
    "ListArtifactsResultTypeDef",
    "ListBackendEnvironmentsRequestRequestTypeDef",
    "ListBackendEnvironmentsResultTypeDef",
    "ListBranchesRequestRequestTypeDef",
    "ListBranchesResultTypeDef",
    "ListDomainAssociationsRequestRequestTypeDef",
    "ListDomainAssociationsResultTypeDef",
    "ListJobsRequestRequestTypeDef",
    "ListJobsResultTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListWebhooksRequestRequestTypeDef",
    "ListWebhooksResultTypeDef",
    "PaginatorConfigTypeDef",
    "ProductionBranchTypeDef",
    "ResponseMetadataTypeDef",
    "StartDeploymentRequestRequestTypeDef",
    "StartDeploymentResultTypeDef",
    "StartJobRequestRequestTypeDef",
    "StartJobResultTypeDef",
    "StepTypeDef",
    "StopJobRequestRequestTypeDef",
    "StopJobResultTypeDef",
    "SubDomainSettingTypeDef",
    "SubDomainTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAppRequestRequestTypeDef",
    "UpdateAppResultTypeDef",
    "UpdateBranchRequestRequestTypeDef",
    "UpdateBranchResultTypeDef",
    "UpdateDomainAssociationRequestRequestTypeDef",
    "UpdateDomainAssociationResultTypeDef",
    "UpdateWebhookRequestRequestTypeDef",
    "UpdateWebhookResultTypeDef",
    "WebhookTypeDef",
)

_RequiredAppTypeDef = TypedDict(
    "_RequiredAppTypeDef",
    {
        "appId": str,
        "appArn": str,
        "name": str,
        "description": str,
        "repository": str,
        "platform": Literal["WEB"],
        "createTime": datetime,
        "updateTime": datetime,
        "environmentVariables": Dict[str, str],
        "defaultDomain": str,
        "enableBranchAutoBuild": bool,
        "enableBasicAuth": bool,
    },
)
_OptionalAppTypeDef = TypedDict(
    "_OptionalAppTypeDef",
    {
        "tags": Dict[str, str],
        "iamServiceRoleArn": str,
        "enableBranchAutoDeletion": bool,
        "basicAuthCredentials": str,
        "customRules": List["CustomRuleTypeDef"],
        "productionBranch": "ProductionBranchTypeDef",
        "buildSpec": str,
        "customHeaders": str,
        "enableAutoBranchCreation": bool,
        "autoBranchCreationPatterns": List[str],
        "autoBranchCreationConfig": "AutoBranchCreationConfigTypeDef",
    },
    total=False,
)


class AppTypeDef(_RequiredAppTypeDef, _OptionalAppTypeDef):
    pass


ArtifactTypeDef = TypedDict(
    "ArtifactTypeDef",
    {
        "artifactFileName": str,
        "artifactId": str,
    },
)

AutoBranchCreationConfigTypeDef = TypedDict(
    "AutoBranchCreationConfigTypeDef",
    {
        "stage": StageType,
        "framework": str,
        "enableAutoBuild": bool,
        "environmentVariables": Mapping[str, str],
        "basicAuthCredentials": str,
        "enableBasicAuth": bool,
        "enablePerformanceMode": bool,
        "buildSpec": str,
        "enablePullRequestPreview": bool,
        "pullRequestEnvironmentName": str,
    },
    total=False,
)

_RequiredBackendEnvironmentTypeDef = TypedDict(
    "_RequiredBackendEnvironmentTypeDef",
    {
        "backendEnvironmentArn": str,
        "environmentName": str,
        "createTime": datetime,
        "updateTime": datetime,
    },
)
_OptionalBackendEnvironmentTypeDef = TypedDict(
    "_OptionalBackendEnvironmentTypeDef",
    {
        "stackName": str,
        "deploymentArtifacts": str,
    },
    total=False,
)


class BackendEnvironmentTypeDef(
    _RequiredBackendEnvironmentTypeDef, _OptionalBackendEnvironmentTypeDef
):
    pass


_RequiredBranchTypeDef = TypedDict(
    "_RequiredBranchTypeDef",
    {
        "branchArn": str,
        "branchName": str,
        "description": str,
        "stage": StageType,
        "displayName": str,
        "enableNotification": bool,
        "createTime": datetime,
        "updateTime": datetime,
        "environmentVariables": Dict[str, str],
        "enableAutoBuild": bool,
        "customDomains": List[str],
        "framework": str,
        "activeJobId": str,
        "totalNumberOfJobs": str,
        "enableBasicAuth": bool,
        "ttl": str,
        "enablePullRequestPreview": bool,
    },
)
_OptionalBranchTypeDef = TypedDict(
    "_OptionalBranchTypeDef",
    {
        "tags": Dict[str, str],
        "enablePerformanceMode": bool,
        "thumbnailUrl": str,
        "basicAuthCredentials": str,
        "buildSpec": str,
        "associatedResources": List[str],
        "pullRequestEnvironmentName": str,
        "destinationBranch": str,
        "sourceBranch": str,
        "backendEnvironmentArn": str,
    },
    total=False,
)


class BranchTypeDef(_RequiredBranchTypeDef, _OptionalBranchTypeDef):
    pass


_RequiredCreateAppRequestRequestTypeDef = TypedDict(
    "_RequiredCreateAppRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalCreateAppRequestRequestTypeDef = TypedDict(
    "_OptionalCreateAppRequestRequestTypeDef",
    {
        "description": str,
        "repository": str,
        "platform": Literal["WEB"],
        "iamServiceRoleArn": str,
        "oauthToken": str,
        "accessToken": str,
        "environmentVariables": Mapping[str, str],
        "enableBranchAutoBuild": bool,
        "enableBranchAutoDeletion": bool,
        "enableBasicAuth": bool,
        "basicAuthCredentials": str,
        "customRules": Sequence["CustomRuleTypeDef"],
        "tags": Mapping[str, str],
        "buildSpec": str,
        "customHeaders": str,
        "enableAutoBranchCreation": bool,
        "autoBranchCreationPatterns": Sequence[str],
        "autoBranchCreationConfig": "AutoBranchCreationConfigTypeDef",
    },
    total=False,
)


class CreateAppRequestRequestTypeDef(
    _RequiredCreateAppRequestRequestTypeDef, _OptionalCreateAppRequestRequestTypeDef
):
    pass


CreateAppResultTypeDef = TypedDict(
    "CreateAppResultTypeDef",
    {
        "app": "AppTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateBackendEnvironmentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBackendEnvironmentRequestRequestTypeDef",
    {
        "appId": str,
        "environmentName": str,
    },
)
_OptionalCreateBackendEnvironmentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBackendEnvironmentRequestRequestTypeDef",
    {
        "stackName": str,
        "deploymentArtifacts": str,
    },
    total=False,
)


class CreateBackendEnvironmentRequestRequestTypeDef(
    _RequiredCreateBackendEnvironmentRequestRequestTypeDef,
    _OptionalCreateBackendEnvironmentRequestRequestTypeDef,
):
    pass


CreateBackendEnvironmentResultTypeDef = TypedDict(
    "CreateBackendEnvironmentResultTypeDef",
    {
        "backendEnvironment": "BackendEnvironmentTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateBranchRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBranchRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)
_OptionalCreateBranchRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBranchRequestRequestTypeDef",
    {
        "description": str,
        "stage": StageType,
        "framework": str,
        "enableNotification": bool,
        "enableAutoBuild": bool,
        "environmentVariables": Mapping[str, str],
        "basicAuthCredentials": str,
        "enableBasicAuth": bool,
        "enablePerformanceMode": bool,
        "tags": Mapping[str, str],
        "buildSpec": str,
        "ttl": str,
        "displayName": str,
        "enablePullRequestPreview": bool,
        "pullRequestEnvironmentName": str,
        "backendEnvironmentArn": str,
    },
    total=False,
)


class CreateBranchRequestRequestTypeDef(
    _RequiredCreateBranchRequestRequestTypeDef, _OptionalCreateBranchRequestRequestTypeDef
):
    pass


CreateBranchResultTypeDef = TypedDict(
    "CreateBranchResultTypeDef",
    {
        "branch": "BranchTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateDeploymentRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDeploymentRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)
_OptionalCreateDeploymentRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDeploymentRequestRequestTypeDef",
    {
        "fileMap": Mapping[str, str],
    },
    total=False,
)


class CreateDeploymentRequestRequestTypeDef(
    _RequiredCreateDeploymentRequestRequestTypeDef, _OptionalCreateDeploymentRequestRequestTypeDef
):
    pass


CreateDeploymentResultTypeDef = TypedDict(
    "CreateDeploymentResultTypeDef",
    {
        "jobId": str,
        "fileUploadUrls": Dict[str, str],
        "zipUploadUrl": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateDomainAssociationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDomainAssociationRequestRequestTypeDef",
    {
        "appId": str,
        "domainName": str,
        "subDomainSettings": Sequence["SubDomainSettingTypeDef"],
    },
)
_OptionalCreateDomainAssociationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDomainAssociationRequestRequestTypeDef",
    {
        "enableAutoSubDomain": bool,
        "autoSubDomainCreationPatterns": Sequence[str],
        "autoSubDomainIAMRole": str,
    },
    total=False,
)


class CreateDomainAssociationRequestRequestTypeDef(
    _RequiredCreateDomainAssociationRequestRequestTypeDef,
    _OptionalCreateDomainAssociationRequestRequestTypeDef,
):
    pass


CreateDomainAssociationResultTypeDef = TypedDict(
    "CreateDomainAssociationResultTypeDef",
    {
        "domainAssociation": "DomainAssociationTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateWebhookRequestRequestTypeDef = TypedDict(
    "_RequiredCreateWebhookRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)
_OptionalCreateWebhookRequestRequestTypeDef = TypedDict(
    "_OptionalCreateWebhookRequestRequestTypeDef",
    {
        "description": str,
    },
    total=False,
)


class CreateWebhookRequestRequestTypeDef(
    _RequiredCreateWebhookRequestRequestTypeDef, _OptionalCreateWebhookRequestRequestTypeDef
):
    pass


CreateWebhookResultTypeDef = TypedDict(
    "CreateWebhookResultTypeDef",
    {
        "webhook": "WebhookTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCustomRuleTypeDef = TypedDict(
    "_RequiredCustomRuleTypeDef",
    {
        "source": str,
        "target": str,
    },
)
_OptionalCustomRuleTypeDef = TypedDict(
    "_OptionalCustomRuleTypeDef",
    {
        "status": str,
        "condition": str,
    },
    total=False,
)


class CustomRuleTypeDef(_RequiredCustomRuleTypeDef, _OptionalCustomRuleTypeDef):
    pass


DeleteAppRequestRequestTypeDef = TypedDict(
    "DeleteAppRequestRequestTypeDef",
    {
        "appId": str,
    },
)

DeleteAppResultTypeDef = TypedDict(
    "DeleteAppResultTypeDef",
    {
        "app": "AppTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteBackendEnvironmentRequestRequestTypeDef = TypedDict(
    "DeleteBackendEnvironmentRequestRequestTypeDef",
    {
        "appId": str,
        "environmentName": str,
    },
)

DeleteBackendEnvironmentResultTypeDef = TypedDict(
    "DeleteBackendEnvironmentResultTypeDef",
    {
        "backendEnvironment": "BackendEnvironmentTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteBranchRequestRequestTypeDef = TypedDict(
    "DeleteBranchRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)

DeleteBranchResultTypeDef = TypedDict(
    "DeleteBranchResultTypeDef",
    {
        "branch": "BranchTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteDomainAssociationRequestRequestTypeDef = TypedDict(
    "DeleteDomainAssociationRequestRequestTypeDef",
    {
        "appId": str,
        "domainName": str,
    },
)

DeleteDomainAssociationResultTypeDef = TypedDict(
    "DeleteDomainAssociationResultTypeDef",
    {
        "domainAssociation": "DomainAssociationTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteJobRequestRequestTypeDef = TypedDict(
    "DeleteJobRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
        "jobId": str,
    },
)

DeleteJobResultTypeDef = TypedDict(
    "DeleteJobResultTypeDef",
    {
        "jobSummary": "JobSummaryTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteWebhookRequestRequestTypeDef = TypedDict(
    "DeleteWebhookRequestRequestTypeDef",
    {
        "webhookId": str,
    },
)

DeleteWebhookResultTypeDef = TypedDict(
    "DeleteWebhookResultTypeDef",
    {
        "webhook": "WebhookTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDomainAssociationTypeDef = TypedDict(
    "_RequiredDomainAssociationTypeDef",
    {
        "domainAssociationArn": str,
        "domainName": str,
        "enableAutoSubDomain": bool,
        "domainStatus": DomainStatusType,
        "statusReason": str,
        "subDomains": List["SubDomainTypeDef"],
    },
)
_OptionalDomainAssociationTypeDef = TypedDict(
    "_OptionalDomainAssociationTypeDef",
    {
        "autoSubDomainCreationPatterns": List[str],
        "autoSubDomainIAMRole": str,
        "certificateVerificationDNSRecord": str,
    },
    total=False,
)


class DomainAssociationTypeDef(
    _RequiredDomainAssociationTypeDef, _OptionalDomainAssociationTypeDef
):
    pass


_RequiredGenerateAccessLogsRequestRequestTypeDef = TypedDict(
    "_RequiredGenerateAccessLogsRequestRequestTypeDef",
    {
        "domainName": str,
        "appId": str,
    },
)
_OptionalGenerateAccessLogsRequestRequestTypeDef = TypedDict(
    "_OptionalGenerateAccessLogsRequestRequestTypeDef",
    {
        "startTime": Union[datetime, str],
        "endTime": Union[datetime, str],
    },
    total=False,
)


class GenerateAccessLogsRequestRequestTypeDef(
    _RequiredGenerateAccessLogsRequestRequestTypeDef,
    _OptionalGenerateAccessLogsRequestRequestTypeDef,
):
    pass


GenerateAccessLogsResultTypeDef = TypedDict(
    "GenerateAccessLogsResultTypeDef",
    {
        "logUrl": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetAppRequestRequestTypeDef = TypedDict(
    "GetAppRequestRequestTypeDef",
    {
        "appId": str,
    },
)

GetAppResultTypeDef = TypedDict(
    "GetAppResultTypeDef",
    {
        "app": "AppTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetArtifactUrlRequestRequestTypeDef = TypedDict(
    "GetArtifactUrlRequestRequestTypeDef",
    {
        "artifactId": str,
    },
)

GetArtifactUrlResultTypeDef = TypedDict(
    "GetArtifactUrlResultTypeDef",
    {
        "artifactId": str,
        "artifactUrl": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetBackendEnvironmentRequestRequestTypeDef = TypedDict(
    "GetBackendEnvironmentRequestRequestTypeDef",
    {
        "appId": str,
        "environmentName": str,
    },
)

GetBackendEnvironmentResultTypeDef = TypedDict(
    "GetBackendEnvironmentResultTypeDef",
    {
        "backendEnvironment": "BackendEnvironmentTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetBranchRequestRequestTypeDef = TypedDict(
    "GetBranchRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)

GetBranchResultTypeDef = TypedDict(
    "GetBranchResultTypeDef",
    {
        "branch": "BranchTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetDomainAssociationRequestRequestTypeDef = TypedDict(
    "GetDomainAssociationRequestRequestTypeDef",
    {
        "appId": str,
        "domainName": str,
    },
)

GetDomainAssociationResultTypeDef = TypedDict(
    "GetDomainAssociationResultTypeDef",
    {
        "domainAssociation": "DomainAssociationTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetJobRequestRequestTypeDef = TypedDict(
    "GetJobRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
        "jobId": str,
    },
)

GetJobResultTypeDef = TypedDict(
    "GetJobResultTypeDef",
    {
        "job": "JobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetWebhookRequestRequestTypeDef = TypedDict(
    "GetWebhookRequestRequestTypeDef",
    {
        "webhookId": str,
    },
)

GetWebhookResultTypeDef = TypedDict(
    "GetWebhookResultTypeDef",
    {
        "webhook": "WebhookTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredJobSummaryTypeDef = TypedDict(
    "_RequiredJobSummaryTypeDef",
    {
        "jobArn": str,
        "jobId": str,
        "commitId": str,
        "commitMessage": str,
        "commitTime": datetime,
        "startTime": datetime,
        "status": JobStatusType,
        "jobType": JobTypeType,
    },
)
_OptionalJobSummaryTypeDef = TypedDict(
    "_OptionalJobSummaryTypeDef",
    {
        "endTime": datetime,
    },
    total=False,
)


class JobSummaryTypeDef(_RequiredJobSummaryTypeDef, _OptionalJobSummaryTypeDef):
    pass


JobTypeDef = TypedDict(
    "JobTypeDef",
    {
        "summary": "JobSummaryTypeDef",
        "steps": List["StepTypeDef"],
    },
)

ListAppsRequestRequestTypeDef = TypedDict(
    "ListAppsRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListAppsResultTypeDef = TypedDict(
    "ListAppsResultTypeDef",
    {
        "apps": List["AppTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListArtifactsRequestRequestTypeDef = TypedDict(
    "_RequiredListArtifactsRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
        "jobId": str,
    },
)
_OptionalListArtifactsRequestRequestTypeDef = TypedDict(
    "_OptionalListArtifactsRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListArtifactsRequestRequestTypeDef(
    _RequiredListArtifactsRequestRequestTypeDef, _OptionalListArtifactsRequestRequestTypeDef
):
    pass


ListArtifactsResultTypeDef = TypedDict(
    "ListArtifactsResultTypeDef",
    {
        "artifacts": List["ArtifactTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListBackendEnvironmentsRequestRequestTypeDef = TypedDict(
    "_RequiredListBackendEnvironmentsRequestRequestTypeDef",
    {
        "appId": str,
    },
)
_OptionalListBackendEnvironmentsRequestRequestTypeDef = TypedDict(
    "_OptionalListBackendEnvironmentsRequestRequestTypeDef",
    {
        "environmentName": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListBackendEnvironmentsRequestRequestTypeDef(
    _RequiredListBackendEnvironmentsRequestRequestTypeDef,
    _OptionalListBackendEnvironmentsRequestRequestTypeDef,
):
    pass


ListBackendEnvironmentsResultTypeDef = TypedDict(
    "ListBackendEnvironmentsResultTypeDef",
    {
        "backendEnvironments": List["BackendEnvironmentTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListBranchesRequestRequestTypeDef = TypedDict(
    "_RequiredListBranchesRequestRequestTypeDef",
    {
        "appId": str,
    },
)
_OptionalListBranchesRequestRequestTypeDef = TypedDict(
    "_OptionalListBranchesRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListBranchesRequestRequestTypeDef(
    _RequiredListBranchesRequestRequestTypeDef, _OptionalListBranchesRequestRequestTypeDef
):
    pass


ListBranchesResultTypeDef = TypedDict(
    "ListBranchesResultTypeDef",
    {
        "branches": List["BranchTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListDomainAssociationsRequestRequestTypeDef = TypedDict(
    "_RequiredListDomainAssociationsRequestRequestTypeDef",
    {
        "appId": str,
    },
)
_OptionalListDomainAssociationsRequestRequestTypeDef = TypedDict(
    "_OptionalListDomainAssociationsRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListDomainAssociationsRequestRequestTypeDef(
    _RequiredListDomainAssociationsRequestRequestTypeDef,
    _OptionalListDomainAssociationsRequestRequestTypeDef,
):
    pass


ListDomainAssociationsResultTypeDef = TypedDict(
    "ListDomainAssociationsResultTypeDef",
    {
        "domainAssociations": List["DomainAssociationTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListJobsRequestRequestTypeDef = TypedDict(
    "_RequiredListJobsRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)
_OptionalListJobsRequestRequestTypeDef = TypedDict(
    "_OptionalListJobsRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListJobsRequestRequestTypeDef(
    _RequiredListJobsRequestRequestTypeDef, _OptionalListJobsRequestRequestTypeDef
):
    pass


ListJobsResultTypeDef = TypedDict(
    "ListJobsResultTypeDef",
    {
        "jobSummaries": List["JobSummaryTypeDef"],
        "nextToken": str,
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
        "tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListWebhooksRequestRequestTypeDef = TypedDict(
    "_RequiredListWebhooksRequestRequestTypeDef",
    {
        "appId": str,
    },
)
_OptionalListWebhooksRequestRequestTypeDef = TypedDict(
    "_OptionalListWebhooksRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListWebhooksRequestRequestTypeDef(
    _RequiredListWebhooksRequestRequestTypeDef, _OptionalListWebhooksRequestRequestTypeDef
):
    pass


ListWebhooksResultTypeDef = TypedDict(
    "ListWebhooksResultTypeDef",
    {
        "webhooks": List["WebhookTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
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

ProductionBranchTypeDef = TypedDict(
    "ProductionBranchTypeDef",
    {
        "lastDeployTime": datetime,
        "status": str,
        "thumbnailUrl": str,
        "branchName": str,
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

_RequiredStartDeploymentRequestRequestTypeDef = TypedDict(
    "_RequiredStartDeploymentRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)
_OptionalStartDeploymentRequestRequestTypeDef = TypedDict(
    "_OptionalStartDeploymentRequestRequestTypeDef",
    {
        "jobId": str,
        "sourceUrl": str,
    },
    total=False,
)


class StartDeploymentRequestRequestTypeDef(
    _RequiredStartDeploymentRequestRequestTypeDef, _OptionalStartDeploymentRequestRequestTypeDef
):
    pass


StartDeploymentResultTypeDef = TypedDict(
    "StartDeploymentResultTypeDef",
    {
        "jobSummary": "JobSummaryTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartJobRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
        "jobType": JobTypeType,
    },
)
_OptionalStartJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartJobRequestRequestTypeDef",
    {
        "jobId": str,
        "jobReason": str,
        "commitId": str,
        "commitMessage": str,
        "commitTime": Union[datetime, str],
    },
    total=False,
)


class StartJobRequestRequestTypeDef(
    _RequiredStartJobRequestRequestTypeDef, _OptionalStartJobRequestRequestTypeDef
):
    pass


StartJobResultTypeDef = TypedDict(
    "StartJobResultTypeDef",
    {
        "jobSummary": "JobSummaryTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStepTypeDef = TypedDict(
    "_RequiredStepTypeDef",
    {
        "stepName": str,
        "startTime": datetime,
        "status": JobStatusType,
        "endTime": datetime,
    },
)
_OptionalStepTypeDef = TypedDict(
    "_OptionalStepTypeDef",
    {
        "logUrl": str,
        "artifactsUrl": str,
        "testArtifactsUrl": str,
        "testConfigUrl": str,
        "screenshots": Dict[str, str],
        "statusReason": str,
        "context": str,
    },
    total=False,
)


class StepTypeDef(_RequiredStepTypeDef, _OptionalStepTypeDef):
    pass


StopJobRequestRequestTypeDef = TypedDict(
    "StopJobRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
        "jobId": str,
    },
)

StopJobResultTypeDef = TypedDict(
    "StopJobResultTypeDef",
    {
        "jobSummary": "JobSummaryTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

SubDomainSettingTypeDef = TypedDict(
    "SubDomainSettingTypeDef",
    {
        "prefix": str,
        "branchName": str,
    },
)

SubDomainTypeDef = TypedDict(
    "SubDomainTypeDef",
    {
        "subDomainSetting": "SubDomainSettingTypeDef",
        "verified": bool,
        "dnsRecord": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

_RequiredUpdateAppRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateAppRequestRequestTypeDef",
    {
        "appId": str,
    },
)
_OptionalUpdateAppRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateAppRequestRequestTypeDef",
    {
        "name": str,
        "description": str,
        "platform": Literal["WEB"],
        "iamServiceRoleArn": str,
        "environmentVariables": Mapping[str, str],
        "enableBranchAutoBuild": bool,
        "enableBranchAutoDeletion": bool,
        "enableBasicAuth": bool,
        "basicAuthCredentials": str,
        "customRules": Sequence["CustomRuleTypeDef"],
        "buildSpec": str,
        "customHeaders": str,
        "enableAutoBranchCreation": bool,
        "autoBranchCreationPatterns": Sequence[str],
        "autoBranchCreationConfig": "AutoBranchCreationConfigTypeDef",
        "repository": str,
        "oauthToken": str,
        "accessToken": str,
    },
    total=False,
)


class UpdateAppRequestRequestTypeDef(
    _RequiredUpdateAppRequestRequestTypeDef, _OptionalUpdateAppRequestRequestTypeDef
):
    pass


UpdateAppResultTypeDef = TypedDict(
    "UpdateAppResultTypeDef",
    {
        "app": "AppTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateBranchRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateBranchRequestRequestTypeDef",
    {
        "appId": str,
        "branchName": str,
    },
)
_OptionalUpdateBranchRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateBranchRequestRequestTypeDef",
    {
        "description": str,
        "framework": str,
        "stage": StageType,
        "enableNotification": bool,
        "enableAutoBuild": bool,
        "environmentVariables": Mapping[str, str],
        "basicAuthCredentials": str,
        "enableBasicAuth": bool,
        "enablePerformanceMode": bool,
        "buildSpec": str,
        "ttl": str,
        "displayName": str,
        "enablePullRequestPreview": bool,
        "pullRequestEnvironmentName": str,
        "backendEnvironmentArn": str,
    },
    total=False,
)


class UpdateBranchRequestRequestTypeDef(
    _RequiredUpdateBranchRequestRequestTypeDef, _OptionalUpdateBranchRequestRequestTypeDef
):
    pass


UpdateBranchResultTypeDef = TypedDict(
    "UpdateBranchResultTypeDef",
    {
        "branch": "BranchTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateDomainAssociationRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDomainAssociationRequestRequestTypeDef",
    {
        "appId": str,
        "domainName": str,
        "subDomainSettings": Sequence["SubDomainSettingTypeDef"],
    },
)
_OptionalUpdateDomainAssociationRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDomainAssociationRequestRequestTypeDef",
    {
        "enableAutoSubDomain": bool,
        "autoSubDomainCreationPatterns": Sequence[str],
        "autoSubDomainIAMRole": str,
    },
    total=False,
)


class UpdateDomainAssociationRequestRequestTypeDef(
    _RequiredUpdateDomainAssociationRequestRequestTypeDef,
    _OptionalUpdateDomainAssociationRequestRequestTypeDef,
):
    pass


UpdateDomainAssociationResultTypeDef = TypedDict(
    "UpdateDomainAssociationResultTypeDef",
    {
        "domainAssociation": "DomainAssociationTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateWebhookRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateWebhookRequestRequestTypeDef",
    {
        "webhookId": str,
    },
)
_OptionalUpdateWebhookRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateWebhookRequestRequestTypeDef",
    {
        "branchName": str,
        "description": str,
    },
    total=False,
)


class UpdateWebhookRequestRequestTypeDef(
    _RequiredUpdateWebhookRequestRequestTypeDef, _OptionalUpdateWebhookRequestRequestTypeDef
):
    pass


UpdateWebhookResultTypeDef = TypedDict(
    "UpdateWebhookResultTypeDef",
    {
        "webhook": "WebhookTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

WebhookTypeDef = TypedDict(
    "WebhookTypeDef",
    {
        "webhookArn": str,
        "webhookId": str,
        "webhookUrl": str,
        "branchName": str,
        "description": str,
        "createTime": datetime,
        "updateTime": datetime,
    },
)
