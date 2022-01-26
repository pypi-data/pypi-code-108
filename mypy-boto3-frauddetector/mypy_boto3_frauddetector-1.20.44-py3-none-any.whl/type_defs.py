"""
Type annotations for frauddetector service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_frauddetector/type_defs.html)

Usage::

    ```python
    from mypy_boto3_frauddetector.type_defs import BatchCreateVariableErrorTypeDef

    data: BatchCreateVariableErrorTypeDef = {...}
    ```
"""
import sys
from typing import IO, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AsyncJobStatusType,
    DataSourceType,
    DataTypeType,
    DetectorVersionStatusType,
    EventIngestionType,
    ModelEndpointStatusType,
    ModelInputDataFormatType,
    ModelOutputDataFormatType,
    ModelTypeEnumType,
    ModelVersionStatusType,
    RuleExecutionModeType,
    TrainingDataSourceEnumType,
    UnlabeledEventsTreatmentType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "BatchCreateVariableErrorTypeDef",
    "BatchCreateVariableRequestRequestTypeDef",
    "BatchCreateVariableResultTypeDef",
    "BatchGetVariableErrorTypeDef",
    "BatchGetVariableRequestRequestTypeDef",
    "BatchGetVariableResultTypeDef",
    "BatchImportTypeDef",
    "BatchPredictionTypeDef",
    "CancelBatchImportJobRequestRequestTypeDef",
    "CancelBatchPredictionJobRequestRequestTypeDef",
    "CreateBatchImportJobRequestRequestTypeDef",
    "CreateBatchPredictionJobRequestRequestTypeDef",
    "CreateDetectorVersionRequestRequestTypeDef",
    "CreateDetectorVersionResultTypeDef",
    "CreateModelRequestRequestTypeDef",
    "CreateModelVersionRequestRequestTypeDef",
    "CreateModelVersionResultTypeDef",
    "CreateRuleRequestRequestTypeDef",
    "CreateRuleResultTypeDef",
    "CreateVariableRequestRequestTypeDef",
    "DataValidationMetricsTypeDef",
    "DeleteBatchImportJobRequestRequestTypeDef",
    "DeleteBatchPredictionJobRequestRequestTypeDef",
    "DeleteDetectorRequestRequestTypeDef",
    "DeleteDetectorVersionRequestRequestTypeDef",
    "DeleteEntityTypeRequestRequestTypeDef",
    "DeleteEventRequestRequestTypeDef",
    "DeleteEventTypeRequestRequestTypeDef",
    "DeleteEventsByEventTypeRequestRequestTypeDef",
    "DeleteEventsByEventTypeResultTypeDef",
    "DeleteExternalModelRequestRequestTypeDef",
    "DeleteLabelRequestRequestTypeDef",
    "DeleteModelRequestRequestTypeDef",
    "DeleteModelVersionRequestRequestTypeDef",
    "DeleteOutcomeRequestRequestTypeDef",
    "DeleteRuleRequestRequestTypeDef",
    "DeleteVariableRequestRequestTypeDef",
    "DescribeDetectorRequestRequestTypeDef",
    "DescribeDetectorResultTypeDef",
    "DescribeModelVersionsRequestRequestTypeDef",
    "DescribeModelVersionsResultTypeDef",
    "DetectorTypeDef",
    "DetectorVersionSummaryTypeDef",
    "EntityTypeDef",
    "EntityTypeTypeDef",
    "EvaluatedExternalModelTypeDef",
    "EvaluatedModelVersionTypeDef",
    "EvaluatedRuleTypeDef",
    "EventPredictionSummaryTypeDef",
    "EventTypeDef",
    "EventTypeTypeDef",
    "EventVariableSummaryTypeDef",
    "ExternalEventsDetailTypeDef",
    "ExternalModelOutputsTypeDef",
    "ExternalModelSummaryTypeDef",
    "ExternalModelTypeDef",
    "FieldValidationMessageTypeDef",
    "FileValidationMessageTypeDef",
    "FilterConditionTypeDef",
    "GetBatchImportJobsRequestRequestTypeDef",
    "GetBatchImportJobsResultTypeDef",
    "GetBatchPredictionJobsRequestRequestTypeDef",
    "GetBatchPredictionJobsResultTypeDef",
    "GetDeleteEventsByEventTypeStatusRequestRequestTypeDef",
    "GetDeleteEventsByEventTypeStatusResultTypeDef",
    "GetDetectorVersionRequestRequestTypeDef",
    "GetDetectorVersionResultTypeDef",
    "GetDetectorsRequestRequestTypeDef",
    "GetDetectorsResultTypeDef",
    "GetEntityTypesRequestRequestTypeDef",
    "GetEntityTypesResultTypeDef",
    "GetEventPredictionMetadataRequestRequestTypeDef",
    "GetEventPredictionMetadataResultTypeDef",
    "GetEventPredictionRequestRequestTypeDef",
    "GetEventPredictionResultTypeDef",
    "GetEventRequestRequestTypeDef",
    "GetEventResultTypeDef",
    "GetEventTypesRequestRequestTypeDef",
    "GetEventTypesResultTypeDef",
    "GetExternalModelsRequestRequestTypeDef",
    "GetExternalModelsResultTypeDef",
    "GetKMSEncryptionKeyResultTypeDef",
    "GetLabelsRequestRequestTypeDef",
    "GetLabelsResultTypeDef",
    "GetModelVersionRequestRequestTypeDef",
    "GetModelVersionResultTypeDef",
    "GetModelsRequestRequestTypeDef",
    "GetModelsResultTypeDef",
    "GetOutcomesRequestRequestTypeDef",
    "GetOutcomesResultTypeDef",
    "GetRulesRequestRequestTypeDef",
    "GetRulesResultTypeDef",
    "GetVariablesRequestRequestTypeDef",
    "GetVariablesResultTypeDef",
    "IngestedEventStatisticsTypeDef",
    "IngestedEventsDetailTypeDef",
    "IngestedEventsTimeWindowTypeDef",
    "KMSKeyTypeDef",
    "LabelSchemaTypeDef",
    "LabelTypeDef",
    "ListEventPredictionsRequestRequestTypeDef",
    "ListEventPredictionsResultTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResultTypeDef",
    "LogOddsMetricTypeDef",
    "MetricDataPointTypeDef",
    "ModelEndpointDataBlobTypeDef",
    "ModelInputConfigurationTypeDef",
    "ModelOutputConfigurationTypeDef",
    "ModelScoresTypeDef",
    "ModelTypeDef",
    "ModelVersionDetailTypeDef",
    "ModelVersionEvaluationTypeDef",
    "ModelVersionTypeDef",
    "OutcomeTypeDef",
    "PredictionExplanationsTypeDef",
    "PredictionTimeRangeTypeDef",
    "PutDetectorRequestRequestTypeDef",
    "PutEntityTypeRequestRequestTypeDef",
    "PutEventTypeRequestRequestTypeDef",
    "PutExternalModelRequestRequestTypeDef",
    "PutKMSEncryptionKeyRequestRequestTypeDef",
    "PutLabelRequestRequestTypeDef",
    "PutOutcomeRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "RuleDetailTypeDef",
    "RuleResultTypeDef",
    "RuleTypeDef",
    "SendEventRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TagTypeDef",
    "TrainingDataSchemaTypeDef",
    "TrainingMetricsTypeDef",
    "TrainingResultTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateDetectorVersionMetadataRequestRequestTypeDef",
    "UpdateDetectorVersionRequestRequestTypeDef",
    "UpdateDetectorVersionStatusRequestRequestTypeDef",
    "UpdateEventLabelRequestRequestTypeDef",
    "UpdateModelRequestRequestTypeDef",
    "UpdateModelVersionRequestRequestTypeDef",
    "UpdateModelVersionResultTypeDef",
    "UpdateModelVersionStatusRequestRequestTypeDef",
    "UpdateRuleMetadataRequestRequestTypeDef",
    "UpdateRuleVersionRequestRequestTypeDef",
    "UpdateRuleVersionResultTypeDef",
    "UpdateVariableRequestRequestTypeDef",
    "VariableEntryTypeDef",
    "VariableImpactExplanationTypeDef",
    "VariableImportanceMetricsTypeDef",
    "VariableTypeDef",
)

