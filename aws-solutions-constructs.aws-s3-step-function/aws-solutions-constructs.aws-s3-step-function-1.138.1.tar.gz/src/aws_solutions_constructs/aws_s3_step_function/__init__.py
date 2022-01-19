'''
# aws-s3-step-function module

<!--BEGIN STABILITY BANNER-->---


![Stability: Deprecated](https://img.shields.io/badge/STABILITY-DEPRECATED-red?style=for-the-badge)

> Some of our early constructs don’t meet the naming standards that evolved for the library. We are releasing completely feature compatible versions with corrected names. The underlying implementation code is the same regardless of whether you deploy the construct using the old or new name. We will support both names for all 1.x releases, but in 2.x we will only publish the correctly named constructs. This construct is being replaced by the functionally identical aws-s3-stepfunctions.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_s3_step_function`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-s3-step-function`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.s3stepfunction`|

This AWS Solutions Construct implements an Amazon S3 bucket connected to an AWS Step Function.

*Note - This constructs sends S3 Event Notification to EventBridge, then triggers AWS Step Functions State Machine executions from EventBridge.*

*An alternative architecture can be built that triggers a Lambda function from S3 Event notifications using aws-s3-lambda and aws-lambda-stepfunctions. Channelling the S3 events through Lambda is less flexible than EventBridge, but is more cost effective and has lower latency.*

Here is a minimal deployable pattern definition in Typescript:

```python
import { S3ToStepFunction, S3ToStepFunctionProps } from '@aws-solutions-constructs/aws-s3-step-function';
import * as stepfunctions from '@aws-cdk/aws-stepfunctions';

const startState = new stepfunctions.Pass(stack, 'StartState');

new S3ToStepFunction(this, 'test-s3-step-function-stack', {
    stateMachineProps: {
      definition: startState
    }
});
```

## Initializer

```text
new S3ToStepFunction(scope: Construct, id: string, props: S3ToStepFunctionProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`S3ToStepFunctionProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingBucketObj?|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Existing instance of S3 Bucket object. The existing bucket must have [EventBridge enabled](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-event-notifications-eventbridge.html) for this to work. If this is provided, then also providing bucketProps is an error. |
|bucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Bucket.|
|stateMachineProps|[`sfn.StateMachineProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-stepfunctions.StateMachineProps.html)|User provided props to override the default props for sfn.StateMachine|
|eventRuleProps?|[`events.RuleProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.RuleProps.html)|Optional user provided eventRuleProps to override the defaults|
|deployCloudTrail?|`boolean`|Whether to deploy a Trail in AWS CloudTrail to log API events in Amazon S3. Defaults to `true`. <span style="color:red">**This is now deprecated and ignored because the construct no longer needs CloudTrail since it uses S3 Event Notifications**</span>.|
|createCloudWatchAlarms|`boolean`|Whether to create recommended CloudWatch alarms.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|
|loggingBucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Logging Bucket.|
|logS3AccessLogs?| boolean|Whether to turn on Access Logging for the S3 bucket. Creates an S3 bucket with associated storage costs for the logs. Enabling Access Logging is a best practice. default - true|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|stateMachine|[`sfn.StateMachine`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-stepfunctions.StateMachine.html)|Returns an instance of sfn.StateMachine created by the construct|
|stateMachineLogGroup|[`logs.ILogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.ILogGroup.html)|Returns an instance of the ILogGroup created by the construct for StateMachine|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudwatch.Alarm.html)|Returns a list of cloudwatch.Alarm created by the construct.|
|s3Bucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of the s3.Bucket created by the construct|
|s3LoggingBucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of s3.Bucket created by the construct as the logging bucket for the primary bucket.|
|s3BucketInterface|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Returns an instance of s3.IBucket created by the construct.|

*Note - with the release of Enable EventBridge for Amazon S3, AWS CloudTrail is no longer required to implement this construct. Because of this, the following properties have been removed:*

* cloudtrail
* cloudtrailBucket
* cloudtrailLoggingBucket

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon S3 Bucket

* Enable EventBridge to send events from the S3 Bucket
* Configure Access logging for S3 Bucket
* Enable server-side encryption for S3 Bucket using AWS managed KMS Key
* Enforce encryption of data in transit
* Turn on the versioning for S3 Bucket
* Don't allow public access for S3 Bucket
* Retain the S3 Bucket when deleting the CloudFormation stack
* Applies Lifecycle rule to move noncurrent object versions to Glacier storage after 90 days

### AWS S3 Event Notification

* Enable S3 to send events to EventBridge when an object is created.

### Amazon CloudWatch Events Rule

* Grant least privilege permissions to CloudWatch Events to trigger the Lambda Function

### AWS Step Function

* Enable CloudWatch logging for API Gateway
* Deploy best practices CloudWatch Alarms for the Step Function

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
import aws_cdk.aws_events
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.aws_stepfunctions
import aws_cdk.core


class S3ToStepFunction(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-s3-step-function.S3ToStepFunction",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        state_machine_props: aws_cdk.aws_stepfunctions.StateMachineProps,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        deploy_cloud_trail: typing.Optional[builtins.bool] = None,
        event_rule_props: typing.Optional[aws_cdk.aws_events.RuleProps] = None,
        existing_bucket_obj: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param state_machine_props: User provided StateMachineProps to override the defaults. Default: - None
        :param bucket_props: Optional user provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param deploy_cloud_trail: Whether to deploy a Trail in AWS CloudTrail to log API events in Amazon S3. Default: - true
        :param event_rule_props: Optional User provided eventRuleProps to override the defaults. Default: - None
        :param existing_bucket_obj: Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true

        :access: public
        :summary: Constructs a new instance of the S3ToStepFunction class.
        '''
        props = S3ToStepFunctionProps(
            state_machine_props=state_machine_props,
            bucket_props=bucket_props,
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            deploy_cloud_trail=deploy_cloud_trail,
            event_rule_props=event_rule_props,
            existing_bucket_obj=existing_bucket_obj,
            logging_bucket_props=logging_bucket_props,
            log_group_props=log_group_props,
            log_s3_access_logs=log_s3_access_logs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInterface")
    def s3_bucket_interface(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "s3BucketInterface"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> aws_cdk.aws_stepfunctions.StateMachine:
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineLogGroup")
    def state_machine_log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        return typing.cast(aws_cdk.aws_logs.ILogGroup, jsii.get(self, "stateMachineLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]]:
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]], jsii.get(self, "cloudwatchAlarms"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LoggingBucket")
    def s3_logging_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3LoggingBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-s3-step-function.S3ToStepFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "state_machine_props": "stateMachineProps",
        "bucket_props": "bucketProps",
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "deploy_cloud_trail": "deployCloudTrail",
        "event_rule_props": "eventRuleProps",
        "existing_bucket_obj": "existingBucketObj",
        "logging_bucket_props": "loggingBucketProps",
        "log_group_props": "logGroupProps",
        "log_s3_access_logs": "logS3AccessLogs",
    },
)
class S3ToStepFunctionProps:
    def __init__(
        self,
        *,
        state_machine_props: aws_cdk.aws_stepfunctions.StateMachineProps,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        deploy_cloud_trail: typing.Optional[builtins.bool] = None,
        event_rule_props: typing.Optional[aws_cdk.aws_events.RuleProps] = None,
        existing_bucket_obj: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param state_machine_props: User provided StateMachineProps to override the defaults. Default: - None
        :param bucket_props: Optional user provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param deploy_cloud_trail: Whether to deploy a Trail in AWS CloudTrail to log API events in Amazon S3. Default: - true
        :param event_rule_props: Optional User provided eventRuleProps to override the defaults. Default: - None
        :param existing_bucket_obj: Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true

        :summary: The properties for the S3ToStepFunction Construct
        '''
        if isinstance(state_machine_props, dict):
            state_machine_props = aws_cdk.aws_stepfunctions.StateMachineProps(**state_machine_props)
        if isinstance(bucket_props, dict):
            bucket_props = aws_cdk.aws_s3.BucketProps(**bucket_props)
        if isinstance(event_rule_props, dict):
            event_rule_props = aws_cdk.aws_events.RuleProps(**event_rule_props)
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = aws_cdk.aws_s3.BucketProps(**logging_bucket_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        self._values: typing.Dict[str, typing.Any] = {
            "state_machine_props": state_machine_props,
        }
        if bucket_props is not None:
            self._values["bucket_props"] = bucket_props
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if deploy_cloud_trail is not None:
            self._values["deploy_cloud_trail"] = deploy_cloud_trail
        if event_rule_props is not None:
            self._values["event_rule_props"] = event_rule_props
        if existing_bucket_obj is not None:
            self._values["existing_bucket_obj"] = existing_bucket_obj
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props
        if log_s3_access_logs is not None:
            self._values["log_s3_access_logs"] = log_s3_access_logs

    @builtins.property
    def state_machine_props(self) -> aws_cdk.aws_stepfunctions.StateMachineProps:
        '''User provided StateMachineProps to override the defaults.

        :default: - None
        '''
        result = self._values.get("state_machine_props")
        assert result is not None, "Required property 'state_machine_props' is missing"
        return typing.cast(aws_cdk.aws_stepfunctions.StateMachineProps, result)

    @builtins.property
    def bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the S3 Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_cloud_trail(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a Trail in AWS CloudTrail to log API events in Amazon S3.

        :default: - true
        '''
        result = self._values.get("deploy_cloud_trail")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_rule_props(self) -> typing.Optional[aws_cdk.aws_events.RuleProps]:
        '''Optional User provided eventRuleProps to override the defaults.

        :default: - None
        '''
        result = self._values.get("event_rule_props")
        return typing.cast(typing.Optional[aws_cdk.aws_events.RuleProps], result)

    @builtins.property
    def existing_bucket_obj(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_bucket_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def logging_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the S3 Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    @builtins.property
    def log_s3_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for the S3 bucket with the associated storage costs.

        Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_s3_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ToStepFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "S3ToStepFunction",
    "S3ToStepFunctionProps",
]

publication.publish()
