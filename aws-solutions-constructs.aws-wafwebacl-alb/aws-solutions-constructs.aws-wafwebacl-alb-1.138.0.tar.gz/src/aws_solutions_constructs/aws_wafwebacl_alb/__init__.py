'''
# aws-wafwebacl-alb module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_wafwebacl_alb`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-wafwebacl-alb`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.wafwebaclalb`|

## Overview

This AWS Solutions Construct implements an AWS WAF web ACL connected to an Application Load Balancer.

Here is a minimal deployable pattern definition in Typescript:

```python
import { Route53ToAlb } from '@aws-solutions-constructs/aws-route53-alb';
import { WafwebaclToAlbProps, WafwebaclToAlb } from "@aws-solutions-constructs/aws-wafwebacl-alb";

// A constructed ALB is required to be attached to the WAF Web ACL.
// In this case, we are using this construct to create one.
const r53ToAlb = new Route53ToAlb(this, 'Route53ToAlbPattern', {
  privateHostedZoneProps: {
    zoneName: 'www.example.com',
  },
  publicApi: false,
  logAccessLogs: false
});

// This construct can only be attached to a configured Application Load Balancer.
new WafwebaclToAlb(this, 'test-wafwebacl-alb', {
    existingLoadBalancerObj: r53ToAlb.loadBalancer
});
```

## Initializer

```text
new WafwebaclToAlb(scope: Construct, id: string, props: WafwebaclToAlbProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`WafwebaclToAlbProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLoadBalancerObj|[`elbv2.ApplicationLoadBalancer`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html)|The existing Application Load Balancer Object that will be protected with the WAF web ACL. *Note that a WAF web ACL can only be added to a configured Application Load Balancer, so this construct only accepts an existing ApplicationLoadBalancer and does not accept applicationLoadBalancerProps.*|
|existingWebaclObj?|[`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-waf.CfnWebACL.html)|Existing instance of a WAF web ACL, an error will occur if this and props is set.|
|webaclProps?|[`waf.CfnWebACLProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-waf.CfnWebACLProps.html)|Optional user-provided props to override the default props for the AWS WAF web ACL. To use a different collection of managed rule sets, specify a new rules property. Use our [`wrapManagedRuleSet(managedGroupName: string, vendorName: string, priority: number)`](../core/lib/waf-defaults.ts) function from core to create an array entry from each desired managed rule set.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|webacl|[`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-waf.CfnWebACL.html)|Returns an instance of the waf.CfnWebACL created by the construct.|
|loadBalancer|[`elbv2.ApplicationLoadBalancer`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html)|Returns an instance of the Application Load Balancer Object created by the pattern. |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS WAF

* Deploy a WAF web ACL with 7 [AWS managed rule groups](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html).

  * AWSManagedRulesBotControlRuleSet
  * AWSManagedRulesKnownBadInputsRuleSet
  * AWSManagedRulesCommonRuleSet
  * AWSManagedRulesAnonymousIpList
  * AWSManagedRulesAmazonIpReputationList
  * AWSManagedRulesAdminProtectionRuleSet
  * AWSManagedRulesSQLiRuleSet

  *Note that the default rules can be replaced by specifying the rules property of CfnWebACLProps*
* Send metrics to Amazon CloudWatch

### Application Load Balancer

* User provided Application Load Balancer object is used as-is

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

import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_wafv2
import aws_cdk.core


class WafwebaclToAlb(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-alb.WafwebaclToAlb",
):
    '''
    :summary: The WafwebaclToAlb class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        existing_load_balancer_obj: aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer,
        existing_webacl_obj: typing.Optional[aws_cdk.aws_wafv2.CfnWebACL] = None,
        webacl_props: typing.Optional[aws_cdk.aws_wafv2.CfnWebACLProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_load_balancer_obj: The existing Application Load Balancer instance that will be protected with the WAF web ACL.
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :access: public
        :summary: Constructs a new instance of the WafwebaclToAlb class.
        '''
        props = WafwebaclToAlbProps(
            existing_load_balancer_obj=existing_load_balancer_obj,
            existing_webacl_obj=existing_webacl_obj,
            webacl_props=webacl_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="webacl")
    def webacl(self) -> aws_cdk.aws_wafv2.CfnWebACL:
        return typing.cast(aws_cdk.aws_wafv2.CfnWebACL, jsii.get(self, "webacl"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-alb.WafwebaclToAlbProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_load_balancer_obj": "existingLoadBalancerObj",
        "existing_webacl_obj": "existingWebaclObj",
        "webacl_props": "webaclProps",
    },
)
class WafwebaclToAlbProps:
    def __init__(
        self,
        *,
        existing_load_balancer_obj: aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer,
        existing_webacl_obj: typing.Optional[aws_cdk.aws_wafv2.CfnWebACL] = None,
        webacl_props: typing.Optional[aws_cdk.aws_wafv2.CfnWebACLProps] = None,
    ) -> None:
        '''
        :param existing_load_balancer_obj: The existing Application Load Balancer instance that will be protected with the WAF web ACL.
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :summary: The properties for the WafwebaclToAlb class.
        '''
        if isinstance(webacl_props, dict):
            webacl_props = aws_cdk.aws_wafv2.CfnWebACLProps(**webacl_props)
        self._values: typing.Dict[str, typing.Any] = {
            "existing_load_balancer_obj": existing_load_balancer_obj,
        }
        if existing_webacl_obj is not None:
            self._values["existing_webacl_obj"] = existing_webacl_obj
        if webacl_props is not None:
            self._values["webacl_props"] = webacl_props

    @builtins.property
    def existing_load_balancer_obj(
        self,
    ) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer:
        '''The existing Application Load Balancer instance that will be protected with the WAF web ACL.'''
        result = self._values.get("existing_load_balancer_obj")
        assert result is not None, "Required property 'existing_load_balancer_obj' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, result)

    @builtins.property
    def existing_webacl_obj(self) -> typing.Optional[aws_cdk.aws_wafv2.CfnWebACL]:
        '''Existing instance of a WAF web ACL, an error will occur if this and props is set.'''
        result = self._values.get("existing_webacl_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_wafv2.CfnWebACL], result)

    @builtins.property
    def webacl_props(self) -> typing.Optional[aws_cdk.aws_wafv2.CfnWebACLProps]:
        '''Optional user-provided props to override the default props for the AWS WAF web ACL.

        :default: - Default properties are used.
        '''
        result = self._values.get("webacl_props")
        return typing.cast(typing.Optional[aws_cdk.aws_wafv2.CfnWebACLProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WafwebaclToAlbProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WafwebaclToAlb",
    "WafwebaclToAlbProps",
]

publication.publish()
