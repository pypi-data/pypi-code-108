'''
# Lifecycle Hook for the CDK AWS AutoScaling Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains integration classes for AutoScaling lifecycle hooks.
Instances of these classes should be passed to the
`autoScalingGroup.addLifecycleHook()` method.

Lifecycle hooks can be activated in one of the following ways:

* Invoke a Lambda function
* Publish to an SNS topic
* Send to an SQS queue

For more information on using this library, see the README of the
`@aws-cdk/aws-autoscaling` library.

For more information about lifecycle hooks, see
[Amazon EC2 AutoScaling Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html) in the Amazon EC2 User Guide.
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

import aws_cdk.aws_autoscaling
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import constructs


@jsii.implements(aws_cdk.aws_autoscaling.ILifecycleHookTarget)
class FunctionHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-autoscaling-hooktargets.FunctionHook",
):
    '''Use a Lambda Function as a hook target.

    Internally creates a Topic to make the connection.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling_hooktargets as autoscaling_hooktargets
        import aws_cdk.aws_kms as kms
        import aws_cdk.aws_lambda as lambda_
        
        # function_: lambda.Function
        # key: kms.Key
        
        function_hook = autoscaling_hooktargets.FunctionHook(function_, key)
    '''

    def __init__(
        self,
        fn: aws_cdk.aws_lambda.IFunction,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
    ) -> None:
        '''
        :param fn: Function to invoke in response to a lifecycle event.
        :param encryption_key: If provided, this key is used to encrypt the contents of the SNS topic.
        '''
        jsii.create(self.__class__, self, [fn, encryption_key])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        *,
        lifecycle_hook: aws_cdk.aws_autoscaling.LifecycleHook,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> aws_cdk.aws_autoscaling.LifecycleHookTargetConfig:
        '''If the ``IRole`` does not exist in ``options``, will create an ``IRole`` and an SNS Topic and attach both to the lifecycle hook.

        If the ``IRole`` does exist in ``options``, will only create an SNS Topic and attach it to the lifecycle hook.

        :param _scope: -
        :param lifecycle_hook: The lifecycle hook to attach to. [disable-awslint:ref-via-interface]
        :param role: The role to use when attaching to the lifecycle hook. [disable-awslint:ref-via-interface] Default: : a role is not created unless the target arn is specified
        '''
        options = aws_cdk.aws_autoscaling.BindHookTargetOptions(
            lifecycle_hook=lifecycle_hook, role=role
        )

        return typing.cast(aws_cdk.aws_autoscaling.LifecycleHookTargetConfig, jsii.invoke(self, "bind", [_scope, options]))


@jsii.implements(aws_cdk.aws_autoscaling.ILifecycleHookTarget)
class QueueHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-autoscaling-hooktargets.QueueHook",
):
    '''Use an SQS queue as a hook target.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling_hooktargets as autoscaling_hooktargets
        import aws_cdk.aws_sqs as sqs
        
        # queue: sqs.Queue
        
        queue_hook = autoscaling_hooktargets.QueueHook(queue)
    '''

    def __init__(self, queue: aws_cdk.aws_sqs.IQueue) -> None:
        '''
        :param queue: -
        '''
        jsii.create(self.__class__, self, [queue])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        *,
        lifecycle_hook: aws_cdk.aws_autoscaling.LifecycleHook,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> aws_cdk.aws_autoscaling.LifecycleHookTargetConfig:
        '''If an ``IRole`` is found in ``options``, grant it access to send messages.

        Otherwise, create a new ``IRole`` and grant it access to send messages.

        :param _scope: -
        :param lifecycle_hook: The lifecycle hook to attach to. [disable-awslint:ref-via-interface]
        :param role: The role to use when attaching to the lifecycle hook. [disable-awslint:ref-via-interface] Default: : a role is not created unless the target arn is specified

        :return: the ``IRole`` with access to send messages and the ARN of the queue it has access to send messages to.
        '''
        options = aws_cdk.aws_autoscaling.BindHookTargetOptions(
            lifecycle_hook=lifecycle_hook, role=role
        )

        return typing.cast(aws_cdk.aws_autoscaling.LifecycleHookTargetConfig, jsii.invoke(self, "bind", [_scope, options]))


@jsii.implements(aws_cdk.aws_autoscaling.ILifecycleHookTarget)
class TopicHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-autoscaling-hooktargets.TopicHook",
):
    '''Use an SNS topic as a hook target.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling_hooktargets as autoscaling_hooktargets
        import aws_cdk.aws_sns as sns
        
        # topic: sns.Topic
        
        topic_hook = autoscaling_hooktargets.TopicHook(topic)
    '''

    def __init__(self, topic: aws_cdk.aws_sns.ITopic) -> None:
        '''
        :param topic: -
        '''
        jsii.create(self.__class__, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        *,
        lifecycle_hook: aws_cdk.aws_autoscaling.LifecycleHook,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> aws_cdk.aws_autoscaling.LifecycleHookTargetConfig:
        '''If an ``IRole`` is found in ``options``, grant it topic publishing permissions.

        Otherwise, create a new ``IRole`` and grant it topic publishing permissions.

        :param _scope: -
        :param lifecycle_hook: The lifecycle hook to attach to. [disable-awslint:ref-via-interface]
        :param role: The role to use when attaching to the lifecycle hook. [disable-awslint:ref-via-interface] Default: : a role is not created unless the target arn is specified

        :return: the ``IRole`` with topic publishing permissions and the ARN of the topic it has publishing permission to.
        '''
        options = aws_cdk.aws_autoscaling.BindHookTargetOptions(
            lifecycle_hook=lifecycle_hook, role=role
        )

        return typing.cast(aws_cdk.aws_autoscaling.LifecycleHookTargetConfig, jsii.invoke(self, "bind", [_scope, options]))


__all__ = [
    "FunctionHook",
    "QueueHook",
    "TopicHook",
]

publication.publish()
