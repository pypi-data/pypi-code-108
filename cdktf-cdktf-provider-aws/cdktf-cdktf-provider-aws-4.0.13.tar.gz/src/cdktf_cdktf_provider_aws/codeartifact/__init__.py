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


class CodeartifactDomain(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactDomain",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain aws_codeartifact_domain}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        encryption_key: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain aws_codeartifact_domain} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#domain CodeartifactDomain#domain}.
        :param encryption_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#encryption_key CodeartifactDomain#encryption_key}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#tags CodeartifactDomain#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#tags_all CodeartifactDomain#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodeartifactDomainConfig(
            domain=domain,
            encryption_key=encryption_key,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEncryptionKey")
    def reset_encryption_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKey", []))

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
    @jsii.member(jsii_name="assetSizeBytes")
    def asset_size_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "assetSizeBytes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdTime")
    def created_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryCount")
    def repository_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "repositoryCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKeyInput")
    def encryption_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKeyInput"))

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
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKey"))

    @encryption_key.setter
    def encryption_key(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionKey", value)

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
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactDomainConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "encryption_key": "encryptionKey",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CodeartifactDomainConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        encryption_key: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CodeArtifact.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#domain CodeartifactDomain#domain}.
        :param encryption_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#encryption_key CodeartifactDomain#encryption_key}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#tags CodeartifactDomain#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#tags_all CodeartifactDomain#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#domain CodeartifactDomain#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#encryption_key CodeartifactDomain#encryption_key}.'''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#tags CodeartifactDomain#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain#tags_all CodeartifactDomain#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeartifactDomainConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeartifactDomainPermissionsPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactDomainPermissionsPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy aws_codeartifact_domain_permissions_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        policy_document: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        policy_revision: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy aws_codeartifact_domain_permissions_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#domain CodeartifactDomainPermissionsPolicy#domain}.
        :param policy_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#policy_document CodeartifactDomainPermissionsPolicy#policy_document}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#domain_owner CodeartifactDomainPermissionsPolicy#domain_owner}.
        :param policy_revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#policy_revision CodeartifactDomainPermissionsPolicy#policy_revision}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodeartifactDomainPermissionsPolicyConfig(
            domain=domain,
            policy_document=policy_document,
            domain_owner=domain_owner,
            policy_revision=policy_revision,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDomainOwner")
    def reset_domain_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainOwner", []))

    @jsii.member(jsii_name="resetPolicyRevision")
    def reset_policy_revision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyRevision", []))

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
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwnerInput")
    def domain_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDocumentInput")
    def policy_document_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyDocumentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyRevisionInput")
    def policy_revision_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyRevisionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @domain_owner.setter
    def domain_owner(self, value: builtins.str) -> None:
        jsii.set(self, "domainOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyDocument"))

    @policy_document.setter
    def policy_document(self, value: builtins.str) -> None:
        jsii.set(self, "policyDocument", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyRevision")
    def policy_revision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyRevision"))

    @policy_revision.setter
    def policy_revision(self, value: builtins.str) -> None:
        jsii.set(self, "policyRevision", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactDomainPermissionsPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "policy_document": "policyDocument",
        "domain_owner": "domainOwner",
        "policy_revision": "policyRevision",
    },
)
class CodeartifactDomainPermissionsPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        policy_document: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        policy_revision: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CodeArtifact.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#domain CodeartifactDomainPermissionsPolicy#domain}.
        :param policy_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#policy_document CodeartifactDomainPermissionsPolicy#policy_document}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#domain_owner CodeartifactDomainPermissionsPolicy#domain_owner}.
        :param policy_revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#policy_revision CodeartifactDomainPermissionsPolicy#policy_revision}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "policy_document": policy_document,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if domain_owner is not None:
            self._values["domain_owner"] = domain_owner
        if policy_revision is not None:
            self._values["policy_revision"] = policy_revision

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#domain CodeartifactDomainPermissionsPolicy#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_document(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#policy_document CodeartifactDomainPermissionsPolicy#policy_document}.'''
        result = self._values.get("policy_document")
        assert result is not None, "Required property 'policy_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#domain_owner CodeartifactDomainPermissionsPolicy#domain_owner}.'''
        result = self._values.get("domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_revision(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_domain_permissions_policy#policy_revision CodeartifactDomainPermissionsPolicy#policy_revision}.'''
        result = self._values.get("policy_revision")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeartifactDomainPermissionsPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeartifactRepository(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository aws_codeartifact_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        repository: builtins.str,
        description: typing.Optional[builtins.str] = None,
        domain_owner: typing.Optional[builtins.str] = None,
        external_connections: typing.Optional["CodeartifactRepositoryExternalConnections"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        upstream: typing.Optional[typing.Sequence["CodeartifactRepositoryUpstream"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository aws_codeartifact_repository} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#domain CodeartifactRepository#domain}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#repository CodeartifactRepository#repository}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#description CodeartifactRepository#description}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#domain_owner CodeartifactRepository#domain_owner}.
        :param external_connections: external_connections block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#external_connections CodeartifactRepository#external_connections}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#tags CodeartifactRepository#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#tags_all CodeartifactRepository#tags_all}.
        :param upstream: upstream block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#upstream CodeartifactRepository#upstream}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodeartifactRepositoryConfig(
            domain=domain,
            repository=repository,
            description=description,
            domain_owner=domain_owner,
            external_connections=external_connections,
            tags=tags,
            tags_all=tags_all,
            upstream=upstream,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putExternalConnections")
    def put_external_connections(
        self,
        *,
        external_connection_name: builtins.str,
    ) -> None:
        '''
        :param external_connection_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#external_connection_name CodeartifactRepository#external_connection_name}.
        '''
        value = CodeartifactRepositoryExternalConnections(
            external_connection_name=external_connection_name
        )

        return typing.cast(None, jsii.invoke(self, "putExternalConnections", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDomainOwner")
    def reset_domain_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainOwner", []))

    @jsii.member(jsii_name="resetExternalConnections")
    def reset_external_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalConnections", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUpstream")
    def reset_upstream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpstream", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="administratorAccount")
    def administrator_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "administratorAccount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalConnections")
    def external_connections(
        self,
    ) -> "CodeartifactRepositoryExternalConnectionsOutputReference":
        return typing.cast("CodeartifactRepositoryExternalConnectionsOutputReference", jsii.get(self, "externalConnections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwnerInput")
    def domain_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalConnectionsInput")
    def external_connections_input(
        self,
    ) -> typing.Optional["CodeartifactRepositoryExternalConnections"]:
        return typing.cast(typing.Optional["CodeartifactRepositoryExternalConnections"], jsii.get(self, "externalConnectionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryInput"))

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
    @jsii.member(jsii_name="upstreamInput")
    def upstream_input(
        self,
    ) -> typing.Optional[typing.List["CodeartifactRepositoryUpstream"]]:
        return typing.cast(typing.Optional[typing.List["CodeartifactRepositoryUpstream"]], jsii.get(self, "upstreamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @domain_owner.setter
    def domain_owner(self, value: builtins.str) -> None:
        jsii.set(self, "domainOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)

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
    @jsii.member(jsii_name="upstream")
    def upstream(self) -> typing.List["CodeartifactRepositoryUpstream"]:
        return typing.cast(typing.List["CodeartifactRepositoryUpstream"], jsii.get(self, "upstream"))

    @upstream.setter
    def upstream(self, value: typing.List["CodeartifactRepositoryUpstream"]) -> None:
        jsii.set(self, "upstream", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "repository": "repository",
        "description": "description",
        "domain_owner": "domainOwner",
        "external_connections": "externalConnections",
        "tags": "tags",
        "tags_all": "tagsAll",
        "upstream": "upstream",
    },
)
class CodeartifactRepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        repository: builtins.str,
        description: typing.Optional[builtins.str] = None,
        domain_owner: typing.Optional[builtins.str] = None,
        external_connections: typing.Optional["CodeartifactRepositoryExternalConnections"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        upstream: typing.Optional[typing.Sequence["CodeartifactRepositoryUpstream"]] = None,
    ) -> None:
        '''AWS CodeArtifact.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#domain CodeartifactRepository#domain}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#repository CodeartifactRepository#repository}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#description CodeartifactRepository#description}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#domain_owner CodeartifactRepository#domain_owner}.
        :param external_connections: external_connections block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#external_connections CodeartifactRepository#external_connections}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#tags CodeartifactRepository#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#tags_all CodeartifactRepository#tags_all}.
        :param upstream: upstream block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#upstream CodeartifactRepository#upstream}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(external_connections, dict):
            external_connections = CodeartifactRepositoryExternalConnections(**external_connections)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "repository": repository,
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
        if domain_owner is not None:
            self._values["domain_owner"] = domain_owner
        if external_connections is not None:
            self._values["external_connections"] = external_connections
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if upstream is not None:
            self._values["upstream"] = upstream

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#domain CodeartifactRepository#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#repository CodeartifactRepository#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#description CodeartifactRepository#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#domain_owner CodeartifactRepository#domain_owner}.'''
        result = self._values.get("domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_connections(
        self,
    ) -> typing.Optional["CodeartifactRepositoryExternalConnections"]:
        '''external_connections block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#external_connections CodeartifactRepository#external_connections}
        '''
        result = self._values.get("external_connections")
        return typing.cast(typing.Optional["CodeartifactRepositoryExternalConnections"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#tags CodeartifactRepository#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#tags_all CodeartifactRepository#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def upstream(
        self,
    ) -> typing.Optional[typing.List["CodeartifactRepositoryUpstream"]]:
        '''upstream block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#upstream CodeartifactRepository#upstream}
        '''
        result = self._values.get("upstream")
        return typing.cast(typing.Optional[typing.List["CodeartifactRepositoryUpstream"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeartifactRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepositoryExternalConnections",
    jsii_struct_bases=[],
    name_mapping={"external_connection_name": "externalConnectionName"},
)
class CodeartifactRepositoryExternalConnections:
    def __init__(self, *, external_connection_name: builtins.str) -> None:
        '''
        :param external_connection_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#external_connection_name CodeartifactRepository#external_connection_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "external_connection_name": external_connection_name,
        }

    @builtins.property
    def external_connection_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#external_connection_name CodeartifactRepository#external_connection_name}.'''
        result = self._values.get("external_connection_name")
        assert result is not None, "Required property 'external_connection_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeartifactRepositoryExternalConnections(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeartifactRepositoryExternalConnectionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepositoryExternalConnectionsOutputReference",
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
    @jsii.member(jsii_name="externalConnectionNameInput")
    def external_connection_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalConnectionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalConnectionName")
    def external_connection_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalConnectionName"))

    @external_connection_name.setter
    def external_connection_name(self, value: builtins.str) -> None:
        jsii.set(self, "externalConnectionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodeartifactRepositoryExternalConnections]:
        return typing.cast(typing.Optional[CodeartifactRepositoryExternalConnections], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodeartifactRepositoryExternalConnections],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CodeartifactRepositoryPermissionsPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepositoryPermissionsPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy aws_codeartifact_repository_permissions_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        policy_document: builtins.str,
        repository: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        policy_revision: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy aws_codeartifact_repository_permissions_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#domain CodeartifactRepositoryPermissionsPolicy#domain}.
        :param policy_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#policy_document CodeartifactRepositoryPermissionsPolicy#policy_document}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#repository CodeartifactRepositoryPermissionsPolicy#repository}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#domain_owner CodeartifactRepositoryPermissionsPolicy#domain_owner}.
        :param policy_revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#policy_revision CodeartifactRepositoryPermissionsPolicy#policy_revision}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodeartifactRepositoryPermissionsPolicyConfig(
            domain=domain,
            policy_document=policy_document,
            repository=repository,
            domain_owner=domain_owner,
            policy_revision=policy_revision,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDomainOwner")
    def reset_domain_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainOwner", []))

    @jsii.member(jsii_name="resetPolicyRevision")
    def reset_policy_revision(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyRevision", []))

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
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwnerInput")
    def domain_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDocumentInput")
    def policy_document_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyDocumentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyRevisionInput")
    def policy_revision_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyRevisionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @domain_owner.setter
    def domain_owner(self, value: builtins.str) -> None:
        jsii.set(self, "domainOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyDocument"))

    @policy_document.setter
    def policy_document(self, value: builtins.str) -> None:
        jsii.set(self, "policyDocument", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyRevision")
    def policy_revision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyRevision"))

    @policy_revision.setter
    def policy_revision(self, value: builtins.str) -> None:
        jsii.set(self, "policyRevision", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepositoryPermissionsPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "policy_document": "policyDocument",
        "repository": "repository",
        "domain_owner": "domainOwner",
        "policy_revision": "policyRevision",
    },
)
class CodeartifactRepositoryPermissionsPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        policy_document: builtins.str,
        repository: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        policy_revision: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CodeArtifact.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#domain CodeartifactRepositoryPermissionsPolicy#domain}.
        :param policy_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#policy_document CodeartifactRepositoryPermissionsPolicy#policy_document}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#repository CodeartifactRepositoryPermissionsPolicy#repository}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#domain_owner CodeartifactRepositoryPermissionsPolicy#domain_owner}.
        :param policy_revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#policy_revision CodeartifactRepositoryPermissionsPolicy#policy_revision}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "policy_document": policy_document,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if domain_owner is not None:
            self._values["domain_owner"] = domain_owner
        if policy_revision is not None:
            self._values["policy_revision"] = policy_revision

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#domain CodeartifactRepositoryPermissionsPolicy#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_document(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#policy_document CodeartifactRepositoryPermissionsPolicy#policy_document}.'''
        result = self._values.get("policy_document")
        assert result is not None, "Required property 'policy_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#repository CodeartifactRepositoryPermissionsPolicy#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#domain_owner CodeartifactRepositoryPermissionsPolicy#domain_owner}.'''
        result = self._values.get("domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_revision(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository_permissions_policy#policy_revision CodeartifactRepositoryPermissionsPolicy#policy_revision}.'''
        result = self._values.get("policy_revision")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeartifactRepositoryPermissionsPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.CodeartifactRepositoryUpstream",
    jsii_struct_bases=[],
    name_mapping={"repository_name": "repositoryName"},
)
class CodeartifactRepositoryUpstream:
    def __init__(self, *, repository_name: builtins.str) -> None:
        '''
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#repository_name CodeartifactRepository#repository_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
        }

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codeartifact_repository#repository_name CodeartifactRepository#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeartifactRepositoryUpstream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCodeartifactAuthorizationToken(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.DataAwsCodeartifactAuthorizationToken",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token aws_codeartifact_authorization_token}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        duration_seconds: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token aws_codeartifact_authorization_token} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#domain DataAwsCodeartifactAuthorizationToken#domain}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#domain_owner DataAwsCodeartifactAuthorizationToken#domain_owner}.
        :param duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#duration_seconds DataAwsCodeartifactAuthorizationToken#duration_seconds}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCodeartifactAuthorizationTokenConfig(
            domain=domain,
            domain_owner=domain_owner,
            duration_seconds=duration_seconds,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDomainOwner")
    def reset_domain_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainOwner", []))

    @jsii.member(jsii_name="resetDurationSeconds")
    def reset_duration_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDurationSeconds", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationToken")
    def authorization_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizationToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwnerInput")
    def domain_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationSecondsInput")
    def duration_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @domain_owner.setter
    def domain_owner(self, value: builtins.str) -> None:
        jsii.set(self, "domainOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="durationSeconds")
    def duration_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "durationSeconds"))

    @duration_seconds.setter
    def duration_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "durationSeconds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.DataAwsCodeartifactAuthorizationTokenConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "domain_owner": "domainOwner",
        "duration_seconds": "durationSeconds",
    },
)
class DataAwsCodeartifactAuthorizationTokenConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        duration_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS CodeArtifact.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#domain DataAwsCodeartifactAuthorizationToken#domain}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#domain_owner DataAwsCodeartifactAuthorizationToken#domain_owner}.
        :param duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#duration_seconds DataAwsCodeartifactAuthorizationToken#duration_seconds}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if domain_owner is not None:
            self._values["domain_owner"] = domain_owner
        if duration_seconds is not None:
            self._values["duration_seconds"] = duration_seconds

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#domain DataAwsCodeartifactAuthorizationToken#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#domain_owner DataAwsCodeartifactAuthorizationToken#domain_owner}.'''
        result = self._values.get("domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_authorization_token#duration_seconds DataAwsCodeartifactAuthorizationToken#duration_seconds}.'''
        result = self._values.get("duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCodeartifactAuthorizationTokenConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCodeartifactRepositoryEndpoint(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codeartifact.DataAwsCodeartifactRepositoryEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint aws_codeartifact_repository_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        format: builtins.str,
        repository: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint aws_codeartifact_repository_endpoint} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#domain DataAwsCodeartifactRepositoryEndpoint#domain}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#format DataAwsCodeartifactRepositoryEndpoint#format}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#repository DataAwsCodeartifactRepositoryEndpoint#repository}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#domain_owner DataAwsCodeartifactRepositoryEndpoint#domain_owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCodeartifactRepositoryEndpointConfig(
            domain=domain,
            format=format,
            repository=repository,
            domain_owner=domain_owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDomainOwner")
    def reset_domain_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainOwner", []))

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
    @jsii.member(jsii_name="repositoryEndpoint")
    def repository_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwnerInput")
    def domain_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @domain_owner.setter
    def domain_owner(self, value: builtins.str) -> None:
        jsii.set(self, "domainOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codeartifact.DataAwsCodeartifactRepositoryEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "format": "format",
        "repository": "repository",
        "domain_owner": "domainOwner",
    },
)
class DataAwsCodeartifactRepositoryEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        format: builtins.str,
        repository: builtins.str,
        domain_owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CodeArtifact.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#domain DataAwsCodeartifactRepositoryEndpoint#domain}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#format DataAwsCodeartifactRepositoryEndpoint#format}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#repository DataAwsCodeartifactRepositoryEndpoint#repository}.
        :param domain_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#domain_owner DataAwsCodeartifactRepositoryEndpoint#domain_owner}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "format": format,
            "repository": repository,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if domain_owner is not None:
            self._values["domain_owner"] = domain_owner

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#domain DataAwsCodeartifactRepositoryEndpoint#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#format DataAwsCodeartifactRepositoryEndpoint#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#repository DataAwsCodeartifactRepositoryEndpoint#repository}.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codeartifact_repository_endpoint#domain_owner DataAwsCodeartifactRepositoryEndpoint#domain_owner}.'''
        result = self._values.get("domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCodeartifactRepositoryEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodeartifactDomain",
    "CodeartifactDomainConfig",
    "CodeartifactDomainPermissionsPolicy",
    "CodeartifactDomainPermissionsPolicyConfig",
    "CodeartifactRepository",
    "CodeartifactRepositoryConfig",
    "CodeartifactRepositoryExternalConnections",
    "CodeartifactRepositoryExternalConnectionsOutputReference",
    "CodeartifactRepositoryPermissionsPolicy",
    "CodeartifactRepositoryPermissionsPolicyConfig",
    "CodeartifactRepositoryUpstream",
    "DataAwsCodeartifactAuthorizationToken",
    "DataAwsCodeartifactAuthorizationTokenConfig",
    "DataAwsCodeartifactRepositoryEndpoint",
    "DataAwsCodeartifactRepositoryEndpointConfig",
]

publication.publish()
