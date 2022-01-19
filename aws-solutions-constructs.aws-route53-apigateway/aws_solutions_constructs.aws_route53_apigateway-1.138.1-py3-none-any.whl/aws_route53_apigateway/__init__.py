'''
# aws-route53-apigateway module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_route53_apigateway`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-route53-apigateway`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.route53apigateway`|

## Overview

This AWS Solutions Construct implements an Amazon Route 53 connected to a configured Amazon API Gateway REST API.

Here is a minimal deployable pattern definition in Typescript:

```python
import * as api from '@aws-cdk/aws-apigateway';
import * as lambda from "@aws-cdk/aws-lambda";
import * as route53 from "@aws-cdk/aws-route53";
import { Route53ToApigateway } from '@aws-solutions-constructs/aws-route53-apigateway';

// The construct requires an existing REST API, this can be created in raw CDK or extracted
// from a previously instantiated construct that created an API Gateway REST API
const existingRestApi = previouslyCreatedApigatewayToLambdaConstruct.apiGateway;

const ourHostedZone = route53.HostedZone.fromLookup(this, 'HostedZone', {
    domainName: "example.com",
  });

const certificate = acm.Certificate.fromCertificateArn(
    stack,
    "fake-cert",
    "arn:aws:acm:us-east-1:123456789012:certificate/11112222-3333-1234-1234-123456789012"
  );

// This construct can only be attached to a configured API Gateway.
new Route53ToApigateway(this, 'Route53ToApigatewayPattern', {
    existingApiGatewayObj: existingRestApi,
    existingHostedZoneInterface: ourHostedZone,
    publicApi: true,
    existingCertificateInterface: certificate
});
```

## Initializer

```text
new Route53ToApigateway(scope: Construct, id: string, props: Route53ToApigatewayProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`Route53ToApigatewayProps`](#pattern-construct-props)

## Pattern Construct Props

This construct cannot create a new Public Hosted Zone, if you are creating a public API you must supply an existing Public Hosted Zone that will be reconfigured with a new Alias record. Public Hosted Zones are configured with public domain names and are not well suited to be launched and torn down dynamically, so this construct will only reconfigure existing Public Hosted Zones.

This construct can create Private Hosted Zones. If you want a Private Hosted Zone, then you can either provide an existing Private Hosted Zone or a privateHostedZoneProps value with at least the Domain Name defined. If you are using privateHostedZoneProps, an existing wildcard certificate (*.example.com) must be issued from a previous domain to be used in the newly created Private Hosted Zone. New certificate creation and validation do not take place in this construct. A private Rest API already exists in a VPC, so that VPC must be provided in the existingVpc prop. There is no scenario where this construct can create a new VPC (since it can't create a new API), so the vpcProps property is not supported on this construct.

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| publicApi | boolean | Whether the construct is deploying a private or public API. This has implications for the Hosted Zone and VPC. |
| privateHostedZoneProps? | [route53.PrivateHostedZoneProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.PrivateHostedZoneProps.html) | Optional custom properties for a new Private Hosted Zone. Cannot be specified for a public API. Cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Providing both this and existingHostedZoneInterface is an error. |
| existingHostedZoneInterface? | [route53.IHostedZone](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.IHostedZone.html) | Existing Public or Private Hosted Zone (type must match publicApi setting). Specifying both this and privateHostedZoneProps is an error. If this is a Private Hosted Zone, the associated VPC must be provided as the existingVpc property.|
| existingVpc? | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | An existing VPC in which to deploy the construct.|
|existingApiGatewayInterface|[api.IRestApi](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.IRestApi.html)|The existing API Gateway instance that will be connected to the Route 53 hosted zone. *Note that Route 53 can only be connected to a configured API Gateway, so this construct only accepts an existing IRestApi and does not accept apiGatewayProps.*|
| existingCertificateInterface |[certificatemanager.ICertificate](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-certificatemanager.ICertificate.html)| An existing AWS Certificate Manager certificate for your custom domain name.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|hostedZone|[route53.IHostedZone](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.IHostedZone.html)|The hosted zone used by the construct (whether created by the construct or provided by the client) |
| vpc? | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | The VPC used by the construct. |
|apiGateway|[api.RestApi](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|certificate|[certificatemanager.ICertificate](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-certificatemanager.ICertificate.html)| THe certificate used by the construct (whether create by the construct or provided by the client)

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Route53

* Adds an ALIAS record to the new or provided Hosted Zone that routes to the construct's API Gateway

### Amazon API Gateway

* User provided API Gateway object is used as-is
* Sets up custom domain name mapping to API

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import aws_cdk.aws_certificatemanager
import aws_cdk.aws_ec2
import aws_cdk.aws_route53
import aws_cdk.core


class Route53ToApiGateway(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-route53-apigateway.Route53ToApiGateway",
):
    '''
    :summary: The Route53ToApiGateway class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        existing_api_gateway_interface: aws_cdk.aws_apigateway.IRestApi,
        existing_certificate_interface: aws_cdk.aws_certificatemanager.ICertificate,
        public_api: builtins.bool,
        existing_hosted_zone_interface: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        private_hosted_zone_props: typing.Any = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_api_gateway_interface: The existing API Gateway instance that will be protected with the Route 53 hosted zone. Default: - None
        :param existing_certificate_interface: An existing AWS Certificate Manager certificate for your custom domain name.
        :param public_api: Whether to create a public or private API. This value has implications for the VPC, the type of Hosted Zone and the Application Load Balancer Default: - None
        :param existing_hosted_zone_interface: Existing Public or Private Hosted Zone. If a Private Hosted Zone, must exist in the same VPC specified in existingVpc Default: - None
        :param existing_vpc: An existing VPC. If an existing Private Hosted Zone is provided, this value must be the VPC associated with those resources. Default: - None
        :param private_hosted_zone_props: Optional custom properties for a new Private Hosted Zone. Cannot be specified for a public API. Cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Providing both this and existingHostedZoneInterface is an error. Default: - None

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the Route53ToApiGateway class.
        '''
        props = Route53ToApiGatewayProps(
            existing_api_gateway_interface=existing_api_gateway_interface,
            existing_certificate_interface=existing_certificate_interface,
            public_api=public_api,
            existing_hosted_zone_interface=existing_hosted_zone_interface,
            existing_vpc=existing_vpc,
            private_hosted_zone_props=private_hosted_zone_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> aws_cdk.aws_apigateway.RestApi:
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> aws_cdk.aws_certificatemanager.ICertificate:
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, jsii.get(self, "certificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.get(self, "hostedZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-route53-apigateway.Route53ToApiGatewayProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_api_gateway_interface": "existingApiGatewayInterface",
        "existing_certificate_interface": "existingCertificateInterface",
        "public_api": "publicApi",
        "existing_hosted_zone_interface": "existingHostedZoneInterface",
        "existing_vpc": "existingVpc",
        "private_hosted_zone_props": "privateHostedZoneProps",
    },
)
class Route53ToApiGatewayProps:
    def __init__(
        self,
        *,
        existing_api_gateway_interface: aws_cdk.aws_apigateway.IRestApi,
        existing_certificate_interface: aws_cdk.aws_certificatemanager.ICertificate,
        public_api: builtins.bool,
        existing_hosted_zone_interface: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        private_hosted_zone_props: typing.Any = None,
    ) -> None:
        '''The properties for the Route53ToApiGateway class.

        :param existing_api_gateway_interface: The existing API Gateway instance that will be protected with the Route 53 hosted zone. Default: - None
        :param existing_certificate_interface: An existing AWS Certificate Manager certificate for your custom domain name.
        :param public_api: Whether to create a public or private API. This value has implications for the VPC, the type of Hosted Zone and the Application Load Balancer Default: - None
        :param existing_hosted_zone_interface: Existing Public or Private Hosted Zone. If a Private Hosted Zone, must exist in the same VPC specified in existingVpc Default: - None
        :param existing_vpc: An existing VPC. If an existing Private Hosted Zone is provided, this value must be the VPC associated with those resources. Default: - None
        :param private_hosted_zone_props: Optional custom properties for a new Private Hosted Zone. Cannot be specified for a public API. Cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Providing both this and existingHostedZoneInterface is an error. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "existing_api_gateway_interface": existing_api_gateway_interface,
            "existing_certificate_interface": existing_certificate_interface,
            "public_api": public_api,
        }
        if existing_hosted_zone_interface is not None:
            self._values["existing_hosted_zone_interface"] = existing_hosted_zone_interface
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if private_hosted_zone_props is not None:
            self._values["private_hosted_zone_props"] = private_hosted_zone_props

    @builtins.property
    def existing_api_gateway_interface(self) -> aws_cdk.aws_apigateway.IRestApi:
        '''The existing API Gateway instance that will be protected with the Route 53 hosted zone.

        :default: - None
        '''
        result = self._values.get("existing_api_gateway_interface")
        assert result is not None, "Required property 'existing_api_gateway_interface' is missing"
        return typing.cast(aws_cdk.aws_apigateway.IRestApi, result)

    @builtins.property
    def existing_certificate_interface(
        self,
    ) -> aws_cdk.aws_certificatemanager.ICertificate:
        '''An existing AWS Certificate Manager certificate for your custom domain name.

        :defualt: - None
        '''
        result = self._values.get("existing_certificate_interface")
        assert result is not None, "Required property 'existing_certificate_interface' is missing"
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, result)

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
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC.

        If an existing Private Hosted Zone is provided,
        this value must be the VPC associated with those resources.

        :default: - None
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def private_hosted_zone_props(self) -> typing.Any:
        '''Optional custom properties for a new Private Hosted Zone.

        Cannot be specified for a
        public API. Cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct.
        Providing both this and existingHostedZoneInterface is an error.

        :default: - None
        '''
        result = self._values.get("private_hosted_zone_props")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Route53ToApiGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Route53ToApiGateway",
    "Route53ToApiGatewayProps",
]

publication.publish()