BatchCreateVariableErrorTypeDef = TypedDict(
    "BatchCreateVariableErrorTypeDef",
    {
        "name": str,
        "code": int,
        "message": str,
    },
    total=False,
)

_RequiredBatchCreateVariableRequestRequestTypeDef = TypedDict(
    "_RequiredBatchCreateVariableRequestRequestTypeDef",
    {
        "variableEntries": Sequence["VariableEntryTypeDef"],
    },
)
_OptionalBatchCreateVariableRequestRequestTypeDef = TypedDict(
    "_OptionalBatchCreateVariableRequestRequestTypeDef",
    {
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class BatchCreateVariableRequestRequestTypeDef(
    _RequiredBatchCreateVariableRequestRequestTypeDef,
    _OptionalBatchCreateVariableRequestRequestTypeDef,
):
    pass


BatchCreateVariableResultTypeDef = TypedDict(
    "BatchCreateVariableResultTypeDef",
    {
        "errors": List["BatchCreateVariableErrorTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

BatchGetVariableErrorTypeDef = TypedDict(
    "BatchGetVariableErrorTypeDef",
    {
        "name": str,
        "code": int,
        "message": str,
    },
    total=False,
)

BatchGetVariableRequestRequestTypeDef = TypedDict(
    "BatchGetVariableRequestRequestTypeDef",
    {
        "names": Sequence[str],
    },
)

BatchGetVariableResultTypeDef = TypedDict(
    "BatchGetVariableResultTypeDef",
    {
        "variables": List["VariableTypeDef"],
        "errors": List["BatchGetVariableErrorTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

BatchImportTypeDef = TypedDict(
    "BatchImportTypeDef",
    {
        "jobId": str,
        "status": AsyncJobStatusType,
        "failureReason": str,
        "startTime": str,
        "completionTime": str,
        "inputPath": str,
        "outputPath": str,
        "eventTypeName": str,
        "iamRoleArn": str,
        "arn": str,
        "processedRecordsCount": int,
        "failedRecordsCount": int,
        "totalRecordsCount": int,
    },
    total=False,
)

BatchPredictionTypeDef = TypedDict(
    "BatchPredictionTypeDef",
    {
        "jobId": str,
        "status": AsyncJobStatusType,
        "failureReason": str,
        "startTime": str,
        "completionTime": str,
        "lastHeartbeatTime": str,
        "inputPath": str,
        "outputPath": str,
        "eventTypeName": str,
        "detectorName": str,
        "detectorVersion": str,
        "iamRoleArn": str,
        "arn": str,
        "processedRecordsCount": int,
        "totalRecordsCount": int,
    },
    total=False,
)

CancelBatchImportJobRequestRequestTypeDef = TypedDict(
    "CancelBatchImportJobRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

CancelBatchPredictionJobRequestRequestTypeDef = TypedDict(
    "CancelBatchPredictionJobRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

_RequiredCreateBatchImportJobRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBatchImportJobRequestRequestTypeDef",
    {
        "jobId": str,
        "inputPath": str,
        "outputPath": str,
        "eventTypeName": str,
        "iamRoleArn": str,
    },
)
_OptionalCreateBatchImportJobRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBatchImportJobRequestRequestTypeDef",
    {
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateBatchImportJobRequestRequestTypeDef(
    _RequiredCreateBatchImportJobRequestRequestTypeDef,
    _OptionalCreateBatchImportJobRequestRequestTypeDef,
):
    pass


_RequiredCreateBatchPredictionJobRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBatchPredictionJobRequestRequestTypeDef",
    {
        "jobId": str,
        "inputPath": str,
        "outputPath": str,
        "eventTypeName": str,
        "detectorName": str,
        "iamRoleArn": str,
    },
)
_OptionalCreateBatchPredictionJobRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBatchPredictionJobRequestRequestTypeDef",
    {
        "detectorVersion": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateBatchPredictionJobRequestRequestTypeDef(
    _RequiredCreateBatchPredictionJobRequestRequestTypeDef,
    _OptionalCreateBatchPredictionJobRequestRequestTypeDef,
):
    pass


_RequiredCreateDetectorVersionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDetectorVersionRequestRequestTypeDef",
    {
        "detectorId": str,
        "rules": Sequence["RuleTypeDef"],
    },
)
_OptionalCreateDetectorVersionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDetectorVersionRequestRequestTypeDef",
    {
        "description": str,
        "externalModelEndpoints": Sequence[str],
        "modelVersions": Sequence["ModelVersionTypeDef"],
        "ruleExecutionMode": RuleExecutionModeType,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateDetectorVersionRequestRequestTypeDef(
    _RequiredCreateDetectorVersionRequestRequestTypeDef,
    _OptionalCreateDetectorVersionRequestRequestTypeDef,
):
    pass


CreateDetectorVersionResultTypeDef = TypedDict(
    "CreateDetectorVersionResultTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
        "status": DetectorVersionStatusType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateModelRequestRequestTypeDef = TypedDict(
    "_RequiredCreateModelRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "eventTypeName": str,
    },
)
_OptionalCreateModelRequestRequestTypeDef = TypedDict(
    "_OptionalCreateModelRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateModelRequestRequestTypeDef(
    _RequiredCreateModelRequestRequestTypeDef, _OptionalCreateModelRequestRequestTypeDef
):
    pass


_RequiredCreateModelVersionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateModelVersionRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "trainingDataSource": TrainingDataSourceEnumType,
        "trainingDataSchema": "TrainingDataSchemaTypeDef",
    },
)
_OptionalCreateModelVersionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateModelVersionRequestRequestTypeDef",
    {
        "externalEventsDetail": "ExternalEventsDetailTypeDef",
        "ingestedEventsDetail": "IngestedEventsDetailTypeDef",
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateModelVersionRequestRequestTypeDef(
    _RequiredCreateModelVersionRequestRequestTypeDef,
    _OptionalCreateModelVersionRequestRequestTypeDef,
):
    pass


CreateModelVersionResultTypeDef = TypedDict(
    "CreateModelVersionResultTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
        "status": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateRuleRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRuleRequestRequestTypeDef",
    {
        "ruleId": str,
        "detectorId": str,
        "expression": str,
        "language": Literal["DETECTORPL"],
        "outcomes": Sequence[str],
    },
)
_OptionalCreateRuleRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRuleRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateRuleRequestRequestTypeDef(
    _RequiredCreateRuleRequestRequestTypeDef, _OptionalCreateRuleRequestRequestTypeDef
):
    pass


CreateRuleResultTypeDef = TypedDict(
    "CreateRuleResultTypeDef",
    {
        "rule": "RuleTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateVariableRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVariableRequestRequestTypeDef",
    {
        "name": str,
        "dataType": DataTypeType,
        "dataSource": DataSourceType,
        "defaultValue": str,
    },
)
_OptionalCreateVariableRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVariableRequestRequestTypeDef",
    {
        "description": str,
        "variableType": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateVariableRequestRequestTypeDef(
    _RequiredCreateVariableRequestRequestTypeDef, _OptionalCreateVariableRequestRequestTypeDef
):
    pass


DataValidationMetricsTypeDef = TypedDict(
    "DataValidationMetricsTypeDef",
    {
        "fileLevelMessages": List["FileValidationMessageTypeDef"],
        "fieldLevelMessages": List["FieldValidationMessageTypeDef"],
    },
    total=False,
)

DeleteBatchImportJobRequestRequestTypeDef = TypedDict(
    "DeleteBatchImportJobRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

DeleteBatchPredictionJobRequestRequestTypeDef = TypedDict(
    "DeleteBatchPredictionJobRequestRequestTypeDef",
    {
        "jobId": str,
    },
)

DeleteDetectorRequestRequestTypeDef = TypedDict(
    "DeleteDetectorRequestRequestTypeDef",
    {
        "detectorId": str,
    },
)

DeleteDetectorVersionRequestRequestTypeDef = TypedDict(
    "DeleteDetectorVersionRequestRequestTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
    },
)

DeleteEntityTypeRequestRequestTypeDef = TypedDict(
    "DeleteEntityTypeRequestRequestTypeDef",
    {
        "name": str,
    },
)

_RequiredDeleteEventRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteEventRequestRequestTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
    },
)
_OptionalDeleteEventRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteEventRequestRequestTypeDef",
    {
        "deleteAuditHistory": bool,
    },
    total=False,
)


class DeleteEventRequestRequestTypeDef(
    _RequiredDeleteEventRequestRequestTypeDef, _OptionalDeleteEventRequestRequestTypeDef
):
    pass


DeleteEventTypeRequestRequestTypeDef = TypedDict(
    "DeleteEventTypeRequestRequestTypeDef",
    {
        "name": str,
    },
)

DeleteEventsByEventTypeRequestRequestTypeDef = TypedDict(
    "DeleteEventsByEventTypeRequestRequestTypeDef",
    {
        "eventTypeName": str,
    },
)

DeleteEventsByEventTypeResultTypeDef = TypedDict(
    "DeleteEventsByEventTypeResultTypeDef",
    {
        "eventTypeName": str,
        "eventsDeletionStatus": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteExternalModelRequestRequestTypeDef = TypedDict(
    "DeleteExternalModelRequestRequestTypeDef",
    {
        "modelEndpoint": str,
    },
)

DeleteLabelRequestRequestTypeDef = TypedDict(
    "DeleteLabelRequestRequestTypeDef",
    {
        "name": str,
    },
)

DeleteModelRequestRequestTypeDef = TypedDict(
    "DeleteModelRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
    },
)

DeleteModelVersionRequestRequestTypeDef = TypedDict(
    "DeleteModelVersionRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
    },
)

DeleteOutcomeRequestRequestTypeDef = TypedDict(
    "DeleteOutcomeRequestRequestTypeDef",
    {
        "name": str,
    },
)

DeleteRuleRequestRequestTypeDef = TypedDict(
    "DeleteRuleRequestRequestTypeDef",
    {
        "rule": "RuleTypeDef",
    },
)

DeleteVariableRequestRequestTypeDef = TypedDict(
    "DeleteVariableRequestRequestTypeDef",
    {
        "name": str,
    },
)

_RequiredDescribeDetectorRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeDetectorRequestRequestTypeDef",
    {
        "detectorId": str,
    },
)
_OptionalDescribeDetectorRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeDetectorRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class DescribeDetectorRequestRequestTypeDef(
    _RequiredDescribeDetectorRequestRequestTypeDef, _OptionalDescribeDetectorRequestRequestTypeDef
):
    pass


DescribeDetectorResultTypeDef = TypedDict(
    "DescribeDetectorResultTypeDef",
    {
        "detectorId": str,
        "detectorVersionSummaries": List["DetectorVersionSummaryTypeDef"],
        "nextToken": str,
        "arn": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeModelVersionsRequestRequestTypeDef = TypedDict(
    "DescribeModelVersionsRequestRequestTypeDef",
    {
        "modelId": str,
        "modelVersionNumber": str,
        "modelType": ModelTypeEnumType,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

DescribeModelVersionsResultTypeDef = TypedDict(
    "DescribeModelVersionsResultTypeDef",
    {
        "modelVersionDetails": List["ModelVersionDetailTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DetectorTypeDef = TypedDict(
    "DetectorTypeDef",
    {
        "detectorId": str,
        "description": str,
        "eventTypeName": str,
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

DetectorVersionSummaryTypeDef = TypedDict(
    "DetectorVersionSummaryTypeDef",
    {
        "detectorVersionId": str,
        "status": DetectorVersionStatusType,
        "description": str,
        "lastUpdatedTime": str,
    },
    total=False,
)

EntityTypeDef = TypedDict(
    "EntityTypeDef",
    {
        "entityType": str,
        "entityId": str,
    },
)

EntityTypeTypeDef = TypedDict(
    "EntityTypeTypeDef",
    {
        "name": str,
        "description": str,
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

EvaluatedExternalModelTypeDef = TypedDict(
    "EvaluatedExternalModelTypeDef",
    {
        "modelEndpoint": str,
        "useEventVariables": bool,
        "inputVariables": Dict[str, str],
        "outputVariables": Dict[str, str],
    },
    total=False,
)

EvaluatedModelVersionTypeDef = TypedDict(
    "EvaluatedModelVersionTypeDef",
    {
        "modelId": str,
        "modelVersion": str,
        "modelType": str,
        "evaluations": List["ModelVersionEvaluationTypeDef"],
    },
    total=False,
)

EvaluatedRuleTypeDef = TypedDict(
    "EvaluatedRuleTypeDef",
    {
        "ruleId": str,
        "ruleVersion": str,
        "expression": str,
        "expressionWithValues": str,
        "outcomes": List[str],
        "evaluated": bool,
        "matched": bool,
    },
    total=False,
)

EventPredictionSummaryTypeDef = TypedDict(
    "EventPredictionSummaryTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
        "eventTimestamp": str,
        "predictionTimestamp": str,
        "detectorId": str,
        "detectorVersionId": str,
    },
    total=False,
)

EventTypeDef = TypedDict(
    "EventTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
        "eventTimestamp": str,
        "eventVariables": Dict[str, str],
        "currentLabel": str,
        "labelTimestamp": str,
        "entities": List["EntityTypeDef"],
    },
    total=False,
)

EventTypeTypeDef = TypedDict(
    "EventTypeTypeDef",
    {
        "name": str,
        "description": str,
        "eventVariables": List[str],
        "labels": List[str],
        "entityTypes": List[str],
        "eventIngestion": EventIngestionType,
        "ingestedEventStatistics": "IngestedEventStatisticsTypeDef",
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

EventVariableSummaryTypeDef = TypedDict(
    "EventVariableSummaryTypeDef",
    {
        "name": str,
        "value": str,
        "source": str,
    },
    total=False,
)

ExternalEventsDetailTypeDef = TypedDict(
    "ExternalEventsDetailTypeDef",
    {
        "dataLocation": str,
        "dataAccessRoleArn": str,
    },
)

ExternalModelOutputsTypeDef = TypedDict(
    "ExternalModelOutputsTypeDef",
    {
        "externalModel": "ExternalModelSummaryTypeDef",
        "outputs": Dict[str, str],
    },
    total=False,
)

ExternalModelSummaryTypeDef = TypedDict(
    "ExternalModelSummaryTypeDef",
    {
        "modelEndpoint": str,
        "modelSource": Literal["SAGEMAKER"],
    },
    total=False,
)

ExternalModelTypeDef = TypedDict(
    "ExternalModelTypeDef",
    {
        "modelEndpoint": str,
        "modelSource": Literal["SAGEMAKER"],
        "invokeModelEndpointRoleArn": str,
        "inputConfiguration": "ModelInputConfigurationTypeDef",
        "outputConfiguration": "ModelOutputConfigurationTypeDef",
        "modelEndpointStatus": ModelEndpointStatusType,
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

FieldValidationMessageTypeDef = TypedDict(
    "FieldValidationMessageTypeDef",
    {
        "fieldName": str,
        "identifier": str,
        "title": str,
        "content": str,
        "type": str,
    },
    total=False,
)

FileValidationMessageTypeDef = TypedDict(
    "FileValidationMessageTypeDef",
    {
        "title": str,
        "content": str,
        "type": str,
    },
    total=False,
)

FilterConditionTypeDef = TypedDict(
    "FilterConditionTypeDef",
    {
        "value": str,
    },
    total=False,
)

GetBatchImportJobsRequestRequestTypeDef = TypedDict(
    "GetBatchImportJobsRequestRequestTypeDef",
    {
        "jobId": str,
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

GetBatchImportJobsResultTypeDef = TypedDict(
    "GetBatchImportJobsResultTypeDef",
    {
        "batchImports": List["BatchImportTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetBatchPredictionJobsRequestRequestTypeDef = TypedDict(
    "GetBatchPredictionJobsRequestRequestTypeDef",
    {
        "jobId": str,
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

GetBatchPredictionJobsResultTypeDef = TypedDict(
    "GetBatchPredictionJobsResultTypeDef",
    {
        "batchPredictions": List["BatchPredictionTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetDeleteEventsByEventTypeStatusRequestRequestTypeDef = TypedDict(
    "GetDeleteEventsByEventTypeStatusRequestRequestTypeDef",
    {
        "eventTypeName": str,
    },
)

GetDeleteEventsByEventTypeStatusResultTypeDef = TypedDict(
    "GetDeleteEventsByEventTypeStatusResultTypeDef",
    {
        "eventTypeName": str,
        "eventsDeletionStatus": AsyncJobStatusType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetDetectorVersionRequestRequestTypeDef = TypedDict(
    "GetDetectorVersionRequestRequestTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
    },
)

GetDetectorVersionResultTypeDef = TypedDict(
    "GetDetectorVersionResultTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
        "description": str,
        "externalModelEndpoints": List[str],
        "modelVersions": List["ModelVersionTypeDef"],
        "rules": List["RuleTypeDef"],
        "status": DetectorVersionStatusType,
        "lastUpdatedTime": str,
        "createdTime": str,
        "ruleExecutionMode": RuleExecutionModeType,
        "arn": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetDetectorsRequestRequestTypeDef = TypedDict(
    "GetDetectorsRequestRequestTypeDef",
    {
        "detectorId": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetDetectorsResultTypeDef = TypedDict(
    "GetDetectorsResultTypeDef",
    {
        "detectors": List["DetectorTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetEntityTypesRequestRequestTypeDef = TypedDict(
    "GetEntityTypesRequestRequestTypeDef",
    {
        "name": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetEntityTypesResultTypeDef = TypedDict(
    "GetEntityTypesResultTypeDef",
    {
        "entityTypes": List["EntityTypeTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetEventPredictionMetadataRequestRequestTypeDef = TypedDict(
    "GetEventPredictionMetadataRequestRequestTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
        "detectorId": str,
        "detectorVersionId": str,
        "predictionTimestamp": str,
    },
)

GetEventPredictionMetadataResultTypeDef = TypedDict(
    "GetEventPredictionMetadataResultTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
        "entityId": str,
        "entityType": str,
        "eventTimestamp": str,
        "detectorId": str,
        "detectorVersionId": str,
        "detectorVersionStatus": str,
        "eventVariables": List["EventVariableSummaryTypeDef"],
        "rules": List["EvaluatedRuleTypeDef"],
        "ruleExecutionMode": RuleExecutionModeType,
        "outcomes": List[str],
        "evaluatedModelVersions": List["EvaluatedModelVersionTypeDef"],
        "evaluatedExternalModels": List["EvaluatedExternalModelTypeDef"],
        "predictionTimestamp": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetEventPredictionRequestRequestTypeDef = TypedDict(
    "_RequiredGetEventPredictionRequestRequestTypeDef",
    {
        "detectorId": str,
        "eventId": str,
        "eventTypeName": str,
        "entities": Sequence["EntityTypeDef"],
        "eventTimestamp": str,
        "eventVariables": Mapping[str, str],
    },
)
_OptionalGetEventPredictionRequestRequestTypeDef = TypedDict(
    "_OptionalGetEventPredictionRequestRequestTypeDef",
    {
        "detectorVersionId": str,
        "externalModelEndpointDataBlobs": Mapping[str, "ModelEndpointDataBlobTypeDef"],
    },
    total=False,
)


class GetEventPredictionRequestRequestTypeDef(
    _RequiredGetEventPredictionRequestRequestTypeDef,
    _OptionalGetEventPredictionRequestRequestTypeDef,
):
    pass


GetEventPredictionResultTypeDef = TypedDict(
    "GetEventPredictionResultTypeDef",
    {
        "modelScores": List["ModelScoresTypeDef"],
        "ruleResults": List["RuleResultTypeDef"],
        "externalModelOutputs": List["ExternalModelOutputsTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetEventRequestRequestTypeDef = TypedDict(
    "GetEventRequestRequestTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
    },
)

GetEventResultTypeDef = TypedDict(
    "GetEventResultTypeDef",
    {
        "event": "EventTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetEventTypesRequestRequestTypeDef = TypedDict(
    "GetEventTypesRequestRequestTypeDef",
    {
        "name": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetEventTypesResultTypeDef = TypedDict(
    "GetEventTypesResultTypeDef",
    {
        "eventTypes": List["EventTypeTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetExternalModelsRequestRequestTypeDef = TypedDict(
    "GetExternalModelsRequestRequestTypeDef",
    {
        "modelEndpoint": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetExternalModelsResultTypeDef = TypedDict(
    "GetExternalModelsResultTypeDef",
    {
        "externalModels": List["ExternalModelTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetKMSEncryptionKeyResultTypeDef = TypedDict(
    "GetKMSEncryptionKeyResultTypeDef",
    {
        "kmsKey": "KMSKeyTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetLabelsRequestRequestTypeDef = TypedDict(
    "GetLabelsRequestRequestTypeDef",
    {
        "name": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetLabelsResultTypeDef = TypedDict(
    "GetLabelsResultTypeDef",
    {
        "labels": List["LabelTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetModelVersionRequestRequestTypeDef = TypedDict(
    "GetModelVersionRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
    },
)

GetModelVersionResultTypeDef = TypedDict(
    "GetModelVersionResultTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
        "trainingDataSource": TrainingDataSourceEnumType,
        "trainingDataSchema": "TrainingDataSchemaTypeDef",
        "externalEventsDetail": "ExternalEventsDetailTypeDef",
        "ingestedEventsDetail": "IngestedEventsDetailTypeDef",
        "status": str,
        "arn": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetModelsRequestRequestTypeDef = TypedDict(
    "GetModelsRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetModelsResultTypeDef = TypedDict(
    "GetModelsResultTypeDef",
    {
        "nextToken": str,
        "models": List["ModelTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetOutcomesRequestRequestTypeDef = TypedDict(
    "GetOutcomesRequestRequestTypeDef",
    {
        "name": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetOutcomesResultTypeDef = TypedDict(
    "GetOutcomesResultTypeDef",
    {
        "outcomes": List["OutcomeTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetRulesRequestRequestTypeDef = TypedDict(
    "_RequiredGetRulesRequestRequestTypeDef",
    {
        "detectorId": str,
    },
)
_OptionalGetRulesRequestRequestTypeDef = TypedDict(
    "_OptionalGetRulesRequestRequestTypeDef",
    {
        "ruleId": str,
        "ruleVersion": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class GetRulesRequestRequestTypeDef(
    _RequiredGetRulesRequestRequestTypeDef, _OptionalGetRulesRequestRequestTypeDef
):
    pass


GetRulesResultTypeDef = TypedDict(
    "GetRulesResultTypeDef",
    {
        "ruleDetails": List["RuleDetailTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetVariablesRequestRequestTypeDef = TypedDict(
    "GetVariablesRequestRequestTypeDef",
    {
        "name": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

GetVariablesResultTypeDef = TypedDict(
    "GetVariablesResultTypeDef",
    {
        "variables": List["VariableTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

IngestedEventStatisticsTypeDef = TypedDict(
    "IngestedEventStatisticsTypeDef",
    {
        "numberOfEvents": int,
        "eventDataSizeInBytes": int,
        "leastRecentEvent": str,
        "mostRecentEvent": str,
        "lastUpdatedTime": str,
    },
    total=False,
)

IngestedEventsDetailTypeDef = TypedDict(
    "IngestedEventsDetailTypeDef",
    {
        "ingestedEventsTimeWindow": "IngestedEventsTimeWindowTypeDef",
    },
)

IngestedEventsTimeWindowTypeDef = TypedDict(
    "IngestedEventsTimeWindowTypeDef",
    {
        "startTime": str,
        "endTime": str,
    },
)

KMSKeyTypeDef = TypedDict(
    "KMSKeyTypeDef",
    {
        "kmsEncryptionKeyArn": str,
    },
    total=False,
)

_RequiredLabelSchemaTypeDef = TypedDict(
    "_RequiredLabelSchemaTypeDef",
    {
        "labelMapper": Mapping[str, Sequence[str]],
    },
)
_OptionalLabelSchemaTypeDef = TypedDict(
    "_OptionalLabelSchemaTypeDef",
    {
        "unlabeledEventsTreatment": UnlabeledEventsTreatmentType,
    },
    total=False,
)


class LabelSchemaTypeDef(_RequiredLabelSchemaTypeDef, _OptionalLabelSchemaTypeDef):
    pass


LabelTypeDef = TypedDict(
    "LabelTypeDef",
    {
        "name": str,
        "description": str,
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

ListEventPredictionsRequestRequestTypeDef = TypedDict(
    "ListEventPredictionsRequestRequestTypeDef",
    {
        "eventId": "FilterConditionTypeDef",
        "eventType": "FilterConditionTypeDef",
        "detectorId": "FilterConditionTypeDef",
        "detectorVersionId": "FilterConditionTypeDef",
        "predictionTimeRange": "PredictionTimeRangeTypeDef",
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListEventPredictionsResultTypeDef = TypedDict(
    "ListEventPredictionsResultTypeDef",
    {
        "eventPredictionSummaries": List["EventPredictionSummaryTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListTagsForResourceRequestRequestTypeDef = TypedDict(
    "_RequiredListTagsForResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
    },
)
_OptionalListTagsForResourceRequestRequestTypeDef = TypedDict(
    "_OptionalListTagsForResourceRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)


class ListTagsForResourceRequestRequestTypeDef(
    _RequiredListTagsForResourceRequestRequestTypeDef,
    _OptionalListTagsForResourceRequestRequestTypeDef,
):
    pass


ListTagsForResourceResultTypeDef = TypedDict(
    "ListTagsForResourceResultTypeDef",
    {
        "tags": List["TagTypeDef"],
        "nextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

LogOddsMetricTypeDef = TypedDict(
    "LogOddsMetricTypeDef",
    {
        "variableName": str,
        "variableType": str,
        "variableImportance": float,
    },
)

MetricDataPointTypeDef = TypedDict(
    "MetricDataPointTypeDef",
    {
        "fpr": float,
        "precision": float,
        "tpr": float,
        "threshold": float,
    },
    total=False,
)

ModelEndpointDataBlobTypeDef = TypedDict(
    "ModelEndpointDataBlobTypeDef",
    {
        "byteBuffer": Union[bytes, IO[bytes], StreamingBody],
        "contentType": str,
    },
    total=False,
)

_RequiredModelInputConfigurationTypeDef = TypedDict(
    "_RequiredModelInputConfigurationTypeDef",
    {
        "useEventVariables": bool,
    },
)
_OptionalModelInputConfigurationTypeDef = TypedDict(
    "_OptionalModelInputConfigurationTypeDef",
    {
        "eventTypeName": str,
        "format": ModelInputDataFormatType,
        "jsonInputTemplate": str,
        "csvInputTemplate": str,
    },
    total=False,
)


class ModelInputConfigurationTypeDef(
    _RequiredModelInputConfigurationTypeDef, _OptionalModelInputConfigurationTypeDef
):
    pass


_RequiredModelOutputConfigurationTypeDef = TypedDict(
    "_RequiredModelOutputConfigurationTypeDef",
    {
        "format": ModelOutputDataFormatType,
    },
)
_OptionalModelOutputConfigurationTypeDef = TypedDict(
    "_OptionalModelOutputConfigurationTypeDef",
    {
        "jsonKeyToVariableMap": Dict[str, str],
        "csvIndexToVariableMap": Dict[str, str],
    },
    total=False,
)


class ModelOutputConfigurationTypeDef(
    _RequiredModelOutputConfigurationTypeDef, _OptionalModelOutputConfigurationTypeDef
):
    pass


ModelScoresTypeDef = TypedDict(
    "ModelScoresTypeDef",
    {
        "modelVersion": "ModelVersionTypeDef",
        "scores": Dict[str, float],
    },
    total=False,
)

ModelTypeDef = TypedDict(
    "ModelTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "description": str,
        "eventTypeName": str,
        "createdTime": str,
        "lastUpdatedTime": str,
        "arn": str,
    },
    total=False,
)

ModelVersionDetailTypeDef = TypedDict(
    "ModelVersionDetailTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
        "status": str,
        "trainingDataSource": TrainingDataSourceEnumType,
        "trainingDataSchema": "TrainingDataSchemaTypeDef",
        "externalEventsDetail": "ExternalEventsDetailTypeDef",
        "ingestedEventsDetail": "IngestedEventsDetailTypeDef",
        "trainingResult": "TrainingResultTypeDef",
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

ModelVersionEvaluationTypeDef = TypedDict(
    "ModelVersionEvaluationTypeDef",
    {
        "outputVariableName": str,
        "evaluationScore": str,
        "predictionExplanations": "PredictionExplanationsTypeDef",
    },
    total=False,
)

_RequiredModelVersionTypeDef = TypedDict(
    "_RequiredModelVersionTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
    },
)
_OptionalModelVersionTypeDef = TypedDict(
    "_OptionalModelVersionTypeDef",
    {
        "arn": str,
    },
    total=False,
)


class ModelVersionTypeDef(_RequiredModelVersionTypeDef, _OptionalModelVersionTypeDef):
    pass


OutcomeTypeDef = TypedDict(
    "OutcomeTypeDef",
    {
        "name": str,
        "description": str,
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

PredictionExplanationsTypeDef = TypedDict(
    "PredictionExplanationsTypeDef",
    {
        "variableImpactExplanations": List["VariableImpactExplanationTypeDef"],
    },
    total=False,
)

PredictionTimeRangeTypeDef = TypedDict(
    "PredictionTimeRangeTypeDef",
    {
        "startTime": str,
        "endTime": str,
    },
)

_RequiredPutDetectorRequestRequestTypeDef = TypedDict(
    "_RequiredPutDetectorRequestRequestTypeDef",
    {
        "detectorId": str,
        "eventTypeName": str,
    },
)
_OptionalPutDetectorRequestRequestTypeDef = TypedDict(
    "_OptionalPutDetectorRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class PutDetectorRequestRequestTypeDef(
    _RequiredPutDetectorRequestRequestTypeDef, _OptionalPutDetectorRequestRequestTypeDef
):
    pass


_RequiredPutEntityTypeRequestRequestTypeDef = TypedDict(
    "_RequiredPutEntityTypeRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalPutEntityTypeRequestRequestTypeDef = TypedDict(
    "_OptionalPutEntityTypeRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class PutEntityTypeRequestRequestTypeDef(
    _RequiredPutEntityTypeRequestRequestTypeDef, _OptionalPutEntityTypeRequestRequestTypeDef
):
    pass


_RequiredPutEventTypeRequestRequestTypeDef = TypedDict(
    "_RequiredPutEventTypeRequestRequestTypeDef",
    {
        "name": str,
        "eventVariables": Sequence[str],
        "entityTypes": Sequence[str],
    },
)
_OptionalPutEventTypeRequestRequestTypeDef = TypedDict(
    "_OptionalPutEventTypeRequestRequestTypeDef",
    {
        "description": str,
        "labels": Sequence[str],
        "eventIngestion": EventIngestionType,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class PutEventTypeRequestRequestTypeDef(
    _RequiredPutEventTypeRequestRequestTypeDef, _OptionalPutEventTypeRequestRequestTypeDef
):
    pass


_RequiredPutExternalModelRequestRequestTypeDef = TypedDict(
    "_RequiredPutExternalModelRequestRequestTypeDef",
    {
        "modelEndpoint": str,
        "modelSource": Literal["SAGEMAKER"],
        "invokeModelEndpointRoleArn": str,
        "inputConfiguration": "ModelInputConfigurationTypeDef",
        "outputConfiguration": "ModelOutputConfigurationTypeDef",
        "modelEndpointStatus": ModelEndpointStatusType,
    },
)
_OptionalPutExternalModelRequestRequestTypeDef = TypedDict(
    "_OptionalPutExternalModelRequestRequestTypeDef",
    {
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class PutExternalModelRequestRequestTypeDef(
    _RequiredPutExternalModelRequestRequestTypeDef, _OptionalPutExternalModelRequestRequestTypeDef
):
    pass


PutKMSEncryptionKeyRequestRequestTypeDef = TypedDict(
    "PutKMSEncryptionKeyRequestRequestTypeDef",
    {
        "kmsEncryptionKeyArn": str,
    },
)

_RequiredPutLabelRequestRequestTypeDef = TypedDict(
    "_RequiredPutLabelRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalPutLabelRequestRequestTypeDef = TypedDict(
    "_OptionalPutLabelRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class PutLabelRequestRequestTypeDef(
    _RequiredPutLabelRequestRequestTypeDef, _OptionalPutLabelRequestRequestTypeDef
):
    pass


_RequiredPutOutcomeRequestRequestTypeDef = TypedDict(
    "_RequiredPutOutcomeRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalPutOutcomeRequestRequestTypeDef = TypedDict(
    "_OptionalPutOutcomeRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class PutOutcomeRequestRequestTypeDef(
    _RequiredPutOutcomeRequestRequestTypeDef, _OptionalPutOutcomeRequestRequestTypeDef
):
    pass


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

RuleDetailTypeDef = TypedDict(
    "RuleDetailTypeDef",
    {
        "ruleId": str,
        "description": str,
        "detectorId": str,
        "ruleVersion": str,
        "expression": str,
        "language": Literal["DETECTORPL"],
        "outcomes": List[str],
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)

RuleResultTypeDef = TypedDict(
    "RuleResultTypeDef",
    {
        "ruleId": str,
        "outcomes": List[str],
    },
    total=False,
)

RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "detectorId": str,
        "ruleId": str,
        "ruleVersion": str,
    },
)

_RequiredSendEventRequestRequestTypeDef = TypedDict(
    "_RequiredSendEventRequestRequestTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
        "eventTimestamp": str,
        "eventVariables": Mapping[str, str],
        "entities": Sequence["EntityTypeDef"],
    },
)
_OptionalSendEventRequestRequestTypeDef = TypedDict(
    "_OptionalSendEventRequestRequestTypeDef",
    {
        "assignedLabel": str,
        "labelTimestamp": str,
    },
    total=False,
)


class SendEventRequestRequestTypeDef(
    _RequiredSendEventRequestRequestTypeDef, _OptionalSendEventRequestRequestTypeDef
):
    pass


TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
        "tags": Sequence["TagTypeDef"],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": str,
        "value": str,
    },
)

TrainingDataSchemaTypeDef = TypedDict(
    "TrainingDataSchemaTypeDef",
    {
        "modelVariables": Sequence[str],
        "labelSchema": "LabelSchemaTypeDef",
    },
)

TrainingMetricsTypeDef = TypedDict(
    "TrainingMetricsTypeDef",
    {
        "auc": float,
        "metricDataPoints": List["MetricDataPointTypeDef"],
    },
    total=False,
)

TrainingResultTypeDef = TypedDict(
    "TrainingResultTypeDef",
    {
        "dataValidationMetrics": "DataValidationMetricsTypeDef",
        "trainingMetrics": "TrainingMetricsTypeDef",
        "variableImportanceMetrics": "VariableImportanceMetricsTypeDef",
    },
    total=False,
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
        "tagKeys": Sequence[str],
    },
)

UpdateDetectorVersionMetadataRequestRequestTypeDef = TypedDict(
    "UpdateDetectorVersionMetadataRequestRequestTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
        "description": str,
    },
)

_RequiredUpdateDetectorVersionRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDetectorVersionRequestRequestTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
        "externalModelEndpoints": Sequence[str],
        "rules": Sequence["RuleTypeDef"],
    },
)
_OptionalUpdateDetectorVersionRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDetectorVersionRequestRequestTypeDef",
    {
        "description": str,
        "modelVersions": Sequence["ModelVersionTypeDef"],
        "ruleExecutionMode": RuleExecutionModeType,
    },
    total=False,
)


class UpdateDetectorVersionRequestRequestTypeDef(
    _RequiredUpdateDetectorVersionRequestRequestTypeDef,
    _OptionalUpdateDetectorVersionRequestRequestTypeDef,
):
    pass


UpdateDetectorVersionStatusRequestRequestTypeDef = TypedDict(
    "UpdateDetectorVersionStatusRequestRequestTypeDef",
    {
        "detectorId": str,
        "detectorVersionId": str,
        "status": DetectorVersionStatusType,
    },
)

UpdateEventLabelRequestRequestTypeDef = TypedDict(
    "UpdateEventLabelRequestRequestTypeDef",
    {
        "eventId": str,
        "eventTypeName": str,
        "assignedLabel": str,
        "labelTimestamp": str,
    },
)

_RequiredUpdateModelRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateModelRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
    },
)
_OptionalUpdateModelRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateModelRequestRequestTypeDef",
    {
        "description": str,
    },
    total=False,
)


class UpdateModelRequestRequestTypeDef(
    _RequiredUpdateModelRequestRequestTypeDef, _OptionalUpdateModelRequestRequestTypeDef
):
    pass


_RequiredUpdateModelVersionRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateModelVersionRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "majorVersionNumber": str,
    },
)
_OptionalUpdateModelVersionRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateModelVersionRequestRequestTypeDef",
    {
        "externalEventsDetail": "ExternalEventsDetailTypeDef",
        "ingestedEventsDetail": "IngestedEventsDetailTypeDef",
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class UpdateModelVersionRequestRequestTypeDef(
    _RequiredUpdateModelVersionRequestRequestTypeDef,
    _OptionalUpdateModelVersionRequestRequestTypeDef,
):
    pass


UpdateModelVersionResultTypeDef = TypedDict(
    "UpdateModelVersionResultTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
        "status": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateModelVersionStatusRequestRequestTypeDef = TypedDict(
    "UpdateModelVersionStatusRequestRequestTypeDef",
    {
        "modelId": str,
        "modelType": ModelTypeEnumType,
        "modelVersionNumber": str,
        "status": ModelVersionStatusType,
    },
)

UpdateRuleMetadataRequestRequestTypeDef = TypedDict(
    "UpdateRuleMetadataRequestRequestTypeDef",
    {
        "rule": "RuleTypeDef",
        "description": str,
    },
)

_RequiredUpdateRuleVersionRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateRuleVersionRequestRequestTypeDef",
    {
        "rule": "RuleTypeDef",
        "expression": str,
        "language": Literal["DETECTORPL"],
        "outcomes": Sequence[str],
    },
)
_OptionalUpdateRuleVersionRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateRuleVersionRequestRequestTypeDef",
    {
        "description": str,
        "tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class UpdateRuleVersionRequestRequestTypeDef(
    _RequiredUpdateRuleVersionRequestRequestTypeDef, _OptionalUpdateRuleVersionRequestRequestTypeDef
):
    pass


UpdateRuleVersionResultTypeDef = TypedDict(
    "UpdateRuleVersionResultTypeDef",
    {
        "rule": "RuleTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateVariableRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateVariableRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalUpdateVariableRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateVariableRequestRequestTypeDef",
    {
        "defaultValue": str,
        "description": str,
        "variableType": str,
    },
    total=False,
)


class UpdateVariableRequestRequestTypeDef(
    _RequiredUpdateVariableRequestRequestTypeDef, _OptionalUpdateVariableRequestRequestTypeDef
):
    pass


VariableEntryTypeDef = TypedDict(
    "VariableEntryTypeDef",
    {
        "name": str,
        "dataType": str,
        "dataSource": str,
        "defaultValue": str,
        "description": str,
        "variableType": str,
    },
    total=False,
)

VariableImpactExplanationTypeDef = TypedDict(
    "VariableImpactExplanationTypeDef",
    {
        "eventVariableName": str,
        "relativeImpact": str,
        "logOddsImpact": float,
    },
    total=False,
)

VariableImportanceMetricsTypeDef = TypedDict(
    "VariableImportanceMetricsTypeDef",
    {
        "logOddsMetrics": List["LogOddsMetricTypeDef"],
    },
    total=False,
)

VariableTypeDef = TypedDict(
    "VariableTypeDef",
    {
        "name": str,
        "dataType": DataTypeType,
        "dataSource": DataSourceType,
        "defaultValue": str,
        "description": str,
        "variableType": str,
        "lastUpdatedTime": str,
        "createdTime": str,
        "arn": str,
    },
    total=False,
)
