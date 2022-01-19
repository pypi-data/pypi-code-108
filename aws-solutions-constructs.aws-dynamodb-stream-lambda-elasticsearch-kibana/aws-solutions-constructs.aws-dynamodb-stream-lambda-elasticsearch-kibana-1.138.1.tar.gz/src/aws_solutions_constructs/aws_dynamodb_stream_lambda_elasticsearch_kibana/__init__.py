'''
# aws-dynamodb-stream-lambda-elasticsearch-kibana module

<!--BEGIN STABILITY BANNER-->---


![Stability: Deprecated](https://img.shields.io/badge/STABILITY-DEPRECATED-red?style=for-the-badge)

> Some of our early constructs don’t meet the naming standards that evolved for the library. We are releasing completely feature compatible versions with corrected names. The underlying implementation code is the same regardless of whether you deploy the construct using the old or new name. We will support both names for all 1.x releases, but in 2.x we will only publish the correctly named constructs. This construct is being replaced by the functionally identical aws-dynamodbstreams-lambda-elasticsearch-kibana.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_dynamodb_stream_elasticsearch_kibana`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-dynamodb-stream-lambda-elasticsearch-kibana`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.dynamodbstreamlambdaelasticsearchkibana`|

This AWS Solutions Construct implements Amazon DynamoDB table with stream, AWS Lambda function and Amazon Elasticsearch Service with the least privileged permissions.

Here is a minimal deployable pattern definition in Typescript:

```python
import { DynamoDBStreamToLambdaToElasticSearchAndKibana, DynamoDBStreamToLambdaToElasticSearchAndKibanaProps } from '@aws-solutions-constructs/aws-dynamodb-stream-lambda-elasticsearch-kibana';
import { Aws } from "@aws-cdk/core";

const props: DynamoDBStreamToLambdaToElasticSearchAndKibanaProps = {
  lambdaFunctionProps: {
      code: lambda.Code.fromAsset(`${__dirname}/lambda`),
      runtime: lambda.Runtime.NODEJS_14_X,
      handler: 'index.handler'
  },
  domainName: 'test-domain',
  // TODO: Ensure the Cognito domain name is globally unique
  cognitoDomainName: 'globallyuniquedomain' + Aws.ACCOUNT_ID;
};

new DynamoDBStreamToLambdaToElasticSearchAndKibana(this, 'test-dynamodb-stream-lambda-elasticsearch-kibana', props);
```

## Initializer

```text
new DynamoDBStreamToLambdaToElasticSearchAndKibana(scope: Construct, id: string, props: DynamoDBStreamToLambdaToElasticSearchAndKibanaProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`DynamoDBStreamToLambdaToElasticSearchAndKibanaProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|dynamoTableProps?|[`dynamodb.TableProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.TableProps.html)|Optional user provided props to override the default props for DynamoDB Table|
|existingTableInterface?|[`dynamodb.ITable`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.ITable.html)|Existing instance of DynamoDB table object or interface, providing both this and `dynamoTableProps` will cause an error.|
|dynamoEventSourceProps?|[`aws-lambda-event-sources.DynamoEventSourceProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda-event-sources.DynamoEventSourceProps.html)|Optional user provided props to override the default props for DynamoDB Event Source|
|esDomainProps?|[`elasticsearch.CfnDomainProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticsearch.CfnDomainProps.html)|Optional user provided props to override the default props for the Elasticsearch Service|
|domainName|`string`|Domain name for the Cognito and the Elasticsearch Service|
|createCloudWatchAlarms|`boolean`|Whether to create recommended CloudWatch alarms|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|dynamoTableInterface|[`dynamodb.ITable`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.ITable.html)|Returns an instance of dynamodb.ITable created by the construct|
|dynamoTable?|[`dynamodb.Table`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.Table.html)|Returns an instance of dynamodb.Table created by the construct. IMPORTANT: If existingTableInterface was provided in Pattern Construct Props, this property will be `undefined`|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of lambda.Function created by the construct|
|userPool|[`cognito.UserPool`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.UserPool.html)|Returns an instance of cognito.UserPool created by the construct|
|userPoolClient|[`cognito.UserPoolClient`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.UserPoolClient.html)|Returns an instance of cognito.UserPoolClient created by the construct|
|identityPool|[`cognito.CfnIdentityPool`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cognito.CfnIdentityPool.html)|Returns an instance of cognito.CfnIdentityPool created by the construct|
|elasticsearchDomain|[`elasticsearch.CfnDomain`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticsearch.CfnDomain.html)|Returns an instance of elasticsearch.CfnDomain created by the construct|
|elasticsearchDomain|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of iam.Role created by the construct for elasticsearch.CfnDomain|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudwatch.Alarm.html)|Returns a list of cloudwatch.Alarm created by the construct|

## Lambda Function

This pattern requires a lambda function that can post data into the Elasticsearch from DynamoDB stream. A sample function is provided [here](https://github.com/awslabs/aws-solutions-constructs/blob/master/source/patterns/%40aws-solutions-constructs/aws-dynamodb-stream-lambda-elasticsearch-kibana/test/lambda/index.js).

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon DynamoDB Table

* Set the billing mode for DynamoDB Table to On-Demand (Pay per request)
* Enable server-side encryption for DynamoDB Table using AWS managed KMS Key
* Creates a partition key called 'id' for DynamoDB Table
* Retain the Table when deleting the CloudFormation stack
* Enable continuous backups and point-in-time recovery

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Enable Failure-Handling features like enable bisect on function Error, set defaults for Maximum Record Age (24 hours) & Maximum Retry Attempts (500) and deploy SQS dead-letter queue as destination on failure
* Set Environment Variables

  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon Cognito

* Set password policy for User Pools
* Enforce the advanced security mode for User Pools

### Amazon Elasticsearch Service

* Deploy best practices CloudWatch Alarms for the Elasticsearch Domain
* Secure the Kibana dashboard access with Cognito User Pools
* Enable server-side encryption for Elasticsearch Domain using AWS managed KMS Key
* Enable node-to-node encryption for Elasticsearch Domain
* Configure the cluster for the Amazon ES domain

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_cognito
import aws_cdk.aws_dynamodb
import aws_cdk.aws_elasticsearch
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_event_sources
import aws_cdk.aws_sqs
import aws_cdk.core


class DynamoDBStreamToLambdaToElasticSearchAndKibana(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-dynamodb-stream-lambda-elasticsearch-kibana.DynamoDBStreamToLambdaToElasticSearchAndKibana",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        cognito_domain_name: typing.Optional[builtins.str] = None,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        deploy_sqs_dlq_queue: typing.Optional[builtins.bool] = None,
        dynamo_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps] = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        es_domain_props: typing.Optional[aws_cdk.aws_elasticsearch.CfnDomainProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_table_interface: typing.Optional[aws_cdk.aws_dynamodb.ITable] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        sqs_dlq_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param domain_name: Cognito & ES Domain Name. Default: - None
        :param cognito_domain_name: Optional Cognito Domain Name, if provided it will be used for Cognito Domain, and domainName will be used for the Elasticsearch Domain. Default: - None
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param deploy_sqs_dlq_queue: Whether to deploy a SQS dead letter queue when a data record reaches the Maximum Retry Attempts or Maximum Record Age, its metadata like shard ID and stream ARN will be sent to an SQS queue. Default: - true.
        :param dynamo_event_source_props: Optional user provided props to override the default props. Default: - Default props are used
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param es_domain_props: Optional user provided props to override the default props for the API Gateway. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_table_interface: Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param sqs_dlq_queue_props: Optional user provided properties for the SQS dead letter queue. Default: - Default props are used

        :access: public
        :summary: Constructs a new instance of the LambdaToDynamoDB class.
        '''
        props = DynamoDBStreamToLambdaToElasticSearchAndKibanaProps(
            domain_name=domain_name,
            cognito_domain_name=cognito_domain_name,
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            deploy_sqs_dlq_queue=deploy_sqs_dlq_queue,
            dynamo_event_source_props=dynamo_event_source_props,
            dynamo_table_props=dynamo_table_props,
            es_domain_props=es_domain_props,
            existing_lambda_obj=existing_lambda_obj,
            existing_table_interface=existing_table_interface,
            lambda_function_props=lambda_function_props,
            sqs_dlq_queue_props=sqs_dlq_queue_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoTableInterface")
    def dynamo_table_interface(self) -> aws_cdk.aws_dynamodb.ITable:
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "dynamoTableInterface"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchDomain")
    def elasticsearch_domain(self) -> aws_cdk.aws_elasticsearch.CfnDomain:
        return typing.cast(aws_cdk.aws_elasticsearch.CfnDomain, jsii.get(self, "elasticsearchDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchRole")
    def elasticsearch_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "elasticsearchRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPool")
    def identity_pool(self) -> aws_cdk.aws_cognito.CfnIdentityPool:
        return typing.cast(aws_cdk.aws_cognito.CfnIdentityPool, jsii.get(self, "identityPool"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPool")
    def user_pool(self) -> aws_cdk.aws_cognito.UserPool:
        return typing.cast(aws_cdk.aws_cognito.UserPool, jsii.get(self, "userPool"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolClient")
    def user_pool_client(self) -> aws_cdk.aws_cognito.UserPoolClient:
        return typing.cast(aws_cdk.aws_cognito.UserPoolClient, jsii.get(self, "userPoolClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]]:
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]], jsii.get(self, "cloudwatchAlarms"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoTable")
    def dynamo_table(self) -> typing.Optional[aws_cdk.aws_dynamodb.Table]:
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.Table], jsii.get(self, "dynamoTable"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-dynamodb-stream-lambda-elasticsearch-kibana.DynamoDBStreamToLambdaToElasticSearchAndKibanaProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "cognito_domain_name": "cognitoDomainName",
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "deploy_sqs_dlq_queue": "deploySqsDlqQueue",
        "dynamo_event_source_props": "dynamoEventSourceProps",
        "dynamo_table_props": "dynamoTableProps",
        "es_domain_props": "esDomainProps",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_table_interface": "existingTableInterface",
        "lambda_function_props": "lambdaFunctionProps",
        "sqs_dlq_queue_props": "sqsDlqQueueProps",
    },
)
class DynamoDBStreamToLambdaToElasticSearchAndKibanaProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        cognito_domain_name: typing.Optional[builtins.str] = None,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        deploy_sqs_dlq_queue: typing.Optional[builtins.bool] = None,
        dynamo_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps] = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        es_domain_props: typing.Optional[aws_cdk.aws_elasticsearch.CfnDomainProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_table_interface: typing.Optional[aws_cdk.aws_dynamodb.ITable] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        sqs_dlq_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
    ) -> None:
        '''
        :param domain_name: Cognito & ES Domain Name. Default: - None
        :param cognito_domain_name: Optional Cognito Domain Name, if provided it will be used for Cognito Domain, and domainName will be used for the Elasticsearch Domain. Default: - None
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param deploy_sqs_dlq_queue: Whether to deploy a SQS dead letter queue when a data record reaches the Maximum Retry Attempts or Maximum Record Age, its metadata like shard ID and stream ARN will be sent to an SQS queue. Default: - true.
        :param dynamo_event_source_props: Optional user provided props to override the default props. Default: - Default props are used
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param es_domain_props: Optional user provided props to override the default props for the API Gateway. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_table_interface: Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param sqs_dlq_queue_props: Optional user provided properties for the SQS dead letter queue. Default: - Default props are used

        :summary: The properties for the DynamoDBStreamToLambdaToElastciSearchAndKibana Construct
        '''
        if isinstance(dynamo_event_source_props, dict):
            dynamo_event_source_props = aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps(**dynamo_event_source_props)
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = aws_cdk.aws_dynamodb.TableProps(**dynamo_table_props)
        if isinstance(es_domain_props, dict):
            es_domain_props = aws_cdk.aws_elasticsearch.CfnDomainProps(**es_domain_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(sqs_dlq_queue_props, dict):
            sqs_dlq_queue_props = aws_cdk.aws_sqs.QueueProps(**sqs_dlq_queue_props)
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
        }
        if cognito_domain_name is not None:
            self._values["cognito_domain_name"] = cognito_domain_name
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if deploy_sqs_dlq_queue is not None:
            self._values["deploy_sqs_dlq_queue"] = deploy_sqs_dlq_queue
        if dynamo_event_source_props is not None:
            self._values["dynamo_event_source_props"] = dynamo_event_source_props
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if es_domain_props is not None:
            self._values["es_domain_props"] = es_domain_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_table_interface is not None:
            self._values["existing_table_interface"] = existing_table_interface
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if sqs_dlq_queue_props is not None:
            self._values["sqs_dlq_queue_props"] = sqs_dlq_queue_props

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Cognito & ES Domain Name.

        :default: - None
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cognito_domain_name(self) -> typing.Optional[builtins.str]:
        '''Optional Cognito Domain Name, if provided it will be used for Cognito Domain, and domainName will be used for the Elasticsearch Domain.

        :default: - None
        '''
        result = self._values.get("cognito_domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_sqs_dlq_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a SQS dead letter queue when a data record reaches the Maximum Retry Attempts or Maximum Record Age, its metadata like shard ID and stream ARN will be sent to an SQS queue.

        :default: - true.
        '''
        result = self._values.get("deploy_sqs_dlq_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dynamo_event_source_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_event_source_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps], result)

    @builtins.property
    def dynamo_table_props(self) -> typing.Optional[aws_cdk.aws_dynamodb.TableProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.TableProps], result)

    @builtins.property
    def es_domain_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticsearch.CfnDomainProps]:
        '''Optional user provided props to override the default props for the API Gateway.

        :default: - Default props are used
        '''
        result = self._values.get("es_domain_props")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticsearch.CfnDomainProps], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_table_interface(self) -> typing.Optional[aws_cdk.aws_dynamodb.ITable]:
        '''Existing instance of DynamoDB table object, providing both this and ``dynamoTableProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_table_interface")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.ITable], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default props are used
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def sqs_dlq_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the SQS dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("sqs_dlq_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamoDBStreamToLambdaToElasticSearchAndKibanaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamoDBStreamToLambdaToElasticSearchAndKibana",
    "DynamoDBStreamToLambdaToElasticSearchAndKibanaProps",
]

publication.publish()
