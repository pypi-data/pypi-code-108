"""
Type annotations for mediaconvert service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_mediaconvert import MediaConvertClient

    client: MediaConvertClient = boto3.client("mediaconvert")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    BillingTagsSourceType,
    DescribeEndpointsModeType,
    JobStatusType,
    JobTemplateListByType,
    OrderType,
    PresetListByType,
    PricingPlanType,
    QueueListByType,
    QueueStatusType,
    SimulateReservedQueueType,
    StatusUpdateIntervalType,
)
from .paginator import (
    DescribeEndpointsPaginator,
    ListJobsPaginator,
    ListJobTemplatesPaginator,
    ListPresetsPaginator,
    ListQueuesPaginator,
)
from .type_defs import (
    AccelerationSettingsTypeDef,
    CreateJobResponseTypeDef,
    CreateJobTemplateResponseTypeDef,
    CreatePresetResponseTypeDef,
    CreateQueueResponseTypeDef,
    DescribeEndpointsResponseTypeDef,
    GetJobResponseTypeDef,
    GetJobTemplateResponseTypeDef,
    GetPolicyResponseTypeDef,
    GetPresetResponseTypeDef,
    GetQueueResponseTypeDef,
    HopDestinationTypeDef,
    JobSettingsTypeDef,
    JobTemplateSettingsTypeDef,
    ListJobsResponseTypeDef,
    ListJobTemplatesResponseTypeDef,
    ListPresetsResponseTypeDef,
    ListQueuesResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    PolicyTypeDef,
    PresetSettingsTypeDef,
    PutPolicyResponseTypeDef,
    ReservationPlanSettingsTypeDef,
    UpdateJobTemplateResponseTypeDef,
    UpdatePresetResponseTypeDef,
    UpdateQueueResponseTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("MediaConvertClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    BadRequestException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    ForbiddenException: Type[BotocoreClientError]
    InternalServerErrorException: Type[BotocoreClientError]
    NotFoundException: Type[BotocoreClientError]
    TooManyRequestsException: Type[BotocoreClientError]


class MediaConvertClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        MediaConvertClient exceptions.
        """

    def associate_certificate(self, *, Arn: str) -> Dict[str, Any]:
        """
        Associates an AWS Certificate Manager (ACM) Amazon Resource Name (ARN) with AWS
        Elemental MediaConvert.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.associate_certificate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#associate_certificate)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#can_paginate)
        """

    def cancel_job(self, *, Id: str) -> Dict[str, Any]:
        """
        Permanently cancel a job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.cancel_job)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#cancel_job)
        """

    def create_job(
        self,
        *,
        Role: str,
        Settings: "JobSettingsTypeDef",
        AccelerationSettings: "AccelerationSettingsTypeDef" = ...,
        BillingTagsSource: BillingTagsSourceType = ...,
        ClientRequestToken: str = ...,
        HopDestinations: Sequence["HopDestinationTypeDef"] = ...,
        JobTemplate: str = ...,
        Priority: int = ...,
        Queue: str = ...,
        SimulateReservedQueue: SimulateReservedQueueType = ...,
        StatusUpdateInterval: StatusUpdateIntervalType = ...,
        Tags: Mapping[str, str] = ...,
        UserMetadata: Mapping[str, str] = ...
    ) -> CreateJobResponseTypeDef:
        """
        Create a new transcoding job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.create_job)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#create_job)
        """

    def create_job_template(
        self,
        *,
        Name: str,
        Settings: "JobTemplateSettingsTypeDef",
        AccelerationSettings: "AccelerationSettingsTypeDef" = ...,
        Category: str = ...,
        Description: str = ...,
        HopDestinations: Sequence["HopDestinationTypeDef"] = ...,
        Priority: int = ...,
        Queue: str = ...,
        StatusUpdateInterval: StatusUpdateIntervalType = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateJobTemplateResponseTypeDef:
        """
        Create a new job template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.create_job_template)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#create_job_template)
        """

    def create_preset(
        self,
        *,
        Name: str,
        Settings: "PresetSettingsTypeDef",
        Category: str = ...,
        Description: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreatePresetResponseTypeDef:
        """
        Create a new preset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.create_preset)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#create_preset)
        """

    def create_queue(
        self,
        *,
        Name: str,
        Description: str = ...,
        PricingPlan: PricingPlanType = ...,
        ReservationPlanSettings: "ReservationPlanSettingsTypeDef" = ...,
        Status: QueueStatusType = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateQueueResponseTypeDef:
        """
        Create a new transcoding queue.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.create_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#create_queue)
        """

    def delete_job_template(self, *, Name: str) -> Dict[str, Any]:
        """
        Permanently delete a job template you have created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.delete_job_template)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#delete_job_template)
        """

    def delete_policy(self) -> Dict[str, Any]:
        """
        Permanently delete a policy that you created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.delete_policy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#delete_policy)
        """

    def delete_preset(self, *, Name: str) -> Dict[str, Any]:
        """
        Permanently delete a preset you have created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.delete_preset)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#delete_preset)
        """

    def delete_queue(self, *, Name: str) -> Dict[str, Any]:
        """
        Permanently delete a queue you have created.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.delete_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#delete_queue)
        """

    def describe_endpoints(
        self, *, MaxResults: int = ..., Mode: DescribeEndpointsModeType = ..., NextToken: str = ...
    ) -> DescribeEndpointsResponseTypeDef:
        """
        Send an request with an empty body to the regional API endpoint to get your
        account API endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.describe_endpoints)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#describe_endpoints)
        """

    def disassociate_certificate(self, *, Arn: str) -> Dict[str, Any]:
        """
        Removes an association between the Amazon Resource Name (ARN) of an AWS
        Certificate Manager (ACM) certificate and an AWS Elemental MediaConvert
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.disassociate_certificate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#disassociate_certificate)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#generate_presigned_url)
        """

    def get_job(self, *, Id: str) -> GetJobResponseTypeDef:
        """
        Retrieve the JSON for a specific completed transcoding job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.get_job)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#get_job)
        """

    def get_job_template(self, *, Name: str) -> GetJobTemplateResponseTypeDef:
        """
        Retrieve the JSON for a specific job template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.get_job_template)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#get_job_template)
        """

    def get_policy(self) -> GetPolicyResponseTypeDef:
        """
        Retrieve the JSON for your policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.get_policy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#get_policy)
        """

    def get_preset(self, *, Name: str) -> GetPresetResponseTypeDef:
        """
        Retrieve the JSON for a specific preset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.get_preset)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#get_preset)
        """

    def get_queue(self, *, Name: str) -> GetQueueResponseTypeDef:
        """
        Retrieve the JSON for a specific queue.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.get_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#get_queue)
        """

    def list_job_templates(
        self,
        *,
        Category: str = ...,
        ListBy: JobTemplateListByType = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        Order: OrderType = ...
    ) -> ListJobTemplatesResponseTypeDef:
        """
        Retrieve a JSON array of up to twenty of your job templates.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.list_job_templates)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#list_job_templates)
        """

    def list_jobs(
        self,
        *,
        MaxResults: int = ...,
        NextToken: str = ...,
        Order: OrderType = ...,
        Queue: str = ...,
        Status: JobStatusType = ...
    ) -> ListJobsResponseTypeDef:
        """
        Retrieve a JSON array of up to twenty of your most recently created jobs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.list_jobs)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#list_jobs)
        """

    def list_presets(
        self,
        *,
        Category: str = ...,
        ListBy: PresetListByType = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        Order: OrderType = ...
    ) -> ListPresetsResponseTypeDef:
        """
        Retrieve a JSON array of up to twenty of your presets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.list_presets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#list_presets)
        """

    def list_queues(
        self,
        *,
        ListBy: QueueListByType = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        Order: OrderType = ...
    ) -> ListQueuesResponseTypeDef:
        """
        Retrieve a JSON array of up to twenty of your queues.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.list_queues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#list_queues)
        """

    def list_tags_for_resource(self, *, Arn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Retrieve the tags for a MediaConvert resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#list_tags_for_resource)
        """

    def put_policy(self, *, Policy: "PolicyTypeDef") -> PutPolicyResponseTypeDef:
        """
        Create or change your policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.put_policy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#put_policy)
        """

    def tag_resource(self, *, Arn: str, Tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Add tags to a MediaConvert queue, preset, or job template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#tag_resource)
        """

    def untag_resource(self, *, Arn: str, TagKeys: Sequence[str] = ...) -> Dict[str, Any]:
        """
        Remove tags from a MediaConvert queue, preset, or job template.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#untag_resource)
        """

    def update_job_template(
        self,
        *,
        Name: str,
        AccelerationSettings: "AccelerationSettingsTypeDef" = ...,
        Category: str = ...,
        Description: str = ...,
        HopDestinations: Sequence["HopDestinationTypeDef"] = ...,
        Priority: int = ...,
        Queue: str = ...,
        Settings: "JobTemplateSettingsTypeDef" = ...,
        StatusUpdateInterval: StatusUpdateIntervalType = ...
    ) -> UpdateJobTemplateResponseTypeDef:
        """
        Modify one of your existing job templates.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.update_job_template)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#update_job_template)
        """

    def update_preset(
        self,
        *,
        Name: str,
        Category: str = ...,
        Description: str = ...,
        Settings: "PresetSettingsTypeDef" = ...
    ) -> UpdatePresetResponseTypeDef:
        """
        Modify one of your existing presets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.update_preset)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#update_preset)
        """

    def update_queue(
        self,
        *,
        Name: str,
        Description: str = ...,
        ReservationPlanSettings: "ReservationPlanSettingsTypeDef" = ...,
        Status: QueueStatusType = ...
    ) -> UpdateQueueResponseTypeDef:
        """
        Modify one of your existing queues.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Client.update_queue)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/client.html#update_queue)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_endpoints"]
    ) -> DescribeEndpointsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Paginator.DescribeEndpoints)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/paginators.html#describeendpointspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_job_templates"]
    ) -> ListJobTemplatesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Paginator.ListJobTemplates)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/paginators.html#listjobtemplatespaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_jobs"]) -> ListJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Paginator.ListJobs)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/paginators.html#listjobspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_presets"]) -> ListPresetsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Paginator.ListPresets)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/paginators.html#listpresetspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_queues"]) -> ListQueuesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.41/reference/services/mediaconvert.html#MediaConvert.Paginator.ListQueues)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediaconvert/paginators.html#listqueuespaginator)
        """
