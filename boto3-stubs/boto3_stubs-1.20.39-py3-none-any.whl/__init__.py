import importlib.util
import logging
import sys
from typing import Any, Optional, Union, overload

import boto3.session
from boto3.session import Session
from botocore.config import Config

try:
    from mypy_boto3_accessanalyzer.client import AccessAnalyzerClient
except ModuleNotFoundError:
    AccessAnalyzerClient = Any

try:
    from mypy_boto3_account.client import AccountClient
except ModuleNotFoundError:
    AccountClient = Any

try:
    from mypy_boto3_acm.client import ACMClient
except ModuleNotFoundError:
    ACMClient = Any

try:
    from mypy_boto3_acm_pca.client import ACMPCAClient
except ModuleNotFoundError:
    ACMPCAClient = Any

try:
    from mypy_boto3_alexaforbusiness.client import AlexaForBusinessClient
except ModuleNotFoundError:
    AlexaForBusinessClient = Any

try:
    from mypy_boto3_amp.client import PrometheusServiceClient
except ModuleNotFoundError:
    PrometheusServiceClient = Any

try:
    from mypy_boto3_amplify.client import AmplifyClient
except ModuleNotFoundError:
    AmplifyClient = Any

try:
    from mypy_boto3_amplifybackend.client import AmplifyBackendClient
except ModuleNotFoundError:
    AmplifyBackendClient = Any

try:
    from mypy_boto3_amplifyuibuilder.client import AmplifyUIBuilderClient
except ModuleNotFoundError:
    AmplifyUIBuilderClient = Any

try:
    from mypy_boto3_apigateway.client import APIGatewayClient
except ModuleNotFoundError:
    APIGatewayClient = Any

try:
    from mypy_boto3_apigatewaymanagementapi.client import ApiGatewayManagementApiClient
except ModuleNotFoundError:
    ApiGatewayManagementApiClient = Any

try:
    from mypy_boto3_apigatewayv2.client import ApiGatewayV2Client
except ModuleNotFoundError:
    ApiGatewayV2Client = Any

try:
    from mypy_boto3_appconfig.client import AppConfigClient
except ModuleNotFoundError:
    AppConfigClient = Any

try:
    from mypy_boto3_appconfigdata.client import AppConfigDataClient
except ModuleNotFoundError:
    AppConfigDataClient = Any

try:
    from mypy_boto3_appflow.client import AppflowClient
except ModuleNotFoundError:
    AppflowClient = Any

try:
    from mypy_boto3_appintegrations.client import AppIntegrationsServiceClient
except ModuleNotFoundError:
    AppIntegrationsServiceClient = Any

try:
    from mypy_boto3_application_autoscaling.client import ApplicationAutoScalingClient
except ModuleNotFoundError:
    ApplicationAutoScalingClient = Any

try:
    from mypy_boto3_application_insights.client import ApplicationInsightsClient
except ModuleNotFoundError:
    ApplicationInsightsClient = Any

try:
    from mypy_boto3_applicationcostprofiler.client import ApplicationCostProfilerClient
except ModuleNotFoundError:
    ApplicationCostProfilerClient = Any

try:
    from mypy_boto3_appmesh.client import AppMeshClient
except ModuleNotFoundError:
    AppMeshClient = Any

try:
    from mypy_boto3_apprunner.client import AppRunnerClient
except ModuleNotFoundError:
    AppRunnerClient = Any

try:
    from mypy_boto3_appstream.client import AppStreamClient
except ModuleNotFoundError:
    AppStreamClient = Any

try:
    from mypy_boto3_appsync.client import AppSyncClient
except ModuleNotFoundError:
    AppSyncClient = Any

try:
    from mypy_boto3_athena.client import AthenaClient
except ModuleNotFoundError:
    AthenaClient = Any

try:
    from mypy_boto3_auditmanager.client import AuditManagerClient
except ModuleNotFoundError:
    AuditManagerClient = Any

try:
    from mypy_boto3_autoscaling.client import AutoScalingClient
except ModuleNotFoundError:
    AutoScalingClient = Any

try:
    from mypy_boto3_autoscaling_plans.client import AutoScalingPlansClient
except ModuleNotFoundError:
    AutoScalingPlansClient = Any

try:
    from mypy_boto3_backup.client import BackupClient
except ModuleNotFoundError:
    BackupClient = Any

try:
    from mypy_boto3_backup_gateway.client import BackupGatewayClient
except ModuleNotFoundError:
    BackupGatewayClient = Any

try:
    from mypy_boto3_batch.client import BatchClient
except ModuleNotFoundError:
    BatchClient = Any

try:
    from mypy_boto3_braket.client import BraketClient
except ModuleNotFoundError:
    BraketClient = Any

try:
    from mypy_boto3_budgets.client import BudgetsClient
except ModuleNotFoundError:
    BudgetsClient = Any

try:
    from mypy_boto3_ce.client import CostExplorerClient
except ModuleNotFoundError:
    CostExplorerClient = Any

try:
    from mypy_boto3_chime.client import ChimeClient
except ModuleNotFoundError:
    ChimeClient = Any

try:
    from mypy_boto3_chime_sdk_identity.client import ChimeSDKIdentityClient
except ModuleNotFoundError:
    ChimeSDKIdentityClient = Any

try:
    from mypy_boto3_chime_sdk_meetings.client import ChimeSDKMeetingsClient
except ModuleNotFoundError:
    ChimeSDKMeetingsClient = Any

try:
    from mypy_boto3_chime_sdk_messaging.client import ChimeSDKMessagingClient
except ModuleNotFoundError:
    ChimeSDKMessagingClient = Any

try:
    from mypy_boto3_cloud9.client import Cloud9Client
except ModuleNotFoundError:
    Cloud9Client = Any

try:
    from mypy_boto3_cloudcontrol.client import CloudControlApiClient
except ModuleNotFoundError:
    CloudControlApiClient = Any

try:
    from mypy_boto3_clouddirectory.client import CloudDirectoryClient
except ModuleNotFoundError:
    CloudDirectoryClient = Any

try:
    from mypy_boto3_cloudformation.client import CloudFormationClient
except ModuleNotFoundError:
    CloudFormationClient = Any

try:
    from mypy_boto3_cloudformation.service_resource import CloudFormationServiceResource
except ModuleNotFoundError:
    CloudFormationServiceResource = Any

try:
    from mypy_boto3_cloudfront.client import CloudFrontClient
except ModuleNotFoundError:
    CloudFrontClient = Any

try:
    from mypy_boto3_cloudhsm.client import CloudHSMClient
except ModuleNotFoundError:
    CloudHSMClient = Any

try:
    from mypy_boto3_cloudhsmv2.client import CloudHSMV2Client
except ModuleNotFoundError:
    CloudHSMV2Client = Any

try:
    from mypy_boto3_cloudsearch.client import CloudSearchClient
except ModuleNotFoundError:
    CloudSearchClient = Any

try:
    from mypy_boto3_cloudsearchdomain.client import CloudSearchDomainClient
except ModuleNotFoundError:
    CloudSearchDomainClient = Any

try:
    from mypy_boto3_cloudtrail.client import CloudTrailClient
except ModuleNotFoundError:
    CloudTrailClient = Any

try:
    from mypy_boto3_cloudwatch.client import CloudWatchClient
except ModuleNotFoundError:
    CloudWatchClient = Any

try:
    from mypy_boto3_cloudwatch.service_resource import CloudWatchServiceResource
except ModuleNotFoundError:
    CloudWatchServiceResource = Any

try:
    from mypy_boto3_codeartifact.client import CodeArtifactClient
except ModuleNotFoundError:
    CodeArtifactClient = Any

try:
    from mypy_boto3_codebuild.client import CodeBuildClient
except ModuleNotFoundError:
    CodeBuildClient = Any

try:
    from mypy_boto3_codecommit.client import CodeCommitClient
except ModuleNotFoundError:
    CodeCommitClient = Any

try:
    from mypy_boto3_codedeploy.client import CodeDeployClient
except ModuleNotFoundError:
    CodeDeployClient = Any

try:
    from mypy_boto3_codeguru_reviewer.client import CodeGuruReviewerClient
except ModuleNotFoundError:
    CodeGuruReviewerClient = Any

try:
    from mypy_boto3_codeguruprofiler.client import CodeGuruProfilerClient
except ModuleNotFoundError:
    CodeGuruProfilerClient = Any

try:
    from mypy_boto3_codepipeline.client import CodePipelineClient
except ModuleNotFoundError:
    CodePipelineClient = Any

try:
    from mypy_boto3_codestar.client import CodeStarClient
except ModuleNotFoundError:
    CodeStarClient = Any

try:
    from mypy_boto3_codestar_connections.client import CodeStarconnectionsClient
except ModuleNotFoundError:
    CodeStarconnectionsClient = Any

try:
    from mypy_boto3_codestar_notifications.client import CodeStarNotificationsClient
except ModuleNotFoundError:
    CodeStarNotificationsClient = Any

try:
    from mypy_boto3_cognito_identity.client import CognitoIdentityClient
except ModuleNotFoundError:
    CognitoIdentityClient = Any

try:
    from mypy_boto3_cognito_idp.client import CognitoIdentityProviderClient
except ModuleNotFoundError:
    CognitoIdentityProviderClient = Any

try:
    from mypy_boto3_cognito_sync.client import CognitoSyncClient
