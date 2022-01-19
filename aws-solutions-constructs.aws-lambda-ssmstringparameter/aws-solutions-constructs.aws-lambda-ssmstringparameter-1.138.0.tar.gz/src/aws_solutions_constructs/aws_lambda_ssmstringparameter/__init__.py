'''
# aws-lambda-ssmstringparameter module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_ssm_string_parameter`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-ssmstringparameter`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdassmstringparameter`|

This AWS Solutions Construct implements the AWS Lambda function and AWS Systems Manager Parameter Store String parameter with the least privileged permissions.

Here is a minimal deployable pattern definition in Typescript:

```javascript
const { LambdaToSsmstringparameterProps,  LambdaToSsmstringparameter } from '@aws-solutions-constructs/aws-lambda-ssmstringparameter';

const props: LambdaToSsmstringparameterProps = {
    lambdaFunctionProps: {
      runtime: lambda.Runtime.NODEJS_14_X,
      // This assumes a handler function in lib/lambda/index.js
      code: lambda.Code.fromAsset(`${__dirname}/lambda`),
      handler: 'index.handler'
    },
    stringParameterProps: { stringValue: "test-string-value" }
};

new LambdaToSsmstringparameter(this, 'test-lambda-ssmstringparameter-stack', props);

```

## Initializer

```text
new LambdaToSsmstringparameter(scope: Construct, id: string, props: LambdaToSsmstringparameterProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`LambdaToSsmstringparameterProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|existingStringParameterObj?|[`ssm.StringParameter`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ssm.StringParameter.html)|Existing instance of SSM String parameter object, providing both this and `stringParameterProps` will cause an error|
|stringParameterProps?|[`ssm.StringParameterProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ssm.StringParameterProps.html)|Optional user provided props to override the default props for SSM String parameter. If existingStringParameterObj is not set stringParameterProps is required. The only supported [`ssm.StringParameterProps.type`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ssm.StringParameterProps.html#type) is [`STRING`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ssm.ParameterType.html#string) if a different value is provided it will be overridden.|
|stringParameterEnvironmentVariableName?|`string`|Optional Name for the SSM String parameter environment variable set for the Lambda function.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for AWS Systems Manager Parameter. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overrriden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|
|stringParameterPermissions|`string`|Optional SSM String parameter permissions to grant to the Lambda function. One of the following may be specified: "Read", "ReadWrite".

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of lambda.Function created by the construct|
|stringParameter|[`ssm.StringParameter`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ssm.StringParameter.html)|Returns an instance of ssm.StringParameter created by the construct|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * (default) SSM_STRING_PARAMETER_NAME
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon AWS Systems Manager Parameter Store String

* Enable read-only access for the associated AWS Lambda Function
* Creates a new SSM String parameter with the values provided
* Retain the SSM String parameter when deleting the CloudFormation stack

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
import aws_cdk.aws_ssm
import aws_cdk.core


class LambdaToSsmstringparameter(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-ssmstringparameter.LambdaToSsmstringparameter",
):
    '''
    :summary: The LambdaToSsmstringparameter class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_string_parameter_obj: typing.Optional[aws_cdk.aws_ssm.StringParameter] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        string_parameter_environment_variable_name: typing.Optional[builtins.str] = None,
        string_parameter_permissions: typing.Optional[builtins.str] = None,
        string_parameter_props: typing.Optional[aws_cdk.aws_ssm.StringParameterProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param existing_string_parameter_obj: Existing instance of SSM String parameter object, If this is set then the stringParameterProps is ignored. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param string_parameter_environment_variable_name: Optional Name for the SSM String parameter environment variable set for the Lambda function. Default: - SSM_STRING_PARAMETER_NAME
        :param string_parameter_permissions: Optional SSM String parameter permissions to grant to the Lambda function. One of the following may be specified: "Read", "ReadWrite". Default: - Read access is given to the Lambda function if no value is specified.
        :param string_parameter_props: Optional user provided props to override the default props for SSM String parameter. If existingStringParameterObj is not set stringParameterProps is required. The only supported string parameter type is ParameterType.STRING. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :since: 1.49.0
        :summary: Constructs a new instance of the LambdaToSsmstringparameter class.
        '''
        props = LambdaToSsmstringparameterProps(
            deploy_vpc=deploy_vpc,
            existing_lambda_obj=existing_lambda_obj,
            existing_string_parameter_obj=existing_string_parameter_obj,
            existing_vpc=existing_vpc,
            lambda_function_props=lambda_function_props,
            string_parameter_environment_variable_name=string_parameter_environment_variable_name,
            string_parameter_permissions=string_parameter_permissions,
            string_parameter_props=string_parameter_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringParameter")
    def string_parameter(self) -> aws_cdk.aws_ssm.StringParameter:
        return typing.cast(aws_cdk.aws_ssm.StringParameter, jsii.get(self, "stringParameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-ssmstringparameter.LambdaToSsmstringparameterProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_vpc": "deployVpc",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_string_parameter_obj": "existingStringParameterObj",
        "existing_vpc": "existingVpc",
        "lambda_function_props": "lambdaFunctionProps",
        "string_parameter_environment_variable_name": "stringParameterEnvironmentVariableName",
        "string_parameter_permissions": "stringParameterPermissions",
        "string_parameter_props": "stringParameterProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToSsmstringparameterProps:
    def __init__(
        self,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_string_parameter_obj: typing.Optional[aws_cdk.aws_ssm.StringParameter] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        string_parameter_environment_variable_name: typing.Optional[builtins.str] = None,
        string_parameter_permissions: typing.Optional[builtins.str] = None,
        string_parameter_props: typing.Optional[aws_cdk.aws_ssm.StringParameterProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param existing_string_parameter_obj: Existing instance of SSM String parameter object, If this is set then the stringParameterProps is ignored. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param string_parameter_environment_variable_name: Optional Name for the SSM String parameter environment variable set for the Lambda function. Default: - SSM_STRING_PARAMETER_NAME
        :param string_parameter_permissions: Optional SSM String parameter permissions to grant to the Lambda function. One of the following may be specified: "Read", "ReadWrite". Default: - Read access is given to the Lambda function if no value is specified.
        :param string_parameter_props: Optional user provided props to override the default props for SSM String parameter. If existingStringParameterObj is not set stringParameterProps is required. The only supported string parameter type is ParameterType.STRING. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToSsmstringparameter class.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(string_parameter_props, dict):
            string_parameter_props = aws_cdk.aws_ssm.StringParameterProps(**string_parameter_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_string_parameter_obj is not None:
            self._values["existing_string_parameter_obj"] = existing_string_parameter_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if string_parameter_environment_variable_name is not None:
            self._values["string_parameter_environment_variable_name"] = string_parameter_environment_variable_name
        if string_parameter_permissions is not None:
            self._values["string_parameter_permissions"] = string_parameter_permissions
        if string_parameter_props is not None:
            self._values["string_parameter_props"] = string_parameter_props
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
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_string_parameter_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_ssm.StringParameter]:
        '''Existing instance of SSM String parameter object, If this is set then the stringParameterProps is ignored.

        :default: - Default props are used
        '''
        result = self._values.get("existing_string_parameter_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_ssm.StringParameter], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function.

        :default: - Default properties are used.
        '''
        result = self._values.get("lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def string_parameter_environment_variable_name(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Optional Name for the SSM String parameter environment variable set for the Lambda function.

        :default: - SSM_STRING_PARAMETER_NAME
        '''
        result = self._values.get("string_parameter_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def string_parameter_permissions(self) -> typing.Optional[builtins.str]:
        '''Optional SSM String parameter permissions to grant to the Lambda function.

        One of the following may be specified: "Read", "ReadWrite".

        :default: - Read access is given to the Lambda function if no value is specified.
        '''
        result = self._values.get("string_parameter_permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def string_parameter_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_ssm.StringParameterProps]:
        '''Optional user provided props to override the default props for SSM String parameter.

        If existingStringParameterObj
        is not set stringParameterProps is required. The only supported string parameter type is ParameterType.STRING.

        :default: - Default props are used
        '''
        result = self._values.get("string_parameter_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ssm.StringParameterProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Properties to override default properties if deployVpc is true.'''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaToSsmstringparameterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToSsmstringparameter",
    "LambdaToSsmstringparameterProps",
]

publication.publish()
