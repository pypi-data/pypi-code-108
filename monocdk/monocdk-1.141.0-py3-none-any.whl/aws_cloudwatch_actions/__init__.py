'''
# CloudWatch Alarm Actions library

This library contains a set of classes which can be used as CloudWatch Alarm actions.

The currently implemented actions are: EC2 Actions, SNS Actions, Autoscaling Actions and Aplication Autoscaling Actions

## EC2 Action Example

```python
# Example automatically generated from non-compiling source. May contain errors.
import monocdk as cw

# Alarm must be configured with an EC2 per-instance metric
# alarm: cw.Alarm
# Attach a reboot when alarm triggers
alarm.add_alarm_action(
    Ec2Action(Ec2InstanceActions.REBOOT))
```

See `@aws-cdk/aws-cloudwatch` for more information.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import Construct as _Construct_e78e779f
from ..aws_applicationautoscaling import (
    StepScalingAction as _StepScalingAction_20c2d829
)
from ..aws_autoscaling import StepScalingAction as _StepScalingAction_569c9499
from ..aws_cloudwatch import (
    AlarmActionConfig as _AlarmActionConfig_aebdae35,
    IAlarm as _IAlarm_bf66c8d0,
    IAlarmAction as _IAlarmAction_22055cd4,
)
from ..aws_sns import ITopic as _ITopic_465e36b9


@jsii.implements(_IAlarmAction_22055cd4)
class ApplicationScalingAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudwatch_actions.ApplicationScalingAction",
):
    '''(experimental) Use an ApplicationAutoScaling StepScalingAction as an Alarm Action.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_applicationautoscaling as applicationautoscaling
        from monocdk import aws_cloudwatch_actions as cloudwatch_actions
        
        # step_scaling_action: applicationautoscaling.StepScalingAction
        
        application_scaling_action = cloudwatch_actions.ApplicationScalingAction(step_scaling_action)
    '''

    def __init__(self, step_scaling_action: _StepScalingAction_20c2d829) -> None:
        '''
        :param step_scaling_action: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        _alarm: _IAlarm_bf66c8d0,
    ) -> _AlarmActionConfig_aebdae35:
        '''(experimental) Returns an alarm action configuration to use an ApplicationScaling StepScalingAction as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_aebdae35, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(_IAlarmAction_22055cd4)
class AutoScalingAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudwatch_actions.AutoScalingAction",
):
    '''(experimental) Use an AutoScaling StepScalingAction as an Alarm Action.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_autoscaling as autoscaling
        from monocdk import aws_cloudwatch_actions as cloudwatch_actions
        
        # step_scaling_action: autoscaling.StepScalingAction
        
        auto_scaling_action = cloudwatch_actions.AutoScalingAction(step_scaling_action)
    '''

    def __init__(self, step_scaling_action: _StepScalingAction_569c9499) -> None:
        '''
        :param step_scaling_action: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        _alarm: _IAlarm_bf66c8d0,
    ) -> _AlarmActionConfig_aebdae35:
        '''(experimental) Returns an alarm action configuration to use an AutoScaling StepScalingAction as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_aebdae35, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(_IAlarmAction_22055cd4)
class Ec2Action(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudwatch_actions.Ec2Action",
):
    '''(experimental) Use an EC2 action as an Alarm action.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_cloudwatch_actions as cloudwatch_actions
        
        ec2_action = cloudwatch_actions.Ec2Action(cloudwatch_actions.Ec2InstanceAction.STOP)
    '''

    def __init__(self, instance_action: "Ec2InstanceAction") -> None:
        '''
        :param instance_action: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [instance_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        _alarm: _IAlarm_bf66c8d0,
    ) -> _AlarmActionConfig_aebdae35:
        '''(experimental) Returns an alarm action configuration to use an EC2 action as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_aebdae35, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.enum(jsii_type="monocdk.aws_cloudwatch_actions.Ec2InstanceAction")
class Ec2InstanceAction(enum.Enum):
    '''(experimental) Types of EC2 actions available.

    :stability: experimental
    '''

    STOP = "STOP"
    '''(experimental) Stop the instance.

    :stability: experimental
    '''
    TERMINATE = "TERMINATE"
    '''(experimental) Terminatethe instance.

    :stability: experimental
    '''
    RECOVER = "RECOVER"
    '''(experimental) Recover the instance.

    :stability: experimental
    '''
    REBOOT = "REBOOT"
    '''(experimental) Reboot the instance.

    :stability: experimental
    '''


@jsii.implements(_IAlarmAction_22055cd4)
class SnsAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudwatch_actions.SnsAction",
):
    '''(experimental) Use an SNS topic as an alarm action.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as cw_actions
        # alarm: cloudwatch.Alarm
        
        
        topic = sns.Topic(self, "Topic")
        alarm.add_alarm_action(cw_actions.SnsAction(topic))
    '''

    def __init__(self, topic: _ITopic_465e36b9) -> None:
        '''
        :param topic: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _Construct_e78e779f,
        _alarm: _IAlarm_bf66c8d0,
    ) -> _AlarmActionConfig_aebdae35:
        '''(experimental) Returns an alarm action configuration to use an SNS topic as an alarm action.

        :param _scope: -
        :param _alarm: -

        :stability: experimental
        '''
        return typing.cast(_AlarmActionConfig_aebdae35, jsii.invoke(self, "bind", [_scope, _alarm]))


__all__ = [
    "ApplicationScalingAction",
    "AutoScalingAction",
    "Ec2Action",
    "Ec2InstanceAction",
    "SnsAction",
]

publication.publish()