except ModuleNotFoundError:
    CognitoSyncClient = Any

try:
    from mypy_boto3_comprehend.client import ComprehendClient
except ModuleNotFoundError:
    ComprehendClient = Any

try:
    from mypy_boto3_comprehendmedical.client import ComprehendMedicalClient
except ModuleNotFoundError:
    ComprehendMedicalClient = Any

try:
    from mypy_boto3_compute_optimizer.client import ComputeOptimizerClient
except ModuleNotFoundError:
    ComputeOptimizerClient = Any

try:
    from mypy_boto3_config.client import ConfigServiceClient
except ModuleNotFoundError:
    ConfigServiceClient = Any

try:
    from mypy_boto3_connect.client import ConnectClient
except ModuleNotFoundError:
    ConnectClient = Any

try:
    from mypy_boto3_connect_contact_lens.client import ConnectContactLensClient
except ModuleNotFoundError:
    ConnectContactLensClient = Any

try:
    from mypy_boto3_connectparticipant.client import ConnectParticipantClient
except ModuleNotFoundError:
    ConnectParticipantClient = Any

try:
    from mypy_boto3_cur.client import CostandUsageReportServiceClient
except ModuleNotFoundError:
    CostandUsageReportServiceClient = Any

try:
    from mypy_boto3_customer_profiles.client import CustomerProfilesClient
except ModuleNotFoundError:
    CustomerProfilesClient = Any

try:
    from mypy_boto3_databrew.client import GlueDataBrewClient
except ModuleNotFoundError:
    GlueDataBrewClient = Any

try:
    from mypy_boto3_dataexchange.client import DataExchangeClient
except ModuleNotFoundError:
    DataExchangeClient = Any

try:
    from mypy_boto3_datapipeline.client import DataPipelineClient
except ModuleNotFoundError:
    DataPipelineClient = Any

try:
    from mypy_boto3_datasync.client import DataSyncClient
except ModuleNotFoundError:
    DataSyncClient = Any

try:
    from mypy_boto3_dax.client import DAXClient
except ModuleNotFoundError:
    DAXClient = Any

try:
    from mypy_boto3_detective.client import DetectiveClient
except ModuleNotFoundError:
    DetectiveClient = Any

try:
    from mypy_boto3_devicefarm.client import DeviceFarmClient
except ModuleNotFoundError:
    DeviceFarmClient = Any

try:
    from mypy_boto3_devops_guru.client import DevOpsGuruClient
except ModuleNotFoundError:
    DevOpsGuruClient = Any

try:
    from mypy_boto3_directconnect.client import DirectConnectClient
except ModuleNotFoundError:
    DirectConnectClient = Any

try:
    from mypy_boto3_discovery.client import ApplicationDiscoveryServiceClient
except ModuleNotFoundError:
    ApplicationDiscoveryServiceClient = Any

try:
    from mypy_boto3_dlm.client import DLMClient
except ModuleNotFoundError:
    DLMClient = Any

try:
    from mypy_boto3_dms.client import DatabaseMigrationServiceClient
except ModuleNotFoundError:
    DatabaseMigrationServiceClient = Any

try:
    from mypy_boto3_docdb.client import DocDBClient
except ModuleNotFoundError:
    DocDBClient = Any

try:
    from mypy_boto3_drs.client import drsClient
except ModuleNotFoundError:
    drsClient = Any

try:
    from mypy_boto3_ds.client import DirectoryServiceClient
except ModuleNotFoundError:
    DirectoryServiceClient = Any

try:
    from mypy_boto3_dynamodb.client import DynamoDBClient
except ModuleNotFoundError:
    DynamoDBClient = Any

try:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
except ModuleNotFoundError:
    DynamoDBServiceResource = Any

try:
    from mypy_boto3_dynamodbstreams.client import DynamoDBStreamsClient
except ModuleNotFoundError:
    DynamoDBStreamsClient = Any

try:
    from mypy_boto3_ebs.client import EBSClient
except ModuleNotFoundError:
    EBSClient = Any

try:
    from mypy_boto3_ec2.client import EC2Client
except ModuleNotFoundError:
    EC2Client = Any

try:
    from mypy_boto3_ec2.service_resource import EC2ServiceResource
except ModuleNotFoundError:
    EC2ServiceResource = Any

try:
    from mypy_boto3_ec2_instance_connect.client import EC2InstanceConnectClient
except ModuleNotFoundError:
    EC2InstanceConnectClient = Any

try:
    from mypy_boto3_ecr.client import ECRClient
except ModuleNotFoundError:
    ECRClient = Any

try:
    from mypy_boto3_ecr_public.client import ECRPublicClient
except ModuleNotFoundError:
    ECRPublicClient = Any

try:
    from mypy_boto3_ecs.client import ECSClient
except ModuleNotFoundError:
    ECSClient = Any

try:
    from mypy_boto3_efs.client import EFSClient
except ModuleNotFoundError:
    EFSClient = Any

try:
    from mypy_boto3_eks.client import EKSClient
except ModuleNotFoundError:
    EKSClient = Any

try:
    from mypy_boto3_elastic_inference.client import ElasticInferenceClient
except ModuleNotFoundError:
    ElasticInferenceClient = Any

try:
    from mypy_boto3_elasticache.client import ElastiCacheClient
except ModuleNotFoundError:
    ElastiCacheClient = Any

try:
    from mypy_boto3_elasticbeanstalk.client import ElasticBeanstalkClient
except ModuleNotFoundError:
    ElasticBeanstalkClient = Any

try:
    from mypy_boto3_elastictranscoder.client import ElasticTranscoderClient
except ModuleNotFoundError:
    ElasticTranscoderClient = Any

try:
    from mypy_boto3_elb.client import ElasticLoadBalancingClient
except ModuleNotFoundError:
    ElasticLoadBalancingClient = Any

try:
    from mypy_boto3_elbv2.client import ElasticLoadBalancingv2Client
except ModuleNotFoundError:
    ElasticLoadBalancingv2Client = Any

try:
    from mypy_boto3_emr.client import EMRClient
except ModuleNotFoundError:
    EMRClient = Any

try:
    from mypy_boto3_emr_containers.client import EMRContainersClient
except ModuleNotFoundError:
    EMRContainersClient = Any

try:
    from mypy_boto3_es.client import ElasticsearchServiceClient
except ModuleNotFoundError:
    ElasticsearchServiceClient = Any

try:
    from mypy_boto3_events.client import EventBridgeClient
except ModuleNotFoundError:
    EventBridgeClient = Any

try:
    from mypy_boto3_evidently.client import CloudWatchEvidentlyClient
except ModuleNotFoundError:
    CloudWatchEvidentlyClient = Any

try:
    from mypy_boto3_finspace.client import finspaceClient
except ModuleNotFoundError:
    finspaceClient = Any

try:
    from mypy_boto3_finspace_data.client import FinSpaceDataClient
except ModuleNotFoundError:
    FinSpaceDataClient = Any

try:
    from mypy_boto3_firehose.client import FirehoseClient
except ModuleNotFoundError:
    FirehoseClient = Any

try:
    from mypy_boto3_fis.client import FISClient
except ModuleNotFoundError:
    FISClient = Any

try:
    from mypy_boto3_fms.client import FMSClient
except ModuleNotFoundError:
    FMSClient = Any

try:
    from mypy_boto3_forecast.client import ForecastServiceClient
except ModuleNotFoundError:
    ForecastServiceClient = Any

try:
    from mypy_boto3_forecastquery.client import ForecastQueryServiceClient
except ModuleNotFoundError:
    ForecastQueryServiceClient = Any

try:
    from mypy_boto3_frauddetector.client import FraudDetectorClient
except ModuleNotFoundError:
    FraudDetectorClient = Any

try:
    from mypy_boto3_fsx.client import FSxClient
except ModuleNotFoundError:
    FSxClient = Any

try:
    from mypy_boto3_gamelift.client import GameLiftClient
except ModuleNotFoundError:
    GameLiftClient = Any

try:
    from mypy_boto3_glacier.client import GlacierClient
except ModuleNotFoundError:
    GlacierClient = Any

try:
    from mypy_boto3_glacier.service_resource import GlacierServiceResource
except ModuleNotFoundError:
    GlacierServiceResource = Any

try:
    from mypy_boto3_globalaccelerator.client import GlobalAcceleratorClient
except ModuleNotFoundError:
    GlobalAcceleratorClient = Any

try:
    from mypy_boto3_glue.client import GlueClient
except ModuleNotFoundError:
    GlueClient = Any

try:
    from mypy_boto3_grafana.client import ManagedGrafanaClient
except ModuleNotFoundError:
    ManagedGrafanaClient = Any

try:
    from mypy_boto3_greengrass.client import GreengrassClient
except ModuleNotFoundError:
    GreengrassClient = Any

try:
    from mypy_boto3_greengrassv2.client import GreengrassV2Client
except ModuleNotFoundError:
    GreengrassV2Client = Any

try:
    from mypy_boto3_groundstation.client import GroundStationClient
except ModuleNotFoundError:
    GroundStationClient = Any

try:
    from mypy_boto3_guardduty.client import GuardDutyClient
except ModuleNotFoundError:
    GuardDutyClient = Any

try:
    from mypy_boto3_health.client import HealthClient
except ModuleNotFoundError:
    HealthClient = Any

try:
    from mypy_boto3_healthlake.client import HealthLakeClient
