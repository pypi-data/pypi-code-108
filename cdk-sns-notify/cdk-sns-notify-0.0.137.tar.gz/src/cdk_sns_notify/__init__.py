'''
[![NPM version](https://badge.fury.io/js/cdk-sns-notify.svg)](https://badge.fury.io/js/cdk-sns-notify)
[![PyPI version](https://badge.fury.io/py/cdk-sns-notify.svg)](https://badge.fury.io/py/cdk-sns-notify)
![Release](https://github.com/clarencetw/cdk-sns-notify/workflows/Release/badge.svg)

# cdk-sns-notify

A CDK construct library to send line notify or discord webhook

# Sample

```python
import * as sns from "@aws-cdk/aws-sns";
import * as cloudwatch from "@aws-cdk/aws-cloudwatch";
import * as cw_actions from "@aws-cdk/aws-cloudwatch-actions";

import { SnsNotify } from "cdk-sns-notify";

const topic = new sns.Topic(stack, "Topic");

const metric = new cloudwatch.Metric({
  namespace: "AWS/EC2",
  metricName: "CPUUtilization",
  dimensions: {
    InstanceId: instance.instanceId,
  },
  period: cdk.Duration.minutes(1),
});

const alarm = new cloudwatch.Alarm(stack, "Alarm", {
  metric,
  threshold: 5,
  evaluationPeriods: 1,
});

alarm.addAlarmAction(new cw_actions.SnsAction(topic));

const snsLineNotify = new SnsNotify(stack, "sns-line-notify", {
  lineNotifyToken: "lineNotifyToken",
});

topic.addSubscription(snsLineNotify.lambdaSubscription);
```

# Deploy

```sh
cdk deploy
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

import aws_cdk.aws_sns_subscriptions
import aws_cdk.core


class SnsNotify(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-sns-notify.SnsNotify",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        line_notify_token: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param line_notify_token: 
        '''
        props = SnsNotifyProps(line_notify_token=line_notify_token)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaSubscription")
    def lambda_subscription(self) -> aws_cdk.aws_sns_subscriptions.LambdaSubscription:
        return typing.cast(aws_cdk.aws_sns_subscriptions.LambdaSubscription, jsii.get(self, "lambdaSubscription"))


@jsii.data_type(
    jsii_type="cdk-sns-notify.SnsNotifyProps",
    jsii_struct_bases=[],
    name_mapping={"line_notify_token": "lineNotifyToken"},
)
class SnsNotifyProps:
    def __init__(self, *, line_notify_token: builtins.str) -> None:
        '''
        :param line_notify_token: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "line_notify_token": line_notify_token,
        }

    @builtins.property
    def line_notify_token(self) -> builtins.str:
        result = self._values.get("line_notify_token")
        assert result is not None, "Required property 'line_notify_token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnsNotifyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SnsNotify",
    "SnsNotifyProps",
]

publication.publish()
