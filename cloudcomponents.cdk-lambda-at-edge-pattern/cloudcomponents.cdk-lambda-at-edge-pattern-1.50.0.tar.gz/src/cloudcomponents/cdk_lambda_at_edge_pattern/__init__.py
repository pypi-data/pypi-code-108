'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-lambda-at-edge-pattern

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-lambda-at-edge-pattern)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-lambda-at-edge-pattern/)

> CDK Constructs for Lambda@Edge pattern: HttpHeaders

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-lambda-at-edge-pattern
```

Python:

```bash
pip install cloudcomponents.cdk-lambda-at-edge-pattern
```

## How to use

```python
import { Construct, RemovalPolicy, Stack, StackProps } from '@aws-cdk/core';
import { StringParameter } from '@aws-cdk/aws-ssm';
import { SecurityPolicyProtocol } from '@aws-cdk/aws-cloudfront';
import { StaticWebsite } from '@cloudcomponents/cdk-static-website';
import { HttpHeaders } from '@cloudcomponents/cdk-lambda-at-edge-pattern';

export class StaticWebsiteStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const certificateArn = StringParameter.valueFromLookup(
      this,
      '/certificate/cloudcomponents.org',
    );

    const website = new StaticWebsite(this, 'StaticWebsite', {
      bucketConfiguration: {
        removalPolicy: RemovalPolicy.DESTROY,
      },
      aliasConfiguration: {
        domainName: 'cloudcomponents.org',
        names: ['www.cloudcomponents.org', 'cloudcomponents.org'],
        acmCertRef: certificateArn,
      },
    });

    // A us-east-1 stack is generated under the hood
    const httpHeaders = new HttpHeaders(this, 'HttpHeaders', {
      httpHeaders: {
        'Content-Security-Policy':
          "default-src 'none'; img-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'; connect-src 'self'",
        'Strict-Transport-Security':
          'max-age=31536000; includeSubdomains; preload',
        'Referrer-Policy': 'same-origin',
        'X-XSS-Protection': '1; mode=block',
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Cache-Control': 'no-cache',
      },
    });

    website.addLambdaFunctionAssociation(httpHeaders);
  }
}
```

### Cloudfront Distribution

```python
new cloudfront.Distribution(this, 'myDist', {
  defaultBehavior: {
    origin: new origins.S3Origin(myBucket),
    edgeLambdas: [httpHeaders],
  },
});
```

### Cloudfront WebDistribution

```python
new cloudfront.CloudFrontWebDistribution(this, 'MyDistribution', {
  originConfigs: [
    {
      s3OriginSource: {
        s3BucketSource: sourceBucket
      },
      behaviors: [
        {
          isDefaultBehavior: true,
          lambdaFunctionAssociations: [httpHeaders],
        }
      ]
    }
  ]
 });
```

### HttpHeaders

```python
const httpHeaders = new HttpHeaders(this, 'HttpHeaders', {
  httpHeaders: {
    'Content-Security-Policy':
      "default-src 'none'; img-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'; connect-src 'self'",
    'Strict-Transport-Security':
      'max-age=31536000; includeSubdomains; preload',
    'Referrer-Policy': 'same-origin',
    'X-XSS-Protection': '1; mode=block',
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Cache-Control': 'no-cache',
  },
});
```

### OriginMutation

https://chrisschuld.com/2020/05/gatsby-hosting-on-cloudfront/

```python
const originMutation = new OriginMutation(stack, 'OriginMutation');
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-lambda-at-edge-pattern/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-lambda-at-edge-pattern/LICENSE)
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

import aws_cdk.aws_cloudfront
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.core


