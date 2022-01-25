import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class DataAwsTransferServer(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.DataAwsTransferServer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/transfer_server aws_transfer_server}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        server_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/transfer_server aws_transfer_server} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#server_id DataAwsTransferServer#server_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsTransferServerConfig(
            server_id=server_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderType")
    def identity_provider_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invocationRole")
    def invocation_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invocationRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingRole")
    def logging_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loggingRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocols"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyName")
    def security_policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicyName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        jsii.set(self, "serverId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.DataAwsTransferServerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "server_id": "serverId",
    },
)
class DataAwsTransferServerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        server_id: builtins.str,
    ) -> None:
        '''AWS Transfer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#server_id DataAwsTransferServer#server_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "server_id": server_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/transfer_server#server_id DataAwsTransferServer#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsTransferServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferAccess(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferAccess",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_access aws_transfer_access}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        external_id: builtins.str,
        server_id: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Sequence["TransferAccessHomeDirectoryMappings"]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional["TransferAccessPosixProfile"] = None,
        role: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_access aws_transfer_access} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#external_id TransferAccess#external_id}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#server_id TransferAccess#server_id}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory TransferAccess#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_mappings TransferAccess#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_type TransferAccess#home_directory_type}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#policy TransferAccess#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#posix_profile TransferAccess#posix_profile}
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#role TransferAccess#role}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TransferAccessConfig(
            external_id=external_id,
            server_id=server_id,
            home_directory=home_directory,
            home_directory_mappings=home_directory_mappings,
            home_directory_type=home_directory_type,
            policy=policy,
            posix_profile=posix_profile,
            role=role,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putPosixProfile")
    def put_posix_profile(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#gid TransferAccess#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#uid TransferAccess#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#secondary_gids TransferAccess#secondary_gids}.
        '''
        value = TransferAccessPosixProfile(
            gid=gid, uid=uid, secondary_gids=secondary_gids
        )

        return typing.cast(None, jsii.invoke(self, "putPosixProfile", [value]))

    @jsii.member(jsii_name="resetHomeDirectory")
    def reset_home_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectory", []))

    @jsii.member(jsii_name="resetHomeDirectoryMappings")
    def reset_home_directory_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryMappings", []))

    @jsii.member(jsii_name="resetHomeDirectoryType")
    def reset_home_directory_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryType", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetPosixProfile")
    def reset_posix_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosixProfile", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfile")
    def posix_profile(self) -> "TransferAccessPosixProfileOutputReference":
        return typing.cast("TransferAccessPosixProfileOutputReference", jsii.get(self, "posixProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryInput")
    def home_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappingsInput")
    def home_directory_mappings_input(
        self,
    ) -> typing.Optional[typing.List["TransferAccessHomeDirectoryMappings"]]:
        return typing.cast(typing.Optional[typing.List["TransferAccessHomeDirectoryMappings"]], jsii.get(self, "homeDirectoryMappingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryTypeInput")
    def home_directory_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfileInput")
    def posix_profile_input(self) -> typing.Optional["TransferAccessPosixProfile"]:
        return typing.cast(typing.Optional["TransferAccessPosixProfile"], jsii.get(self, "posixProfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        jsii.set(self, "externalId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectory")
    def home_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectory"))

    @home_directory.setter
    def home_directory(self, value: builtins.str) -> None:
        jsii.set(self, "homeDirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappings")
    def home_directory_mappings(
        self,
    ) -> typing.List["TransferAccessHomeDirectoryMappings"]:
        return typing.cast(typing.List["TransferAccessHomeDirectoryMappings"], jsii.get(self, "homeDirectoryMappings"))

    @home_directory_mappings.setter
    def home_directory_mappings(
        self,
        value: typing.List["TransferAccessHomeDirectoryMappings"],
    ) -> None:
        jsii.set(self, "homeDirectoryMappings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryType")
    def home_directory_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectoryType"))

    @home_directory_type.setter
    def home_directory_type(self, value: builtins.str) -> None:
        jsii.set(self, "homeDirectoryType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        jsii.set(self, "serverId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "external_id": "externalId",
        "server_id": "serverId",
        "home_directory": "homeDirectory",
        "home_directory_mappings": "homeDirectoryMappings",
        "home_directory_type": "homeDirectoryType",
        "policy": "policy",
        "posix_profile": "posixProfile",
        "role": "role",
    },
)
class TransferAccessConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        external_id: builtins.str,
        server_id: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Sequence["TransferAccessHomeDirectoryMappings"]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional["TransferAccessPosixProfile"] = None,
        role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Transfer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#external_id TransferAccess#external_id}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#server_id TransferAccess#server_id}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory TransferAccess#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_mappings TransferAccess#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_type TransferAccess#home_directory_type}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#policy TransferAccess#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#posix_profile TransferAccess#posix_profile}
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#role TransferAccess#role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(posix_profile, dict):
            posix_profile = TransferAccessPosixProfile(**posix_profile)
        self._values: typing.Dict[str, typing.Any] = {
            "external_id": external_id,
            "server_id": server_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if home_directory is not None:
            self._values["home_directory"] = home_directory
        if home_directory_mappings is not None:
            self._values["home_directory_mappings"] = home_directory_mappings
        if home_directory_type is not None:
            self._values["home_directory_type"] = home_directory_type
        if policy is not None:
            self._values["policy"] = policy
        if posix_profile is not None:
            self._values["posix_profile"] = posix_profile
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def external_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#external_id TransferAccess#external_id}.'''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#server_id TransferAccess#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def home_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory TransferAccess#home_directory}.'''
        result = self._values.get("home_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def home_directory_mappings(
        self,
    ) -> typing.Optional[typing.List["TransferAccessHomeDirectoryMappings"]]:
        '''home_directory_mappings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_mappings TransferAccess#home_directory_mappings}
        '''
        result = self._values.get("home_directory_mappings")
        return typing.cast(typing.Optional[typing.List["TransferAccessHomeDirectoryMappings"]], result)

    @builtins.property
    def home_directory_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#home_directory_type TransferAccess#home_directory_type}.'''
        result = self._values.get("home_directory_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#policy TransferAccess#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_profile(self) -> typing.Optional["TransferAccessPosixProfile"]:
        '''posix_profile block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#posix_profile TransferAccess#posix_profile}
        '''
        result = self._values.get("posix_profile")
        return typing.cast(typing.Optional["TransferAccessPosixProfile"], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#role TransferAccess#role}.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferAccessConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessHomeDirectoryMappings",
    jsii_struct_bases=[],
    name_mapping={"entry": "entry", "target": "target"},
)
class TransferAccessHomeDirectoryMappings:
    def __init__(self, *, entry: builtins.str, target: builtins.str) -> None:
        '''
        :param entry: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#entry TransferAccess#entry}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#target TransferAccess#target}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "entry": entry,
            "target": target,
        }

    @builtins.property
    def entry(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#entry TransferAccess#entry}.'''
        result = self._values.get("entry")
        assert result is not None, "Required property 'entry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#target TransferAccess#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferAccessHomeDirectoryMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessPosixProfile",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
)
class TransferAccessPosixProfile:
    def __init__(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#gid TransferAccess#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#uid TransferAccess#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#secondary_gids TransferAccess#secondary_gids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "gid": gid,
            "uid": uid,
        }
        if secondary_gids is not None:
            self._values["secondary_gids"] = secondary_gids

    @builtins.property
    def gid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#gid TransferAccess#gid}.'''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def uid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#uid TransferAccess#uid}.'''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def secondary_gids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_access#secondary_gids TransferAccess#secondary_gids}.'''
        result = self._values.get("secondary_gids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferAccessPosixProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferAccessPosixProfileOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferAccessPosixProfileOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetSecondaryGids")
    def reset_secondary_gids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryGids", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gidInput")
    def gid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGidsInput")
    def secondary_gids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "secondaryGidsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "uidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gid")
    def gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gid"))

    @gid.setter
    def gid(self, value: jsii.Number) -> None:
        jsii.set(self, "gid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGids")
    def secondary_gids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "secondaryGids"))

    @secondary_gids.setter
    def secondary_gids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "secondaryGids", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: jsii.Number) -> None:
        jsii.set(self, "uid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferAccessPosixProfile]:
        return typing.cast(typing.Optional[TransferAccessPosixProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferAccessPosixProfile],
    ) -> None:
        jsii.set(self, "internalValue", value)


class TransferServer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferServer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_server aws_transfer_server}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certificate: typing.Optional[builtins.str] = None,
        directory_id: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        endpoint_details: typing.Optional["TransferServerEndpointDetails"] = None,
        endpoint_type: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        function: typing.Optional[builtins.str] = None,
        host_key: typing.Optional[builtins.str] = None,
        identity_provider_type: typing.Optional[builtins.str] = None,
        invocation_role: typing.Optional[builtins.str] = None,
        logging_role: typing.Optional[builtins.str] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_policy_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        url: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_server aws_transfer_server} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#certificate TransferServer#certificate}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#directory_id TransferServer#directory_id}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#domain TransferServer#domain}.
        :param endpoint_details: endpoint_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_details TransferServer#endpoint_details}
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_type TransferServer#endpoint_type}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#force_destroy TransferServer#force_destroy}.
        :param function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#function TransferServer#function}.
        :param host_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#host_key TransferServer#host_key}.
        :param identity_provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#identity_provider_type TransferServer#identity_provider_type}.
        :param invocation_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#invocation_role TransferServer#invocation_role}.
        :param logging_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#logging_role TransferServer#logging_role}.
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#protocols TransferServer#protocols}.
        :param security_policy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_policy_name TransferServer#security_policy_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags TransferServer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags_all TransferServer#tags_all}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#url TransferServer#url}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TransferServerConfig(
            certificate=certificate,
            directory_id=directory_id,
            domain=domain,
            endpoint_details=endpoint_details,
            endpoint_type=endpoint_type,
            force_destroy=force_destroy,
            function=function,
            host_key=host_key,
            identity_provider_type=identity_provider_type,
            invocation_role=invocation_role,
            logging_role=logging_role,
            protocols=protocols,
            security_policy_name=security_policy_name,
            tags=tags,
            tags_all=tags_all,
            url=url,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEndpointDetails")
    def put_endpoint_details(
        self,
        *,
        address_allocation_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address_allocation_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#address_allocation_ids TransferServer#address_allocation_ids}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_group_ids TransferServer#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#subnet_ids TransferServer#subnet_ids}.
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_endpoint_id TransferServer#vpc_endpoint_id}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_id TransferServer#vpc_id}.
        '''
        value = TransferServerEndpointDetails(
            address_allocation_ids=address_allocation_ids,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            vpc_endpoint_id=vpc_endpoint_id,
            vpc_id=vpc_id,
        )

        return typing.cast(None, jsii.invoke(self, "putEndpointDetails", [value]))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetDirectoryId")
    def reset_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryId", []))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetEndpointDetails")
    def reset_endpoint_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointDetails", []))

    @jsii.member(jsii_name="resetEndpointType")
    def reset_endpoint_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointType", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetFunction")
    def reset_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunction", []))

    @jsii.member(jsii_name="resetHostKey")
    def reset_host_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostKey", []))

    @jsii.member(jsii_name="resetIdentityProviderType")
    def reset_identity_provider_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityProviderType", []))

    @jsii.member(jsii_name="resetInvocationRole")
    def reset_invocation_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvocationRole", []))

    @jsii.member(jsii_name="resetLoggingRole")
    def reset_logging_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingRole", []))

    @jsii.member(jsii_name="resetProtocols")
    def reset_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocols", []))

    @jsii.member(jsii_name="resetSecurityPolicyName")
    def reset_security_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityPolicyName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointDetails")
    def endpoint_details(self) -> "TransferServerEndpointDetailsOutputReference":
        return typing.cast("TransferServerEndpointDetailsOutputReference", jsii.get(self, "endpointDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostKeyFingerprint")
    def host_key_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostKeyFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointDetailsInput")
    def endpoint_details_input(
        self,
    ) -> typing.Optional["TransferServerEndpointDetails"]:
        return typing.cast(typing.Optional["TransferServerEndpointDetails"], jsii.get(self, "endpointDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointTypeInput")
    def endpoint_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionInput")
    def function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostKeyInput")
    def host_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderTypeInput")
    def identity_provider_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invocationRoleInput")
    def invocation_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "invocationRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingRoleInput")
    def logging_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggingRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolsInput")
    def protocols_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "protocolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyNameInput")
    def security_policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityPolicyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        jsii.set(self, "certificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @endpoint_type.setter
    def endpoint_type(self, value: builtins.str) -> None:
        jsii.set(self, "endpointType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "function"))

    @function.setter
    def function(self, value: builtins.str) -> None:
        jsii.set(self, "function", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostKey")
    def host_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostKey"))

    @host_key.setter
    def host_key(self, value: builtins.str) -> None:
        jsii.set(self, "hostKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderType")
    def identity_provider_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderType"))

    @identity_provider_type.setter
    def identity_provider_type(self, value: builtins.str) -> None:
        jsii.set(self, "identityProviderType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invocationRole")
    def invocation_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invocationRole"))

    @invocation_role.setter
    def invocation_role(self, value: builtins.str) -> None:
        jsii.set(self, "invocationRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingRole")
    def logging_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loggingRole"))

    @logging_role.setter
    def logging_role(self, value: builtins.str) -> None:
        jsii.set(self, "loggingRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocols"))

    @protocols.setter
    def protocols(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "protocols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityPolicyName")
    def security_policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityPolicyName"))

    @security_policy_name.setter
    def security_policy_name(self, value: builtins.str) -> None:
        jsii.set(self, "securityPolicyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferServerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "certificate": "certificate",
        "directory_id": "directoryId",
        "domain": "domain",
        "endpoint_details": "endpointDetails",
        "endpoint_type": "endpointType",
        "force_destroy": "forceDestroy",
        "function": "function",
        "host_key": "hostKey",
        "identity_provider_type": "identityProviderType",
        "invocation_role": "invocationRole",
        "logging_role": "loggingRole",
        "protocols": "protocols",
        "security_policy_name": "securityPolicyName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "url": "url",
    },
)
class TransferServerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        certificate: typing.Optional[builtins.str] = None,
        directory_id: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        endpoint_details: typing.Optional["TransferServerEndpointDetails"] = None,
        endpoint_type: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        function: typing.Optional[builtins.str] = None,
        host_key: typing.Optional[builtins.str] = None,
        identity_provider_type: typing.Optional[builtins.str] = None,
        invocation_role: typing.Optional[builtins.str] = None,
        logging_role: typing.Optional[builtins.str] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_policy_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Transfer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#certificate TransferServer#certificate}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#directory_id TransferServer#directory_id}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#domain TransferServer#domain}.
        :param endpoint_details: endpoint_details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_details TransferServer#endpoint_details}
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_type TransferServer#endpoint_type}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#force_destroy TransferServer#force_destroy}.
        :param function: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#function TransferServer#function}.
        :param host_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#host_key TransferServer#host_key}.
        :param identity_provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#identity_provider_type TransferServer#identity_provider_type}.
        :param invocation_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#invocation_role TransferServer#invocation_role}.
        :param logging_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#logging_role TransferServer#logging_role}.
        :param protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#protocols TransferServer#protocols}.
        :param security_policy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_policy_name TransferServer#security_policy_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags TransferServer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags_all TransferServer#tags_all}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#url TransferServer#url}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(endpoint_details, dict):
            endpoint_details = TransferServerEndpointDetails(**endpoint_details)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if certificate is not None:
            self._values["certificate"] = certificate
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if domain is not None:
            self._values["domain"] = domain
        if endpoint_details is not None:
            self._values["endpoint_details"] = endpoint_details
        if endpoint_type is not None:
            self._values["endpoint_type"] = endpoint_type
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if function is not None:
            self._values["function"] = function
        if host_key is not None:
            self._values["host_key"] = host_key
        if identity_provider_type is not None:
            self._values["identity_provider_type"] = identity_provider_type
        if invocation_role is not None:
            self._values["invocation_role"] = invocation_role
        if logging_role is not None:
            self._values["logging_role"] = logging_role
        if protocols is not None:
            self._values["protocols"] = protocols
        if security_policy_name is not None:
            self._values["security_policy_name"] = security_policy_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def certificate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#certificate TransferServer#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#directory_id TransferServer#directory_id}.'''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#domain TransferServer#domain}.'''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_details(self) -> typing.Optional["TransferServerEndpointDetails"]:
        '''endpoint_details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_details TransferServer#endpoint_details}
        '''
        result = self._values.get("endpoint_details")
        return typing.cast(typing.Optional["TransferServerEndpointDetails"], result)

    @builtins.property
    def endpoint_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#endpoint_type TransferServer#endpoint_type}.'''
        result = self._values.get("endpoint_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#force_destroy TransferServer#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def function(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#function TransferServer#function}.'''
        result = self._values.get("function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#host_key TransferServer#host_key}.'''
        result = self._values.get("host_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_provider_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#identity_provider_type TransferServer#identity_provider_type}.'''
        result = self._values.get("identity_provider_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invocation_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#invocation_role TransferServer#invocation_role}.'''
        result = self._values.get("invocation_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#logging_role TransferServer#logging_role}.'''
        result = self._values.get("logging_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#protocols TransferServer#protocols}.'''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_policy_name TransferServer#security_policy_name}.'''
        result = self._values.get("security_policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags TransferServer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#tags_all TransferServer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#url TransferServer#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferServerEndpointDetails",
    jsii_struct_bases=[],
    name_mapping={
        "address_allocation_ids": "addressAllocationIds",
        "security_group_ids": "securityGroupIds",
        "subnet_ids": "subnetIds",
        "vpc_endpoint_id": "vpcEndpointId",
        "vpc_id": "vpcId",
    },
)
class TransferServerEndpointDetails:
    def __init__(
        self,
        *,
        address_allocation_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address_allocation_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#address_allocation_ids TransferServer#address_allocation_ids}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_group_ids TransferServer#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#subnet_ids TransferServer#subnet_ids}.
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_endpoint_id TransferServer#vpc_endpoint_id}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_id TransferServer#vpc_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if address_allocation_ids is not None:
            self._values["address_allocation_ids"] = address_allocation_ids
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids
        if vpc_endpoint_id is not None:
            self._values["vpc_endpoint_id"] = vpc_endpoint_id
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def address_allocation_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#address_allocation_ids TransferServer#address_allocation_ids}.'''
        result = self._values.get("address_allocation_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#security_group_ids TransferServer#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#subnet_ids TransferServer#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_endpoint_id TransferServer#vpc_endpoint_id}.'''
        result = self._values.get("vpc_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_server#vpc_id TransferServer#vpc_id}.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferServerEndpointDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferServerEndpointDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferServerEndpointDetailsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAddressAllocationIds")
    def reset_address_allocation_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddressAllocationIds", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @jsii.member(jsii_name="resetVpcEndpointId")
    def reset_vpc_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointId", []))

    @jsii.member(jsii_name="resetVpcId")
    def reset_vpc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressAllocationIdsInput")
    def address_allocation_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addressAllocationIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointIdInput")
    def vpc_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcEndpointIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressAllocationIds")
    def address_allocation_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "addressAllocationIds"))

    @address_allocation_ids.setter
    def address_allocation_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "addressAllocationIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointId"))

    @vpc_endpoint_id.setter
    def vpc_endpoint_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcEndpointId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferServerEndpointDetails]:
        return typing.cast(typing.Optional[TransferServerEndpointDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TransferServerEndpointDetails],
    ) -> None:
        jsii.set(self, "internalValue", value)


class TransferSshKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferSshKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key aws_transfer_ssh_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        body: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key aws_transfer_ssh_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#body TransferSshKey#body}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#server_id TransferSshKey#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#user_name TransferSshKey#user_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TransferSshKeyConfig(
            body=body,
            server_id=server_id,
            user_name=user_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        jsii.set(self, "body", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        jsii.set(self, "serverId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferSshKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "body": "body",
        "server_id": "serverId",
        "user_name": "userName",
    },
)
class TransferSshKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        body: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
    ) -> None:
        '''AWS Transfer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#body TransferSshKey#body}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#server_id TransferSshKey#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#user_name TransferSshKey#user_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "body": body,
            "server_id": server_id,
            "user_name": user_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#body TransferSshKey#body}.'''
        result = self._values.get("body")
        assert result is not None, "Required property 'body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#server_id TransferSshKey#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_ssh_key#user_name TransferSshKey#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferSshKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/transfer_user aws_transfer_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Sequence["TransferUserHomeDirectoryMappings"]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional["TransferUserPosixProfile"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/transfer_user aws_transfer_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#role TransferUser#role}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#server_id TransferUser#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#user_name TransferUser#user_name}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory TransferUser#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_mappings TransferUser#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_type TransferUser#home_directory_type}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#policy TransferUser#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#posix_profile TransferUser#posix_profile}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags TransferUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags_all TransferUser#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TransferUserConfig(
            role=role,
            server_id=server_id,
            user_name=user_name,
            home_directory=home_directory,
            home_directory_mappings=home_directory_mappings,
            home_directory_type=home_directory_type,
            policy=policy,
            posix_profile=posix_profile,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putPosixProfile")
    def put_posix_profile(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#gid TransferUser#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#uid TransferUser#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#secondary_gids TransferUser#secondary_gids}.
        '''
        value = TransferUserPosixProfile(
            gid=gid, uid=uid, secondary_gids=secondary_gids
        )

        return typing.cast(None, jsii.invoke(self, "putPosixProfile", [value]))

    @jsii.member(jsii_name="resetHomeDirectory")
    def reset_home_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectory", []))

    @jsii.member(jsii_name="resetHomeDirectoryMappings")
    def reset_home_directory_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryMappings", []))

    @jsii.member(jsii_name="resetHomeDirectoryType")
    def reset_home_directory_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHomeDirectoryType", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetPosixProfile")
    def reset_posix_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosixProfile", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfile")
    def posix_profile(self) -> "TransferUserPosixProfileOutputReference":
        return typing.cast("TransferUserPosixProfileOutputReference", jsii.get(self, "posixProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryInput")
    def home_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappingsInput")
    def home_directory_mappings_input(
        self,
    ) -> typing.Optional[typing.List["TransferUserHomeDirectoryMappings"]]:
        return typing.cast(typing.Optional[typing.List["TransferUserHomeDirectoryMappings"]], jsii.get(self, "homeDirectoryMappingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryTypeInput")
    def home_directory_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homeDirectoryTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixProfileInput")
    def posix_profile_input(self) -> typing.Optional["TransferUserPosixProfile"]:
        return typing.cast(typing.Optional["TransferUserPosixProfile"], jsii.get(self, "posixProfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectory")
    def home_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectory"))

    @home_directory.setter
    def home_directory(self, value: builtins.str) -> None:
        jsii.set(self, "homeDirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryMappings")
    def home_directory_mappings(
        self,
    ) -> typing.List["TransferUserHomeDirectoryMappings"]:
        return typing.cast(typing.List["TransferUserHomeDirectoryMappings"], jsii.get(self, "homeDirectoryMappings"))

    @home_directory_mappings.setter
    def home_directory_mappings(
        self,
        value: typing.List["TransferUserHomeDirectoryMappings"],
    ) -> None:
        jsii.set(self, "homeDirectoryMappings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homeDirectoryType")
    def home_directory_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "homeDirectoryType"))

    @home_directory_type.setter
    def home_directory_type(self, value: builtins.str) -> None:
        jsii.set(self, "homeDirectoryType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        jsii.set(self, "serverId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "role": "role",
        "server_id": "serverId",
        "user_name": "userName",
        "home_directory": "homeDirectory",
        "home_directory_mappings": "homeDirectoryMappings",
        "home_directory_type": "homeDirectoryType",
        "policy": "policy",
        "posix_profile": "posixProfile",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class TransferUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        role: builtins.str,
        server_id: builtins.str,
        user_name: builtins.str,
        home_directory: typing.Optional[builtins.str] = None,
        home_directory_mappings: typing.Optional[typing.Sequence["TransferUserHomeDirectoryMappings"]] = None,
        home_directory_type: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        posix_profile: typing.Optional["TransferUserPosixProfile"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Transfer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#role TransferUser#role}.
        :param server_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#server_id TransferUser#server_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#user_name TransferUser#user_name}.
        :param home_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory TransferUser#home_directory}.
        :param home_directory_mappings: home_directory_mappings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_mappings TransferUser#home_directory_mappings}
        :param home_directory_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_type TransferUser#home_directory_type}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#policy TransferUser#policy}.
        :param posix_profile: posix_profile block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#posix_profile TransferUser#posix_profile}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags TransferUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags_all TransferUser#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(posix_profile, dict):
            posix_profile = TransferUserPosixProfile(**posix_profile)
        self._values: typing.Dict[str, typing.Any] = {
            "role": role,
            "server_id": server_id,
            "user_name": user_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if home_directory is not None:
            self._values["home_directory"] = home_directory
        if home_directory_mappings is not None:
            self._values["home_directory_mappings"] = home_directory_mappings
        if home_directory_type is not None:
            self._values["home_directory_type"] = home_directory_type
        if policy is not None:
            self._values["policy"] = policy
        if posix_profile is not None:
            self._values["posix_profile"] = posix_profile
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#role TransferUser#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#server_id TransferUser#server_id}.'''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#user_name TransferUser#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def home_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory TransferUser#home_directory}.'''
        result = self._values.get("home_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def home_directory_mappings(
        self,
    ) -> typing.Optional[typing.List["TransferUserHomeDirectoryMappings"]]:
        '''home_directory_mappings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_mappings TransferUser#home_directory_mappings}
        '''
        result = self._values.get("home_directory_mappings")
        return typing.cast(typing.Optional[typing.List["TransferUserHomeDirectoryMappings"]], result)

    @builtins.property
    def home_directory_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#home_directory_type TransferUser#home_directory_type}.'''
        result = self._values.get("home_directory_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#policy TransferUser#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def posix_profile(self) -> typing.Optional["TransferUserPosixProfile"]:
        '''posix_profile block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#posix_profile TransferUser#posix_profile}
        '''
        result = self._values.get("posix_profile")
        return typing.cast(typing.Optional["TransferUserPosixProfile"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags TransferUser#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#tags_all TransferUser#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferUserHomeDirectoryMappings",
    jsii_struct_bases=[],
    name_mapping={"entry": "entry", "target": "target"},
)
class TransferUserHomeDirectoryMappings:
    def __init__(self, *, entry: builtins.str, target: builtins.str) -> None:
        '''
        :param entry: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#entry TransferUser#entry}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#target TransferUser#target}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "entry": entry,
            "target": target,
        }

    @builtins.property
    def entry(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#entry TransferUser#entry}.'''
        result = self._values.get("entry")
        assert result is not None, "Required property 'entry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#target TransferUser#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferUserHomeDirectoryMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.transfer.TransferUserPosixProfile",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
)
class TransferUserPosixProfile:
    def __init__(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#gid TransferUser#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#uid TransferUser#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#secondary_gids TransferUser#secondary_gids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "gid": gid,
            "uid": uid,
        }
        if secondary_gids is not None:
            self._values["secondary_gids"] = secondary_gids

    @builtins.property
    def gid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#gid TransferUser#gid}.'''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def uid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#uid TransferUser#uid}.'''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def secondary_gids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/transfer_user#secondary_gids TransferUser#secondary_gids}.'''
        result = self._values.get("secondary_gids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransferUserPosixProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TransferUserPosixProfileOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.transfer.TransferUserPosixProfileOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetSecondaryGids")
    def reset_secondary_gids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryGids", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gidInput")
    def gid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGidsInput")
    def secondary_gids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "secondaryGidsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "uidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gid")
    def gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gid"))

    @gid.setter
    def gid(self, value: jsii.Number) -> None:
        jsii.set(self, "gid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGids")
    def secondary_gids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "secondaryGids"))

    @secondary_gids.setter
    def secondary_gids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "secondaryGids", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: jsii.Number) -> None:
        jsii.set(self, "uid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[TransferUserPosixProfile]:
        return typing.cast(typing.Optional[TransferUserPosixProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[TransferUserPosixProfile]) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsTransferServer",
    "DataAwsTransferServerConfig",
    "TransferAccess",
    "TransferAccessConfig",
    "TransferAccessHomeDirectoryMappings",
    "TransferAccessPosixProfile",
    "TransferAccessPosixProfileOutputReference",
    "TransferServer",
    "TransferServerConfig",
    "TransferServerEndpointDetails",
    "TransferServerEndpointDetailsOutputReference",
    "TransferSshKey",
    "TransferSshKeyConfig",
    "TransferUser",
    "TransferUserConfig",
    "TransferUserHomeDirectoryMappings",
    "TransferUserPosixProfile",
    "TransferUserPosixProfileOutputReference",
]

publication.publish()
