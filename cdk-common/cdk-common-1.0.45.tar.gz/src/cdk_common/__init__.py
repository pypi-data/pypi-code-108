'''
[![NPM version](https://badge.fury.io/js/cdk-common.svg)](https://badge.fury.io/js/cdk-common)
[![PyPI version](https://badge.fury.io/py/cdk-common.svg)](https://badge.fury.io/py/cdk-common)
[![release](https://github.com/neilkuan/cdk-common/actions/workflows/release.yml/badge.svg)](https://github.com/neilkuan/cdk-common/actions/workflows/release.yml)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk-common?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-common?label=pypi&color=blue)

# Welcome to `cdk-common`

This Constructs Library will collection of useful `function` and `class` for AWS CDK.

## Install

```bash
Use the npm dist tag to opt in CDKv1 or CDKv2:

// for CDKv2
npm install cdk-common
or
npm install cdk-common@latest

// for CDKv1
npm install cdk-common@cdkv1
```

### AWS Managed Policies `enum`

```python
import * as cdk from '@aws-cdk/core';
import { AWSManagedPolicies } from 'cdk-common';
const app = new cdk.App();

const stack = new cdk.Stack(app, 'integ-default', { env });

export class IntegDefault extends cdk.Construct {
  constructor(scope: cdk.Construct, id: string ) {
    super(scope, id);

    const role = new iam.Role(this, 'iamrole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
    });
    // Use this way.
    role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName(AWSManagedPolicies.AMAZON_SSM_MANAGED_INSTANCE_CORE));

    // Not this way.
    role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'));
  }
}
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_codeguruprofiler
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_sqs
import aws_cdk.core


@jsii.enum(jsii_type="cdk-common.AWSManagedPolicies")
class AWSManagedPolicies(enum.Enum):
    '''
    :stability: experimental
    '''

    AWSDIRECT_CONNECT_READ_ONLY_ACCESS = "AWSDIRECT_CONNECT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_GLACIER_READ_ONLY_ACCESS = "AMAZON_GLACIER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_FULL_ACCESS = "AWSMARKETPLACE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    CLIENT_VPN_SERVICE_ROLE_POLICY = "CLIENT_VPN_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSSODIRECTORY_ADMINISTRATOR = "AWSSSODIRECTORY_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AWSIO_T1_CLICK_READ_ONLY_ACCESS = "AWSIO_T1_CLICK_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AUTO_SCALING_CONSOLE_READ_ONLY_ACCESS = "AUTO_SCALING_CONSOLE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DMS_REDSHIFT_S3_ROLE = "AMAZON_DMS_REDSHIFT_S3_ROLE"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_LIST_IA_M = "AWSQUICK_SIGHT_LIST_IA_M"
    '''
    :stability: experimental
    '''
    AWSHEALTH_FULL_ACCESS = "AWSHEALTH_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_GATEWAY_EXECUTION = "ALEXA_FOR_BUSINESS_GATEWAY_EXECUTION"
    '''
    :stability: experimental
    '''
    AMAZONELASTICTRANSCODER_READONLYACCESS = "AMAZONELASTICTRANSCODER_READONLYACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_FULL_ACCESS = "AMAZON_RDS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    SUPPORT_USER = "SUPPORT_USER"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_FULL_ACCESS = "AMAZON_E_C2_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    SECRETS_MANAGER_READ_WRITE = "SECRETS_MANAGER_READ_WRITE"
    '''
    :stability: experimental
    '''
    AWSIO_T_THINGS_REGISTRATION = "AWSIO_T_THINGS_REGISTRATION"
    '''
    :stability: experimental
    '''
    AMAZON_DOC_DB_READ_ONLY_ACCESS = "AMAZON_DOC_DB_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MQ_API_FULL_ACCESS = "AMAZON_MQ_API_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_STORE_READ_ONLY = "AWSELEMENTAL_MEDIA_STORE_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_READ_ONLY = "AWSCERTIFICATE_MANAGER_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSQUICKSIGHT_ATHENA_ACCESS = "AWSQUICKSIGHT_ATHENA_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_MAP_REGISTER_INSTANCE_ACCESS = "AWSCLOUD_MAP_REGISTER_INSTANCE_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_IMAGE_BUILD_FULL_ACCESS = "AWSMARKETPLACE_IMAGE_BUILD_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_COMMIT_POWER_USER = "AWSCODE_COMMIT_POWER_USER"
    '''
    :stability: experimental
    '''
    AWSCODE_COMMIT_FULL_ACCESS = "AWSCODE_COMMIT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    IAMSELF_MANAGE_SERVICE_SPECIFIC_CREDENTIALS = "IAMSELF_MANAGE_SERVICE_SPECIFIC_CREDENTIALS"
    '''
    :stability: experimental
    '''
    AMAZON_EMR_CLEANUP_POLICY = "AMAZON_EMR_CLEANUP_POLICY"
    '''
    :stability: experimental
    '''
    AWSCLOUD9_ENVIRONMENT_MEMBER = "AWSCLOUD9_ENVIRONMENT_MEMBER"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_SAGE_MAKER_ENDPOINT_POLICY = "AWSAPPLICATION_AUTOSCALING_SAGE_MAKER_ENDPOINT_POLICY"
    '''
    :stability: experimental
    '''
    FMSSERVICE_ROLE_POLICY = "FMSSERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_SQS_FULL_ACCESS = "AMAZON_SQS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_READ_ONLY_ACCESS = "ALEXA_FOR_BUSINESS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_LOGGING = "AWSIO_T_LOGGING"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_ROLEFOR_SS_M = "AMAZON_E_C2_ROLEFOR_SS_M"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_NETWORK_PROFILE_SERVICE_POLICY = "ALEXA_FOR_BUSINESS_NETWORK_PROFILE_SERVICE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCLOUD_HSM_ROLE = "AWSCLOUD_HSM_ROLE"
    '''
    :stability: experimental
    '''
    AWSENHANCED_CLASSIC_NETWORKING_MANGEMENT_POLICY = "AWSENHANCED_CLASSIC_NETWORKING_MANGEMENT_POLICY"
    '''
    :stability: experimental
    '''
    IAMFULL_ACCESS = "IAMFULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_INSPECTOR_FULL_ACCESS = "AMAZON_INSPECTOR_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTI_CACHE_FULL_ACCESS = "AMAZON_ELASTI_CACHE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAGENTLESS_DISCOVERY_SERVICE = "AWSAGENTLESS_DISCOVERY_SERVICE"
    '''
    :stability: experimental
    '''
    AWSXRAY_WRITE_ONLY_ACCESS = "AWSXRAY_WRITE_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPRICE_LIST_SERVICE_FULL_ACCESS = "AWSPRICE_LIST_SERVICE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSKEY_MANAGEMENT_SERVICE_CUSTOM_KEY_STORES_SERVICE_ROLE_POLICY = "AWSKEY_MANAGEMENT_SERVICE_CUSTOM_KEY_STORES_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AUTO_SCALING_READ_ONLY_ACCESS = "AUTO_SCALING_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_FORECAST_FULL_ACCESS = "AMAZON_FORECAST_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_LINK_READ_ONLY = "AMAZON_WORK_LINK_READ_ONLY"
    '''
    :stability: experimental
    '''
    TRANSLATE_FULL_ACCESS = "TRANSLATE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AUTO_SCALING_FULL_ACCESS = "AUTO_SCALING_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_ROLEFOR_AWS_CODE_DEPLOY = "AMAZON_E_C2_ROLEFOR_AWS_CODE_DEPLOY"
    '''
    :stability: experimental
    '''
    AWSFMMEMBER_READ_ONLY_ACCESS = "AWSFMMEMBER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCE_EDITORS_ROLE = "AMAZON_ELASTIC_MAP_REDUCE_EDITORS_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_CLUSTER_POLICY = "AMAZON_EKS_CLUSTER_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_WORKER_NODE_POLICY = "AMAZON_EKS_WORKER_NODE_POLICY"
    '''
    :stability: experimental
    '''
    AWSMOBILEHUB_READONLY = "AWSMOBILEHUB_READONLY"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_EVENTS_BUILT_IN_TARGET_EXECUTION_ACCESS = "CLOUD_WATCH_EVENTS_BUILT_IN_TARGET_EXECUTION_ACCESS"
    '''
    :stability: experimental
    '''
    AUTO_SCALING_SERVICE_ROLE_POLICY = "AUTO_SCALING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZONELASTICTRANSCODER_FULLACCESS = "AMAZONELASTICTRANSCODER_FULLACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_DIRECTORY_READ_ONLY_ACCESS = "AMAZON_CLOUD_DIRECTORY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_AGENT_ADMIN_POLICY = "CLOUD_WATCH_AGENT_ADMIN_POLICY"
    '''
    :stability: experimental
    '''
    AWSOPS_WORKS_CM_INSTANCE_PROFILE_ROLE = "AWSOPS_WORKS_CM_INSTANCE_PROFILE_ROLE"
    '''
    :stability: experimental
    '''
    AWSBATCH_SERVICE_EVENT_TARGET_ROLE = "AWSBATCH_SERVICE_EVENT_TARGET_ROLE"
    '''
    :stability: experimental
    '''
    AWSCODE_PIPELINE_APPROVER_ACCESS = "AWSCODE_PIPELINE_APPROVER_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_DISCOVERY_AGENT_ACCESS = "AWSAPPLICATION_DISCOVERY_AGENT_ACCESS"
    '''
    :stability: experimental
    '''
    VIEW_ONLY_ACCESS = "VIEW_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCE_ROLE = "AMAZON_ELASTIC_MAP_REDUCE_ROLE"
    '''
    :stability: experimental
    '''
    ELASTIC_LOAD_BALANCING_FULL_ACCESS = "ELASTIC_LOAD_BALANCING_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_DOMAINS_READ_ONLY_ACCESS = "AMAZON_ROUTE53_DOMAINS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_AUTOMATION_APPROVER_ACCESS = "AMAZON_SSM_AUTOMATION_APPROVER_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSECURITY_HUB_READ_ONLY_ACCESS = "AWSSECURITY_HUB_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCONFIG_ROLE_FOR_ORGANIZATIONS = "AWSCONFIG_ROLE_FOR_ORGANIZATIONS"
    '''
    :stability: experimental
    '''
    APPLICATION_AUTO_SCALING_FOR_AMAZON_APP_STREAM_ACCESS = "APPLICATION_AUTO_SCALING_FOR_AMAZON_APP_STREAM_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_REGISTRY_FULL_ACCESS = "AMAZON_E_C2_CONTAINER_REGISTRY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_F_SX_FULL_ACCESS = "AMAZON_F_SX_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    SIMPLE_WORKFLOW_FULL_ACCESS = "SIMPLE_WORKFLOW_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    GREENGRASS_OTA_UPDATE_ARTIFACT_ACCESS = "GREENGRASS_OTA_UPDATE_ARTIFACT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_S3_FULL_ACCESS = "AMAZON_S3_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSTORAGE_GATEWAY_READ_ONLY_ACCESS = "AWSSTORAGE_GATEWAY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    BILLING = "BILLING"
    '''
    :stability: experimental
    '''
    QUICK_SIGHT_ACCESS_FOR_S3_STORAGE_MANAGEMENT_ANALYTICS_READ_ONLY = "QUICK_SIGHT_ACCESS_FOR_S3_STORAGE_MANAGEMENT_ANALYTICS_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_REGISTRY_READ_ONLY = "AMAZON_E_C2_CONTAINER_REGISTRY_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCEFOR_E_C2_ROLE = "AMAZON_ELASTIC_MAP_REDUCEFOR_E_C2_ROLE"
    '''
    :stability: experimental
    '''
    DATABASE_ADMINISTRATOR = "DATABASE_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_READ_ONLY_ACCESS = "AMAZON_REDSHIFT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_READ_ONLY_ACCESS = "AMAZON_E_C2_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_AGENT_SERVER_POLICY = "CLOUD_WATCH_AGENT_SERVER_POLICY"
    '''
    :stability: experimental
    '''
    AWSXRAY_READ_ONLY_ACCESS = "AWSXRAY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ENHANCED_HEALTH = "AWSELASTIC_BEANSTALK_ENHANCED_HEALTH"
    '''
    :stability: experimental
    '''
    WELL_ARCHITECTED_CONSOLE_FULL_ACCESS = "WELL_ARCHITECTED_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCE_READ_ONLY_ACCESS = "AMAZON_ELASTIC_MAP_REDUCE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDIRECTORY_SERVICE_READ_ONLY_ACCESS = "AWSDIRECTORY_SERVICE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSSOMASTER_ACCOUNT_ADMINISTRATOR = "AWSSSOMASTER_ACCOUNT_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AMAZON_GUARD_DUTY_SERVICE_ROLE_POLICY = "AMAZON_GUARD_DUTY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_VPC_READ_ONLY_ACCESS = "AMAZON_VPC_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_SERVICE_ROLE_POLICY = "AWSELASTIC_BEANSTALK_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    SERVER_MIGRATION_SERVICE_LAUNCH_ROLE = "SERVER_MIGRATION_SERVICE_LAUNCH_ROLE"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_ROLE_FOR_EC_S = "AWSCODE_DEPLOY_ROLE_FOR_EC_S"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_EVENTS_READ_ONLY_ACCESS = "CLOUD_WATCH_EVENTS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_REPLICATOR = "AWSLAMBDA_REPLICATOR"
    '''
    :stability: experimental
    '''
    AMAZON_API_GATEWAY_INVOKE_FULL_ACCESS = "AMAZON_API_GATEWAY_INVOKE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSSOSERVICE_ROLE_POLICY = "AWSSSOSERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSLICENSE_MANAGER_MASTER_ACCOUNT_ROLE_POLICY = "AWSLICENSE_MANAGER_MASTER_ACCOUNT_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_ANALYTICS_READ_ONLY = "AMAZON_KINESIS_ANALYTICS_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_MOBILE_ANALYTICS_FULL_ACCESS = "AMAZON_MOBILE_ANALYTICS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMOBILEHUB_FULLACCESS = "AWSMOBILEHUB_FULLACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_API_GATEWAY_PUSH_TO_CLOUD_WATCH_LOGS = "AMAZON_API_GATEWAY_PUSH_TO_CLOUD_WATCH_LOGS"
    '''
    :stability: experimental
    '''
    AWSDATA_PIPELINE_ROLE = "AWSDATA_PIPELINE_ROLE"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_FULL_ACCESS = "CLOUD_WATCH_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MQ_API_READ_ONLY_ACCESS = "AMAZON_MQ_API_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEEP_LENS_LAMBDA_FUNCTION_ACCESS_POLICY = "AWSDEEP_LENS_LAMBDA_FUNCTION_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_GUARD_DUTY_FULL_ACCESS = "AMAZON_GUARD_DUTY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_DIRECTORY_SERVICE_ACCESS = "AMAZON_RDS_DIRECTORY_SERVICE_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_PIPELINE_READ_ONLY_ACCESS = "AWSCODE_PIPELINE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    READ_ONLY_ACCESS = "READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPP_SYNC_INVOKE_FULL_ACCESS = "AWSAPP_SYNC_INVOKE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_BATCH_PREDICTIONS_ACCESS = "AMAZON_MACHINE_LEARNING_BATCH_PREDICTIONS_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_SITE_WISE_FULL_ACCESS = "AWSIO_T_SITE_WISE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_FULL_ACCESS = "ALEXA_FOR_BUSINESS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSEC2_SPOT_FLEET_SERVICE_ROLE_POLICY = "AWSEC2_SPOT_FLEET_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_REKOGNITION_READ_ONLY_ACCESS = "AMAZON_REKOGNITION_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_READ_ONLY_ACCESS = "AWSCODE_DEPLOY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_SEARCH_FULL_ACCESS = "CLOUD_SEARCH_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLICENSE_MANAGER_SERVICE_ROLE_POLICY = "AWSLICENSE_MANAGER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCLOUD_HSM_FULL_ACCESS = "AWSCLOUD_HSM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_SPOT_FLEET_AUTOSCALE_ROLE = "AMAZON_E_C2_SPOT_FLEET_AUTOSCALE_ROLE"
    '''
    :stability: experimental
    '''
    AWSELASTIC_LOAD_BALANCING_SERVICE_ROLE_POLICY = "AWSELASTIC_LOAD_BALANCING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCODE_BUILD_DEVELOPER_ACCESS = "AWSCODE_BUILD_DEVELOPER_ACCESS"
    '''
    :stability: experimental
    '''
    ELASTI_CACHE_SERVICE_ROLE_POLICY = "ELASTI_CACHE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSGLUE_SERVICE_NOTEBOOK_ROLE = "AWSGLUE_SERVICE_NOTEBOOK_ROLE"
    '''
    :stability: experimental
    '''
    AWSDATAPIPELINE_POWERUSER = "AWSDATAPIPELINE_POWERUSER"
    '''
    :stability: experimental
    '''
    AWSCODE_STAR_SERVICE_ROLE = "AWSCODE_STAR_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_TRANSCRIBE_FULL_ACCESS = "AMAZON_TRANSCRIBE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDIRECTORY_SERVICE_FULL_ACCESS = "AWSDIRECTORY_SERVICE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_FREE_RTOSOTA_UPDATE = "AMAZON_FREE_RTOSOTA_UPDATE"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_LINK_SERVICE_ROLE_POLICY = "AMAZON_WORK_LINK_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DYNAMO_DB_FULL_ACCESS = "AMAZON_DYNAMO_DB_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SES_READ_ONLY_ACCESS = "AMAZON_SES_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_QUERY_EDITOR = "AMAZON_REDSHIFT_QUERY_EDITOR"
    '''
    :stability: experimental
    '''
    AWSWAFREAD_ONLY_ACCESS = "AWSWAFREAD_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AUTO_SCALING_NOTIFICATION_ACCESS_ROLE = "AUTO_SCALING_NOTIFICATION_ACCESS_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_MECHANICAL_TURK_READ_ONLY = "AMAZON_MECHANICAL_TURK_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_READ_ONLY_ACCESS = "AMAZON_KINESIS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSXRAY_DAEMON_WRITE_ACCESS = "AWSXRAY_DAEMON_WRITE_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_MAP_READ_ONLY_ACCESS = "AWSCLOUD_MAP_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_FRONT_LOGGER = "AWSCLOUD_FRONT_LOGGER"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_FULL_ACCESS = "AWSCODE_DEPLOY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSBACKUP_SERVICE_ROLE_POLICY_FOR_BACKUP = "AWSBACKUP_SERVICE_ROLE_POLICY_FOR_BACKUP"
    '''
    :stability: experimental
    '''
    AWSROBO_MAKER_SERVICE_ROLE_POLICY = "AWSROBO_MAKER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_ACTIONS_E_C2_ACCESS = "CLOUD_WATCH_ACTIONS_E_C2_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_DYNAMO_DB_EXECUTION_ROLE = "AWSLAMBDA_DYNAMO_DB_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_DOMAINS_FULL_ACCESS = "AMAZON_ROUTE53_DOMAINS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTI_CACHE_READ_ONLY_ACCESS = "AMAZON_ELASTI_CACHE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_SERVICE_ROLE_POLICY = "AMAZON_RDS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ATHENA_FULL_ACCESS = "AMAZON_ATHENA_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEM_READ_ONLY_ACCESS = "AMAZON_ELASTIC_FILE_SYSTEM_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_MAP_DISCOVER_INSTANCE_ACCESS = "AWSCLOUD_MAP_DISCOVER_INSTANCE_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_FRONT_FULL_ACCESS = "CLOUD_FRONT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CONNECT_FULL_ACCESS = "AMAZON_CONNECT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD9_ADMINISTRATOR = "AWSCLOUD9_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_EMR_INSTANCE_GROUP_POLICY = "AWSAPPLICATION_AUTOSCALING_EMR_INSTANCE_GROUP_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_TEXTRACT_FULL_ACCESS = "AMAZON_TEXTRACT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSORGANIZATIONS_SERVICE_TRUST_POLICY = "AWSORGANIZATIONS_SERVICE_TRUST_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DOC_DB_FULL_ACCESS = "AMAZON_DOC_DB_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZONMOBILEANALYTICSNON_FINANCIALREPORTACCESS = "AMAZONMOBILEANALYTICSNON_FINANCIALREPORTACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_COGNITO_DEVELOPER_AUTHENTICATED_IDENTITIES = "AMAZON_COGNITO_DEVELOPER_AUTHENTICATED_IDENTITIES"
    '''
    :stability: experimental
    '''
    AWSCONFIG_ROLE = "AWSCONFIG_ROLE"
    '''
    :stability: experimental
    '''
    AWSSSOMEMBER_ACCOUNT_ADMINISTRATOR = "AWSSSOMEMBER_ACCOUNT_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_APP_STREAM_FLEET_POLICY = "AWSAPPLICATION_AUTOSCALING_APP_STREAM_FLEET_POLICY"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_PRIVATE_CA_FULL_ACCESS = "AWSCERTIFICATE_MANAGER_PRIVATE_CA_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSGLUE_SERVICE_ROLE = "AWSGLUE_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_APP_STREAM_SERVICE_ACCESS = "AMAZON_APP_STREAM_SERVICE_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_FULL_ACCESS = "AMAZON_REDSHIFT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSTRANSFER_LOGGING_ACCESS = "AWSTRANSFER_LOGGING_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ZOCALO_READ_ONLY_ACCESS = "AMAZON_ZOCALO_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_HSM_READ_ONLY_ACCESS = "AWSCLOUD_HSM_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    COMPREHEND_FULL_ACCESS = "COMPREHEND_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_F_SX_CONSOLE_FULL_ACCESS = "AMAZON_F_SX_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    SYSTEM_ADMINISTRATOR = "SYSTEM_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_SERVICE_EVENTS_ROLE = "AMAZON_E_C2_CONTAINER_SERVICE_EVENTS_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_READ_ONLY_ACCESS = "AMAZON_ROUTE53_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_DISCOVERY_ACCESS = "AWSMIGRATION_HUB_DISCOVERY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_SERVICE_AUTOSCALE_ROLE = "AMAZON_E_C2_CONTAINER_SERVICE_AUTOSCALE_ROLE"
    '''
    :stability: experimental
    '''
    AWSAPP_SYNC_SCHEMA_AUTHOR = "AWSAPP_SYNC_SCHEMA_AUTHOR"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_DEVICE_SETUP = "ALEXA_FOR_BUSINESS_DEVICE_SETUP"
    '''
    :stability: experimental
    '''
    AWSBATCH_SERVICE_ROLE = "AWSBATCH_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_WEB_TIER = "AWSELASTIC_BEANSTALK_WEB_TIER"
    '''
    :stability: experimental
    '''
    AMAZON_SQS_READ_ONLY_ACCESS = "AMAZON_SQS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_FULL_ACCESS = "AMAZON_CHIME_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEEP_RACER_ROBO_MAKER_ACCESS_POLICY = "AWSDEEP_RACER_ROBO_MAKER_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_LOAD_BALANCING_CLASSIC_SERVICE_ROLE_POLICY = "AWSELASTIC_LOAD_BALANCING_CLASSIC_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_DMS_ACCESS = "AWSMIGRATION_HUB_DMS_ACCESS"
    '''
    :stability: experimental
    '''
    WELL_ARCHITECTED_CONSOLE_READ_ONLY_ACCESS = "WELL_ARCHITECTED_CONSOLE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_FULL_ACCESS = "AMAZON_KINESIS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_GUARD_DUTY_READ_ONLY_ACCESS = "AMAZON_GUARD_DUTY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_F_SX_SERVICE_ROLE_POLICY = "AMAZON_F_SX_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ECS_SERVICE_ROLE_POLICY = "AMAZON_ECS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CONNECT_READ_ONLY_ACCESS = "AMAZON_CONNECT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_READ_ONLY_ACCESS = "AMAZON_MACHINE_LEARNING_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REKOGNITION_FULL_ACCESS = "AMAZON_REKOGNITION_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    RDSCLOUD_HSM_AUTHORIZATION_ROLE = "RDSCLOUD_HSM_AUTHORIZATION_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_FULL_ACCESS = "AMAZON_MACHINE_LEARNING_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ADMINISTRATOR_ACCESS = "ADMINISTRATOR_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_REAL_TIME_PREDICTION_ONLY_ACCESS = "AMAZON_MACHINE_LEARNING_REAL_TIME_PREDICTION_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPP_SYNC_PUSH_TO_CLOUD_WATCH_LOGS = "AWSAPP_SYNC_PUSH_TO_CLOUD_WATCH_LOGS"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_SMS_ACCESS = "AWSMIGRATION_HUB_SMS_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCONFIG_USER_ACCESS = "AWSCONFIG_USER_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_CONFIG_ACCESS = "AWSIO_T_CONFIG_ACCESS"
    '''
    :stability: experimental
    '''
    SECURITY_AUDIT = "SECURITY_AUDIT"
    '''
    :stability: experimental
    '''
    AWSDISCOVERY_CONTINUOUS_EXPORT_FIREHOSE_POLICY = "AWSDISCOVERY_CONTINUOUS_EXPORT_FIREHOSE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_COGNITO_IDP_EMAIL_SERVICE_ROLE_POLICY = "AMAZON_COGNITO_IDP_EMAIL_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_CONVERT_FULL_ACCESS = "AWSELEMENTAL_MEDIA_CONVERT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSROBO_MAKER_READ_ONLY_ACCESS = "AWSROBO_MAKER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSRESOURCE_GROUPS_READ_ONLY_ACCESS = "AWSRESOURCE_GROUPS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_STAR_FULL_ACCESS = "AWSCODE_STAR_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_SERVICE_ROLE_POLICY = "AMAZON_SSM_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSDATAPIPELINE_FULLACCESS = "AWSDATAPIPELINE_FULLACCESS"
    '''
    :stability: experimental
    '''
    NEPTUNE_FULL_ACCESS = "NEPTUNE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_MANAGED_INSTANCE_CORE = "AMAZON_SSM_MANAGED_INSTANCE_CORE"
    '''
    :stability: experimental
    '''
    AWSAUTO_SCALING_PLANS_E_C2_AUTO_SCALING_POLICY = "AWSAUTO_SCALING_PLANS_E_C2_AUTO_SCALING_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DYNAMO_DB_READ_ONLY_ACCESS = "AMAZON_DYNAMO_DB_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AUTO_SCALING_CONSOLE_FULL_ACCESS = "AUTO_SCALING_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_PACKAGE_FULL_ACCESS = "AWSELEMENTAL_MEDIA_PACKAGE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_VIDEO_STREAMS_FULL_ACCESS = "AMAZON_KINESIS_VIDEO_STREAMS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SNS_READ_ONLY_ACCESS = "AMAZON_SNS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_PREVIEW_SERVICE_ROLE_POLICY = "AMAZON_RDS_PREVIEW_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSEC2_SPOT_SERVICE_ROLE_POLICY = "AWSEC2_SPOT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCE_FULL_ACCESS = "AMAZON_ELASTIC_MAP_REDUCE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_MAP_FULL_ACCESS = "AWSCLOUD_MAP_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDATA_LIFECYCLE_MANAGER_SERVICE_ROLE = "AWSDATA_LIFECYCLE_MANAGER_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_S3_READ_ONLY_ACCESS = "AMAZON_S3_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_SPACES_ADMIN = "AMAZON_WORK_SPACES_ADMIN"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_ROLE = "AWSCODE_DEPLOY_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_SES_FULL_ACCESS = "AMAZON_SES_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_LOGS_READ_ONLY_ACCESS = "CLOUD_WATCH_LOGS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_BETA_SERVICE_ROLE_POLICY = "AMAZON_RDS_BETA_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_FIREHOSE_READ_ONLY_ACCESS = "AMAZON_KINESIS_FIREHOSE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    GLOBAL_ACCELERATOR_FULL_ACCESS = "GLOBAL_ACCELERATOR_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DYNAMO_DB_FULL_ACCESSWITH_DATA_PIPELINE = "AMAZON_DYNAMO_DB_FULL_ACCESSWITH_DATA_PIPELINE"
    '''
    :stability: experimental
    '''
    AWSIO_T_ANALYTICS_READ_ONLY_ACCESS = "AWSIO_T_ANALYTICS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_ROLEFOR_DATA_PIPELINE_ROLE = "AMAZON_E_C2_ROLEFOR_DATA_PIPELINE_ROLE"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_LOGS_FULL_ACCESS = "CLOUD_WATCH_LOGS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSECURITY_HUB_FULL_ACCESS = "AWSSECURITY_HUB_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_PACKAGE_READ_ONLY = "AWSELEMENTAL_MEDIA_PACKAGE_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_MULTICONTAINER_DOCKER = "AWSELASTIC_BEANSTALK_MULTICONTAINER_DOCKER"
    '''
    :stability: experimental
    '''
    AMAZON_PERSONALIZE_FULL_ACCESS = "AMAZON_PERSONALIZE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_FULL_ACCESS = "AWSMIGRATION_HUB_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_F_SX_READ_ONLY_ACCESS = "AMAZON_F_SX_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    IAMUSER_CHANGE_PASSWORD = "IAMUSER_CHANGE_PASSWORD"
    '''
    :stability: experimental
    '''
    LIGHTSAIL_EXPORT_ACCESS = "LIGHTSAIL_EXPORT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_API_GATEWAY_ADMINISTRATOR = "AMAZON_API_GATEWAY_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AMAZON_VPC_CROSS_ACCOUNT_NETWORK_INTERFACE_OPERATIONS = "AMAZON_VPC_CROSS_ACCOUNT_NETWORK_INTERFACE_OPERATIONS"
    '''
    :stability: experimental
    '''
    AMAZON_MACIE_SETUP_ROLE = "AMAZON_MACIE_SETUP_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_POLLY_READ_ONLY_ACCESS = "AMAZON_POLLY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_DATA_FULL_ACCESS = "AMAZON_RDS_DATA_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MOBILE_ANALYTICS_WRITE_ONLY_ACCESS = "AMAZON_MOBILE_ANALYTICS_WRITE_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_SPOT_FLEET_TAGGING_ROLE = "AMAZON_E_C2_SPOT_FLEET_TAGGING_ROLE"
    '''
    :stability: experimental
    '''
    DATA_SCIENTIST = "DATA_SCIENTIST"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_METERING_FULL_ACCESS = "AWSMARKETPLACE_METERING_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSOPS_WORKS_CM_SERVICE_ROLE = "AWSOPS_WORKS_CM_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    FSX_DELETE_SERVICE_LINKED_ROLE_ACCESS = "FSX_DELETE_SERVICE_LINKED_ROLE_ACCESS"
    '''
    :stability: experimental
    '''
    WORK_LINK_SERVICE_ROLE_POLICY = "WORK_LINK_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CONNECT_SERVICE_LINKED_ROLE_POLICY = "AMAZON_CONNECT_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSPRIVATE_MARKETPLACE_ADMIN_FULL_ACCESS = "AWSPRIVATE_MARKETPLACE_ADMIN_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCONNECTOR = "AWSCONNECTOR"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_ROLE_FOR_ECS_LIMITED = "AWSCODE_DEPLOY_ROLE_FOR_ECS_LIMITED"
    '''
    :stability: experimental
    '''
    AMAZONELASTICTRANSCODER_JOBSSUBMITTER = "AMAZONELASTICTRANSCODER_JOBSSUBMITTER"
    '''
    :stability: experimental
    '''
    AMAZON_MACIE_HANDSHAKE_ROLE = "AMAZON_MACIE_HANDSHAKE_ROLE"
    '''
    :stability: experimental
    '''
    AWSIO_T_ANALYTICS_FULL_ACCESS = "AWSIO_T_ANALYTICS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSBATCH_FULL_ACCESS = "AWSBATCH_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_DIRECTORY_SERVICE_ACCESS = "AMAZON_SSM_DIRECTORY_SERVICE_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZONECS_FULLACCESS = "AMAZONECS_FULLACCESS"
    '''
    :stability: experimental
    '''
    AWSSUPPORT_SERVICE_ROLE_POLICY = "AWSSUPPORT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_RDS_CLUSTER_POLICY = "AWSAPPLICATION_AUTOSCALING_RDS_CLUSTER_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_E_C2_SCHEDULED_INSTANCES = "AWSSERVICE_ROLE_FOR_E_C2_SCHEDULED_INSTANCES"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_ROLE_FOR_LAMBDA = "AWSCODE_DEPLOY_ROLE_FOR_LAMBDA"
    '''
    :stability: experimental
    '''
    AWSFMADMIN_READ_ONLY_ACCESS = "AWSFMADMIN_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_FULL_ACCESS = "AMAZON_SSM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_COMMIT_READ_ONLY = "AWSCODE_COMMIT_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_FREE_RTOS_FULL_ACCESS = "AMAZON_FREE_RTOS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_TEXTRACT_SERVICE_ROLE = "AMAZON_TEXTRACT_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_COGNITO_READ_ONLY = "AMAZON_COGNITO_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_DMS_CLOUD_WATCH_LOGS_ROLE = "AMAZON_DMS_CLOUD_WATCH_LOGS_ROLE"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_DISCOVERY_SERVICE_FULL_ACCESS = "AWSAPPLICATION_DISCOVERY_SERVICE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_AUTO_NAMING_READ_ONLY_ACCESS = "AMAZON_ROUTE53_AUTO_NAMING_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSSOREAD_ONLY = "AWSSSOREAD_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_VPC_FULL_ACCESS = "AMAZON_VPC_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_PRIVATE_CA_USER = "AWSCERTIFICATE_MANAGER_PRIVATE_CA_USER"
    '''
    :stability: experimental
    '''
    AWSAPP_SYNC_ADMINISTRATOR = "AWSAPP_SYNC_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AWSEC2_FLEET_SERVICE_ROLE_POLICY = "AWSEC2_FLEET_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_AUTO_NAMING_FULL_ACCESS = "AMAZON_ROUTE53_AUTO_NAMING_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIMPORT_EXPORT_FULL_ACCESS = "AWSIMPORT_EXPORT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    DYNAMO_DB_REPLICATION_SERVICE_ROLE_POLICY = "DYNAMO_DB_REPLICATION_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MECHANICAL_TURK_FULL_ACCESS = "AMAZON_MECHANICAL_TURK_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_REGISTRY_POWER_USER = "AMAZON_E_C2_CONTAINER_REGISTRY_POWER_USER"
    '''
    :stability: experimental
    '''
    AWSSSODIRECTORY_READ_ONLY = "AWSSSODIRECTORY_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_CREATE_ONLY_ACCESS = "AMAZON_MACHINE_LEARNING_CREATE_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_VIDEO_STREAMS_READ_ONLY_ACCESS = "AMAZON_KINESIS_VIDEO_STREAMS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_TRAIL_READ_ONLY_ACCESS = "AWSCLOUD_TRAIL_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    WAFREGIONAL_LOGGING_SERVICE_ROLE_POLICY = "WAFREGIONAL_LOGGING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_EXECUTE = "AWSLAMBDA_EXECUTE"
    '''
    :stability: experimental
    '''
    AWSGLUE_CONSOLE_SAGE_MAKER_NOTEBOOK_FULL_ACCESS = "AWSGLUE_CONSOLE_SAGE_MAKER_NOTEBOOK_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MSK_FULL_ACCESS = "AMAZON_MSK_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_RULE_ACTIONS = "AWSIO_T_RULE_ACTIONS"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_SERVICE_POLICY = "AMAZON_EKS_SERVICE_POLICY"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_DESCRIBE_REDSHIFT = "AWSQUICK_SIGHT_DESCRIBE_REDSHIFT"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTICSEARCH_SERVICE_ROLE_POLICY = "AMAZON_ELASTICSEARCH_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MQ_READ_ONLY_ACCESS = "AMAZON_MQ_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    VMIMPORT_EXPORT_ROLE_FOR_AWS_CONNECTOR = "VMIMPORT_EXPORT_ROLE_FOR_AWS_CONNECTOR"
    '''
    :stability: experimental
    '''
    AWSCODE_PIPELINE_CUSTOM_ACTION_ACCESS = "AWSCODE_PIPELINE_CUSTOM_ACTION_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_SQS_QUEUE_EXECUTION_ROLE = "AWSLAMBDA_SQS_QUEUE_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    AWSCLOUD9_SERVICE_ROLE_POLICY = "AWSCLOUD9_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_ECS_SERVICE_POLICY = "AWSAPPLICATION_AUTOSCALING_ECS_SERVICE_POLICY"
    '''
    :stability: experimental
    '''
    AWSOPS_WORKS_INSTANCE_REGISTRATION = "AWSOPS_WORKS_INSTANCE_REGISTRATION"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_DIRECTORY_FULL_ACCESS = "AMAZON_CLOUD_DIRECTORY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ECS_TASK_EXECUTION_ROLE_POLICY = "AMAZON_ECS_TASK_EXECUTION_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSTORAGE_GATEWAY_FULL_ACCESS = "AWSSTORAGE_GATEWAY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_EVENTS_FULL_ACCESS = "AWSIO_T_EVENTS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LEX_READ_ONLY = "AMAZON_LEX_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_USER_MANAGEMENT = "AMAZON_CHIME_USER_MANAGEMENT"
    '''
    :stability: experimental
    '''
    AMAZON_MSK_READ_ONLY_ACCESS = "AMAZON_MSK_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDATA_SYNC_FULL_ACCESS = "AWSDATA_SYNC_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_IO_T_SITE_WISE = "AWSSERVICE_ROLE_FOR_IO_T_SITE_WISE"
    '''
    :stability: experimental
    '''
    CLOUDWATCH_APPLICATION_INSIGHTS_SERVICE_LINKED_ROLE_POLICY = "CLOUDWATCH_APPLICATION_INSIGHTS_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSTRUSTED_ADVISOR_SERVICE_ROLE_POLICY = "AWSTRUSTED_ADVISOR_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_CONFIG_READ_ONLY_ACCESS = "AWSIO_T_CONFIG_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_MAIL_READ_ONLY_ACCESS = "AMAZON_WORK_MAIL_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DMSVPC_MANAGEMENT_ROLE = "AMAZON_DMSVPC_MANAGEMENT_ROLE"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_KINESIS_EXECUTION_ROLE = "AWSLAMBDA_KINESIS_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    COMPREHEND_DATA_ACCESS_ROLE_POLICY = "COMPREHEND_DATA_ACCESS_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DOC_DB_CONSOLE_FULL_ACCESS = "AMAZON_DOC_DB_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    RESOURCE_GROUPSAND_TAG_EDITOR_READ_ONLY_ACCESS = "RESOURCE_GROUPSAND_TAG_EDITOR_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REKOGNITION_SERVICE_ROLE = "AMAZON_REKOGNITION_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_AUTOMATION_ROLE = "AMAZON_SSM_AUTOMATION_ROLE"
    '''
    :stability: experimental
    '''
    CLOUD_HSM_SERVICE_ROLE_POLICY = "CLOUD_HSM_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    COMPREHEND_READ_ONLY = "COMPREHEND_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSSTEP_FUNCTIONS_CONSOLE_FULL_ACCESS = "AWSSTEP_FUNCTIONS_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_IO_T_ANALYTICS_ACCESS = "AWSQUICK_SIGHT_IO_T_ANALYTICS_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_BUILD_READ_ONLY_ACCESS = "AWSCODE_BUILD_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    LEX_BOT_POLICY = "LEX_BOT_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MACIE_FULL_ACCESS = "AMAZON_MACIE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_MANAGE_REAL_TIME_ENDPOINT_ONLY_ACCESS = "AMAZON_MACHINE_LEARNING_MANAGE_REAL_TIME_ENDPOINT_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_EVENTS_INVOCATION_ACCESS = "CLOUD_WATCH_EVENTS_INVOCATION_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_FRONT_READ_ONLY_ACCESS = "CLOUD_FRONT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEEP_LENS_SERVICE_ROLE_POLICY = "AWSDEEP_LENS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_SNS_ROLE = "AMAZON_SNS_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_INSPECTOR_SERVICE_ROLE_POLICY = "AMAZON_INSPECTOR_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MOBILE_ANALYTICS_FINANCIAL_REPORT_ACCESS = "AMAZON_MOBILE_ANALYTICS_FINANCIAL_REPORT_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_SERVICE = "AWSELASTIC_BEANSTALK_SERVICE"
    '''
    :stability: experimental
    '''
    IAMREAD_ONLY_ACCESS = "IAMREAD_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_READ_ONLY_ACCESS = "AMAZON_RDS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_AUDIT = "AWSIO_T_DEVICE_DEFENDER_AUDIT"
    '''
    :stability: experimental
    '''
    AMAZON_COGNITO_POWER_USER = "AMAZON_COGNITO_POWER_USER"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_AUTO_NAMING_REGISTRANT_ACCESS = "AMAZON_ROUTE53_AUTO_NAMING_REGISTRANT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEM_FULL_ACCESS = "AMAZON_ELASTIC_FILE_SYSTEM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    LEX_CHANNEL_POLICY = "LEX_CHANNEL_POLICY"
    '''
    :stability: experimental
    '''
    SERVER_MIGRATION_CONNECTOR = "SERVER_MIGRATION_CONNECTOR"
    '''
    :stability: experimental
    '''
    AMAZON_ES_COGNITO_ACCESS = "AMAZON_ES_COGNITO_ACCESS"
    '''
    :stability: experimental
    '''
    AWSFMADMIN_FULL_ACCESS = "AWSFMADMIN_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_READ_ONLY = "AMAZON_CHIME_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_ZOCALO_FULL_ACCESS = "AMAZON_ZOCALO_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_SITE_WISE_READ_ONLY_ACCESS = "AWSIO_T_SITE_WISE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSACCOUNT_USAGE_REPORT_ACCESS = "AWSACCOUNT_USAGE_REPORT_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_TOTA_UPDATE = "AWSIO_TOTA_UPDATE"
    '''
    :stability: experimental
    '''
    AMAZON_MQ_FULL_ACCESS = "AMAZON_MQ_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_GET_ENTITLEMENTS = "AWSMARKETPLACE_GET_ENTITLEMENTS"
    '''
    :stability: experimental
    '''
    AWSGREENGRASS_READ_ONLY_ACCESS = "AWSGREENGRASS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_SERVICEFOR_E_C2_ROLE = "AMAZON_E_C2_CONTAINER_SERVICEFOR_E_C2_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_APP_STREAM_FULL_ACCESS = "AMAZON_APP_STREAM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_DATA_ACCESS = "AWSIO_T_DATA_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_LINK_FULL_ACCESS = "AMAZON_WORK_LINK_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_TRANSCRIBE_READ_ONLY_ACCESS = "AMAZON_TRANSCRIBE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ES_FULL_ACCESS = "AMAZON_ES_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    APPLICATION_DISCOVERY_SERVICE_CONTINUOUS_EXPORT_SERVICE_ROLE_POLICY = "APPLICATION_DISCOVERY_SERVICE_CONTINUOUS_EXPORT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_SUMERIAN_FULL_ACCESS = "AMAZON_SUMERIAN_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSWAFFULL_ACCESS = "AWSWAFFULL_ACCESS"
    '''
    :stability: experimental
    '''
    ELASTIC_LOAD_BALANCING_READ_ONLY = "ELASTIC_LOAD_BALANCING_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSARTIFACT_ACCOUNT_SYNC = "AWSARTIFACT_ACCOUNT_SYNC"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_FIREHOSE_FULL_ACCESS = "AMAZON_KINESIS_FIREHOSE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_READ_ONLY_ACCESS = "CLOUD_WATCH_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_BASIC_EXECUTION_ROLE = "AWSLAMBDA_BASIC_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    RESOURCE_GROUPSAND_TAG_EDITOR_FULL_ACCESS = "RESOURCE_GROUPSAND_TAG_EDITOR_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSKEY_MANAGEMENT_SERVICE_POWER_USER = "AWSKEY_MANAGEMENT_SERVICE_POWER_USER"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_E_C2_SPOT_FLEET_REQUEST_POLICY = "AWSAPPLICATION_AUTOSCALING_E_C2_SPOT_FLEET_REQUEST_POLICY"
    '''
    :stability: experimental
    '''
    AWSIMPORT_EXPORT_READ_ONLY_ACCESS = "AWSIMPORT_EXPORT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_EVENTS_SERVICE_ROLE_POLICY = "CLOUD_WATCH_EVENTS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_TRANSCODER_ROLE = "AMAZON_ELASTIC_TRANSCODER_ROLE"
    '''
    :stability: experimental
    '''
    AWSGLUE_CONSOLE_FULL_ACCESS = "AWSGLUE_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_CONTAINER_SERVICE_ROLE = "AMAZON_E_C2_CONTAINER_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AWSDEVICE_FARM_FULL_ACCESS = "AWSDEVICE_FARM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_READ_ONLY_ACCESS = "AMAZON_SSM_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSTEP_FUNCTIONS_READ_ONLY_ACCESS = "AWSSTEP_FUNCTIONS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACEREAD_ONLY = "AWSMARKETPLACEREAD_ONLY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_DYNAMO_DB_TABLE_POLICY = "AWSAPPLICATION_AUTOSCALING_DYNAMO_DB_TABLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCODE_PIPELINE_FULL_ACCESS = "AWSCODE_PIPELINE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD9_USER = "AWSCLOUD9_USER"
    '''
    :stability: experimental
    '''
    AWSGREENGRASS_RESOURCE_ACCESS_ROLE_POLICY = "AWSGREENGRASS_RESOURCE_ACCESS_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MACIE_SERVICE_ROLE_POLICY = "AMAZON_MACIE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    NETWORK_ADMINISTRATOR = "NETWORK_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AWSIO_T1_CLICK_FULL_ACCESS = "AWSIO_T1_CLICK_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_SPACES_APPLICATION_MANAGER_ADMIN_ACCESS = "AMAZON_WORK_SPACES_APPLICATION_MANAGER_ADMIN_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DRSVPC_MANAGEMENT = "AMAZON_DRSVPC_MANAGEMENT"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_SERVICE_LINKED_ROLE_POLICY = "AMAZON_REDSHIFT_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_PRIVATE_CA_READ_ONLY = "AWSCERTIFICATE_MANAGER_PRIVATE_CA_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSXRAY_FULL_ACCESS = "AWSXRAY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_WORKER_TIER = "AWSELASTIC_BEANSTALK_WORKER_TIER"
    '''
    :stability: experimental
    '''
    AWSDIRECT_CONNECT_FULL_ACCESS = "AWSDIRECT_CONNECT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_BUILD_ADMIN_ACCESS = "AWSCODE_BUILD_ADMIN_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_KINESIS_ANALYTICS_FULL_ACCESS = "AMAZON_KINESIS_ANALYTICS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSECURITY_HUB_SERVICE_ROLE_POLICY = "AWSSECURITY_HUB_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_MAINTENANCE = "AWSELASTIC_BEANSTALK_MAINTENANCE"
    '''
    :stability: experimental
    '''
    APIGATEWAY_SERVICE_ROLE_POLICY = "APIGATEWAY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSACCOUNT_ACTIVITY_ACCESS = "AWSACCOUNT_ACTIVITY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_GLACIER_FULL_ACCESS = "AMAZON_GLACIER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_F_SX_CONSOLE_READ_ONLY_ACCESS = "AMAZON_F_SX_CONSOLE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_MAIL_FULL_ACCESS = "AMAZON_WORK_MAIL_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    DAXSERVICE_ROLE_POLICY = "DAXSERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    COMPREHEND_MEDICAL_FULL_ACCESS = "COMPREHEND_MEDICAL_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_MANAGE_SUBSCRIPTIONS = "AWSMARKETPLACE_MANAGE_SUBSCRIPTIONS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_CUSTOM_PLATFORMFOR_E_C2_ROLE = "AWSELASTIC_BEANSTALK_CUSTOM_PLATFORMFOR_E_C2_ROLE"
    '''
    :stability: experimental
    '''
    AWSDATA_SYNC_READ_ONLY_ACCESS = "AWSDATA_SYNC_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSVPCTRANSIT_GATEWAY_SERVICE_ROLE_POLICY = "AWSVPCTRANSIT_GATEWAY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    NEPTUNE_READ_ONLY_ACCESS = "NEPTUNE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSUPPORT_ACCESS = "AWSSUPPORT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCEFOR_AUTO_SCALING_ROLE = "AMAZON_ELASTIC_MAP_REDUCEFOR_AUTO_SCALING_ROLE"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_CONVERT_READ_ONLY = "AWSELEMENTAL_MEDIA_CONVERT_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSLAMBDAINVOCATION_DYNAMODB = "AWSLAMBDAINVOCATION_DYNAMODB"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_END_USER_FULL_ACCESS = "AWSSERVICE_CATALOG_END_USER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    IAMUSER_SSH_KEYS = "IAMUSER_SSH_KEYS"
    '''
    :stability: experimental
    '''
    AWSDEEP_RACER_SERVICE_ROLE_POLICY = "AWSDEEP_RACER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_READ_ONLY = "AMAZON_SAGE_MAKER_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSIO_T_FULL_ACCESS = "AWSIO_T_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_DESCRIBE_RD_S = "AWSQUICK_SIGHT_DESCRIBE_RD_S"
    '''
    :stability: experimental
    '''
    AWSRESOURCE_ACCESS_MANAGER_SERVICE_ROLE_POLICY = "AWSRESOURCE_ACCESS_MANAGER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCONFIG_RULES_EXECUTION_ROLE = "AWSCONFIG_RULES_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    AWSCONFIG_SERVICE_ROLE_POLICY = "AWSCONFIG_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ES_READ_ONLY_ACCESS = "AMAZON_ES_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_DEPLOYER_ACCESS = "AWSCODE_DEPLOY_DEPLOYER_ACCESS"
    '''
    :stability: experimental
    '''
    KAFKA_SERVICE_ROLE_POLICY = "KAFKA_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_POLLY_FULL_ACCESS = "AMAZON_POLLY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_MAINTENANCE_WINDOW_ROLE = "AMAZON_SSM_MAINTENANCE_WINDOW_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_ENHANCED_MONITORING_ROLE = "AMAZON_RDS_ENHANCED_MONITORING_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_LEX_FULL_ACCESS = "AMAZON_LEX_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_VPC_ACCESS_EXECUTION_ROLE = "AWSLAMBDA_VPC_ACCESS_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_MACIE_SERVICE_ROLE = "AMAZON_MACIE_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_LEX_RUN_BOTS_ONLY = "AMAZON_LEX_RUN_BOTS_ONLY"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_PRIVATE_CA_AUDITOR = "AWSCERTIFICATE_MANAGER_PRIVATE_CA_AUDITOR"
    '''
    :stability: experimental
    '''
    AMAZON_SNS_FULL_ACCESS = "AMAZON_SNS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZONEKS_CNI_POLICY = "AMAZONEKS_CNI_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_ADMIN_FULL_ACCESS = "AWSSERVICE_CATALOG_ADMIN_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSHIELD_DRT_ACCESS_POLICY = "AWSSHIELD_DRT_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    CLOUD_SEARCH_READ_ONLY_ACCESS = "CLOUD_SEARCH_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSGREENGRASS_FULL_ACCESS = "AWSGREENGRASS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    NEPTUNE_CONSOLE_FULL_ACCESS = "NEPTUNE_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_FORMATION_READ_ONLY_ACCESS = "AWSCLOUD_FORMATION_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_FULL_ACCESS = "AMAZON_ROUTE53_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_ROLE = "AWSLAMBDA_ROLE"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_ENI_MANAGEMENT_ACCESS = "AWSLAMBDA_ENI_MANAGEMENT_ACCESS"
    '''
    :stability: experimental
    '''
    AWSOPS_WORKS_CLOUD_WATCH_LOGS = "AWSOPS_WORKS_CLOUD_WATCH_LOGS"
    '''
    :stability: experimental
    '''
    AMAZON_APP_STREAM_READ_ONLY_ACCESS = "AMAZON_APP_STREAM_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSTEP_FUNCTIONS_FULL_ACCESS = "AWSSTEP_FUNCTIONS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_TRAIL_SERVICE_ROLE_POLICY = "CLOUD_TRAIL_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_INSPECTOR_READ_ONLY_ACCESS = "AMAZON_INSPECTOR_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSORGANIZATIONS_READ_ONLY_ACCESS = "AWSORGANIZATIONS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    TRANSLATE_READ_ONLY = "TRANSLATE_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_FULL_ACCESS = "AWSCERTIFICATE_MANAGER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEEP_RACER_CLOUD_FORMATION_ACCESS_POLICY = "AWSDEEP_RACER_CLOUD_FORMATION_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_EVENTS_READ_ONLY_ACCESS = "AWSIO_T_EVENTS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSROBO_MAKER_SERVICE_POLICY = "AWSROBO_MAKER_SERVICE_POLICY"
    '''
    :stability: experimental
    '''
    POWER_USER_ACCESS = "POWER_USER_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTO_SCALING_CUSTOM_RESOURCE_POLICY = "AWSAPPLICATION_AUTO_SCALING_CUSTOM_RESOURCE_POLICY"
    '''
    :stability: experimental
    '''
    GLOBAL_ACCELERATOR_READ_ONLY_ACCESS = "GLOBAL_ACCELERATOR_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_FULL_ACCESS = "AMAZON_SAGE_MAKER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    WAFLOGGING_SERVICE_ROLE_POLICY = "WAFLOGGING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSBACKUP_SERVICE_ROLE_POLICY_FOR_RESTORES = "AWSBACKUP_SERVICE_ROLE_POLICY_FOR_RESTORES"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_STORE_FULL_ACCESS = "AWSELEMENTAL_MEDIA_STORE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_EVENTS_FULL_ACCESS = "CLOUD_WATCH_EVENTS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLICENSE_MANAGER_MEMBER_ACCOUNT_ROLE_POLICY = "AWSLICENSE_MANAGER_MEMBER_ACCOUNT_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSORGANIZATIONS_FULL_ACCESS = "AWSORGANIZATIONS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODEPIPELINE_FULLACCESS = "AWSCODEPIPELINE_FULLACCESS"
    '''
    :stability: experimental
    '''
    DYNAMO_DB_KINESIS_REPLICATION_SERVICE_ROLE_POLICY = "DYNAMO_DB_KINESIS_REPLICATION_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_ELASTI_CACHE_RG_POLICY = "AWSAPPLICATION_AUTOSCALING_ELASTI_CACHE_RG_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_AUGMENTED_AI_INTEGRATED_API_ACCESS = "AMAZON_AUGMENTED_AI_INTEGRATED_API_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_READ_ONLY_ACCESS = "AWSELASTIC_DISASTER_RECOVERY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_FRAUD_DETECTOR_FULL_ACCESS_POLICY = "AMAZON_FRAUD_DETECTOR_FULL_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AMAZONLAUNCHWIZARD_FULLACCESS = "AMAZONLAUNCHWIZARD_FULLACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_SD_K = "AMAZON_CHIME_SD_K"
    '''
    :stability: experimental
    '''
    AWS_GLUE_DATA_BREW_FULL_ACCESS_POLICY = "AWS_GLUE_DATA_BREW_FULL_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_READ_ONLY = "AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_TESTER_FOR_FREE_RTOS_FULL_ACCESS = "AWSIO_T_DEVICE_TESTER_FOR_FREE_RTOS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ROUTE53_RESOLVER_SERVICE_ROLE_POLICY = "ROUTE53_RESOLVER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    WAFV2_LOGGING_SERVICE_ROLE_POLICY = "WAFV2_LOGGING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSBUDGETS_ACTIONS_WITH_AWS_RESOURCE_CONTROL_ACCESS = "AWSBUDGETS_ACTIONS_WITH_AWS_RESOURCE_CONTROL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_MANAGED_UPDATES_CUSTOMER_ROLE_POLICY = "AWSELASTIC_BEANSTALK_MANAGED_UPDATES_CUSTOMER_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    ADMINISTRATORACCESS_AMPLIFY = "ADMINISTRATORACCESS_AMPLIFY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RECOVERY_READINESS_FULL_ACCESS = "AMAZON_ROUTE53_RECOVERY_READINESS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSNETWORK_MANAGER_FULL_ACCESS = "AWSNETWORK_MANAGER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_AMI_INGESTION = "AWSMARKETPLACE_AMI_INGESTION"
    '''
    :stability: experimental
    '''
    AWSPRIVATE_MARKETPLACE_REQUESTS = "AWSPRIVATE_MARKETPLACE_REQUESTS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_APPLICATION_INSIGHTS_READ_ONLY_ACCESS = "CLOUD_WATCH_APPLICATION_INSIGHTS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    ADMINISTRATORACCESS_AWSELASTICBEANSTALK = "ADMINISTRATORACCESS_AWSELASTICBEANSTALK"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_MECHANICAL_TURK_ACCESS = "AMAZON_SAGE_MAKER_MECHANICAL_TURK_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_TIMESTREAM_CONSOLE_FULL_ACCESS = "AMAZON_TIMESTREAM_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSWAFCONSOLE_FULL_ACCESS = "AWSWAFCONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSGLUE_SCHEMA_REGISTRY_READONLY_ACCESS = "AWSGLUE_SCHEMA_REGISTRY_READONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSNETWORK_MANAGER_SERVICE_ROLE_POLICY = "AWSNETWORK_MANAGER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPP_MESH_SERVICE_ROLE_POLICY = "AWSAPP_MESH_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSCONFIG_REMEDIATION_SERVICE_ROLE_POLICY = "AWSCONFIG_REMEDIATION_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    CONFIG_CONFORMS_SERVICE_ROLE_POLICY = "CONFIG_CONFORMS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_EVENT_BRIDGE_READ_ONLY_ACCESS = "AMAZON_EVENT_BRIDGE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_STAR_NOTIFICATIONS_SERVICE_ROLE_POLICY = "AWSCODE_STAR_NOTIFICATIONS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_PURCHASE_ORDERS_SERVICE_ROLE_POLICY = "AWSMARKETPLACE_PURCHASE_ORDERS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_TAILOR_READ_ONLY = "AWSELEMENTAL_MEDIA_TAILOR_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_INSPECTOR2_SERVICE_ROLE_POLICY = "AMAZON_INSPECTOR2_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_KENDRA_FULL_ACCESS = "AMAZON_KENDRA_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZONEMRFULLACCESSPOLICY_V2 = "AMAZONEMRFULLACCESSPOLICY_V2"
    '''
    :stability: experimental
    '''
    AMAZON_S3_OUTPOSTS_FULL_ACCESS = "AMAZON_S3_OUTPOSTS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    APP_RUNNER_NETWORKING_SERVICE_ROLE_POLICY = "APP_RUNNER_NETWORKING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_QUERY_EDITOR_V2_FULL_ACCESS = "AMAZON_REDSHIFT_QUERY_EDITOR_V2_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_ELASTICSEARCH_POLICY = "AWSQUICK_SIGHT_ELASTICSEARCH_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_FULL_ACCESS = "AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_CASSANDRA_TABLE_POLICY = "AWSAPPLICATION_AUTOSCALING_CASSANDRA_TABLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSYSTEMS_MANAGER_ACCOUNT_DISCOVERY_SERVICE_POLICY = "AWSSYSTEMS_MANAGER_ACCOUNT_DISCOVERY_SERVICE_POLICY"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_SERVICE_LINKED_ROLE_POLICY = "AWSPANORAMA_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DEV_OPS_GURU_FULL_ACCESS = "AMAZON_DEV_OPS_GURU_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSRESOURCE_ACCESS_MANAGER_READ_ONLY_ACCESS = "AWSRESOURCE_ACCESS_MANAGER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_EVENT_BRIDGE_FULL_ACCESS = "AMAZON_EVENT_BRIDGE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_AWS_PORTAL_ADMIN_POLICY = "AWSTHINKBOX_AWS_PORTAL_ADMIN_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_READ_ONLY = "AWSELASTIC_BEANSTALK_READ_ONLY"
    '''
    :stability: experimental
    '''
    EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER_ECR_CONTAINER_BUILDS = "EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER_ECR_CONTAINER_BUILDS"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_ROLE_FOR_LAMBDA_LIMITED = "AWSCODE_DEPLOY_ROLE_FOR_LAMBDA_LIMITED"
    '''
    :stability: experimental
    '''
    AWSAUDIT_MANAGER_SERVICE_ROLE_POLICY = "AWSAUDIT_MANAGER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSBACKUP_AUDIT_ACCESS = "AWSBACKUP_AUDIT_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_SYNTHETICS_READ_ONLY_ACCESS = "CLOUD_WATCH_SYNTHETICS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZONNIMBLESTUDIO_STUDIOUSER = "AMAZONNIMBLESTUDIO_STUDIOUSER"
    '''
    :stability: experimental
    '''
    AWSCLOUDTRAIL_FULLACCESS = "AWSCLOUDTRAIL_FULLACCESS"
    '''
    :stability: experimental
    '''
    ACCESS_ANALYZER_SERVICE_ROLE_POLICY = "ACCESS_ANALYZER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RESOLVER_READ_ONLY_ACCESS = "AMAZON_ROUTE53_RESOLVER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_BRAKET_JOBS_EXECUTION_POLICY = "AMAZON_BRAKET_JOBS_EXECUTION_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_ROLE_POLICY_FOR_LAUNCH_WIZARD = "AMAZON_E_C2_ROLE_POLICY_FOR_LAUNCH_WIZARD"
    '''
    :stability: experimental
    '''
    AMAZON_APP_FLOW_READ_ONLY_ACCESS = "AMAZON_APP_FLOW_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_VISION_CONSOLE_READ_ONLY_ACCESS = "AMAZON_LOOKOUT_VISION_CONSOLE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_TIMESTREAM_POLICY = "AWSQUICK_SIGHT_TIMESTREAM_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MANAGED_BLOCKCHAIN_FULL_ACCESS = "AMAZON_MANAGED_BLOCKCHAIN_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    SERVICE_QUOTAS_FULL_ACCESS = "SERVICE_QUOTAS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_TIMESTREAM_FULL_ACCESS = "AMAZON_TIMESTREAM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPP_RUNNER_FULL_ACCESS = "AWSAPP_RUNNER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_INSPECTOR2_FULL_ACCESS = "AMAZON_INSPECTOR2_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ELEMENTAL_APPLIANCES_SOFTWARE_READ_ONLY_ACCESS = "ELEMENTAL_APPLIANCES_SOFTWARE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_VISION_FULL_ACCESS = "AMAZON_LOOKOUT_VISION_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_DEPLOY_ROLE_FOR_CLOUD_FORMATION = "AWSCODE_DEPLOY_ROLE_FOR_CLOUD_FORMATION"
    '''
    :stability: experimental
    '''
    BATCH_SERVICE_ROLE_POLICY = "BATCH_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_SERVICE_ROLE_POLICY = "AMAZON_HONEYCODE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSBUG_BUST_PLAYER_ACCESS = "AWSBUG_BUST_PLAYER_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_EDGE_DEVICE_FLEET_POLICY = "AMAZON_SAGE_MAKER_EDGE_DEVICE_FLEET_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_SITE_WISE_MONITOR_SERVICE_ROLE_POLICY = "AWSIO_T_SITE_WISE_MONITOR_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_READ_ONLY_ACCESS = "AMAZON_HONEYCODE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCLOUD_FORMATION_FULL_ACCESS = "AWSCLOUD_FORMATION_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_APPLIANCE_ROLE_POLICY = "AWSPANORAMA_APPLIANCE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_METRICS_FULL_ACCESS = "AMAZON_LOOKOUT_METRICS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_AGENT_POLICY = "AWSAPPLICATION_MIGRATION_AGENT_POLICY"
    '''
    :stability: experimental
    '''
    AWSOPSWORKS_FULLACCESS = "AWSOPSWORKS_FULLACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_CUSTOM_PREVIEW_SERVICE_ROLE_POLICY = "AMAZON_RDS_CUSTOM_PREVIEW_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_READ_ONLY_ACCESS = "AMAZON_ROUTE53_RECOVERY_CONTROL_CONFIG_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_TRANSCRIPTION_SERVICE_LINKED_ROLE_POLICY = "AMAZON_CHIME_TRANSCRIPTION_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSNETWORK_FIREWALL_SERVICE_ROLE_POLICY = "AWSNETWORK_FIREWALL_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    ELEMENTAL_APPLIANCES_SOFTWARE_FULL_ACCESS = "ELEMENTAL_APPLIANCES_SOFTWARE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MACHINE_LEARNING_ROLEFOR_REDSHIFT_DATA_SOURCE_V3 = "AMAZON_MACHINE_LEARNING_ROLEFOR_REDSHIFT_DATA_SOURCE_V3"
    '''
    :stability: experimental
    '''
    AMAZON_AUGMENTED_AI_HUMAN_LOOP_FULL_ACCESS = "AMAZON_AUGMENTED_AI_HUMAN_LOOP_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_EQUIPMENT_READ_ONLY_ACCESS = "AMAZON_LOOKOUT_EQUIPMENT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_WATCH_RUM_FULL_ACCESS = "AMAZON_CLOUD_WATCH_RUM_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDATA_EXCHANGE_READ_ONLY = "AWSDATA_EXCHANGE_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_SELLER_PRODUCTS_FULL_ACCESS = "AWSMARKETPLACE_SELLER_PRODUCTS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_LICENSE_MANAGEMENT_SERVICE_ROLE_POLICY = "AWSMARKETPLACE_LICENSE_MANAGEMENT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSPROTON_READ_ONLY_ACCESS = "AWSPROTON_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LEX_V2_BOT_POLICY = "AMAZON_LEX_V2_BOT_POLICY"
    '''
    :stability: experimental
    '''
    AWSIQCONTRACT_SERVICE_ROLE_POLICY = "AWSIQCONTRACT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSTORAGE_GATEWAY_SERVICE_ROLE_POLICY = "AWSSTORAGE_GATEWAY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSBACKUP_ORGANIZATION_ADMIN_ACCESS = "AWSBACKUP_ORGANIZATION_ADMIN_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_SITE_WISE_MONITOR_PORTAL_ACCESS = "AWSIO_T_SITE_WISE_MONITOR_PORTAL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAUDIT_MANAGER_ADMINISTRATOR_ACCESS = "AWSAUDIT_MANAGER_ADMINISTRATOR_ACCESS"
    '''
    :stability: experimental
    '''
    ELEMENTAL_SUPPORT_CENTER_FULL_ACCESS = "ELEMENTAL_SUPPORT_CENTER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_FULL_ACCESS = "AMAZON_HONEYCODE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_DOCS_READ_ONLY_ACCESS = "AMAZON_WORK_DOCS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_LAMBDA_INSIGHTS_EXECUTION_ROLE_POLICY = "CLOUD_WATCH_LAMBDA_INSIGHTS_EXECUTION_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CONNECT_VOICE_ID_FULL_ACCESS = "AMAZON_CONNECT_VOICE_ID_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSGLOBAL_ACCELERATOR_SLR_POLICY = "AWSGLOBAL_ACCELERATOR_SLR_POLICY"
    '''
    :stability: experimental
    '''
    EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER = "EC2_INSTANCE_PROFILE_FOR_IMAGE_BUILDER"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_LOG_DELIVERY_POLICY = "AWSSERVICE_ROLE_FOR_LOG_DELIVERY_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CODE_GURU_REVIEWER_FULL_ACCESS = "AMAZON_CODE_GURU_REVIEWER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSVPCS2_S_VPN_SERVICE_ROLE_POLICY = "AWSVPCS2_S_VPN_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIMAGE_BUILDER_FULL_ACCESS = "AWSIMAGE_BUILDER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSINCIDENT_MANAGER_RESOLVER_ACCESS = "AWSINCIDENT_MANAGER_RESOLVER_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCERTIFICATE_MANAGER_PRIVATE_CA_PRIVILEGED_USER = "AWSCERTIFICATE_MANAGER_PRIVATE_CA_PRIVILEGED_USER"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_WATCH_EVIDENTLY_READ_ONLY_ACCESS = "AMAZON_CLOUD_WATCH_EVIDENTLY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SSM_PATCH_ASSOCIATION = "AMAZON_SSM_PATCH_ASSOCIATION"
    '''
    :stability: experimental
    '''
    AWSBUDGETS_READ_ONLY_ACCESS = "AWSBUDGETS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSOPSWORKSREGISTERCLI_ONPREMISES = "AWSOPSWORKSREGISTERCLI_ONPREMISES"
    '''
    :stability: experimental
    '''
    HEALTH_ORGANIZATIONSSERVICEROLEPOLICY = "HEALTH_ORGANIZATIONSSERVICEROLEPOLICY"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_STRATEGY_SERVICE_ROLE_POLICY = "AWSMIGRATION_HUB_STRATEGY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_V_CENTER_CLIENT_POLICY = "AWSAPPLICATION_MIGRATION_V_CENTER_CLIENT_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_RDS_CUSTOM_SERVICE_ROLE_POLICY = "AMAZON_RDS_CUSTOM_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_FULL_ACCESS = "AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MCS_READ_ONLY_ACCESS = "AMAZON_MCS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_OPEN_SEARCH_SERVICE_FULL_ACCESS = "AMAZON_OPEN_SEARCH_SERVICE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSROBOMAKER_FULLACCESS = "AWSROBOMAKER_FULLACCESS"
    '''
    :stability: experimental
    '''
    AWSAPP_MESH_PREVIEW_SERVICE_ROLE_POLICY = "AWSAPP_MESH_PREVIEW_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    SERVICE_QUOTAS_SERVICE_ROLE_POLICY = "SERVICE_QUOTAS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_MSK_EXECUTION_ROLE = "AWSLAMBDA_MSK_EXECUTION_ROLE"
    '''
    :stability: experimental
    '''
    COMPUTE_OPTIMIZER_READ_ONLY_ACCESS = "COMPUTE_OPTIMIZER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_POLY_DELEGATED_ACCESS_POLICY = "ALEXA_FOR_BUSINESS_POLY_DELEGATED_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_PROCUREMENT_SYSTEM_ADMIN_FULL_ACCESS = "AWSMARKETPLACE_PROCUREMENT_SYSTEM_ADMIN_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSACCOUNT_MANAGEMENT_READ_ONLY_ACCESS = "AWSACCOUNT_MANAGEMENT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_FARGATE_POD_EXECUTION_ROLE_POLICY = "AMAZON_EKS_FARGATE_POD_EXECUTION_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_WIRELESS_READ_ONLY_ACCESS = "AWSIO_T_WIRELESS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_PIPELINES_INTEGRATIONS = "AMAZON_SAGE_MAKER_PIPELINES_INTEGRATIONS"
    '''
    :stability: experimental
    '''
    APP_RUNNER_SERVICE_ROLE_POLICY = "APP_RUNNER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_DEADLINE_RESOURCE_TRACKER_ADMIN_POLICY = "AWSTHINKBOX_DEADLINE_RESOURCE_TRACKER_ADMIN_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_ALL_COMMANDS_FULL_ACCESS = "AMAZON_REDSHIFT_ALL_COMMANDS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    IAMACCESS_ADVISOR_READ_ONLY = "IAMACCESS_ADVISOR_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_FEATURE_STORE_ACCESS = "AMAZON_SAGE_MAKER_FEATURE_STORE_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CODE_GURU_REVIEWER_READ_ONLY_ACCESS = "AMAZON_CODE_GURU_REVIEWER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_AWS_PORTAL_GATEWAY_POLICY = "AWSTHINKBOX_AWS_PORTAL_GATEWAY_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_FAILBACK_POLICY = "AWSELASTIC_DISASTER_RECOVERY_FAILBACK_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_KAFKA_CLUSTER_POLICY = "AWSAPPLICATION_AUTOSCALING_KAFKA_CLUSTER_POLICY"
    '''
    :stability: experimental
    '''
    AWSSYSTEMS_MANAGER_OPS_DATA_SYNC_SERVICE_ROLE_POLICY = "AWSSYSTEMS_MANAGER_OPS_DATA_SYNC_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CODE_GURU_PROFILER_FULL_ACCESS = "AMAZON_CODE_GURU_PROFILER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPROTON_DEVELOPER_ACCESS = "AWSPROTON_DEVELOPER_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEM_SERVICE_ROLE_POLICY = "AMAZON_ELASTIC_FILE_SYSTEM_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_GROUND_TRUTH_EXECUTION = "AMAZON_SAGE_MAKER_GROUND_TRUTH_EXECUTION"
    '''
    :stability: experimental
    '''
    AWSRESOURCE_ACCESS_MANAGER_FULL_ACCESS = "AWSRESOURCE_ACCESS_MANAGER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    CERTIFICATE_MANAGER_SERVICE_ROLE_POLICY = "CERTIFICATE_MANAGER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_ENABLE_IO_T_LOGGING_MITIGATION_ACTION = "AWSIO_T_DEVICE_DEFENDER_ENABLE_IO_T_LOGGING_MITIGATION_ACTION"
    '''
    :stability: experimental
    '''
    AWSGRAFANA_WORKSPACE_PERMISSION_MANAGEMENT = "AWSGRAFANA_WORKSPACE_PERMISSION_MANAGEMENT"
    '''
    :stability: experimental
    '''
    AMAZONNIMBLESTUDIO_LAUNCHPROFILEWORKER = "AMAZONNIMBLESTUDIO_LAUNCHPROFILEWORKER"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ROLE_CW_L = "AWSELASTIC_BEANSTALK_ROLE_CW_L"
    '''
    :stability: experimental
    '''
    DYNAMO_DB_CLOUD_WATCH_CONTRIBUTOR_INSIGHTS_SERVICE_ROLE_POLICY = "DYNAMO_DB_CLOUD_WATCH_CONTRIBUTOR_INSIGHTS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DETECTIVE_SERVICE_LINKED_ROLE_POLICY = "AMAZON_DETECTIVE_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ROLE_RD_S = "AWSELASTIC_BEANSTALK_ROLE_RD_S"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_SHARING = "AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_SHARING"
    '''
    :stability: experimental
    '''
    AWSECRPULLTHROUGHCACHE_SERVICEROLEPOLICY = "AWSECRPULLTHROUGHCACHE_SERVICEROLEPOLICY"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_SERVICE_ROLE_POLICY = "AWSPANORAMA_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_CONVERSION_SERVER_POLICY = "AWSELASTIC_DISASTER_RECOVERY_CONVERSION_SERVER_POLICY"
    '''
    :stability: experimental
    '''
    AMAZONEMRREADONLYACCESSPOLICY_V2 = "AMAZONEMRREADONLYACCESSPOLICY_V2"
    '''
    :stability: experimental
    '''
    AMAZON_EVENT_BRIDGE_API_DESTINATIONS_SERVICE_ROLE_POLICY = "AMAZON_EVENT_BRIDGE_API_DESTINATIONS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICEROLEFORCODEGURU_PROFILER = "AWSSERVICEROLEFORCODEGURU_PROFILER"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_VOICE_CONNECTOR_SERVICE_LINKED_ROLE_POLICY = "AMAZON_CHIME_VOICE_CONNECTOR_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_PROMETHEUS_QUERY_ACCESS = "AMAZON_PROMETHEUS_QUERY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_GRAFANA_REDSHIFT_ACCESS = "AMAZON_GRAFANA_REDSHIFT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DEV_OPS_GURU_CONSOLE_FULL_ACCESS = "AMAZON_DEV_OPS_GURU_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_DOCS_FULL_ACCESS = "AMAZON_WORK_DOCS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_WORKBOOK_READ_ONLY_ACCESS = "AMAZON_HONEYCODE_WORKBOOK_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    MEDIA_PACKAGE_SERVICE_ROLE_POLICY = "MEDIA_PACKAGE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_GRAFANA_ATHENA_ACCESS = "AMAZON_GRAFANA_ATHENA_ACCESS"
    '''
    :stability: experimental
    '''
    IAMACCESS_ANALYZER_READ_ONLY_ACCESS = "IAMACCESS_ANALYZER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_WATCH_RUM_SERVICE_ROLE_POLICY = "AMAZON_CLOUD_WATCH_RUM_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_EVENT_BRIDGE_SCHEMAS_SERVICE_ROLE_POLICY = "AMAZON_EVENT_BRIDGE_SCHEMAS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_PUBLISH_FINDINGS_TO_SNS_MITIGATION_ACTION = "AWSIO_T_DEVICE_DEFENDER_PUBLISH_FINDINGS_TO_SNS_MITIGATION_ACTION"
    '''
    :stability: experimental
    '''
    AMAZON_QLDB_CONSOLE_FULL_ACCESS = "AMAZON_QLDB_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSGLUE_SCHEMA_REGISTRY_FULL_ACCESS = "AWSGLUE_SCHEMA_REGISTRY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_CONNECTOR_SERVICE_ROLE_POLICY = "AMAZON_EKS_CONNECTOR_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_APP_REGISTRY_SERVICE_ROLE_POLICY = "AWSSERVICE_CATALOG_APP_REGISTRY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_FLEET_HUB_FEDERATION_ACCESS = "AWSIO_T_FLEET_HUB_FEDERATION_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPROTON_SYNC_SERVICE_ROLE_POLICY = "AWSPROTON_SYNC_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_WRITE_ACCESS = "AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_WRITE_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_SERVICE_ROLE_POLICY = "AWSELASTIC_DISASTER_RECOVERY_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_COMPREHEND_ENDPOINT_POLICY = "AWSAPPLICATION_AUTOSCALING_COMPREHEND_ENDPOINT_POLICY"
    '''
    :stability: experimental
    '''
    AWSCLOUD_SHELL_FULL_ACCESS = "AWSCLOUD_SHELL_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_ADD_THINGS_TO_THING_GROUP_MITIGATION_ACTION = "AWSIO_T_DEVICE_DEFENDER_ADD_THINGS_TO_THING_GROUP_MITIGATION_ACTION"
    '''
    :stability: experimental
    '''
    AMAZON_MEMORY_DB_READ_ONLY_ACCESS = "AMAZON_MEMORY_DB_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_WIRELESS_DATA_ACCESS = "AWSIO_T_WIRELESS_DATA_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_QLDB_FULL_ACCESS = "AMAZON_QLDB_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_SPACES_WEB_READ_ONLY = "AMAZON_WORK_SPACES_WEB_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_AUGMENTED_AI_FULL_ACCESS = "AMAZON_AUGMENTED_AI_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEEP_RACER_ACCOUNT_ADMIN_ACCESS = "AWSDEEP_RACER_ACCOUNT_ADMIN_ACCESS"
    '''
    :stability: experimental
    '''
    AWSEC2_CAPACITY_RESERVATION_FLEET_ROLE_POLICY = "AWSEC2_CAPACITY_RESERVATION_FLEET_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_KEYSPACES_FULL_ACCESS = "AMAZON_KEYSPACES_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_REPLACE_DEFAULT_POLICY_MITIGATION_ACTION = "AWSIO_T_DEVICE_DEFENDER_REPLACE_DEFAULT_POLICY_MITIGATION_ACTION"
    '''
    :stability: experimental
    '''
    AWSAPP_MESH_READ_ONLY = "AWSAPP_MESH_READ_ONLY"
    '''
    :stability: experimental
    '''
    COMPUTE_OPTIMIZER_SERVICE_ROLE_POLICY = "COMPUTE_OPTIMIZER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_FULL_ACCESS = "AWSAPPLICATION_MIGRATION_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAKE_FORMATION_CROSS_ACCOUNT_MANAGER = "AWSLAKE_FORMATION_CROSS_ACCOUNT_MANAGER"
    '''
    :stability: experimental
    '''
    AWSGLUE_DATA_BREW_SERVICE_ROLE = "AWSGLUE_DATA_BREW_SERVICE_ROLE"
    '''
    :stability: experimental
    '''
    AMAZON_BRAKET_FULL_ACCESS = "AMAZON_BRAKET_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_MANAGED_UPDATES_SERVICE_ROLE_POLICY = "AWSELASTIC_BEANSTALK_MANAGED_UPDATES_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_LEX_CHANNELS_ACCESS = "AMAZON_LEX_CHANNELS_ACCESS"
    '''
    :stability: experimental
    '''
    ALEXA_FOR_BUSINESS_LIFESIZE_DELEGATED_ACCESS_POLICY = "ALEXA_FOR_BUSINESS_LIFESIZE_DELEGATED_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_OPEN_SEARCH_SERVICE_COGNITO_ACCESS = "AMAZON_OPEN_SEARCH_SERVICE_COGNITO_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_TIMESTREAM_READ_ONLY_ACCESS = "AMAZON_TIMESTREAM_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_FULL_ACCESS = "AWSPANORAMA_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_QLDB_READ_ONLY = "AMAZON_QLDB_READ_ONLY"
    '''
    :stability: experimental
    '''
    AWSCHATBOT_SERVICE_LINKED_ROLE_POLICY = "AWSCHATBOT_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSDEEP_RACER_DEFAULT_MULTI_USER_ACCESS = "AWSDEEP_RACER_DEFAULT_MULTI_USER_ACCESS"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_READONLYACCESS = "AWSLAMBDA_READONLYACCESS"
    '''
    :stability: experimental
    '''
    AWSCODEPIPELINE_READONLYACCESS = "AWSCODEPIPELINE_READONLYACCESS"
    '''
    :stability: experimental
    '''
    AWSPRIVATE_NETWORKS_SERVICE_ROLE_POLICY = "AWSPRIVATE_NETWORKS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    S3_STORAGE_LENS_SERVICE_ROLE_POLICY = "S3_STORAGE_LENS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    SERVER_MIGRATION_SERVICE_CONSOLE_FULL_ACCESS = "SERVER_MIGRATION_SERVICE_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPP_SYNC_SERVICE_ROLE_POLICY = "AWSAPP_SYNC_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPP_MESH_FULL_ACCESS = "AWSAPP_MESH_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSINCIDENT_MANAGER_SERVICE_ROLE_POLICY = "AWSINCIDENT_MANAGER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSPROTON_FULL_ACCESS = "AWSPROTON_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_AGENT_POLICY = "AWSELASTIC_DISASTER_RECOVERY_AGENT_POLICY"
    '''
    :stability: experimental
    '''
    AWSCLOUD9_SSM_INSTANCE_PROFILE = "AWSCLOUD9_SSM_INSTANCE_PROFILE"
    '''
    :stability: experimental
    '''
    ELEMENTAL_ACTIVATIONS_DOWNLOAD_SOFTWARE_ACCESS = "ELEMENTAL_ACTIVATIONS_DOWNLOAD_SOFTWARE_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_GREENGRASS_GROUP_ROLE_POLICY = "AWSPANORAMA_GREENGRASS_GROUP_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_DETECTIVE_FULL_ACCESS = "AMAZON_DETECTIVE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSSMOPS_INSIGHTS_SERVICE_ROLE_POLICY = "AWSSSMOPS_INSIGHTS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSTRANSFER_READ_ONLY_ACCESS = "AWSTRANSFER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    SERVICE_QUOTAS_READ_ONLY_ACCESS = "SERVICE_QUOTAS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    EC2_FLEET_TIME_SHIFTABLE_SERVICE_ROLE_POLICY = "EC2_FLEET_TIME_SHIFTABLE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    MIGRATION_HUB_DMS_ACCESS_SERVICE_ROLE_POLICY = "MIGRATION_HUB_DMS_ACCESS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_END_USER_READ_ONLY_ACCESS = "AWSSERVICE_CATALOG_END_USER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIOT_ROBO_RUNNER_FULL_ACCESS = "AWSIOT_ROBO_RUNNER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    ELEMENTAL_ACTIVATIONS_FULL_ACCESS = "ELEMENTAL_ACTIVATIONS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIQPERMISSION_SERVICE_ROLE_POLICY = "AWSIQPERMISSION_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    ROUTE53_RECOVERY_READINESS_SERVICE_ROLE_POLICY = "ROUTE53_RECOVERY_READINESS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_FOR_FARGATE_SERVICE_ROLE_POLICY = "AMAZON_EKS_FOR_FARGATE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    ELEMENTAL_ACTIVATIONS_READ_ONLY_ACCESS = "ELEMENTAL_ACTIVATIONS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    MIGRATION_HUB_SMS_ACCESS_SERVICE_ROLE_POLICY = "MIGRATION_HUB_SMS_ACCESS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    CLOUD_FORMATION_STACK_SETS_ORG_ADMIN_SERVICE_ROLE_POLICY = "CLOUD_FORMATION_STACK_SETS_ORG_ADMIN_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIPAMSERVICE_ROLE_POLICY = "AWSIPAMSERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_EVENT_BRIDGE_SCHEMAS_FULL_ACCESS = "AMAZON_EVENT_BRIDGE_SCHEMAS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_SELLER_FULL_ACCESS = "AWSMARKETPLACE_SELLER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_QUERY_EDITOR_V2_NO_SHARING = "AMAZON_REDSHIFT_QUERY_EDITOR_V2_NO_SHARING"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_AUTOMATIC_DASHBOARDS_ACCESS = "CLOUD_WATCH_AUTOMATIC_DASHBOARDS_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEEP_RACER_FULL_ACCESS = "AWSDEEP_RACER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_MAIL_EVENTS_SERVICE_ROLE_POLICY = "AMAZON_WORK_MAIL_EVENTS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_TEAM_ASSOCIATION_FULL_ACCESS = "AMAZON_HONEYCODE_TEAM_ASSOCIATION_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_PROMETHEUS_REMOTE_WRITE_ACCESS = "AMAZON_PROMETHEUS_REMOTE_WRITE_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DEV_OPS_GURU_READ_ONLY_ACCESS = "AMAZON_DEV_OPS_GURU_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_EVENT_BRIDGE_SCHEMAS_READ_ONLY_ACCESS = "AMAZON_EVENT_BRIDGE_SCHEMAS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_FIS_SERVICE_ROLE_POLICY = "AMAZON_FIS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_WORKER_POLICY = "AWSTHINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_WORKER_POLICY"
    '''
    :stability: experimental
    '''
    AWSCLOUDWATCHALARMS_ACTIONSSMINCIDENTSSERVICEROLEPOLICY = "AWSCLOUDWATCHALARMS_ACTIONSSMINCIDENTSSERVICEROLEPOLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_WIRELESS_FULL_PUBLISH_ACCESS = "AWSIO_T_WIRELESS_FULL_PUBLISH_ACCESS"
    '''
    :stability: experimental
    '''
    GAME_LIFT_GAME_SERVER_GROUP_POLICY = "GAME_LIFT_GAME_SERVER_GROUP_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MWAA_SERVICE_ROLE_POLICY = "AMAZON_MWAA_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_SPACES_WEB_SERVICE_ROLE_POLICY = "AMAZON_WORK_SPACES_WEB_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSQUICKSIGHT_OPEN_SEARCH_POLICY = "AWSQUICKSIGHT_OPEN_SEARCH_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_FAILBACK_INSTALLATION_POLICY = "AWSELASTIC_DISASTER_RECOVERY_FAILBACK_INSTALLATION_POLICY"
    '''
    :stability: experimental
    '''
    AMAZONCONNECT_FULLACCESS = "AMAZONCONNECT_FULLACCESS"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_LIVE_FULL_ACCESS = "AWSELEMENTAL_MEDIA_LIVE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_SELLER_PRODUCTS_READ_ONLY = "AWSMARKETPLACE_SELLER_PRODUCTS_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_MCS_FULL_ACCESS = "AMAZON_MCS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_SITE_WISE_CONSOLE_FULL_ACCESS = "AWSIO_T_SITE_WISE_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_FULL_ACCESS = "AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_UPDATE_DEVICE_CERT_MITIGATION_ACTION = "AWSIO_T_DEVICE_DEFENDER_UPDATE_DEVICE_CERT_MITIGATION_ACTION"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_ASSET_SERVER_POLICY = "AWSTHINKBOX_ASSET_SERVER_POLICY"
    '''
    :stability: experimental
    '''
    AWSFOR_WORD_PRESS_PLUGIN_POLICY = "AWSFOR_WORD_PRESS_PLUGIN_POLICY"
    '''
    :stability: experimental
    '''
    KAFKA_CONNECT_SERVICE_ROLE_POLICY = "KAFKA_CONNECT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSTRANSFER_FULL_ACCESS = "AWSTRANSFER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_AMAZON_EKS_NODEGROUP = "AWSSERVICE_ROLE_FOR_AMAZON_EKS_NODEGROUP"
    '''
    :stability: experimental
    '''
    AWSGRAFANA_ACCOUNT_ADMINISTRATOR = "AWSGRAFANA_ACCOUNT_ADMINISTRATOR"
    '''
    :stability: experimental
    '''
    AWSBACKUP_OPERATOR_ACCESS = "AWSBACKUP_OPERATOR_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_REFACTOR_SPACES_SERVICE_ROLE_POLICY = "AWSMIGRATION_HUB_REFACTOR_SPACES_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_LAMBDA_CONCURRENCY_POLICY = "AWSAPPLICATION_AUTOSCALING_LAMBDA_CONCURRENCY_POLICY"
    '''
    :stability: experimental
    '''
    AWSBUDGETS_ACTIONS_ROLE_POLICY_FOR_RESOURCE_ADMINISTRATION_WITH_SS_M = "AWSBUDGETS_ACTIONS_ROLE_POLICY_FOR_RESOURCE_ADMINISTRATION_WITH_SS_M"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_DEFENDER_UPDATE_CA_CERT_MITIGATION_ACTION = "AWSIO_T_DEVICE_DEFENDER_UPDATE_CA_CERT_MITIGATION_ACTION"
    '''
    :stability: experimental
    '''
    AWSBACKUP_SERVICE_LINKED_ROLE_POLICY_FOR_BACKUP_TEST = "AWSBACKUP_SERVICE_LINKED_ROLE_POLICY_FOR_BACKUP_TEST"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_MGH_ACCESS = "AWSAPPLICATION_MIGRATION_MGH_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDEVICE_FARM_TEST_GRID_SERVICE_ROLE_POLICY = "AWSDEVICE_FARM_TEST_GRID_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_EQUIPMENT_FULL_ACCESS = "AMAZON_LOOKOUT_EQUIPMENT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSPURCHASE_ORDERS_SERVICE_ROLE_POLICY = "AWSPURCHASE_ORDERS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_TEAM_ASSOCIATION_READ_ONLY_ACCESS = "AMAZON_HONEYCODE_TEAM_ASSOCIATION_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_SPACES_SERVICE_ACCESS = "AMAZON_WORK_SPACES_SERVICE_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSECURITY_HUB_ORGANIZATIONS_ACCESS = "AWSSECURITY_HUB_ORGANIZATIONS_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEMS_UTILS = "AMAZON_ELASTIC_FILE_SYSTEMS_UTILS"
    '''
    :stability: experimental
    '''
    AWSCOST_AND_USAGE_REPORT_AUTOMATION_POLICY = "AWSCOST_AND_USAGE_REPORT_AUTOMATION_POLICY"
    '''
    :stability: experimental
    '''
    MEMORY_DB_SERVICE_ROLE_POLICY = "MEMORY_DB_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSLICENSE_MANAGER_CONSUMPTION_POLICY = "AWSLICENSE_MANAGER_CONSUMPTION_POLICY"
    '''
    :stability: experimental
    '''
    AWSTRANSFER_CONSOLE_FULL_ACCESS = "AWSTRANSFER_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_EKS_SERVICE_ROLE_POLICY = "AMAZON_EKS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_WIRELESS_LOGGING = "AWSIO_T_WIRELESS_LOGGING"
    '''
    :stability: experimental
    '''
    AWSCONFIG_MULTI_ACCOUNT_SETUP_POLICY = "AWSCONFIG_MULTI_ACCOUNT_SETUP_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_WIRELESS_FULL_ACCESS = "AWSIO_T_WIRELESS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_LIVE_READ_ONLY = "AWSELEMENTAL_MEDIA_LIVE_READ_ONLY"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_ONLY_ACCESS = "AMAZON_ELASTIC_FILE_SYSTEM_CLIENT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_MAP_REDUCE_PLACEMENT_GROUP_POLICY = "AMAZON_ELASTIC_MAP_REDUCE_PLACEMENT_GROUP_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS = "AWSELASTIC_DISASTER_RECOVERY_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_COGNITO_IDP_SERVICE_ROLE_POLICY = "AMAZON_COGNITO_IDP_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MQ_SERVICE_ROLE_POLICY = "AMAZON_MQ_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_SERVICE_ROLE_POLICY = "AWSAPPLICATION_MIGRATION_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MEMORY_DB_FULL_ACCESS = "AMAZON_MEMORY_DB_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_KEYSPACES_READ_ONLY_ACCESS = "AMAZON_KEYSPACES_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_AGENT_INSTALLATION_POLICY = "AWSELASTIC_DISASTER_RECOVERY_AGENT_INSTALLATION_POLICY"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_STRATEGY_COLLECTOR = "AWSMIGRATION_HUB_STRATEGY_COLLECTOR"
    '''
    :stability: experimental
    '''
    CLOUD_FORMATION_STACK_SETS_ORG_MEMBER_SERVICE_ROLE_POLICY = "CLOUD_FORMATION_STACK_SETS_ORG_MEMBER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSRESOURCE_ACCESS_MANAGER_RESOURCE_SHARE_PARTICIPANT_ACCESS = "AWSRESOURCE_ACCESS_MANAGER_RESOURCE_SHARE_PARTICIPANT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_WRITE_SHARING = "AMAZON_REDSHIFT_QUERY_EDITOR_V2_READ_WRITE_SHARING"
    '''
    :stability: experimental
    '''
    AWSBILLING_READ_ONLY_ACCESS = "AWSBILLING_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    SERVER_MIGRATION_SERVICE_ROLE_FOR_INSTANCE_VALIDATION = "SERVER_MIGRATION_SERVICE_ROLE_FOR_INSTANCE_VALIDATION"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_AUTOSCALING_NEPTUNE_CLUSTER_POLICY = "AWSAPPLICATION_AUTOSCALING_NEPTUNE_CLUSTER_POLICY"
    '''
    :stability: experimental
    '''
    AWSBACKUP_FULL_ACCESS = "AWSBACKUP_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DEV_OPS_GURU_SERVICE_ROLE_POLICY = "AMAZON_DEV_OPS_GURU_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ROLE_WORKER_TIER = "AWSELASTIC_BEANSTALK_ROLE_WORKER_TIER"
    '''
    :stability: experimental
    '''
    AMAZON_CODE_GURU_PROFILER_READ_ONLY_ACCESS = "AMAZON_CODE_GURU_PROFILER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    ELEMENTAL_ACTIVATIONS_GENERATE_LICENSES = "ELEMENTAL_ACTIVATIONS_GENERATE_LICENSES"
    '''
    :stability: experimental
    '''
    AWSSHIELD_SERVICE_ROLE_POLICY = "AWSSHIELD_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSBUG_BUST_SERVICE_ROLE_POLICY = "AWSBUG_BUST_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPP_RUNNER_SERVICE_POLICY_FOR_ECR_ACCESS = "AWSAPP_RUNNER_SERVICE_POLICY_FOR_ECR_ACCESS"
    '''
    :stability: experimental
    '''
    AWSNETWORK_MANAGER_READ_ONLY_ACCESS = "AWSNETWORK_MANAGER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_DEV_OPS_GURU_ORGANIZATIONS_ACCESS = "AMAZON_DEV_OPS_GURU_ORGANIZATIONS_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZONEMRSERVICEPOLICY_V2 = "AMAZONEMRSERVICEPOLICY_V2"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_READ_ONLY_ACCESS = "AWSAPPLICATION_MIGRATION_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_APP_REGISTRY_READ_ONLY_ACCESS = "AWSSERVICE_CATALOG_APP_REGISTRY_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_CLOUD_WATCH_ALARMS_ACTION_SSM_SERVICE_ROLE_POLICY = "AWSSERVICE_ROLE_FOR_CLOUD_WATCH_ALARMS_ACTION_SSM_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    IVSRECORD_TO_S3 = "IVSRECORD_TO_S3"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RECOVERY_READINESS_READ_ONLY_ACCESS = "AMAZON_ROUTE53_RECOVERY_READINESS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_MAIL_MESSAGE_FLOW_READ_ONLY_ACCESS = "AMAZON_WORK_MAIL_MESSAGE_FLOW_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_SYNTHETICS_FULL_ACCESS = "CLOUD_WATCH_SYNTHETICS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDATA_EXCHANGE_SUBSCRIBER_FULL_ACCESS = "AWSDATA_EXCHANGE_SUBSCRIBER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    IAMACCESS_ANALYZER_FULL_ACCESS = "IAMACCESS_ANALYZER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCODE_ARTIFACT_ADMIN_ACCESS = "AWSCODE_ARTIFACT_ADMIN_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_ADMIN_READ_ONLY_ACCESS = "AWSSERVICE_CATALOG_ADMIN_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSQUICK_SIGHT_SAGE_MAKER_POLICY = "AWSQUICK_SIGHT_SAGE_MAKER_POLICY"
    '''
    :stability: experimental
    '''
    AWSDATA_LIFECYCLE_MANAGER_SERVICE_ROLE_FOR_AMI_MANAGEMENT = "AWSDATA_LIFECYCLE_MANAGER_SERVICE_ROLE_FOR_AMI_MANAGEMENT"
    '''
    :stability: experimental
    '''
    AMAZON_MONITRON_FULL_ACCESS = "AMAZON_MONITRON_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_HEALTH_LAKE_READ_ONLY_ACCESS = "AMAZON_HEALTH_LAKE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_SPACES_SELF_SERVICE_ACCESS = "AMAZON_WORK_SPACES_SELF_SERVICE_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_MANAGED_BLOCKCHAIN_SERVICE_ROLE_POLICY = "AMAZON_MANAGED_BLOCKCHAIN_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RECOVERY_CLUSTER_FULL_ACCESS = "AMAZON_ROUTE53_RECOVERY_CLUSTER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_CORE_SERVICE_ROLE_POLICY = "AMAZON_SAGE_MAKER_CORE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_WATCH_RUM_READ_ONLY_ACCESS = "AMAZON_CLOUD_WATCH_RUM_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_ADMIN_POLICY = "AWSTHINKBOX_DEADLINE_SPOT_EVENT_PLUGIN_ADMIN_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_METRICS_READ_ONLY_ACCESS = "AMAZON_LOOKOUT_METRICS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDATA_EXCHANGE_FULL_ACCESS = "AWSDATA_EXCHANGE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSDATA_EXCHANGE_PROVIDER_FULL_ACCESS = "AWSDATA_EXCHANGE_PROVIDER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSBUG_BUST_FULL_ACCESS = "AWSBUG_BUST_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_POLICY_FOR_BACKUP_REPORTS = "AWSSERVICE_ROLE_POLICY_FOR_BACKUP_REPORTS"
    '''
    :stability: experimental
    '''
    CLOUD_WATCH_APPLICATION_INSIGHTS_FULL_ACCESS = "CLOUD_WATCH_APPLICATION_INSIGHTS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCONTROL_TOWER_SERVICE_ROLE_POLICY = "AWSCONTROL_TOWER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_SAGE_MAKER_NOTEBOOKS_SERVICE_ROLE_POLICY = "AMAZON_SAGE_MAKER_NOTEBOOKS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RESOLVER_FULL_ACCESS = "AMAZON_ROUTE53_RESOLVER_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSYSTEMS_MANAGER_CHANGE_MANAGEMENT_SERVICE_POLICY = "AWSSYSTEMS_MANAGER_CHANGE_MANAGEMENT_SERVICE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICE_CATALOG_APP_REGISTRY_FULL_ACCESS = "AWSSERVICE_CATALOG_APP_REGISTRY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    LAKE_FORMATION_DATA_ACCESS_SERVICE_ROLE_POLICY = "LAKE_FORMATION_DATA_ACCESS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSMEDIA_TAILOR_SERVICE_ROLE_POLICY = "AWSMEDIA_TAILOR_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CHIME_SERVICE_ROLE_POLICY = "AMAZON_CHIME_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZONSAGEMAKERADMIN_SERVICECATALOGPRODUCTSSERVICEROLEPOLICY = "AMAZONSAGEMAKERADMIN_SERVICECATALOGPRODUCTSSERVICEROLEPOLICY"
    '''
    :stability: experimental
    '''
    AMAZON_MSK_CONNECT_READ_ONLY_ACCESS = "AMAZON_MSK_CONNECT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSTRUSTED_ADVISOR_REPORTING_SERVICE_ROLE_POLICY = "AWSTRUSTED_ADVISOR_REPORTING_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSOPSWORKSREGISTERCLI_EC2 = "AWSOPSWORKSREGISTERCLI_EC2"
    '''
    :stability: experimental
    '''
    AWSWAFCONSOLE_READ_ONLY_ACCESS = "AWSWAFCONSOLE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSAVINGS_PLANS_FULL_ACCESS = "AWSSAVINGS_PLANS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_IMAGE_BUILDER = "AWSSERVICE_ROLE_FOR_IMAGE_BUILDER"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_RECOVERY_INSTANCE_POLICY = "AWSELASTIC_DISASTER_RECOVERY_RECOVERY_INSTANCE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_OPEN_SEARCH_SERVICE_ROLE_POLICY = "AMAZON_OPEN_SEARCH_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_BRAKET_SERVICE_ROLE_POLICY = "AMAZON_BRAKET_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_CODE_GURU_PROFILER_AGENT_ACCESS = "AMAZON_CODE_GURU_PROFILER_AGENT_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_VISION_CONSOLE_FULL_ACCESS = "AMAZON_LOOKOUT_VISION_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSACCOUNT_MANAGEMENT_FULL_ACCESS = "AWSACCOUNT_MANAGEMENT_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CODE_GURU_REVIEWER_SERVICE_ROLE_POLICY = "AMAZON_CODE_GURU_REVIEWER_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    SERVERMIGRATION_SERVICEROLE = "SERVERMIGRATION_SERVICEROLE"
    '''
    :stability: experimental
    '''
    AWSAPP_MESH_PREVIEW_ENVOY_ACCESS = "AWSAPP_MESH_PREVIEW_ENVOY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSOUTPOSTS_SERVICE_ROLE_POLICY = "AWSOUTPOSTS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_LAMBDA_ROLE_POLICY_FOR_LAUNCH_WIZARD_SA_P = "AMAZON_LAMBDA_ROLE_POLICY_FOR_LAUNCH_WIZARD_SA_P"
    '''
    :stability: experimental
    '''
    AMAZON_E_C2_ROLEFOR_AWS_CODE_DEPLOY_LIMITED = "AMAZON_E_C2_ROLEFOR_AWS_CODE_DEPLOY_LIMITED"
    '''
    :stability: experimental
    '''
    AWSELEMENTAL_MEDIA_TAILOR_FULL_ACCESS = "AWSELEMENTAL_MEDIA_TAILOR_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_STRATEGY_CONSOLE_FULL_ACCESS = "AWSMIGRATION_HUB_STRATEGY_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIOT_ROBO_RUNNER_READ_ONLY = "AWSIOT_ROBO_RUNNER_READ_ONLY"
    '''
    :stability: experimental
    '''
    ECRREPLICATION_SERVICE_ROLE_POLICY = "ECRREPLICATION_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    MIGRATION_HUB_SERVICE_ROLE_POLICY = "MIGRATION_HUB_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_MONITRON_POLICY = "AWSSERVICE_ROLE_FOR_MONITRON_POLICY"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_SAGE_MAKER_ROLE_POLICY = "AWSPANORAMA_SAGE_MAKER_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSPANORAMA_APPLIANCE_SERVICE_ROLE_POLICY = "AWSPANORAMA_APPLIANCE_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSIO_T_WIRELESS_GATEWAY_CERT_MANAGER = "AWSIO_T_WIRELESS_GATEWAY_CERT_MANAGER"
    '''
    :stability: experimental
    '''
    AWSDIRECT_CONNECT_SERVICE_ROLE_POLICY = "AWSDIRECT_CONNECT_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_E_C2_ACCESS = "AWSAPPLICATION_MIGRATION_E_C2_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CLOUD_WATCH_EVIDENTLY_FULL_ACCESS = "AMAZON_CLOUD_WATCH_EVIDENTLY_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIMAGE_BUILDER_READ_ONLY_ACCESS = "AWSIMAGE_BUILDER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSGRAFANA_CONSOLE_READ_ONLY_ACCESS = "AWSGRAFANA_CONSOLE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMARKETPLACE_METERING_REGISTER_USAGE = "AWSMARKETPLACE_METERING_REGISTER_USAGE"
    '''
    :stability: experimental
    '''
    AMAZON_MANAGED_BLOCKCHAIN_READ_ONLY_ACCESS = "AMAZON_MANAGED_BLOCKCHAIN_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_LOOKOUT_VISION_READ_ONLY_ACCESS = "AMAZON_LOOKOUT_VISION_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REKOGNITION_CUSTOM_LABELS_FULL_ACCESS = "AMAZON_REKOGNITION_CUSTOM_LABELS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_HEALTH_LAKE_FULL_ACCESS = "AMAZON_HEALTH_LAKE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSBACKUP_SERVICE_LINKED_ROLE_POLICY_FOR_BACKUP = "AWSBACKUP_SERVICE_LINKED_ROLE_POLICY_FOR_BACKUP"
    '''
    :stability: experimental
    '''
    AMAZON_MANAGED_BLOCKCHAIN_CONSOLE_FULL_ACCESS = "AMAZON_MANAGED_BLOCKCHAIN_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_CONVERSION_SERVER_POLICY = "AWSAPPLICATION_MIGRATION_CONVERSION_SERVER_POLICY"
    '''
    :stability: experimental
    '''
    AWSSAVINGS_PLANS_READ_ONLY_ACCESS = "AWSSAVINGS_PLANS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSMIGRATION_HUB_REFACTOR_SPACES_FULL_ACCESS = "AWSMIGRATION_HUB_REFACTOR_SPACES_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_HONEYCODE_WORKBOOK_FULL_ACCESS = "AMAZON_HONEYCODE_WORKBOOK_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSIO_T_DEVICE_TESTER_FOR_GREENGRASS_FULL_ACCESS = "AWSIO_T_DEVICE_TESTER_FOR_GREENGRASS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ROLE_EC_S = "AWSELASTIC_BEANSTALK_ROLE_EC_S"
    '''
    :stability: experimental
    '''
    AMAZON_WORK_MAIL_MESSAGE_FLOW_FULL_ACCESS = "AMAZON_WORK_MAIL_MESSAGE_FLOW_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSSERVICE_ROLE_FOR_SM_S = "AWSSERVICE_ROLE_FOR_SM_S"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_DEADLINE_RESOURCE_TRACKER_ACCESS_POLICY = "AWSTHINKBOX_DEADLINE_RESOURCE_TRACKER_ACCESS_POLICY"
    '''
    :stability: experimental
    '''
    CLOUDWATCH_CROSSACCOUNTACCESS = "CLOUDWATCH_CROSSACCOUNTACCESS"
    '''
    :stability: experimental
    '''
    AWSLAKE_FORMATION_DATA_ADMIN = "AWSLAKE_FORMATION_DATA_ADMIN"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ROLE_CORE = "AWSELASTIC_BEANSTALK_ROLE_CORE"
    '''
    :stability: experimental
    '''
    AWSLAMBDA_FULLACCESS = "AWSLAMBDA_FULLACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_EMR_CONTAINERS_SERVICE_ROLE_POLICY = "AMAZON_EMR_CONTAINERS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSKEY_MANAGEMENT_SERVICE_MULTI_REGION_KEYS_SERVICE_ROLE_POLICY = "AWSKEY_MANAGEMENT_SERVICE_MULTI_REGION_KEYS_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AWSDENY_ALL = "AWSDENY_ALL"
    '''
    :stability: experimental
    '''
    AWSIQFULL_ACCESS = "AWSIQFULL_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_POWER_USER = "AMAZON_ELASTIC_CONTAINER_REGISTRY_PUBLIC_POWER_USER"
    '''
    :stability: experimental
    '''
    AMAZON_PROMETHEUS_CONSOLE_FULL_ACCESS = "AMAZON_PROMETHEUS_CONSOLE_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_BEANSTALK_ROLE_SN_S = "AWSELASTIC_BEANSTALK_ROLE_SN_S"
    '''
    :stability: experimental
    '''
    EC2_FAST_LAUNCH_SERVICE_ROLE_POLICY = "EC2_FAST_LAUNCH_SERVICE_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_EKSVPC_RESOURCE_CONTROLLER = "AMAZON_EKSVPC_RESOURCE_CONTROLLER"
    '''
    :stability: experimental
    '''
    EC2_INSTANCE_CONNECT = "EC2_INSTANCE_CONNECT"
    '''
    :stability: experimental
    '''
    AWSCOMPROMISED_KEY_QUARANTINE_V2 = "AWSCOMPROMISED_KEY_QUARANTINE_V2"
    '''
    :stability: experimental
    '''
    AMAZON_S3_OBJECT_LAMBDA_EXECUTION_ROLE_POLICY = "AMAZON_S3_OBJECT_LAMBDA_EXECUTION_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    CLIENT_VPN_SERVICE_CONNECTIONS_ROLE_POLICY = "CLIENT_VPN_SERVICE_CONNECTIONS_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_APP_FLOW_FULL_ACCESS = "AMAZON_APP_FLOW_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSELASTIC_DISASTER_RECOVERY_REPLICATION_SERVER_POLICY = "AWSELASTIC_DISASTER_RECOVERY_REPLICATION_SERVER_POLICY"
    '''
    :stability: experimental
    '''
    EC2_IMAGE_BUILDER_CROSS_ACCOUNT_DISTRIBUTION_ACCESS = "EC2_IMAGE_BUILDER_CROSS_ACCOUNT_DISTRIBUTION_ACCESS"
    '''
    :stability: experimental
    '''
    AWSTHINKBOX_AWS_PORTAL_WORKER_POLICY = "AWSTHINKBOX_AWS_PORTAL_WORKER_POLICY"
    '''
    :stability: experimental
    '''
    AMAZON_S3_OUTPOSTS_READ_ONLY_ACCESS = "AMAZON_S3_OUTPOSTS_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AWSCOMPROMISED_KEY_QUARANTINE = "AWSCOMPROMISED_KEY_QUARANTINE"
    '''
    :stability: experimental
    '''
    AWSAPP_MESH_ENVOY_ACCESS = "AWSAPP_MESH_ENVOY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_ROUTE53_RECOVERY_CLUSTER_READ_ONLY_ACCESS = "AMAZON_ROUTE53_RECOVERY_CLUSTER_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_KENDRA_READ_ONLY_ACCESS = "AMAZON_KENDRA_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_PROMETHEUS_FULL_ACCESS = "AMAZON_PROMETHEUS_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWS_CONFIGROLE = "AWS_CONFIGROLE"
    '''
    :stability: experimental
    '''
    AMAZON_OPEN_SEARCH_SERVICE_READ_ONLY_ACCESS = "AMAZON_OPEN_SEARCH_SERVICE_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_CONNECT_CAMPAIGNS_SERVICE_LINKED_ROLE_POLICY = "AMAZON_CONNECT_CAMPAIGNS_SERVICE_LINKED_ROLE_POLICY"
    '''
    :stability: experimental
    '''
    AMAZONNIMBLESTUDIO_STUDIOADMIN = "AMAZONNIMBLESTUDIO_STUDIOADMIN"
    '''
    :stability: experimental
    '''
    AWSCODE_ARTIFACT_READ_ONLY_ACCESS = "AWSCODE_ARTIFACT_READ_ONLY_ACCESS"
    '''
    :stability: experimental
    '''
    AMAZON_REDSHIFT_DATA_FULL_ACCESS = "AMAZON_REDSHIFT_DATA_FULL_ACCESS"
    '''
    :stability: experimental
    '''
    AWSAPPLICATION_MIGRATION_REPLICATION_SERVER_POLICY = "AWSAPPLICATION_MIGRATION_REPLICATION_SERVER_POLICY"
    '''
    :stability: experimental
    '''


class LambdaArmFunction(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-common.LambdaArmFunction",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        code: aws_cdk.aws_lambda.Code,
        handler: builtins.str,
        runtime: aws_cdk.aws_lambda.Runtime,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        architectures: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.Architecture]] = None,
        code_signing_config: typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[aws_cdk.aws_lambda.VersionOptions] = None,
        dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        events: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.IEventSource]] = None,
        filesystem: typing.Optional[aws_cdk.aws_lambda.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        insights_version: typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions] = None,
        log_retention_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
        tracing: typing.Optional[aws_cdk.aws_lambda.Tracing] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        max_event_age: typing.Optional[aws_cdk.core.Duration] = None,
        on_failure: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_success: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when when defining a function from a Docker image.
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param architectures: (deprecated) DEPRECATED. Default: [Architecture.X86_64]
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param security_group: (deprecated) What security group to associate with the Lambda's network interfaces. This property is being deprecated, consider using securityGroups instead. Only used if 'vpc' is supplied. Use securityGroups property instead. Function constructor will throw an error if both are specified. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroups prop, a dedicated security group will be created for this function.
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - the Vpc default strategy if not specified
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2

        :stability: experimental
        '''
        props = LambdaArmFunctionProps(
            code=code,
            handler=handler,
            runtime=runtime,
            allow_all_outbound=allow_all_outbound,
            allow_public_subnet=allow_public_subnet,
            architecture=architecture,
            architectures=architectures,
            code_signing_config=code_signing_config,
            current_version_options=current_version_options,
            dead_letter_queue=dead_letter_queue,
            dead_letter_queue_enabled=dead_letter_queue_enabled,
            description=description,
            environment=environment,
            environment_encryption=environment_encryption,
            events=events,
            filesystem=filesystem,
            function_name=function_name,
            initial_policy=initial_policy,
            insights_version=insights_version,
            layers=layers,
            log_retention=log_retention,
            log_retention_retry_options=log_retention_retry_options,
            log_retention_role=log_retention_role,
            memory_size=memory_size,
            profiling=profiling,
            profiling_group=profiling_group,
            reserved_concurrent_executions=reserved_concurrent_executions,
            role=role,
            security_group=security_group,
            security_groups=security_groups,
            timeout=timeout,
            tracing=tracing,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            max_event_age=max_event_age,
            on_failure=on_failure,
            on_success=on_success,
            retry_attempts=retry_attempts,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))


