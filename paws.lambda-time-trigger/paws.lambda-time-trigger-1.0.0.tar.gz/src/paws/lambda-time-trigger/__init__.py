'''
# PAWS Lambda Time Trigger

This package makes it easy to trigger Lambda functions more often than once a minute - the default service to trigger Lambdas periodically, EventBridge rules, will only allow to define schedules down to a resolution of 1 minute.

Using the PAWS Lambda Time Trigger package, you can define schedules with a resolution down to 1 second.

The PAWS Lambda Time Trigger package will, on top of any resources you create, including the Lambda function to be triggered on a schedule, create:

* An AWS Step Function running the sub-minute schedule you defined by waiting between invokes of your target Lambda
* An EventBrige rule triggering the AWS step function based on the rest of the schedule you define as a CRON expression

If you specify a CRON schedule without the `second` field being set, or with it being set to 0, the `TimeTrigger` will just create a plain EventBridge rule with that schedule triggering your Lambda directly, without the AWS Step Function in between.

## Basic usage

### TypeScript / JavaScript

```python
const timeTrigger = new TimeTrigger(this, 'time-trigger', {
  schedule: {
    cron: {
      second: '0-19/5,20-59/20', // Triggers at seconds 0, 5, 10, 15, 20 and 40 of every minute...
      hour: '9-17' // ... of every hour between 9 and 17 each day
    },
  },
});

yourLambdaFunction.addEventSource(timeTrigger);
```

## Known limitations

### Lambda execution time

As of now, the AWS Step Function does not take the time required to execute the scheduled Lambda into account. In other words: if you schedule your Lambda with a TimeTrigger to be executed every 10 seconds (`second:'*/10'`), but your scheduled Lambda takes 1 second to run, you will see the following behavior:

* The AWS Step function will be triggered every minute (unless you specified another schedule)
* The AWS Step function will run your Lambda on...

  * Second 0, taking 1 second to complete, then waiting 10 seconds
  * Second 11, taking 1 second to complete, then waiting 10 seconds
  * Second 22, taking 1 second to complete, then waiting 10 seconds
  * Second 33, taking 1 second to complete, then waiting 10 seconds
  * Second 44, taking 1 second to complete, then waiting 10 seconds
  * Second 55, taking 1 second to complete, then finishing
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
import aws_cdk.aws_lambda
import constructs


@jsii.data_type(
    jsii_type="paws-lambda-time-trigger.CronOptionsWithSeconds",
    jsii_struct_bases=[aws_cdk.aws_events.CronOptions],
    name_mapping={
        "day": "day",
        "hour": "hour",
        "minute": "minute",
        "month": "month",
        "week_day": "weekDay",
        "year": "year",
        "second": "second",
    },
)
class CronOptionsWithSeconds(aws_cdk.aws_events.CronOptions):
    def __init__(
        self,
        *,
        day: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        week_day: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
        second: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Defines a cron expression.

        :param day: The day of the month to run this rule at. Default: - Every day of the month
        :param hour: The hour to run this rule at. Default: - Every hour
        :param minute: The minute to run this rule at. Default: - Every minute
        :param month: The month to run this rule at. Default: - Every month
        :param week_day: The day of the week to run this rule at. Default: - Any day of the week
        :param year: The year to run this rule at. Default: - Every year
        :param second: The second to run the Lambda at. Default: - At the first second of every minute
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if day is not None:
            self._values["day"] = day
        if hour is not None:
            self._values["hour"] = hour
        if minute is not None:
            self._values["minute"] = minute
        if month is not None:
            self._values["month"] = month
        if week_day is not None:
            self._values["week_day"] = week_day
        if year is not None:
            self._values["year"] = year
        if second is not None:
            self._values["second"] = second

    @builtins.property
    def day(self) -> typing.Optional[builtins.str]:
        '''The day of the month to run this rule at.

        :default: - Every day of the month
        '''
        result = self._values.get("day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hour(self) -> typing.Optional[builtins.str]:
        '''The hour to run this rule at.

        :default: - Every hour
        '''
        result = self._values.get("hour")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minute(self) -> typing.Optional[builtins.str]:
        '''The minute to run this rule at.

        :default: - Every minute
        '''
        result = self._values.get("minute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def month(self) -> typing.Optional[builtins.str]:
        '''The month to run this rule at.

        :default: - Every month
        '''
        result = self._values.get("month")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def week_day(self) -> typing.Optional[builtins.str]:
        '''The day of the week to run this rule at.

        :default: - Any day of the week
        '''
        result = self._values.get("week_day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def year(self) -> typing.Optional[builtins.str]:
        '''The year to run this rule at.

        :default: - Every year
        '''
        result = self._values.get("year")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def second(self) -> typing.Optional[builtins.str]:
        '''The second to run the Lambda at.

        :default: - At the first second of every minute
        '''
        result = self._values.get("second")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CronOptionsWithSeconds(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_lambda.IEventSource)
class TimeTrigger(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="paws-lambda-time-trigger.TimeTrigger",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        schedule: "TimeTriggerSchedule",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param schedule: Defines the schedule for a time trigger.
        '''
        props = TimeTriggerProps(schedule=schedule)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="bind")
    def bind(self, target: aws_cdk.aws_lambda.IFunction) -> None:
        '''Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        :param target: -
        '''
        return typing.cast(None, jsii.invoke(self, "bind", [target]))


@jsii.data_type(
    jsii_type="paws-lambda-time-trigger.TimeTriggerProps",
    jsii_struct_bases=[],
    name_mapping={"schedule": "schedule"},
)
class TimeTriggerProps:
    def __init__(self, *, schedule: "TimeTriggerSchedule") -> None:
        '''
        :param schedule: Defines the schedule for a time trigger.
        '''
        if isinstance(schedule, dict):
            schedule = TimeTriggerSchedule(**schedule)
        self._values: typing.Dict[str, typing.Any] = {
            "schedule": schedule,
        }

    @builtins.property
    def schedule(self) -> "TimeTriggerSchedule":
        '''Defines the schedule for a time trigger.'''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast("TimeTriggerSchedule", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimeTriggerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="paws-lambda-time-trigger.TimeTriggerSchedule",
    jsii_struct_bases=[],
    name_mapping={"cron": "cron"},
)
class TimeTriggerSchedule:
    def __init__(self, *, cron: CronOptionsWithSeconds) -> None:
        '''Defines the schedule for a time trigger.

        :param cron: Set this to define the schedule using a cron expression. As of now, this is the only supported option
        '''
        if isinstance(cron, dict):
            cron = CronOptionsWithSeconds(**cron)
        self._values: typing.Dict[str, typing.Any] = {
            "cron": cron,
        }

    @builtins.property
    def cron(self) -> CronOptionsWithSeconds:
        '''Set this to define the schedule using a cron expression.

        As of now, this is the only supported option
        '''
        result = self._values.get("cron")
        assert result is not None, "Required property 'cron' is missing"
        return typing.cast(CronOptionsWithSeconds, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimeTriggerSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CronOptionsWithSeconds",
    "TimeTrigger",
    "TimeTriggerProps",
    "TimeTriggerSchedule",
]

publication.publish()
