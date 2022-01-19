'''
# aws-route53-alb module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_route53_alb`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-route53-alb`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.route53alb`|

This AWS Solutions Construct implements an Amazon Route53 Hosted Zone routing to an Application Load Balancer

Here is a minimal deployable pattern definition in Typescript:

```python
import { Route53ToAlb } from '@aws-solutions-constructs/aws-route53-alb';

new Route53ToAlb(this, 'Route53ToAlbPattern', {
  privateHostedZoneProps: {
    zoneName: 'www.example.com',
  }
  publicApi: false,
});
```

## Initializer

```text
new Route53ToAlb(scope: Construct, id: string, props: Route53ToAlbProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`Route53ToAlbProps`](#pattern-construct-props)

## Pattern Construct Props

This construct cannot create a new Public Hosted Zone, if you are creating a public API you must supply an existing Public Hosted Zone that will be reconfigured with a new Alias record. Public Hosted Zones are configured with public domain names and are not well suited to be launched and torn down dynamically, so this construct will only reconfigure existing Public Hosted Zones.

This construct can create Private Hosted Zones. If you want a Private Hosted Zone, then you can either provide an existing Private Hosted Zone or a privateHostedZoneProps value with at least the Domain Name defined.

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| privateHostedZoneProps? | [route53.PrivateHostedZoneProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.PrivateHostedZoneProps.html) | Optional custom properties for a new Private Hosted Zone. Cannot be specified for a public API. Cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Providing both this and existingHostedZoneInterfaceis an error. |
| existingHostedZoneInterface? | [route53.IHostedZone](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.IHostedZone.html) | Existing Public or Private Hosted Zone (type must match publicApi setting). Specifying both this and privateHostedZoneProps is an error. If this is a Private Hosted Zone, the associated VPC must be provided as the existingVpc property |
| loadBalancerProps? | [elasticloadbalancingv2.ApplicationLoadBalancerProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancerProps.html) | Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. |
| existingLoadBalancerObj? | [elasticloadbalancingv2.ApplicationLoadBalancer](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html) | Existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc. |
| vpcProps? | [ec2.VpcProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html) | Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. |
| existingVpc? | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. |
| logAlbAccessLogs? | boolean| Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs.Enabling Access Logging is a best practice. default - true |
| albLoggingBucketProps? | [s3.BucketProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html) | Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. @default - none |

| publicApi | boolean | Whether the construct is deploying a private or public API. This has implications for the Hosted Zone, VPC and ALB. |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| hostedZone | [route53.IHostedZone](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.IHostedZone.html) | The hosted zone used by the construct (whether created by the construct or providedb by the client) |
| vpc | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | The VPC used by the construct (whether created by the construct or providedb by the client) |
| loadBalancer | [elasticloadbalancingv2.ApplicationLoadBalancer](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html) | The Load Balancer used by the construct (whether created by the construct or providedb by the client) |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Route53

* Adds an ALIAS record to the new or provided Hosted Zone that routes to the construct's ALB

### Application Load Balancer

* Creates an Application Load Balancer with no Listener or target. The consruct can incorporate an existing, fully configured ALB if provided.

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
import aws_cdk.aws_route53
import aws_cdk.aws_s3
import aws_cdk.core


class Route53ToAlb(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-route53-alb.Route53ToAlb",
):
    '''
    :summary: Configures a Route53 Hosted Zone to route to an Application Load Balancer
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        public_api: builtins.bool,
        alb_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_hosted_zone_interface: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        existing_load_balancer_obj: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        load_balancer_props: typing.Any = None,
        log_alb_access_logs: typing.Optional[builtins.bool] = None,
        private_hosted_zone_props: typing.Any = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param public_api: Whether to create a public or private API. This value has implications for the VPC, the type of Hosted Zone and the Application Load Balancer Default: - None
        :param alb_logging_bucket_props: Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. Default: - none
        :param existing_hosted_zone_interface: Existing Public or Private Hosted Zone. If a Private Hosted Zone, must exist in the same VPC specified in existingVpc Default: - None
        :param existing_load_balancer_obj: An existing Application Load Balancer. Providing both this and loadBalancerProps is an error. This ALB must exist in the same VPC specified in existingVPC Default: - None
        :param existing_vpc: An existing VPC. Providing both this and vpcProps is an error. If an existingAlb or existing Private Hosted Zone is provided, this value must be the VPC associated with those resources. Default: - None
        :param load_balancer_props: Custom properties for a new ALB. Providing both this and existingLoadBalancerObj is an error. These properties cannot include a VPC. Default: - None
        :param log_alb_access_logs: Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param private_hosted_zone_props: Custom properties for a new Private Hosted Zone. Cannot be specified for a public API. Cannot specify a VPC Default: - None
        :param vpc_props: Custom properties for a new VPC. Providing both this and existingVpc is an error. If an existingAlb or existing Private Hosted Zone is provided, those already exist in a VPC so this value cannot be provided. Default: - None

        :access: public
        :summary: Constructs a new instance of the Route53ToAlb class.
        '''
        props = Route53ToAlbProps(
            public_api=public_api,
            alb_logging_bucket_props=alb_logging_bucket_props,
            existing_hosted_zone_interface=existing_hosted_zone_interface,
            existing_load_balancer_obj=existing_load_balancer_obj,
            existing_vpc=existing_vpc,
            load_balancer_props=load_balancer_props,
            log_alb_access_logs=log_alb_access_logs,
            private_hosted_zone_props=private_hosted_zone_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.get(self, "hostedZone"))

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
    jsii_type="@aws-solutions-constructs/aws-route53-alb.Route53ToAlbProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_api": "publicApi",
        "alb_logging_bucket_props": "albLoggingBucketProps",
        "existing_hosted_zone_interface": "existingHostedZoneInterface",
        "existing_load_balancer_obj": "existingLoadBalancerObj",
        "existing_vpc": "existingVpc",
        "load_balancer_props": "loadBalancerProps",
        "log_alb_access_logs": "logAlbAccessLogs",
        "private_hosted_zone_props": "privateHostedZoneProps",
        "vpc_props": "vpcProps",
    },
)
class Route53ToAlbProps:
    def __init__(
        self,
        *,
        public_api: builtins.bool,
        alb_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_hosted_zone_interface: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        existing_load_balancer_obj: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        load_balancer_props: typing.Any = None,
        log_alb_access_logs: typing.Optional[builtins.bool] = None,
        private_hosted_zone_props: typing.Any = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param public_api: Whether to create a public or private API. This value has implications for the VPC, the type of Hosted Zone and the Application Load Balancer Default: - None
        :param alb_logging_bucket_props: Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. Default: - none
        :param existing_hosted_zone_interface: Existing Public or Private Hosted Zone. If a Private Hosted Zone, must exist in the same VPC specified in existingVpc Default: - None
        :param existing_load_balancer_obj: An existing Application Load Balancer. Providing both this and loadBalancerProps is an error. This ALB must exist in the same VPC specified in existingVPC Default: - None
        :param existing_vpc: An existing VPC. Providing both this and vpcProps is an error. If an existingAlb or existing Private Hosted Zone is provided, this value must be the VPC associated with those resources. Default: - None
        :param load_balancer_props: Custom properties for a new ALB. Providing both this and existingLoadBalancerObj is an error. These properties cannot include a VPC. Default: - None
        :param log_alb_access_logs: Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param private_hosted_zone_props: Custom properties for a new Private Hosted Zone. Cannot be specified for a public API. Cannot specify a VPC Default: - None
        :param vpc_props: Custom properties for a new VPC. Providing both this and existingVpc is an error. If an existingAlb or existing Private Hosted Zone is provided, those already exist in a VPC so this value cannot be provided. Default: - None
        '''
        if isinstance(alb_logging_bucket_props, dict):
            alb_logging_bucket_props = aws_cdk.aws_s3.BucketProps(**alb_logging_bucket_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {
            "public_api": public_api,
        }
        if alb_logging_bucket_props is not None:
            self._values["alb_logging_bucket_props"] = alb_logging_bucket_props
        if existing_hosted_zone_interface is not None:
            self._values["existing_hosted_zone_interface"] = existing_hosted_zone_interface
        if existing_load_balancer_obj is not None:
            self._values["existing_load_balancer_obj"] = existing_load_balancer_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if load_balancer_props is not None:
            self._values["load_balancer_props"] = load_balancer_props
        if log_alb_access_logs is not None:
            self._values["log_alb_access_logs"] = log_alb_access_logs
        if private_hosted_zone_props is not None:
            self._values["private_hosted_zone_props"] = private_hosted_zone_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def public_api(self) -> builtins.bool:
        '''Whether to create a public or private API.

        This value has implications
        for the VPC, the type of Hosted Zone and the Application Load Balancer

        :default: - None
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
    def existing_hosted_zone_interface(
        self,
    ) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''Existing Public or Private Hosted Zone.

        If a Private Hosted Zone, must
        exist in the same VPC specified in existingVpc

        :default: - None
        '''
        result = self._values.get("existing_hosted_zone_interface")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def existing_load_balancer_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        '''An existing Application Load Balancer.

        Providing both this and loadBalancerProps
        is an error. This ALB must exist in the same VPC specified in existingVPC

        :default: - None
        '''
        result = self._values.get("existing_load_balancer_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC.

        Providing both this and vpcProps is an error. If an existingAlb or existing
        Private Hosted Zone is provided, this value must be the VPC associated with those resources.

        :default: - None
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def load_balancer_props(self) -> typing.Any:
        '''Custom properties for a new ALB.

        Providing both this and existingLoadBalancerObj
        is an error. These properties cannot include a VPC.

        :default: - None
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
    def private_hosted_zone_props(self) -> typing.Any:
        '''Custom properties for a new Private Hosted Zone.

        Cannot be specified for a
        public API. Cannot specify a VPC

        :default: - None
        '''
        result = self._values.get("private_hosted_zone_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Custom properties for a new VPC.

        Providing both this and existingVpc is
        an error. If an existingAlb or existing Private Hosted Zone is provided, those
        already exist in a VPC so this value cannot be provided.

        :default: - None
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Route53ToAlbProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Route53ToAlb",
    "Route53ToAlbProps",
]

publication.publish()
