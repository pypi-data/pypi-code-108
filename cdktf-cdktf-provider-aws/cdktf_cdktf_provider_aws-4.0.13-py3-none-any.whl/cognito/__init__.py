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


class CognitoIdentityPool(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPool",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool aws_cognito_identity_pool}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity_pool_name: builtins.str,
        allow_classic_flow: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allow_unauthenticated_identities: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cognito_identity_providers: typing.Optional[typing.Sequence["CognitoIdentityPoolCognitoIdentityProviders"]] = None,
        developer_provider_name: typing.Optional[builtins.str] = None,
        openid_connect_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        saml_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        supported_login_providers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool aws_cognito_identity_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_pool_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#identity_pool_name CognitoIdentityPool#identity_pool_name}.
        :param allow_classic_flow: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_classic_flow CognitoIdentityPool#allow_classic_flow}.
        :param allow_unauthenticated_identities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_unauthenticated_identities CognitoIdentityPool#allow_unauthenticated_identities}.
        :param cognito_identity_providers: cognito_identity_providers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#cognito_identity_providers CognitoIdentityPool#cognito_identity_providers}
        :param developer_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#developer_provider_name CognitoIdentityPool#developer_provider_name}.
        :param openid_connect_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#openid_connect_provider_arns CognitoIdentityPool#openid_connect_provider_arns}.
        :param saml_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#saml_provider_arns CognitoIdentityPool#saml_provider_arns}.
        :param supported_login_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#supported_login_providers CognitoIdentityPool#supported_login_providers}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags CognitoIdentityPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags_all CognitoIdentityPool#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoIdentityPoolConfig(
            identity_pool_name=identity_pool_name,
            allow_classic_flow=allow_classic_flow,
            allow_unauthenticated_identities=allow_unauthenticated_identities,
            cognito_identity_providers=cognito_identity_providers,
            developer_provider_name=developer_provider_name,
            openid_connect_provider_arns=openid_connect_provider_arns,
            saml_provider_arns=saml_provider_arns,
            supported_login_providers=supported_login_providers,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllowClassicFlow")
    def reset_allow_classic_flow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowClassicFlow", []))

    @jsii.member(jsii_name="resetAllowUnauthenticatedIdentities")
    def reset_allow_unauthenticated_identities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUnauthenticatedIdentities", []))

    @jsii.member(jsii_name="resetCognitoIdentityProviders")
    def reset_cognito_identity_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCognitoIdentityProviders", []))

    @jsii.member(jsii_name="resetDeveloperProviderName")
    def reset_developer_provider_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeveloperProviderName", []))

    @jsii.member(jsii_name="resetOpenidConnectProviderArns")
    def reset_openid_connect_provider_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenidConnectProviderArns", []))

    @jsii.member(jsii_name="resetSamlProviderArns")
    def reset_saml_provider_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamlProviderArns", []))

    @jsii.member(jsii_name="resetSupportedLoginProviders")
    def reset_supported_login_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportedLoginProviders", []))

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
    @jsii.member(jsii_name="allowClassicFlowInput")
    def allow_classic_flow_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowClassicFlowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowUnauthenticatedIdentitiesInput")
    def allow_unauthenticated_identities_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowUnauthenticatedIdentitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cognitoIdentityProvidersInput")
    def cognito_identity_providers_input(
        self,
    ) -> typing.Optional[typing.List["CognitoIdentityPoolCognitoIdentityProviders"]]:
        return typing.cast(typing.Optional[typing.List["CognitoIdentityPoolCognitoIdentityProviders"]], jsii.get(self, "cognitoIdentityProvidersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="developerProviderNameInput")
    def developer_provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "developerProviderNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolNameInput")
    def identity_pool_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openidConnectProviderArnsInput")
    def openid_connect_provider_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "openidConnectProviderArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlProviderArnsInput")
    def saml_provider_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "samlProviderArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedLoginProvidersInput")
    def supported_login_providers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "supportedLoginProvidersInput"))

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
    @jsii.member(jsii_name="allowClassicFlow")
    def allow_classic_flow(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowClassicFlow"))

    @allow_classic_flow.setter
    def allow_classic_flow(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowClassicFlow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowUnauthenticatedIdentities")
    def allow_unauthenticated_identities(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowUnauthenticatedIdentities"))

    @allow_unauthenticated_identities.setter
    def allow_unauthenticated_identities(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowUnauthenticatedIdentities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cognitoIdentityProviders")
    def cognito_identity_providers(
        self,
    ) -> typing.List["CognitoIdentityPoolCognitoIdentityProviders"]:
        return typing.cast(typing.List["CognitoIdentityPoolCognitoIdentityProviders"], jsii.get(self, "cognitoIdentityProviders"))

    @cognito_identity_providers.setter
    def cognito_identity_providers(
        self,
        value: typing.List["CognitoIdentityPoolCognitoIdentityProviders"],
    ) -> None:
        jsii.set(self, "cognitoIdentityProviders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="developerProviderName")
    def developer_provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "developerProviderName"))

    @developer_provider_name.setter
    def developer_provider_name(self, value: builtins.str) -> None:
        jsii.set(self, "developerProviderName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolName")
    def identity_pool_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityPoolName"))

    @identity_pool_name.setter
    def identity_pool_name(self, value: builtins.str) -> None:
        jsii.set(self, "identityPoolName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openidConnectProviderArns")
    def openid_connect_provider_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "openidConnectProviderArns"))

    @openid_connect_provider_arns.setter
    def openid_connect_provider_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "openidConnectProviderArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlProviderArns")
    def saml_provider_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "samlProviderArns"))

    @saml_provider_arns.setter
    def saml_provider_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "samlProviderArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedLoginProviders")
    def supported_login_providers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "supportedLoginProviders"))

    @supported_login_providers.setter
    def supported_login_providers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "supportedLoginProviders", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolCognitoIdentityProviders",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "provider_name": "providerName",
        "server_side_token_check": "serverSideTokenCheck",
    },
)
class CognitoIdentityPoolCognitoIdentityProviders:
    def __init__(
        self,
        *,
        client_id: typing.Optional[builtins.str] = None,
        provider_name: typing.Optional[builtins.str] = None,
        server_side_token_check: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#client_id CognitoIdentityPool#client_id}.
        :param provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#provider_name CognitoIdentityPool#provider_name}.
        :param server_side_token_check: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#server_side_token_check CognitoIdentityPool#server_side_token_check}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if provider_name is not None:
            self._values["provider_name"] = provider_name
        if server_side_token_check is not None:
            self._values["server_side_token_check"] = server_side_token_check

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#client_id CognitoIdentityPool#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#provider_name CognitoIdentityPool#provider_name}.'''
        result = self._values.get("provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_token_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#server_side_token_check CognitoIdentityPool#server_side_token_check}.'''
        result = self._values.get("server_side_token_check")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolCognitoIdentityProviders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity_pool_name": "identityPoolName",
        "allow_classic_flow": "allowClassicFlow",
        "allow_unauthenticated_identities": "allowUnauthenticatedIdentities",
        "cognito_identity_providers": "cognitoIdentityProviders",
        "developer_provider_name": "developerProviderName",
        "openid_connect_provider_arns": "openidConnectProviderArns",
        "saml_provider_arns": "samlProviderArns",
        "supported_login_providers": "supportedLoginProviders",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CognitoIdentityPoolConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity_pool_name: builtins.str,
        allow_classic_flow: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allow_unauthenticated_identities: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cognito_identity_providers: typing.Optional[typing.Sequence[CognitoIdentityPoolCognitoIdentityProviders]] = None,
        developer_provider_name: typing.Optional[builtins.str] = None,
        openid_connect_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        saml_provider_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        supported_login_providers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity_pool_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#identity_pool_name CognitoIdentityPool#identity_pool_name}.
        :param allow_classic_flow: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_classic_flow CognitoIdentityPool#allow_classic_flow}.
        :param allow_unauthenticated_identities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_unauthenticated_identities CognitoIdentityPool#allow_unauthenticated_identities}.
        :param cognito_identity_providers: cognito_identity_providers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#cognito_identity_providers CognitoIdentityPool#cognito_identity_providers}
        :param developer_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#developer_provider_name CognitoIdentityPool#developer_provider_name}.
        :param openid_connect_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#openid_connect_provider_arns CognitoIdentityPool#openid_connect_provider_arns}.
        :param saml_provider_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#saml_provider_arns CognitoIdentityPool#saml_provider_arns}.
        :param supported_login_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#supported_login_providers CognitoIdentityPool#supported_login_providers}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags CognitoIdentityPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags_all CognitoIdentityPool#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool_name": identity_pool_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_classic_flow is not None:
            self._values["allow_classic_flow"] = allow_classic_flow
        if allow_unauthenticated_identities is not None:
            self._values["allow_unauthenticated_identities"] = allow_unauthenticated_identities
        if cognito_identity_providers is not None:
            self._values["cognito_identity_providers"] = cognito_identity_providers
        if developer_provider_name is not None:
            self._values["developer_provider_name"] = developer_provider_name
        if openid_connect_provider_arns is not None:
            self._values["openid_connect_provider_arns"] = openid_connect_provider_arns
        if saml_provider_arns is not None:
            self._values["saml_provider_arns"] = saml_provider_arns
        if supported_login_providers is not None:
            self._values["supported_login_providers"] = supported_login_providers
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
    def identity_pool_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#identity_pool_name CognitoIdentityPool#identity_pool_name}.'''
        result = self._values.get("identity_pool_name")
        assert result is not None, "Required property 'identity_pool_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_classic_flow(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_classic_flow CognitoIdentityPool#allow_classic_flow}.'''
        result = self._values.get("allow_classic_flow")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def allow_unauthenticated_identities(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#allow_unauthenticated_identities CognitoIdentityPool#allow_unauthenticated_identities}.'''
        result = self._values.get("allow_unauthenticated_identities")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cognito_identity_providers(
        self,
    ) -> typing.Optional[typing.List[CognitoIdentityPoolCognitoIdentityProviders]]:
        '''cognito_identity_providers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#cognito_identity_providers CognitoIdentityPool#cognito_identity_providers}
        '''
        result = self._values.get("cognito_identity_providers")
        return typing.cast(typing.Optional[typing.List[CognitoIdentityPoolCognitoIdentityProviders]], result)

    @builtins.property
    def developer_provider_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#developer_provider_name CognitoIdentityPool#developer_provider_name}.'''
        result = self._values.get("developer_provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def openid_connect_provider_arns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#openid_connect_provider_arns CognitoIdentityPool#openid_connect_provider_arns}.'''
        result = self._values.get("openid_connect_provider_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def saml_provider_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#saml_provider_arns CognitoIdentityPool#saml_provider_arns}.'''
        result = self._values.get("saml_provider_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def supported_login_providers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#supported_login_providers CognitoIdentityPool#supported_login_providers}.'''
        result = self._values.get("supported_login_providers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags CognitoIdentityPool#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool#tags_all CognitoIdentityPool#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolProviderPrincipalTag(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolProviderPrincipalTag",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag aws_cognito_identity_pool_provider_principal_tag}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity_pool_id: builtins.str,
        identity_provider_name: builtins.str,
        principal_tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_defaults: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag aws_cognito_identity_pool_provider_principal_tag} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_pool_id CognitoIdentityPoolProviderPrincipalTag#identity_pool_id}.
        :param identity_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_provider_name CognitoIdentityPoolProviderPrincipalTag#identity_provider_name}.
        :param principal_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#principal_tags CognitoIdentityPoolProviderPrincipalTag#principal_tags}.
        :param use_defaults: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#use_defaults CognitoIdentityPoolProviderPrincipalTag#use_defaults}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoIdentityPoolProviderPrincipalTagConfig(
            identity_pool_id=identity_pool_id,
            identity_provider_name=identity_provider_name,
            principal_tags=principal_tags,
            use_defaults=use_defaults,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetPrincipalTags")
    def reset_principal_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrincipalTags", []))

    @jsii.member(jsii_name="resetUseDefaults")
    def reset_use_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseDefaults", []))

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
    @jsii.member(jsii_name="identityPoolIdInput")
    def identity_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderNameInput")
    def identity_provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalTagsInput")
    def principal_tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "principalTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useDefaultsInput")
    def use_defaults_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useDefaultsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

    @identity_pool_id.setter
    def identity_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "identityPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviderName")
    def identity_provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderName"))

    @identity_provider_name.setter
    def identity_provider_name(self, value: builtins.str) -> None:
        jsii.set(self, "identityProviderName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalTags")
    def principal_tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "principalTags"))

    @principal_tags.setter
    def principal_tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "principalTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useDefaults")
    def use_defaults(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useDefaults"))

    @use_defaults.setter
    def use_defaults(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useDefaults", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolProviderPrincipalTagConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity_pool_id": "identityPoolId",
        "identity_provider_name": "identityProviderName",
        "principal_tags": "principalTags",
        "use_defaults": "useDefaults",
    },
)
class CognitoIdentityPoolProviderPrincipalTagConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity_pool_id: builtins.str,
        identity_provider_name: builtins.str,
        principal_tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_defaults: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_pool_id CognitoIdentityPoolProviderPrincipalTag#identity_pool_id}.
        :param identity_provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_provider_name CognitoIdentityPoolProviderPrincipalTag#identity_provider_name}.
        :param principal_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#principal_tags CognitoIdentityPoolProviderPrincipalTag#principal_tags}.
        :param use_defaults: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#use_defaults CognitoIdentityPoolProviderPrincipalTag#use_defaults}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool_id": identity_pool_id,
            "identity_provider_name": identity_provider_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if principal_tags is not None:
            self._values["principal_tags"] = principal_tags
        if use_defaults is not None:
            self._values["use_defaults"] = use_defaults

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
    def identity_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_pool_id CognitoIdentityPoolProviderPrincipalTag#identity_pool_id}.'''
        result = self._values.get("identity_pool_id")
        assert result is not None, "Required property 'identity_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_provider_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#identity_provider_name CognitoIdentityPoolProviderPrincipalTag#identity_provider_name}.'''
        result = self._values.get("identity_provider_name")
        assert result is not None, "Required property 'identity_provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal_tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#principal_tags CognitoIdentityPoolProviderPrincipalTag#principal_tags}.'''
        result = self._values.get("principal_tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_defaults(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_provider_principal_tag#use_defaults CognitoIdentityPoolProviderPrincipalTag#use_defaults}.'''
        result = self._values.get("use_defaults")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolProviderPrincipalTagConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityPoolRolesAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment aws_cognito_identity_pool_roles_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity_pool_id: builtins.str,
        roles: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        role_mapping: typing.Optional[typing.Sequence["CognitoIdentityPoolRolesAttachmentRoleMapping"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment aws_cognito_identity_pool_roles_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_pool_id CognitoIdentityPoolRolesAttachment#identity_pool_id}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#roles CognitoIdentityPoolRolesAttachment#roles}.
        :param role_mapping: role_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_mapping CognitoIdentityPoolRolesAttachment#role_mapping}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoIdentityPoolRolesAttachmentConfig(
            identity_pool_id=identity_pool_id,
            roles=roles,
            role_mapping=role_mapping,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRoleMapping")
    def reset_role_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleMapping", []))

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
    @jsii.member(jsii_name="identityPoolIdInput")
    def identity_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleMappingInput")
    def role_mapping_input(
        self,
    ) -> typing.Optional[typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]]:
        return typing.cast(typing.Optional[typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]], jsii.get(self, "roleMappingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rolesInput")
    def roles_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "rolesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

    @identity_pool_id.setter
    def identity_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "identityPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleMapping")
    def role_mapping(
        self,
    ) -> typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]:
        return typing.cast(typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"], jsii.get(self, "roleMapping"))

    @role_mapping.setter
    def role_mapping(
        self,
        value: typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"],
    ) -> None:
        jsii.set(self, "roleMapping", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roles")
    def roles(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "roles"))

    @roles.setter
    def roles(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "roles", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity_pool_id": "identityPoolId",
        "roles": "roles",
        "role_mapping": "roleMapping",
    },
)
class CognitoIdentityPoolRolesAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity_pool_id: builtins.str,
        roles: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        role_mapping: typing.Optional[typing.Sequence["CognitoIdentityPoolRolesAttachmentRoleMapping"]] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_pool_id CognitoIdentityPoolRolesAttachment#identity_pool_id}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#roles CognitoIdentityPoolRolesAttachment#roles}.
        :param role_mapping: role_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_mapping CognitoIdentityPoolRolesAttachment#role_mapping}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool_id": identity_pool_id,
            "roles": roles,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if role_mapping is not None:
            self._values["role_mapping"] = role_mapping

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
    def identity_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_pool_id CognitoIdentityPoolRolesAttachment#identity_pool_id}.'''
        result = self._values.get("identity_pool_id")
        assert result is not None, "Required property 'identity_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def roles(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#roles CognitoIdentityPoolRolesAttachment#roles}.'''
        result = self._values.get("roles")
        assert result is not None, "Required property 'roles' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def role_mapping(
        self,
    ) -> typing.Optional[typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]]:
        '''role_mapping block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_mapping CognitoIdentityPoolRolesAttachment#role_mapping}
        '''
        result = self._values.get("role_mapping")
        return typing.cast(typing.Optional[typing.List["CognitoIdentityPoolRolesAttachmentRoleMapping"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolRolesAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMapping",
    jsii_struct_bases=[],
    name_mapping={
        "identity_provider": "identityProvider",
        "type": "type",
        "ambiguous_role_resolution": "ambiguousRoleResolution",
        "mapping_rule": "mappingRule",
    },
)
class CognitoIdentityPoolRolesAttachmentRoleMapping:
    def __init__(
        self,
        *,
        identity_provider: builtins.str,
        type: builtins.str,
        ambiguous_role_resolution: typing.Optional[builtins.str] = None,
        mapping_rule: typing.Optional[typing.Sequence["CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule"]] = None,
    ) -> None:
        '''
        :param identity_provider: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_provider CognitoIdentityPoolRolesAttachment#identity_provider}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#type CognitoIdentityPoolRolesAttachment#type}.
        :param ambiguous_role_resolution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#ambiguous_role_resolution CognitoIdentityPoolRolesAttachment#ambiguous_role_resolution}.
        :param mapping_rule: mapping_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#mapping_rule CognitoIdentityPoolRolesAttachment#mapping_rule}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "identity_provider": identity_provider,
            "type": type,
        }
        if ambiguous_role_resolution is not None:
            self._values["ambiguous_role_resolution"] = ambiguous_role_resolution
        if mapping_rule is not None:
            self._values["mapping_rule"] = mapping_rule

    @builtins.property
    def identity_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#identity_provider CognitoIdentityPoolRolesAttachment#identity_provider}.'''
        result = self._values.get("identity_provider")
        assert result is not None, "Required property 'identity_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#type CognitoIdentityPoolRolesAttachment#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ambiguous_role_resolution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#ambiguous_role_resolution CognitoIdentityPoolRolesAttachment#ambiguous_role_resolution}.'''
        result = self._values.get("ambiguous_role_resolution")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mapping_rule(
        self,
    ) -> typing.Optional[typing.List["CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule"]]:
        '''mapping_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#mapping_rule CognitoIdentityPoolRolesAttachment#mapping_rule}
        '''
        result = self._values.get("mapping_rule")
        return typing.cast(typing.Optional[typing.List["CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolRolesAttachmentRoleMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule",
    jsii_struct_bases=[],
    name_mapping={
        "claim": "claim",
        "match_type": "matchType",
        "role_arn": "roleArn",
        "value": "value",
    },
)
class CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule:
    def __init__(
        self,
        *,
        claim: builtins.str,
        match_type: builtins.str,
        role_arn: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param claim: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#claim CognitoIdentityPoolRolesAttachment#claim}.
        :param match_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#match_type CognitoIdentityPoolRolesAttachment#match_type}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_arn CognitoIdentityPoolRolesAttachment#role_arn}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#value CognitoIdentityPoolRolesAttachment#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "claim": claim,
            "match_type": match_type,
            "role_arn": role_arn,
            "value": value,
        }

    @builtins.property
    def claim(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#claim CognitoIdentityPoolRolesAttachment#claim}.'''
        result = self._values.get("claim")
        assert result is not None, "Required property 'claim' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def match_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#match_type CognitoIdentityPoolRolesAttachment#match_type}.'''
        result = self._values.get("match_type")
        assert result is not None, "Required property 'match_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#role_arn CognitoIdentityPoolRolesAttachment#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_pool_roles_attachment#value CognitoIdentityPoolRolesAttachment#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoIdentityProvider(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider aws_cognito_identity_provider}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        provider_details: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        provider_name: builtins.str,
        provider_type: builtins.str,
        user_pool_id: builtins.str,
        attribute_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        idp_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider aws_cognito_identity_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param provider_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_details CognitoIdentityProvider#provider_details}.
        :param provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_name CognitoIdentityProvider#provider_name}.
        :param provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_type CognitoIdentityProvider#provider_type}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#user_pool_id CognitoIdentityProvider#user_pool_id}.
        :param attribute_mapping: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#attribute_mapping CognitoIdentityProvider#attribute_mapping}.
        :param idp_identifiers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#idp_identifiers CognitoIdentityProvider#idp_identifiers}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoIdentityProviderConfig(
            provider_details=provider_details,
            provider_name=provider_name,
            provider_type=provider_type,
            user_pool_id=user_pool_id,
            attribute_mapping=attribute_mapping,
            idp_identifiers=idp_identifiers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAttributeMapping")
    def reset_attribute_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributeMapping", []))

    @jsii.member(jsii_name="resetIdpIdentifiers")
    def reset_idp_identifiers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpIdentifiers", []))

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
    @jsii.member(jsii_name="attributeMappingInput")
    def attribute_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "attributeMappingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpIdentifiersInput")
    def idp_identifiers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "idpIdentifiersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerDetailsInput")
    def provider_details_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "providerDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerNameInput")
    def provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerTypeInput")
    def provider_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeMapping")
    def attribute_mapping(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "attributeMapping"))

    @attribute_mapping.setter
    def attribute_mapping(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "attributeMapping", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpIdentifiers")
    def idp_identifiers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "idpIdentifiers"))

    @idp_identifiers.setter
    def idp_identifiers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "idpIdentifiers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerDetails")
    def provider_details(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "providerDetails"))

    @provider_details.setter
    def provider_details(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "providerDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @provider_name.setter
    def provider_name(self, value: builtins.str) -> None:
        jsii.set(self, "providerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerType")
    def provider_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerType"))

    @provider_type.setter
    def provider_type(self, value: builtins.str) -> None:
        jsii.set(self, "providerType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoIdentityProviderConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provider_details": "providerDetails",
        "provider_name": "providerName",
        "provider_type": "providerType",
        "user_pool_id": "userPoolId",
        "attribute_mapping": "attributeMapping",
        "idp_identifiers": "idpIdentifiers",
    },
)
class CognitoIdentityProviderConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provider_details: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        provider_name: builtins.str,
        provider_type: builtins.str,
        user_pool_id: builtins.str,
        attribute_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        idp_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param provider_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_details CognitoIdentityProvider#provider_details}.
        :param provider_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_name CognitoIdentityProvider#provider_name}.
        :param provider_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_type CognitoIdentityProvider#provider_type}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#user_pool_id CognitoIdentityProvider#user_pool_id}.
        :param attribute_mapping: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#attribute_mapping CognitoIdentityProvider#attribute_mapping}.
        :param idp_identifiers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#idp_identifiers CognitoIdentityProvider#idp_identifiers}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "provider_details": provider_details,
            "provider_name": provider_name,
            "provider_type": provider_type,
            "user_pool_id": user_pool_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if attribute_mapping is not None:
            self._values["attribute_mapping"] = attribute_mapping
        if idp_identifiers is not None:
            self._values["idp_identifiers"] = idp_identifiers

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
    def provider_details(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_details CognitoIdentityProvider#provider_details}.'''
        result = self._values.get("provider_details")
        assert result is not None, "Required property 'provider_details' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_name CognitoIdentityProvider#provider_name}.'''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#provider_type CognitoIdentityProvider#provider_type}.'''
        result = self._values.get("provider_type")
        assert result is not None, "Required property 'provider_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#user_pool_id CognitoIdentityProvider#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_mapping(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#attribute_mapping CognitoIdentityProvider#attribute_mapping}.'''
        result = self._values.get("attribute_mapping")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def idp_identifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_identity_provider#idp_identifiers CognitoIdentityProvider#idp_identifiers}.'''
        result = self._values.get("idp_identifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoIdentityProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoResourceServer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server aws_cognito_resource_server}.'''

    def __init__(
        self,
        scope_: constructs.Construct,
        id: builtins.str,
        *,
        identifier: builtins.str,
        name: builtins.str,
        user_pool_id: builtins.str,
        scope: typing.Optional[typing.Sequence["CognitoResourceServerScope"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server aws_cognito_resource_server} Resource.

        :param scope_: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#identifier CognitoResourceServer#identifier}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#name CognitoResourceServer#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#user_pool_id CognitoResourceServer#user_pool_id}.
        :param scope: scope block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope CognitoResourceServer#scope}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoResourceServerConfig(
            identifier=identifier,
            name=name,
            user_pool_id=user_pool_id,
            scope=scope,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope_, id, config])

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

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
    @jsii.member(jsii_name="scopeIdentifiers")
    def scope_identifiers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopeIdentifiers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[typing.List["CognitoResourceServerScope"]]:
        return typing.cast(typing.Optional[typing.List["CognitoResourceServerScope"]], jsii.get(self, "scopeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identifier"))

    @identifier.setter
    def identifier(self, value: builtins.str) -> None:
        jsii.set(self, "identifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.List["CognitoResourceServerScope"]:
        return typing.cast(typing.List["CognitoResourceServerScope"], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.List["CognitoResourceServerScope"]) -> None:
        jsii.set(self, "scope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identifier": "identifier",
        "name": "name",
        "user_pool_id": "userPoolId",
        "scope": "scope",
    },
)
class CognitoResourceServerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identifier: builtins.str,
        name: builtins.str,
        user_pool_id: builtins.str,
        scope: typing.Optional[typing.Sequence["CognitoResourceServerScope"]] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#identifier CognitoResourceServer#identifier}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#name CognitoResourceServer#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#user_pool_id CognitoResourceServer#user_pool_id}.
        :param scope: scope block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope CognitoResourceServer#scope}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identifier": identifier,
            "name": name,
            "user_pool_id": user_pool_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if scope is not None:
            self._values["scope"] = scope

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
    def identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#identifier CognitoResourceServer#identifier}.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#name CognitoResourceServer#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#user_pool_id CognitoResourceServer#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> typing.Optional[typing.List["CognitoResourceServerScope"]]:
        '''scope block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope CognitoResourceServer#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[typing.List["CognitoResourceServerScope"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoResourceServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoResourceServerScope",
    jsii_struct_bases=[],
    name_mapping={"scope_description": "scopeDescription", "scope_name": "scopeName"},
)
class CognitoResourceServerScope:
    def __init__(
        self,
        *,
        scope_description: builtins.str,
        scope_name: builtins.str,
    ) -> None:
        '''
        :param scope_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_description CognitoResourceServer#scope_description}.
        :param scope_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_name CognitoResourceServer#scope_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "scope_description": scope_description,
            "scope_name": scope_name,
        }

    @builtins.property
    def scope_description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_description CognitoResourceServer#scope_description}.'''
        result = self._values.get("scope_description")
        assert result is not None, "Required property 'scope_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_resource_server#scope_name CognitoResourceServer#scope_name}.'''
        result = self._values.get("scope_name")
        assert result is not None, "Required property 'scope_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoResourceServerScope(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group aws_cognito_user_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        user_pool_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        precedence: typing.Optional[jsii.Number] = None,
        role_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group aws_cognito_user_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#name CognitoUserGroup#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#user_pool_id CognitoUserGroup#user_pool_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#description CognitoUserGroup#description}.
        :param precedence: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#precedence CognitoUserGroup#precedence}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#role_arn CognitoUserGroup#role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoUserGroupConfig(
            name=name,
            user_pool_id=user_pool_id,
            description=description,
            precedence=precedence,
            role_arn=role_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetPrecedence")
    def reset_precedence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecedence", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="precedenceInput")
    def precedence_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precedenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @precedence.setter
    def precedence(self, value: jsii.Number) -> None:
        jsii.set(self, "precedence", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "user_pool_id": "userPoolId",
        "description": "description",
        "precedence": "precedence",
        "role_arn": "roleArn",
    },
)
class CognitoUserGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        user_pool_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        precedence: typing.Optional[jsii.Number] = None,
        role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#name CognitoUserGroup#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#user_pool_id CognitoUserGroup#user_pool_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#description CognitoUserGroup#description}.
        :param precedence: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#precedence CognitoUserGroup#precedence}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#role_arn CognitoUserGroup#role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "user_pool_id": user_pool_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if precedence is not None:
            self._values["precedence"] = precedence
        if role_arn is not None:
            self._values["role_arn"] = role_arn

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#name CognitoUserGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#user_pool_id CognitoUserGroup#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#description CognitoUserGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def precedence(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#precedence CognitoUserGroup#precedence}.'''
        result = self._values.get("precedence")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_group#role_arn CognitoUserGroup#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPool(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPool",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool aws_cognito_user_pool}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        account_recovery_setting: typing.Optional["CognitoUserPoolAccountRecoverySetting"] = None,
        admin_create_user_config: typing.Optional["CognitoUserPoolAdminCreateUserConfig"] = None,
        alias_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_verified_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        device_configuration: typing.Optional["CognitoUserPoolDeviceConfiguration"] = None,
        email_configuration: typing.Optional["CognitoUserPoolEmailConfiguration"] = None,
        email_verification_message: typing.Optional[builtins.str] = None,
        email_verification_subject: typing.Optional[builtins.str] = None,
        lambda_config: typing.Optional["CognitoUserPoolLambdaConfig"] = None,
        mfa_configuration: typing.Optional[builtins.str] = None,
        password_policy: typing.Optional["CognitoUserPoolPasswordPolicy"] = None,
        schema: typing.Optional[typing.Sequence["CognitoUserPoolSchema"]] = None,
        sms_authentication_message: typing.Optional[builtins.str] = None,
        sms_configuration: typing.Optional["CognitoUserPoolSmsConfiguration"] = None,
        sms_verification_message: typing.Optional[builtins.str] = None,
        software_token_mfa_configuration: typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        username_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        username_configuration: typing.Optional["CognitoUserPoolUsernameConfiguration"] = None,
        user_pool_add_ons: typing.Optional["CognitoUserPoolUserPoolAddOns"] = None,
        verification_message_template: typing.Optional["CognitoUserPoolVerificationMessageTemplate"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool aws_cognito_user_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param account_recovery_setting: account_recovery_setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#account_recovery_setting CognitoUserPool#account_recovery_setting}
        :param admin_create_user_config: admin_create_user_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#admin_create_user_config CognitoUserPool#admin_create_user_config}
        :param alias_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#alias_attributes CognitoUserPool#alias_attributes}.
        :param auto_verified_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#auto_verified_attributes CognitoUserPool#auto_verified_attributes}.
        :param device_configuration: device_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_configuration CognitoUserPool#device_configuration}
        :param email_configuration: email_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_configuration CognitoUserPool#email_configuration}
        :param email_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_message CognitoUserPool#email_verification_message}.
        :param email_verification_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_subject CognitoUserPool#email_verification_subject}.
        :param lambda_config: lambda_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_config CognitoUserPool#lambda_config}
        :param mfa_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mfa_configuration CognitoUserPool#mfa_configuration}.
        :param password_policy: password_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#password_policy CognitoUserPool#password_policy}
        :param schema: schema block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#schema CognitoUserPool#schema}
        :param sms_authentication_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_authentication_message CognitoUserPool#sms_authentication_message}.
        :param sms_configuration: sms_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_configuration CognitoUserPool#sms_configuration}
        :param sms_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_verification_message CognitoUserPool#sms_verification_message}.
        :param software_token_mfa_configuration: software_token_mfa_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#software_token_mfa_configuration CognitoUserPool#software_token_mfa_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags CognitoUserPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags_all CognitoUserPool#tags_all}.
        :param username_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_attributes CognitoUserPool#username_attributes}.
        :param username_configuration: username_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_configuration CognitoUserPool#username_configuration}
        :param user_pool_add_ons: user_pool_add_ons block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_pool_add_ons CognitoUserPool#user_pool_add_ons}
        :param verification_message_template: verification_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verification_message_template CognitoUserPool#verification_message_template}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoUserPoolConfig(
            name=name,
            account_recovery_setting=account_recovery_setting,
            admin_create_user_config=admin_create_user_config,
            alias_attributes=alias_attributes,
            auto_verified_attributes=auto_verified_attributes,
            device_configuration=device_configuration,
            email_configuration=email_configuration,
            email_verification_message=email_verification_message,
            email_verification_subject=email_verification_subject,
            lambda_config=lambda_config,
            mfa_configuration=mfa_configuration,
            password_policy=password_policy,
            schema=schema,
            sms_authentication_message=sms_authentication_message,
            sms_configuration=sms_configuration,
            sms_verification_message=sms_verification_message,
            software_token_mfa_configuration=software_token_mfa_configuration,
            tags=tags,
            tags_all=tags_all,
            username_attributes=username_attributes,
            username_configuration=username_configuration,
            user_pool_add_ons=user_pool_add_ons,
            verification_message_template=verification_message_template,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAccountRecoverySetting")
    def put_account_recovery_setting(
        self,
        *,
        recovery_mechanism: typing.Sequence["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"],
    ) -> None:
        '''
        :param recovery_mechanism: recovery_mechanism block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#recovery_mechanism CognitoUserPool#recovery_mechanism}
        '''
        value = CognitoUserPoolAccountRecoverySetting(
            recovery_mechanism=recovery_mechanism
        )

        return typing.cast(None, jsii.invoke(self, "putAccountRecoverySetting", [value]))

    @jsii.member(jsii_name="putAdminCreateUserConfig")
    def put_admin_create_user_config(
        self,
        *,
        allow_admin_create_user_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invite_message_template: typing.Optional["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate"] = None,
    ) -> None:
        '''
        :param allow_admin_create_user_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#allow_admin_create_user_only CognitoUserPool#allow_admin_create_user_only}.
        :param invite_message_template: invite_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#invite_message_template CognitoUserPool#invite_message_template}
        '''
        value = CognitoUserPoolAdminCreateUserConfig(
            allow_admin_create_user_only=allow_admin_create_user_only,
            invite_message_template=invite_message_template,
        )

        return typing.cast(None, jsii.invoke(self, "putAdminCreateUserConfig", [value]))

    @jsii.member(jsii_name="putDeviceConfiguration")
    def put_device_configuration(
        self,
        *,
        challenge_required_on_new_device: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        device_only_remembered_on_user_prompt: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param challenge_required_on_new_device: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#challenge_required_on_new_device CognitoUserPool#challenge_required_on_new_device}.
        :param device_only_remembered_on_user_prompt: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_only_remembered_on_user_prompt CognitoUserPool#device_only_remembered_on_user_prompt}.
        '''
        value = CognitoUserPoolDeviceConfiguration(
            challenge_required_on_new_device=challenge_required_on_new_device,
            device_only_remembered_on_user_prompt=device_only_remembered_on_user_prompt,
        )

        return typing.cast(None, jsii.invoke(self, "putDeviceConfiguration", [value]))

    @jsii.member(jsii_name="putEmailConfiguration")
    def put_email_configuration(
        self,
        *,
        configuration_set: typing.Optional[builtins.str] = None,
        email_sending_account: typing.Optional[builtins.str] = None,
        from_email_address: typing.Optional[builtins.str] = None,
        reply_to_email_address: typing.Optional[builtins.str] = None,
        source_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param configuration_set: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#configuration_set CognitoUserPool#configuration_set}.
        :param email_sending_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_sending_account CognitoUserPool#email_sending_account}.
        :param from_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#from_email_address CognitoUserPool#from_email_address}.
        :param reply_to_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#reply_to_email_address CognitoUserPool#reply_to_email_address}.
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#source_arn CognitoUserPool#source_arn}.
        '''
        value = CognitoUserPoolEmailConfiguration(
            configuration_set=configuration_set,
            email_sending_account=email_sending_account,
            from_email_address=from_email_address,
            reply_to_email_address=reply_to_email_address,
            source_arn=source_arn,
        )

        return typing.cast(None, jsii.invoke(self, "putEmailConfiguration", [value]))

    @jsii.member(jsii_name="putLambdaConfig")
    def put_lambda_config(
        self,
        *,
        create_auth_challenge: typing.Optional[builtins.str] = None,
        custom_email_sender: typing.Optional["CognitoUserPoolLambdaConfigCustomEmailSender"] = None,
        custom_message: typing.Optional[builtins.str] = None,
        custom_sms_sender: typing.Optional["CognitoUserPoolLambdaConfigCustomSmsSender"] = None,
        define_auth_challenge: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        post_authentication: typing.Optional[builtins.str] = None,
        post_confirmation: typing.Optional[builtins.str] = None,
        pre_authentication: typing.Optional[builtins.str] = None,
        pre_sign_up: typing.Optional[builtins.str] = None,
        pre_token_generation: typing.Optional[builtins.str] = None,
        user_migration: typing.Optional[builtins.str] = None,
        verify_auth_challenge_response: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#create_auth_challenge CognitoUserPool#create_auth_challenge}.
        :param custom_email_sender: custom_email_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_email_sender CognitoUserPool#custom_email_sender}
        :param custom_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_message CognitoUserPool#custom_message}.
        :param custom_sms_sender: custom_sms_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_sms_sender CognitoUserPool#custom_sms_sender}
        :param define_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#define_auth_challenge CognitoUserPool#define_auth_challenge}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#kms_key_id CognitoUserPool#kms_key_id}.
        :param post_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_authentication CognitoUserPool#post_authentication}.
        :param post_confirmation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_confirmation CognitoUserPool#post_confirmation}.
        :param pre_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_authentication CognitoUserPool#pre_authentication}.
        :param pre_sign_up: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_sign_up CognitoUserPool#pre_sign_up}.
        :param pre_token_generation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_token_generation CognitoUserPool#pre_token_generation}.
        :param user_migration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_migration CognitoUserPool#user_migration}.
        :param verify_auth_challenge_response: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verify_auth_challenge_response CognitoUserPool#verify_auth_challenge_response}.
        '''
        value = CognitoUserPoolLambdaConfig(
            create_auth_challenge=create_auth_challenge,
            custom_email_sender=custom_email_sender,
            custom_message=custom_message,
            custom_sms_sender=custom_sms_sender,
            define_auth_challenge=define_auth_challenge,
            kms_key_id=kms_key_id,
            post_authentication=post_authentication,
            post_confirmation=post_confirmation,
            pre_authentication=pre_authentication,
            pre_sign_up=pre_sign_up,
            pre_token_generation=pre_token_generation,
            user_migration=user_migration,
            verify_auth_challenge_response=verify_auth_challenge_response,
        )

        return typing.cast(None, jsii.invoke(self, "putLambdaConfig", [value]))

    @jsii.member(jsii_name="putPasswordPolicy")
    def put_password_policy(
        self,
        *,
        minimum_length: typing.Optional[jsii.Number] = None,
        require_lowercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_numbers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_symbols: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_uppercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        temporary_password_validity_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param minimum_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#minimum_length CognitoUserPool#minimum_length}.
        :param require_lowercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_lowercase CognitoUserPool#require_lowercase}.
        :param require_numbers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_numbers CognitoUserPool#require_numbers}.
        :param require_symbols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_symbols CognitoUserPool#require_symbols}.
        :param require_uppercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_uppercase CognitoUserPool#require_uppercase}.
        :param temporary_password_validity_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#temporary_password_validity_days CognitoUserPool#temporary_password_validity_days}.
        '''
        value = CognitoUserPoolPasswordPolicy(
            minimum_length=minimum_length,
            require_lowercase=require_lowercase,
            require_numbers=require_numbers,
            require_symbols=require_symbols,
            require_uppercase=require_uppercase,
            temporary_password_validity_days=temporary_password_validity_days,
        )

        return typing.cast(None, jsii.invoke(self, "putPasswordPolicy", [value]))

    @jsii.member(jsii_name="putSmsConfiguration")
    def put_sms_configuration(
        self,
        *,
        external_id: builtins.str,
        sns_caller_arn: builtins.str,
    ) -> None:
        '''
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#external_id CognitoUserPool#external_id}.
        :param sns_caller_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sns_caller_arn CognitoUserPool#sns_caller_arn}.
        '''
        value = CognitoUserPoolSmsConfiguration(
            external_id=external_id, sns_caller_arn=sns_caller_arn
        )

        return typing.cast(None, jsii.invoke(self, "putSmsConfiguration", [value]))

    @jsii.member(jsii_name="putSoftwareTokenMfaConfiguration")
    def put_software_token_mfa_configuration(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#enabled CognitoUserPool#enabled}.
        '''
        value = CognitoUserPoolSoftwareTokenMfaConfiguration(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putSoftwareTokenMfaConfiguration", [value]))

    @jsii.member(jsii_name="putUsernameConfiguration")
    def put_username_configuration(
        self,
        *,
        case_sensitive: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param case_sensitive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#case_sensitive CognitoUserPool#case_sensitive}.
        '''
        value = CognitoUserPoolUsernameConfiguration(case_sensitive=case_sensitive)

        return typing.cast(None, jsii.invoke(self, "putUsernameConfiguration", [value]))

    @jsii.member(jsii_name="putUserPoolAddOns")
    def put_user_pool_add_ons(self, *, advanced_security_mode: builtins.str) -> None:
        '''
        :param advanced_security_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#advanced_security_mode CognitoUserPool#advanced_security_mode}.
        '''
        value = CognitoUserPoolUserPoolAddOns(
            advanced_security_mode=advanced_security_mode
        )

        return typing.cast(None, jsii.invoke(self, "putUserPoolAddOns", [value]))

    @jsii.member(jsii_name="putVerificationMessageTemplate")
    def put_verification_message_template(
        self,
        *,
        default_email_option: typing.Optional[builtins.str] = None,
        email_message: typing.Optional[builtins.str] = None,
        email_message_by_link: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        email_subject_by_link: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_email_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#default_email_option CognitoUserPool#default_email_option}.
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_message_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message_by_link CognitoUserPool#email_message_by_link}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param email_subject_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject_by_link CognitoUserPool#email_subject_by_link}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        value = CognitoUserPoolVerificationMessageTemplate(
            default_email_option=default_email_option,
            email_message=email_message,
            email_message_by_link=email_message_by_link,
            email_subject=email_subject,
            email_subject_by_link=email_subject_by_link,
            sms_message=sms_message,
        )

        return typing.cast(None, jsii.invoke(self, "putVerificationMessageTemplate", [value]))

    @jsii.member(jsii_name="resetAccountRecoverySetting")
    def reset_account_recovery_setting(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountRecoverySetting", []))

    @jsii.member(jsii_name="resetAdminCreateUserConfig")
    def reset_admin_create_user_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminCreateUserConfig", []))

    @jsii.member(jsii_name="resetAliasAttributes")
    def reset_alias_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasAttributes", []))

    @jsii.member(jsii_name="resetAutoVerifiedAttributes")
    def reset_auto_verified_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoVerifiedAttributes", []))

    @jsii.member(jsii_name="resetDeviceConfiguration")
    def reset_device_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceConfiguration", []))

    @jsii.member(jsii_name="resetEmailConfiguration")
    def reset_email_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailConfiguration", []))

    @jsii.member(jsii_name="resetEmailVerificationMessage")
    def reset_email_verification_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailVerificationMessage", []))

    @jsii.member(jsii_name="resetEmailVerificationSubject")
    def reset_email_verification_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailVerificationSubject", []))

    @jsii.member(jsii_name="resetLambdaConfig")
    def reset_lambda_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaConfig", []))

    @jsii.member(jsii_name="resetMfaConfiguration")
    def reset_mfa_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaConfiguration", []))

    @jsii.member(jsii_name="resetPasswordPolicy")
    def reset_password_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordPolicy", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetSmsAuthenticationMessage")
    def reset_sms_authentication_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsAuthenticationMessage", []))

    @jsii.member(jsii_name="resetSmsConfiguration")
    def reset_sms_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsConfiguration", []))

    @jsii.member(jsii_name="resetSmsVerificationMessage")
    def reset_sms_verification_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsVerificationMessage", []))

    @jsii.member(jsii_name="resetSoftwareTokenMfaConfiguration")
    def reset_software_token_mfa_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSoftwareTokenMfaConfiguration", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUsernameAttributes")
    def reset_username_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameAttributes", []))

    @jsii.member(jsii_name="resetUsernameConfiguration")
    def reset_username_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameConfiguration", []))

    @jsii.member(jsii_name="resetUserPoolAddOns")
    def reset_user_pool_add_ons(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserPoolAddOns", []))

    @jsii.member(jsii_name="resetVerificationMessageTemplate")
    def reset_verification_message_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerificationMessageTemplate", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountRecoverySetting")
    def account_recovery_setting(
        self,
    ) -> "CognitoUserPoolAccountRecoverySettingOutputReference":
        return typing.cast("CognitoUserPoolAccountRecoverySettingOutputReference", jsii.get(self, "accountRecoverySetting"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminCreateUserConfig")
    def admin_create_user_config(
        self,
    ) -> "CognitoUserPoolAdminCreateUserConfigOutputReference":
        return typing.cast("CognitoUserPoolAdminCreateUserConfigOutputReference", jsii.get(self, "adminCreateUserConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDomain")
    def custom_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceConfiguration")
    def device_configuration(
        self,
    ) -> "CognitoUserPoolDeviceConfigurationOutputReference":
        return typing.cast("CognitoUserPoolDeviceConfigurationOutputReference", jsii.get(self, "deviceConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailConfiguration")
    def email_configuration(self) -> "CognitoUserPoolEmailConfigurationOutputReference":
        return typing.cast("CognitoUserPoolEmailConfigurationOutputReference", jsii.get(self, "emailConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="estimatedNumberOfUsers")
    def estimated_number_of_users(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "estimatedNumberOfUsers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaConfig")
    def lambda_config(self) -> "CognitoUserPoolLambdaConfigOutputReference":
        return typing.cast("CognitoUserPoolLambdaConfigOutputReference", jsii.get(self, "lambdaConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordPolicy")
    def password_policy(self) -> "CognitoUserPoolPasswordPolicyOutputReference":
        return typing.cast("CognitoUserPoolPasswordPolicyOutputReference", jsii.get(self, "passwordPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsConfiguration")
    def sms_configuration(self) -> "CognitoUserPoolSmsConfigurationOutputReference":
        return typing.cast("CognitoUserPoolSmsConfigurationOutputReference", jsii.get(self, "smsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="softwareTokenMfaConfiguration")
    def software_token_mfa_configuration(
        self,
    ) -> "CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference":
        return typing.cast("CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference", jsii.get(self, "softwareTokenMfaConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameConfiguration")
    def username_configuration(
        self,
    ) -> "CognitoUserPoolUsernameConfigurationOutputReference":
        return typing.cast("CognitoUserPoolUsernameConfigurationOutputReference", jsii.get(self, "usernameConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolAddOns")
    def user_pool_add_ons(self) -> "CognitoUserPoolUserPoolAddOnsOutputReference":
        return typing.cast("CognitoUserPoolUserPoolAddOnsOutputReference", jsii.get(self, "userPoolAddOns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationMessageTemplate")
    def verification_message_template(
        self,
    ) -> "CognitoUserPoolVerificationMessageTemplateOutputReference":
        return typing.cast("CognitoUserPoolVerificationMessageTemplateOutputReference", jsii.get(self, "verificationMessageTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountRecoverySettingInput")
    def account_recovery_setting_input(
        self,
    ) -> typing.Optional["CognitoUserPoolAccountRecoverySetting"]:
        return typing.cast(typing.Optional["CognitoUserPoolAccountRecoverySetting"], jsii.get(self, "accountRecoverySettingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminCreateUserConfigInput")
    def admin_create_user_config_input(
        self,
    ) -> typing.Optional["CognitoUserPoolAdminCreateUserConfig"]:
        return typing.cast(typing.Optional["CognitoUserPoolAdminCreateUserConfig"], jsii.get(self, "adminCreateUserConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasAttributesInput")
    def alias_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "aliasAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoVerifiedAttributesInput")
    def auto_verified_attributes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "autoVerifiedAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceConfigurationInput")
    def device_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolDeviceConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolDeviceConfiguration"], jsii.get(self, "deviceConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailConfigurationInput")
    def email_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolEmailConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolEmailConfiguration"], jsii.get(self, "emailConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationMessageInput")
    def email_verification_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailVerificationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationSubjectInput")
    def email_verification_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailVerificationSubjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaConfigInput")
    def lambda_config_input(self) -> typing.Optional["CognitoUserPoolLambdaConfig"]:
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfig"], jsii.get(self, "lambdaConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaConfigurationInput")
    def mfa_configuration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mfaConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordPolicyInput")
    def password_policy_input(self) -> typing.Optional["CognitoUserPoolPasswordPolicy"]:
        return typing.cast(typing.Optional["CognitoUserPoolPasswordPolicy"], jsii.get(self, "passwordPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[typing.List["CognitoUserPoolSchema"]]:
        return typing.cast(typing.Optional[typing.List["CognitoUserPoolSchema"]], jsii.get(self, "schemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsAuthenticationMessageInput")
    def sms_authentication_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsAuthenticationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsConfigurationInput")
    def sms_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolSmsConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolSmsConfiguration"], jsii.get(self, "smsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsVerificationMessageInput")
    def sms_verification_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsVerificationMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="softwareTokenMfaConfigurationInput")
    def software_token_mfa_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"], jsii.get(self, "softwareTokenMfaConfigurationInput"))

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
    @jsii.member(jsii_name="usernameAttributesInput")
    def username_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usernameAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameConfigurationInput")
    def username_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolUsernameConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolUsernameConfiguration"], jsii.get(self, "usernameConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolAddOnsInput")
    def user_pool_add_ons_input(
        self,
    ) -> typing.Optional["CognitoUserPoolUserPoolAddOns"]:
        return typing.cast(typing.Optional["CognitoUserPoolUserPoolAddOns"], jsii.get(self, "userPoolAddOnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationMessageTemplateInput")
    def verification_message_template_input(
        self,
    ) -> typing.Optional["CognitoUserPoolVerificationMessageTemplate"]:
        return typing.cast(typing.Optional["CognitoUserPoolVerificationMessageTemplate"], jsii.get(self, "verificationMessageTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasAttributes")
    def alias_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliasAttributes"))

    @alias_attributes.setter
    def alias_attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "aliasAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoVerifiedAttributes")
    def auto_verified_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "autoVerifiedAttributes"))

    @auto_verified_attributes.setter
    def auto_verified_attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "autoVerifiedAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationMessage")
    def email_verification_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailVerificationMessage"))

    @email_verification_message.setter
    def email_verification_message(self, value: builtins.str) -> None:
        jsii.set(self, "emailVerificationMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailVerificationSubject")
    def email_verification_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailVerificationSubject"))

    @email_verification_subject.setter
    def email_verification_subject(self, value: builtins.str) -> None:
        jsii.set(self, "emailVerificationSubject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaConfiguration")
    def mfa_configuration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mfaConfiguration"))

    @mfa_configuration.setter
    def mfa_configuration(self, value: builtins.str) -> None:
        jsii.set(self, "mfaConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> typing.List["CognitoUserPoolSchema"]:
        return typing.cast(typing.List["CognitoUserPoolSchema"], jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: typing.List["CognitoUserPoolSchema"]) -> None:
        jsii.set(self, "schema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsAuthenticationMessage")
    def sms_authentication_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsAuthenticationMessage"))

    @sms_authentication_message.setter
    def sms_authentication_message(self, value: builtins.str) -> None:
        jsii.set(self, "smsAuthenticationMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsVerificationMessage")
    def sms_verification_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsVerificationMessage"))

    @sms_verification_message.setter
    def sms_verification_message(self, value: builtins.str) -> None:
        jsii.set(self, "smsVerificationMessage", value)

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
    @jsii.member(jsii_name="usernameAttributes")
    def username_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usernameAttributes"))

    @username_attributes.setter
    def username_attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "usernameAttributes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySetting",
    jsii_struct_bases=[],
    name_mapping={"recovery_mechanism": "recoveryMechanism"},
)
class CognitoUserPoolAccountRecoverySetting:
    def __init__(
        self,
        *,
        recovery_mechanism: typing.Sequence["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"],
    ) -> None:
        '''
        :param recovery_mechanism: recovery_mechanism block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#recovery_mechanism CognitoUserPool#recovery_mechanism}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "recovery_mechanism": recovery_mechanism,
        }

    @builtins.property
    def recovery_mechanism(
        self,
    ) -> typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]:
        '''recovery_mechanism block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#recovery_mechanism CognitoUserPool#recovery_mechanism}
        '''
        result = self._values.get("recovery_mechanism")
        assert result is not None, "Required property 'recovery_mechanism' is missing"
        return typing.cast(typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAccountRecoverySetting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolAccountRecoverySettingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySettingOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recoveryMechanismInput")
    def recovery_mechanism_input(
        self,
    ) -> typing.Optional[typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]]:
        return typing.cast(typing.Optional[typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]], jsii.get(self, "recoveryMechanismInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recoveryMechanism")
    def recovery_mechanism(
        self,
    ) -> typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"]:
        return typing.cast(typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"], jsii.get(self, "recoveryMechanism"))

    @recovery_mechanism.setter
    def recovery_mechanism(
        self,
        value: typing.List["CognitoUserPoolAccountRecoverySettingRecoveryMechanism"],
    ) -> None:
        jsii.set(self, "recoveryMechanism", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolAccountRecoverySetting]:
        return typing.cast(typing.Optional[CognitoUserPoolAccountRecoverySetting], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolAccountRecoverySetting],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAccountRecoverySettingRecoveryMechanism",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "priority": "priority"},
)
class CognitoUserPoolAccountRecoverySettingRecoveryMechanism:
    def __init__(self, *, name: builtins.str, priority: jsii.Number) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#priority CognitoUserPool#priority}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "priority": priority,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#priority CognitoUserPool#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAccountRecoverySettingRecoveryMechanism(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfig",
    jsii_struct_bases=[],
    name_mapping={
        "allow_admin_create_user_only": "allowAdminCreateUserOnly",
        "invite_message_template": "inviteMessageTemplate",
    },
)
class CognitoUserPoolAdminCreateUserConfig:
    def __init__(
        self,
        *,
        allow_admin_create_user_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invite_message_template: typing.Optional["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate"] = None,
    ) -> None:
        '''
        :param allow_admin_create_user_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#allow_admin_create_user_only CognitoUserPool#allow_admin_create_user_only}.
        :param invite_message_template: invite_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#invite_message_template CognitoUserPool#invite_message_template}
        '''
        if isinstance(invite_message_template, dict):
            invite_message_template = CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate(**invite_message_template)
        self._values: typing.Dict[str, typing.Any] = {}
        if allow_admin_create_user_only is not None:
            self._values["allow_admin_create_user_only"] = allow_admin_create_user_only
        if invite_message_template is not None:
            self._values["invite_message_template"] = invite_message_template

    @builtins.property
    def allow_admin_create_user_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#allow_admin_create_user_only CognitoUserPool#allow_admin_create_user_only}.'''
        result = self._values.get("allow_admin_create_user_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def invite_message_template(
        self,
    ) -> typing.Optional["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate"]:
        '''invite_message_template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#invite_message_template CognitoUserPool#invite_message_template}
        '''
        result = self._values.get("invite_message_template")
        return typing.cast(typing.Optional["CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAdminCreateUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "email_message": "emailMessage",
        "email_subject": "emailSubject",
        "sms_message": "smsMessage",
    },
)
class CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate:
    def __init__(
        self,
        *,
        email_message: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if email_message is not None:
            self._values["email_message"] = email_message
        if email_subject is not None:
            self._values["email_subject"] = email_subject
        if sms_message is not None:
            self._values["sms_message"] = sms_message

    @builtins.property
    def email_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.'''
        result = self._values.get("email_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.'''
        result = self._values.get("email_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.'''
        result = self._values.get("sms_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference",
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

    @jsii.member(jsii_name="resetEmailMessage")
    def reset_email_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailMessage", []))

    @jsii.member(jsii_name="resetEmailSubject")
    def reset_email_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSubject", []))

    @jsii.member(jsii_name="resetSmsMessage")
    def reset_sms_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsMessage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageInput")
    def email_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectInput")
    def email_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSubjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessageInput")
    def sms_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessage")
    def email_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailMessage"))

    @email_message.setter
    def email_message(self, value: builtins.str) -> None:
        jsii.set(self, "emailMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubject")
    def email_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSubject"))

    @email_subject.setter
    def email_subject(self, value: builtins.str) -> None:
        jsii.set(self, "emailSubject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessage")
    def sms_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsMessage"))

    @sms_message.setter
    def sms_message(self, value: builtins.str) -> None:
        jsii.set(self, "smsMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate]:
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CognitoUserPoolAdminCreateUserConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolAdminCreateUserConfigOutputReference",
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

    @jsii.member(jsii_name="putInviteMessageTemplate")
    def put_invite_message_template(
        self,
        *,
        email_message: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        value = CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate(
            email_message=email_message,
            email_subject=email_subject,
            sms_message=sms_message,
        )

        return typing.cast(None, jsii.invoke(self, "putInviteMessageTemplate", [value]))

    @jsii.member(jsii_name="resetAllowAdminCreateUserOnly")
    def reset_allow_admin_create_user_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAdminCreateUserOnly", []))

    @jsii.member(jsii_name="resetInviteMessageTemplate")
    def reset_invite_message_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInviteMessageTemplate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inviteMessageTemplate")
    def invite_message_template(
        self,
    ) -> CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference:
        return typing.cast(CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference, jsii.get(self, "inviteMessageTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowAdminCreateUserOnlyInput")
    def allow_admin_create_user_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowAdminCreateUserOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inviteMessageTemplateInput")
    def invite_message_template_input(
        self,
    ) -> typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate]:
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate], jsii.get(self, "inviteMessageTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowAdminCreateUserOnly")
    def allow_admin_create_user_only(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowAdminCreateUserOnly"))

    @allow_admin_create_user_only.setter
    def allow_admin_create_user_only(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowAdminCreateUserOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolAdminCreateUserConfig]:
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolAdminCreateUserConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CognitoUserPoolClient(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClient",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client aws_cognito_user_pool_client}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        user_pool_id: builtins.str,
        access_token_validity: typing.Optional[jsii.Number] = None,
        allowed_oauth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_oauth_flows_user_pool_client: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allowed_oauth_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        analytics_configuration: typing.Optional["CognitoUserPoolClientAnalyticsConfiguration"] = None,
        callback_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_redirect_uri: typing.Optional[builtins.str] = None,
        enable_token_revocation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        explicit_auth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_secret: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id_token_validity: typing.Optional[jsii.Number] = None,
        logout_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        prevent_user_existence_errors: typing.Optional[builtins.str] = None,
        read_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        refresh_token_validity: typing.Optional[jsii.Number] = None,
        supported_identity_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_validity_units: typing.Optional["CognitoUserPoolClientTokenValidityUnits"] = None,
        write_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client aws_cognito_user_pool_client} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#name CognitoUserPoolClient#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_pool_id CognitoUserPoolClient#user_pool_id}.
        :param access_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token_validity CognitoUserPoolClient#access_token_validity}.
        :param allowed_oauth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows CognitoUserPoolClient#allowed_oauth_flows}.
        :param allowed_oauth_flows_user_pool_client: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows_user_pool_client CognitoUserPoolClient#allowed_oauth_flows_user_pool_client}.
        :param allowed_oauth_scopes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_scopes CognitoUserPoolClient#allowed_oauth_scopes}.
        :param analytics_configuration: analytics_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#analytics_configuration CognitoUserPoolClient#analytics_configuration}
        :param callback_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#callback_urls CognitoUserPoolClient#callback_urls}.
        :param default_redirect_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#default_redirect_uri CognitoUserPoolClient#default_redirect_uri}.
        :param enable_token_revocation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_token_revocation CognitoUserPoolClient#enable_token_revocation}.
        :param explicit_auth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#explicit_auth_flows CognitoUserPoolClient#explicit_auth_flows}.
        :param generate_secret: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#generate_secret CognitoUserPoolClient#generate_secret}.
        :param id_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token_validity CognitoUserPoolClient#id_token_validity}.
        :param logout_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#logout_urls CognitoUserPoolClient#logout_urls}.
        :param prevent_user_existence_errors: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#prevent_user_existence_errors CognitoUserPoolClient#prevent_user_existence_errors}.
        :param read_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#read_attributes CognitoUserPoolClient#read_attributes}.
        :param refresh_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token_validity CognitoUserPoolClient#refresh_token_validity}.
        :param supported_identity_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#supported_identity_providers CognitoUserPoolClient#supported_identity_providers}.
        :param token_validity_units: token_validity_units block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#token_validity_units CognitoUserPoolClient#token_validity_units}
        :param write_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#write_attributes CognitoUserPoolClient#write_attributes}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoUserPoolClientConfig(
            name=name,
            user_pool_id=user_pool_id,
            access_token_validity=access_token_validity,
            allowed_oauth_flows=allowed_oauth_flows,
            allowed_oauth_flows_user_pool_client=allowed_oauth_flows_user_pool_client,
            allowed_oauth_scopes=allowed_oauth_scopes,
            analytics_configuration=analytics_configuration,
            callback_urls=callback_urls,
            default_redirect_uri=default_redirect_uri,
            enable_token_revocation=enable_token_revocation,
            explicit_auth_flows=explicit_auth_flows,
            generate_secret=generate_secret,
            id_token_validity=id_token_validity,
            logout_urls=logout_urls,
            prevent_user_existence_errors=prevent_user_existence_errors,
            read_attributes=read_attributes,
            refresh_token_validity=refresh_token_validity,
            supported_identity_providers=supported_identity_providers,
            token_validity_units=token_validity_units,
            write_attributes=write_attributes,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAnalyticsConfiguration")
    def put_analytics_configuration(
        self,
        *,
        application_arn: typing.Optional[builtins.str] = None,
        application_id: typing.Optional[builtins.str] = None,
        external_id: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        user_data_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param application_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_arn CognitoUserPoolClient#application_arn}.
        :param application_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_id CognitoUserPoolClient#application_id}.
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#external_id CognitoUserPoolClient#external_id}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#role_arn CognitoUserPoolClient#role_arn}.
        :param user_data_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_data_shared CognitoUserPoolClient#user_data_shared}.
        '''
        value = CognitoUserPoolClientAnalyticsConfiguration(
            application_arn=application_arn,
            application_id=application_id,
            external_id=external_id,
            role_arn=role_arn,
            user_data_shared=user_data_shared,
        )

        return typing.cast(None, jsii.invoke(self, "putAnalyticsConfiguration", [value]))

    @jsii.member(jsii_name="putTokenValidityUnits")
    def put_token_validity_units(
        self,
        *,
        access_token: typing.Optional[builtins.str] = None,
        id_token: typing.Optional[builtins.str] = None,
        refresh_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token CognitoUserPoolClient#access_token}.
        :param id_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token CognitoUserPoolClient#id_token}.
        :param refresh_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token CognitoUserPoolClient#refresh_token}.
        '''
        value = CognitoUserPoolClientTokenValidityUnits(
            access_token=access_token, id_token=id_token, refresh_token=refresh_token
        )

        return typing.cast(None, jsii.invoke(self, "putTokenValidityUnits", [value]))

    @jsii.member(jsii_name="resetAccessTokenValidity")
    def reset_access_token_validity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessTokenValidity", []))

    @jsii.member(jsii_name="resetAllowedOauthFlows")
    def reset_allowed_oauth_flows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOauthFlows", []))

    @jsii.member(jsii_name="resetAllowedOauthFlowsUserPoolClient")
    def reset_allowed_oauth_flows_user_pool_client(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOauthFlowsUserPoolClient", []))

    @jsii.member(jsii_name="resetAllowedOauthScopes")
    def reset_allowed_oauth_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOauthScopes", []))

    @jsii.member(jsii_name="resetAnalyticsConfiguration")
    def reset_analytics_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalyticsConfiguration", []))

    @jsii.member(jsii_name="resetCallbackUrls")
    def reset_callback_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCallbackUrls", []))

    @jsii.member(jsii_name="resetDefaultRedirectUri")
    def reset_default_redirect_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRedirectUri", []))

    @jsii.member(jsii_name="resetEnableTokenRevocation")
    def reset_enable_token_revocation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableTokenRevocation", []))

    @jsii.member(jsii_name="resetExplicitAuthFlows")
    def reset_explicit_auth_flows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExplicitAuthFlows", []))

    @jsii.member(jsii_name="resetGenerateSecret")
    def reset_generate_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateSecret", []))

    @jsii.member(jsii_name="resetIdTokenValidity")
    def reset_id_token_validity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdTokenValidity", []))

    @jsii.member(jsii_name="resetLogoutUrls")
    def reset_logout_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogoutUrls", []))

    @jsii.member(jsii_name="resetPreventUserExistenceErrors")
    def reset_prevent_user_existence_errors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreventUserExistenceErrors", []))

    @jsii.member(jsii_name="resetReadAttributes")
    def reset_read_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadAttributes", []))

    @jsii.member(jsii_name="resetRefreshTokenValidity")
    def reset_refresh_token_validity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshTokenValidity", []))

    @jsii.member(jsii_name="resetSupportedIdentityProviders")
    def reset_supported_identity_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportedIdentityProviders", []))

    @jsii.member(jsii_name="resetTokenValidityUnits")
    def reset_token_validity_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenValidityUnits", []))

    @jsii.member(jsii_name="resetWriteAttributes")
    def reset_write_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWriteAttributes", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyticsConfiguration")
    def analytics_configuration(
        self,
    ) -> "CognitoUserPoolClientAnalyticsConfigurationOutputReference":
        return typing.cast("CognitoUserPoolClientAnalyticsConfigurationOutputReference", jsii.get(self, "analyticsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenValidityUnits")
    def token_validity_units(
        self,
    ) -> "CognitoUserPoolClientTokenValidityUnitsOutputReference":
        return typing.cast("CognitoUserPoolClientTokenValidityUnitsOutputReference", jsii.get(self, "tokenValidityUnits"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenValidityInput")
    def access_token_validity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessTokenValidityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsInput")
    def allowed_oauth_flows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOauthFlowsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsUserPoolClientInput")
    def allowed_oauth_flows_user_pool_client_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowedOauthFlowsUserPoolClientInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthScopesInput")
    def allowed_oauth_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOauthScopesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyticsConfigurationInput")
    def analytics_configuration_input(
        self,
    ) -> typing.Optional["CognitoUserPoolClientAnalyticsConfiguration"]:
        return typing.cast(typing.Optional["CognitoUserPoolClientAnalyticsConfiguration"], jsii.get(self, "analyticsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callbackUrlsInput")
    def callback_urls_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "callbackUrlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRedirectUriInput")
    def default_redirect_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultRedirectUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTokenRevocationInput")
    def enable_token_revocation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableTokenRevocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="explicitAuthFlowsInput")
    def explicit_auth_flows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "explicitAuthFlowsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecretInput")
    def generate_secret_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "generateSecretInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenValidityInput")
    def id_token_validity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idTokenValidityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logoutUrlsInput")
    def logout_urls_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "logoutUrlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preventUserExistenceErrorsInput")
    def prevent_user_existence_errors_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preventUserExistenceErrorsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readAttributesInput")
    def read_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "readAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenValidityInput")
    def refresh_token_validity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "refreshTokenValidityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedIdentityProvidersInput")
    def supported_identity_providers_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "supportedIdentityProvidersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenValidityUnitsInput")
    def token_validity_units_input(
        self,
    ) -> typing.Optional["CognitoUserPoolClientTokenValidityUnits"]:
        return typing.cast(typing.Optional["CognitoUserPoolClientTokenValidityUnits"], jsii.get(self, "tokenValidityUnitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeAttributesInput")
    def write_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "writeAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenValidity")
    def access_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessTokenValidity"))

    @access_token_validity.setter
    def access_token_validity(self, value: jsii.Number) -> None:
        jsii.set(self, "accessTokenValidity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlows")
    def allowed_oauth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthFlows"))

    @allowed_oauth_flows.setter
    def allowed_oauth_flows(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedOauthFlows", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsUserPoolClient")
    def allowed_oauth_flows_user_pool_client(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowedOauthFlowsUserPoolClient"))

    @allowed_oauth_flows_user_pool_client.setter
    def allowed_oauth_flows_user_pool_client(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowedOauthFlowsUserPoolClient", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthScopes")
    def allowed_oauth_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthScopes"))

    @allowed_oauth_scopes.setter
    def allowed_oauth_scopes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedOauthScopes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callbackUrls")
    def callback_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "callbackUrls"))

    @callback_urls.setter
    def callback_urls(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "callbackUrls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRedirectUri")
    def default_redirect_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRedirectUri"))

    @default_redirect_uri.setter
    def default_redirect_uri(self, value: builtins.str) -> None:
        jsii.set(self, "defaultRedirectUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTokenRevocation")
    def enable_token_revocation(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableTokenRevocation"))

    @enable_token_revocation.setter
    def enable_token_revocation(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableTokenRevocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="explicitAuthFlows")
    def explicit_auth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "explicitAuthFlows"))

    @explicit_auth_flows.setter
    def explicit_auth_flows(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "explicitAuthFlows", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecret")
    def generate_secret(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "generateSecret"))

    @generate_secret.setter
    def generate_secret(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "generateSecret", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenValidity")
    def id_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idTokenValidity"))

    @id_token_validity.setter
    def id_token_validity(self, value: jsii.Number) -> None:
        jsii.set(self, "idTokenValidity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logoutUrls")
    def logout_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logoutUrls"))

    @logout_urls.setter
    def logout_urls(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "logoutUrls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preventUserExistenceErrors")
    def prevent_user_existence_errors(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preventUserExistenceErrors"))

    @prevent_user_existence_errors.setter
    def prevent_user_existence_errors(self, value: builtins.str) -> None:
        jsii.set(self, "preventUserExistenceErrors", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readAttributes")
    def read_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "readAttributes"))

    @read_attributes.setter
    def read_attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "readAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenValidity")
    def refresh_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshTokenValidity"))

    @refresh_token_validity.setter
    def refresh_token_validity(self, value: jsii.Number) -> None:
        jsii.set(self, "refreshTokenValidity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedIdentityProviders")
    def supported_identity_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedIdentityProviders"))

    @supported_identity_providers.setter
    def supported_identity_providers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "supportedIdentityProviders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeAttributes")
    def write_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "writeAttributes"))

    @write_attributes.setter
    def write_attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "writeAttributes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientAnalyticsConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "application_arn": "applicationArn",
        "application_id": "applicationId",
        "external_id": "externalId",
        "role_arn": "roleArn",
        "user_data_shared": "userDataShared",
    },
)
class CognitoUserPoolClientAnalyticsConfiguration:
    def __init__(
        self,
        *,
        application_arn: typing.Optional[builtins.str] = None,
        application_id: typing.Optional[builtins.str] = None,
        external_id: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        user_data_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param application_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_arn CognitoUserPoolClient#application_arn}.
        :param application_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_id CognitoUserPoolClient#application_id}.
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#external_id CognitoUserPoolClient#external_id}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#role_arn CognitoUserPoolClient#role_arn}.
        :param user_data_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_data_shared CognitoUserPoolClient#user_data_shared}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if application_arn is not None:
            self._values["application_arn"] = application_arn
        if application_id is not None:
            self._values["application_id"] = application_id
        if external_id is not None:
            self._values["external_id"] = external_id
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if user_data_shared is not None:
            self._values["user_data_shared"] = user_data_shared

    @builtins.property
    def application_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_arn CognitoUserPoolClient#application_arn}.'''
        result = self._values.get("application_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#application_id CognitoUserPoolClient#application_id}.'''
        result = self._values.get("application_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#external_id CognitoUserPoolClient#external_id}.'''
        result = self._values.get("external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#role_arn CognitoUserPoolClient#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_data_shared(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_data_shared CognitoUserPoolClient#user_data_shared}.'''
        result = self._values.get("user_data_shared")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolClientAnalyticsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolClientAnalyticsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientAnalyticsConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetApplicationArn")
    def reset_application_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationArn", []))

    @jsii.member(jsii_name="resetApplicationId")
    def reset_application_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationId", []))

    @jsii.member(jsii_name="resetExternalId")
    def reset_external_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalId", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="resetUserDataShared")
    def reset_user_data_shared(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDataShared", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArnInput")
    def application_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationIdInput")
    def application_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataSharedInput")
    def user_data_shared_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "userDataSharedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @application_arn.setter
    def application_arn(self, value: builtins.str) -> None:
        jsii.set(self, "applicationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @application_id.setter
    def application_id(self, value: builtins.str) -> None:
        jsii.set(self, "applicationId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        jsii.set(self, "externalId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataShared")
    def user_data_shared(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "userDataShared"))

    @user_data_shared.setter
    def user_data_shared(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "userDataShared", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolClientAnalyticsConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolClientAnalyticsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolClientAnalyticsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "user_pool_id": "userPoolId",
        "access_token_validity": "accessTokenValidity",
        "allowed_oauth_flows": "allowedOauthFlows",
        "allowed_oauth_flows_user_pool_client": "allowedOauthFlowsUserPoolClient",
        "allowed_oauth_scopes": "allowedOauthScopes",
        "analytics_configuration": "analyticsConfiguration",
        "callback_urls": "callbackUrls",
        "default_redirect_uri": "defaultRedirectUri",
        "enable_token_revocation": "enableTokenRevocation",
        "explicit_auth_flows": "explicitAuthFlows",
        "generate_secret": "generateSecret",
        "id_token_validity": "idTokenValidity",
        "logout_urls": "logoutUrls",
        "prevent_user_existence_errors": "preventUserExistenceErrors",
        "read_attributes": "readAttributes",
        "refresh_token_validity": "refreshTokenValidity",
        "supported_identity_providers": "supportedIdentityProviders",
        "token_validity_units": "tokenValidityUnits",
        "write_attributes": "writeAttributes",
    },
)
class CognitoUserPoolClientConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        user_pool_id: builtins.str,
        access_token_validity: typing.Optional[jsii.Number] = None,
        allowed_oauth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_oauth_flows_user_pool_client: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allowed_oauth_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        analytics_configuration: typing.Optional[CognitoUserPoolClientAnalyticsConfiguration] = None,
        callback_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_redirect_uri: typing.Optional[builtins.str] = None,
        enable_token_revocation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        explicit_auth_flows: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_secret: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id_token_validity: typing.Optional[jsii.Number] = None,
        logout_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        prevent_user_existence_errors: typing.Optional[builtins.str] = None,
        read_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        refresh_token_validity: typing.Optional[jsii.Number] = None,
        supported_identity_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_validity_units: typing.Optional["CognitoUserPoolClientTokenValidityUnits"] = None,
        write_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#name CognitoUserPoolClient#name}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_pool_id CognitoUserPoolClient#user_pool_id}.
        :param access_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token_validity CognitoUserPoolClient#access_token_validity}.
        :param allowed_oauth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows CognitoUserPoolClient#allowed_oauth_flows}.
        :param allowed_oauth_flows_user_pool_client: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows_user_pool_client CognitoUserPoolClient#allowed_oauth_flows_user_pool_client}.
        :param allowed_oauth_scopes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_scopes CognitoUserPoolClient#allowed_oauth_scopes}.
        :param analytics_configuration: analytics_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#analytics_configuration CognitoUserPoolClient#analytics_configuration}
        :param callback_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#callback_urls CognitoUserPoolClient#callback_urls}.
        :param default_redirect_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#default_redirect_uri CognitoUserPoolClient#default_redirect_uri}.
        :param enable_token_revocation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_token_revocation CognitoUserPoolClient#enable_token_revocation}.
        :param explicit_auth_flows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#explicit_auth_flows CognitoUserPoolClient#explicit_auth_flows}.
        :param generate_secret: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#generate_secret CognitoUserPoolClient#generate_secret}.
        :param id_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token_validity CognitoUserPoolClient#id_token_validity}.
        :param logout_urls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#logout_urls CognitoUserPoolClient#logout_urls}.
        :param prevent_user_existence_errors: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#prevent_user_existence_errors CognitoUserPoolClient#prevent_user_existence_errors}.
        :param read_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#read_attributes CognitoUserPoolClient#read_attributes}.
        :param refresh_token_validity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token_validity CognitoUserPoolClient#refresh_token_validity}.
        :param supported_identity_providers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#supported_identity_providers CognitoUserPoolClient#supported_identity_providers}.
        :param token_validity_units: token_validity_units block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#token_validity_units CognitoUserPoolClient#token_validity_units}
        :param write_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#write_attributes CognitoUserPoolClient#write_attributes}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(analytics_configuration, dict):
            analytics_configuration = CognitoUserPoolClientAnalyticsConfiguration(**analytics_configuration)
        if isinstance(token_validity_units, dict):
            token_validity_units = CognitoUserPoolClientTokenValidityUnits(**token_validity_units)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "user_pool_id": user_pool_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if access_token_validity is not None:
            self._values["access_token_validity"] = access_token_validity
        if allowed_oauth_flows is not None:
            self._values["allowed_oauth_flows"] = allowed_oauth_flows
        if allowed_oauth_flows_user_pool_client is not None:
            self._values["allowed_oauth_flows_user_pool_client"] = allowed_oauth_flows_user_pool_client
        if allowed_oauth_scopes is not None:
            self._values["allowed_oauth_scopes"] = allowed_oauth_scopes
        if analytics_configuration is not None:
            self._values["analytics_configuration"] = analytics_configuration
        if callback_urls is not None:
            self._values["callback_urls"] = callback_urls
        if default_redirect_uri is not None:
            self._values["default_redirect_uri"] = default_redirect_uri
        if enable_token_revocation is not None:
            self._values["enable_token_revocation"] = enable_token_revocation
        if explicit_auth_flows is not None:
            self._values["explicit_auth_flows"] = explicit_auth_flows
        if generate_secret is not None:
            self._values["generate_secret"] = generate_secret
        if id_token_validity is not None:
            self._values["id_token_validity"] = id_token_validity
        if logout_urls is not None:
            self._values["logout_urls"] = logout_urls
        if prevent_user_existence_errors is not None:
            self._values["prevent_user_existence_errors"] = prevent_user_existence_errors
        if read_attributes is not None:
            self._values["read_attributes"] = read_attributes
        if refresh_token_validity is not None:
            self._values["refresh_token_validity"] = refresh_token_validity
        if supported_identity_providers is not None:
            self._values["supported_identity_providers"] = supported_identity_providers
        if token_validity_units is not None:
            self._values["token_validity_units"] = token_validity_units
        if write_attributes is not None:
            self._values["write_attributes"] = write_attributes

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#name CognitoUserPoolClient#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#user_pool_id CognitoUserPoolClient#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token_validity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token_validity CognitoUserPoolClient#access_token_validity}.'''
        result = self._values.get("access_token_validity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allowed_oauth_flows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows CognitoUserPoolClient#allowed_oauth_flows}.'''
        result = self._values.get("allowed_oauth_flows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_oauth_flows_user_pool_client(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_flows_user_pool_client CognitoUserPoolClient#allowed_oauth_flows_user_pool_client}.'''
        result = self._values.get("allowed_oauth_flows_user_pool_client")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def allowed_oauth_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#allowed_oauth_scopes CognitoUserPoolClient#allowed_oauth_scopes}.'''
        result = self._values.get("allowed_oauth_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def analytics_configuration(
        self,
    ) -> typing.Optional[CognitoUserPoolClientAnalyticsConfiguration]:
        '''analytics_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#analytics_configuration CognitoUserPoolClient#analytics_configuration}
        '''
        result = self._values.get("analytics_configuration")
        return typing.cast(typing.Optional[CognitoUserPoolClientAnalyticsConfiguration], result)

    @builtins.property
    def callback_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#callback_urls CognitoUserPoolClient#callback_urls}.'''
        result = self._values.get("callback_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_redirect_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#default_redirect_uri CognitoUserPoolClient#default_redirect_uri}.'''
        result = self._values.get("default_redirect_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_token_revocation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#enable_token_revocation CognitoUserPoolClient#enable_token_revocation}.'''
        result = self._values.get("enable_token_revocation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def explicit_auth_flows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#explicit_auth_flows CognitoUserPoolClient#explicit_auth_flows}.'''
        result = self._values.get("explicit_auth_flows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def generate_secret(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#generate_secret CognitoUserPoolClient#generate_secret}.'''
        result = self._values.get("generate_secret")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id_token_validity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token_validity CognitoUserPoolClient#id_token_validity}.'''
        result = self._values.get("id_token_validity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def logout_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#logout_urls CognitoUserPoolClient#logout_urls}.'''
        result = self._values.get("logout_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def prevent_user_existence_errors(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#prevent_user_existence_errors CognitoUserPoolClient#prevent_user_existence_errors}.'''
        result = self._values.get("prevent_user_existence_errors")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#read_attributes CognitoUserPoolClient#read_attributes}.'''
        result = self._values.get("read_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def refresh_token_validity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token_validity CognitoUserPoolClient#refresh_token_validity}.'''
        result = self._values.get("refresh_token_validity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def supported_identity_providers(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#supported_identity_providers CognitoUserPoolClient#supported_identity_providers}.'''
        result = self._values.get("supported_identity_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_validity_units(
        self,
    ) -> typing.Optional["CognitoUserPoolClientTokenValidityUnits"]:
        '''token_validity_units block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#token_validity_units CognitoUserPoolClient#token_validity_units}
        '''
        result = self._values.get("token_validity_units")
        return typing.cast(typing.Optional["CognitoUserPoolClientTokenValidityUnits"], result)

    @builtins.property
    def write_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#write_attributes CognitoUserPoolClient#write_attributes}.'''
        result = self._values.get("write_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolClientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientTokenValidityUnits",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "id_token": "idToken",
        "refresh_token": "refreshToken",
    },
)
class CognitoUserPoolClientTokenValidityUnits:
    def __init__(
        self,
        *,
        access_token: typing.Optional[builtins.str] = None,
        id_token: typing.Optional[builtins.str] = None,
        refresh_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token CognitoUserPoolClient#access_token}.
        :param id_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token CognitoUserPoolClient#id_token}.
        :param refresh_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token CognitoUserPoolClient#refresh_token}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if id_token is not None:
            self._values["id_token"] = id_token
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def access_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#access_token CognitoUserPoolClient#access_token}.'''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#id_token CognitoUserPoolClient#id_token}.'''
        result = self._values.get("id_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_client#refresh_token CognitoUserPoolClient#refresh_token}.'''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolClientTokenValidityUnits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolClientTokenValidityUnitsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolClientTokenValidityUnitsOutputReference",
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

    @jsii.member(jsii_name="resetAccessToken")
    def reset_access_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessToken", []))

    @jsii.member(jsii_name="resetIdToken")
    def reset_id_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdToken", []))

    @jsii.member(jsii_name="resetRefreshToken")
    def reset_refresh_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefreshToken", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenInput")
    def access_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenInput")
    def id_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenInput")
    def refresh_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "refreshTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(self, value: builtins.str) -> None:
        jsii.set(self, "accessToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idToken")
    def id_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idToken"))

    @id_token.setter
    def id_token(self, value: builtins.str) -> None:
        jsii.set(self, "idToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshToken")
    def refresh_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refreshToken"))

    @refresh_token.setter
    def refresh_token(self, value: builtins.str) -> None:
        jsii.set(self, "refreshToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolClientTokenValidityUnits]:
        return typing.cast(typing.Optional[CognitoUserPoolClientTokenValidityUnits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolClientTokenValidityUnits],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "account_recovery_setting": "accountRecoverySetting",
        "admin_create_user_config": "adminCreateUserConfig",
        "alias_attributes": "aliasAttributes",
        "auto_verified_attributes": "autoVerifiedAttributes",
        "device_configuration": "deviceConfiguration",
        "email_configuration": "emailConfiguration",
        "email_verification_message": "emailVerificationMessage",
        "email_verification_subject": "emailVerificationSubject",
        "lambda_config": "lambdaConfig",
        "mfa_configuration": "mfaConfiguration",
        "password_policy": "passwordPolicy",
        "schema": "schema",
        "sms_authentication_message": "smsAuthenticationMessage",
        "sms_configuration": "smsConfiguration",
        "sms_verification_message": "smsVerificationMessage",
        "software_token_mfa_configuration": "softwareTokenMfaConfiguration",
        "tags": "tags",
        "tags_all": "tagsAll",
        "username_attributes": "usernameAttributes",
        "username_configuration": "usernameConfiguration",
        "user_pool_add_ons": "userPoolAddOns",
        "verification_message_template": "verificationMessageTemplate",
    },
)
class CognitoUserPoolConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        account_recovery_setting: typing.Optional[CognitoUserPoolAccountRecoverySetting] = None,
        admin_create_user_config: typing.Optional[CognitoUserPoolAdminCreateUserConfig] = None,
        alias_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_verified_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        device_configuration: typing.Optional["CognitoUserPoolDeviceConfiguration"] = None,
        email_configuration: typing.Optional["CognitoUserPoolEmailConfiguration"] = None,
        email_verification_message: typing.Optional[builtins.str] = None,
        email_verification_subject: typing.Optional[builtins.str] = None,
        lambda_config: typing.Optional["CognitoUserPoolLambdaConfig"] = None,
        mfa_configuration: typing.Optional[builtins.str] = None,
        password_policy: typing.Optional["CognitoUserPoolPasswordPolicy"] = None,
        schema: typing.Optional[typing.Sequence["CognitoUserPoolSchema"]] = None,
        sms_authentication_message: typing.Optional[builtins.str] = None,
        sms_configuration: typing.Optional["CognitoUserPoolSmsConfiguration"] = None,
        sms_verification_message: typing.Optional[builtins.str] = None,
        software_token_mfa_configuration: typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        username_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        username_configuration: typing.Optional["CognitoUserPoolUsernameConfiguration"] = None,
        user_pool_add_ons: typing.Optional["CognitoUserPoolUserPoolAddOns"] = None,
        verification_message_template: typing.Optional["CognitoUserPoolVerificationMessageTemplate"] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param account_recovery_setting: account_recovery_setting block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#account_recovery_setting CognitoUserPool#account_recovery_setting}
        :param admin_create_user_config: admin_create_user_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#admin_create_user_config CognitoUserPool#admin_create_user_config}
        :param alias_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#alias_attributes CognitoUserPool#alias_attributes}.
        :param auto_verified_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#auto_verified_attributes CognitoUserPool#auto_verified_attributes}.
        :param device_configuration: device_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_configuration CognitoUserPool#device_configuration}
        :param email_configuration: email_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_configuration CognitoUserPool#email_configuration}
        :param email_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_message CognitoUserPool#email_verification_message}.
        :param email_verification_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_subject CognitoUserPool#email_verification_subject}.
        :param lambda_config: lambda_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_config CognitoUserPool#lambda_config}
        :param mfa_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mfa_configuration CognitoUserPool#mfa_configuration}.
        :param password_policy: password_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#password_policy CognitoUserPool#password_policy}
        :param schema: schema block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#schema CognitoUserPool#schema}
        :param sms_authentication_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_authentication_message CognitoUserPool#sms_authentication_message}.
        :param sms_configuration: sms_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_configuration CognitoUserPool#sms_configuration}
        :param sms_verification_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_verification_message CognitoUserPool#sms_verification_message}.
        :param software_token_mfa_configuration: software_token_mfa_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#software_token_mfa_configuration CognitoUserPool#software_token_mfa_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags CognitoUserPool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags_all CognitoUserPool#tags_all}.
        :param username_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_attributes CognitoUserPool#username_attributes}.
        :param username_configuration: username_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_configuration CognitoUserPool#username_configuration}
        :param user_pool_add_ons: user_pool_add_ons block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_pool_add_ons CognitoUserPool#user_pool_add_ons}
        :param verification_message_template: verification_message_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verification_message_template CognitoUserPool#verification_message_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(account_recovery_setting, dict):
            account_recovery_setting = CognitoUserPoolAccountRecoverySetting(**account_recovery_setting)
        if isinstance(admin_create_user_config, dict):
            admin_create_user_config = CognitoUserPoolAdminCreateUserConfig(**admin_create_user_config)
        if isinstance(device_configuration, dict):
            device_configuration = CognitoUserPoolDeviceConfiguration(**device_configuration)
        if isinstance(email_configuration, dict):
            email_configuration = CognitoUserPoolEmailConfiguration(**email_configuration)
        if isinstance(lambda_config, dict):
            lambda_config = CognitoUserPoolLambdaConfig(**lambda_config)
        if isinstance(password_policy, dict):
            password_policy = CognitoUserPoolPasswordPolicy(**password_policy)
        if isinstance(sms_configuration, dict):
            sms_configuration = CognitoUserPoolSmsConfiguration(**sms_configuration)
        if isinstance(software_token_mfa_configuration, dict):
            software_token_mfa_configuration = CognitoUserPoolSoftwareTokenMfaConfiguration(**software_token_mfa_configuration)
        if isinstance(username_configuration, dict):
            username_configuration = CognitoUserPoolUsernameConfiguration(**username_configuration)
        if isinstance(user_pool_add_ons, dict):
            user_pool_add_ons = CognitoUserPoolUserPoolAddOns(**user_pool_add_ons)
        if isinstance(verification_message_template, dict):
            verification_message_template = CognitoUserPoolVerificationMessageTemplate(**verification_message_template)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_recovery_setting is not None:
            self._values["account_recovery_setting"] = account_recovery_setting
        if admin_create_user_config is not None:
            self._values["admin_create_user_config"] = admin_create_user_config
        if alias_attributes is not None:
            self._values["alias_attributes"] = alias_attributes
        if auto_verified_attributes is not None:
            self._values["auto_verified_attributes"] = auto_verified_attributes
        if device_configuration is not None:
            self._values["device_configuration"] = device_configuration
        if email_configuration is not None:
            self._values["email_configuration"] = email_configuration
        if email_verification_message is not None:
            self._values["email_verification_message"] = email_verification_message
        if email_verification_subject is not None:
            self._values["email_verification_subject"] = email_verification_subject
        if lambda_config is not None:
            self._values["lambda_config"] = lambda_config
        if mfa_configuration is not None:
            self._values["mfa_configuration"] = mfa_configuration
        if password_policy is not None:
            self._values["password_policy"] = password_policy
        if schema is not None:
            self._values["schema"] = schema
        if sms_authentication_message is not None:
            self._values["sms_authentication_message"] = sms_authentication_message
        if sms_configuration is not None:
            self._values["sms_configuration"] = sms_configuration
        if sms_verification_message is not None:
            self._values["sms_verification_message"] = sms_verification_message
        if software_token_mfa_configuration is not None:
            self._values["software_token_mfa_configuration"] = software_token_mfa_configuration
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if username_attributes is not None:
            self._values["username_attributes"] = username_attributes
        if username_configuration is not None:
            self._values["username_configuration"] = username_configuration
        if user_pool_add_ons is not None:
            self._values["user_pool_add_ons"] = user_pool_add_ons
        if verification_message_template is not None:
            self._values["verification_message_template"] = verification_message_template

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_recovery_setting(
        self,
    ) -> typing.Optional[CognitoUserPoolAccountRecoverySetting]:
        '''account_recovery_setting block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#account_recovery_setting CognitoUserPool#account_recovery_setting}
        '''
        result = self._values.get("account_recovery_setting")
        return typing.cast(typing.Optional[CognitoUserPoolAccountRecoverySetting], result)

    @builtins.property
    def admin_create_user_config(
        self,
    ) -> typing.Optional[CognitoUserPoolAdminCreateUserConfig]:
        '''admin_create_user_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#admin_create_user_config CognitoUserPool#admin_create_user_config}
        '''
        result = self._values.get("admin_create_user_config")
        return typing.cast(typing.Optional[CognitoUserPoolAdminCreateUserConfig], result)

    @builtins.property
    def alias_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#alias_attributes CognitoUserPool#alias_attributes}.'''
        result = self._values.get("alias_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auto_verified_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#auto_verified_attributes CognitoUserPool#auto_verified_attributes}.'''
        result = self._values.get("auto_verified_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def device_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolDeviceConfiguration"]:
        '''device_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_configuration CognitoUserPool#device_configuration}
        '''
        result = self._values.get("device_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolDeviceConfiguration"], result)

    @builtins.property
    def email_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolEmailConfiguration"]:
        '''email_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_configuration CognitoUserPool#email_configuration}
        '''
        result = self._values.get("email_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolEmailConfiguration"], result)

    @builtins.property
    def email_verification_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_message CognitoUserPool#email_verification_message}.'''
        result = self._values.get("email_verification_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_verification_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_verification_subject CognitoUserPool#email_verification_subject}.'''
        result = self._values.get("email_verification_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_config(self) -> typing.Optional["CognitoUserPoolLambdaConfig"]:
        '''lambda_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_config CognitoUserPool#lambda_config}
        '''
        result = self._values.get("lambda_config")
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfig"], result)

    @builtins.property
    def mfa_configuration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mfa_configuration CognitoUserPool#mfa_configuration}.'''
        result = self._values.get("mfa_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_policy(self) -> typing.Optional["CognitoUserPoolPasswordPolicy"]:
        '''password_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#password_policy CognitoUserPool#password_policy}
        '''
        result = self._values.get("password_policy")
        return typing.cast(typing.Optional["CognitoUserPoolPasswordPolicy"], result)

    @builtins.property
    def schema(self) -> typing.Optional[typing.List["CognitoUserPoolSchema"]]:
        '''schema block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#schema CognitoUserPool#schema}
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[typing.List["CognitoUserPoolSchema"]], result)

    @builtins.property
    def sms_authentication_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_authentication_message CognitoUserPool#sms_authentication_message}.'''
        result = self._values.get("sms_authentication_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_configuration(self) -> typing.Optional["CognitoUserPoolSmsConfiguration"]:
        '''sms_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_configuration CognitoUserPool#sms_configuration}
        '''
        result = self._values.get("sms_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolSmsConfiguration"], result)

    @builtins.property
    def sms_verification_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_verification_message CognitoUserPool#sms_verification_message}.'''
        result = self._values.get("sms_verification_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def software_token_mfa_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"]:
        '''software_token_mfa_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#software_token_mfa_configuration CognitoUserPool#software_token_mfa_configuration}
        '''
        result = self._values.get("software_token_mfa_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolSoftwareTokenMfaConfiguration"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags CognitoUserPool#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#tags_all CognitoUserPool#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def username_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_attributes CognitoUserPool#username_attributes}.'''
        result = self._values.get("username_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def username_configuration(
        self,
    ) -> typing.Optional["CognitoUserPoolUsernameConfiguration"]:
        '''username_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#username_configuration CognitoUserPool#username_configuration}
        '''
        result = self._values.get("username_configuration")
        return typing.cast(typing.Optional["CognitoUserPoolUsernameConfiguration"], result)

    @builtins.property
    def user_pool_add_ons(self) -> typing.Optional["CognitoUserPoolUserPoolAddOns"]:
        '''user_pool_add_ons block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_pool_add_ons CognitoUserPool#user_pool_add_ons}
        '''
        result = self._values.get("user_pool_add_ons")
        return typing.cast(typing.Optional["CognitoUserPoolUserPoolAddOns"], result)

    @builtins.property
    def verification_message_template(
        self,
    ) -> typing.Optional["CognitoUserPoolVerificationMessageTemplate"]:
        '''verification_message_template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verification_message_template CognitoUserPool#verification_message_template}
        '''
        result = self._values.get("verification_message_template")
        return typing.cast(typing.Optional["CognitoUserPoolVerificationMessageTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDeviceConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "challenge_required_on_new_device": "challengeRequiredOnNewDevice",
        "device_only_remembered_on_user_prompt": "deviceOnlyRememberedOnUserPrompt",
    },
)
class CognitoUserPoolDeviceConfiguration:
    def __init__(
        self,
        *,
        challenge_required_on_new_device: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        device_only_remembered_on_user_prompt: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param challenge_required_on_new_device: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#challenge_required_on_new_device CognitoUserPool#challenge_required_on_new_device}.
        :param device_only_remembered_on_user_prompt: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_only_remembered_on_user_prompt CognitoUserPool#device_only_remembered_on_user_prompt}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if challenge_required_on_new_device is not None:
            self._values["challenge_required_on_new_device"] = challenge_required_on_new_device
        if device_only_remembered_on_user_prompt is not None:
            self._values["device_only_remembered_on_user_prompt"] = device_only_remembered_on_user_prompt

    @builtins.property
    def challenge_required_on_new_device(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#challenge_required_on_new_device CognitoUserPool#challenge_required_on_new_device}.'''
        result = self._values.get("challenge_required_on_new_device")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def device_only_remembered_on_user_prompt(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#device_only_remembered_on_user_prompt CognitoUserPool#device_only_remembered_on_user_prompt}.'''
        result = self._values.get("device_only_remembered_on_user_prompt")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolDeviceConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolDeviceConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDeviceConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetChallengeRequiredOnNewDevice")
    def reset_challenge_required_on_new_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChallengeRequiredOnNewDevice", []))

    @jsii.member(jsii_name="resetDeviceOnlyRememberedOnUserPrompt")
    def reset_device_only_remembered_on_user_prompt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceOnlyRememberedOnUserPrompt", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="challengeRequiredOnNewDeviceInput")
    def challenge_required_on_new_device_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "challengeRequiredOnNewDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceOnlyRememberedOnUserPromptInput")
    def device_only_remembered_on_user_prompt_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deviceOnlyRememberedOnUserPromptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="challengeRequiredOnNewDevice")
    def challenge_required_on_new_device(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "challengeRequiredOnNewDevice"))

    @challenge_required_on_new_device.setter
    def challenge_required_on_new_device(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "challengeRequiredOnNewDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceOnlyRememberedOnUserPrompt")
    def device_only_remembered_on_user_prompt(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deviceOnlyRememberedOnUserPrompt"))

    @device_only_remembered_on_user_prompt.setter
    def device_only_remembered_on_user_prompt(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deviceOnlyRememberedOnUserPrompt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolDeviceConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolDeviceConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolDeviceConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CognitoUserPoolDomain(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDomain",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain aws_cognito_user_pool_domain}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        user_pool_id: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain aws_cognito_user_pool_domain} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#domain CognitoUserPoolDomain#domain}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#user_pool_id CognitoUserPoolDomain#user_pool_id}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#certificate_arn CognitoUserPoolDomain#certificate_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoUserPoolDomainConfig(
            domain=domain,
            user_pool_id=user_pool_id,
            certificate_arn=certificate_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCertificateArn")
    def reset_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateArn", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontDistributionArn")
    def cloudfront_distribution_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontDistributionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArnInput")
    def certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateArn"))

    @certificate_arn.setter
    def certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "certificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolDomainConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "user_pool_id": "userPoolId",
        "certificate_arn": "certificateArn",
    },
)
class CognitoUserPoolDomainConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        user_pool_id: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#domain CognitoUserPoolDomain#domain}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#user_pool_id CognitoUserPoolDomain#user_pool_id}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#certificate_arn CognitoUserPoolDomain#certificate_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "user_pool_id": user_pool_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn

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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#domain CognitoUserPoolDomain#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#user_pool_id CognitoUserPoolDomain#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_domain#certificate_arn CognitoUserPoolDomain#certificate_arn}.'''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolDomainConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolEmailConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_set": "configurationSet",
        "email_sending_account": "emailSendingAccount",
        "from_email_address": "fromEmailAddress",
        "reply_to_email_address": "replyToEmailAddress",
        "source_arn": "sourceArn",
    },
)
class CognitoUserPoolEmailConfiguration:
    def __init__(
        self,
        *,
        configuration_set: typing.Optional[builtins.str] = None,
        email_sending_account: typing.Optional[builtins.str] = None,
        from_email_address: typing.Optional[builtins.str] = None,
        reply_to_email_address: typing.Optional[builtins.str] = None,
        source_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param configuration_set: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#configuration_set CognitoUserPool#configuration_set}.
        :param email_sending_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_sending_account CognitoUserPool#email_sending_account}.
        :param from_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#from_email_address CognitoUserPool#from_email_address}.
        :param reply_to_email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#reply_to_email_address CognitoUserPool#reply_to_email_address}.
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#source_arn CognitoUserPool#source_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if configuration_set is not None:
            self._values["configuration_set"] = configuration_set
        if email_sending_account is not None:
            self._values["email_sending_account"] = email_sending_account
        if from_email_address is not None:
            self._values["from_email_address"] = from_email_address
        if reply_to_email_address is not None:
            self._values["reply_to_email_address"] = reply_to_email_address
        if source_arn is not None:
            self._values["source_arn"] = source_arn

    @builtins.property
    def configuration_set(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#configuration_set CognitoUserPool#configuration_set}.'''
        result = self._values.get("configuration_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_sending_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_sending_account CognitoUserPool#email_sending_account}.'''
        result = self._values.get("email_sending_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_email_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#from_email_address CognitoUserPool#from_email_address}.'''
        result = self._values.get("from_email_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reply_to_email_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#reply_to_email_address CognitoUserPool#reply_to_email_address}.'''
        result = self._values.get("reply_to_email_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#source_arn CognitoUserPool#source_arn}.'''
        result = self._values.get("source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolEmailConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolEmailConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolEmailConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetConfigurationSet")
    def reset_configuration_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationSet", []))

    @jsii.member(jsii_name="resetEmailSendingAccount")
    def reset_email_sending_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSendingAccount", []))

    @jsii.member(jsii_name="resetFromEmailAddress")
    def reset_from_email_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFromEmailAddress", []))

    @jsii.member(jsii_name="resetReplyToEmailAddress")
    def reset_reply_to_email_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplyToEmailAddress", []))

    @jsii.member(jsii_name="resetSourceArn")
    def reset_source_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSetInput")
    def configuration_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSendingAccountInput")
    def email_sending_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSendingAccountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromEmailAddressInput")
    def from_email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fromEmailAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replyToEmailAddressInput")
    def reply_to_email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replyToEmailAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArnInput")
    def source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSet")
    def configuration_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationSet"))

    @configuration_set.setter
    def configuration_set(self, value: builtins.str) -> None:
        jsii.set(self, "configurationSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSendingAccount")
    def email_sending_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSendingAccount"))

    @email_sending_account.setter
    def email_sending_account(self, value: builtins.str) -> None:
        jsii.set(self, "emailSendingAccount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromEmailAddress")
    def from_email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fromEmailAddress"))

    @from_email_address.setter
    def from_email_address(self, value: builtins.str) -> None:
        jsii.set(self, "fromEmailAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replyToEmailAddress")
    def reply_to_email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replyToEmailAddress"))

    @reply_to_email_address.setter
    def reply_to_email_address(self, value: builtins.str) -> None:
        jsii.set(self, "replyToEmailAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArn")
    def source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceArn"))

    @source_arn.setter
    def source_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolEmailConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolEmailConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolEmailConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfig",
    jsii_struct_bases=[],
    name_mapping={
        "create_auth_challenge": "createAuthChallenge",
        "custom_email_sender": "customEmailSender",
        "custom_message": "customMessage",
        "custom_sms_sender": "customSmsSender",
        "define_auth_challenge": "defineAuthChallenge",
        "kms_key_id": "kmsKeyId",
        "post_authentication": "postAuthentication",
        "post_confirmation": "postConfirmation",
        "pre_authentication": "preAuthentication",
        "pre_sign_up": "preSignUp",
        "pre_token_generation": "preTokenGeneration",
        "user_migration": "userMigration",
        "verify_auth_challenge_response": "verifyAuthChallengeResponse",
    },
)
class CognitoUserPoolLambdaConfig:
    def __init__(
        self,
        *,
        create_auth_challenge: typing.Optional[builtins.str] = None,
        custom_email_sender: typing.Optional["CognitoUserPoolLambdaConfigCustomEmailSender"] = None,
        custom_message: typing.Optional[builtins.str] = None,
        custom_sms_sender: typing.Optional["CognitoUserPoolLambdaConfigCustomSmsSender"] = None,
        define_auth_challenge: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        post_authentication: typing.Optional[builtins.str] = None,
        post_confirmation: typing.Optional[builtins.str] = None,
        pre_authentication: typing.Optional[builtins.str] = None,
        pre_sign_up: typing.Optional[builtins.str] = None,
        pre_token_generation: typing.Optional[builtins.str] = None,
        user_migration: typing.Optional[builtins.str] = None,
        verify_auth_challenge_response: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#create_auth_challenge CognitoUserPool#create_auth_challenge}.
        :param custom_email_sender: custom_email_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_email_sender CognitoUserPool#custom_email_sender}
        :param custom_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_message CognitoUserPool#custom_message}.
        :param custom_sms_sender: custom_sms_sender block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_sms_sender CognitoUserPool#custom_sms_sender}
        :param define_auth_challenge: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#define_auth_challenge CognitoUserPool#define_auth_challenge}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#kms_key_id CognitoUserPool#kms_key_id}.
        :param post_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_authentication CognitoUserPool#post_authentication}.
        :param post_confirmation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_confirmation CognitoUserPool#post_confirmation}.
        :param pre_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_authentication CognitoUserPool#pre_authentication}.
        :param pre_sign_up: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_sign_up CognitoUserPool#pre_sign_up}.
        :param pre_token_generation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_token_generation CognitoUserPool#pre_token_generation}.
        :param user_migration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_migration CognitoUserPool#user_migration}.
        :param verify_auth_challenge_response: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verify_auth_challenge_response CognitoUserPool#verify_auth_challenge_response}.
        '''
        if isinstance(custom_email_sender, dict):
            custom_email_sender = CognitoUserPoolLambdaConfigCustomEmailSender(**custom_email_sender)
        if isinstance(custom_sms_sender, dict):
            custom_sms_sender = CognitoUserPoolLambdaConfigCustomSmsSender(**custom_sms_sender)
        self._values: typing.Dict[str, typing.Any] = {}
        if create_auth_challenge is not None:
            self._values["create_auth_challenge"] = create_auth_challenge
        if custom_email_sender is not None:
            self._values["custom_email_sender"] = custom_email_sender
        if custom_message is not None:
            self._values["custom_message"] = custom_message
        if custom_sms_sender is not None:
            self._values["custom_sms_sender"] = custom_sms_sender
        if define_auth_challenge is not None:
            self._values["define_auth_challenge"] = define_auth_challenge
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if post_authentication is not None:
            self._values["post_authentication"] = post_authentication
        if post_confirmation is not None:
            self._values["post_confirmation"] = post_confirmation
        if pre_authentication is not None:
            self._values["pre_authentication"] = pre_authentication
        if pre_sign_up is not None:
            self._values["pre_sign_up"] = pre_sign_up
        if pre_token_generation is not None:
            self._values["pre_token_generation"] = pre_token_generation
        if user_migration is not None:
            self._values["user_migration"] = user_migration
        if verify_auth_challenge_response is not None:
            self._values["verify_auth_challenge_response"] = verify_auth_challenge_response

    @builtins.property
    def create_auth_challenge(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#create_auth_challenge CognitoUserPool#create_auth_challenge}.'''
        result = self._values.get("create_auth_challenge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_email_sender(
        self,
    ) -> typing.Optional["CognitoUserPoolLambdaConfigCustomEmailSender"]:
        '''custom_email_sender block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_email_sender CognitoUserPool#custom_email_sender}
        '''
        result = self._values.get("custom_email_sender")
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfigCustomEmailSender"], result)

    @builtins.property
    def custom_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_message CognitoUserPool#custom_message}.'''
        result = self._values.get("custom_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_sms_sender(
        self,
    ) -> typing.Optional["CognitoUserPoolLambdaConfigCustomSmsSender"]:
        '''custom_sms_sender block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#custom_sms_sender CognitoUserPool#custom_sms_sender}
        '''
        result = self._values.get("custom_sms_sender")
        return typing.cast(typing.Optional["CognitoUserPoolLambdaConfigCustomSmsSender"], result)

    @builtins.property
    def define_auth_challenge(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#define_auth_challenge CognitoUserPool#define_auth_challenge}.'''
        result = self._values.get("define_auth_challenge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#kms_key_id CognitoUserPool#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_authentication(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_authentication CognitoUserPool#post_authentication}.'''
        result = self._values.get("post_authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_confirmation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#post_confirmation CognitoUserPool#post_confirmation}.'''
        result = self._values.get("post_confirmation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_authentication(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_authentication CognitoUserPool#pre_authentication}.'''
        result = self._values.get("pre_authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_sign_up(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_sign_up CognitoUserPool#pre_sign_up}.'''
        result = self._values.get("pre_sign_up")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_token_generation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#pre_token_generation CognitoUserPool#pre_token_generation}.'''
        result = self._values.get("pre_token_generation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_migration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#user_migration CognitoUserPool#user_migration}.'''
        result = self._values.get("user_migration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_auth_challenge_response(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#verify_auth_challenge_response CognitoUserPool#verify_auth_challenge_response}.'''
        result = self._values.get("verify_auth_challenge_response")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolLambdaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomEmailSender",
    jsii_struct_bases=[],
    name_mapping={"lambda_arn": "lambdaArn", "lambda_version": "lambdaVersion"},
)
class CognitoUserPoolLambdaConfigCustomEmailSender:
    def __init__(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_arn": lambda_arn,
            "lambda_version": lambda_version,
        }

    @builtins.property
    def lambda_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.'''
        result = self._values.get("lambda_arn")
        assert result is not None, "Required property 'lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.'''
        result = self._values.get("lambda_version")
        assert result is not None, "Required property 'lambda_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolLambdaConfigCustomEmailSender(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArnInput")
    def lambda_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersionInput")
    def lambda_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArn")
    def lambda_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaArn"))

    @lambda_arn.setter
    def lambda_arn(self, value: builtins.str) -> None:
        jsii.set(self, "lambdaArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersion")
    def lambda_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaVersion"))

    @lambda_version.setter
    def lambda_version(self, value: builtins.str) -> None:
        jsii.set(self, "lambdaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomSmsSender",
    jsii_struct_bases=[],
    name_mapping={"lambda_arn": "lambdaArn", "lambda_version": "lambdaVersion"},
)
class CognitoUserPoolLambdaConfigCustomSmsSender:
    def __init__(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_arn": lambda_arn,
            "lambda_version": lambda_version,
        }

    @builtins.property
    def lambda_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.'''
        result = self._values.get("lambda_arn")
        assert result is not None, "Required property 'lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.'''
        result = self._values.get("lambda_version")
        assert result is not None, "Required property 'lambda_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolLambdaConfigCustomSmsSender(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArnInput")
    def lambda_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersionInput")
    def lambda_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lambdaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArn")
    def lambda_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaArn"))

    @lambda_arn.setter
    def lambda_arn(self, value: builtins.str) -> None:
        jsii.set(self, "lambdaArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaVersion")
    def lambda_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lambdaVersion"))

    @lambda_version.setter
    def lambda_version(self, value: builtins.str) -> None:
        jsii.set(self, "lambdaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CognitoUserPoolLambdaConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolLambdaConfigOutputReference",
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

    @jsii.member(jsii_name="putCustomEmailSender")
    def put_custom_email_sender(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        value = CognitoUserPoolLambdaConfigCustomEmailSender(
            lambda_arn=lambda_arn, lambda_version=lambda_version
        )

        return typing.cast(None, jsii.invoke(self, "putCustomEmailSender", [value]))

    @jsii.member(jsii_name="putCustomSmsSender")
    def put_custom_sms_sender(
        self,
        *,
        lambda_arn: builtins.str,
        lambda_version: builtins.str,
    ) -> None:
        '''
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_arn CognitoUserPool#lambda_arn}.
        :param lambda_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#lambda_version CognitoUserPool#lambda_version}.
        '''
        value = CognitoUserPoolLambdaConfigCustomSmsSender(
            lambda_arn=lambda_arn, lambda_version=lambda_version
        )

        return typing.cast(None, jsii.invoke(self, "putCustomSmsSender", [value]))

    @jsii.member(jsii_name="resetCreateAuthChallenge")
    def reset_create_auth_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateAuthChallenge", []))

    @jsii.member(jsii_name="resetCustomEmailSender")
    def reset_custom_email_sender(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomEmailSender", []))

    @jsii.member(jsii_name="resetCustomMessage")
    def reset_custom_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomMessage", []))

    @jsii.member(jsii_name="resetCustomSmsSender")
    def reset_custom_sms_sender(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSmsSender", []))

    @jsii.member(jsii_name="resetDefineAuthChallenge")
    def reset_define_auth_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefineAuthChallenge", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetPostAuthentication")
    def reset_post_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostAuthentication", []))

    @jsii.member(jsii_name="resetPostConfirmation")
    def reset_post_confirmation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostConfirmation", []))

    @jsii.member(jsii_name="resetPreAuthentication")
    def reset_pre_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreAuthentication", []))

    @jsii.member(jsii_name="resetPreSignUp")
    def reset_pre_sign_up(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreSignUp", []))

    @jsii.member(jsii_name="resetPreTokenGeneration")
    def reset_pre_token_generation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreTokenGeneration", []))

    @jsii.member(jsii_name="resetUserMigration")
    def reset_user_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserMigration", []))

    @jsii.member(jsii_name="resetVerifyAuthChallengeResponse")
    def reset_verify_auth_challenge_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyAuthChallengeResponse", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customEmailSender")
    def custom_email_sender(
        self,
    ) -> CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference:
        return typing.cast(CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference, jsii.get(self, "customEmailSender"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSmsSender")
    def custom_sms_sender(
        self,
    ) -> CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference:
        return typing.cast(CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference, jsii.get(self, "customSmsSender"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createAuthChallengeInput")
    def create_auth_challenge_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createAuthChallengeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customEmailSenderInput")
    def custom_email_sender_input(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomEmailSender], jsii.get(self, "customEmailSenderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customMessageInput")
    def custom_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSmsSenderInput")
    def custom_sms_sender_input(
        self,
    ) -> typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfigCustomSmsSender], jsii.get(self, "customSmsSenderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defineAuthChallengeInput")
    def define_auth_challenge_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defineAuthChallengeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postAuthenticationInput")
    def post_authentication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postConfirmationInput")
    def post_confirmation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postConfirmationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preAuthenticationInput")
    def pre_authentication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preSignUpInput")
    def pre_sign_up_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preSignUpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preTokenGenerationInput")
    def pre_token_generation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preTokenGenerationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userMigrationInput")
    def user_migration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userMigrationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyAuthChallengeResponseInput")
    def verify_auth_challenge_response_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "verifyAuthChallengeResponseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createAuthChallenge")
    def create_auth_challenge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createAuthChallenge"))

    @create_auth_challenge.setter
    def create_auth_challenge(self, value: builtins.str) -> None:
        jsii.set(self, "createAuthChallenge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customMessage")
    def custom_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customMessage"))

    @custom_message.setter
    def custom_message(self, value: builtins.str) -> None:
        jsii.set(self, "customMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defineAuthChallenge")
    def define_auth_challenge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defineAuthChallenge"))

    @define_auth_challenge.setter
    def define_auth_challenge(self, value: builtins.str) -> None:
        jsii.set(self, "defineAuthChallenge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postAuthentication")
    def post_authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postAuthentication"))

    @post_authentication.setter
    def post_authentication(self, value: builtins.str) -> None:
        jsii.set(self, "postAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postConfirmation")
    def post_confirmation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postConfirmation"))

    @post_confirmation.setter
    def post_confirmation(self, value: builtins.str) -> None:
        jsii.set(self, "postConfirmation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preAuthentication")
    def pre_authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preAuthentication"))

    @pre_authentication.setter
    def pre_authentication(self, value: builtins.str) -> None:
        jsii.set(self, "preAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preSignUp")
    def pre_sign_up(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preSignUp"))

    @pre_sign_up.setter
    def pre_sign_up(self, value: builtins.str) -> None:
        jsii.set(self, "preSignUp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preTokenGeneration")
    def pre_token_generation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preTokenGeneration"))

    @pre_token_generation.setter
    def pre_token_generation(self, value: builtins.str) -> None:
        jsii.set(self, "preTokenGeneration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userMigration")
    def user_migration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userMigration"))

    @user_migration.setter
    def user_migration(self, value: builtins.str) -> None:
        jsii.set(self, "userMigration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyAuthChallengeResponse")
    def verify_auth_challenge_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "verifyAuthChallengeResponse"))

    @verify_auth_challenge_response.setter
    def verify_auth_challenge_response(self, value: builtins.str) -> None:
        jsii.set(self, "verifyAuthChallengeResponse", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolLambdaConfig]:
        return typing.cast(typing.Optional[CognitoUserPoolLambdaConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolLambdaConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolPasswordPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "minimum_length": "minimumLength",
        "require_lowercase": "requireLowercase",
        "require_numbers": "requireNumbers",
        "require_symbols": "requireSymbols",
        "require_uppercase": "requireUppercase",
        "temporary_password_validity_days": "temporaryPasswordValidityDays",
    },
)
class CognitoUserPoolPasswordPolicy:
    def __init__(
        self,
        *,
        minimum_length: typing.Optional[jsii.Number] = None,
        require_lowercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_numbers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_symbols: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_uppercase: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        temporary_password_validity_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param minimum_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#minimum_length CognitoUserPool#minimum_length}.
        :param require_lowercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_lowercase CognitoUserPool#require_lowercase}.
        :param require_numbers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_numbers CognitoUserPool#require_numbers}.
        :param require_symbols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_symbols CognitoUserPool#require_symbols}.
        :param require_uppercase: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_uppercase CognitoUserPool#require_uppercase}.
        :param temporary_password_validity_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#temporary_password_validity_days CognitoUserPool#temporary_password_validity_days}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if minimum_length is not None:
            self._values["minimum_length"] = minimum_length
        if require_lowercase is not None:
            self._values["require_lowercase"] = require_lowercase
        if require_numbers is not None:
            self._values["require_numbers"] = require_numbers
        if require_symbols is not None:
            self._values["require_symbols"] = require_symbols
        if require_uppercase is not None:
            self._values["require_uppercase"] = require_uppercase
        if temporary_password_validity_days is not None:
            self._values["temporary_password_validity_days"] = temporary_password_validity_days

    @builtins.property
    def minimum_length(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#minimum_length CognitoUserPool#minimum_length}.'''
        result = self._values.get("minimum_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def require_lowercase(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_lowercase CognitoUserPool#require_lowercase}.'''
        result = self._values.get("require_lowercase")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_numbers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_numbers CognitoUserPool#require_numbers}.'''
        result = self._values.get("require_numbers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_symbols(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_symbols CognitoUserPool#require_symbols}.'''
        result = self._values.get("require_symbols")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_uppercase(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#require_uppercase CognitoUserPool#require_uppercase}.'''
        result = self._values.get("require_uppercase")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def temporary_password_validity_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#temporary_password_validity_days CognitoUserPool#temporary_password_validity_days}.'''
        result = self._values.get("temporary_password_validity_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolPasswordPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolPasswordPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolPasswordPolicyOutputReference",
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

    @jsii.member(jsii_name="resetMinimumLength")
    def reset_minimum_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumLength", []))

    @jsii.member(jsii_name="resetRequireLowercase")
    def reset_require_lowercase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireLowercase", []))

    @jsii.member(jsii_name="resetRequireNumbers")
    def reset_require_numbers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireNumbers", []))

    @jsii.member(jsii_name="resetRequireSymbols")
    def reset_require_symbols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSymbols", []))

    @jsii.member(jsii_name="resetRequireUppercase")
    def reset_require_uppercase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireUppercase", []))

    @jsii.member(jsii_name="resetTemporaryPasswordValidityDays")
    def reset_temporary_password_validity_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemporaryPasswordValidityDays", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumLengthInput")
    def minimum_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireLowercaseInput")
    def require_lowercase_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireLowercaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireNumbersInput")
    def require_numbers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireNumbersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSymbolsInput")
    def require_symbols_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireSymbolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireUppercaseInput")
    def require_uppercase_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireUppercaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="temporaryPasswordValidityDaysInput")
    def temporary_password_validity_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "temporaryPasswordValidityDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumLength")
    def minimum_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumLength"))

    @minimum_length.setter
    def minimum_length(self, value: jsii.Number) -> None:
        jsii.set(self, "minimumLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireLowercase")
    def require_lowercase(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireLowercase"))

    @require_lowercase.setter
    def require_lowercase(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireLowercase", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireNumbers")
    def require_numbers(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireNumbers"))

    @require_numbers.setter
    def require_numbers(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireNumbers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSymbols")
    def require_symbols(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireSymbols"))

    @require_symbols.setter
    def require_symbols(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireSymbols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireUppercase")
    def require_uppercase(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireUppercase"))

    @require_uppercase.setter
    def require_uppercase(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireUppercase", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="temporaryPasswordValidityDays")
    def temporary_password_validity_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "temporaryPasswordValidityDays"))

    @temporary_password_validity_days.setter
    def temporary_password_validity_days(self, value: jsii.Number) -> None:
        jsii.set(self, "temporaryPasswordValidityDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolPasswordPolicy]:
        return typing.cast(typing.Optional[CognitoUserPoolPasswordPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolPasswordPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchema",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_data_type": "attributeDataType",
        "name": "name",
        "developer_only_attribute": "developerOnlyAttribute",
        "mutable": "mutable",
        "number_attribute_constraints": "numberAttributeConstraints",
        "required": "required",
        "string_attribute_constraints": "stringAttributeConstraints",
    },
)
class CognitoUserPoolSchema:
    def __init__(
        self,
        *,
        attribute_data_type: builtins.str,
        name: builtins.str,
        developer_only_attribute: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        mutable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        number_attribute_constraints: typing.Optional["CognitoUserPoolSchemaNumberAttributeConstraints"] = None,
        required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        string_attribute_constraints: typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"] = None,
    ) -> None:
        '''
        :param attribute_data_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#attribute_data_type CognitoUserPool#attribute_data_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.
        :param developer_only_attribute: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#developer_only_attribute CognitoUserPool#developer_only_attribute}.
        :param mutable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mutable CognitoUserPool#mutable}.
        :param number_attribute_constraints: number_attribute_constraints block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#number_attribute_constraints CognitoUserPool#number_attribute_constraints}
        :param required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#required CognitoUserPool#required}.
        :param string_attribute_constraints: string_attribute_constraints block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#string_attribute_constraints CognitoUserPool#string_attribute_constraints}
        '''
        if isinstance(number_attribute_constraints, dict):
            number_attribute_constraints = CognitoUserPoolSchemaNumberAttributeConstraints(**number_attribute_constraints)
        if isinstance(string_attribute_constraints, dict):
            string_attribute_constraints = CognitoUserPoolSchemaStringAttributeConstraints(**string_attribute_constraints)
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_data_type": attribute_data_type,
            "name": name,
        }
        if developer_only_attribute is not None:
            self._values["developer_only_attribute"] = developer_only_attribute
        if mutable is not None:
            self._values["mutable"] = mutable
        if number_attribute_constraints is not None:
            self._values["number_attribute_constraints"] = number_attribute_constraints
        if required is not None:
            self._values["required"] = required
        if string_attribute_constraints is not None:
            self._values["string_attribute_constraints"] = string_attribute_constraints

    @builtins.property
    def attribute_data_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#attribute_data_type CognitoUserPool#attribute_data_type}.'''
        result = self._values.get("attribute_data_type")
        assert result is not None, "Required property 'attribute_data_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#name CognitoUserPool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def developer_only_attribute(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#developer_only_attribute CognitoUserPool#developer_only_attribute}.'''
        result = self._values.get("developer_only_attribute")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def mutable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#mutable CognitoUserPool#mutable}.'''
        result = self._values.get("mutable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def number_attribute_constraints(
        self,
    ) -> typing.Optional["CognitoUserPoolSchemaNumberAttributeConstraints"]:
        '''number_attribute_constraints block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#number_attribute_constraints CognitoUserPool#number_attribute_constraints}
        '''
        result = self._values.get("number_attribute_constraints")
        return typing.cast(typing.Optional["CognitoUserPoolSchemaNumberAttributeConstraints"], result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#required CognitoUserPool#required}.'''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def string_attribute_constraints(
        self,
    ) -> typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"]:
        '''string_attribute_constraints block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#string_attribute_constraints CognitoUserPool#string_attribute_constraints}
        '''
        result = self._values.get("string_attribute_constraints")
        return typing.cast(typing.Optional["CognitoUserPoolSchemaStringAttributeConstraints"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSchema(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaNumberAttributeConstraints",
    jsii_struct_bases=[],
    name_mapping={"max_value": "maxValue", "min_value": "minValue"},
)
class CognitoUserPoolSchemaNumberAttributeConstraints:
    def __init__(
        self,
        *,
        max_value: typing.Optional[builtins.str] = None,
        min_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_value CognitoUserPool#max_value}.
        :param min_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_value CognitoUserPool#min_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_value is not None:
            self._values["max_value"] = max_value
        if min_value is not None:
            self._values["min_value"] = min_value

    @builtins.property
    def max_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_value CognitoUserPool#max_value}.'''
        result = self._values.get("max_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_value CognitoUserPool#min_value}.'''
        result = self._values.get("min_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSchemaNumberAttributeConstraints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference",
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

    @jsii.member(jsii_name="resetMaxValue")
    def reset_max_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxValue", []))

    @jsii.member(jsii_name="resetMinValue")
    def reset_min_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxValueInput")
    def max_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minValueInput")
    def min_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxValue")
    def max_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxValue"))

    @max_value.setter
    def max_value(self, value: builtins.str) -> None:
        jsii.set(self, "maxValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minValue")
    def min_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minValue"))

    @min_value.setter
    def min_value(self, value: builtins.str) -> None:
        jsii.set(self, "minValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints]:
        return typing.cast(typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSchemaNumberAttributeConstraints],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaStringAttributeConstraints",
    jsii_struct_bases=[],
    name_mapping={"max_length": "maxLength", "min_length": "minLength"},
)
class CognitoUserPoolSchemaStringAttributeConstraints:
    def __init__(
        self,
        *,
        max_length: typing.Optional[builtins.str] = None,
        min_length: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_length CognitoUserPool#max_length}.
        :param min_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_length CognitoUserPool#min_length}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_length is not None:
            self._values["max_length"] = max_length
        if min_length is not None:
            self._values["min_length"] = min_length

    @builtins.property
    def max_length(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#max_length CognitoUserPool#max_length}.'''
        result = self._values.get("max_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_length(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#min_length CognitoUserPool#min_length}.'''
        result = self._values.get("min_length")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSchemaStringAttributeConstraints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSchemaStringAttributeConstraintsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSchemaStringAttributeConstraintsOutputReference",
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

    @jsii.member(jsii_name="resetMaxLength")
    def reset_max_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLength", []))

    @jsii.member(jsii_name="resetMinLength")
    def reset_min_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinLength", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLengthInput")
    def max_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLengthInput")
    def min_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLength")
    def max_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxLength"))

    @max_length.setter
    def max_length(self, value: builtins.str) -> None:
        jsii.set(self, "maxLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLength")
    def min_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minLength"))

    @min_length.setter
    def min_length(self, value: builtins.str) -> None:
        jsii.set(self, "minLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolSchemaStringAttributeConstraints]:
        return typing.cast(typing.Optional[CognitoUserPoolSchemaStringAttributeConstraints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSchemaStringAttributeConstraints],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSmsConfiguration",
    jsii_struct_bases=[],
    name_mapping={"external_id": "externalId", "sns_caller_arn": "snsCallerArn"},
)
class CognitoUserPoolSmsConfiguration:
    def __init__(
        self,
        *,
        external_id: builtins.str,
        sns_caller_arn: builtins.str,
    ) -> None:
        '''
        :param external_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#external_id CognitoUserPool#external_id}.
        :param sns_caller_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sns_caller_arn CognitoUserPool#sns_caller_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "external_id": external_id,
            "sns_caller_arn": sns_caller_arn,
        }

    @builtins.property
    def external_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#external_id CognitoUserPool#external_id}.'''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sns_caller_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sns_caller_arn CognitoUserPool#sns_caller_arn}.'''
        result = self._values.get("sns_caller_arn")
        assert result is not None, "Required property 'sns_caller_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSmsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSmsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSmsConfigurationOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsCallerArnInput")
    def sns_caller_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsCallerArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        jsii.set(self, "externalId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsCallerArn")
    def sns_caller_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsCallerArn"))

    @sns_caller_arn.setter
    def sns_caller_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsCallerArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolSmsConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolSmsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSmsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSoftwareTokenMfaConfiguration",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class CognitoUserPoolSoftwareTokenMfaConfiguration:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#enabled CognitoUserPool#enabled}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#enabled CognitoUserPool#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolSoftwareTokenMfaConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolSoftwareTokenMfaConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolSoftwareTokenMfaConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolSoftwareTokenMfaConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CognitoUserPoolUiCustomization(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUiCustomization",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization aws_cognito_user_pool_ui_customization}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user_pool_id: builtins.str,
        client_id: typing.Optional[builtins.str] = None,
        css: typing.Optional[builtins.str] = None,
        image_file: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization aws_cognito_user_pool_ui_customization} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#user_pool_id CognitoUserPoolUiCustomization#user_pool_id}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#client_id CognitoUserPoolUiCustomization#client_id}.
        :param css: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#css CognitoUserPoolUiCustomization#css}.
        :param image_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#image_file CognitoUserPoolUiCustomization#image_file}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CognitoUserPoolUiCustomizationConfig(
            user_pool_id=user_pool_id,
            client_id=client_id,
            css=css,
            image_file=image_file,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetCss")
    def reset_css(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCss", []))

    @jsii.member(jsii_name="resetImageFile")
    def reset_image_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageFile", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cssVersion")
    def css_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cssVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUrl")
    def image_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cssInput")
    def css_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cssInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageFileInput")
    def image_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="css")
    def css(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "css"))

    @css.setter
    def css(self, value: builtins.str) -> None:
        jsii.set(self, "css", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageFile")
    def image_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageFile"))

    @image_file.setter
    def image_file(self, value: builtins.str) -> None:
        jsii.set(self, "imageFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUiCustomizationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user_pool_id": "userPoolId",
        "client_id": "clientId",
        "css": "css",
        "image_file": "imageFile",
    },
)
class CognitoUserPoolUiCustomizationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user_pool_id: builtins.str,
        client_id: typing.Optional[builtins.str] = None,
        css: typing.Optional[builtins.str] = None,
        image_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#user_pool_id CognitoUserPoolUiCustomization#user_pool_id}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#client_id CognitoUserPoolUiCustomization#client_id}.
        :param css: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#css CognitoUserPoolUiCustomization#css}.
        :param image_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#image_file CognitoUserPoolUiCustomization#image_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if client_id is not None:
            self._values["client_id"] = client_id
        if css is not None:
            self._values["css"] = css
        if image_file is not None:
            self._values["image_file"] = image_file

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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#user_pool_id CognitoUserPoolUiCustomization#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#client_id CognitoUserPoolUiCustomization#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def css(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#css CognitoUserPoolUiCustomization#css}.'''
        result = self._values.get("css")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool_ui_customization#image_file CognitoUserPoolUiCustomization#image_file}.'''
        result = self._values.get("image_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolUiCustomizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUserPoolAddOns",
    jsii_struct_bases=[],
    name_mapping={"advanced_security_mode": "advancedSecurityMode"},
)
class CognitoUserPoolUserPoolAddOns:
    def __init__(self, *, advanced_security_mode: builtins.str) -> None:
        '''
        :param advanced_security_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#advanced_security_mode CognitoUserPool#advanced_security_mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "advanced_security_mode": advanced_security_mode,
        }

    @builtins.property
    def advanced_security_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#advanced_security_mode CognitoUserPool#advanced_security_mode}.'''
        result = self._values.get("advanced_security_mode")
        assert result is not None, "Required property 'advanced_security_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolUserPoolAddOns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolUserPoolAddOnsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUserPoolAddOnsOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedSecurityModeInput")
    def advanced_security_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "advancedSecurityModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="advancedSecurityMode")
    def advanced_security_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "advancedSecurityMode"))

    @advanced_security_mode.setter
    def advanced_security_mode(self, value: builtins.str) -> None:
        jsii.set(self, "advancedSecurityMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolUserPoolAddOns]:
        return typing.cast(typing.Optional[CognitoUserPoolUserPoolAddOns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolUserPoolAddOns],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUsernameConfiguration",
    jsii_struct_bases=[],
    name_mapping={"case_sensitive": "caseSensitive"},
)
class CognitoUserPoolUsernameConfiguration:
    def __init__(
        self,
        *,
        case_sensitive: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param case_sensitive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#case_sensitive CognitoUserPool#case_sensitive}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "case_sensitive": case_sensitive,
        }

    @builtins.property
    def case_sensitive(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#case_sensitive CognitoUserPool#case_sensitive}.'''
        result = self._values.get("case_sensitive")
        assert result is not None, "Required property 'case_sensitive' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolUsernameConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolUsernameConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolUsernameConfigurationOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caseSensitiveInput")
    def case_sensitive_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "caseSensitiveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caseSensitive")
    def case_sensitive(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "caseSensitive"))

    @case_sensitive.setter
    def case_sensitive(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "caseSensitive", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CognitoUserPoolUsernameConfiguration]:
        return typing.cast(typing.Optional[CognitoUserPoolUsernameConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolUsernameConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolVerificationMessageTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "default_email_option": "defaultEmailOption",
        "email_message": "emailMessage",
        "email_message_by_link": "emailMessageByLink",
        "email_subject": "emailSubject",
        "email_subject_by_link": "emailSubjectByLink",
        "sms_message": "smsMessage",
    },
)
class CognitoUserPoolVerificationMessageTemplate:
    def __init__(
        self,
        *,
        default_email_option: typing.Optional[builtins.str] = None,
        email_message: typing.Optional[builtins.str] = None,
        email_message_by_link: typing.Optional[builtins.str] = None,
        email_subject: typing.Optional[builtins.str] = None,
        email_subject_by_link: typing.Optional[builtins.str] = None,
        sms_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_email_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#default_email_option CognitoUserPool#default_email_option}.
        :param email_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.
        :param email_message_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message_by_link CognitoUserPool#email_message_by_link}.
        :param email_subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.
        :param email_subject_by_link: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject_by_link CognitoUserPool#email_subject_by_link}.
        :param sms_message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if default_email_option is not None:
            self._values["default_email_option"] = default_email_option
        if email_message is not None:
            self._values["email_message"] = email_message
        if email_message_by_link is not None:
            self._values["email_message_by_link"] = email_message_by_link
        if email_subject is not None:
            self._values["email_subject"] = email_subject
        if email_subject_by_link is not None:
            self._values["email_subject_by_link"] = email_subject_by_link
        if sms_message is not None:
            self._values["sms_message"] = sms_message

    @builtins.property
    def default_email_option(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#default_email_option CognitoUserPool#default_email_option}.'''
        result = self._values.get("default_email_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message CognitoUserPool#email_message}.'''
        result = self._values.get("email_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_message_by_link(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_message_by_link CognitoUserPool#email_message_by_link}.'''
        result = self._values.get("email_message_by_link")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject CognitoUserPool#email_subject}.'''
        result = self._values.get("email_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_subject_by_link(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#email_subject_by_link CognitoUserPool#email_subject_by_link}.'''
        result = self._values.get("email_subject_by_link")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cognito_user_pool#sms_message CognitoUserPool#sms_message}.'''
        result = self._values.get("sms_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoUserPoolVerificationMessageTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoUserPoolVerificationMessageTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.CognitoUserPoolVerificationMessageTemplateOutputReference",
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

    @jsii.member(jsii_name="resetDefaultEmailOption")
    def reset_default_email_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultEmailOption", []))

    @jsii.member(jsii_name="resetEmailMessage")
    def reset_email_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailMessage", []))

    @jsii.member(jsii_name="resetEmailMessageByLink")
    def reset_email_message_by_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailMessageByLink", []))

    @jsii.member(jsii_name="resetEmailSubject")
    def reset_email_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSubject", []))

    @jsii.member(jsii_name="resetEmailSubjectByLink")
    def reset_email_subject_by_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailSubjectByLink", []))

    @jsii.member(jsii_name="resetSmsMessage")
    def reset_sms_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsMessage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultEmailOptionInput")
    def default_email_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultEmailOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageByLinkInput")
    def email_message_by_link_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailMessageByLinkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageInput")
    def email_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectByLinkInput")
    def email_subject_by_link_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSubjectByLinkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectInput")
    def email_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailSubjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessageInput")
    def sms_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smsMessageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultEmailOption")
    def default_email_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultEmailOption"))

    @default_email_option.setter
    def default_email_option(self, value: builtins.str) -> None:
        jsii.set(self, "defaultEmailOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessage")
    def email_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailMessage"))

    @email_message.setter
    def email_message(self, value: builtins.str) -> None:
        jsii.set(self, "emailMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailMessageByLink")
    def email_message_by_link(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailMessageByLink"))

    @email_message_by_link.setter
    def email_message_by_link(self, value: builtins.str) -> None:
        jsii.set(self, "emailMessageByLink", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubject")
    def email_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSubject"))

    @email_subject.setter
    def email_subject(self, value: builtins.str) -> None:
        jsii.set(self, "emailSubject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailSubjectByLink")
    def email_subject_by_link(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailSubjectByLink"))

    @email_subject_by_link.setter
    def email_subject_by_link(self, value: builtins.str) -> None:
        jsii.set(self, "emailSubjectByLink", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smsMessage")
    def sms_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smsMessage"))

    @sms_message.setter
    def sms_message(self, value: builtins.str) -> None:
        jsii.set(self, "smsMessage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CognitoUserPoolVerificationMessageTemplate]:
        return typing.cast(typing.Optional[CognitoUserPoolVerificationMessageTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CognitoUserPoolVerificationMessageTemplate],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsCognitoUserPoolClient(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClient",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client aws_cognito_user_pool_client}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        client_id: builtins.str,
        user_pool_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client aws_cognito_user_pool_client} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#client_id DataAwsCognitoUserPoolClient#client_id}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#user_pool_id DataAwsCognitoUserPoolClient#user_pool_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCognitoUserPoolClientConfig(
            client_id=client_id,
            user_pool_id=user_pool_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="analyticsConfiguration")
    def analytics_configuration(
        self,
        index: builtins.str,
    ) -> "DataAwsCognitoUserPoolClientAnalyticsConfiguration":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCognitoUserPoolClientAnalyticsConfiguration", jsii.invoke(self, "analyticsConfiguration", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="tokenValidityUnits")
    def token_validity_units(
        self,
        index: builtins.str,
    ) -> "DataAwsCognitoUserPoolClientTokenValidityUnits":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCognitoUserPoolClientTokenValidityUnits", jsii.invoke(self, "tokenValidityUnits", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenValidity")
    def access_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessTokenValidity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlows")
    def allowed_oauth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthFlows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthFlowsUserPoolClient")
    def allowed_oauth_flows_user_pool_client(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "allowedOauthFlowsUserPoolClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedOauthScopes")
    def allowed_oauth_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOauthScopes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callbackUrls")
    def callback_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "callbackUrls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRedirectUri")
    def default_redirect_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRedirectUri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTokenRevocation")
    def enable_token_revocation(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableTokenRevocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="explicitAuthFlows")
    def explicit_auth_flows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "explicitAuthFlows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateSecret")
    def generate_secret(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "generateSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idTokenValidity")
    def id_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idTokenValidity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logoutUrls")
    def logout_urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "logoutUrls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preventUserExistenceErrors")
    def prevent_user_existence_errors(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preventUserExistenceErrors"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readAttributes")
    def read_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "readAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshTokenValidity")
    def refresh_token_validity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "refreshTokenValidity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedIdentityProviders")
    def supported_identity_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedIdentityProviders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeAttributes")
    def write_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "writeAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


class DataAwsCognitoUserPoolClientAnalyticsConfiguration(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientAnalyticsConfiguration",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataShared")
    def user_data_shared(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "userDataShared"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "client_id": "clientId",
        "user_pool_id": "userPoolId",
    },
)
class DataAwsCognitoUserPoolClientConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        client_id: builtins.str,
        user_pool_id: builtins.str,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#client_id DataAwsCognitoUserPoolClient#client_id}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#user_pool_id DataAwsCognitoUserPoolClient#user_pool_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "client_id": client_id,
            "user_pool_id": user_pool_id,
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
    def client_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#client_id DataAwsCognitoUserPoolClient#client_id}.'''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_client#user_pool_id DataAwsCognitoUserPoolClient#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCognitoUserPoolClientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPoolClientTokenValidityUnits(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientTokenValidityUnits",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idToken")
    def id_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshToken")
    def refresh_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refreshToken"))


class DataAwsCognitoUserPoolClients(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClients",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients aws_cognito_user_pool_clients}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user_pool_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients aws_cognito_user_pool_clients} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#user_pool_id DataAwsCognitoUserPoolClients#user_pool_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCognitoUserPoolClientsConfig(
            user_pool_id=user_pool_id,
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
    @jsii.member(jsii_name="clientIds")
    def client_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolClientsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user_pool_id": "userPoolId",
    },
)
class DataAwsCognitoUserPoolClientsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user_pool_id: builtins.str,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#user_pool_id DataAwsCognitoUserPoolClients#user_pool_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_clients#user_pool_id DataAwsCognitoUserPoolClients#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCognitoUserPoolClientsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPoolSigningCertificate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolSigningCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate aws_cognito_user_pool_signing_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user_pool_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate aws_cognito_user_pool_signing_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#user_pool_id DataAwsCognitoUserPoolSigningCertificate#user_pool_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCognitoUserPoolSigningCertificateConfig(
            user_pool_id=user_pool_id,
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
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolSigningCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user_pool_id": "userPoolId",
    },
)
class DataAwsCognitoUserPoolSigningCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user_pool_id: builtins.str,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#user_pool_id DataAwsCognitoUserPoolSigningCertificate#user_pool_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
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
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pool_signing_certificate#user_pool_id DataAwsCognitoUserPoolSigningCertificate#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCognitoUserPoolSigningCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCognitoUserPools(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPools",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools aws_cognito_user_pools}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools aws_cognito_user_pools} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#name DataAwsCognitoUserPools#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCognitoUserPoolsConfig(
            name=name,
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
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ids")
    def ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ids"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cognito.DataAwsCognitoUserPoolsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsCognitoUserPoolsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Cognito.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#name DataAwsCognitoUserPools#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cognito_user_pools#name DataAwsCognitoUserPools#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCognitoUserPoolsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CognitoIdentityPool",
    "CognitoIdentityPoolCognitoIdentityProviders",
    "CognitoIdentityPoolConfig",
    "CognitoIdentityPoolProviderPrincipalTag",
    "CognitoIdentityPoolProviderPrincipalTagConfig",
    "CognitoIdentityPoolRolesAttachment",
    "CognitoIdentityPoolRolesAttachmentConfig",
    "CognitoIdentityPoolRolesAttachmentRoleMapping",
    "CognitoIdentityPoolRolesAttachmentRoleMappingMappingRule",
    "CognitoIdentityProvider",
    "CognitoIdentityProviderConfig",
    "CognitoResourceServer",
    "CognitoResourceServerConfig",
    "CognitoResourceServerScope",
    "CognitoUserGroup",
    "CognitoUserGroupConfig",
    "CognitoUserPool",
    "CognitoUserPoolAccountRecoverySetting",
    "CognitoUserPoolAccountRecoverySettingOutputReference",
    "CognitoUserPoolAccountRecoverySettingRecoveryMechanism",
    "CognitoUserPoolAdminCreateUserConfig",
    "CognitoUserPoolAdminCreateUserConfigInviteMessageTemplate",
    "CognitoUserPoolAdminCreateUserConfigInviteMessageTemplateOutputReference",
    "CognitoUserPoolAdminCreateUserConfigOutputReference",
    "CognitoUserPoolClient",
    "CognitoUserPoolClientAnalyticsConfiguration",
    "CognitoUserPoolClientAnalyticsConfigurationOutputReference",
    "CognitoUserPoolClientConfig",
    "CognitoUserPoolClientTokenValidityUnits",
    "CognitoUserPoolClientTokenValidityUnitsOutputReference",
    "CognitoUserPoolConfig",
    "CognitoUserPoolDeviceConfiguration",
    "CognitoUserPoolDeviceConfigurationOutputReference",
    "CognitoUserPoolDomain",
    "CognitoUserPoolDomainConfig",
    "CognitoUserPoolEmailConfiguration",
    "CognitoUserPoolEmailConfigurationOutputReference",
    "CognitoUserPoolLambdaConfig",
    "CognitoUserPoolLambdaConfigCustomEmailSender",
    "CognitoUserPoolLambdaConfigCustomEmailSenderOutputReference",
    "CognitoUserPoolLambdaConfigCustomSmsSender",
    "CognitoUserPoolLambdaConfigCustomSmsSenderOutputReference",
    "CognitoUserPoolLambdaConfigOutputReference",
    "CognitoUserPoolPasswordPolicy",
    "CognitoUserPoolPasswordPolicyOutputReference",
    "CognitoUserPoolSchema",
    "CognitoUserPoolSchemaNumberAttributeConstraints",
    "CognitoUserPoolSchemaNumberAttributeConstraintsOutputReference",
    "CognitoUserPoolSchemaStringAttributeConstraints",
    "CognitoUserPoolSchemaStringAttributeConstraintsOutputReference",
    "CognitoUserPoolSmsConfiguration",
    "CognitoUserPoolSmsConfigurationOutputReference",
    "CognitoUserPoolSoftwareTokenMfaConfiguration",
    "CognitoUserPoolSoftwareTokenMfaConfigurationOutputReference",
    "CognitoUserPoolUiCustomization",
    "CognitoUserPoolUiCustomizationConfig",
    "CognitoUserPoolUserPoolAddOns",
    "CognitoUserPoolUserPoolAddOnsOutputReference",
    "CognitoUserPoolUsernameConfiguration",
    "CognitoUserPoolUsernameConfigurationOutputReference",
    "CognitoUserPoolVerificationMessageTemplate",
    "CognitoUserPoolVerificationMessageTemplateOutputReference",
    "DataAwsCognitoUserPoolClient",
    "DataAwsCognitoUserPoolClientAnalyticsConfiguration",
    "DataAwsCognitoUserPoolClientConfig",
    "DataAwsCognitoUserPoolClientTokenValidityUnits",
    "DataAwsCognitoUserPoolClients",
    "DataAwsCognitoUserPoolClientsConfig",
    "DataAwsCognitoUserPoolSigningCertificate",
    "DataAwsCognitoUserPoolSigningCertificateConfig",
    "DataAwsCognitoUserPools",
    "DataAwsCognitoUserPoolsConfig",
]

publication.publish()
