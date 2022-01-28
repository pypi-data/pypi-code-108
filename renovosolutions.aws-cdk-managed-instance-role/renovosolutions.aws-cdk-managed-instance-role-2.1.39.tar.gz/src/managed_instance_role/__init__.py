'''
# cdk-library-managed-instance-role

[![build](https://github.com/RenovoSolutions/cdk-library-managed-instance-role/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-managed-instance-role/workflows/build.yml)

This CDK Construct Library includes a construct (`ManagedInstanceRole`) which creates an AWS instance profile. By default this instance profile includes the basic policies required for instance management in SSM and the ability to Domain Join the instance.

The purpose of this CDK Construct Library is to ease the creation of instance roles by not needing to code the inclusion of baseline management roles for evey single different role implementation every time. Instance profiles only support a single role so its important the role includes all required access. This construct allows making additions to those baseline policies with ease.

The construct defines an interface (`IManagedInstanceRoleProps`) to configure the managed policies of the role as well as manage the inclusion of the default roles.

## Dev

### Pre-reqs:

You will need

* npm installed on your machine
* AWS CDK installed on your machine
* python installed on your machine
* dotnet installed on your machine
* a github account

This project is managed with `projen`. Modify the `.projenrc.js` file and run `npx projen`. You can also modify this `README` file and the `src` code directory as needed. Github actions take care of publishing utilizing the automatically created workflows from `projen`.
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

import aws_cdk.aws_iam
import constructs


class ManagedInstanceRole(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-managed-instance-role.ManagedInstanceRole",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain_join_enabled: typing.Optional[builtins.bool] = None,
        managed_policies: typing.Optional[typing.Sequence[aws_cdk.aws_iam.ManagedPolicy]] = None,
        ssm_management_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_join_enabled: Should the role include directory service access with SSM.
        :param managed_policies: The managed policies to apply to the role in addition to the default policies.
        :param ssm_management_enabled: Should the role include SSM management. By default if domainJoinEnabled is true then this role is always included.
        '''
        props = ManagedInstanceRoleProps(
            domain_join_enabled=domain_join_enabled,
            managed_policies=managed_policies,
            ssm_management_enabled=ssm_management_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> aws_cdk.aws_iam.CfnInstanceProfile:
        return typing.cast(aws_cdk.aws_iam.CfnInstanceProfile, jsii.get(self, "instanceProfile"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-managed-instance-role.ManagedInstanceRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_join_enabled": "domainJoinEnabled",
        "managed_policies": "managedPolicies",
        "ssm_management_enabled": "ssmManagementEnabled",
    },
)
class ManagedInstanceRoleProps:
    def __init__(
        self,
        *,
        domain_join_enabled: typing.Optional[builtins.bool] = None,
        managed_policies: typing.Optional[typing.Sequence[aws_cdk.aws_iam.ManagedPolicy]] = None,
        ssm_management_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param domain_join_enabled: Should the role include directory service access with SSM.
        :param managed_policies: The managed policies to apply to the role in addition to the default policies.
        :param ssm_management_enabled: Should the role include SSM management. By default if domainJoinEnabled is true then this role is always included.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if domain_join_enabled is not None:
            self._values["domain_join_enabled"] = domain_join_enabled
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if ssm_management_enabled is not None:
            self._values["ssm_management_enabled"] = ssm_management_enabled

    @builtins.property
    def domain_join_enabled(self) -> typing.Optional[builtins.bool]:
        '''Should the role include directory service access with SSM.'''
        result = self._values.get("domain_join_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.ManagedPolicy]]:
        '''The managed policies to apply to the role in addition to the default policies.'''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.ManagedPolicy]], result)

    @builtins.property
    def ssm_management_enabled(self) -> typing.Optional[builtins.bool]:
        '''Should the role include SSM management.

        By default if domainJoinEnabled is true then this role is always included.
        '''
        result = self._values.get("ssm_management_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ManagedInstanceRole",
    "ManagedInstanceRoleProps",
]

publication.publish()
