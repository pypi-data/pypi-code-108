'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-security-group?style=flat-square)](https://github.com/pepperize/cdk-security-group/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-security-group?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-security-group)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-security-group?style=flat-square)](https://pypi.org/project/pepperize.cdk-security-group/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.SecurityGroup?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.SecurityGroup/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-security-group/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-security-group/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-security-group?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-security-group/releases)

# AWS CDK SecurityGroup

This project provides a CDK construct to create an EC2 SecurityGroup, which property `securityGroupName` returns the
GroupName.

> The [CDK EC2 SecurityGroup](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ec2.SecurityGroup.html)
> returns the GroupId from the `Ref` return value of [AWS::EC2::SecurityGroup](https://docs.aws.amazon.com/de_de/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html),
> rather than the GroupName.

## Install

### TypeScript

```shell
npm install @pepperize/cdk-security-group
```

or

```shell
yarn add @pepperize/cdk-security-group
```

### Python

```shell
pip install pepperize.cdk-security-group
```

### C# / .Net

```
dotnet add package Pepperize.CDK.SecurityGroup
```

## Example

```shell
npm install @pepperize/cdk-security-group
```

See [API.md](https://github.com/pepperize/cdk-security-group/blob/main/API.md).

```python
import { SecurityGroup } from "@pepperize/cdk-security-group";

const securityGroup = new SecurityGroup(this, "SecurityGroup", {});

// Pass to another construct
new OtherConstruct(this, OtherConstruct, {
  SecurityGroupName: securityGroup.securityGroupName,
});
```
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
import constructs


class SecurityGroup(
    aws_cdk.aws_ec2.SecurityGroup,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-security-group.SecurityGroup",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC in which to create the security group.
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. Default: true
        :param description: A description of the security group. Default: The default name will be the construct's CDK path.
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param security_group_name: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.
        '''
        props = SecurityGroupProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            description=description,
            disable_inline_rules=disable_inline_rules,
            security_group_name=security_group_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupName")
    def security_group_name(self) -> builtins.str:
        '''An attribute that represents the security group name.'''
        return typing.cast(builtins.str, jsii.get(self, "securityGroupName"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-security-group.SecurityGroupProps",
    jsii_struct_bases=[aws_cdk.aws_ec2.SecurityGroupProps],
    name_mapping={
        "vpc": "vpc",
        "allow_all_outbound": "allowAllOutbound",
        "description": "description",
        "disable_inline_rules": "disableInlineRules",
        "security_group_name": "securityGroupName",
    },
)
class SecurityGroupProps(aws_cdk.aws_ec2.SecurityGroupProps):
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param vpc: The VPC in which to create the security group.
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. Default: true
        :param description: A description of the security group. Default: The default name will be the construct's CDK path.
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param security_group_name: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if description is not None:
            self._values["description"] = description
        if disable_inline_rules is not None:
            self._values["disable_inline_rules"] = disable_inline_rules
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC in which to create the security group.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow all outbound traffic by default.

        If this is set to true, there will only be a single egress rule which allows all
        outbound traffic. If this is set to false, no outbound traffic will be allowed by
        default and all egress traffic must be explicitly authorized.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the security group.

        :default: The default name will be the construct's CDK path.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_inline_rules(self) -> typing.Optional[builtins.bool]:
        '''Whether to disable inline ingress and egress rule optimization.

        If this is set to true, ingress and egress rules will not be declared under the
        SecurityGroup in cloudformation, but will be separate elements.

        Inlining rules is an optimization for producing smaller stack templates. Sometimes
        this is not desirable, for example when security group access is managed via tags.

        The default value can be overriden globally by setting the context variable
        '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'.

        :default: false
        '''
        result = self._values.get("disable_inline_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''The name of the security group.

        For valid values, see the GroupName
        parameter of the CreateSecurityGroup action in the Amazon EC2 API
        Reference.

        It is not recommended to use an explicit group name.

        :default:

        If you don't specify a GroupName, AWS CloudFormation generates a
        unique physical ID and uses that ID for the group name.
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecurityGroup",
    "SecurityGroupProps",
]

publication.publish()
