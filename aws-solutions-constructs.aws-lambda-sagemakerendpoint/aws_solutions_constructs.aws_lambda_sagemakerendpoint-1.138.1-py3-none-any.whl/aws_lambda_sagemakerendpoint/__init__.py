'''
# aws-lambda-sagemakerendpoint module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**: | <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span> |
| :--------------------------- | :------------------------------------------------------------------------------------------------ |

<div style="height:8px"></div>

| **Language**                                                                                   | **Package**                                                      |
| :--------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| ![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python             | `aws_solutions_constructs.aws_lambda_sagemakerendpoint`          |
| ![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript | `@aws-solutions-constructs/aws-lambda-sagemakerendpoint`         |
| ![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java                   | `software.amazon.awsconstructs.services.lambdasagemakerendpoint` |

This AWS Solutions Construct implements an AWS Lambda function connected to an Amazon Sagemaker Endpoint.

Here is a minimal deployable pattern definition in Typescript:

```python
import { Duration } from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import {
  LambdaToSagemakerEndpoint,
  LambdaToSagemakerEndpointProps,
} from '@aws-solutions-constructs/aws-lambda-sagemakerendpoint';

const constructProps: LambdaToSagemakerEndpointProps = {
  modelProps: {
    primaryContainer: {
      image: '<AccountId>.dkr.ecr.<region>.amazonaws.com/linear-learner:latest',
      modelDataUrl: 's3://<bucket-name>/<prefix>/model.tar.gz',
    },
  },
  lambdaFunctionProps: {
    runtime: lambda.Runtime.PYTHON_3_8,
    code: lambda.Code.fromAsset(`${__dirname}/lambda`),
    handler: 'index.handler',
    timeout: Duration.minutes(5),
    memorySize: 128,
  },
};

new LambdaToSagemakerEndpoint(this, 'LambdaToSagemakerEndpointPattern', constructProps);
```

## Initializer

```text
new LambdaToSagemakerEndpoint(scope: Construct, id: string, props: LambdaToSagemakerEndpointProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`LambdaToSagemakerEndpointProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|An optional, existing Lambda function to be used instead of the default function. Providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|Optional user-provided properties to override the default properties for the Lambda function.|
|existingSagemakerEndpointObj?|[`sagemaker.CfnEndpoint`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnEndpoint.html)|An optional, existing Sagemaker Enpoint to be used. Providing both this and `endpointProps?` will cause an error.|
|modelProps?|[`sagemaker.CfnModelProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnModelProps.html) | `any`|User-provided properties to override the default properties for the Sagemaker Model. At least `modelProps?.primaryContainer` must be provided to create a model. By default, the pattern will create a role with the minimum required permissions, but the client can provide a custom role with additional capabilities using `modelProps?.executionRoleArn`.|
|endpointConfigProps?|[`sagemaker.CfnEndpointConfigProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnEndpointConfigProps.html)|Optional user-provided properties to override the default properties for the Sagemaker Endpoint Config. |
|endpointProps?|[`sagemaker.CfnEndpointProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnEndpointProps.html)| Optional user-provided properties to override the default properties for the Sagemaker Endpoint Config. |
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|An optional, existing VPC into which this construct should be deployed. When deployed in a VPC, the Lambda function and Sagemaker Endpoint will use ENIs in the VPC to access network resources. An Interface Endpoint will be created in the VPC for Amazon Sagemaker Runtime, and Amazon S3 VPC Endpoint. If an existing VPC is provided, the `deployVpc?` property cannot be `true`.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the Construct, so any values for those properties supplied here will be overrriden. If `deployVpc?` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|
|sagemakerEnvironmentVariableName?|`string`|Optional Name for the SageMaker endpoint environment variable set for the Lambda function.|

## Pattern Properties

| **Name**                 | **Type**                                                                                                                       | **Description**                                                                                                                 |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| lambdaFunction           | [`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)                         | Returns an instance of the Lambda function created by the pattern.                                                              |
| sagemakerEndpoint        | [`sagemaker.CfnEndpoint`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnEndpoint.html)             | Returns an instance of the Sagemaker Endpoint created by the pattern.                                                           |
| sagemakerEndpointConfig? | [`sagemaker.CfnEndpointConfig`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnEndpointConfig.html) | Returns an instance of the SageMaker EndpointConfig created by the pattern, if `existingSagemakerEndpointObj?` is not provided. |
| sagemakerModel?          | [`sagemaker.CfnModel`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sagemaker.CfnModel.html)                   | Returns an instance of the Sagemaker Model created by the pattern, if `existingSagemakerEndpointObj?` is not provided.          |
| vpc?                     | `ec2.IVpc`                                                                                                                     | Returns an instance of the VPC created by the pattern, if `deployVpc?` is `true`, or `existingVpc?` is provided.                |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Allow the function to invoke the Sagemaker endpoint for Inferences
* Configure the function to access resources in the VPC, where the Sagemaker endpoint is deployed
* Enable X-Ray Tracing
* Set environment variables:

  * (default) SAGEMAKER_ENDPOINT_NAME
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions).

### Amazon Sagemaker Endpoint

* Configure limited privilege to create Sagemaker resources
* Deploy Sagemaker model, endpointConfig, and endpoint
* Configure the Sagemaker endpoint to be deployed in a VPC
* Deploy S3 VPC Endpoint and Sagemaker Runtime VPC Interface

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
import aws_cdk.aws_lambda
import aws_cdk.aws_sagemaker
import aws_cdk.core


class LambdaToSagemakerEndpoint(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-sagemakerendpoint.LambdaToSagemakerEndpoint",
):
    '''
    :summary: The LambdaToSagemakerEndpoint class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        endpoint_config_props: typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointConfigProps] = None,
        endpoint_props: typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_sagemaker_endpoint_obj: typing.Optional[aws_cdk.aws_sagemaker.CfnEndpoint] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        model_props: typing.Any = None,
        sagemaker_environment_variable_name: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a scope-unique id.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param endpoint_config_props: User provided props to create Sagemaker Endpoint Configuration. Default: - Default props are used
        :param endpoint_props: User provided props to create Sagemaker Endpoint. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, Providing both this and lambdaFunctionProps will cause an error. Default: - None
        :param existing_sagemaker_endpoint_obj: Existing Sagemaker Enpoint object, providing both this and endpointProps will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case). Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param model_props: User provided props to create Sagemaker Model. Default: - None
        :param sagemaker_environment_variable_name: Optional Name for the SageMaker endpoint environment variable set for the Lambda function. Default: - None
        :param vpc_props: Properties to override default properties if deployVpc is true. Default: - None

        :access: public
        :since: 1.87.1
        :summary: Constructs a new instance of the LambdaToSagemakerEndpoint class.
        '''
        props = LambdaToSagemakerEndpointProps(
            deploy_vpc=deploy_vpc,
            endpoint_config_props=endpoint_config_props,
            endpoint_props=endpoint_props,
            existing_lambda_obj=existing_lambda_obj,
            existing_sagemaker_endpoint_obj=existing_sagemaker_endpoint_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            model_props=model_props,
            sagemaker_environment_variable_name=sagemaker_environment_variable_name,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sagemakerEndpoint")
    def sagemaker_endpoint(self) -> aws_cdk.aws_sagemaker.CfnEndpoint:
        return typing.cast(aws_cdk.aws_sagemaker.CfnEndpoint, jsii.get(self, "sagemakerEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sagemakerEndpointConfig")
    def sagemaker_endpoint_config(
        self,
    ) -> typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointConfig]:
        return typing.cast(typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointConfig], jsii.get(self, "sagemakerEndpointConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sagemakerModel")
    def sagemaker_model(self) -> typing.Optional[aws_cdk.aws_sagemaker.CfnModel]:
        return typing.cast(typing.Optional[aws_cdk.aws_sagemaker.CfnModel], jsii.get(self, "sagemakerModel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-sagemakerendpoint.LambdaToSagemakerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_vpc": "deployVpc",
        "endpoint_config_props": "endpointConfigProps",
        "endpoint_props": "endpointProps",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_sagemaker_endpoint_obj": "existingSagemakerEndpointObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "model_props": "modelProps",
        "sagemaker_environment_variable_name": "sagemakerEnvironmentVariableName",
        "vpc_props": "vpcProps",
    },
)
class LambdaToSagemakerEndpointProps:
    def __init__(
        self,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        endpoint_config_props: typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointConfigProps] = None,
        endpoint_props: typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_sagemaker_endpoint_obj: typing.Optional[aws_cdk.aws_sagemaker.CfnEndpoint] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        model_props: typing.Any = None,
        sagemaker_environment_variable_name: typing.Optional[builtins.str] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param endpoint_config_props: User provided props to create Sagemaker Endpoint Configuration. Default: - Default props are used
        :param endpoint_props: User provided props to create Sagemaker Endpoint. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, Providing both this and lambdaFunctionProps will cause an error. Default: - None
        :param existing_sagemaker_endpoint_obj: Existing Sagemaker Enpoint object, providing both this and endpointProps will cause an error. Default: - None
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case). Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used
        :param model_props: User provided props to create Sagemaker Model. Default: - None
        :param sagemaker_environment_variable_name: Optional Name for the SageMaker endpoint environment variable set for the Lambda function. Default: - None
        :param vpc_props: Properties to override default properties if deployVpc is true. Default: - None

        :summary: The properties for the LambdaToSagemakerEndpoint class
        '''
        if isinstance(endpoint_config_props, dict):
            endpoint_config_props = aws_cdk.aws_sagemaker.CfnEndpointConfigProps(**endpoint_config_props)
        if isinstance(endpoint_props, dict):
            endpoint_props = aws_cdk.aws_sagemaker.CfnEndpointProps(**endpoint_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if endpoint_config_props is not None:
            self._values["endpoint_config_props"] = endpoint_config_props
        if endpoint_props is not None:
            self._values["endpoint_props"] = endpoint_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_sagemaker_endpoint_obj is not None:
            self._values["existing_sagemaker_endpoint_obj"] = existing_sagemaker_endpoint_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if model_props is not None:
            self._values["model_props"] = model_props
        if sagemaker_environment_variable_name is not None:
            self._values["sagemaker_environment_variable_name"] = sagemaker_environment_variable_name
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def deploy_vpc(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a new VPC.

        :default: - false
        '''
        result = self._values.get("deploy_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def endpoint_config_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointConfigProps]:
        '''User provided props to create Sagemaker Endpoint Configuration.

        :default: - Default props are used
        '''
        result = self._values.get("endpoint_config_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointConfigProps], result)

    @builtins.property
    def endpoint_props(self) -> typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointProps]:
        '''User provided props to create Sagemaker Endpoint.

        :default: - Default props are used
        '''
        result = self._values.get("endpoint_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sagemaker.CfnEndpointProps], result)

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, Providing both this and lambdaFunctionProps will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_sagemaker_endpoint_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_sagemaker.CfnEndpoint]:
        '''Existing Sagemaker Enpoint object, providing both this and endpointProps will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_sagemaker_endpoint_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sagemaker.CfnEndpoint], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).

        :default: - None
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
    def model_props(self) -> typing.Any:
        '''User provided props to create Sagemaker Model.

        :default: - None
        '''
        result = self._values.get("model_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def sagemaker_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the SageMaker endpoint environment variable set for the Lambda function.

        :default: - None
        '''
        result = self._values.get("sagemaker_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Properties to override default properties if deployVpc is true.

        :default: - None
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToSagemakerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToSagemakerEndpoint",
    "LambdaToSagemakerEndpointProps",
]

publication.publish()
