'''
# aws-iot-s3 module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_iot_s3`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-iot-s3`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.iots3`|

This AWS Solutions Construct implements an AWS IoT MQTT topic rule and an Amazon S3 Bucket pattern.

Here is a minimal deployable pattern definition in Typescript:

```python
const { IotToS3Props, IotToS3 } from '@aws-solutions-constructs/aws-iot-s3';

const props: IotToS3Props = {
    iotTopicRuleProps: {
        topicRulePayload: {
            ruleDisabled: false,
            description: "Testing the IotToS3 Pattern",
            sql: "SELECT * FROM 'solutions/constructs'",
            actions: []
        }
    }
};

new IotToS3(this, 'test-iot-s3-integration', props);
```

## Initializer

```text
new IotToS3(scope: Construct, id: string, props: IotToS3Props);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`IotToS3Props`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingBucketInterface?|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Existing S3 Bucket interface. Providing this property and `bucketProps` results in an error.|
|bucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Bucket. Providing this and `existingBucketObj` reults in an error.|
|loggingBucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Logging Bucket.|
|iotTopicRuleProps?|[`iot.CfnTopicRuleProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iot.CfnTopicRuleProps.html)|User provided CfnTopicRuleProps to override the defaults.|
|s3Key|`string`|User provided s3Key to override the default (`${topic()}/${timestamp()}`) object key. Used to store messages matched by the IoT Rule.|
|logS3AccessLogs?|`boolean`|Whether to turn on Access Logging for the S3 bucket. Creates an S3 bucket with associated storage costs for the logs. Enabling Access Logging is a best practice. default - true|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|s3Bucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of the S3 bucket created by the pattern. If an existingBucketInterface is provided in IotToS3Props, then this value will be undefined|
|s3BucketInterface?|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Returns S3 Bucket interface created or used by the pattern. If an existingBucketInterface is provided in IotToS3Props, then only this value will be set and s3Bucket will be undefined. If the construct creates the bucket, then both properties will be set.|
|s3LoggingBucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of `s3.Bucket` created by the construct as the logging bucket for the primary bucket.|
|iotActionsRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of `iam.Role` created by the construct, which allows IoT to publish messages to the S3 bucket.|
|iotTopicRule|[`iot.CfnTopicRule`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iot.CfnTopicRule.html)|Returns an instance of `iot.CfnTopicRule` created by the construct|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon IoT Rule

* Configure an IoT Rule to send messages to the S3 Bucket

### Amazon IAM Role

* Configure least privilege access IAM role for Amazon IoT to be able to publish messages to the S3 Bucket

### Amazon S3 Bucket

* Configure Access logging for S3 Bucket
* Enable server-side encryption for S3 Bucket using AWS managed KMS Key
* Enforce encryption of data in transit
* Turn on the versioning for S3 Bucket
* Don't allow public access for S3 Bucket
* Retain the S3 Bucket when deleting the CloudFormation stack
* Applies Lifecycle rule to move noncurrent object versions to Glacier storage after 90 days

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

import aws_cdk.aws_iam
import aws_cdk.aws_iot
import aws_cdk.aws_s3
import aws_cdk.core


class IotToS3(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-iot-s3.IotToS3",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iot_topic_rule_props: aws_cdk.aws_iot.CfnTopicRuleProps,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_bucket_interface: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
        s3_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param iot_topic_rule_props: User provided CfnTopicRuleProps to override the defaults. Default: - Default props are used. S3ActionProperty with S3 Key '${topic()}/${timestamp()}' is used.
        :param bucket_props: User provided props to override the default props for the S3 Bucket. Default: - Default props are used.
        :param existing_bucket_interface: Existing S3 Bucket interface, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param s3_key: Optional user provided value to override the default S3Key for IoTRule S3 Action. Default: - Default value '${topic()}/${timestamp()}' is used

        :access: public
        :summary: Constructs a new instance of the IotToSqs class.
        '''
        props = IotToS3Props(
            iot_topic_rule_props=iot_topic_rule_props,
            bucket_props=bucket_props,
            existing_bucket_interface=existing_bucket_interface,
            logging_bucket_props=logging_bucket_props,
            log_s3_access_logs=log_s3_access_logs,
            s3_key=s3_key,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotActionsRole")
    def iot_actions_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "iotActionsRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotTopicRule")
    def iot_topic_rule(self) -> aws_cdk.aws_iot.CfnTopicRule:
        return typing.cast(aws_cdk.aws_iot.CfnTopicRule, jsii.get(self, "iotTopicRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInterface")
    def s3_bucket_interface(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "s3BucketInterface"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LoggingBucket")
    def s3_logging_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3LoggingBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-iot-s3.IotToS3Props",
    jsii_struct_bases=[],
    name_mapping={
        "iot_topic_rule_props": "iotTopicRuleProps",
        "bucket_props": "bucketProps",
        "existing_bucket_interface": "existingBucketInterface",
        "logging_bucket_props": "loggingBucketProps",
        "log_s3_access_logs": "logS3AccessLogs",
        "s3_key": "s3Key",
    },
)
class IotToS3Props:
    def __init__(
        self,
        *,
        iot_topic_rule_props: aws_cdk.aws_iot.CfnTopicRuleProps,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_bucket_interface: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
        s3_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iot_topic_rule_props: User provided CfnTopicRuleProps to override the defaults. Default: - Default props are used. S3ActionProperty with S3 Key '${topic()}/${timestamp()}' is used.
        :param bucket_props: User provided props to override the default props for the S3 Bucket. Default: - Default props are used.
        :param existing_bucket_interface: Existing S3 Bucket interface, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param s3_key: Optional user provided value to override the default S3Key for IoTRule S3 Action. Default: - Default value '${topic()}/${timestamp()}' is used

        :summary: The properties for the IotToS3 class.
        '''
        if isinstance(iot_topic_rule_props, dict):
            iot_topic_rule_props = aws_cdk.aws_iot.CfnTopicRuleProps(**iot_topic_rule_props)
        if isinstance(bucket_props, dict):
            bucket_props = aws_cdk.aws_s3.BucketProps(**bucket_props)
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = aws_cdk.aws_s3.BucketProps(**logging_bucket_props)
        self._values: typing.Dict[str, typing.Any] = {
            "iot_topic_rule_props": iot_topic_rule_props,
        }
        if bucket_props is not None:
            self._values["bucket_props"] = bucket_props
        if existing_bucket_interface is not None:
            self._values["existing_bucket_interface"] = existing_bucket_interface
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props
        if log_s3_access_logs is not None:
            self._values["log_s3_access_logs"] = log_s3_access_logs
        if s3_key is not None:
            self._values["s3_key"] = s3_key

    @builtins.property
    def iot_topic_rule_props(self) -> aws_cdk.aws_iot.CfnTopicRuleProps:
        '''User provided CfnTopicRuleProps to override the defaults.

        :default: - Default props are used. S3ActionProperty with S3 Key '${topic()}/${timestamp()}' is used.
        '''
        result = self._values.get("iot_topic_rule_props")
        assert result is not None, "Required property 'iot_topic_rule_props' is missing"
        return typing.cast(aws_cdk.aws_iot.CfnTopicRuleProps, result)

    @builtins.property
    def bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''User provided props to override the default props for the S3 Bucket.

        :default: - Default props are used.
        '''
        result = self._values.get("bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def existing_bucket_interface(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''Existing S3 Bucket interface, providing both this and ``bucketProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_bucket_interface")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def logging_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the S3 Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def log_s3_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for the S3 bucket with the associated storage costs.

        Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_s3_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_key(self) -> typing.Optional[builtins.str]:
        '''Optional user provided value to override the default S3Key for IoTRule S3 Action.

        :default: - Default value '${topic()}/${timestamp()}' is used
        '''
        result = self._values.get("s3_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotToS3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IotToS3",
    "IotToS3Props",
]

publication.publish()