except ModuleNotFoundError:
    HealthLakeClient = Any

try:
    from mypy_boto3_honeycode.client import HoneycodeClient
except ModuleNotFoundError:
    HoneycodeClient = Any

try:
    from mypy_boto3_iam.client import IAMClient
except ModuleNotFoundError:
    IAMClient = Any

try:
    from mypy_boto3_iam.service_resource import IAMServiceResource
except ModuleNotFoundError:
    IAMServiceResource = Any

try:
    from mypy_boto3_identitystore.client import IdentityStoreClient
except ModuleNotFoundError:
    IdentityStoreClient = Any

try:
    from mypy_boto3_imagebuilder.client import imagebuilderClient
except ModuleNotFoundError:
    imagebuilderClient = Any

try:
    from mypy_boto3_importexport.client import ImportExportClient
except ModuleNotFoundError:
    ImportExportClient = Any

try:
    from mypy_boto3_inspector.client import InspectorClient
except ModuleNotFoundError:
    InspectorClient = Any

try:
    from mypy_boto3_inspector2.client import Inspector2Client
except ModuleNotFoundError:
    Inspector2Client = Any

try:
    from mypy_boto3_iot.client import IoTClient
except ModuleNotFoundError:
    IoTClient = Any

try:
    from mypy_boto3_iot1click_devices.client import IoT1ClickDevicesServiceClient
except ModuleNotFoundError:
    IoT1ClickDevicesServiceClient = Any

try:
    from mypy_boto3_iot1click_projects.client import IoT1ClickProjectsClient
except ModuleNotFoundError:
    IoT1ClickProjectsClient = Any

try:
    from mypy_boto3_iot_data.client import IoTDataPlaneClient
except ModuleNotFoundError:
    IoTDataPlaneClient = Any

try:
    from mypy_boto3_iot_jobs_data.client import IoTJobsDataPlaneClient
except ModuleNotFoundError:
    IoTJobsDataPlaneClient = Any

try:
    from mypy_boto3_iotanalytics.client import IoTAnalyticsClient
except ModuleNotFoundError:
    IoTAnalyticsClient = Any

try:
    from mypy_boto3_iotdeviceadvisor.client import IoTDeviceAdvisorClient
except ModuleNotFoundError:
    IoTDeviceAdvisorClient = Any

try:
    from mypy_boto3_iotevents.client import IoTEventsClient
except ModuleNotFoundError:
    IoTEventsClient = Any

try:
    from mypy_boto3_iotevents_data.client import IoTEventsDataClient
except ModuleNotFoundError:
    IoTEventsDataClient = Any

try:
    from mypy_boto3_iotfleethub.client import IoTFleetHubClient
except ModuleNotFoundError:
    IoTFleetHubClient = Any

try:
    from mypy_boto3_iotsecuretunneling.client import IoTSecureTunnelingClient
except ModuleNotFoundError:
    IoTSecureTunnelingClient = Any

try:
    from mypy_boto3_iotsitewise.client import IoTSiteWiseClient
except ModuleNotFoundError:
    IoTSiteWiseClient = Any

try:
    from mypy_boto3_iotthingsgraph.client import IoTThingsGraphClient
except ModuleNotFoundError:
    IoTThingsGraphClient = Any

try:
    from mypy_boto3_iottwinmaker.client import IoTTwinMakerClient
except ModuleNotFoundError:
    IoTTwinMakerClient = Any

try:
    from mypy_boto3_iotwireless.client import IoTWirelessClient
except ModuleNotFoundError:
    IoTWirelessClient = Any

try:
    from mypy_boto3_ivs.client import IVSClient
except ModuleNotFoundError:
    IVSClient = Any

try:
    from mypy_boto3_kafka.client import KafkaClient
except ModuleNotFoundError:
    KafkaClient = Any

try:
    from mypy_boto3_kafkaconnect.client import KafkaConnectClient
except ModuleNotFoundError:
    KafkaConnectClient = Any

try:
    from mypy_boto3_kendra.client import kendraClient
except ModuleNotFoundError:
    kendraClient = Any

try:
    from mypy_boto3_kinesis.client import KinesisClient
except ModuleNotFoundError:
    KinesisClient = Any

try:
    from mypy_boto3_kinesis_video_archived_media.client import KinesisVideoArchivedMediaClient
except ModuleNotFoundError:
    KinesisVideoArchivedMediaClient = Any

try:
    from mypy_boto3_kinesis_video_media.client import KinesisVideoMediaClient
except ModuleNotFoundError:
    KinesisVideoMediaClient = Any

try:
    from mypy_boto3_kinesis_video_signaling.client import KinesisVideoSignalingChannelsClient
except ModuleNotFoundError:
    KinesisVideoSignalingChannelsClient = Any

try:
    from mypy_boto3_kinesisanalytics.client import KinesisAnalyticsClient
except ModuleNotFoundError:
    KinesisAnalyticsClient = Any

try:
    from mypy_boto3_kinesisanalyticsv2.client import KinesisAnalyticsV2Client
except ModuleNotFoundError:
    KinesisAnalyticsV2Client = Any

try:
    from mypy_boto3_kinesisvideo.client import KinesisVideoClient
except ModuleNotFoundError:
    KinesisVideoClient = Any

try:
    from mypy_boto3_kms.client import KMSClient
except ModuleNotFoundError:
    KMSClient = Any

try:
    from mypy_boto3_lakeformation.client import LakeFormationClient
except ModuleNotFoundError:
    LakeFormationClient = Any

try:
    from mypy_boto3_lambda.client import LambdaClient
except ModuleNotFoundError:
    LambdaClient = Any

try:
    from mypy_boto3_lex_models.client import LexModelBuildingServiceClient
except ModuleNotFoundError:
    LexModelBuildingServiceClient = Any

try:
    from mypy_boto3_lex_runtime.client import LexRuntimeServiceClient
except ModuleNotFoundError:
    LexRuntimeServiceClient = Any

try:
    from mypy_boto3_lexv2_models.client import LexModelsV2Client
except ModuleNotFoundError:
    LexModelsV2Client = Any

try:
    from mypy_boto3_lexv2_runtime.client import LexRuntimeV2Client
except ModuleNotFoundError:
    LexRuntimeV2Client = Any

try:
    from mypy_boto3_license_manager.client import LicenseManagerClient
except ModuleNotFoundError:
    LicenseManagerClient = Any

try:
    from mypy_boto3_lightsail.client import LightsailClient
except ModuleNotFoundError:
    LightsailClient = Any

try:
    from mypy_boto3_location.client import LocationServiceClient
except ModuleNotFoundError:
    LocationServiceClient = Any

try:
    from mypy_boto3_logs.client import CloudWatchLogsClient
except ModuleNotFoundError:
    CloudWatchLogsClient = Any

try:
    from mypy_boto3_lookoutequipment.client import LookoutEquipmentClient
except ModuleNotFoundError:
    LookoutEquipmentClient = Any

try:
    from mypy_boto3_lookoutmetrics.client import LookoutMetricsClient
except ModuleNotFoundError:
    LookoutMetricsClient = Any

try:
    from mypy_boto3_lookoutvision.client import LookoutforVisionClient
except ModuleNotFoundError:
    LookoutforVisionClient = Any

try:
    from mypy_boto3_machinelearning.client import MachineLearningClient
except ModuleNotFoundError:
    MachineLearningClient = Any

try:
    from mypy_boto3_macie.client import MacieClient
except ModuleNotFoundError:
    MacieClient = Any

try:
    from mypy_boto3_macie2.client import Macie2Client
except ModuleNotFoundError:
    Macie2Client = Any

try:
    from mypy_boto3_managedblockchain.client import ManagedBlockchainClient
except ModuleNotFoundError:
    ManagedBlockchainClient = Any

try:
    from mypy_boto3_marketplace_catalog.client import MarketplaceCatalogClient
except ModuleNotFoundError:
    MarketplaceCatalogClient = Any

try:
    from mypy_boto3_marketplace_entitlement.client import MarketplaceEntitlementServiceClient
except ModuleNotFoundError:
    MarketplaceEntitlementServiceClient = Any

try:
    from mypy_boto3_marketplacecommerceanalytics.client import MarketplaceCommerceAnalyticsClient
except ModuleNotFoundError:
    MarketplaceCommerceAnalyticsClient = Any

try:
    from mypy_boto3_mediaconnect.client import MediaConnectClient
except ModuleNotFoundError:
    MediaConnectClient = Any

try:
    from mypy_boto3_mediaconvert.client import MediaConvertClient
except ModuleNotFoundError:
    MediaConvertClient = Any

try:
    from mypy_boto3_medialive.client import MediaLiveClient
except ModuleNotFoundError:
    MediaLiveClient = Any

try:
    from mypy_boto3_mediapackage.client import MediaPackageClient
except ModuleNotFoundError:
    MediaPackageClient = Any

try:
    from mypy_boto3_mediapackage_vod.client import MediaPackageVodClient
except ModuleNotFoundError:
    MediaPackageVodClient = Any

try:
    from mypy_boto3_mediastore.client import MediaStoreClient
except ModuleNotFoundError:
    MediaStoreClient = Any

try:
    from mypy_boto3_mediastore_data.client import MediaStoreDataClient
except ModuleNotFoundError:
    MediaStoreDataClient = Any

try:
    from mypy_boto3_mediatailor.client import MediaTailorClient
