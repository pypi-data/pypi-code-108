'''
[![NPM version](https://badge.fury.io/js/cdk-demo-construct.svg)](https://badge.fury.io/js/cdk-demo-construct)
[![PyPI version](https://badge.fury.io/py/cdk-demo-construct.svg)](https://badge.fury.io/py/cdk-demo-construct)
![Release](https://github.com/neilkuan/cdk-demo-construct/workflows/release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk-demo-construct?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-demo-construct?label=pypi&color=blue)

# Welcome to `cdk-demo-construct`

The Constructs for the CDK Demo.

## To Use

```python
import * as ec2 from '@aws-cdk/aws-ec2';
import * as cdk from '@aws-cdk/core';
import { AlarmInstance } from 'cdk-demo-construct';
const app = new cdk.App();
const stack = new cdk.Stack(app, 'integ-default');
const vpc = new ec2.Vpc(stack, 'VPC');
new AlarmInstance(stack, 'AlarmInstance', { vpc, notifyMail: ['mail@example.com'] });
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

import aws_cdk.aws_ec2
import aws_cdk.aws_sns
import aws_cdk.core


class AlarmInstance(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-demo-construct.AlarmInstance",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        notify_mail: typing.Optional[typing.Sequence[builtins.str]] = None,
        topic: typing.Optional[aws_cdk.aws_sns.Topic] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: 
        :param notify_mail: 
        :param topic: 
        :param user_data: 
        '''
        props = AlarmInstanceProps(
            vpc=vpc, notify_mail=notify_mail, topic=topic, user_data=user_data
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instance")
    def instance(self) -> aws_cdk.aws_ec2.Instance:
        return typing.cast(aws_cdk.aws_ec2.Instance, jsii.get(self, "instance"))

    @instance.setter
    def instance(self, value: aws_cdk.aws_ec2.Instance) -> None:
        jsii.set(self, "instance", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.Topic:
        return typing.cast(aws_cdk.aws_sns.Topic, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: aws_cdk.aws_sns.Topic) -> None:
        jsii.set(self, "topic", value)


@jsii.data_type(
    jsii_type="cdk-demo-construct.AlarmInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "notify_mail": "notifyMail",
        "topic": "topic",
        "user_data": "userData",
    },
)
class AlarmInstanceProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        notify_mail: typing.Optional[typing.Sequence[builtins.str]] = None,
        topic: typing.Optional[aws_cdk.aws_sns.Topic] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param vpc: 
        :param notify_mail: 
        :param topic: 
        :param user_data: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if notify_mail is not None:
            self._values["notify_mail"] = notify_mail
        if topic is not None:
            self._values["topic"] = topic
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def notify_mail(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("notify_mail")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def topic(self) -> typing.Optional[aws_cdk.aws_sns.Topic]:
        result = self._values.get("topic")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.Topic], result)

    @builtins.property
    def user_data(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlarmInstance",
    "AlarmInstanceProps",
]

publication.publish()
