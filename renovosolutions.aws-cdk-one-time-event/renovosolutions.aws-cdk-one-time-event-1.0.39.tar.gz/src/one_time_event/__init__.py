'''
# cdk-library-one-time-event

[![build](https://github.com/RenovoSolutions/cdk-library-one-time-event/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-one-time-event/workflows/build.yml)

An AWS CDK Construct library to create one time event [schedules](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.Schedule.html).

## Features

* Create two types of event [schedules](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-events.Schedule.html) easily:

  * On Deployment: An one time event schedule for directly after deployment. Defaults to 10mins after.
  * At: A one time even schedule for any future `Date()`

## API Doc

See [API](API.md)

## Examples

### Typescript - run after deploy, offset 15mins

```
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as oneTimeEvents from '@renovosolutions/cdk-library-one-time-event';

export class CdkExampleLambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const handler = new lambda.Function(this, 'handler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset(functionDir + '/function.zip'),
      handler: 'index.handler',
    });

    new events.Rule(this, 'triggerImmediate', {
      schedule: new oneTimeEvents.OnDeploy(this, 'schedule', {
        offsetMinutes: 15
      }).schedule,
      targets: [new targets.LambdaFunction(this.handler)],
    });
```

### Typescript - run in 24 hours

```
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as oneTimeEvents from '@renovosolutions/cdk-library-one-time-event';

export class CdkExampleLambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const handler = new lambda.Function(this, 'handler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset(functionDir + '/function.zip'),
      handler: 'index.handler',
    });

    var tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)

    new events.Rule(this, 'triggerImmediate', {
      schedule: new oneTimeEvents.At(this, 'schedule', {
        date: tomorrow
      }).schedule,
      targets: [new targets.LambdaFunction(this.handler)],
    });
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

import aws_cdk.aws_events
import aws_cdk.core


class At(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-one-time-event.At",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        date: datetime.datetime,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param date: The future date to use for one time event.
        '''
        props = AtProps(date=date)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> aws_cdk.aws_events.Schedule:
        return typing.cast(aws_cdk.aws_events.Schedule, jsii.get(self, "schedule"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-one-time-event.AtProps",
    jsii_struct_bases=[],
    name_mapping={"date": "date"},
)
class AtProps:
    def __init__(self, *, date: datetime.datetime) -> None:
        '''
        :param date: The future date to use for one time event.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "date": date,
        }

    @builtins.property
    def date(self) -> datetime.datetime:
        '''The future date to use for one time event.'''
        result = self._values.get("date")
        assert result is not None, "Required property 'date' is missing"
        return typing.cast(datetime.datetime, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AtProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnDeploy(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-one-time-event.OnDeploy",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        offset_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param offset_minutes: The number of minutes to add to the current time when generating the expression. Should exceed the expected time for the appropriate resources to converge. Default: 10
        '''
        props = OnDeployProps(offset_minutes=offset_minutes)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> aws_cdk.aws_events.Schedule:
        return typing.cast(aws_cdk.aws_events.Schedule, jsii.get(self, "schedule"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-one-time-event.OnDeployProps",
    jsii_struct_bases=[],
    name_mapping={"offset_minutes": "offsetMinutes"},
)
class OnDeployProps:
    def __init__(self, *, offset_minutes: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param offset_minutes: The number of minutes to add to the current time when generating the expression. Should exceed the expected time for the appropriate resources to converge. Default: 10
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if offset_minutes is not None:
            self._values["offset_minutes"] = offset_minutes

    @builtins.property
    def offset_minutes(self) -> typing.Optional[jsii.Number]:
        '''The number of minutes to add to the current time when generating the expression.

        Should exceed the expected time for the appropriate resources to converge.

        :default: 10
        '''
        result = self._values.get("offset_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnDeployProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "At",
    "AtProps",
    "OnDeploy",
    "OnDeployProps",
]

publication.publish()
