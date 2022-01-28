'''
# cdk-renovo-instance-service

[![build](https://github.com/RenovoSolutions/cdk-library-renovo-instance-service/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-renovo-instance-service/actions/workflows/build.yml)
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
import aws_cdk.aws_iam
import constructs
import managed_instance_role


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.AmiLookup",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "owners": "owners", "windows": "windows"},
)
class AmiLookup:
    def __init__(
        self,
        *,
        name: builtins.str,
        owners: typing.Optional[typing.Sequence[builtins.str]] = None,
        windows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param name: The name string to use for AMI lookup.
        :param owners: The owners to use for AMI lookup.
        :param windows: Is this AMI expected to be windows?
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if owners is not None:
            self._values["owners"] = owners
        if windows is not None:
            self._values["windows"] = windows

    @builtins.property
    def name(self) -> builtins.str:
        '''The name string to use for AMI lookup.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def owners(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The owners to use for AMI lookup.'''
        result = self._values.get("owners")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def windows(self) -> typing.Optional[builtins.bool]:
        '''Is this AMI expected to be windows?'''
        result = self._values.get("windows")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmiLookup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstanceService(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.InstanceService",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ami: aws_cdk.aws_ec2.IMachineImage,
        name: builtins.str,
        vpc: aws_cdk.aws_ec2.Vpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
        enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
        enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
        enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ami: The Amazon Machine Image (AMI) to launch the target instance with.
        :param name: The name of the service this instance service will host.
        :param vpc: The VPC to launch this service in.
        :param allow_all_outbound: Allow all outbound traffic for the instances security group. Default: true
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization for the instances security group. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param enable_cloudwatch_logs: Whether or not to enable logging to Cloudwatch Logs. Default: true
        :param enabled_no_public_ingress_aspect: Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0. If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        :param enable_no_db_ports_aspect: Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param enable_no_remote_management_ports_aspect: Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param subnet_type: The subnet type to launch this service in. Default: ec2.SubnetType.PRIVATE
        '''
        props = InstanceServiceProps(
            ami=ami,
            name=name,
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            disable_inline_rules=disable_inline_rules,
            enable_cloudwatch_logs=enable_cloudwatch_logs,
            enabled_no_public_ingress_aspect=enabled_no_public_ingress_aspect,
            enable_no_db_ports_aspect=enable_no_db_ports_aspect,
            enable_no_remote_management_ports_aspect=enable_no_remote_management_ports_aspect,
            subnet_type=subnet_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> managed_instance_role.ManagedInstanceRole:
        return typing.cast(managed_instance_role.ManagedInstanceRole, jsii.get(self, "instanceProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, jsii.get(self, "securityGroup"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.InstanceServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "ami": "ami",
        "name": "name",
        "vpc": "vpc",
        "allow_all_outbound": "allowAllOutbound",
        "disable_inline_rules": "disableInlineRules",
        "enable_cloudwatch_logs": "enableCloudwatchLogs",
        "enabled_no_public_ingress_aspect": "enabledNoPublicIngressAspect",
        "enable_no_db_ports_aspect": "enableNoDBPortsAspect",
        "enable_no_remote_management_ports_aspect": "enableNoRemoteManagementPortsAspect",
        "subnet_type": "subnetType",
    },
)
class InstanceServiceProps:
    def __init__(
        self,
        *,
        ami: aws_cdk.aws_ec2.IMachineImage,
        name: builtins.str,
        vpc: aws_cdk.aws_ec2.Vpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
        enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
        enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
        enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
    ) -> None:
        '''
        :param ami: The Amazon Machine Image (AMI) to launch the target instance with.
        :param name: The name of the service this instance service will host.
        :param vpc: The VPC to launch this service in.
        :param allow_all_outbound: Allow all outbound traffic for the instances security group. Default: true
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization for the instances security group. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param enable_cloudwatch_logs: Whether or not to enable logging to Cloudwatch Logs. Default: true
        :param enabled_no_public_ingress_aspect: Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0. If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        :param enable_no_db_ports_aspect: Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param enable_no_remote_management_ports_aspect: Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param subnet_type: The subnet type to launch this service in. Default: ec2.SubnetType.PRIVATE
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ami": ami,
            "name": name,
            "vpc": vpc,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if disable_inline_rules is not None:
            self._values["disable_inline_rules"] = disable_inline_rules
        if enable_cloudwatch_logs is not None:
            self._values["enable_cloudwatch_logs"] = enable_cloudwatch_logs
        if enabled_no_public_ingress_aspect is not None:
            self._values["enabled_no_public_ingress_aspect"] = enabled_no_public_ingress_aspect
        if enable_no_db_ports_aspect is not None:
            self._values["enable_no_db_ports_aspect"] = enable_no_db_ports_aspect
        if enable_no_remote_management_ports_aspect is not None:
            self._values["enable_no_remote_management_ports_aspect"] = enable_no_remote_management_ports_aspect
        if subnet_type is not None:
            self._values["subnet_type"] = subnet_type

    @builtins.property
    def ami(self) -> aws_cdk.aws_ec2.IMachineImage:
        '''The Amazon Machine Image (AMI) to launch the target instance with.'''
        result = self._values.get("ami")
        assert result is not None, "Required property 'ami' is missing"
        return typing.cast(aws_cdk.aws_ec2.IMachineImage, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the service this instance service will host.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.Vpc:
        '''The VPC to launch this service in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.Vpc, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Allow all outbound traffic for the instances security group.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_inline_rules(self) -> typing.Optional[builtins.bool]:
        '''Whether to disable inline ingress and egress rule optimization for the instances security group.

        If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements.

        Inlining rules is an optimization for producing smaller stack templates.
        Sometimes this is not desirable, for example when security group access is managed via tags.

        The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'.

        :default: false
        '''
        result = self._values.get("disable_inline_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_cloudwatch_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable logging to Cloudwatch Logs.

        :default: true
        '''
        result = self._values.get("enable_cloudwatch_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enabled_no_public_ingress_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0.

        If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        '''
        result = self._values.get("enabled_no_public_ingress_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_no_db_ports_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server.

        If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail.

        :default: true
        '''
        result = self._values.get("enable_no_db_ports_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_no_remote_management_ports_aspect(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs.

        If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail.

        :default: true
        '''
        result = self._values.get("enable_no_remote_management_ports_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_type(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetType]:
        '''The subnet type to launch this service in.

        :default: ec2.SubnetType.PRIVATE
        '''
        result = self._values.get("subnet_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedLoggingPolicy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.ManagedLoggingPolicy",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        os: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param os: The OS of the instance this policy is for.
        '''
        props = ManagedLoggingPolicyProps(os=os)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> aws_cdk.aws_iam.ManagedPolicy:
        return typing.cast(aws_cdk.aws_iam.ManagedPolicy, jsii.get(self, "policy"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.ManagedLoggingPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"os": "os"},
)
class ManagedLoggingPolicyProps:
    def __init__(self, *, os: builtins.str) -> None:
        '''
        :param os: The OS of the instance this policy is for.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "os": os,
        }

    @builtins.property
    def os(self) -> builtins.str:
        '''The OS of the instance this policy is for.'''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedLoggingPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AmiLookup",
    "InstanceService",
    "InstanceServiceProps",
    "ManagedLoggingPolicy",
    "ManagedLoggingPolicyProps",
]

publication.publish()
