'''
# aws-lambda-secretsmanager module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_lambda_secretsmanager`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-lambda-secretsmanager`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.lambdasecretsmanager`|

This AWS Solutions Construct implements the AWS Lambda function and AWS Secrets Manager secret with the least privileged permissions.

Here is a minimal deployable pattern definition in Typescript:

```javascript
const { LambdaToSecretsmanagerProps,  LambdaToSecretsmanager } from '@aws-solutions-constructs/aws-lambda-secretsmanager';

const props: LambdaToSecretsmanagerProps = {
    lambdaFunctionProps: {
      runtime: lambda.Runtime.NODEJS_14_X,
      // This assumes a handler function in lib/lambda/index.js
      code: lambda.Code.fromAsset(`${__dirname}/lambda`),
      handler: 'index.handler'
    },
};

new LambdaToSecretsmanager(this, 'test-lambda-secretsmanager-stack', props);

```

## Initializer

```text
new LambdaToSecretsmanager(scope: Construct, id: string, props: LambdaToSecretsmanagerProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`LambdaToSecretsmanagerProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, providing both this and `lambdaFunctionProps` will cause an error.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|secretProps?|[`secretsmanager.SecretProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-secretsmanager.SecretProps.html)|Optional user provided props to override the default props for Secrets Manager|
|existingSecretObj?|[`secretsmanager.Secret`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-secretsmanager.Secret.html)|Existing instance of Secrets Manager Secret object, If this is set then the secretProps is ignored|
|grantWriteAccess?|`boolean`|Optional write access to the Secret for the Lambda function (Read-Only by default)
|secretEnvironmentVariableName?|`string`|Optional Name for the Secrets Manager secret environment variable set for the Lambda function.|
|existingVpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|An optional, existing VPC into which this pattern should be deployed. When deployed in a VPC, the Lambda function will use ENIs in the VPC to access network resources and an Interface Endpoint will be created in the VPC for AWS Secrets Manager. If an existing VPC is provided, the `deployVpc` property cannot be `true`. This uses `ec2.IVpc` to allow clients to supply VPCs that exist outside the stack using the [`ec2.Vpc.fromLookup()`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.Vpc.html#static-fromwbrlookupscope-id-options) method.|
|vpcProps?|[`ec2.VpcProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html)|Optional user-provided properties to override the default properties for the new VPC. `enableDnsHostnames`, `enableDnsSupport`, `natGateways` and `subnetConfiguration` are set by the pattern, so any values for those properties supplied here will be overrriden. If `deployVpc` is not `true` then this property will be ignored.|
|deployVpc?|`boolean`|Whether to create a new VPC based on `vpcProps` into which to deploy this pattern. Setting this to true will deploy the minimal, most private VPC to run the pattern:<ul><li> One isolated subnet in each Availability Zone used by the CDK program</li><li>`enableDnsHostnames` and `enableDnsSupport` will both be set to true</li></ul>If this property is `true` then `existingVpc` cannot be specified. Defaults to `false`.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of lambda.Function created by the construct|
|secret|[`secretsmanager.Secret`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-secretsmanager.Secret.html)|Returns an instance of secretsmanager.Secret created by the construct|
|vpc?|[`ec2.IVpc`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html)|Returns an interface on the VPC used by the pattern (if any). This may be a VPC created by the pattern or the VPC supplied to the pattern constructor.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### AWS Lambda Function

* Configure limited privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing
* Set Environment Variables

  * (default) SECRET_ARN containing the ARN of the secret as return by CDK [secretArn property](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-secretsmanager.Secret.html#secretarn).
  * AWS_NODEJS_CONNECTION_REUSE_ENABLED (for Node 10.x and higher functions)

### Amazon SecretsManager Secret

* Enable read-only access for the associated AWS Lambda Function
* Enable server-side encryption using a default KMS key for the account and region
* Creates a new Secret

  * (default) random name
  * (default) random value
* Retain the Secret when deleting the CloudFormation stack

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
import aws_cdk.aws_secretsmanager
import aws_cdk.core


class LambdaToSecretsmanager(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-lambda-secretsmanager.LambdaToSecretsmanager",
):
    '''
    :summary: The LambdaToSecretsmanager class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_secret_obj: typing.Optional[aws_cdk.aws_secretsmanager.Secret] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        grant_write_access: typing.Optional[builtins.str] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        secret_environment_variable_name: typing.Optional[builtins.str] = None,
        secret_props: typing.Optional[aws_cdk.aws_secretsmanager.SecretProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_secret_obj: Existing instance of Secret object, providing both this and secretProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param grant_write_access: Optional secret permissions to grant to the Lambda function. One of the following may be specified: "Read" or "ReadWrite". Default: - Read only acess is given to the Lambda function if no value is specified.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param secret_environment_variable_name: Optional Name for the Secret environment variable set for the Lambda function. Default: - SECRET_NAME
        :param secret_props: Optional user-provided props to override the default props for the Secret. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :access: public
        :summary: Constructs a new instance of the LambdaToSecretsmanager class.
        '''
        props = LambdaToSecretsmanagerProps(
            deploy_vpc=deploy_vpc,
            existing_lambda_obj=existing_lambda_obj,
            existing_secret_obj=existing_secret_obj,
            existing_vpc=existing_vpc,
            grant_write_access=grant_write_access,
            lambda_function_props=lambda_function_props,
            secret_environment_variable_name=secret_environment_variable_name,
            secret_props=secret_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> aws_cdk.aws_secretsmanager.Secret:
        return typing.cast(aws_cdk.aws_secretsmanager.Secret, jsii.get(self, "secret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-lambda-secretsmanager.LambdaToSecretsmanagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_vpc": "deployVpc",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_secret_obj": "existingSecretObj",
        "existing_vpc": "existingVpc",
        "grant_write_access": "grantWriteAccess",
        "lambda_function_props": "lambdaFunctionProps",
        "secret_environment_variable_name": "secretEnvironmentVariableName",
        "secret_props": "secretProps",
        "vpc_props": "vpcProps",
    },
)
class LambdaToSecretsmanagerProps:
    def __init__(
        self,
        *,
        deploy_vpc: typing.Optional[builtins.bool] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_secret_obj: typing.Optional[aws_cdk.aws_secretsmanager.Secret] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        grant_write_access: typing.Optional[builtins.str] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        secret_environment_variable_name: typing.Optional[builtins.str] = None,
        secret_props: typing.Optional[aws_cdk.aws_secretsmanager.SecretProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param deploy_vpc: Whether to deploy a new VPC. Default: - false
        :param existing_lambda_obj: Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error. Default: - None
        :param existing_secret_obj: Existing instance of Secret object, providing both this and secretProps will cause an error. Default: - Default props are used
        :param existing_vpc: An existing VPC for the construct to use (construct will NOT create a new VPC in this case).
        :param grant_write_access: Optional secret permissions to grant to the Lambda function. One of the following may be specified: "Read" or "ReadWrite". Default: - Read only acess is given to the Lambda function if no value is specified.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default properties are used.
        :param secret_environment_variable_name: Optional Name for the Secret environment variable set for the Lambda function. Default: - SECRET_NAME
        :param secret_props: Optional user-provided props to override the default props for the Secret. Default: - Default props are used
        :param vpc_props: Properties to override default properties if deployVpc is true.

        :summary: The properties for the LambdaToSecretsmanager class.
        '''
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        if isinstance(secret_props, dict):
            secret_props = aws_cdk.aws_secretsmanager.SecretProps(**secret_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if deploy_vpc is not None:
            self._values["deploy_vpc"] = deploy_vpc
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_secret_obj is not None:
            self._values["existing_secret_obj"] = existing_secret_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if grant_write_access is not None:
            self._values["grant_write_access"] = grant_write_access
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props
        if secret_environment_variable_name is not None:
            self._values["secret_environment_variable_name"] = secret_environment_variable_name
        if secret_props is not None:
            self._values["secret_props"] = secret_props
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
        '''Existing instance of Lambda Function object, providing both this and ``lambdaFunctionProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def existing_secret_obj(self) -> typing.Optional[aws_cdk.aws_secretsmanager.Secret]:
        '''Existing instance of Secret object, providing both this and secretProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_secret_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.Secret], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC for the construct to use (construct will NOT create a new VPC in this case).'''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def grant_write_access(self) -> typing.Optional[builtins.str]:
        '''Optional secret permissions to grant to the Lambda function.

        One of the following may be specified: "Read" or "ReadWrite".

        :default: - Read only acess is given to the Lambda function if no value is specified.
        '''
        result = self._values.get("grant_write_access")
        return typing.cast(typing.Optional[builtins.str], result)

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
    def secret_environment_variable_name(self) -> typing.Optional[builtins.str]:
        '''Optional Name for the Secret environment variable set for the Lambda function.

        :default: - SECRET_NAME
        '''
        result = self._values.get("secret_environment_variable_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_props(self) -> typing.Optional[aws_cdk.aws_secretsmanager.SecretProps]:
        '''Optional user-provided props to override the default props for the Secret.

        :default: - Default props are used
        '''
        result = self._values.get("secret_props")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.SecretProps], result)

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
        return "LambdaToSecretsmanagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaToSecretsmanager",
    "LambdaToSecretsmanagerProps",
]

publication.publish()