except ModuleNotFoundError:
    MediaTailorClient = Any

try:
    from mypy_boto3_memorydb.client import MemoryDBClient
except ModuleNotFoundError:
    MemoryDBClient = Any

try:
    from mypy_boto3_meteringmarketplace.client import MarketplaceMeteringClient
except ModuleNotFoundError:
    MarketplaceMeteringClient = Any

try:
    from mypy_boto3_mgh.client import MigrationHubClient
except ModuleNotFoundError:
    MigrationHubClient = Any

try:
    from mypy_boto3_mgn.client import mgnClient
except ModuleNotFoundError:
    mgnClient = Any

try:
    from mypy_boto3_migration_hub_refactor_spaces.client import MigrationHubRefactorSpacesClient
except ModuleNotFoundError:
    MigrationHubRefactorSpacesClient = Any

try:
    from mypy_boto3_migrationhub_config.client import MigrationHubConfigClient
except ModuleNotFoundError:
    MigrationHubConfigClient = Any

try:
    from mypy_boto3_migrationhubstrategy.client import MigrationHubStrategyRecommendationsClient
except ModuleNotFoundError:
    MigrationHubStrategyRecommendationsClient = Any

try:
    from mypy_boto3_mobile.client import MobileClient
except ModuleNotFoundError:
    MobileClient = Any

try:
    from mypy_boto3_mq.client import MQClient
except ModuleNotFoundError:
    MQClient = Any

try:
    from mypy_boto3_mturk.client import MTurkClient
except ModuleNotFoundError:
    MTurkClient = Any

try:
    from mypy_boto3_mwaa.client import MWAAClient
except ModuleNotFoundError:
    MWAAClient = Any

try:
    from mypy_boto3_neptune.client import NeptuneClient
except ModuleNotFoundError:
    NeptuneClient = Any

try:
    from mypy_boto3_network_firewall.client import NetworkFirewallClient
except ModuleNotFoundError:
    NetworkFirewallClient = Any

try:
    from mypy_boto3_networkmanager.client import NetworkManagerClient
except ModuleNotFoundError:
    NetworkManagerClient = Any

try:
    from mypy_boto3_nimble.client import NimbleStudioClient
except ModuleNotFoundError:
    NimbleStudioClient = Any

try:
    from mypy_boto3_opensearch.client import OpenSearchServiceClient
except ModuleNotFoundError:
    OpenSearchServiceClient = Any

try:
    from mypy_boto3_opsworks.client import OpsWorksClient
except ModuleNotFoundError:
    OpsWorksClient = Any

try:
    from mypy_boto3_opsworks.service_resource import OpsWorksServiceResource
except ModuleNotFoundError:
    OpsWorksServiceResource = Any

try:
    from mypy_boto3_opsworkscm.client import OpsWorksCMClient
except ModuleNotFoundError:
    OpsWorksCMClient = Any

try:
    from mypy_boto3_organizations.client import OrganizationsClient
except ModuleNotFoundError:
    OrganizationsClient = Any

try:
    from mypy_boto3_outposts.client import OutpostsClient
except ModuleNotFoundError:
    OutpostsClient = Any

try:
    from mypy_boto3_panorama.client import PanoramaClient
except ModuleNotFoundError:
    PanoramaClient = Any

try:
    from mypy_boto3_personalize.client import PersonalizeClient
except ModuleNotFoundError:
    PersonalizeClient = Any

try:
    from mypy_boto3_personalize_events.client import PersonalizeEventsClient
except ModuleNotFoundError:
    PersonalizeEventsClient = Any

try:
    from mypy_boto3_personalize_runtime.client import PersonalizeRuntimeClient
except ModuleNotFoundError:
    PersonalizeRuntimeClient = Any

try:
    from mypy_boto3_pi.client import PIClient
except ModuleNotFoundError:
    PIClient = Any

try:
    from mypy_boto3_pinpoint.client import PinpointClient
except ModuleNotFoundError:
    PinpointClient = Any

try:
    from mypy_boto3_pinpoint_email.client import PinpointEmailClient
except ModuleNotFoundError:
    PinpointEmailClient = Any

try:
    from mypy_boto3_pinpoint_sms_voice.client import PinpointSMSVoiceClient
except ModuleNotFoundError:
    PinpointSMSVoiceClient = Any

try:
    from mypy_boto3_polly.client import PollyClient
except ModuleNotFoundError:
    PollyClient = Any

try:
    from mypy_boto3_pricing.client import PricingClient
except ModuleNotFoundError:
    PricingClient = Any

try:
    from mypy_boto3_proton.client import ProtonClient
except ModuleNotFoundError:
    ProtonClient = Any

try:
    from mypy_boto3_qldb.client import QLDBClient
except ModuleNotFoundError:
    QLDBClient = Any

try:
    from mypy_boto3_qldb_session.client import QLDBSessionClient
except ModuleNotFoundError:
    QLDBSessionClient = Any

try:
    from mypy_boto3_quicksight.client import QuickSightClient
except ModuleNotFoundError:
    QuickSightClient = Any

try:
    from mypy_boto3_ram.client import RAMClient
except ModuleNotFoundError:
    RAMClient = Any

try:
    from mypy_boto3_rbin.client import RecycleBinClient
except ModuleNotFoundError:
    RecycleBinClient = Any

try:
    from mypy_boto3_rds.client import RDSClient
except ModuleNotFoundError:
    RDSClient = Any

try:
    from mypy_boto3_rds_data.client import RDSDataServiceClient
except ModuleNotFoundError:
    RDSDataServiceClient = Any

try:
    from mypy_boto3_redshift.client import RedshiftClient
except ModuleNotFoundError:
    RedshiftClient = Any

try:
    from mypy_boto3_redshift_data.client import RedshiftDataAPIServiceClient
except ModuleNotFoundError:
    RedshiftDataAPIServiceClient = Any

try:
    from mypy_boto3_rekognition.client import RekognitionClient
except ModuleNotFoundError:
    RekognitionClient = Any

try:
    from mypy_boto3_resiliencehub.client import ResilienceHubClient
except ModuleNotFoundError:
    ResilienceHubClient = Any

try:
    from mypy_boto3_resource_groups.client import ResourceGroupsClient
except ModuleNotFoundError:
    ResourceGroupsClient = Any

try:
    from mypy_boto3_resourcegroupstaggingapi.client import ResourceGroupsTaggingAPIClient
except ModuleNotFoundError:
    ResourceGroupsTaggingAPIClient = Any

try:
    from mypy_boto3_robomaker.client import RoboMakerClient
except ModuleNotFoundError:
    RoboMakerClient = Any

try:
    from mypy_boto3_route53.client import Route53Client
except ModuleNotFoundError:
    Route53Client = Any

try:
    from mypy_boto3_route53_recovery_cluster.client import Route53RecoveryClusterClient
except ModuleNotFoundError:
    Route53RecoveryClusterClient = Any

try:
    from mypy_boto3_route53_recovery_control_config.client import Route53RecoveryControlConfigClient
except ModuleNotFoundError:
    Route53RecoveryControlConfigClient = Any

try:
    from mypy_boto3_route53_recovery_readiness.client import Route53RecoveryReadinessClient
except ModuleNotFoundError:
    Route53RecoveryReadinessClient = Any

try:
    from mypy_boto3_route53domains.client import Route53DomainsClient
except ModuleNotFoundError:
    Route53DomainsClient = Any

try:
    from mypy_boto3_route53resolver.client import Route53ResolverClient
except ModuleNotFoundError:
    Route53ResolverClient = Any

try:
    from mypy_boto3_rum.client import CloudWatchRUMClient
except ModuleNotFoundError:
    CloudWatchRUMClient = Any

try:
    from mypy_boto3_s3.client import S3Client
except ModuleNotFoundError:
    S3Client = Any

try:
    from mypy_boto3_s3.service_resource import S3ServiceResource
except ModuleNotFoundError:
    S3ServiceResource = Any

try:
    from mypy_boto3_s3control.client import S3ControlClient
except ModuleNotFoundError:
    S3ControlClient = Any

try:
    from mypy_boto3_s3outposts.client import S3OutpostsClient
except ModuleNotFoundError:
    S3OutpostsClient = Any

try:
    from mypy_boto3_sagemaker.client import SageMakerClient
except ModuleNotFoundError:
    SageMakerClient = Any

try:
    from mypy_boto3_sagemaker_a2i_runtime.client import AugmentedAIRuntimeClient
except ModuleNotFoundError:
    AugmentedAIRuntimeClient = Any

try:
    from mypy_boto3_sagemaker_edge.client import SagemakerEdgeManagerClient
except ModuleNotFoundError:
    SagemakerEdgeManagerClient = Any

try:
    from mypy_boto3_sagemaker_featurestore_runtime.client import SageMakerFeatureStoreRuntimeClient
except ModuleNotFoundError:
    SageMakerFeatureStoreRuntimeClient = Any

try:
    from mypy_boto3_sagemaker_runtime.client import SageMakerRuntimeClient
except ModuleNotFoundError:
    SageMakerRuntimeClient = Any

try:
    from mypy_boto3_savingsplans.client import SavingsPlansClient
except ModuleNotFoundError:
    SavingsPlansClient = Any

try:
    from mypy_boto3_schemas.client import SchemasClient
except ModuleNotFoundError:
    SchemasClient = Any

try:
    from mypy_boto3_sdb.client import SimpleDBClient