@jsii.data_type(
    jsii_type="cdk-common.LambdaArmFunctionProps",
    jsii_struct_bases=[aws_cdk.aws_lambda.FunctionProps],
    name_mapping={
        "max_event_age": "maxEventAge",
        "on_failure": "onFailure",
        "on_success": "onSuccess",
        "retry_attempts": "retryAttempts",
        "allow_all_outbound": "allowAllOutbound",
        "allow_public_subnet": "allowPublicSubnet",
        "architecture": "architecture",
        "architectures": "architectures",
        "code_signing_config": "codeSigningConfig",
        "current_version_options": "currentVersionOptions",
        "dead_letter_queue": "deadLetterQueue",
        "dead_letter_queue_enabled": "deadLetterQueueEnabled",
        "description": "description",
        "environment": "environment",
        "environment_encryption": "environmentEncryption",
        "events": "events",
        "filesystem": "filesystem",
        "function_name": "functionName",
        "initial_policy": "initialPolicy",
        "insights_version": "insightsVersion",
        "layers": "layers",
        "log_retention": "logRetention",
        "log_retention_retry_options": "logRetentionRetryOptions",
        "log_retention_role": "logRetentionRole",
        "memory_size": "memorySize",
        "profiling": "profiling",
        "profiling_group": "profilingGroup",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "role": "role",
        "security_group": "securityGroup",
        "security_groups": "securityGroups",
        "timeout": "timeout",
        "tracing": "tracing",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "code": "code",
        "handler": "handler",
        "runtime": "runtime",
    },
)
class LambdaArmFunctionProps(aws_cdk.aws_lambda.FunctionProps):
    def __init__(
        self,
        *,
        max_event_age: typing.Optional[aws_cdk.core.Duration] = None,
        on_failure: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_success: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        architectures: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.Architecture]] = None,
        code_signing_config: typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[aws_cdk.aws_lambda.VersionOptions] = None,
        dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        events: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.IEventSource]] = None,
        filesystem: typing.Optional[aws_cdk.aws_lambda.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        insights_version: typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions] = None,
        log_retention_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
        tracing: typing.Optional[aws_cdk.aws_lambda.Tracing] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        code: aws_cdk.aws_lambda.Code,
        handler: builtins.str,
        runtime: aws_cdk.aws_lambda.Runtime,
    ) -> None:
        '''
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param architectures: (deprecated) DEPRECATED. Default: [Architecture.X86_64]
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param security_group: (deprecated) What security group to associate with the Lambda's network interfaces. This property is being deprecated, consider using securityGroups instead. Only used if 'vpc' is supplied. Use securityGroups property instead. Function constructor will throw an error if both are specified. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroups prop, a dedicated security group will be created for this function.
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - the Vpc default strategy if not specified
        :param code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
        :param handler: The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel. Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
        :param runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide. Use ``Runtime.FROM_IMAGE`` when when defining a function from a Docker image.

        :stability: experimental
        '''
        if isinstance(current_version_options, dict):
            current_version_options = aws_cdk.aws_lambda.VersionOptions(**current_version_options)
        if isinstance(log_retention_retry_options, dict):
            log_retention_retry_options = aws_cdk.aws_lambda.LogRetentionRetryOptions(**log_retention_retry_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "handler": handler,
            "runtime": runtime,
        }
        if max_event_age is not None:
            self._values["max_event_age"] = max_event_age
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if allow_public_subnet is not None:
            self._values["allow_public_subnet"] = allow_public_subnet
        if architecture is not None:
            self._values["architecture"] = architecture
        if architectures is not None:
            self._values["architectures"] = architectures
        if code_signing_config is not None:
            self._values["code_signing_config"] = code_signing_config
        if current_version_options is not None:
            self._values["current_version_options"] = current_version_options
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if dead_letter_queue_enabled is not None:
            self._values["dead_letter_queue_enabled"] = dead_letter_queue_enabled
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if events is not None:
            self._values["events"] = events
        if filesystem is not None:
            self._values["filesystem"] = filesystem
        if function_name is not None:
            self._values["function_name"] = function_name
        if initial_policy is not None:
            self._values["initial_policy"] = initial_policy
        if insights_version is not None:
            self._values["insights_version"] = insights_version
        if layers is not None:
            self._values["layers"] = layers
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if log_retention_retry_options is not None:
            self._values["log_retention_retry_options"] = log_retention_retry_options
        if log_retention_role is not None:
            self._values["log_retention_role"] = log_retention_role
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if profiling is not None:
            self._values["profiling"] = profiling
        if profiling_group is not None:
            self._values["profiling_group"] = profiling_group
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing is not None:
            self._values["tracing"] = tracing
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def max_event_age(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The maximum age of a request that Lambda sends to a function for processing.

        Minimum: 60 seconds
        Maximum: 6 hours

        :default: Duration.hours(6)
        '''
        result = self._values.get("max_event_age")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def on_failure(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The destination for failed invocations.

        :default: - no destination
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def on_success(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The destination for successful invocations.

        :default: - no destination
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry when the function returns an error.

        Minimum: 0
        Maximum: 2

        :default: 2
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all network traffic.

        If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_public_subnet(self) -> typing.Optional[builtins.bool]:
        '''Lambda Functions in a public subnet can NOT access the internet.

        Use this property to acknowledge this limitation and still place the function in a public subnet.

        :default: false

        :see: https://stackoverflow.com/questions/52992085/why-cant-an-aws-lambda-function-inside-a-public-subnet-in-a-vpc-connect-to-the/52994841#52994841
        '''
        result = self._values.get("allow_public_subnet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def architecture(self) -> typing.Optional[aws_cdk.aws_lambda.Architecture]:
        '''The system architectures compatible with this lambda function.

        :default: Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Architecture], result)

    @builtins.property
    def architectures(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_lambda.Architecture]]:
        '''(deprecated) DEPRECATED.

        :default: [Architecture.X86_64]

        :deprecated: use ``architecture``

        :stability: deprecated
        '''
        result = self._values.get("architectures")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.Architecture]], result)

    @builtins.property
    def code_signing_config(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig]:
        '''Code signing config associated with this function.

        :default: - Not Sign the Code
        '''
        result = self._values.get("code_signing_config")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig], result)

    @builtins.property
    def current_version_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.VersionOptions]:
        '''Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method.

        :default: - default options as described in ``VersionOptions``
        '''
        result = self._values.get("current_version_options")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.VersionOptions], result)

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.IQueue]:
        '''The SQS queue to use if DLQ is enabled.

        :default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.IQueue], result)

    @builtins.property
    def dead_letter_queue_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enabled DLQ.

        If ``deadLetterQueue`` is undefined,
        an SQS queue with default options will be defined for your Function.

        :default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        '''
        result = self._values.get("dead_letter_queue_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the function.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key-value pairs that Lambda caches and makes available for your Lambda functions.

        Use environment variables to apply configuration changes, such
        as test and production environment configurations, without changing your
        Lambda function source code.

        :default: - No environment variables.
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''The AWS KMS key that's used to encrypt your function's environment variables.

        :default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        '''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def events(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.IEventSource]]:
        '''Event sources for this function.

        You can also add event sources using ``addEventSource``.

        :default: - No event sources.
        '''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.IEventSource]], result)

    @builtins.property
    def filesystem(self) -> typing.Optional[aws_cdk.aws_lambda.FileSystem]:
        '''The filesystem configuration for the lambda function.

        :default: - will not mount any filesystem
        '''
        result = self._values.get("filesystem")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FileSystem], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''A name for the function.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that
        ID for the function's name. For more information, see Name Type.
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initial_policy(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]:
        '''Initial policy statements to add to the created Lambda Role.

        You can call ``addToRolePolicy`` to the created lambda to add statements post creation.

        :default: - No policy statements are added to the created Lambda role.
        '''
        result = self._values.get("initial_policy")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]], result)

    @builtins.property
    def insights_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion]:
        '''Specify the version of CloudWatch Lambda insights to use for monitoring.

        :default: - No Lambda Insights

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights-Getting-Started-docker.html
        '''
        result = self._values.get("insights_version")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion], result)

    @builtins.property
    def layers(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]]:
        '''A list of layers to add to the function's execution environment.

        You can configure your Lambda function to pull in
        additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies
        that can be used by multiple functions.

        :default: - No layers.
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]], result)

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.INFINITE
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def log_retention_retry_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions]:
        '''When log retention is specified, a custom resource attempts to create the CloudWatch log group.

        These options control the retry policy when interacting with CloudWatch APIs.

        :default: - Default AWS SDK retry options.
        '''
        result = self._values.get("log_retention_retry_options")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions], result)

    @builtins.property
    def log_retention_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        :default: - A new role is created.
        '''
        result = self._values.get("log_retention_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU
        power. For more information, see Resource Model in the AWS Lambda
        Developer Guide.

        :default: 128
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def profiling(self) -> typing.Optional[builtins.bool]:
        '''Enable profiling.

        :default: - No profiling.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profiling_group(
        self,
    ) -> typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup]:
        '''Profiling Group.

        :default: - A new profiling group will be created if ``profiling`` is set.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling_group")
        return typing.cast(typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''The maximum of concurrent executions you want to reserve for the function.

        :default: - No specific limit - account limit.

        :see: https://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html
        '''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Lambda execution role.

        This is the role that will be assumed by the function upon execution.
        It controls the permissions that the function will have. The Role must
        be assumable by the 'lambda.amazonaws.com' service principal.

        The default Role automatically has permissions granted for Lambda execution. If you
        provide a Role, you must add the relevant AWS managed policies yourself.

        The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and
        "service-role/AWSLambdaVPCAccessExecutionRole".

        :default:

        - A unique role will be generated for this lambda function.
        Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(deprecated) What security group to associate with the Lambda's network interfaces. This property is being deprecated, consider using securityGroups instead.

        Only used if 'vpc' is supplied.

        Use securityGroups property instead.
        Function constructor will throw an error if both are specified.

        :default:

        - If the function is placed within a VPC and a security group is
        not specified, either by this or securityGroups prop, a dedicated security
        group will be created for this function.

        :deprecated: - This property is deprecated, use securityGroups instead

        :stability: deprecated
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''The list of security groups to associate with the Lambda's network interfaces.

        Only used if 'vpc' is supplied.

        :default:

        - If the function is placed within a VPC and a security group is
        not specified, either by this or securityGroup prop, a dedicated security
        group will be created for this function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.seconds(3)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def tracing(self) -> typing.Optional[aws_cdk.aws_lambda.Tracing]:
        '''Enable AWS X-Ray Tracing for Lambda Function.

        :default: Tracing.Disabled
        '''
        result = self._values.get("tracing")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Tracing], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC network to place Lambda network interfaces.

        Specify this if the Lambda function needs to access resources in a VPC.

        :default: - Function is not placed within a VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied. Note: internet access for Lambdas
        requires a NAT gateway, so picking Public subnets is not allowed.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def code(self) -> aws_cdk.aws_lambda.Code:
        '''The source code of your Lambda function.

        You can point to a file in an
        Amazon Simple Storage Service (Amazon S3) bucket or specify your source
        code as inline text.
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(aws_cdk.aws_lambda.Code, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''The name of the method within your code that Lambda calls to execute your function.

        The format includes the file name. It can also include
        namespaces and other qualifiers, depending on the runtime.
        For more information, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-features.html#gettingstarted-features-programmingmodel.

        Use ``Handler.FROM_IMAGE`` when defining a function from a Docker image.

        NOTE: If you specify your source code as inline text by specifying the
        ZipFile property within the Code property, specify index.function_name as
        the handler.
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime(self) -> aws_cdk.aws_lambda.Runtime:
        '''The runtime environment for the Lambda function that you are uploading.

        For valid values, see the Runtime property in the AWS Lambda Developer
        Guide.

        Use ``Runtime.FROM_IMAGE`` when when defining a function from a Docker image.
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(aws_cdk.aws_lambda.Runtime, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaArmFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AWSManagedPolicies",
    "LambdaArmFunction",
    "LambdaArmFunctionProps",
]

publication.publish()