class BaseEdgeConstruct(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.BaseEdgeConstruct",
):
    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="edgeStack")
    def _edge_stack(self) -> aws_cdk.core.Stack:
        return typing.cast(aws_cdk.core.Stack, jsii.get(self, "edgeStack"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stack")
    def _stack(self) -> aws_cdk.core.Stack:
        return typing.cast(aws_cdk.core.Stack, jsii.get(self, "stack"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.CommonEdgeFunctionProps",
    jsii_struct_bases=[],
    name_mapping={"edge_role": "edgeRole", "parameter_name": "parameterName"},
)
class CommonEdgeFunctionProps:
    def __init__(
        self,
        *,
        edge_role: typing.Optional["IEdgeRole"] = None,
        parameter_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param edge_role: -
        :param parameter_name: The name of the parameter.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if edge_role is not None:
            self._values["edge_role"] = edge_role
        if parameter_name is not None:
            self._values["parameter_name"] = parameter_name

    @builtins.property
    def edge_role(self) -> typing.Optional["IEdgeRole"]:
        result = self._values.get("edge_role")
        return typing.cast(typing.Optional["IEdgeRole"], result)

    @builtins.property
    def parameter_name(self) -> typing.Optional[builtins.str]:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonEdgeFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.Configuration",
    jsii_struct_bases=[],
    name_mapping={"log_level": "logLevel"},
)
class Configuration:
    def __init__(self, *, log_level: "LogLevel") -> None:
        '''
        :param log_level: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_level": log_level,
        }

    @builtins.property
    def log_level(self) -> "LogLevel":
        result = self._values.get("log_level")
        assert result is not None, "Required property 'log_level' is missing"
        return typing.cast("LogLevel", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.EdgeFunctionProps",
    jsii_struct_bases=[CommonEdgeFunctionProps],
    name_mapping={
        "edge_role": "edgeRole",
        "parameter_name": "parameterName",
        "code": "code",
        "configuration": "configuration",
        "event_type": "eventType",
        "name": "name",
    },
)
class EdgeFunctionProps(CommonEdgeFunctionProps):
    def __init__(
        self,
        *,
        edge_role: typing.Optional["IEdgeRole"] = None,
        parameter_name: typing.Optional[builtins.str] = None,
        code: aws_cdk.aws_lambda.Code,
        configuration: Configuration,
        event_type: aws_cdk.aws_cloudfront.LambdaEdgeEventType,
        name: builtins.str,
    ) -> None:
        '''
        :param edge_role: -
        :param parameter_name: The name of the parameter.
        :param code: -
        :param configuration: -
        :param event_type: -
        :param name: -
        '''
        if isinstance(configuration, dict):
            configuration = Configuration(**configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "configuration": configuration,
            "event_type": event_type,
            "name": name,
        }
        if edge_role is not None:
            self._values["edge_role"] = edge_role
        if parameter_name is not None:
            self._values["parameter_name"] = parameter_name

    @builtins.property
    def edge_role(self) -> typing.Optional["IEdgeRole"]:
        result = self._values.get("edge_role")
        return typing.cast(typing.Optional["IEdgeRole"], result)

    @builtins.property
    def parameter_name(self) -> typing.Optional[builtins.str]:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code(self) -> aws_cdk.aws_lambda.Code:
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(aws_cdk.aws_lambda.Code, result)

    @builtins.property
    def configuration(self) -> Configuration:
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(Configuration, result)

    @builtins.property
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EdgeFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.EdgeRoleProps",
    jsii_struct_bases=[],
    name_mapping={"role_name": "roleName"},
)
class EdgeRoleProps:
    def __init__(self, *, role_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param role_name: -
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EdgeRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.HttpHeadersProps",
    jsii_struct_bases=[CommonEdgeFunctionProps],
    name_mapping={
        "edge_role": "edgeRole",
        "parameter_name": "parameterName",
        "http_headers": "httpHeaders",
        "log_level": "logLevel",
    },
)
class HttpHeadersProps(CommonEdgeFunctionProps):
    def __init__(
        self,
        *,
        edge_role: typing.Optional["IEdgeRole"] = None,
        parameter_name: typing.Optional[builtins.str] = None,
        http_headers: typing.Mapping[builtins.str, builtins.str],
        log_level: typing.Optional["LogLevel"] = None,
    ) -> None:
        '''
        :param edge_role: -
        :param parameter_name: The name of the parameter.
        :param http_headers: -
        :param log_level: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "http_headers": http_headers,
        }
        if edge_role is not None:
            self._values["edge_role"] = edge_role
        if parameter_name is not None:
            self._values["parameter_name"] = parameter_name
        if log_level is not None:
            self._values["log_level"] = log_level

    @builtins.property
    def edge_role(self) -> typing.Optional["IEdgeRole"]:
        result = self._values.get("edge_role")
        return typing.cast(typing.Optional["IEdgeRole"], result)

    @builtins.property
    def parameter_name(self) -> typing.Optional[builtins.str]:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        result = self._values.get("http_headers")
        assert result is not None, "Required property 'http_headers' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional["LogLevel"]:
        result = self._values.get("log_level")
        return typing.cast(typing.Optional["LogLevel"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpHeadersProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.IEdgeLambda")
class IEdgeLambda(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.IVersion:
        ...


class _IEdgeLambdaProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-lambda-at-edge-pattern.IEdgeLambda"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.IVersion:
        return typing.cast(aws_cdk.aws_lambda.IVersion, jsii.get(self, "functionVersion"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEdgeLambda).__jsii_proxy_class__ = lambda : _IEdgeLambdaProxy


@jsii.interface(jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.IEdgeRole")
class IEdgeRole(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        ...

    @jsii.member(jsii_name="addToEdgeRolePolicy")
    def add_to_edge_role_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> None:
        '''
        :param statement: -
        '''
        ...


class _IEdgeRoleProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-lambda-at-edge-pattern.IEdgeRole"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))

    @jsii.member(jsii_name="addToEdgeRolePolicy")
    def add_to_edge_role_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> None:
        '''
        :param statement: -
        '''
        return typing.cast(None, jsii.invoke(self, "addToEdgeRolePolicy", [statement]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEdgeRole).__jsii_proxy_class__ = lambda : _IEdgeRoleProxy


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.ILambdaFunctionAssociation"
)
class ILambdaFunctionAssociation(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IVersion:
        ...


class _ILambdaFunctionAssociationProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-lambda-at-edge-pattern.ILambdaFunctionAssociation"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IVersion:
        return typing.cast(aws_cdk.aws_lambda.IVersion, jsii.get(self, "lambdaFunction"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILambdaFunctionAssociation).__jsii_proxy_class__ = lambda : _ILambdaFunctionAssociationProxy


@jsii.enum(jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.LogLevel")
class LogLevel(enum.Enum):
    NONE = "NONE"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class WithConfiguration(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.WithConfiguration",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        configuration: Configuration,
        function: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param configuration: -
        :param function: -
        '''
        props = WithConfigurationProps(configuration=configuration, function=function)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.IVersion:
        return typing.cast(aws_cdk.aws_lambda.IVersion, jsii.get(self, "functionVersion"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.WithConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={"configuration": "configuration", "function": "function"},
)
class WithConfigurationProps:
    def __init__(
        self,
        *,
        configuration: Configuration,
        function: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''
        :param configuration: -
        :param function: -
        '''
        if isinstance(configuration, dict):
            configuration = Configuration(**configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "configuration": configuration,
            "function": function,
        }

    @builtins.property
    def configuration(self) -> Configuration:
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(Configuration, result)

    @builtins.property
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WithConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ILambdaFunctionAssociation, IEdgeLambda)
class EdgeFunction(
    BaseEdgeConstruct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.EdgeFunction",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        code: aws_cdk.aws_lambda.Code,
        configuration: Configuration,
        event_type: aws_cdk.aws_cloudfront.LambdaEdgeEventType,
        name: builtins.str,
        edge_role: typing.Optional[IEdgeRole] = None,
        parameter_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: -
        :param configuration: -
        :param event_type: -
        :param name: -
        :param edge_role: -
        :param parameter_name: The name of the parameter.
        '''
        props = EdgeFunctionProps(
            code=code,
            configuration=configuration,
            event_type=event_type,
            name=name,
            edge_role=edge_role,
            parameter_name=parameter_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="edgeRole")
    def edge_role(self) -> IEdgeRole:
        return typing.cast(IEdgeRole, jsii.get(self, "edgeRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> aws_cdk.aws_cloudfront.LambdaEdgeEventType:
        return typing.cast(aws_cdk.aws_cloudfront.LambdaEdgeEventType, jsii.get(self, "eventType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> aws_cdk.aws_lambda.IVersion:
        return typing.cast(aws_cdk.aws_lambda.IVersion, jsii.get(self, "functionVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IVersion:
        return typing.cast(aws_cdk.aws_lambda.IVersion, jsii.get(self, "lambdaFunction"))


@jsii.implements(IEdgeRole)
class EdgeRole(
    BaseEdgeConstruct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.EdgeRole",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param role_name: -
        '''
        props = EdgeRoleProps(role_name=role_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToEdgeRolePolicy")
    def add_to_edge_role_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> None:
        '''
        :param statement: -
        '''
        return typing.cast(None, jsii.invoke(self, "addToEdgeRolePolicy", [statement]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))


class HttpHeaders(
    EdgeFunction,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-lambda-at-edge-pattern.HttpHeaders",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        http_headers: typing.Mapping[builtins.str, builtins.str],
        log_level: typing.Optional[LogLevel] = None,
        edge_role: typing.Optional[IEdgeRole] = None,
        parameter_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param http_headers: -
        :param log_level: -
        :param edge_role: -
        :param parameter_name: The name of the parameter.
        '''
        props = HttpHeadersProps(
            http_headers=http_headers,
            log_level=log_level,
            edge_role=edge_role,
            parameter_name=parameter_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "BaseEdgeConstruct",
    "CommonEdgeFunctionProps",
    "Configuration",
    "EdgeFunction",
    "EdgeFunctionProps",
    "EdgeRole",
    "EdgeRoleProps",
    "HttpHeaders",
    "HttpHeadersProps",
    "IEdgeLambda",
    "IEdgeRole",
    "ILambdaFunctionAssociation",
    "LogLevel",
    "WithConfiguration",
    "WithConfigurationProps",
]

publication.publish()