except ModuleNotFoundError:
    SimpleDBClient = Any

try:
    from mypy_boto3_secretsmanager.client import SecretsManagerClient
except ModuleNotFoundError:
    SecretsManagerClient = Any

try:
    from mypy_boto3_securityhub.client import SecurityHubClient
except ModuleNotFoundError:
    SecurityHubClient = Any

try:
    from mypy_boto3_serverlessrepo.client import ServerlessApplicationRepositoryClient
except ModuleNotFoundError:
    ServerlessApplicationRepositoryClient = Any

try:
    from mypy_boto3_service_quotas.client import ServiceQuotasClient
except ModuleNotFoundError:
    ServiceQuotasClient = Any

try:
    from mypy_boto3_servicecatalog.client import ServiceCatalogClient
except ModuleNotFoundError:
    ServiceCatalogClient = Any

try:
    from mypy_boto3_servicecatalog_appregistry.client import AppRegistryClient
except ModuleNotFoundError:
    AppRegistryClient = Any

try:
    from mypy_boto3_servicediscovery.client import ServiceDiscoveryClient
except ModuleNotFoundError:
    ServiceDiscoveryClient = Any

try:
    from mypy_boto3_ses.client import SESClient
except ModuleNotFoundError:
    SESClient = Any

try:
    from mypy_boto3_sesv2.client import SESV2Client
except ModuleNotFoundError:
    SESV2Client = Any

try:
    from mypy_boto3_shield.client import ShieldClient
except ModuleNotFoundError:
    ShieldClient = Any

try:
    from mypy_boto3_signer.client import signerClient
except ModuleNotFoundError:
    signerClient = Any

try:
    from mypy_boto3_sms.client import SMSClient
except ModuleNotFoundError:
    SMSClient = Any

try:
    from mypy_boto3_sms_voice.client import PinpointSMSVoiceClient
except ModuleNotFoundError:
    PinpointSMSVoiceClient = Any

try:
    from mypy_boto3_snow_device_management.client import SnowDeviceManagementClient
except ModuleNotFoundError:
    SnowDeviceManagementClient = Any

try:
    from mypy_boto3_snowball.client import SnowballClient
except ModuleNotFoundError:
    SnowballClient = Any

try:
    from mypy_boto3_sns.client import SNSClient
except ModuleNotFoundError:
    SNSClient = Any

try:
    from mypy_boto3_sns.service_resource import SNSServiceResource
except ModuleNotFoundError:
    SNSServiceResource = Any

try:
    from mypy_boto3_sqs.client import SQSClient
except ModuleNotFoundError:
    SQSClient = Any

try:
    from mypy_boto3_sqs.service_resource import SQSServiceResource
except ModuleNotFoundError:
    SQSServiceResource = Any

try:
    from mypy_boto3_ssm.client import SSMClient
except ModuleNotFoundError:
    SSMClient = Any

try:
    from mypy_boto3_ssm_contacts.client import SSMContactsClient
except ModuleNotFoundError:
    SSMContactsClient = Any

try:
    from mypy_boto3_ssm_incidents.client import SSMIncidentsClient
except ModuleNotFoundError:
    SSMIncidentsClient = Any

try:
    from mypy_boto3_sso.client import SSOClient
except ModuleNotFoundError:
    SSOClient = Any

try:
    from mypy_boto3_sso_admin.client import SSOAdminClient
except ModuleNotFoundError:
    SSOAdminClient = Any

try:
    from mypy_boto3_sso_oidc.client import SSOOIDCClient
except ModuleNotFoundError:
    SSOOIDCClient = Any

try:
    from mypy_boto3_stepfunctions.client import SFNClient
except ModuleNotFoundError:
    SFNClient = Any

try:
    from mypy_boto3_storagegateway.client import StorageGatewayClient
except ModuleNotFoundError:
    StorageGatewayClient = Any

try:
    from mypy_boto3_sts.client import STSClient
except ModuleNotFoundError:
    STSClient = Any

try:
    from mypy_boto3_support.client import SupportClient
except ModuleNotFoundError:
    SupportClient = Any

try:
    from mypy_boto3_swf.client import SWFClient
except ModuleNotFoundError:
    SWFClient = Any

try:
    from mypy_boto3_synthetics.client import SyntheticsClient
except ModuleNotFoundError:
    SyntheticsClient = Any

try:
    from mypy_boto3_textract.client import TextractClient
except ModuleNotFoundError:
    TextractClient = Any

try:
    from mypy_boto3_timestream_query.client import TimestreamQueryClient
except ModuleNotFoundError:
    TimestreamQueryClient = Any

try:
    from mypy_boto3_timestream_write.client import TimestreamWriteClient
except ModuleNotFoundError:
    TimestreamWriteClient = Any

try:
    from mypy_boto3_transcribe.client import TranscribeServiceClient
except ModuleNotFoundError:
    TranscribeServiceClient = Any

try:
    from mypy_boto3_transfer.client import TransferClient
except ModuleNotFoundError:
    TransferClient = Any

try:
    from mypy_boto3_translate.client import TranslateClient
except ModuleNotFoundError:
    TranslateClient = Any

try:
    from mypy_boto3_voice_id.client import VoiceIDClient
except ModuleNotFoundError:
    VoiceIDClient = Any

try:
    from mypy_boto3_waf.client import WAFClient
except ModuleNotFoundError:
    WAFClient = Any

try:
    from mypy_boto3_waf_regional.client import WAFRegionalClient
except ModuleNotFoundError:
    WAFRegionalClient = Any

try:
    from mypy_boto3_wafv2.client import WAFV2Client
except ModuleNotFoundError:
    WAFV2Client = Any

try:
    from mypy_boto3_wellarchitected.client import WellArchitectedClient
except ModuleNotFoundError:
    WellArchitectedClient = Any

try:
    from mypy_boto3_wisdom.client import ConnectWisdomServiceClient
except ModuleNotFoundError:
    ConnectWisdomServiceClient = Any

try:
    from mypy_boto3_workdocs.client import WorkDocsClient
except ModuleNotFoundError:
    WorkDocsClient = Any

try:
    from mypy_boto3_worklink.client import WorkLinkClient
except ModuleNotFoundError:
    WorkLinkClient = Any

try:
    from mypy_boto3_workmail.client import WorkMailClient
except ModuleNotFoundError:
    WorkMailClient = Any

try:
    from mypy_boto3_workmailmessageflow.client import WorkMailMessageFlowClient
except ModuleNotFoundError:
    WorkMailMessageFlowClient = Any

try:
    from mypy_boto3_workspaces.client import WorkSpacesClient
except ModuleNotFoundError:
    WorkSpacesClient = Any

try:
    from mypy_boto3_workspaces_web.client import WorkSpacesWebClient
except ModuleNotFoundError:
    WorkSpacesWebClient = Any

try:
    from mypy_boto3_xray.client import XRayClient
except ModuleNotFoundError:
    XRayClient = Any

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
__all__ = (
    "DEFAULT_SESSION",
    "NullHandler",
    "Session",
    "client",
    "resource",
    "session",
    "set_stream_logger",
    "setup_default_session",
)

__author__: str
__version__: str

DEFAULT_SESSION: Optional[Session] = None


def setup_default_session(
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_session_token: str = None,
    region_name: str = None,
    botocore_session: str = None,
    profile_name: str = None,
) -> Session:
    ...


def set_stream_logger(
    name: str = "boto3", level: int = logging.DEBUG, format_string: Optional[str] = None
) -> None:
    ...


def _get_default_session() -> Session:
    ...


class NullHandler(logging.Handler):
    def emit(self, record: Any) -> Any:
        ...


