'''
# aws-iot-kinesisstreams module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_iot_kinesisstreams`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-iot-kinesisstreams`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.iotkinesisstreams`|

This AWS Solutions Construct implements an AWS IoT MQTT topic rule to send data to an Amazon Kinesis Data Stream.

Here is a minimal deployable pattern definition in Typescript:

```python
const { IotToKinesisStreamsProps,
        IotToKinesisStreams } from '@aws-solutions-constructs/aws-iot-kinesisstreams';

const props: IotToKinesisStreamsProps = {
    iotTopicRuleProps: {
        topicRulePayload: {
            ruleDisabled: false,
            description: "Sends data to kinesis data stream",
            sql: "SELECT * FROM 'solutions/construct'",
            actions: []
        }
    }
};

new IotToKinesisStreams(this, 'test-iot-kinesisstream', props);
```

## Initializer

```text
new IotToKinesisStreams(scope: Construct, id: string, props: IotToKinesisStreamsProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`IotToKinesisStreamsProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|iotTopicRuleProps|[`iot.CfnTopicRuleProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iot.CfnTopicRuleProps.html)|User provided CfnTopicRuleProps to override the defaults|
|existingStreamObj?|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Existing instance of Kinesis Stream, providing both this and `kinesisStreamProps` will cause an error.|
|kinesisStreamProps?|[`kinesis.StreamProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.StreamProps.html)|Optional user-provided props to override the default props for the Kinesis data stream, providing both this and `existingStreamObj` will cause an error|
|createCloudWatchAlarms|`boolean`|Whether to create recommended CloudWatch alarms for Kinesis Data Stream. Default value is set to `true`|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|iotTopicRule|[`iot.CfnTopicRule`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iot.CfnTopicRule.html)|Returns an instance of iot.CfnTopicRule created by the construct|
|iotActionsRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for IoT Rule|
|kinesisStream|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Returns an instance of the Kinesis stream created by the construct.|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudwatch.Alarm.html)|Returns an array of recommended CloudWatch Alarms created by the construct for Kinesis Data stream|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon IoT Rule

* Configure least privilege access IAM role for Amazon IoT Rule

### Amazon Kinesis Data Stream

* Configure recommended CloudWatch Alarms for Amazon Kinesis Data Stream
* Configure least privilege access IAM role for Amazon Kinesis Data Stream

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
import aws_cdk.aws_iam
import aws_cdk.aws_iot
import aws_cdk.aws_kinesis
import aws_cdk.core


class IotToKinesisStreams(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-iot-kinesisstreams.IotToKinesisStreams",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        iot_topic_rule_props: aws_cdk.aws_iot.CfnTopicRuleProps,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        kinesis_stream_props: typing.Any = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param iot_topic_rule_props: User provided CfnTopicRuleProps to override the defaults. Default: - Default props are used
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param existing_stream_obj: Existing instance of Kinesis Stream object, providing both this and KinesisStreamProps will cause an error. Default: - Default props are used
        :param kinesis_stream_props: User provided props to override the default props for the Kinesis Stream. Default: - Default props are used

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the IotToKinesisFirehoseToS3 class.
        '''
        props = IotToKinesisStreamsProps(
            iot_topic_rule_props=iot_topic_rule_props,
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            existing_stream_obj=existing_stream_obj,
            kinesis_stream_props=kinesis_stream_props,
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
    @jsii.member(jsii_name="kinesisStream")
    def kinesis_stream(self) -> aws_cdk.aws_kinesis.Stream:
        return typing.cast(aws_cdk.aws_kinesis.Stream, jsii.get(self, "kinesisStream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]]:
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]], jsii.get(self, "cloudwatchAlarms"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-iot-kinesisstreams.IotToKinesisStreamsProps",
    jsii_struct_bases=[],
    name_mapping={
        "iot_topic_rule_props": "iotTopicRuleProps",
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "existing_stream_obj": "existingStreamObj",
        "kinesis_stream_props": "kinesisStreamProps",
    },
)
class IotToKinesisStreamsProps:
    def __init__(
        self,
        *,
        iot_topic_rule_props: aws_cdk.aws_iot.CfnTopicRuleProps,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        kinesis_stream_props: typing.Any = None,
    ) -> None:
        '''
        :param iot_topic_rule_props: User provided CfnTopicRuleProps to override the defaults. Default: - Default props are used
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param existing_stream_obj: Existing instance of Kinesis Stream object, providing both this and KinesisStreamProps will cause an error. Default: - Default props are used
        :param kinesis_stream_props: User provided props to override the default props for the Kinesis Stream. Default: - Default props are used

        :summary: The properties for the IotToKinesisFirehoseToS3 Construct
        '''
        if isinstance(iot_topic_rule_props, dict):
            iot_topic_rule_props = aws_cdk.aws_iot.CfnTopicRuleProps(**iot_topic_rule_props)
        self._values: typing.Dict[str, typing.Any] = {
            "iot_topic_rule_props": iot_topic_rule_props,
        }
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props

    @builtins.property
    def iot_topic_rule_props(self) -> aws_cdk.aws_iot.CfnTopicRuleProps:
        '''User provided CfnTopicRuleProps to override the defaults.

        :default: - Default props are used
        '''
        result = self._values.get("iot_topic_rule_props")
        assert result is not None, "Required property 'iot_topic_rule_props' is missing"
        return typing.cast(aws_cdk.aws_iot.CfnTopicRuleProps, result)

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def existing_stream_obj(self) -> typing.Optional[aws_cdk.aws_kinesis.Stream]:
        '''Existing instance of Kinesis Stream object, providing both this and KinesisStreamProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_stream_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesis.Stream], result)

    @builtins.property
    def kinesis_stream_props(self) -> typing.Any:
        '''User provided props to override the default props for the Kinesis Stream.

        :default: - Default props are used
        '''
        result = self._values.get("kinesis_stream_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotToKinesisStreamsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IotToKinesisStreams",
    "IotToKinesisStreamsProps",
]

publication.publish()
