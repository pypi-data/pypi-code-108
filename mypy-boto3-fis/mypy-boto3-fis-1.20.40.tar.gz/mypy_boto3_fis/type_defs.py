"""
Type annotations for fis service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_fis/type_defs.html)

Usage::

    ```python
    from mypy_boto3_fis.type_defs import ActionParameterTypeDef

    data: ActionParameterTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import ExperimentActionStatusType, ExperimentStatusType

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "ActionParameterTypeDef",
    "ActionSummaryTypeDef",
    "ActionTargetTypeDef",
    "ActionTypeDef",
    "CreateExperimentTemplateActionInputTypeDef",
    "CreateExperimentTemplateRequestRequestTypeDef",
    "CreateExperimentTemplateResponseTypeDef",
    "CreateExperimentTemplateStopConditionInputTypeDef",
    "CreateExperimentTemplateTargetInputTypeDef",
    "DeleteExperimentTemplateRequestRequestTypeDef",
    "DeleteExperimentTemplateResponseTypeDef",
    "ExperimentActionStateTypeDef",
    "ExperimentActionTypeDef",
    "ExperimentStateTypeDef",
    "ExperimentStopConditionTypeDef",
    "ExperimentSummaryTypeDef",
    "ExperimentTargetFilterTypeDef",
    "ExperimentTargetTypeDef",
    "ExperimentTemplateActionTypeDef",
    "ExperimentTemplateStopConditionTypeDef",
    "ExperimentTemplateSummaryTypeDef",
    "ExperimentTemplateTargetFilterTypeDef",
    "ExperimentTemplateTargetInputFilterTypeDef",
    "ExperimentTemplateTargetTypeDef",
    "ExperimentTemplateTypeDef",
    "ExperimentTypeDef",
    "GetActionRequestRequestTypeDef",
    "GetActionResponseTypeDef",
    "GetExperimentRequestRequestTypeDef",
    "GetExperimentResponseTypeDef",
    "GetExperimentTemplateRequestRequestTypeDef",
    "GetExperimentTemplateResponseTypeDef",
    "ListActionsRequestRequestTypeDef",
    "ListActionsResponseTypeDef",
    "ListExperimentTemplatesRequestRequestTypeDef",
    "ListExperimentTemplatesResponseTypeDef",
    "ListExperimentsRequestRequestTypeDef",
    "ListExperimentsResponseTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ResponseMetadataTypeDef",
    "StartExperimentRequestRequestTypeDef",
    "StartExperimentResponseTypeDef",
    "StopExperimentRequestRequestTypeDef",
    "StopExperimentResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateExperimentTemplateActionInputItemTypeDef",
    "UpdateExperimentTemplateRequestRequestTypeDef",
    "UpdateExperimentTemplateResponseTypeDef",
    "UpdateExperimentTemplateStopConditionInputTypeDef",
    "UpdateExperimentTemplateTargetInputTypeDef",
)

ActionParameterTypeDef = TypedDict(
    "ActionParameterTypeDef",
    {
        "description": str,
        "required": bool,
    },
    total=False,
)

ActionSummaryTypeDef = TypedDict(
    "ActionSummaryTypeDef",
    {
        "id": str,
        "description": str,
        "targets": Dict[str, "ActionTargetTypeDef"],
        "tags": Dict[str, str],
    },
    total=False,
)

ActionTargetTypeDef = TypedDict(
    "ActionTargetTypeDef",
    {
        "resourceType": str,
    },
    total=False,
)

ActionTypeDef = TypedDict(
    "ActionTypeDef",
    {
        "id": str,
        "description": str,
        "parameters": Dict[str, "ActionParameterTypeDef"],
        "targets": Dict[str, "ActionTargetTypeDef"],
        "tags": Dict[str, str],
    },
    total=False,
)

_RequiredCreateExperimentTemplateActionInputTypeDef = TypedDict(
    "_RequiredCreateExperimentTemplateActionInputTypeDef",
    {
        "actionId": str,
    },
)
_OptionalCreateExperimentTemplateActionInputTypeDef = TypedDict(
    "_OptionalCreateExperimentTemplateActionInputTypeDef",
    {
        "description": str,
        "parameters": Mapping[str, str],
        "targets": Mapping[str, str],
        "startAfter": Sequence[str],
    },
    total=False,
)


class CreateExperimentTemplateActionInputTypeDef(
    _RequiredCreateExperimentTemplateActionInputTypeDef,
    _OptionalCreateExperimentTemplateActionInputTypeDef,
):
    pass


_RequiredCreateExperimentTemplateRequestRequestTypeDef = TypedDict(
    "_RequiredCreateExperimentTemplateRequestRequestTypeDef",
    {
        "clientToken": str,
        "description": str,
        "stopConditions": Sequence["CreateExperimentTemplateStopConditionInputTypeDef"],
        "actions": Mapping[str, "CreateExperimentTemplateActionInputTypeDef"],
        "roleArn": str,
    },
)
_OptionalCreateExperimentTemplateRequestRequestTypeDef = TypedDict(
    "_OptionalCreateExperimentTemplateRequestRequestTypeDef",
    {
        "targets": Mapping[str, "CreateExperimentTemplateTargetInputTypeDef"],
        "tags": Mapping[str, str],
    },
    total=False,
)


class CreateExperimentTemplateRequestRequestTypeDef(
    _RequiredCreateExperimentTemplateRequestRequestTypeDef,
    _OptionalCreateExperimentTemplateRequestRequestTypeDef,
):
    pass


CreateExperimentTemplateResponseTypeDef = TypedDict(
    "CreateExperimentTemplateResponseTypeDef",
    {
        "experimentTemplate": "ExperimentTemplateTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateExperimentTemplateStopConditionInputTypeDef = TypedDict(
    "_RequiredCreateExperimentTemplateStopConditionInputTypeDef",
    {
        "source": str,
    },
)
_OptionalCreateExperimentTemplateStopConditionInputTypeDef = TypedDict(
    "_OptionalCreateExperimentTemplateStopConditionInputTypeDef",
    {
        "value": str,
    },
    total=False,
)


class CreateExperimentTemplateStopConditionInputTypeDef(
    _RequiredCreateExperimentTemplateStopConditionInputTypeDef,
    _OptionalCreateExperimentTemplateStopConditionInputTypeDef,
):
    pass


_RequiredCreateExperimentTemplateTargetInputTypeDef = TypedDict(
    "_RequiredCreateExperimentTemplateTargetInputTypeDef",
    {
        "resourceType": str,
        "selectionMode": str,
    },
)
_OptionalCreateExperimentTemplateTargetInputTypeDef = TypedDict(
    "_OptionalCreateExperimentTemplateTargetInputTypeDef",
    {
        "resourceArns": Sequence[str],
        "resourceTags": Mapping[str, str],
        "filters": Sequence["ExperimentTemplateTargetInputFilterTypeDef"],
    },
    total=False,
)


class CreateExperimentTemplateTargetInputTypeDef(
    _RequiredCreateExperimentTemplateTargetInputTypeDef,
    _OptionalCreateExperimentTemplateTargetInputTypeDef,
):
    pass


DeleteExperimentTemplateRequestRequestTypeDef = TypedDict(
    "DeleteExperimentTemplateRequestRequestTypeDef",
    {
        "id": str,
    },
)

DeleteExperimentTemplateResponseTypeDef = TypedDict(
    "DeleteExperimentTemplateResponseTypeDef",
    {
        "experimentTemplate": "ExperimentTemplateTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ExperimentActionStateTypeDef = TypedDict(
    "ExperimentActionStateTypeDef",
    {
        "status": ExperimentActionStatusType,
        "reason": str,
    },
    total=False,
)

ExperimentActionTypeDef = TypedDict(
    "ExperimentActionTypeDef",
    {
        "actionId": str,
        "description": str,
        "parameters": Dict[str, str],
        "targets": Dict[str, str],
        "startAfter": List[str],
        "state": "ExperimentActionStateTypeDef",
        "startTime": datetime,
        "endTime": datetime,
    },
    total=False,
)

ExperimentStateTypeDef = TypedDict(
    "ExperimentStateTypeDef",
    {
        "status": ExperimentStatusType,
        "reason": str,
    },
    total=False,
)

ExperimentStopConditionTypeDef = TypedDict(
    "ExperimentStopConditionTypeDef",
    {
        "source": str,
        "value": str,
    },
    total=False,
)

ExperimentSummaryTypeDef = TypedDict(
    "ExperimentSummaryTypeDef",
    {
        "id": str,
        "experimentTemplateId": str,
        "state": "ExperimentStateTypeDef",
        "creationTime": datetime,
        "tags": Dict[str, str],
    },
    total=False,
)

ExperimentTargetFilterTypeDef = TypedDict(
    "ExperimentTargetFilterTypeDef",
    {
        "path": str,
        "values": List[str],
    },
    total=False,
)

ExperimentTargetTypeDef = TypedDict(
    "ExperimentTargetTypeDef",
    {
        "resourceType": str,
        "resourceArns": List[str],
        "resourceTags": Dict[str, str],
        "filters": List["ExperimentTargetFilterTypeDef"],
        "selectionMode": str,
    },
    total=False,
)

ExperimentTemplateActionTypeDef = TypedDict(
    "ExperimentTemplateActionTypeDef",
    {
        "actionId": str,
        "description": str,
        "parameters": Dict[str, str],
        "targets": Dict[str, str],
        "startAfter": List[str],
    },
    total=False,
)

ExperimentTemplateStopConditionTypeDef = TypedDict(
    "ExperimentTemplateStopConditionTypeDef",
    {
        "source": str,
        "value": str,
    },
    total=False,
)

ExperimentTemplateSummaryTypeDef = TypedDict(
    "ExperimentTemplateSummaryTypeDef",
    {
        "id": str,
        "description": str,
        "creationTime": datetime,
        "lastUpdateTime": datetime,
        "tags": Dict[str, str],
    },
    total=False,
)

ExperimentTemplateTargetFilterTypeDef = TypedDict(
    "ExperimentTemplateTargetFilterTypeDef",
    {
        "path": str,
        "values": List[str],
    },
    total=False,
)

ExperimentTemplateTargetInputFilterTypeDef = TypedDict(
    "ExperimentTemplateTargetInputFilterTypeDef",
    {
        "path": str,
        "values": Sequence[str],
    },
)

ExperimentTemplateTargetTypeDef = TypedDict(
    "ExperimentTemplateTargetTypeDef",
    {
        "resourceType": str,
        "resourceArns": List[str],
        "resourceTags": Dict[str, str],
        "filters": List["ExperimentTemplateTargetFilterTypeDef"],
        "selectionMode": str,
    },
    total=False,
)

ExperimentTemplateTypeDef = TypedDict(
    "ExperimentTemplateTypeDef",
    {
        "id": str,
        "description": str,
        "targets": Dict[str, "ExperimentTemplateTargetTypeDef"],
        "actions": Dict[str, "ExperimentTemplateActionTypeDef"],
        "stopConditions": List["ExperimentTemplateStopConditionTypeDef"],
        "creationTime": datetime,
        "lastUpdateTime": datetime,
        "roleArn": str,
        "tags": Dict[str, str],
    },
    total=False,
)

ExperimentTypeDef = TypedDict(
    "ExperimentTypeDef",
    {
        "id": str,
        "experimentTemplateId": str,
        "roleArn": str,
        "state": "ExperimentStateTypeDef",
        "targets": Dict[str, "ExperimentTargetTypeDef"],
        "actions": Dict[str, "ExperimentActionTypeDef"],
        "stopConditions": List["ExperimentStopConditionTypeDef"],
        "creationTime": datetime,
        "startTime": datetime,
        "endTime": datetime,
        "tags": Dict[str, str],
    },
    total=False,
)

GetActionRequestRequestTypeDef = TypedDict(
    "GetActionRequestRequestTypeDef",
    {
        "id": str,
    },
)

GetActionResponseTypeDef = TypedDict(
    "GetActionResponseTypeDef",
    {
        "action": "ActionTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetExperimentRequestRequestTypeDef = TypedDict(
    "GetExperimentRequestRequestTypeDef",
    {
        "id": str,
    },
)

GetExperimentResponseTypeDef = TypedDict(
    "GetExperimentResponseTypeDef",
    {
        "experiment": "ExperimentTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetExperimentTemplateRequestRequestTypeDef = TypedDict(
    "GetExperimentTemplateRequestRequestTypeDef",
    {
        "id": str,
    },
)

GetExperimentTemplateResponseTypeDef = TypedDict(
    "GetExperimentTemplateResponseTypeDef",
    {
        "experimentTemplate": "ExperimentTemplateTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListActionsRequestRequestTypeDef = TypedDict(
    "ListActionsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

ListActionsResponseTypeDef = TypedDict(
    "ListActionsResponseTypeDef",
    {
        "actions": List["ActionSummaryTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListExperimentTemplatesRequestRequestTypeDef = TypedDict(
    "ListExperimentTemplatesRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

ListExperimentTemplatesResponseTypeDef = TypedDict(
    "ListExperimentTemplatesResponseTypeDef",
    {
        "experimentTemplates": List["ExperimentTemplateSummaryTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListExperimentsRequestRequestTypeDef = TypedDict(
    "ListExperimentsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

ListExperimentsResponseTypeDef = TypedDict(
    "ListExperimentsResponseTypeDef",
    {
        "experiments": List["ExperimentSummaryTypeDef"],
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

_RequiredStartExperimentRequestRequestTypeDef = TypedDict(
    "_RequiredStartExperimentRequestRequestTypeDef",
    {
        "clientToken": str,
        "experimentTemplateId": str,
    },
)
_OptionalStartExperimentRequestRequestTypeDef = TypedDict(
    "_OptionalStartExperimentRequestRequestTypeDef",
    {
        "tags": Mapping[str, str],
    },
    total=False,
)


class StartExperimentRequestRequestTypeDef(
    _RequiredStartExperimentRequestRequestTypeDef, _OptionalStartExperimentRequestRequestTypeDef
):
    pass


StartExperimentResponseTypeDef = TypedDict(
    "StartExperimentResponseTypeDef",
    {
        "experiment": "ExperimentTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

StopExperimentRequestRequestTypeDef = TypedDict(
    "StopExperimentRequestRequestTypeDef",
    {
        "id": str,
    },
)

StopExperimentResponseTypeDef = TypedDict(
    "StopExperimentResponseTypeDef",
    {
        "experiment": "ExperimentTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

_RequiredUntagResourceRequestRequestTypeDef = TypedDict(
    "_RequiredUntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
_OptionalUntagResourceRequestRequestTypeDef = TypedDict(
    "_OptionalUntagResourceRequestRequestTypeDef",
    {
        "tagKeys": Sequence[str],
    },
    total=False,
)


class UntagResourceRequestRequestTypeDef(
    _RequiredUntagResourceRequestRequestTypeDef, _OptionalUntagResourceRequestRequestTypeDef
):
    pass


UpdateExperimentTemplateActionInputItemTypeDef = TypedDict(
    "UpdateExperimentTemplateActionInputItemTypeDef",
    {
        "actionId": str,
        "description": str,
        "parameters": Mapping[str, str],
        "targets": Mapping[str, str],
        "startAfter": Sequence[str],
    },
    total=False,
)

_RequiredUpdateExperimentTemplateRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateExperimentTemplateRequestRequestTypeDef",
    {
        "id": str,
    },
)
_OptionalUpdateExperimentTemplateRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateExperimentTemplateRequestRequestTypeDef",
    {
        "description": str,
        "stopConditions": Sequence["UpdateExperimentTemplateStopConditionInputTypeDef"],
        "targets": Mapping[str, "UpdateExperimentTemplateTargetInputTypeDef"],
        "actions": Mapping[str, "UpdateExperimentTemplateActionInputItemTypeDef"],
        "roleArn": str,
    },
    total=False,
)


class UpdateExperimentTemplateRequestRequestTypeDef(
    _RequiredUpdateExperimentTemplateRequestRequestTypeDef,
    _OptionalUpdateExperimentTemplateRequestRequestTypeDef,
):
    pass


UpdateExperimentTemplateResponseTypeDef = TypedDict(
    "UpdateExperimentTemplateResponseTypeDef",
    {
        "experimentTemplate": "ExperimentTemplateTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateExperimentTemplateStopConditionInputTypeDef = TypedDict(
    "_RequiredUpdateExperimentTemplateStopConditionInputTypeDef",
    {
        "source": str,
    },
)
_OptionalUpdateExperimentTemplateStopConditionInputTypeDef = TypedDict(
    "_OptionalUpdateExperimentTemplateStopConditionInputTypeDef",
    {
        "value": str,
    },
    total=False,
)


class UpdateExperimentTemplateStopConditionInputTypeDef(
    _RequiredUpdateExperimentTemplateStopConditionInputTypeDef,
    _OptionalUpdateExperimentTemplateStopConditionInputTypeDef,
):
    pass


_RequiredUpdateExperimentTemplateTargetInputTypeDef = TypedDict(
    "_RequiredUpdateExperimentTemplateTargetInputTypeDef",
    {
        "resourceType": str,
        "selectionMode": str,
    },
)
_OptionalUpdateExperimentTemplateTargetInputTypeDef = TypedDict(
    "_OptionalUpdateExperimentTemplateTargetInputTypeDef",
    {
        "resourceArns": Sequence[str],
        "resourceTags": Mapping[str, str],
        "filters": Sequence["ExperimentTemplateTargetInputFilterTypeDef"],
    },
    total=False,
)


class UpdateExperimentTemplateTargetInputTypeDef(
    _RequiredUpdateExperimentTemplateTargetInputTypeDef,
    _OptionalUpdateExperimentTemplateTargetInputTypeDef,
):
    pass
