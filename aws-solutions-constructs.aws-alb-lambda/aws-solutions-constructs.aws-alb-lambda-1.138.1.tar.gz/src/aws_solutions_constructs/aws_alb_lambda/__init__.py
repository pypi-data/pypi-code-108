'''
# aws-alb-lambda module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_alb_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-alb-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.alblambda`|

This AWS Solutions Construct implements an an Application Load Balancer to an AWS Lambda function

Here is a minimal deployable pattern definition in Typescript:

```python

  // Obtain a pre-existing certificate from your account
  const certificate = acm.Certificate.fromCertificateArn(
        scope,
        'existing-cert',
        "arn:aws:acm:us-east-1:123456789012:certificate/11112222-3333-1234-1234-123456789012"
      );
  const props: AlbToLambdaProps = {
    lambdaFunctionProps: {
      code: lambda.Code.fromAsset(`${__dirname}/lambda`),
      runtime: lambda.Runtime.NODEJS_14_X,
      handler: 'index.handler'
    },
    listenerProps: {
      certificates: [ certificate ]
    },
    publicApi: true
  };
  new AlbToLambda(stack, 'new-construct', props);
```

## Initializer

```text
new AlbToLambda(scope: Construct, id: string, props: AlbToLambdaProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`AlbToLambdaProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| loadBalancerProps? | [elasticloadbalancingv2.ApplicationLoadBalancerProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancerProps.html) | Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. |
| existingLoadBalancerObj? | [elasticloadbalancingv2.ApplicationLoadBalancer](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html) | Existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc. |
| listenerProps? | [ApplicationListenerProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationListenerProps.html) | Props to define the listener. Must be provided when adding the listener to an ALB (eg - when creating the alb), may not be provided when adding a second target to an already established listener. When provided, must include either a certificate or protocol: HTTP |
| targetProps? | [ApplicationTargetGroupProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationTargetGroupProps.html) | Optional custom properties for a new target group. While this is a standard attribute of props for ALB constructs, there are few pertinent properties for a Lambda target. |
| ruleProps? | [AddRuleProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.AddRuleProps.html) | Rules for directing traffic to the target being created. May not be specified for the first listener added to an ALB, and must be specified for the second target added to a listener. Add a second target by instantiating this construct a second time and providing the existingAlb from the first instantiation. |
| vpcProps? | [ec2.VpcProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html) | Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. |
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|Optional user provided props to override the default props for the Lambda function.|
| existingVpc? | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. |
| logAlbAccessLogs? | boolean| Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs.Enabling Access Logging is a best practice. default - true |
| albLoggingBucketProps? | [s3.BucketProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html) | Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. @default - none |
| publicApi | boolean | Whether the construct is deploying a private or public API. This has implications for the VPC and ALB. |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| vpc | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | The VPC used by the construct (whether created by the construct or providedb by the client) |
| loadBalancer | [elasticloadbalancingv2.ApplicationLoadBalancer](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html) | The Load Balancer used by the construct (whether created by the construct or provided by the client) |
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of the Lambda function used in the pattern.|
| listener | [`elb.ApplicationListener`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationListener.html) | The listener used by this pattern. |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Application Load Balancer

* Creates or configures an Application Load Balancer with:

  * Required listeners
  * New target group with routing rules if appropriate

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

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

import aws_cdk.aws_ec2
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.core


class AlbToLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-alb-lambda.AlbToLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        public_api: builtins.bool,
        alb_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_load_balancer_obj: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        listener_props: typing.Any = None,
        load_balancer_props: typing.Any = None,
        log_alb_access_logs: typing.Optional[builtins.bool] = None,
        rule_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps] = None,
        target_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC and ALB. Default: - none
        :param alb_logging_bucket_props: Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. Default: - none
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_load_balancer_obj: Existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc. Default: - none
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. Default: - none
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param listener_props: Props to define the listener. Must be provided when adding the listener to an ALB (eg - when creating the alb), may not be provided when adding a second target to an already established listener. When provided, must include either a certificate or protocol: HTTP Default: - none
        :param load_balancer_props: Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Default: - none
        :param log_alb_access_logs: Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param rule_props: Rules for directing traffic to the target being created. May not be specified for the first listener added to an ALB, and must be specified for the second target added to a listener. Add a second target by instantiating this construct a second time and providing the existingAlb from the first instantiation. Default: - none
        :param target_props: Optional custom properties for a new target group. While this is a standard attribute of props for ALB constructs, there are few pertinent properties for a Lambda target. Default: - none
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. Default: - none
        '''
        props = AlbToLambdaProps(
            public_api=public_api,
            alb_logging_bucket_props=alb_logging_bucket_props,
            existing_lambda_obj=existing_lambda_obj,
            existing_load_balancer_obj=existing_load_balancer_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            listener_props=listener_props,
            load_balancer_props=load_balancer_props,
            log_alb_access_logs=log_alb_access_logs,
            rule_props=rule_props,
            target_props=target_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="listener")
    def listener(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationListener:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationListener, jsii.get(self, "listener"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-alb-lambda.AlbToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_api": "publicApi",
        "alb_logging_bucket_props": "albLoggingBucketProps",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_load_balancer_obj": "existingLoadBalancerObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "listener_props": "listenerProps",
        "load_balancer_props": "loadBalancerProps",
        "log_alb_access_logs": "logAlbAccessLogs",
        "rule_props": "ruleProps",
        "target_props": "targetProps",
        "vpc_props": "vpcProps",
    },
)
class AlbToLambdaProps:
    def __init__(
        self,
        *,
        public_api: builtins.bool,
        alb_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_load_balancer_obj: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        listener_props: typing.Any = None,
        load_balancer_props: typing.Any = None,
        log_alb_access_logs: typing.Optional[builtins.bool] = None,
        rule_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps] = None,
        target_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC and ALB. Default: - none
        :param alb_logging_bucket_props: Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. Default: - none
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_load_balancer_obj: Existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc. Default: - none
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. Default: - none
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param listener_props: Props to define the listener. Must be provided when adding the listener to an ALB (eg - when creating the alb), may not be provided when adding a second target to an already established listener. When provided, must include either a certificate or protocol: HTTP Default: - none
        :param load_balancer_props: Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Default: - none
        :param log_alb_access_logs: Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param rule_props: Rules for directing traffic to the target being created. May not be specified for the first listener added to an ALB, and must be specified for the second target added to a listener. Add a second target by instantiating this construct a second time and providing the existingAlb from the first instantiation. Default: - none
        :param target_props: Optional custom properties for a new target group. While this is a standard attribute of props for ALB constructs, there are few pertinent properties for a Lambda target. Default: - none
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. Default: - none
        '''
        if isinstance(alb_logging_bucket_props, dict):
            alb_logging_bucket_props = aws_cdk.aws_s3.BucketProps(**alb_logging_bucket_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(rule_props, dict):
            rule_props = aws_cdk.aws_elasticloadbalancingv2.AddRuleProps(**rule_props)
        if isinstance(target_props, dict):
            target_props = aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps(**target_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {
            "public_api": public_api,
        }
        if alb_logging_bucket_props is not None:
            self._values["alb_logging_bucket_props"] = alb_logging_bucket_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_load_balancer_obj is not None:
            self._values["existing_load_balancer_obj"] = existing_load_balancer_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if listener_props is not None:
            self._values["listener_props"] = listener_props
        if load_balancer_props is not None:
            self._values["load_balancer_props"] = load_balancer_props
        if log_alb_access_logs is not None:
            self._values["log_alb_access_logs"] = log_alb_access_logs
        if rule_props is not None:
            self._values["rule_props"] = rule_props
        if target_props is not None:
            self._values["target_props"] = target_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def public_api(self) -> builtins.bool:
        '''Whether the construct is deploying a private or public API.

        This has implications for the VPC and ALB.

        :default: - none
        '''
        result = self._values.get("public_api")
        assert result is not None, "Required property 'public_api' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def alb_logging_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional properties to customize the bucket used to store the ALB Access Logs.

        Supplying this and setting logAccessLogs to false is an error.

        :default: - none
        '''
        result = self._values.get("alb_logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_load_balancer_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        '''Existing Application Load Balancer to incorporate into the construct architecture.

        Providing both this and loadBalancerProps is an
        error. The VPC containing this loadBalancer must match the VPC provided in existingVpc.

        :default: - none
        '''
        result = self._values.get("existing_load_balancer_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC in which to deploy the construct.

        Providing both this and
        vpcProps is an error. If the client provides an existing load balancer and/or
        existing Private Hosted Zone, those constructs must exist in this VPC.

        :default: - none
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

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
    def listener_props(self) -> typing.Any:
        '''Props to define the listener.

        Must be provided when adding the listener
        to an ALB (eg - when creating the alb), may not be provided when adding
        a second target to an already established listener. When provided, must include
        either a certificate or protocol: HTTP

        :default: - none
        '''
        result = self._values.get("listener_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def load_balancer_props(self) -> typing.Any:
        '''Optional custom properties for a new loadBalancer.

        Providing both this and
        existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC
        in existingVpc or the VPC created by the construct.

        :default: - none
        '''
        result = self._values.get("load_balancer_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def log_alb_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for the Application Load Balancer.

        Uses an S3 bucket
        with associated storage costs. Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_alb_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rule_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps]:
        '''Rules for directing traffic to the target being created.

        May not be specified
        for the first listener added to an ALB, and must be specified for the second
        target added to a listener. Add a second target by instantiating this construct a
        second time and providing the existingAlb from the first instantiation.

        :default: - none
        '''
        result = self._values.get("rule_props")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps], result)

    @builtins.property
    def target_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps]:
        '''Optional custom properties for a new target group.

        While this is a standard
        attribute of props for ALB constructs, there are few pertinent properties for a Lambda target.

        :default: - none
        '''
        result = self._values.get("target_props")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Optional custom properties for a VPC the construct will create.

        This VPC will
        be used by the new ALB and any Private Hosted Zone the construct creates (that's
        why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing
        both this and existingVpc is an error.

        :default: - none
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlbToLambda",
    "AlbToLambdaProps",
]

publication.publish()
