'''
# aws-wafwebacl-apigateway module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_wafwebacl_apigateway`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-wafwebacl-apigateway`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.wafwebaclapigateway`|

## Overview

This AWS Solutions Construct implements an AWS WAF web ACL connected to Amazon API Gateway REST API.

Here is a minimal deployable pattern definition in Typescript:

```python
import * as api from '@aws-cdk/aws-apigateway';
import * as lambda from "@aws-cdk/aws-lambda";
import { ApiGatewayToLambda } from '@aws-solutions-constructs/aws-apigateway-lambda';
import { WafwebaclToApiGatewayProps, WafwebaclToApiGateway } from "@aws-solutions-constructs/aws-wafwebacl-apigateway";

const apiGatewayToLambda = new ApiGatewayToLambda(this, 'ApiGatewayToLambdaPattern', {
    lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_14_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`lambda`)
    }
});

// This construct can only be attached to a configured API Gateway.
new WafwebaclToApiGateway(this, 'test-wafwebacl-apigateway', {
    existingApiGatewayInterface: apiGatewayToLambda.apiGateway
});
```

## Initializer

```text
new WafwebaclToApiGateway(scope: Construct, id: string, props: WafwebaclToApiGatewayProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`WafwebaclToApiGatewayProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingApiGatewayInterface|[`api.IRestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.IRestApi.html)|The existing API Gateway instance that will be protected with the WAF web ACL. *Note that a WAF web ACL can only be added to a configured API Gateway, so this construct only accepts an existing IRestApi and does not accept apiGatewayProps.*|
|existingWebaclObj?|[`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-waf.CfnWebACL.html)|Existing instance of a WAF web ACL, an error will occur if this and props is set.|
|webaclProps?|[`waf.CfnWebACLProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-waf.CfnWebACLProps.html)|Optional user-provided props to override the default props for the AWS WAF web ACL. To use a different collection of managed rule sets, specify a new rules property. Use our [`wrapManagedRuleSet(managedGroupName: string, vendorName: string, priority: number)`](../core/lib/waf-defaults.ts) function from core to create an array entry from each desired managed rule set.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|webacl|[`waf.CfnWebACL`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-waf.CfnWebACL.html)|Returns an instance of the waf.CfnWebACL created by the construct.|
|apiGateway|[`api.IRestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.IRestApi.html)|Returns an instance of the API Gateway REST API created by the pattern. |

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

### Amazon API Gateway

* User provided API Gateway object is used as-is

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

import aws_cdk.aws_apigateway
import aws_cdk.aws_wafv2
import aws_cdk.core


class WafwebaclToApiGateway(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-apigateway.WafwebaclToApiGateway",
):
    '''
    :summary: The WafwebaclToApiGateway class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        existing_api_gateway_interface: aws_cdk.aws_apigateway.IRestApi,
        existing_webacl_obj: typing.Optional[aws_cdk.aws_wafv2.CfnWebACL] = None,
        webacl_props: typing.Optional[aws_cdk.aws_wafv2.CfnWebACLProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_api_gateway_interface: The existing API Gateway instance that will be protected with the WAF web ACL.
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :access: public
        :summary: Constructs a new instance of the WafwebaclToApiGateway class.
        '''
        props = WafwebaclToApiGatewayProps(
            existing_api_gateway_interface=existing_api_gateway_interface,
            existing_webacl_obj=existing_webacl_obj,
            webacl_props=webacl_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> aws_cdk.aws_apigateway.IRestApi:
        return typing.cast(aws_cdk.aws_apigateway.IRestApi, jsii.get(self, "apiGateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="webacl")
    def webacl(self) -> aws_cdk.aws_wafv2.CfnWebACL:
        return typing.cast(aws_cdk.aws_wafv2.CfnWebACL, jsii.get(self, "webacl"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-wafwebacl-apigateway.WafwebaclToApiGatewayProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_api_gateway_interface": "existingApiGatewayInterface",
        "existing_webacl_obj": "existingWebaclObj",
        "webacl_props": "webaclProps",
    },
)
class WafwebaclToApiGatewayProps:
    def __init__(
        self,
        *,
        existing_api_gateway_interface: aws_cdk.aws_apigateway.IRestApi,
        existing_webacl_obj: typing.Optional[aws_cdk.aws_wafv2.CfnWebACL] = None,
        webacl_props: typing.Optional[aws_cdk.aws_wafv2.CfnWebACLProps] = None,
    ) -> None:
        '''
        :param existing_api_gateway_interface: The existing API Gateway instance that will be protected with the WAF web ACL.
        :param existing_webacl_obj: Existing instance of a WAF web ACL, an error will occur if this and props is set.
        :param webacl_props: Optional user-provided props to override the default props for the AWS WAF web ACL. Default: - Default properties are used.

        :summary: The properties for the WafwebaclToApiGateway class.
        '''
        if isinstance(webacl_props, dict):
            webacl_props = aws_cdk.aws_wafv2.CfnWebACLProps(**webacl_props)
        self._values: typing.Dict[str, typing.Any] = {
            "existing_api_gateway_interface": existing_api_gateway_interface,
        }
        if existing_webacl_obj is not None:
            self._values["existing_webacl_obj"] = existing_webacl_obj
        if webacl_props is not None:
            self._values["webacl_props"] = webacl_props

    @builtins.property
    def existing_api_gateway_interface(self) -> aws_cdk.aws_apigateway.IRestApi:
        '''The existing API Gateway instance that will be protected with the WAF web ACL.'''
        result = self._values.get("existing_api_gateway_interface")
        assert result is not None, "Required property 'existing_api_gateway_interface' is missing"
        return typing.cast(aws_cdk.aws_apigateway.IRestApi, result)

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
        return "WafwebaclToApiGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WafwebaclToApiGateway",
    "WafwebaclToApiGatewayProps",
]

publication.publish()
