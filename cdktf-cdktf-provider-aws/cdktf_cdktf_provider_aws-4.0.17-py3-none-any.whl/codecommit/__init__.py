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


class CodecommitApprovalRuleTemplate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitApprovalRuleTemplate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template aws_codecommit_approval_rule_template}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template aws_codecommit_approval_rule_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#content CodecommitApprovalRuleTemplate#content}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#name CodecommitApprovalRuleTemplate#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#description CodecommitApprovalRuleTemplate#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodecommitApprovalRuleTemplateConfig(
            content=content,
            name=name,
            description=description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="approvalRuleTemplateId")
    def approval_rule_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "approvalRuleTemplateId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedUser")
    def last_modified_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedUser"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleContentSha256")
    def rule_content_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleContentSha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        jsii.set(self, "content", value)

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


class CodecommitApprovalRuleTemplateAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitApprovalRuleTemplateAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association aws_codecommit_approval_rule_template_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        approval_rule_template_name: builtins.str,
        repository_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association aws_codecommit_approval_rule_template_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param approval_rule_template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association#approval_rule_template_name CodecommitApprovalRuleTemplateAssociation#approval_rule_template_name}.
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association#repository_name CodecommitApprovalRuleTemplateAssociation#repository_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodecommitApprovalRuleTemplateAssociationConfig(
            approval_rule_template_name=approval_rule_template_name,
            repository_name=repository_name,
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
    @jsii.member(jsii_name="approvalRuleTemplateNameInput")
    def approval_rule_template_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "approvalRuleTemplateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="approvalRuleTemplateName")
    def approval_rule_template_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "approvalRuleTemplateName"))

    @approval_rule_template_name.setter
    def approval_rule_template_name(self, value: builtins.str) -> None:
        jsii.set(self, "approvalRuleTemplateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitApprovalRuleTemplateAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "approval_rule_template_name": "approvalRuleTemplateName",
        "repository_name": "repositoryName",
    },
)
class CodecommitApprovalRuleTemplateAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        approval_rule_template_name: builtins.str,
        repository_name: builtins.str,
    ) -> None:
        '''AWS CodeCommit.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param approval_rule_template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association#approval_rule_template_name CodecommitApprovalRuleTemplateAssociation#approval_rule_template_name}.
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association#repository_name CodecommitApprovalRuleTemplateAssociation#repository_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "approval_rule_template_name": approval_rule_template_name,
            "repository_name": repository_name,
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
    def approval_rule_template_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association#approval_rule_template_name CodecommitApprovalRuleTemplateAssociation#approval_rule_template_name}.'''
        result = self._values.get("approval_rule_template_name")
        assert result is not None, "Required property 'approval_rule_template_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template_association#repository_name CodecommitApprovalRuleTemplateAssociation#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodecommitApprovalRuleTemplateAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitApprovalRuleTemplateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content": "content",
        "name": "name",
        "description": "description",
    },
)
class CodecommitApprovalRuleTemplateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CodeCommit.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#content CodecommitApprovalRuleTemplate#content}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#name CodecommitApprovalRuleTemplate#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#description CodecommitApprovalRuleTemplate#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
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
        if description is not None:
            self._values["description"] = description

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
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#content CodecommitApprovalRuleTemplate#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#name CodecommitApprovalRuleTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_approval_rule_template#description CodecommitApprovalRuleTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodecommitApprovalRuleTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodecommitRepository(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitRepository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository aws_codecommit_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository_name: builtins.str,
        default_branch: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository aws_codecommit_repository} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#repository_name CodecommitRepository#repository_name}.
        :param default_branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#default_branch CodecommitRepository#default_branch}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#description CodecommitRepository#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#tags CodecommitRepository#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#tags_all CodecommitRepository#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodecommitRepositoryConfig(
            repository_name=repository_name,
            default_branch=default_branch,
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDefaultBranch")
    def reset_default_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultBranch", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="cloneUrlHttp")
    def clone_url_http(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloneUrlHttp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloneUrlSsh")
    def clone_url_ssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloneUrlSsh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryId")
    def repository_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBranchInput")
    def default_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultBranchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

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
    @jsii.member(jsii_name="defaultBranch")
    def default_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultBranch"))

    @default_branch.setter
    def default_branch(self, value: builtins.str) -> None:
        jsii.set(self, "defaultBranch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)

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
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitRepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository_name": "repositoryName",
        "default_branch": "defaultBranch",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CodecommitRepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository_name: builtins.str,
        default_branch: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CodeCommit.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#repository_name CodecommitRepository#repository_name}.
        :param default_branch: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#default_branch CodecommitRepository#default_branch}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#description CodecommitRepository#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#tags CodecommitRepository#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#tags_all CodecommitRepository#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if default_branch is not None:
            self._values["default_branch"] = default_branch
        if description is not None:
            self._values["description"] = description
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
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#repository_name CodecommitRepository#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_branch(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#default_branch CodecommitRepository#default_branch}.'''
        result = self._values.get("default_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#description CodecommitRepository#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#tags CodecommitRepository#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_repository#tags_all CodecommitRepository#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodecommitRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodecommitTrigger(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitTrigger",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger aws_codecommit_trigger}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository_name: builtins.str,
        trigger: typing.Sequence["CodecommitTriggerTrigger"],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger aws_codecommit_trigger} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#repository_name CodecommitTrigger#repository_name}.
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#trigger CodecommitTrigger#trigger}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodecommitTriggerConfig(
            repository_name=repository_name,
            trigger=trigger,
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
    @jsii.member(jsii_name="configurationId")
    def configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggerInput")
    def trigger_input(self) -> typing.Optional[typing.List["CodecommitTriggerTrigger"]]:
        return typing.cast(typing.Optional[typing.List["CodecommitTriggerTrigger"]], jsii.get(self, "triggerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> typing.List["CodecommitTriggerTrigger"]:
        return typing.cast(typing.List["CodecommitTriggerTrigger"], jsii.get(self, "trigger"))

    @trigger.setter
    def trigger(self, value: typing.List["CodecommitTriggerTrigger"]) -> None:
        jsii.set(self, "trigger", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitTriggerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository_name": "repositoryName",
        "trigger": "trigger",
    },
)
class CodecommitTriggerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository_name: builtins.str,
        trigger: typing.Sequence["CodecommitTriggerTrigger"],
    ) -> None:
        '''AWS CodeCommit.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#repository_name CodecommitTrigger#repository_name}.
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#trigger CodecommitTrigger#trigger}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
            "trigger": trigger,
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
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#repository_name CodecommitTrigger#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def trigger(self) -> typing.List["CodecommitTriggerTrigger"]:
        '''trigger block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#trigger CodecommitTrigger#trigger}
        '''
        result = self._values.get("trigger")
        assert result is not None, "Required property 'trigger' is missing"
        return typing.cast(typing.List["CodecommitTriggerTrigger"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodecommitTriggerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codecommit.CodecommitTriggerTrigger",
    jsii_struct_bases=[],
    name_mapping={
        "destination_arn": "destinationArn",
        "events": "events",
        "name": "name",
        "branches": "branches",
        "custom_data": "customData",
    },
)
class CodecommitTriggerTrigger:
    def __init__(
        self,
        *,
        destination_arn: builtins.str,
        events: typing.Sequence[builtins.str],
        name: builtins.str,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#destination_arn CodecommitTrigger#destination_arn}.
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#events CodecommitTrigger#events}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#name CodecommitTrigger#name}.
        :param branches: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#branches CodecommitTrigger#branches}.
        :param custom_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#custom_data CodecommitTrigger#custom_data}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_arn": destination_arn,
            "events": events,
            "name": name,
        }
        if branches is not None:
            self._values["branches"] = branches
        if custom_data is not None:
            self._values["custom_data"] = custom_data

    @builtins.property
    def destination_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#destination_arn CodecommitTrigger#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#events CodecommitTrigger#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#name CodecommitTrigger#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#branches CodecommitTrigger#branches}.'''
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codecommit_trigger#custom_data CodecommitTrigger#custom_data}.'''
        result = self._values.get("custom_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodecommitTriggerTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCodecommitApprovalRuleTemplate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codecommit.DataAwsCodecommitApprovalRuleTemplate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/codecommit_approval_rule_template aws_codecommit_approval_rule_template}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/codecommit_approval_rule_template aws_codecommit_approval_rule_template} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codecommit_approval_rule_template#name DataAwsCodecommitApprovalRuleTemplate#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCodecommitApprovalRuleTemplateConfig(
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
    @jsii.member(jsii_name="approvalRuleTemplateId")
    def approval_rule_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "approvalRuleTemplateId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedDate")
    def last_modified_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedUser")
    def last_modified_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedUser"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleContentSha256")
    def rule_content_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleContentSha256"))

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
    jsii_type="@cdktf/provider-aws.codecommit.DataAwsCodecommitApprovalRuleTemplateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsCodecommitApprovalRuleTemplateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS CodeCommit.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codecommit_approval_rule_template#name DataAwsCodecommitApprovalRuleTemplate#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codecommit_approval_rule_template#name DataAwsCodecommitApprovalRuleTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCodecommitApprovalRuleTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCodecommitRepository(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codecommit.DataAwsCodecommitRepository",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/codecommit_repository aws_codecommit_repository}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repository_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/codecommit_repository aws_codecommit_repository} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codecommit_repository#repository_name DataAwsCodecommitRepository#repository_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCodecommitRepositoryConfig(
            repository_name=repository_name,
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
    @jsii.member(jsii_name="cloneUrlHttp")
    def clone_url_http(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloneUrlHttp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloneUrlSsh")
    def clone_url_ssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloneUrlSsh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryId")
    def repository_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codecommit.DataAwsCodecommitRepositoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "repository_name": "repositoryName",
    },
)
class DataAwsCodecommitRepositoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        repository_name: builtins.str,
    ) -> None:
        '''AWS CodeCommit.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codecommit_repository#repository_name DataAwsCodecommitRepository#repository_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
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
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/codecommit_repository#repository_name DataAwsCodecommitRepository#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCodecommitRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodecommitApprovalRuleTemplate",
    "CodecommitApprovalRuleTemplateAssociation",
    "CodecommitApprovalRuleTemplateAssociationConfig",
    "CodecommitApprovalRuleTemplateConfig",
    "CodecommitRepository",
    "CodecommitRepositoryConfig",
    "CodecommitTrigger",
    "CodecommitTriggerConfig",
    "CodecommitTriggerTrigger",
    "DataAwsCodecommitApprovalRuleTemplate",
    "DataAwsCodecommitApprovalRuleTemplateConfig",
    "DataAwsCodecommitRepository",
    "DataAwsCodecommitRepositoryConfig",
]

publication.publish()
