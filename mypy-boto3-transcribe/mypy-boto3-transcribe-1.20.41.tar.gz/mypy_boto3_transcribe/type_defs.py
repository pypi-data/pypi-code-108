"""
Type annotations for transcribe service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_transcribe/type_defs.html)

Usage::

    ```python
    from mypy_boto3_transcribe.type_defs import AbsoluteTimeRangeTypeDef

    data: AbsoluteTimeRangeTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    BaseModelNameType,
    CallAnalyticsJobStatusType,
    CLMLanguageCodeType,
    LanguageCodeType,
    MediaFormatType,
    ModelStatusType,
    OutputLocationTypeType,
    ParticipantRoleType,
    PiiEntityTypeType,
    RedactionOutputType,
    SentimentValueType,
    SubtitleFormatType,
    TranscriptionJobStatusType,
    TypeType,
    VocabularyFilterMethodType,
    VocabularyStateType,
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
    "AbsoluteTimeRangeTypeDef",
    "CallAnalyticsJobSettingsTypeDef",
    "CallAnalyticsJobSummaryTypeDef",
    "CallAnalyticsJobTypeDef",
    "CategoryPropertiesTypeDef",
    "ChannelDefinitionTypeDef",
    "ContentRedactionTypeDef",
    "CreateCallAnalyticsCategoryRequestRequestTypeDef",
    "CreateCallAnalyticsCategoryResponseTypeDef",
    "CreateLanguageModelRequestRequestTypeDef",
    "CreateLanguageModelResponseTypeDef",
    "CreateMedicalVocabularyRequestRequestTypeDef",
    "CreateMedicalVocabularyResponseTypeDef",
    "CreateVocabularyFilterRequestRequestTypeDef",
    "CreateVocabularyFilterResponseTypeDef",
    "CreateVocabularyRequestRequestTypeDef",
    "CreateVocabularyResponseTypeDef",
    "DeleteCallAnalyticsCategoryRequestRequestTypeDef",
    "DeleteCallAnalyticsJobRequestRequestTypeDef",
    "DeleteLanguageModelRequestRequestTypeDef",
    "DeleteMedicalTranscriptionJobRequestRequestTypeDef",
    "DeleteMedicalVocabularyRequestRequestTypeDef",
    "DeleteTranscriptionJobRequestRequestTypeDef",
    "DeleteVocabularyFilterRequestRequestTypeDef",
    "DeleteVocabularyRequestRequestTypeDef",
    "DescribeLanguageModelRequestRequestTypeDef",
    "DescribeLanguageModelResponseTypeDef",
    "GetCallAnalyticsCategoryRequestRequestTypeDef",
    "GetCallAnalyticsCategoryResponseTypeDef",
    "GetCallAnalyticsJobRequestRequestTypeDef",
    "GetCallAnalyticsJobResponseTypeDef",
    "GetMedicalTranscriptionJobRequestRequestTypeDef",
    "GetMedicalTranscriptionJobResponseTypeDef",
    "GetMedicalVocabularyRequestRequestTypeDef",
    "GetMedicalVocabularyResponseTypeDef",
    "GetTranscriptionJobRequestRequestTypeDef",
    "GetTranscriptionJobResponseTypeDef",
    "GetVocabularyFilterRequestRequestTypeDef",
    "GetVocabularyFilterResponseTypeDef",
    "GetVocabularyRequestRequestTypeDef",
    "GetVocabularyResponseTypeDef",
    "InputDataConfigTypeDef",
    "InterruptionFilterTypeDef",
    "JobExecutionSettingsTypeDef",
    "LanguageIdSettingsTypeDef",
    "LanguageModelTypeDef",
    "ListCallAnalyticsCategoriesRequestRequestTypeDef",
    "ListCallAnalyticsCategoriesResponseTypeDef",
    "ListCallAnalyticsJobsRequestRequestTypeDef",
    "ListCallAnalyticsJobsResponseTypeDef",
    "ListLanguageModelsRequestRequestTypeDef",
    "ListLanguageModelsResponseTypeDef",
    "ListMedicalTranscriptionJobsRequestRequestTypeDef",
    "ListMedicalTranscriptionJobsResponseTypeDef",
    "ListMedicalVocabulariesRequestRequestTypeDef",
    "ListMedicalVocabulariesResponseTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListTranscriptionJobsRequestRequestTypeDef",
    "ListTranscriptionJobsResponseTypeDef",
    "ListVocabulariesRequestRequestTypeDef",
    "ListVocabulariesResponseTypeDef",
    "ListVocabularyFiltersRequestRequestTypeDef",
    "ListVocabularyFiltersResponseTypeDef",
    "MediaTypeDef",
    "MedicalTranscriptTypeDef",
    "MedicalTranscriptionJobSummaryTypeDef",
    "MedicalTranscriptionJobTypeDef",
    "MedicalTranscriptionSettingTypeDef",
    "ModelSettingsTypeDef",
    "NonTalkTimeFilterTypeDef",
    "RelativeTimeRangeTypeDef",
    "ResponseMetadataTypeDef",
    "RuleTypeDef",
    "SentimentFilterTypeDef",
    "SettingsTypeDef",
    "StartCallAnalyticsJobRequestRequestTypeDef",
    "StartCallAnalyticsJobResponseTypeDef",
    "StartMedicalTranscriptionJobRequestRequestTypeDef",
    "StartMedicalTranscriptionJobResponseTypeDef",
    "StartTranscriptionJobRequestRequestTypeDef",
    "StartTranscriptionJobResponseTypeDef",
    "SubtitlesOutputTypeDef",
    "SubtitlesTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TagTypeDef",
    "TranscriptFilterTypeDef",
    "TranscriptTypeDef",
    "TranscriptionJobSummaryTypeDef",
    "TranscriptionJobTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateCallAnalyticsCategoryRequestRequestTypeDef",
    "UpdateCallAnalyticsCategoryResponseTypeDef",
    "UpdateMedicalVocabularyRequestRequestTypeDef",
    "UpdateMedicalVocabularyResponseTypeDef",
    "UpdateVocabularyFilterRequestRequestTypeDef",
    "UpdateVocabularyFilterResponseTypeDef",
    "UpdateVocabularyRequestRequestTypeDef",
    "UpdateVocabularyResponseTypeDef",
    "VocabularyFilterInfoTypeDef",
    "VocabularyInfoTypeDef",
)

AbsoluteTimeRangeTypeDef = TypedDict(
    "AbsoluteTimeRangeTypeDef",
    {
        "StartTime": int,
        "EndTime": int,
        "First": int,
        "Last": int,
    },
    total=False,
)

CallAnalyticsJobSettingsTypeDef = TypedDict(
    "CallAnalyticsJobSettingsTypeDef",
    {
        "VocabularyName": str,
        "VocabularyFilterName": str,
        "VocabularyFilterMethod": VocabularyFilterMethodType,
        "LanguageModelName": str,
        "ContentRedaction": "ContentRedactionTypeDef",
        "LanguageOptions": List[LanguageCodeType],
        "LanguageIdSettings": Dict[LanguageCodeType, "LanguageIdSettingsTypeDef"],
    },
    total=False,
)

CallAnalyticsJobSummaryTypeDef = TypedDict(
    "CallAnalyticsJobSummaryTypeDef",
    {
        "CallAnalyticsJobName": str,
        "CreationTime": datetime,
        "StartTime": datetime,
        "CompletionTime": datetime,
        "LanguageCode": LanguageCodeType,
        "CallAnalyticsJobStatus": CallAnalyticsJobStatusType,
        "FailureReason": str,
    },
    total=False,
)

CallAnalyticsJobTypeDef = TypedDict(
    "CallAnalyticsJobTypeDef",
    {
        "CallAnalyticsJobName": str,
        "CallAnalyticsJobStatus": CallAnalyticsJobStatusType,
        "LanguageCode": LanguageCodeType,
        "MediaSampleRateHertz": int,
        "MediaFormat": MediaFormatType,
        "Media": "MediaTypeDef",
        "Transcript": "TranscriptTypeDef",
        "StartTime": datetime,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "FailureReason": str,
        "DataAccessRoleArn": str,
        "IdentifiedLanguageScore": float,
        "Settings": "CallAnalyticsJobSettingsTypeDef",
        "ChannelDefinitions": List["ChannelDefinitionTypeDef"],
    },
    total=False,
)

CategoryPropertiesTypeDef = TypedDict(
    "CategoryPropertiesTypeDef",
    {
        "CategoryName": str,
        "Rules": List["RuleTypeDef"],
        "CreateTime": datetime,
        "LastUpdateTime": datetime,
    },
    total=False,
)

ChannelDefinitionTypeDef = TypedDict(
    "ChannelDefinitionTypeDef",
    {
        "ChannelId": int,
        "ParticipantRole": ParticipantRoleType,
    },
    total=False,
)

_RequiredContentRedactionTypeDef = TypedDict(
    "_RequiredContentRedactionTypeDef",
    {
        "RedactionType": Literal["PII"],
        "RedactionOutput": RedactionOutputType,
    },
)
_OptionalContentRedactionTypeDef = TypedDict(
    "_OptionalContentRedactionTypeDef",
    {
        "PiiEntityTypes": List[PiiEntityTypeType],
    },
    total=False,
)


class ContentRedactionTypeDef(_RequiredContentRedactionTypeDef, _OptionalContentRedactionTypeDef):
    pass


CreateCallAnalyticsCategoryRequestRequestTypeDef = TypedDict(
    "CreateCallAnalyticsCategoryRequestRequestTypeDef",
    {
        "CategoryName": str,
        "Rules": Sequence["RuleTypeDef"],
    },
)

CreateCallAnalyticsCategoryResponseTypeDef = TypedDict(
    "CreateCallAnalyticsCategoryResponseTypeDef",
    {
        "CategoryProperties": "CategoryPropertiesTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateLanguageModelRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLanguageModelRequestRequestTypeDef",
    {
        "LanguageCode": CLMLanguageCodeType,
        "BaseModelName": BaseModelNameType,
        "ModelName": str,
        "InputDataConfig": "InputDataConfigTypeDef",
    },
)
_OptionalCreateLanguageModelRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLanguageModelRequestRequestTypeDef",
    {
        "Tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateLanguageModelRequestRequestTypeDef(
    _RequiredCreateLanguageModelRequestRequestTypeDef,
    _OptionalCreateLanguageModelRequestRequestTypeDef,
):
    pass


CreateLanguageModelResponseTypeDef = TypedDict(
    "CreateLanguageModelResponseTypeDef",
    {
        "LanguageCode": CLMLanguageCodeType,
        "BaseModelName": BaseModelNameType,
        "ModelName": str,
        "InputDataConfig": "InputDataConfigTypeDef",
        "ModelStatus": ModelStatusType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateMedicalVocabularyRequestRequestTypeDef = TypedDict(
    "_RequiredCreateMedicalVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "VocabularyFileUri": str,
    },
)
_OptionalCreateMedicalVocabularyRequestRequestTypeDef = TypedDict(
    "_OptionalCreateMedicalVocabularyRequestRequestTypeDef",
    {
        "Tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateMedicalVocabularyRequestRequestTypeDef(
    _RequiredCreateMedicalVocabularyRequestRequestTypeDef,
    _OptionalCreateMedicalVocabularyRequestRequestTypeDef,
):
    pass


CreateMedicalVocabularyResponseTypeDef = TypedDict(
    "CreateMedicalVocabularyResponseTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "VocabularyState": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateVocabularyFilterRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVocabularyFilterRequestRequestTypeDef",
    {
        "VocabularyFilterName": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalCreateVocabularyFilterRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVocabularyFilterRequestRequestTypeDef",
    {
        "Words": Sequence[str],
        "VocabularyFilterFileUri": str,
        "Tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateVocabularyFilterRequestRequestTypeDef(
    _RequiredCreateVocabularyFilterRequestRequestTypeDef,
    _OptionalCreateVocabularyFilterRequestRequestTypeDef,
):
    pass


CreateVocabularyFilterResponseTypeDef = TypedDict(
    "CreateVocabularyFilterResponseTypeDef",
    {
        "VocabularyFilterName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateVocabularyRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalCreateVocabularyRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVocabularyRequestRequestTypeDef",
    {
        "Phrases": Sequence[str],
        "VocabularyFileUri": str,
        "Tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateVocabularyRequestRequestTypeDef(
    _RequiredCreateVocabularyRequestRequestTypeDef, _OptionalCreateVocabularyRequestRequestTypeDef
):
    pass


CreateVocabularyResponseTypeDef = TypedDict(
    "CreateVocabularyResponseTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "VocabularyState": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteCallAnalyticsCategoryRequestRequestTypeDef = TypedDict(
    "DeleteCallAnalyticsCategoryRequestRequestTypeDef",
    {
        "CategoryName": str,
    },
)

DeleteCallAnalyticsJobRequestRequestTypeDef = TypedDict(
    "DeleteCallAnalyticsJobRequestRequestTypeDef",
    {
        "CallAnalyticsJobName": str,
    },
)

DeleteLanguageModelRequestRequestTypeDef = TypedDict(
    "DeleteLanguageModelRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

DeleteMedicalTranscriptionJobRequestRequestTypeDef = TypedDict(
    "DeleteMedicalTranscriptionJobRequestRequestTypeDef",
    {
        "MedicalTranscriptionJobName": str,
    },
)

DeleteMedicalVocabularyRequestRequestTypeDef = TypedDict(
    "DeleteMedicalVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
    },
)

DeleteTranscriptionJobRequestRequestTypeDef = TypedDict(
    "DeleteTranscriptionJobRequestRequestTypeDef",
    {
        "TranscriptionJobName": str,
    },
)

DeleteVocabularyFilterRequestRequestTypeDef = TypedDict(
    "DeleteVocabularyFilterRequestRequestTypeDef",
    {
        "VocabularyFilterName": str,
    },
)

DeleteVocabularyRequestRequestTypeDef = TypedDict(
    "DeleteVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
    },
)

DescribeLanguageModelRequestRequestTypeDef = TypedDict(
    "DescribeLanguageModelRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

DescribeLanguageModelResponseTypeDef = TypedDict(
    "DescribeLanguageModelResponseTypeDef",
    {
        "LanguageModel": "LanguageModelTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetCallAnalyticsCategoryRequestRequestTypeDef = TypedDict(
    "GetCallAnalyticsCategoryRequestRequestTypeDef",
    {
        "CategoryName": str,
    },
)

GetCallAnalyticsCategoryResponseTypeDef = TypedDict(
    "GetCallAnalyticsCategoryResponseTypeDef",
    {
        "CategoryProperties": "CategoryPropertiesTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetCallAnalyticsJobRequestRequestTypeDef = TypedDict(
    "GetCallAnalyticsJobRequestRequestTypeDef",
    {
        "CallAnalyticsJobName": str,
    },
)

GetCallAnalyticsJobResponseTypeDef = TypedDict(
    "GetCallAnalyticsJobResponseTypeDef",
    {
        "CallAnalyticsJob": "CallAnalyticsJobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetMedicalTranscriptionJobRequestRequestTypeDef = TypedDict(
    "GetMedicalTranscriptionJobRequestRequestTypeDef",
    {
        "MedicalTranscriptionJobName": str,
    },
)

GetMedicalTranscriptionJobResponseTypeDef = TypedDict(
    "GetMedicalTranscriptionJobResponseTypeDef",
    {
        "MedicalTranscriptionJob": "MedicalTranscriptionJobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetMedicalVocabularyRequestRequestTypeDef = TypedDict(
    "GetMedicalVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
    },
)

GetMedicalVocabularyResponseTypeDef = TypedDict(
    "GetMedicalVocabularyResponseTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "VocabularyState": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "DownloadUri": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetTranscriptionJobRequestRequestTypeDef = TypedDict(
    "GetTranscriptionJobRequestRequestTypeDef",
    {
        "TranscriptionJobName": str,
    },
)

GetTranscriptionJobResponseTypeDef = TypedDict(
    "GetTranscriptionJobResponseTypeDef",
    {
        "TranscriptionJob": "TranscriptionJobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetVocabularyFilterRequestRequestTypeDef = TypedDict(
    "GetVocabularyFilterRequestRequestTypeDef",
    {
        "VocabularyFilterName": str,
    },
)

GetVocabularyFilterResponseTypeDef = TypedDict(
    "GetVocabularyFilterResponseTypeDef",
    {
        "VocabularyFilterName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
        "DownloadUri": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetVocabularyRequestRequestTypeDef = TypedDict(
    "GetVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
    },
)

GetVocabularyResponseTypeDef = TypedDict(
    "GetVocabularyResponseTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "VocabularyState": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "DownloadUri": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredInputDataConfigTypeDef = TypedDict(
    "_RequiredInputDataConfigTypeDef",
    {
        "S3Uri": str,
        "DataAccessRoleArn": str,
    },
)
_OptionalInputDataConfigTypeDef = TypedDict(
    "_OptionalInputDataConfigTypeDef",
    {
        "TuningDataS3Uri": str,
    },
    total=False,
)


class InputDataConfigTypeDef(_RequiredInputDataConfigTypeDef, _OptionalInputDataConfigTypeDef):
    pass


InterruptionFilterTypeDef = TypedDict(
    "InterruptionFilterTypeDef",
    {
        "Threshold": int,
        "ParticipantRole": ParticipantRoleType,
        "AbsoluteTimeRange": "AbsoluteTimeRangeTypeDef",
        "RelativeTimeRange": "RelativeTimeRangeTypeDef",
        "Negate": bool,
    },
    total=False,
)

JobExecutionSettingsTypeDef = TypedDict(
    "JobExecutionSettingsTypeDef",
    {
        "AllowDeferredExecution": bool,
        "DataAccessRoleArn": str,
    },
    total=False,
)

LanguageIdSettingsTypeDef = TypedDict(
    "LanguageIdSettingsTypeDef",
    {
        "VocabularyName": str,
        "VocabularyFilterName": str,
        "LanguageModelName": str,
    },
    total=False,
)

LanguageModelTypeDef = TypedDict(
    "LanguageModelTypeDef",
    {
        "ModelName": str,
        "CreateTime": datetime,
        "LastModifiedTime": datetime,
        "LanguageCode": CLMLanguageCodeType,
        "BaseModelName": BaseModelNameType,
        "ModelStatus": ModelStatusType,
        "UpgradeAvailability": bool,
        "FailureReason": str,
        "InputDataConfig": "InputDataConfigTypeDef",
    },
    total=False,
)

ListCallAnalyticsCategoriesRequestRequestTypeDef = TypedDict(
    "ListCallAnalyticsCategoriesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListCallAnalyticsCategoriesResponseTypeDef = TypedDict(
    "ListCallAnalyticsCategoriesResponseTypeDef",
    {
        "NextToken": str,
        "Categories": List["CategoryPropertiesTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListCallAnalyticsJobsRequestRequestTypeDef = TypedDict(
    "ListCallAnalyticsJobsRequestRequestTypeDef",
    {
        "Status": CallAnalyticsJobStatusType,
        "JobNameContains": str,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListCallAnalyticsJobsResponseTypeDef = TypedDict(
    "ListCallAnalyticsJobsResponseTypeDef",
    {
        "Status": CallAnalyticsJobStatusType,
        "NextToken": str,
        "CallAnalyticsJobSummaries": List["CallAnalyticsJobSummaryTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListLanguageModelsRequestRequestTypeDef = TypedDict(
    "ListLanguageModelsRequestRequestTypeDef",
    {
        "StatusEquals": ModelStatusType,
        "NameContains": str,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListLanguageModelsResponseTypeDef = TypedDict(
    "ListLanguageModelsResponseTypeDef",
    {
        "NextToken": str,
        "Models": List["LanguageModelTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListMedicalTranscriptionJobsRequestRequestTypeDef = TypedDict(
    "ListMedicalTranscriptionJobsRequestRequestTypeDef",
    {
        "Status": TranscriptionJobStatusType,
        "JobNameContains": str,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListMedicalTranscriptionJobsResponseTypeDef = TypedDict(
    "ListMedicalTranscriptionJobsResponseTypeDef",
    {
        "Status": TranscriptionJobStatusType,
        "NextToken": str,
        "MedicalTranscriptionJobSummaries": List["MedicalTranscriptionJobSummaryTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListMedicalVocabulariesRequestRequestTypeDef = TypedDict(
    "ListMedicalVocabulariesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "StateEquals": VocabularyStateType,
        "NameContains": str,
    },
    total=False,
)

ListMedicalVocabulariesResponseTypeDef = TypedDict(
    "ListMedicalVocabulariesResponseTypeDef",
    {
        "Status": VocabularyStateType,
        "NextToken": str,
        "Vocabularies": List["VocabularyInfoTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "ResourceArn": str,
        "Tags": List["TagTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListTranscriptionJobsRequestRequestTypeDef = TypedDict(
    "ListTranscriptionJobsRequestRequestTypeDef",
    {
        "Status": TranscriptionJobStatusType,
        "JobNameContains": str,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

ListTranscriptionJobsResponseTypeDef = TypedDict(
    "ListTranscriptionJobsResponseTypeDef",
    {
        "Status": TranscriptionJobStatusType,
        "NextToken": str,
        "TranscriptionJobSummaries": List["TranscriptionJobSummaryTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVocabulariesRequestRequestTypeDef = TypedDict(
    "ListVocabulariesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "StateEquals": VocabularyStateType,
        "NameContains": str,
    },
    total=False,
)

ListVocabulariesResponseTypeDef = TypedDict(
    "ListVocabulariesResponseTypeDef",
    {
        "Status": VocabularyStateType,
        "NextToken": str,
        "Vocabularies": List["VocabularyInfoTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVocabularyFiltersRequestRequestTypeDef = TypedDict(
    "ListVocabularyFiltersRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
        "NameContains": str,
    },
    total=False,
)

ListVocabularyFiltersResponseTypeDef = TypedDict(
    "ListVocabularyFiltersResponseTypeDef",
    {
        "NextToken": str,
        "VocabularyFilters": List["VocabularyFilterInfoTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

MediaTypeDef = TypedDict(
    "MediaTypeDef",
    {
        "MediaFileUri": str,
        "RedactedMediaFileUri": str,
    },
    total=False,
)

MedicalTranscriptTypeDef = TypedDict(
    "MedicalTranscriptTypeDef",
    {
        "TranscriptFileUri": str,
    },
    total=False,
)

MedicalTranscriptionJobSummaryTypeDef = TypedDict(
    "MedicalTranscriptionJobSummaryTypeDef",
    {
        "MedicalTranscriptionJobName": str,
        "CreationTime": datetime,
        "StartTime": datetime,
        "CompletionTime": datetime,
        "LanguageCode": LanguageCodeType,
        "TranscriptionJobStatus": TranscriptionJobStatusType,
        "FailureReason": str,
        "OutputLocationType": OutputLocationTypeType,
        "Specialty": Literal["PRIMARYCARE"],
        "ContentIdentificationType": Literal["PHI"],
        "Type": TypeType,
    },
    total=False,
)

MedicalTranscriptionJobTypeDef = TypedDict(
    "MedicalTranscriptionJobTypeDef",
    {
        "MedicalTranscriptionJobName": str,
        "TranscriptionJobStatus": TranscriptionJobStatusType,
        "LanguageCode": LanguageCodeType,
        "MediaSampleRateHertz": int,
        "MediaFormat": MediaFormatType,
        "Media": "MediaTypeDef",
        "Transcript": "MedicalTranscriptTypeDef",
        "StartTime": datetime,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "FailureReason": str,
        "Settings": "MedicalTranscriptionSettingTypeDef",
        "ContentIdentificationType": Literal["PHI"],
        "Specialty": Literal["PRIMARYCARE"],
        "Type": TypeType,
        "Tags": List["TagTypeDef"],
    },
    total=False,
)

MedicalTranscriptionSettingTypeDef = TypedDict(
    "MedicalTranscriptionSettingTypeDef",
    {
        "ShowSpeakerLabels": bool,
        "MaxSpeakerLabels": int,
        "ChannelIdentification": bool,
        "ShowAlternatives": bool,
        "MaxAlternatives": int,
        "VocabularyName": str,
    },
    total=False,
)

ModelSettingsTypeDef = TypedDict(
    "ModelSettingsTypeDef",
    {
        "LanguageModelName": str,
    },
    total=False,
)

NonTalkTimeFilterTypeDef = TypedDict(
    "NonTalkTimeFilterTypeDef",
    {
        "Threshold": int,
        "AbsoluteTimeRange": "AbsoluteTimeRangeTypeDef",
        "RelativeTimeRange": "RelativeTimeRangeTypeDef",
        "Negate": bool,
    },
    total=False,
)

RelativeTimeRangeTypeDef = TypedDict(
    "RelativeTimeRangeTypeDef",
    {
        "StartPercentage": int,
        "EndPercentage": int,
        "First": int,
        "Last": int,
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

RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "NonTalkTimeFilter": "NonTalkTimeFilterTypeDef",
        "InterruptionFilter": "InterruptionFilterTypeDef",
        "TranscriptFilter": "TranscriptFilterTypeDef",
        "SentimentFilter": "SentimentFilterTypeDef",
    },
    total=False,
)

_RequiredSentimentFilterTypeDef = TypedDict(
    "_RequiredSentimentFilterTypeDef",
    {
        "Sentiments": Sequence[SentimentValueType],
    },
)
_OptionalSentimentFilterTypeDef = TypedDict(
    "_OptionalSentimentFilterTypeDef",
    {
        "AbsoluteTimeRange": "AbsoluteTimeRangeTypeDef",
        "RelativeTimeRange": "RelativeTimeRangeTypeDef",
        "ParticipantRole": ParticipantRoleType,
        "Negate": bool,
    },
    total=False,
)


class SentimentFilterTypeDef(_RequiredSentimentFilterTypeDef, _OptionalSentimentFilterTypeDef):
    pass


SettingsTypeDef = TypedDict(
    "SettingsTypeDef",
    {
        "VocabularyName": str,
        "ShowSpeakerLabels": bool,
        "MaxSpeakerLabels": int,
        "ChannelIdentification": bool,
        "ShowAlternatives": bool,
        "MaxAlternatives": int,
        "VocabularyFilterName": str,
        "VocabularyFilterMethod": VocabularyFilterMethodType,
    },
    total=False,
)

_RequiredStartCallAnalyticsJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartCallAnalyticsJobRequestRequestTypeDef",
    {
        "CallAnalyticsJobName": str,
        "Media": "MediaTypeDef",
        "DataAccessRoleArn": str,
    },
)
_OptionalStartCallAnalyticsJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartCallAnalyticsJobRequestRequestTypeDef",
    {
        "OutputLocation": str,
        "OutputEncryptionKMSKeyId": str,
        "Settings": "CallAnalyticsJobSettingsTypeDef",
        "ChannelDefinitions": Sequence["ChannelDefinitionTypeDef"],
    },
    total=False,
)


class StartCallAnalyticsJobRequestRequestTypeDef(
    _RequiredStartCallAnalyticsJobRequestRequestTypeDef,
    _OptionalStartCallAnalyticsJobRequestRequestTypeDef,
):
    pass


StartCallAnalyticsJobResponseTypeDef = TypedDict(
    "StartCallAnalyticsJobResponseTypeDef",
    {
        "CallAnalyticsJob": "CallAnalyticsJobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartMedicalTranscriptionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartMedicalTranscriptionJobRequestRequestTypeDef",
    {
        "MedicalTranscriptionJobName": str,
        "LanguageCode": LanguageCodeType,
        "Media": "MediaTypeDef",
        "OutputBucketName": str,
        "Specialty": Literal["PRIMARYCARE"],
        "Type": TypeType,
    },
)
_OptionalStartMedicalTranscriptionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartMedicalTranscriptionJobRequestRequestTypeDef",
    {
        "MediaSampleRateHertz": int,
        "MediaFormat": MediaFormatType,
        "OutputKey": str,
        "OutputEncryptionKMSKeyId": str,
        "KMSEncryptionContext": Mapping[str, str],
        "Settings": "MedicalTranscriptionSettingTypeDef",
        "ContentIdentificationType": Literal["PHI"],
        "Tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class StartMedicalTranscriptionJobRequestRequestTypeDef(
    _RequiredStartMedicalTranscriptionJobRequestRequestTypeDef,
    _OptionalStartMedicalTranscriptionJobRequestRequestTypeDef,
):
    pass


StartMedicalTranscriptionJobResponseTypeDef = TypedDict(
    "StartMedicalTranscriptionJobResponseTypeDef",
    {
        "MedicalTranscriptionJob": "MedicalTranscriptionJobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredStartTranscriptionJobRequestRequestTypeDef = TypedDict(
    "_RequiredStartTranscriptionJobRequestRequestTypeDef",
    {
        "TranscriptionJobName": str,
        "Media": "MediaTypeDef",
    },
)
_OptionalStartTranscriptionJobRequestRequestTypeDef = TypedDict(
    "_OptionalStartTranscriptionJobRequestRequestTypeDef",
    {
        "LanguageCode": LanguageCodeType,
        "MediaSampleRateHertz": int,
        "MediaFormat": MediaFormatType,
        "OutputBucketName": str,
        "OutputKey": str,
        "OutputEncryptionKMSKeyId": str,
        "KMSEncryptionContext": Mapping[str, str],
        "Settings": "SettingsTypeDef",
        "ModelSettings": "ModelSettingsTypeDef",
        "JobExecutionSettings": "JobExecutionSettingsTypeDef",
        "ContentRedaction": "ContentRedactionTypeDef",
        "IdentifyLanguage": bool,
        "LanguageOptions": Sequence[LanguageCodeType],
        "Subtitles": "SubtitlesTypeDef",
        "Tags": Sequence["TagTypeDef"],
        "LanguageIdSettings": Mapping[LanguageCodeType, "LanguageIdSettingsTypeDef"],
    },
    total=False,
)


class StartTranscriptionJobRequestRequestTypeDef(
    _RequiredStartTranscriptionJobRequestRequestTypeDef,
    _OptionalStartTranscriptionJobRequestRequestTypeDef,
):
    pass


StartTranscriptionJobResponseTypeDef = TypedDict(
    "StartTranscriptionJobResponseTypeDef",
    {
        "TranscriptionJob": "TranscriptionJobTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

SubtitlesOutputTypeDef = TypedDict(
    "SubtitlesOutputTypeDef",
    {
        "Formats": List[SubtitleFormatType],
        "SubtitleFileUris": List[str],
    },
    total=False,
)

SubtitlesTypeDef = TypedDict(
    "SubtitlesTypeDef",
    {
        "Formats": Sequence[SubtitleFormatType],
    },
    total=False,
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence["TagTypeDef"],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

_RequiredTranscriptFilterTypeDef = TypedDict(
    "_RequiredTranscriptFilterTypeDef",
    {
        "TranscriptFilterType": Literal["EXACT"],
        "Targets": Sequence[str],
    },
)
_OptionalTranscriptFilterTypeDef = TypedDict(
    "_OptionalTranscriptFilterTypeDef",
    {
        "AbsoluteTimeRange": "AbsoluteTimeRangeTypeDef",
        "RelativeTimeRange": "RelativeTimeRangeTypeDef",
        "ParticipantRole": ParticipantRoleType,
        "Negate": bool,
    },
    total=False,
)


class TranscriptFilterTypeDef(_RequiredTranscriptFilterTypeDef, _OptionalTranscriptFilterTypeDef):
    pass


TranscriptTypeDef = TypedDict(
    "TranscriptTypeDef",
    {
        "TranscriptFileUri": str,
        "RedactedTranscriptFileUri": str,
    },
    total=False,
)

TranscriptionJobSummaryTypeDef = TypedDict(
    "TranscriptionJobSummaryTypeDef",
    {
        "TranscriptionJobName": str,
        "CreationTime": datetime,
        "StartTime": datetime,
        "CompletionTime": datetime,
        "LanguageCode": LanguageCodeType,
        "TranscriptionJobStatus": TranscriptionJobStatusType,
        "FailureReason": str,
        "OutputLocationType": OutputLocationTypeType,
        "ContentRedaction": "ContentRedactionTypeDef",
        "ModelSettings": "ModelSettingsTypeDef",
        "IdentifyLanguage": bool,
        "IdentifiedLanguageScore": float,
    },
    total=False,
)

TranscriptionJobTypeDef = TypedDict(
    "TranscriptionJobTypeDef",
    {
        "TranscriptionJobName": str,
        "TranscriptionJobStatus": TranscriptionJobStatusType,
        "LanguageCode": LanguageCodeType,
        "MediaSampleRateHertz": int,
        "MediaFormat": MediaFormatType,
        "Media": "MediaTypeDef",
        "Transcript": "TranscriptTypeDef",
        "StartTime": datetime,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "FailureReason": str,
        "Settings": "SettingsTypeDef",
        "ModelSettings": "ModelSettingsTypeDef",
        "JobExecutionSettings": "JobExecutionSettingsTypeDef",
        "ContentRedaction": "ContentRedactionTypeDef",
        "IdentifyLanguage": bool,
        "LanguageOptions": List[LanguageCodeType],
        "IdentifiedLanguageScore": float,
        "Tags": List["TagTypeDef"],
        "Subtitles": "SubtitlesOutputTypeDef",
        "LanguageIdSettings": Dict[LanguageCodeType, "LanguageIdSettingsTypeDef"],
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

UpdateCallAnalyticsCategoryRequestRequestTypeDef = TypedDict(
    "UpdateCallAnalyticsCategoryRequestRequestTypeDef",
    {
        "CategoryName": str,
        "Rules": Sequence["RuleTypeDef"],
    },
)

UpdateCallAnalyticsCategoryResponseTypeDef = TypedDict(
    "UpdateCallAnalyticsCategoryResponseTypeDef",
    {
        "CategoryProperties": "CategoryPropertiesTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateMedicalVocabularyRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateMedicalVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalUpdateMedicalVocabularyRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateMedicalVocabularyRequestRequestTypeDef",
    {
        "VocabularyFileUri": str,
    },
    total=False,
)


class UpdateMedicalVocabularyRequestRequestTypeDef(
    _RequiredUpdateMedicalVocabularyRequestRequestTypeDef,
    _OptionalUpdateMedicalVocabularyRequestRequestTypeDef,
):
    pass


UpdateMedicalVocabularyResponseTypeDef = TypedDict(
    "UpdateMedicalVocabularyResponseTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
        "VocabularyState": VocabularyStateType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateVocabularyFilterRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateVocabularyFilterRequestRequestTypeDef",
    {
        "VocabularyFilterName": str,
    },
)
_OptionalUpdateVocabularyFilterRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateVocabularyFilterRequestRequestTypeDef",
    {
        "Words": Sequence[str],
        "VocabularyFilterFileUri": str,
    },
    total=False,
)


class UpdateVocabularyFilterRequestRequestTypeDef(
    _RequiredUpdateVocabularyFilterRequestRequestTypeDef,
    _OptionalUpdateVocabularyFilterRequestRequestTypeDef,
):
    pass


UpdateVocabularyFilterResponseTypeDef = TypedDict(
    "UpdateVocabularyFilterResponseTypeDef",
    {
        "VocabularyFilterName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateVocabularyRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateVocabularyRequestRequestTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
    },
)
_OptionalUpdateVocabularyRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateVocabularyRequestRequestTypeDef",
    {
        "Phrases": Sequence[str],
        "VocabularyFileUri": str,
    },
    total=False,
)


class UpdateVocabularyRequestRequestTypeDef(
    _RequiredUpdateVocabularyRequestRequestTypeDef, _OptionalUpdateVocabularyRequestRequestTypeDef
):
    pass


UpdateVocabularyResponseTypeDef = TypedDict(
    "UpdateVocabularyResponseTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
        "VocabularyState": VocabularyStateType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

VocabularyFilterInfoTypeDef = TypedDict(
    "VocabularyFilterInfoTypeDef",
    {
        "VocabularyFilterName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
    },
    total=False,
)

VocabularyInfoTypeDef = TypedDict(
    "VocabularyInfoTypeDef",
    {
        "VocabularyName": str,
        "LanguageCode": LanguageCodeType,
        "LastModifiedTime": datetime,
        "VocabularyState": VocabularyStateType,
    },
    total=False,
)
