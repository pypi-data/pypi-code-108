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


class AmplifyApp(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyApp",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/amplify_app aws_amplify_app}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        access_token: typing.Optional[builtins.str] = None,
        auto_branch_creation_config: typing.Optional["AmplifyAppAutoBranchCreationConfig"] = None,
        auto_branch_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        basic_auth_credentials: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[builtins.str] = None,
        custom_rule: typing.Optional[typing.Sequence["AmplifyAppCustomRule"]] = None,
        description: typing.Optional[builtins.str] = None,
        enable_auto_branch_creation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_basic_auth: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_branch_auto_build: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_branch_auto_deletion: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment_variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        iam_service_role_arn: typing.Optional[builtins.str] = None,
        oauth_token: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/amplify_app aws_amplify_app} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#name AmplifyApp#name}.
        :param access_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#access_token AmplifyApp#access_token}.
        :param auto_branch_creation_config: auto_branch_creation_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#auto_branch_creation_config AmplifyApp#auto_branch_creation_config}
        :param auto_branch_creation_patterns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#auto_branch_creation_patterns AmplifyApp#auto_branch_creation_patterns}.
        :param basic_auth_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#basic_auth_credentials AmplifyApp#basic_auth_credentials}.
        :param build_spec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#build_spec AmplifyApp#build_spec}.
        :param custom_rule: custom_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#custom_rule AmplifyApp#custom_rule}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#description AmplifyApp#description}.
        :param enable_auto_branch_creation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_auto_branch_creation AmplifyApp#enable_auto_branch_creation}.
        :param enable_basic_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_basic_auth AmplifyApp#enable_basic_auth}.
        :param enable_branch_auto_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_branch_auto_build AmplifyApp#enable_branch_auto_build}.
        :param enable_branch_auto_deletion: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_branch_auto_deletion AmplifyApp#enable_branch_auto_deletion}.
        :param environment_variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#environment_variables AmplifyApp#environment_variables}.
        :param iam_service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#iam_service_role_arn AmplifyApp#iam_service_role_arn}.
        :param oauth_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#oauth_token AmplifyApp#oauth_token}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#platform AmplifyApp#platform}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#repository AmplifyApp#repository}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#tags AmplifyApp#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#tags_all AmplifyApp#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AmplifyAppConfig(
            name=name,
            access_token=access_token,
            auto_branch_creation_config=auto_branch_creation_config,
            auto_branch_creation_patterns=auto_branch_creation_patterns,
            basic_auth_credentials=basic_auth_credentials,
            build_spec=build_spec,
            custom_rule=custom_rule,
            description=description,
            enable_auto_branch_creation=enable_auto_branch_creation,
            enable_basic_auth=enable_basic_auth,
            enable_branch_auto_build=enable_branch_auto_build,
            enable_branch_auto_deletion=enable_branch_auto_deletion,
            environment_variables=environment_variables,
            iam_service_role_arn=iam_service_role_arn,
            oauth_token=oauth_token,
            platform=platform,
            repository=repository,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="productionBranch")
    def production_branch(self, index: builtins.str) -> "AmplifyAppProductionBranch":
        '''
        :param index: -
        '''
        return typing.cast("AmplifyAppProductionBranch", jsii.invoke(self, "productionBranch", [index]))

    @jsii.member(jsii_name="putAutoBranchCreationConfig")
    def put_auto_branch_creation_config(
        self,
        *,
        basic_auth_credentials: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[builtins.str] = None,
        enable_auto_build: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_basic_auth: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_performance_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment_variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        framework: typing.Optional[builtins.str] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param basic_auth_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#basic_auth_credentials AmplifyApp#basic_auth_credentials}.
        :param build_spec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#build_spec AmplifyApp#build_spec}.
        :param enable_auto_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_auto_build AmplifyApp#enable_auto_build}.
        :param enable_basic_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_basic_auth AmplifyApp#enable_basic_auth}.
        :param enable_performance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_performance_mode AmplifyApp#enable_performance_mode}.
        :param enable_pull_request_preview: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_pull_request_preview AmplifyApp#enable_pull_request_preview}.
        :param environment_variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#environment_variables AmplifyApp#environment_variables}.
        :param framework: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#framework AmplifyApp#framework}.
        :param pull_request_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#pull_request_environment_name AmplifyApp#pull_request_environment_name}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#stage AmplifyApp#stage}.
        '''
        value = AmplifyAppAutoBranchCreationConfig(
            basic_auth_credentials=basic_auth_credentials,
            build_spec=build_spec,
            enable_auto_build=enable_auto_build,
            enable_basic_auth=enable_basic_auth,
            enable_performance_mode=enable_performance_mode,
            enable_pull_request_preview=enable_pull_request_preview,
            environment_variables=environment_variables,
            framework=framework,
            pull_request_environment_name=pull_request_environment_name,
            stage=stage,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoBranchCreationConfig", [value]))

    @jsii.member(jsii_name="resetAccessToken")
    def reset_access_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessToken", []))

    @jsii.member(jsii_name="resetAutoBranchCreationConfig")
    def reset_auto_branch_creation_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoBranchCreationConfig", []))

    @jsii.member(jsii_name="resetAutoBranchCreationPatterns")
    def reset_auto_branch_creation_patterns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoBranchCreationPatterns", []))

    @jsii.member(jsii_name="resetBasicAuthCredentials")
    def reset_basic_auth_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicAuthCredentials", []))

    @jsii.member(jsii_name="resetBuildSpec")
    def reset_build_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildSpec", []))

    @jsii.member(jsii_name="resetCustomRule")
    def reset_custom_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomRule", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnableAutoBranchCreation")
    def reset_enable_auto_branch_creation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAutoBranchCreation", []))

    @jsii.member(jsii_name="resetEnableBasicAuth")
    def reset_enable_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBasicAuth", []))

    @jsii.member(jsii_name="resetEnableBranchAutoBuild")
    def reset_enable_branch_auto_build(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBranchAutoBuild", []))

    @jsii.member(jsii_name="resetEnableBranchAutoDeletion")
    def reset_enable_branch_auto_deletion(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBranchAutoDeletion", []))

    @jsii.member(jsii_name="resetEnvironmentVariables")
    def reset_environment_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVariables", []))

    @jsii.member(jsii_name="resetIamServiceRoleArn")
    def reset_iam_service_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamServiceRoleArn", []))

    @jsii.member(jsii_name="resetOauthToken")
    def reset_oauth_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthToken", []))

    @jsii.member(jsii_name="resetPlatform")
    def reset_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatform", []))

    @jsii.member(jsii_name="resetRepository")
    def reset_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepository", []))

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
    @jsii.member(jsii_name="autoBranchCreationConfig")
    def auto_branch_creation_config(
        self,
    ) -> "AmplifyAppAutoBranchCreationConfigOutputReference":
        return typing.cast("AmplifyAppAutoBranchCreationConfigOutputReference", jsii.get(self, "autoBranchCreationConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultDomain")
    def default_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTokenInput")
    def access_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoBranchCreationConfigInput")
    def auto_branch_creation_config_input(
        self,
    ) -> typing.Optional["AmplifyAppAutoBranchCreationConfig"]:
        return typing.cast(typing.Optional["AmplifyAppAutoBranchCreationConfig"], jsii.get(self, "autoBranchCreationConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoBranchCreationPatternsInput")
    def auto_branch_creation_patterns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "autoBranchCreationPatternsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthCredentialsInput")
    def basic_auth_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "basicAuthCredentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildSpecInput")
    def build_spec_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customRuleInput")
    def custom_rule_input(self) -> typing.Optional[typing.List["AmplifyAppCustomRule"]]:
        return typing.cast(typing.Optional[typing.List["AmplifyAppCustomRule"]], jsii.get(self, "customRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBranchCreationInput")
    def enable_auto_branch_creation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableAutoBranchCreationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBasicAuthInput")
    def enable_basic_auth_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableBasicAuthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBranchAutoBuildInput")
    def enable_branch_auto_build_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableBranchAutoBuildInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBranchAutoDeletionInput")
    def enable_branch_auto_deletion_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableBranchAutoDeletionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariablesInput")
    def environment_variables_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "environmentVariablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamServiceRoleArnInput")
    def iam_service_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamServiceRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oauthTokenInput")
    def oauth_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oauthTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformInput")
    def platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformInput"))

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
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(self, value: builtins.str) -> None:
        jsii.set(self, "accessToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoBranchCreationPatterns")
    def auto_branch_creation_patterns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "autoBranchCreationPatterns"))

    @auto_branch_creation_patterns.setter
    def auto_branch_creation_patterns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "autoBranchCreationPatterns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthCredentials")
    def basic_auth_credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "basicAuthCredentials"))

    @basic_auth_credentials.setter
    def basic_auth_credentials(self, value: builtins.str) -> None:
        jsii.set(self, "basicAuthCredentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildSpec"))

    @build_spec.setter
    def build_spec(self, value: builtins.str) -> None:
        jsii.set(self, "buildSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customRule")
    def custom_rule(self) -> typing.List["AmplifyAppCustomRule"]:
        return typing.cast(typing.List["AmplifyAppCustomRule"], jsii.get(self, "customRule"))

    @custom_rule.setter
    def custom_rule(self, value: typing.List["AmplifyAppCustomRule"]) -> None:
        jsii.set(self, "customRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBranchCreation")
    def enable_auto_branch_creation(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableAutoBranchCreation"))

    @enable_auto_branch_creation.setter
    def enable_auto_branch_creation(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableAutoBranchCreation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBasicAuth")
    def enable_basic_auth(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableBasicAuth"))

    @enable_basic_auth.setter
    def enable_basic_auth(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableBasicAuth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBranchAutoBuild")
    def enable_branch_auto_build(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableBranchAutoBuild"))

    @enable_branch_auto_build.setter
    def enable_branch_auto_build(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableBranchAutoBuild", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBranchAutoDeletion")
    def enable_branch_auto_deletion(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableBranchAutoDeletion"))

    @enable_branch_auto_deletion.setter
    def enable_branch_auto_deletion(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableBranchAutoDeletion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVariables"))

    @environment_variables.setter
    def environment_variables(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "environmentVariables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamServiceRoleArn")
    def iam_service_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamServiceRoleArn"))

    @iam_service_role_arn.setter
    def iam_service_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "iamServiceRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oauthToken")
    def oauth_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oauthToken"))

    @oauth_token.setter
    def oauth_token(self, value: builtins.str) -> None:
        jsii.set(self, "oauthToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @platform.setter
    def platform(self, value: builtins.str) -> None:
        jsii.set(self, "platform", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyAppAutoBranchCreationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "basic_auth_credentials": "basicAuthCredentials",
        "build_spec": "buildSpec",
        "enable_auto_build": "enableAutoBuild",
        "enable_basic_auth": "enableBasicAuth",
        "enable_performance_mode": "enablePerformanceMode",
        "enable_pull_request_preview": "enablePullRequestPreview",
        "environment_variables": "environmentVariables",
        "framework": "framework",
        "pull_request_environment_name": "pullRequestEnvironmentName",
        "stage": "stage",
    },
)
class AmplifyAppAutoBranchCreationConfig:
    def __init__(
        self,
        *,
        basic_auth_credentials: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[builtins.str] = None,
        enable_auto_build: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_basic_auth: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_performance_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment_variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        framework: typing.Optional[builtins.str] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param basic_auth_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#basic_auth_credentials AmplifyApp#basic_auth_credentials}.
        :param build_spec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#build_spec AmplifyApp#build_spec}.
        :param enable_auto_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_auto_build AmplifyApp#enable_auto_build}.
        :param enable_basic_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_basic_auth AmplifyApp#enable_basic_auth}.
        :param enable_performance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_performance_mode AmplifyApp#enable_performance_mode}.
        :param enable_pull_request_preview: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_pull_request_preview AmplifyApp#enable_pull_request_preview}.
        :param environment_variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#environment_variables AmplifyApp#environment_variables}.
        :param framework: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#framework AmplifyApp#framework}.
        :param pull_request_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#pull_request_environment_name AmplifyApp#pull_request_environment_name}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#stage AmplifyApp#stage}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if basic_auth_credentials is not None:
            self._values["basic_auth_credentials"] = basic_auth_credentials
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if enable_auto_build is not None:
            self._values["enable_auto_build"] = enable_auto_build
        if enable_basic_auth is not None:
            self._values["enable_basic_auth"] = enable_basic_auth
        if enable_performance_mode is not None:
            self._values["enable_performance_mode"] = enable_performance_mode
        if enable_pull_request_preview is not None:
            self._values["enable_pull_request_preview"] = enable_pull_request_preview
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if framework is not None:
            self._values["framework"] = framework
        if pull_request_environment_name is not None:
            self._values["pull_request_environment_name"] = pull_request_environment_name
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def basic_auth_credentials(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#basic_auth_credentials AmplifyApp#basic_auth_credentials}.'''
        result = self._values.get("basic_auth_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#build_spec AmplifyApp#build_spec}.'''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_build(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_auto_build AmplifyApp#enable_auto_build}.'''
        result = self._values.get("enable_auto_build")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_basic_auth(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_basic_auth AmplifyApp#enable_basic_auth}.'''
        result = self._values.get("enable_basic_auth")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_performance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_performance_mode AmplifyApp#enable_performance_mode}.'''
        result = self._values.get("enable_performance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_pull_request_preview(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_pull_request_preview AmplifyApp#enable_pull_request_preview}.'''
        result = self._values.get("enable_pull_request_preview")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#environment_variables AmplifyApp#environment_variables}.'''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def framework(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#framework AmplifyApp#framework}.'''
        result = self._values.get("framework")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#pull_request_environment_name AmplifyApp#pull_request_environment_name}.'''
        result = self._values.get("pull_request_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#stage AmplifyApp#stage}.'''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyAppAutoBranchCreationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AmplifyAppAutoBranchCreationConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyAppAutoBranchCreationConfigOutputReference",
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

    @jsii.member(jsii_name="resetBasicAuthCredentials")
    def reset_basic_auth_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicAuthCredentials", []))

    @jsii.member(jsii_name="resetBuildSpec")
    def reset_build_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildSpec", []))

    @jsii.member(jsii_name="resetEnableAutoBuild")
    def reset_enable_auto_build(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAutoBuild", []))

    @jsii.member(jsii_name="resetEnableBasicAuth")
    def reset_enable_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBasicAuth", []))

    @jsii.member(jsii_name="resetEnablePerformanceMode")
    def reset_enable_performance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePerformanceMode", []))

    @jsii.member(jsii_name="resetEnablePullRequestPreview")
    def reset_enable_pull_request_preview(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePullRequestPreview", []))

    @jsii.member(jsii_name="resetEnvironmentVariables")
    def reset_environment_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVariables", []))

    @jsii.member(jsii_name="resetFramework")
    def reset_framework(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFramework", []))

    @jsii.member(jsii_name="resetPullRequestEnvironmentName")
    def reset_pull_request_environment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullRequestEnvironmentName", []))

    @jsii.member(jsii_name="resetStage")
    def reset_stage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthCredentialsInput")
    def basic_auth_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "basicAuthCredentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildSpecInput")
    def build_spec_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBuildInput")
    def enable_auto_build_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableAutoBuildInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBasicAuthInput")
    def enable_basic_auth_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableBasicAuthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePerformanceModeInput")
    def enable_performance_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enablePerformanceModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePullRequestPreviewInput")
    def enable_pull_request_preview_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enablePullRequestPreviewInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariablesInput")
    def environment_variables_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "environmentVariablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameworkInput")
    def framework_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frameworkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullRequestEnvironmentNameInput")
    def pull_request_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullRequestEnvironmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageInput")
    def stage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthCredentials")
    def basic_auth_credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "basicAuthCredentials"))

    @basic_auth_credentials.setter
    def basic_auth_credentials(self, value: builtins.str) -> None:
        jsii.set(self, "basicAuthCredentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildSpec"))

    @build_spec.setter
    def build_spec(self, value: builtins.str) -> None:
        jsii.set(self, "buildSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBuild")
    def enable_auto_build(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableAutoBuild"))

    @enable_auto_build.setter
    def enable_auto_build(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableAutoBuild", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBasicAuth")
    def enable_basic_auth(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableBasicAuth"))

    @enable_basic_auth.setter
    def enable_basic_auth(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableBasicAuth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePerformanceMode")
    def enable_performance_mode(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enablePerformanceMode"))

    @enable_performance_mode.setter
    def enable_performance_mode(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enablePerformanceMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePullRequestPreview")
    def enable_pull_request_preview(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enablePullRequestPreview"))

    @enable_pull_request_preview.setter
    def enable_pull_request_preview(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enablePullRequestPreview", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVariables"))

    @environment_variables.setter
    def environment_variables(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "environmentVariables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="framework")
    def framework(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "framework"))

    @framework.setter
    def framework(self, value: builtins.str) -> None:
        jsii.set(self, "framework", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullRequestEnvironmentName")
    def pull_request_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullRequestEnvironmentName"))

    @pull_request_environment_name.setter
    def pull_request_environment_name(self, value: builtins.str) -> None:
        jsii.set(self, "pullRequestEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: builtins.str) -> None:
        jsii.set(self, "stage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AmplifyAppAutoBranchCreationConfig]:
        return typing.cast(typing.Optional[AmplifyAppAutoBranchCreationConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AmplifyAppAutoBranchCreationConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyAppConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "access_token": "accessToken",
        "auto_branch_creation_config": "autoBranchCreationConfig",
        "auto_branch_creation_patterns": "autoBranchCreationPatterns",
        "basic_auth_credentials": "basicAuthCredentials",
        "build_spec": "buildSpec",
        "custom_rule": "customRule",
        "description": "description",
        "enable_auto_branch_creation": "enableAutoBranchCreation",
        "enable_basic_auth": "enableBasicAuth",
        "enable_branch_auto_build": "enableBranchAutoBuild",
        "enable_branch_auto_deletion": "enableBranchAutoDeletion",
        "environment_variables": "environmentVariables",
        "iam_service_role_arn": "iamServiceRoleArn",
        "oauth_token": "oauthToken",
        "platform": "platform",
        "repository": "repository",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class AmplifyAppConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        access_token: typing.Optional[builtins.str] = None,
        auto_branch_creation_config: typing.Optional[AmplifyAppAutoBranchCreationConfig] = None,
        auto_branch_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        basic_auth_credentials: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[builtins.str] = None,
        custom_rule: typing.Optional[typing.Sequence["AmplifyAppCustomRule"]] = None,
        description: typing.Optional[builtins.str] = None,
        enable_auto_branch_creation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_basic_auth: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_branch_auto_build: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_branch_auto_deletion: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment_variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        iam_service_role_arn: typing.Optional[builtins.str] = None,
        oauth_token: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Amplify.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#name AmplifyApp#name}.
        :param access_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#access_token AmplifyApp#access_token}.
        :param auto_branch_creation_config: auto_branch_creation_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#auto_branch_creation_config AmplifyApp#auto_branch_creation_config}
        :param auto_branch_creation_patterns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#auto_branch_creation_patterns AmplifyApp#auto_branch_creation_patterns}.
        :param basic_auth_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#basic_auth_credentials AmplifyApp#basic_auth_credentials}.
        :param build_spec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#build_spec AmplifyApp#build_spec}.
        :param custom_rule: custom_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#custom_rule AmplifyApp#custom_rule}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#description AmplifyApp#description}.
        :param enable_auto_branch_creation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_auto_branch_creation AmplifyApp#enable_auto_branch_creation}.
        :param enable_basic_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_basic_auth AmplifyApp#enable_basic_auth}.
        :param enable_branch_auto_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_branch_auto_build AmplifyApp#enable_branch_auto_build}.
        :param enable_branch_auto_deletion: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_branch_auto_deletion AmplifyApp#enable_branch_auto_deletion}.
        :param environment_variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#environment_variables AmplifyApp#environment_variables}.
        :param iam_service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#iam_service_role_arn AmplifyApp#iam_service_role_arn}.
        :param oauth_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#oauth_token AmplifyApp#oauth_token}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#platform AmplifyApp#platform}.
        :param repository: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#repository AmplifyApp#repository}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#tags AmplifyApp#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#tags_all AmplifyApp#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(auto_branch_creation_config, dict):
            auto_branch_creation_config = AmplifyAppAutoBranchCreationConfig(**auto_branch_creation_config)
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
        if access_token is not None:
            self._values["access_token"] = access_token
        if auto_branch_creation_config is not None:
            self._values["auto_branch_creation_config"] = auto_branch_creation_config
        if auto_branch_creation_patterns is not None:
            self._values["auto_branch_creation_patterns"] = auto_branch_creation_patterns
        if basic_auth_credentials is not None:
            self._values["basic_auth_credentials"] = basic_auth_credentials
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if custom_rule is not None:
            self._values["custom_rule"] = custom_rule
        if description is not None:
            self._values["description"] = description
        if enable_auto_branch_creation is not None:
            self._values["enable_auto_branch_creation"] = enable_auto_branch_creation
        if enable_basic_auth is not None:
            self._values["enable_basic_auth"] = enable_basic_auth
        if enable_branch_auto_build is not None:
            self._values["enable_branch_auto_build"] = enable_branch_auto_build
        if enable_branch_auto_deletion is not None:
            self._values["enable_branch_auto_deletion"] = enable_branch_auto_deletion
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if iam_service_role_arn is not None:
            self._values["iam_service_role_arn"] = iam_service_role_arn
        if oauth_token is not None:
            self._values["oauth_token"] = oauth_token
        if platform is not None:
            self._values["platform"] = platform
        if repository is not None:
            self._values["repository"] = repository
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#name AmplifyApp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#access_token AmplifyApp#access_token}.'''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_branch_creation_config(
        self,
    ) -> typing.Optional[AmplifyAppAutoBranchCreationConfig]:
        '''auto_branch_creation_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#auto_branch_creation_config AmplifyApp#auto_branch_creation_config}
        '''
        result = self._values.get("auto_branch_creation_config")
        return typing.cast(typing.Optional[AmplifyAppAutoBranchCreationConfig], result)

    @builtins.property
    def auto_branch_creation_patterns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#auto_branch_creation_patterns AmplifyApp#auto_branch_creation_patterns}.'''
        result = self._values.get("auto_branch_creation_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def basic_auth_credentials(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#basic_auth_credentials AmplifyApp#basic_auth_credentials}.'''
        result = self._values.get("basic_auth_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#build_spec AmplifyApp#build_spec}.'''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_rule(self) -> typing.Optional[typing.List["AmplifyAppCustomRule"]]:
        '''custom_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#custom_rule AmplifyApp#custom_rule}
        '''
        result = self._values.get("custom_rule")
        return typing.cast(typing.Optional[typing.List["AmplifyAppCustomRule"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#description AmplifyApp#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_branch_creation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_auto_branch_creation AmplifyApp#enable_auto_branch_creation}.'''
        result = self._values.get("enable_auto_branch_creation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_basic_auth(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_basic_auth AmplifyApp#enable_basic_auth}.'''
        result = self._values.get("enable_basic_auth")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_branch_auto_build(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_branch_auto_build AmplifyApp#enable_branch_auto_build}.'''
        result = self._values.get("enable_branch_auto_build")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_branch_auto_deletion(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#enable_branch_auto_deletion AmplifyApp#enable_branch_auto_deletion}.'''
        result = self._values.get("enable_branch_auto_deletion")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#environment_variables AmplifyApp#environment_variables}.'''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def iam_service_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#iam_service_role_arn AmplifyApp#iam_service_role_arn}.'''
        result = self._values.get("iam_service_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#oauth_token AmplifyApp#oauth_token}.'''
        result = self._values.get("oauth_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#platform AmplifyApp#platform}.'''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#repository AmplifyApp#repository}.'''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#tags AmplifyApp#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#tags_all AmplifyApp#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyAppConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyAppCustomRule",
    jsii_struct_bases=[],
    name_mapping={
        "source": "source",
        "target": "target",
        "condition": "condition",
        "status": "status",
    },
)
class AmplifyAppCustomRule:
    def __init__(
        self,
        *,
        source: builtins.str,
        target: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#source AmplifyApp#source}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#target AmplifyApp#target}.
        :param condition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#condition AmplifyApp#condition}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#status AmplifyApp#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
            "target": target,
        }
        if condition is not None:
            self._values["condition"] = condition
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#source AmplifyApp#source}.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#target AmplifyApp#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#condition AmplifyApp#condition}.'''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_app#status AmplifyApp#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyAppCustomRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AmplifyAppProductionBranch(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyAppProductionBranch",
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
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastDeployTime")
    def last_deploy_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastDeployTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thumbnailUrl")
    def thumbnail_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thumbnailUrl"))


class AmplifyBackendEnvironment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyBackendEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment aws_amplify_backend_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        environment_name: builtins.str,
        deployment_artifacts: typing.Optional[builtins.str] = None,
        stack_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment aws_amplify_backend_environment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#app_id AmplifyBackendEnvironment#app_id}.
        :param environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#environment_name AmplifyBackendEnvironment#environment_name}.
        :param deployment_artifacts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#deployment_artifacts AmplifyBackendEnvironment#deployment_artifacts}.
        :param stack_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#stack_name AmplifyBackendEnvironment#stack_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AmplifyBackendEnvironmentConfig(
            app_id=app_id,
            environment_name=environment_name,
            deployment_artifacts=deployment_artifacts,
            stack_name=stack_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDeploymentArtifacts")
    def reset_deployment_artifacts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentArtifacts", []))

    @jsii.member(jsii_name="resetStackName")
    def reset_stack_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStackName", []))

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
    @jsii.member(jsii_name="appIdInput")
    def app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentArtifactsInput")
    def deployment_artifacts_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentArtifactsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentNameInput")
    def environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackNameInput")
    def stack_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        jsii.set(self, "appId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentArtifacts")
    def deployment_artifacts(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentArtifacts"))

    @deployment_artifacts.setter
    def deployment_artifacts(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentArtifacts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentName")
    def environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environmentName"))

    @environment_name.setter
    def environment_name(self, value: builtins.str) -> None:
        jsii.set(self, "environmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackName"))

    @stack_name.setter
    def stack_name(self, value: builtins.str) -> None:
        jsii.set(self, "stackName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyBackendEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "app_id": "appId",
        "environment_name": "environmentName",
        "deployment_artifacts": "deploymentArtifacts",
        "stack_name": "stackName",
    },
)
class AmplifyBackendEnvironmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        app_id: builtins.str,
        environment_name: builtins.str,
        deployment_artifacts: typing.Optional[builtins.str] = None,
        stack_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Amplify.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#app_id AmplifyBackendEnvironment#app_id}.
        :param environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#environment_name AmplifyBackendEnvironment#environment_name}.
        :param deployment_artifacts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#deployment_artifacts AmplifyBackendEnvironment#deployment_artifacts}.
        :param stack_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#stack_name AmplifyBackendEnvironment#stack_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "environment_name": environment_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if deployment_artifacts is not None:
            self._values["deployment_artifacts"] = deployment_artifacts
        if stack_name is not None:
            self._values["stack_name"] = stack_name

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
    def app_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#app_id AmplifyBackendEnvironment#app_id}.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#environment_name AmplifyBackendEnvironment#environment_name}.'''
        result = self._values.get("environment_name")
        assert result is not None, "Required property 'environment_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deployment_artifacts(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#deployment_artifacts AmplifyBackendEnvironment#deployment_artifacts}.'''
        result = self._values.get("deployment_artifacts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_backend_environment#stack_name AmplifyBackendEnvironment#stack_name}.'''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyBackendEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AmplifyBranch(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyBranch",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch aws_amplify_branch}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        branch_name: builtins.str,
        backend_environment_arn: typing.Optional[builtins.str] = None,
        basic_auth_credentials: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        enable_auto_build: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_basic_auth: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_notification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_performance_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment_variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        framework: typing.Optional[builtins.str] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        ttl: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch aws_amplify_branch} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#app_id AmplifyBranch#app_id}.
        :param branch_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#branch_name AmplifyBranch#branch_name}.
        :param backend_environment_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#backend_environment_arn AmplifyBranch#backend_environment_arn}.
        :param basic_auth_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#basic_auth_credentials AmplifyBranch#basic_auth_credentials}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#description AmplifyBranch#description}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#display_name AmplifyBranch#display_name}.
        :param enable_auto_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_auto_build AmplifyBranch#enable_auto_build}.
        :param enable_basic_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_basic_auth AmplifyBranch#enable_basic_auth}.
        :param enable_notification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_notification AmplifyBranch#enable_notification}.
        :param enable_performance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_performance_mode AmplifyBranch#enable_performance_mode}.
        :param enable_pull_request_preview: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_pull_request_preview AmplifyBranch#enable_pull_request_preview}.
        :param environment_variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#environment_variables AmplifyBranch#environment_variables}.
        :param framework: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#framework AmplifyBranch#framework}.
        :param pull_request_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#pull_request_environment_name AmplifyBranch#pull_request_environment_name}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#stage AmplifyBranch#stage}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#tags AmplifyBranch#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#tags_all AmplifyBranch#tags_all}.
        :param ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#ttl AmplifyBranch#ttl}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AmplifyBranchConfig(
            app_id=app_id,
            branch_name=branch_name,
            backend_environment_arn=backend_environment_arn,
            basic_auth_credentials=basic_auth_credentials,
            description=description,
            display_name=display_name,
            enable_auto_build=enable_auto_build,
            enable_basic_auth=enable_basic_auth,
            enable_notification=enable_notification,
            enable_performance_mode=enable_performance_mode,
            enable_pull_request_preview=enable_pull_request_preview,
            environment_variables=environment_variables,
            framework=framework,
            pull_request_environment_name=pull_request_environment_name,
            stage=stage,
            tags=tags,
            tags_all=tags_all,
            ttl=ttl,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBackendEnvironmentArn")
    def reset_backend_environment_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackendEnvironmentArn", []))

    @jsii.member(jsii_name="resetBasicAuthCredentials")
    def reset_basic_auth_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicAuthCredentials", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetEnableAutoBuild")
    def reset_enable_auto_build(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAutoBuild", []))

    @jsii.member(jsii_name="resetEnableBasicAuth")
    def reset_enable_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBasicAuth", []))

    @jsii.member(jsii_name="resetEnableNotification")
    def reset_enable_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableNotification", []))

    @jsii.member(jsii_name="resetEnablePerformanceMode")
    def reset_enable_performance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePerformanceMode", []))

    @jsii.member(jsii_name="resetEnablePullRequestPreview")
    def reset_enable_pull_request_preview(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePullRequestPreview", []))

    @jsii.member(jsii_name="resetEnvironmentVariables")
    def reset_environment_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironmentVariables", []))

    @jsii.member(jsii_name="resetFramework")
    def reset_framework(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFramework", []))

    @jsii.member(jsii_name="resetPullRequestEnvironmentName")
    def reset_pull_request_environment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullRequestEnvironmentName", []))

    @jsii.member(jsii_name="resetStage")
    def reset_stage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStage", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="associatedResources")
    def associated_resources(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "associatedResources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDomains")
    def custom_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDomains"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationBranch")
    def destination_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationBranch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceBranch")
    def source_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceBranch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdInput")
    def app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backendEnvironmentArnInput")
    def backend_environment_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendEnvironmentArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthCredentialsInput")
    def basic_auth_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "basicAuthCredentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchNameInput")
    def branch_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBuildInput")
    def enable_auto_build_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableAutoBuildInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBasicAuthInput")
    def enable_basic_auth_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableBasicAuthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableNotificationInput")
    def enable_notification_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableNotificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePerformanceModeInput")
    def enable_performance_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enablePerformanceModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePullRequestPreviewInput")
    def enable_pull_request_preview_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enablePullRequestPreviewInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariablesInput")
    def environment_variables_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "environmentVariablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameworkInput")
    def framework_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frameworkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullRequestEnvironmentNameInput")
    def pull_request_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullRequestEnvironmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageInput")
    def stage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageInput"))

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
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        jsii.set(self, "appId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backendEnvironmentArn")
    def backend_environment_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backendEnvironmentArn"))

    @backend_environment_arn.setter
    def backend_environment_arn(self, value: builtins.str) -> None:
        jsii.set(self, "backendEnvironmentArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="basicAuthCredentials")
    def basic_auth_credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "basicAuthCredentials"))

    @basic_auth_credentials.setter
    def basic_auth_credentials(self, value: builtins.str) -> None:
        jsii.set(self, "basicAuthCredentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchName"))

    @branch_name.setter
    def branch_name(self, value: builtins.str) -> None:
        jsii.set(self, "branchName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        jsii.set(self, "displayName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAutoBuild")
    def enable_auto_build(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableAutoBuild"))

    @enable_auto_build.setter
    def enable_auto_build(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableAutoBuild", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableBasicAuth")
    def enable_basic_auth(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableBasicAuth"))

    @enable_basic_auth.setter
    def enable_basic_auth(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableBasicAuth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableNotification")
    def enable_notification(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableNotification"))

    @enable_notification.setter
    def enable_notification(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableNotification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePerformanceMode")
    def enable_performance_mode(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enablePerformanceMode"))

    @enable_performance_mode.setter
    def enable_performance_mode(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enablePerformanceMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enablePullRequestPreview")
    def enable_pull_request_preview(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enablePullRequestPreview"))

    @enable_pull_request_preview.setter
    def enable_pull_request_preview(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enablePullRequestPreview", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentVariables")
    def environment_variables(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentVariables"))

    @environment_variables.setter
    def environment_variables(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "environmentVariables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="framework")
    def framework(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "framework"))

    @framework.setter
    def framework(self, value: builtins.str) -> None:
        jsii.set(self, "framework", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullRequestEnvironmentName")
    def pull_request_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullRequestEnvironmentName"))

    @pull_request_environment_name.setter
    def pull_request_environment_name(self, value: builtins.str) -> None:
        jsii.set(self, "pullRequestEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: builtins.str) -> None:
        jsii.set(self, "stage", value)

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
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        jsii.set(self, "ttl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyBranchConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "app_id": "appId",
        "branch_name": "branchName",
        "backend_environment_arn": "backendEnvironmentArn",
        "basic_auth_credentials": "basicAuthCredentials",
        "description": "description",
        "display_name": "displayName",
        "enable_auto_build": "enableAutoBuild",
        "enable_basic_auth": "enableBasicAuth",
        "enable_notification": "enableNotification",
        "enable_performance_mode": "enablePerformanceMode",
        "enable_pull_request_preview": "enablePullRequestPreview",
        "environment_variables": "environmentVariables",
        "framework": "framework",
        "pull_request_environment_name": "pullRequestEnvironmentName",
        "stage": "stage",
        "tags": "tags",
        "tags_all": "tagsAll",
        "ttl": "ttl",
    },
)
class AmplifyBranchConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        app_id: builtins.str,
        branch_name: builtins.str,
        backend_environment_arn: typing.Optional[builtins.str] = None,
        basic_auth_credentials: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        enable_auto_build: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_basic_auth: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_notification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_performance_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_pull_request_preview: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment_variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        framework: typing.Optional[builtins.str] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        stage: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Amplify.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#app_id AmplifyBranch#app_id}.
        :param branch_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#branch_name AmplifyBranch#branch_name}.
        :param backend_environment_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#backend_environment_arn AmplifyBranch#backend_environment_arn}.
        :param basic_auth_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#basic_auth_credentials AmplifyBranch#basic_auth_credentials}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#description AmplifyBranch#description}.
        :param display_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#display_name AmplifyBranch#display_name}.
        :param enable_auto_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_auto_build AmplifyBranch#enable_auto_build}.
        :param enable_basic_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_basic_auth AmplifyBranch#enable_basic_auth}.
        :param enable_notification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_notification AmplifyBranch#enable_notification}.
        :param enable_performance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_performance_mode AmplifyBranch#enable_performance_mode}.
        :param enable_pull_request_preview: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_pull_request_preview AmplifyBranch#enable_pull_request_preview}.
        :param environment_variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#environment_variables AmplifyBranch#environment_variables}.
        :param framework: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#framework AmplifyBranch#framework}.
        :param pull_request_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#pull_request_environment_name AmplifyBranch#pull_request_environment_name}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#stage AmplifyBranch#stage}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#tags AmplifyBranch#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#tags_all AmplifyBranch#tags_all}.
        :param ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#ttl AmplifyBranch#ttl}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "branch_name": branch_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if backend_environment_arn is not None:
            self._values["backend_environment_arn"] = backend_environment_arn
        if basic_auth_credentials is not None:
            self._values["basic_auth_credentials"] = basic_auth_credentials
        if description is not None:
            self._values["description"] = description
        if display_name is not None:
            self._values["display_name"] = display_name
        if enable_auto_build is not None:
            self._values["enable_auto_build"] = enable_auto_build
        if enable_basic_auth is not None:
            self._values["enable_basic_auth"] = enable_basic_auth
        if enable_notification is not None:
            self._values["enable_notification"] = enable_notification
        if enable_performance_mode is not None:
            self._values["enable_performance_mode"] = enable_performance_mode
        if enable_pull_request_preview is not None:
            self._values["enable_pull_request_preview"] = enable_pull_request_preview
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if framework is not None:
            self._values["framework"] = framework
        if pull_request_environment_name is not None:
            self._values["pull_request_environment_name"] = pull_request_environment_name
        if stage is not None:
            self._values["stage"] = stage
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if ttl is not None:
            self._values["ttl"] = ttl

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
    def app_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#app_id AmplifyBranch#app_id}.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#branch_name AmplifyBranch#branch_name}.'''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend_environment_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#backend_environment_arn AmplifyBranch#backend_environment_arn}.'''
        result = self._values.get("backend_environment_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def basic_auth_credentials(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#basic_auth_credentials AmplifyBranch#basic_auth_credentials}.'''
        result = self._values.get("basic_auth_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#description AmplifyBranch#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#display_name AmplifyBranch#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_build(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_auto_build AmplifyBranch#enable_auto_build}.'''
        result = self._values.get("enable_auto_build")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_basic_auth(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_basic_auth AmplifyBranch#enable_basic_auth}.'''
        result = self._values.get("enable_basic_auth")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_notification(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_notification AmplifyBranch#enable_notification}.'''
        result = self._values.get("enable_notification")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_performance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_performance_mode AmplifyBranch#enable_performance_mode}.'''
        result = self._values.get("enable_performance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_pull_request_preview(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#enable_pull_request_preview AmplifyBranch#enable_pull_request_preview}.'''
        result = self._values.get("enable_pull_request_preview")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#environment_variables AmplifyBranch#environment_variables}.'''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def framework(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#framework AmplifyBranch#framework}.'''
        result = self._values.get("framework")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#pull_request_environment_name AmplifyBranch#pull_request_environment_name}.'''
        result = self._values.get("pull_request_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#stage AmplifyBranch#stage}.'''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#tags AmplifyBranch#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#tags_all AmplifyBranch#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_branch#ttl AmplifyBranch#ttl}.'''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyBranchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AmplifyDomainAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyDomainAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association aws_amplify_domain_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        domain_name: builtins.str,
        sub_domain: typing.Sequence["AmplifyDomainAssociationSubDomain"],
        wait_for_verification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association aws_amplify_domain_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#app_id AmplifyDomainAssociation#app_id}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#domain_name AmplifyDomainAssociation#domain_name}.
        :param sub_domain: sub_domain block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#sub_domain AmplifyDomainAssociation#sub_domain}
        :param wait_for_verification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#wait_for_verification AmplifyDomainAssociation#wait_for_verification}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AmplifyDomainAssociationConfig(
            app_id=app_id,
            domain_name=domain_name,
            sub_domain=sub_domain,
            wait_for_verification=wait_for_verification,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetWaitForVerification")
    def reset_wait_for_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForVerification", []))

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
    @jsii.member(jsii_name="certificateVerificationDnsRecord")
    def certificate_verification_dns_record(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateVerificationDnsRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdInput")
    def app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subDomainInput")
    def sub_domain_input(
        self,
    ) -> typing.Optional[typing.List["AmplifyDomainAssociationSubDomain"]]:
        return typing.cast(typing.Optional[typing.List["AmplifyDomainAssociationSubDomain"]], jsii.get(self, "subDomainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitForVerificationInput")
    def wait_for_verification_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "waitForVerificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        jsii.set(self, "appId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subDomain")
    def sub_domain(self) -> typing.List["AmplifyDomainAssociationSubDomain"]:
        return typing.cast(typing.List["AmplifyDomainAssociationSubDomain"], jsii.get(self, "subDomain"))

    @sub_domain.setter
    def sub_domain(
        self,
        value: typing.List["AmplifyDomainAssociationSubDomain"],
    ) -> None:
        jsii.set(self, "subDomain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitForVerification")
    def wait_for_verification(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "waitForVerification"))

    @wait_for_verification.setter
    def wait_for_verification(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "waitForVerification", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyDomainAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "app_id": "appId",
        "domain_name": "domainName",
        "sub_domain": "subDomain",
        "wait_for_verification": "waitForVerification",
    },
)
class AmplifyDomainAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        app_id: builtins.str,
        domain_name: builtins.str,
        sub_domain: typing.Sequence["AmplifyDomainAssociationSubDomain"],
        wait_for_verification: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Amplify.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#app_id AmplifyDomainAssociation#app_id}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#domain_name AmplifyDomainAssociation#domain_name}.
        :param sub_domain: sub_domain block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#sub_domain AmplifyDomainAssociation#sub_domain}
        :param wait_for_verification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#wait_for_verification AmplifyDomainAssociation#wait_for_verification}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "domain_name": domain_name,
            "sub_domain": sub_domain,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if wait_for_verification is not None:
            self._values["wait_for_verification"] = wait_for_verification

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
    def app_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#app_id AmplifyDomainAssociation#app_id}.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#domain_name AmplifyDomainAssociation#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sub_domain(self) -> typing.List["AmplifyDomainAssociationSubDomain"]:
        '''sub_domain block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#sub_domain AmplifyDomainAssociation#sub_domain}
        '''
        result = self._values.get("sub_domain")
        assert result is not None, "Required property 'sub_domain' is missing"
        return typing.cast(typing.List["AmplifyDomainAssociationSubDomain"], result)

    @builtins.property
    def wait_for_verification(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#wait_for_verification AmplifyDomainAssociation#wait_for_verification}.'''
        result = self._values.get("wait_for_verification")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyDomainAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyDomainAssociationSubDomain",
    jsii_struct_bases=[],
    name_mapping={"branch_name": "branchName", "prefix": "prefix"},
)
class AmplifyDomainAssociationSubDomain:
    def __init__(self, *, branch_name: builtins.str, prefix: builtins.str) -> None:
        '''
        :param branch_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#branch_name AmplifyDomainAssociation#branch_name}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#prefix AmplifyDomainAssociation#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "branch_name": branch_name,
            "prefix": prefix,
        }

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#branch_name AmplifyDomainAssociation#branch_name}.'''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_domain_association#prefix AmplifyDomainAssociation#prefix}.'''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyDomainAssociationSubDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AmplifyWebhook(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.amplify.AmplifyWebhook",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook aws_amplify_webhook}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        branch_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook aws_amplify_webhook} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#app_id AmplifyWebhook#app_id}.
        :param branch_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#branch_name AmplifyWebhook#branch_name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#description AmplifyWebhook#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AmplifyWebhookConfig(
            app_id=app_id,
            branch_name=branch_name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdInput")
    def app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchNameInput")
    def branch_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        jsii.set(self, "appId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchName"))

    @branch_name.setter
    def branch_name(self, value: builtins.str) -> None:
        jsii.set(self, "branchName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.amplify.AmplifyWebhookConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "app_id": "appId",
        "branch_name": "branchName",
        "description": "description",
    },
)
class AmplifyWebhookConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        app_id: builtins.str,
        branch_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Amplify.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param app_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#app_id AmplifyWebhook#app_id}.
        :param branch_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#branch_name AmplifyWebhook#branch_name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#description AmplifyWebhook#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "branch_name": branch_name,
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
    def app_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#app_id AmplifyWebhook#app_id}.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#branch_name AmplifyWebhook#branch_name}.'''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/amplify_webhook#description AmplifyWebhook#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmplifyWebhookConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AmplifyApp",
    "AmplifyAppAutoBranchCreationConfig",
    "AmplifyAppAutoBranchCreationConfigOutputReference",
    "AmplifyAppConfig",
    "AmplifyAppCustomRule",
    "AmplifyAppProductionBranch",
    "AmplifyBackendEnvironment",
    "AmplifyBackendEnvironmentConfig",
    "AmplifyBranch",
    "AmplifyBranchConfig",
    "AmplifyDomainAssociation",
    "AmplifyDomainAssociationConfig",
    "AmplifyDomainAssociationSubDomain",
    "AmplifyWebhook",
    "AmplifyWebhookConfig",
]

publication.publish()