@overload
def client(
    service_name: Literal["accessanalyzer"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AccessAnalyzerClient:
    ...


@overload
def client(
    service_name: Literal["account"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AccountClient:
    ...


@overload
def client(
    service_name: Literal["acm"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ACMClient:
    ...


@overload
def client(
    service_name: Literal["acm-pca"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ACMPCAClient:
    ...


@overload
def client(
    service_name: Literal["alexaforbusiness"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AlexaForBusinessClient:
    ...


@overload
def client(
    service_name: Literal["amp"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PrometheusServiceClient:
    ...


@overload
def client(
    service_name: Literal["amplify"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AmplifyClient:
    ...


@overload
def client(
    service_name: Literal["amplifybackend"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AmplifyBackendClient:
    ...


@overload
def client(
    service_name: Literal["amplifyuibuilder"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AmplifyUIBuilderClient:
    ...


@overload
def client(
    service_name: Literal["apigateway"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> APIGatewayClient:
    ...


@overload
def client(
    service_name: Literal["apigatewaymanagementapi"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ApiGatewayManagementApiClient:
    ...


@overload
def client(
    service_name: Literal["apigatewayv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ApiGatewayV2Client:
    ...


@overload
def client(
    service_name: Literal["appconfig"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppConfigClient:
    ...


@overload
def client(
    service_name: Literal["appconfigdata"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppConfigDataClient:
    ...


@overload
def client(
    service_name: Literal["appflow"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppflowClient:
    ...


@overload
def client(
    service_name: Literal["appintegrations"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppIntegrationsServiceClient:
    ...


@overload
def client(
    service_name: Literal["application-autoscaling"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ApplicationAutoScalingClient:
    ...


@overload
def client(
    service_name: Literal["application-insights"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ApplicationInsightsClient:
    ...


@overload
def client(
    service_name: Literal["applicationcostprofiler"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ApplicationCostProfilerClient:
    ...


@overload
def client(
    service_name: Literal["appmesh"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppMeshClient:
    ...


@overload
def client(
    service_name: Literal["apprunner"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppRunnerClient:
    ...


@overload
def client(
    service_name: Literal["appstream"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppStreamClient:
    ...


@overload
def client(
    service_name: Literal["appsync"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppSyncClient:
    ...


@overload
def client(
    service_name: Literal["athena"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AthenaClient:
    ...


@overload
def client(
    service_name: Literal["auditmanager"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AuditManagerClient:
    ...


@overload
def client(
    service_name: Literal["autoscaling"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AutoScalingClient:
    ...


@overload
def client(
    service_name: Literal["autoscaling-plans"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AutoScalingPlansClient:
    ...


@overload
def client(
    service_name: Literal["backup"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> BackupClient:
    ...


@overload
def client(
    service_name: Literal["backup-gateway"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> BackupGatewayClient:
    ...


@overload
def client(
    service_name: Literal["batch"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> BatchClient:
    ...


@overload
def client(
    service_name: Literal["braket"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> BraketClient:
    ...


@overload
def client(
    service_name: Literal["budgets"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> BudgetsClient:
    ...


@overload
def client(
    service_name: Literal["ce"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CostExplorerClient:
    ...


@overload
def client(
    service_name: Literal["chime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ChimeClient:
    ...


@overload
def client(
    service_name: Literal["chime-sdk-identity"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ChimeSDKIdentityClient:
    ...


@overload
def client(
    service_name: Literal["chime-sdk-meetings"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ChimeSDKMeetingsClient:
    ...


@overload
def client(
    service_name: Literal["chime-sdk-messaging"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ChimeSDKMessagingClient:
    ...


@overload
def client(
    service_name: Literal["cloud9"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Cloud9Client:
    ...


@overload
def client(
    service_name: Literal["cloudcontrol"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudControlApiClient:
    ...


@overload
def client(
    service_name: Literal["clouddirectory"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudDirectoryClient:
    ...


@overload
def client(
    service_name: Literal["cloudformation"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudFormationClient:
    ...


@overload
def client(
    service_name: Literal["cloudfront"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudFrontClient:
    ...


@overload
def client(
    service_name: Literal["cloudhsm"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudHSMClient:
    ...


@overload
def client(
    service_name: Literal["cloudhsmv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudHSMV2Client:
    ...


@overload
def client(
    service_name: Literal["cloudsearch"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudSearchClient:
    ...


@overload
def client(
    service_name: Literal["cloudsearchdomain"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudSearchDomainClient:
    ...


@overload
def client(
    service_name: Literal["cloudtrail"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudTrailClient:
    ...


@overload
def client(
    service_name: Literal["cloudwatch"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudWatchClient:
    ...


@overload
def client(
    service_name: Literal["codeartifact"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeArtifactClient:
    ...


@overload
def client(
    service_name: Literal["codebuild"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeBuildClient:
    ...


@overload
def client(
    service_name: Literal["codecommit"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeCommitClient:
    ...


@overload
def client(
    service_name: Literal["codedeploy"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeDeployClient:
    ...


@overload
def client(
    service_name: Literal["codeguru-reviewer"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeGuruReviewerClient:
    ...


@overload
def client(
    service_name: Literal["codeguruprofiler"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeGuruProfilerClient:
    ...


@overload
def client(
    service_name: Literal["codepipeline"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodePipelineClient:
    ...


@overload
def client(
    service_name: Literal["codestar"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeStarClient:
    ...


@overload
def client(
    service_name: Literal["codestar-connections"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeStarconnectionsClient:
    ...


@overload
def client(
    service_name: Literal["codestar-notifications"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CodeStarNotificationsClient:
    ...


@overload
def client(
    service_name: Literal["cognito-identity"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CognitoIdentityClient:
    ...


@overload
def client(
    service_name: Literal["cognito-idp"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CognitoIdentityProviderClient:
    ...


@overload
def client(
    service_name: Literal["cognito-sync"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CognitoSyncClient:
    ...


@overload
def client(
    service_name: Literal["comprehend"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ComprehendClient:
    ...


@overload
def client(
    service_name: Literal["comprehendmedical"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ComprehendMedicalClient:
    ...


@overload
def client(
    service_name: Literal["compute-optimizer"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ComputeOptimizerClient:
    ...


@overload
def client(
    service_name: Literal["config"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ConfigServiceClient:
    ...


@overload
def client(
    service_name: Literal["connect"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ConnectClient:
    ...


@overload
def client(
    service_name: Literal["connect-contact-lens"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ConnectContactLensClient:
    ...


@overload
def client(
    service_name: Literal["connectparticipant"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ConnectParticipantClient:
    ...


@overload
def client(
    service_name: Literal["cur"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CostandUsageReportServiceClient:
    ...


@overload
def client(
    service_name: Literal["customer-profiles"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CustomerProfilesClient:
    ...


@overload
def client(
    service_name: Literal["databrew"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GlueDataBrewClient:
    ...


@overload
def client(
    service_name: Literal["dataexchange"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DataExchangeClient:
    ...


@overload
def client(
    service_name: Literal["datapipeline"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DataPipelineClient:
    ...


@overload
def client(
    service_name: Literal["datasync"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DataSyncClient:
    ...


@overload
def client(
    service_name: Literal["dax"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DAXClient:
    ...


@overload
def client(
    service_name: Literal["detective"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DetectiveClient:
    ...


@overload
def client(
    service_name: Literal["devicefarm"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DeviceFarmClient:
    ...


@overload
def client(
    service_name: Literal["devops-guru"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DevOpsGuruClient:
    ...


@overload
def client(
    service_name: Literal["directconnect"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DirectConnectClient:
    ...


@overload
def client(
    service_name: Literal["discovery"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ApplicationDiscoveryServiceClient:
    ...


@overload
def client(
    service_name: Literal["dlm"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DLMClient:
    ...


@overload
def client(
    service_name: Literal["dms"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DatabaseMigrationServiceClient:
    ...


@overload
def client(
    service_name: Literal["docdb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DocDBClient:
    ...


@overload
def client(
    service_name: Literal["drs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> drsClient:
    ...


@overload
def client(
    service_name: Literal["ds"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DirectoryServiceClient:
    ...


@overload
def client(
    service_name: Literal["dynamodb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DynamoDBClient:
    ...


@overload
def client(
    service_name: Literal["dynamodbstreams"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DynamoDBStreamsClient:
    ...


@overload
def client(
    service_name: Literal["ebs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EBSClient:
    ...


@overload
def client(
    service_name: Literal["ec2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EC2Client:
    ...


@overload
def client(
    service_name: Literal["ec2-instance-connect"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EC2InstanceConnectClient:
    ...


@overload
def client(
    service_name: Literal["ecr"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ECRClient:
    ...


@overload
def client(
    service_name: Literal["ecr-public"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ECRPublicClient:
    ...


@overload
def client(
    service_name: Literal["ecs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ECSClient:
    ...


@overload
def client(
    service_name: Literal["efs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EFSClient:
    ...


@overload
def client(
    service_name: Literal["eks"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EKSClient:
    ...


@overload
def client(
    service_name: Literal["elastic-inference"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElasticInferenceClient:
    ...


@overload
def client(
    service_name: Literal["elasticache"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElastiCacheClient:
    ...


@overload
def client(
    service_name: Literal["elasticbeanstalk"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElasticBeanstalkClient:
    ...


@overload
def client(
    service_name: Literal["elastictranscoder"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElasticTranscoderClient:
    ...


@overload
def client(
    service_name: Literal["elb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElasticLoadBalancingClient:
    ...


@overload
def client(
    service_name: Literal["elbv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElasticLoadBalancingv2Client:
    ...


@overload
def client(
    service_name: Literal["emr"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EMRClient:
    ...


@overload
def client(
    service_name: Literal["emr-containers"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EMRContainersClient:
    ...


@overload
def client(
    service_name: Literal["es"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ElasticsearchServiceClient:
    ...


@overload
def client(
    service_name: Literal["events"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EventBridgeClient:
    ...


@overload
def client(
    service_name: Literal["evidently"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudWatchEvidentlyClient:
    ...


@overload
def client(
    service_name: Literal["finspace"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> finspaceClient:
    ...


@overload
def client(
    service_name: Literal["finspace-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> FinSpaceDataClient:
    ...


@overload
def client(
    service_name: Literal["firehose"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> FirehoseClient:
    ...


@overload
def client(
    service_name: Literal["fis"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> FISClient:
    ...


@overload
def client(
    service_name: Literal["fms"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> FMSClient:
    ...


@overload
def client(
    service_name: Literal["forecast"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ForecastServiceClient:
    ...


@overload
def client(
    service_name: Literal["forecastquery"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ForecastQueryServiceClient:
    ...


@overload
def client(
    service_name: Literal["frauddetector"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> FraudDetectorClient:
    ...


@overload
def client(
    service_name: Literal["fsx"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> FSxClient:
    ...


@overload
def client(
    service_name: Literal["gamelift"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GameLiftClient:
    ...


@overload
def client(
    service_name: Literal["glacier"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GlacierClient:
    ...


@overload
def client(
    service_name: Literal["globalaccelerator"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GlobalAcceleratorClient:
    ...


@overload
def client(
    service_name: Literal["glue"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GlueClient:
    ...


@overload
def client(
    service_name: Literal["grafana"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ManagedGrafanaClient:
    ...


@overload
def client(
    service_name: Literal["greengrass"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GreengrassClient:
    ...


@overload
def client(
    service_name: Literal["greengrassv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GreengrassV2Client:
    ...


@overload
def client(
    service_name: Literal["groundstation"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GroundStationClient:
    ...


@overload
def client(
    service_name: Literal["guardduty"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GuardDutyClient:
    ...


@overload
def client(
    service_name: Literal["health"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> HealthClient:
    ...


@overload
def client(
    service_name: Literal["healthlake"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> HealthLakeClient:
    ...


@overload
def client(
    service_name: Literal["honeycode"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> HoneycodeClient:
    ...


@overload
def client(
    service_name: Literal["iam"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IAMClient:
    ...


@overload
def client(
    service_name: Literal["identitystore"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IdentityStoreClient:
    ...


@overload
def client(
    service_name: Literal["imagebuilder"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> imagebuilderClient:
    ...


@overload
def client(
    service_name: Literal["importexport"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ImportExportClient:
    ...


@overload
def client(
    service_name: Literal["inspector"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> InspectorClient:
    ...


@overload
def client(
    service_name: Literal["inspector2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Inspector2Client:
    ...


@overload
def client(
    service_name: Literal["iot"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTClient:
    ...


@overload
def client(
    service_name: Literal["iot-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTDataPlaneClient:
    ...


@overload
def client(
    service_name: Literal["iot-jobs-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTJobsDataPlaneClient:
    ...


@overload
def client(
    service_name: Literal["iot1click-devices"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoT1ClickDevicesServiceClient:
    ...


@overload
def client(
    service_name: Literal["iot1click-projects"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoT1ClickProjectsClient:
    ...


@overload
def client(
    service_name: Literal["iotanalytics"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTAnalyticsClient:
    ...


@overload
def client(
    service_name: Literal["iotdeviceadvisor"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTDeviceAdvisorClient:
    ...


@overload
def client(
    service_name: Literal["iotevents"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTEventsClient:
    ...


@overload
def client(
    service_name: Literal["iotevents-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTEventsDataClient:
    ...


@overload
def client(
    service_name: Literal["iotfleethub"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTFleetHubClient:
    ...


@overload
def client(
    service_name: Literal["iotsecuretunneling"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTSecureTunnelingClient:
    ...


@overload
def client(
    service_name: Literal["iotsitewise"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTSiteWiseClient:
    ...


@overload
def client(
    service_name: Literal["iotthingsgraph"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTThingsGraphClient:
    ...


@overload
def client(
    service_name: Literal["iottwinmaker"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTTwinMakerClient:
    ...


@overload
def client(
    service_name: Literal["iotwireless"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IoTWirelessClient:
    ...


@overload
def client(
    service_name: Literal["ivs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IVSClient:
    ...


@overload
def client(
    service_name: Literal["kafka"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KafkaClient:
    ...


@overload
def client(
    service_name: Literal["kafkaconnect"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KafkaConnectClient:
    ...


@overload
def client(
    service_name: Literal["kendra"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> kendraClient:
    ...


@overload
def client(
    service_name: Literal["kinesis"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisClient:
    ...


@overload
def client(
    service_name: Literal["kinesis-video-archived-media"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisVideoArchivedMediaClient:
    ...


@overload
def client(
    service_name: Literal["kinesis-video-media"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisVideoMediaClient:
    ...


@overload
def client(
    service_name: Literal["kinesis-video-signaling"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisVideoSignalingChannelsClient:
    ...


@overload
def client(
    service_name: Literal["kinesisanalytics"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisAnalyticsClient:
    ...


@overload
def client(
    service_name: Literal["kinesisanalyticsv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisAnalyticsV2Client:
    ...


@overload
def client(
    service_name: Literal["kinesisvideo"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KinesisVideoClient:
    ...


@overload
def client(
    service_name: Literal["kms"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> KMSClient:
    ...


@overload
def client(
    service_name: Literal["lakeformation"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LakeFormationClient:
    ...


@overload
def client(
    service_name: Literal["lambda"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LambdaClient:
    ...


@overload
def client(
    service_name: Literal["lex-models"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LexModelBuildingServiceClient:
    ...


@overload
def client(
    service_name: Literal["lex-runtime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LexRuntimeServiceClient:
    ...


@overload
def client(
    service_name: Literal["lexv2-models"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LexModelsV2Client:
    ...


@overload
def client(
    service_name: Literal["lexv2-runtime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LexRuntimeV2Client:
    ...


@overload
def client(
    service_name: Literal["license-manager"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LicenseManagerClient:
    ...


@overload
def client(
    service_name: Literal["lightsail"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LightsailClient:
    ...


@overload
def client(
    service_name: Literal["location"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LocationServiceClient:
    ...


@overload
def client(
    service_name: Literal["logs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudWatchLogsClient:
    ...


@overload
def client(
    service_name: Literal["lookoutequipment"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LookoutEquipmentClient:
    ...


@overload
def client(
    service_name: Literal["lookoutmetrics"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LookoutMetricsClient:
    ...


@overload
def client(
    service_name: Literal["lookoutvision"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> LookoutforVisionClient:
    ...


@overload
def client(
    service_name: Literal["machinelearning"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MachineLearningClient:
    ...


@overload
def client(
    service_name: Literal["macie"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MacieClient:
    ...


@overload
def client(
    service_name: Literal["macie2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Macie2Client:
    ...


@overload
def client(
    service_name: Literal["managedblockchain"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ManagedBlockchainClient:
    ...


@overload
def client(
    service_name: Literal["marketplace-catalog"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MarketplaceCatalogClient:
    ...


@overload
def client(
    service_name: Literal["marketplace-entitlement"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MarketplaceEntitlementServiceClient:
    ...


@overload
def client(
    service_name: Literal["marketplacecommerceanalytics"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MarketplaceCommerceAnalyticsClient:
    ...


@overload
def client(
    service_name: Literal["mediaconnect"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaConnectClient:
    ...


@overload
def client(
    service_name: Literal["mediaconvert"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaConvertClient:
    ...


@overload
def client(
    service_name: Literal["medialive"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaLiveClient:
    ...


@overload
def client(
    service_name: Literal["mediapackage"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaPackageClient:
    ...


@overload
def client(
    service_name: Literal["mediapackage-vod"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaPackageVodClient:
    ...


@overload
def client(
    service_name: Literal["mediastore"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaStoreClient:
    ...


@overload
def client(
    service_name: Literal["mediastore-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaStoreDataClient:
    ...


@overload
def client(
    service_name: Literal["mediatailor"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MediaTailorClient:
    ...


@overload
def client(
    service_name: Literal["memorydb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MemoryDBClient:
    ...


@overload
def client(
    service_name: Literal["meteringmarketplace"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MarketplaceMeteringClient:
    ...


@overload
def client(
    service_name: Literal["mgh"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MigrationHubClient:
    ...


@overload
def client(
    service_name: Literal["mgn"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> mgnClient:
    ...


@overload
def client(
    service_name: Literal["migration-hub-refactor-spaces"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MigrationHubRefactorSpacesClient:
    ...


@overload
def client(
    service_name: Literal["migrationhub-config"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MigrationHubConfigClient:
    ...


@overload
def client(
    service_name: Literal["migrationhubstrategy"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MigrationHubStrategyRecommendationsClient:
    ...


@overload
def client(
    service_name: Literal["mobile"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MobileClient:
    ...


@overload
def client(
    service_name: Literal["mq"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MQClient:
    ...


@overload
def client(
    service_name: Literal["mturk"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MTurkClient:
    ...


@overload
def client(
    service_name: Literal["mwaa"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> MWAAClient:
    ...


@overload
def client(
    service_name: Literal["neptune"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> NeptuneClient:
    ...


@overload
def client(
    service_name: Literal["network-firewall"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> NetworkFirewallClient:
    ...


@overload
def client(
    service_name: Literal["networkmanager"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> NetworkManagerClient:
    ...


@overload
def client(
    service_name: Literal["nimble"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> NimbleStudioClient:
    ...


@overload
def client(
    service_name: Literal["opensearch"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> OpenSearchServiceClient:
    ...


@overload
def client(
    service_name: Literal["opsworks"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> OpsWorksClient:
    ...


@overload
def client(
    service_name: Literal["opsworkscm"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> OpsWorksCMClient:
    ...


@overload
def client(
    service_name: Literal["organizations"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> OrganizationsClient:
    ...


@overload
def client(
    service_name: Literal["outposts"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> OutpostsClient:
    ...


@overload
def client(
    service_name: Literal["panorama"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PanoramaClient:
    ...


@overload
def client(
    service_name: Literal["personalize"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PersonalizeClient:
    ...


@overload
def client(
    service_name: Literal["personalize-events"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PersonalizeEventsClient:
    ...


@overload
def client(
    service_name: Literal["personalize-runtime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PersonalizeRuntimeClient:
    ...


@overload
def client(
    service_name: Literal["pi"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PIClient:
    ...


@overload
def client(
    service_name: Literal["pinpoint"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PinpointClient:
    ...


@overload
def client(
    service_name: Literal["pinpoint-email"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PinpointEmailClient:
    ...


@overload
def client(
    service_name: Literal["pinpoint-sms-voice"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PinpointSMSVoiceClient:
    ...


@overload
def client(
    service_name: Literal["polly"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PollyClient:
    ...


@overload
def client(
    service_name: Literal["pricing"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PricingClient:
    ...


@overload
def client(
    service_name: Literal["proton"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ProtonClient:
    ...


@overload
def client(
    service_name: Literal["qldb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> QLDBClient:
    ...


@overload
def client(
    service_name: Literal["qldb-session"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> QLDBSessionClient:
    ...


@overload
def client(
    service_name: Literal["quicksight"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> QuickSightClient:
    ...


@overload
def client(
    service_name: Literal["ram"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RAMClient:
    ...


@overload
def client(
    service_name: Literal["rbin"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RecycleBinClient:
    ...


@overload
def client(
    service_name: Literal["rds"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RDSClient:
    ...


@overload
def client(
    service_name: Literal["rds-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RDSDataServiceClient:
    ...


@overload
def client(
    service_name: Literal["redshift"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RedshiftClient:
    ...


@overload
def client(
    service_name: Literal["redshift-data"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RedshiftDataAPIServiceClient:
    ...


@overload
def client(
    service_name: Literal["rekognition"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RekognitionClient:
    ...


@overload
def client(
    service_name: Literal["resiliencehub"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ResilienceHubClient:
    ...


@overload
def client(
    service_name: Literal["resource-groups"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ResourceGroupsClient:
    ...


@overload
def client(
    service_name: Literal["resourcegroupstaggingapi"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ResourceGroupsTaggingAPIClient:
    ...


@overload
def client(
    service_name: Literal["robomaker"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> RoboMakerClient:
    ...


@overload
def client(
    service_name: Literal["route53"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Route53Client:
    ...


@overload
def client(
    service_name: Literal["route53-recovery-cluster"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Route53RecoveryClusterClient:
    ...


@overload
def client(
    service_name: Literal["route53-recovery-control-config"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Route53RecoveryControlConfigClient:
    ...


@overload
def client(
    service_name: Literal["route53-recovery-readiness"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Route53RecoveryReadinessClient:
    ...


@overload
def client(
    service_name: Literal["route53domains"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Route53DomainsClient:
    ...


@overload
def client(
    service_name: Literal["route53resolver"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> Route53ResolverClient:
    ...


@overload
def client(
    service_name: Literal["rum"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudWatchRUMClient:
    ...


@overload
def client(
    service_name: Literal["s3"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> S3Client:
    ...


@overload
def client(
    service_name: Literal["s3control"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> S3ControlClient:
    ...


@overload
def client(
    service_name: Literal["s3outposts"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> S3OutpostsClient:
    ...


@overload
def client(
    service_name: Literal["sagemaker"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SageMakerClient:
    ...


@overload
def client(
    service_name: Literal["sagemaker-a2i-runtime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AugmentedAIRuntimeClient:
    ...


@overload
def client(
    service_name: Literal["sagemaker-edge"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SagemakerEdgeManagerClient:
    ...


@overload
def client(
    service_name: Literal["sagemaker-featurestore-runtime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SageMakerFeatureStoreRuntimeClient:
    ...


@overload
def client(
    service_name: Literal["sagemaker-runtime"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SageMakerRuntimeClient:
    ...


@overload
def client(
    service_name: Literal["savingsplans"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SavingsPlansClient:
    ...


@overload
def client(
    service_name: Literal["schemas"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SchemasClient:
    ...


@overload
def client(
    service_name: Literal["sdb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SimpleDBClient:
    ...


@overload
def client(
    service_name: Literal["secretsmanager"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SecretsManagerClient:
    ...


@overload
def client(
    service_name: Literal["securityhub"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SecurityHubClient:
    ...


@overload
def client(
    service_name: Literal["serverlessrepo"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ServerlessApplicationRepositoryClient:
    ...


@overload
def client(
    service_name: Literal["service-quotas"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ServiceQuotasClient:
    ...


@overload
def client(
    service_name: Literal["servicecatalog"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ServiceCatalogClient:
    ...


@overload
def client(
    service_name: Literal["servicecatalog-appregistry"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> AppRegistryClient:
    ...


@overload
def client(
    service_name: Literal["servicediscovery"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ServiceDiscoveryClient:
    ...


@overload
def client(
    service_name: Literal["ses"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SESClient:
    ...


@overload
def client(
    service_name: Literal["sesv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SESV2Client:
    ...


@overload
def client(
    service_name: Literal["shield"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ShieldClient:
    ...


@overload
def client(
    service_name: Literal["signer"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> signerClient:
    ...


@overload
def client(
    service_name: Literal["sms"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SMSClient:
    ...


@overload
def client(
    service_name: Literal["sms-voice"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> PinpointSMSVoiceClient:
    ...


@overload
def client(
    service_name: Literal["snow-device-management"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SnowDeviceManagementClient:
    ...


@overload
def client(
    service_name: Literal["snowball"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SnowballClient:
    ...


@overload
def client(
    service_name: Literal["sns"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SNSClient:
    ...


@overload
def client(
    service_name: Literal["sqs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SQSClient:
    ...


@overload
def client(
    service_name: Literal["ssm"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SSMClient:
    ...


@overload
def client(
    service_name: Literal["ssm-contacts"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SSMContactsClient:
    ...


@overload
def client(
    service_name: Literal["ssm-incidents"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SSMIncidentsClient:
    ...


@overload
def client(
    service_name: Literal["sso"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SSOClient:
    ...


@overload
def client(
    service_name: Literal["sso-admin"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SSOAdminClient:
    ...


@overload
def client(
    service_name: Literal["sso-oidc"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SSOOIDCClient:
    ...


@overload
def client(
    service_name: Literal["stepfunctions"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SFNClient:
    ...


@overload
def client(
    service_name: Literal["storagegateway"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> StorageGatewayClient:
    ...


@overload
def client(
    service_name: Literal["sts"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> STSClient:
    ...


@overload
def client(
    service_name: Literal["support"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SupportClient:
    ...


@overload
def client(
    service_name: Literal["swf"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SWFClient:
    ...


@overload
def client(
    service_name: Literal["synthetics"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SyntheticsClient:
    ...


@overload
def client(
    service_name: Literal["textract"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> TextractClient:
    ...


@overload
def client(
    service_name: Literal["timestream-query"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> TimestreamQueryClient:
    ...


@overload
def client(
    service_name: Literal["timestream-write"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> TimestreamWriteClient:
    ...


@overload
def client(
    service_name: Literal["transcribe"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> TranscribeServiceClient:
    ...


@overload
def client(
    service_name: Literal["transfer"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> TransferClient:
    ...


@overload
def client(
    service_name: Literal["translate"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> TranslateClient:
    ...


@overload
def client(
    service_name: Literal["voice-id"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> VoiceIDClient:
    ...


@overload
def client(
    service_name: Literal["waf"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WAFClient:
    ...


@overload
def client(
    service_name: Literal["waf-regional"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WAFRegionalClient:
    ...


@overload
def client(
    service_name: Literal["wafv2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WAFV2Client:
    ...


@overload
def client(
    service_name: Literal["wellarchitected"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WellArchitectedClient:
    ...


@overload
def client(
    service_name: Literal["wisdom"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> ConnectWisdomServiceClient:
    ...


@overload
def client(
    service_name: Literal["workdocs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WorkDocsClient:
    ...


@overload
def client(
    service_name: Literal["worklink"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WorkLinkClient:
    ...


@overload
def client(
    service_name: Literal["workmail"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WorkMailClient:
    ...


@overload
def client(
    service_name: Literal["workmailmessageflow"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WorkMailMessageFlowClient:
    ...


@overload
def client(
    service_name: Literal["workspaces"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WorkSpacesClient:
    ...


@overload
def client(
    service_name: Literal["workspaces-web"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> WorkSpacesWebClient:
    ...


@overload
def client(
    service_name: Literal["xray"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> XRayClient:
    ...


@overload
def resource(
    service_name: Literal["cloudformation"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudFormationServiceResource:
    ...


@overload
def resource(
    service_name: Literal["cloudwatch"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> CloudWatchServiceResource:
    ...


@overload
def resource(
    service_name: Literal["dynamodb"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> DynamoDBServiceResource:
    ...


@overload
def resource(
    service_name: Literal["ec2"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> EC2ServiceResource:
    ...


@overload
def resource(
    service_name: Literal["glacier"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> GlacierServiceResource:
    ...


@overload
def resource(
    service_name: Literal["iam"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> IAMServiceResource:
    ...


@overload
def resource(
    service_name: Literal["opsworks"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> OpsWorksServiceResource:
    ...


@overload
def resource(
    service_name: Literal["s3"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> S3ServiceResource:
    ...


@overload
def resource(
    service_name: Literal["sns"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SNSServiceResource:
    ...


@overload
def resource(
    service_name: Literal["sqs"],
    region_name: Optional[str] = ...,
    api_version: Optional[str] = ...,
    use_ssl: Optional[bool] = ...,
    verify: Union[bool, str, None] = ...,
    endpoint_url: Optional[str] = ...,
    aws_access_key_id: Optional[str] = ...,
    aws_secret_access_key: Optional[str] = ...,
    aws_session_token: Optional[str] = ...,
    config: Optional[Config] = ...,
) -> SQSServiceResource:
    ...
