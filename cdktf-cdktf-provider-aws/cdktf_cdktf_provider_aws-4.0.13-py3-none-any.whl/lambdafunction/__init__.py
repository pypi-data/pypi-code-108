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


class DataAwsLambdaAlias(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias aws_lambda_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias aws_lambda_alias} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias#function_name DataAwsLambdaAlias#function_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias#name DataAwsLambdaAlias#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLambdaAliasConfig(
            function_name=function_name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invokeArn")
    def invoke_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invokeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "name": "name",
    },
)
class DataAwsLambdaAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        name: builtins.str,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias#function_name DataAwsLambdaAlias#function_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias#name DataAwsLambdaAlias#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias#function_name DataAwsLambdaAlias#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_alias#name DataAwsLambdaAlias#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLambdaAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLambdaCodeSigningConfig(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaCodeSigningConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lambda_code_signing_config aws_lambda_code_signing_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lambda_code_signing_config aws_lambda_code_signing_config} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_code_signing_config#arn DataAwsLambdaCodeSigningConfig#arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLambdaCodeSigningConfigConfig(
            arn=arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="allowedPublishers")
    def allowed_publishers(
        self,
        index: builtins.str,
    ) -> "DataAwsLambdaCodeSigningConfigAllowedPublishers":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaCodeSigningConfigAllowedPublishers", jsii.invoke(self, "allowedPublishers", [index]))

    @jsii.member(jsii_name="policies")
    def policies(self, index: builtins.str) -> "DataAwsLambdaCodeSigningConfigPolicies":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaCodeSigningConfigPolicies", jsii.invoke(self, "policies", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configId")
    def config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)


class DataAwsLambdaCodeSigningConfigAllowedPublishers(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaCodeSigningConfigAllowedPublishers",
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
    @jsii.member(jsii_name="signingProfileVersionArns")
    def signing_profile_version_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "signingProfileVersionArns"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaCodeSigningConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
    },
)
class DataAwsLambdaCodeSigningConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_code_signing_config#arn DataAwsLambdaCodeSigningConfig#arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_code_signing_config#arn DataAwsLambdaCodeSigningConfig#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLambdaCodeSigningConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLambdaCodeSigningConfigPolicies(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaCodeSigningConfigPolicies",
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
    @jsii.member(jsii_name="untrustedArtifactOnDeployment")
    def untrusted_artifact_on_deployment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "untrustedArtifactOnDeployment"))


class DataAwsLambdaFunction(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lambda_function aws_lambda_function}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        qualifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lambda_function aws_lambda_function} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#function_name DataAwsLambdaFunction#function_name}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#qualifier DataAwsLambdaFunction#qualifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#tags DataAwsLambdaFunction#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLambdaFunctionConfig(
            function_name=function_name,
            qualifier=qualifier,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="deadLetterConfig")
    def dead_letter_config(
        self,
        index: builtins.str,
    ) -> "DataAwsLambdaFunctionDeadLetterConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaFunctionDeadLetterConfig", jsii.invoke(self, "deadLetterConfig", [index]))

    @jsii.member(jsii_name="environment")
    def environment(self, index: builtins.str) -> "DataAwsLambdaFunctionEnvironment":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaFunctionEnvironment", jsii.invoke(self, "environment", [index]))

    @jsii.member(jsii_name="fileSystemConfig")
    def file_system_config(
        self,
        index: builtins.str,
    ) -> "DataAwsLambdaFunctionFileSystemConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaFunctionFileSystemConfig", jsii.invoke(self, "fileSystemConfig", [index]))

    @jsii.member(jsii_name="resetQualifier")
    def reset_qualifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQualifier", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="tracingConfig")
    def tracing_config(
        self,
        index: builtins.str,
    ) -> "DataAwsLambdaFunctionTracingConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaFunctionTracingConfig", jsii.invoke(self, "tracingConfig", [index]))

    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self, index: builtins.str) -> "DataAwsLambdaFunctionVpcConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsLambdaFunctionVpcConfig", jsii.invoke(self, "vpcConfig", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="architectures")
    def architectures(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "architectures"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeSigningConfigArn")
    def code_signing_config_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "codeSigningConfigArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageUri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invokeArn")
    def invoke_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invokeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layers")
    def layers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "layers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySize")
    def memory_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memorySize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifiedArn")
    def qualified_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifiedArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reservedConcurrentExecutions")
    def reserved_concurrent_executions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "reservedConcurrentExecutions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingJobArn")
    def signing_job_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingJobArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingProfileVersionArn")
    def signing_profile_version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingProfileVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeHash")
    def source_code_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodeHash"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeSize")
    def source_code_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sourceCodeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifierInput")
    def qualifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "qualifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifier")
    def qualifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifier"))

    @qualifier.setter
    def qualifier(self, value: builtins.str) -> None:
        jsii.set(self, "qualifier", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunctionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "qualifier": "qualifier",
        "tags": "tags",
    },
)
class DataAwsLambdaFunctionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        qualifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#function_name DataAwsLambdaFunction#function_name}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#qualifier DataAwsLambdaFunction#qualifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#tags DataAwsLambdaFunction#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if qualifier is not None:
            self._values["qualifier"] = qualifier
        if tags is not None:
            self._values["tags"] = tags

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#function_name DataAwsLambdaFunction#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def qualifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#qualifier DataAwsLambdaFunction#qualifier}.'''
        result = self._values.get("qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_function#tags DataAwsLambdaFunction#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLambdaFunctionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLambdaFunctionDeadLetterConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunctionDeadLetterConfig",
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
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))


class DataAwsLambdaFunctionEnvironment(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunctionEnvironment",
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
    @jsii.member(jsii_name="variables")
    def variables(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "variables"))


class DataAwsLambdaFunctionFileSystemConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunctionFileSystemConfig",
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localMountPath")
    def local_mount_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localMountPath"))


class DataAwsLambdaFunctionTracingConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunctionTracingConfig",
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
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))


class DataAwsLambdaFunctionVpcConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaFunctionVpcConfig",
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
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))


class DataAwsLambdaInvocation(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaInvocation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation aws_lambda_invocation}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        input: builtins.str,
        qualifier: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation aws_lambda_invocation} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#function_name DataAwsLambdaInvocation#function_name}.
        :param input: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#input DataAwsLambdaInvocation#input}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#qualifier DataAwsLambdaInvocation#qualifier}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLambdaInvocationConfig(
            function_name=function_name,
            input=input,
            qualifier=qualifier,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetQualifier")
    def reset_qualifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQualifier", []))

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
    @jsii.member(jsii_name="result")
    def result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "result"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputInput")
    def input_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifierInput")
    def qualifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "qualifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="input")
    def input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "input"))

    @input.setter
    def input(self, value: builtins.str) -> None:
        jsii.set(self, "input", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifier")
    def qualifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifier"))

    @qualifier.setter
    def qualifier(self, value: builtins.str) -> None:
        jsii.set(self, "qualifier", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaInvocationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "input": "input",
        "qualifier": "qualifier",
    },
)
class DataAwsLambdaInvocationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        input: builtins.str,
        qualifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#function_name DataAwsLambdaInvocation#function_name}.
        :param input: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#input DataAwsLambdaInvocation#input}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#qualifier DataAwsLambdaInvocation#qualifier}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
            "input": input,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if qualifier is not None:
            self._values["qualifier"] = qualifier

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#function_name DataAwsLambdaInvocation#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def input(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#input DataAwsLambdaInvocation#input}.'''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def qualifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_invocation#qualifier DataAwsLambdaInvocation#qualifier}.'''
        result = self._values.get("qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLambdaInvocationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsLambdaLayerVersion(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaLayerVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version aws_lambda_layer_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        layer_name: builtins.str,
        compatible_architecture: typing.Optional[builtins.str] = None,
        compatible_runtime: typing.Optional[builtins.str] = None,
        version: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version aws_lambda_layer_version} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param layer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#layer_name DataAwsLambdaLayerVersion#layer_name}.
        :param compatible_architecture: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#compatible_architecture DataAwsLambdaLayerVersion#compatible_architecture}.
        :param compatible_runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#compatible_runtime DataAwsLambdaLayerVersion#compatible_runtime}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#version DataAwsLambdaLayerVersion#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsLambdaLayerVersionConfig(
            layer_name=layer_name,
            compatible_architecture=compatible_architecture,
            compatible_runtime=compatible_runtime,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCompatibleArchitecture")
    def reset_compatible_architecture(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibleArchitecture", []))

    @jsii.member(jsii_name="resetCompatibleRuntime")
    def reset_compatible_runtime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibleRuntime", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

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
    @jsii.member(jsii_name="compatibleArchitectures")
    def compatible_architectures(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibleArchitectures"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibleRuntimes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerArn")
    def layer_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "layerArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseInfo")
    def license_info(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingJobArn")
    def signing_job_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingJobArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingProfileVersionArn")
    def signing_profile_version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingProfileVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeHash")
    def source_code_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodeHash"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeSize")
    def source_code_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sourceCodeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleArchitectureInput")
    def compatible_architecture_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compatibleArchitectureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleRuntimeInput")
    def compatible_runtime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compatibleRuntimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerNameInput")
    def layer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "layerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleArchitecture")
    def compatible_architecture(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibleArchitecture"))

    @compatible_architecture.setter
    def compatible_architecture(self, value: builtins.str) -> None:
        jsii.set(self, "compatibleArchitecture", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleRuntime")
    def compatible_runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compatibleRuntime"))

    @compatible_runtime.setter
    def compatible_runtime(self, value: builtins.str) -> None:
        jsii.set(self, "compatibleRuntime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerName")
    def layer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "layerName"))

    @layer_name.setter
    def layer_name(self, value: builtins.str) -> None:
        jsii.set(self, "layerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @version.setter
    def version(self, value: jsii.Number) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.DataAwsLambdaLayerVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "layer_name": "layerName",
        "compatible_architecture": "compatibleArchitecture",
        "compatible_runtime": "compatibleRuntime",
        "version": "version",
    },
)
class DataAwsLambdaLayerVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        layer_name: builtins.str,
        compatible_architecture: typing.Optional[builtins.str] = None,
        compatible_runtime: typing.Optional[builtins.str] = None,
        version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param layer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#layer_name DataAwsLambdaLayerVersion#layer_name}.
        :param compatible_architecture: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#compatible_architecture DataAwsLambdaLayerVersion#compatible_architecture}.
        :param compatible_runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#compatible_runtime DataAwsLambdaLayerVersion#compatible_runtime}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#version DataAwsLambdaLayerVersion#version}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "layer_name": layer_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if compatible_architecture is not None:
            self._values["compatible_architecture"] = compatible_architecture
        if compatible_runtime is not None:
            self._values["compatible_runtime"] = compatible_runtime
        if version is not None:
            self._values["version"] = version

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
    def layer_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#layer_name DataAwsLambdaLayerVersion#layer_name}.'''
        result = self._values.get("layer_name")
        assert result is not None, "Required property 'layer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compatible_architecture(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#compatible_architecture DataAwsLambdaLayerVersion#compatible_architecture}.'''
        result = self._values.get("compatible_architecture")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compatible_runtime(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#compatible_runtime DataAwsLambdaLayerVersion#compatible_runtime}.'''
        result = self._values.get("compatible_runtime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/lambda_layer_version#version DataAwsLambdaLayerVersion#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsLambdaLayerVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaAlias(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias aws_lambda_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        function_version: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        routing_config: typing.Optional["LambdaAliasRoutingConfig"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias aws_lambda_alias} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#function_name LambdaAlias#function_name}.
        :param function_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#function_version LambdaAlias#function_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#name LambdaAlias#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#description LambdaAlias#description}.
        :param routing_config: routing_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#routing_config LambdaAlias#routing_config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaAliasConfig(
            function_name=function_name,
            function_version=function_version,
            name=name,
            description=description,
            routing_config=routing_config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putRoutingConfig")
    def put_routing_config(
        self,
        *,
        additional_version_weights: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]] = None,
    ) -> None:
        '''
        :param additional_version_weights: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#additional_version_weights LambdaAlias#additional_version_weights}.
        '''
        value = LambdaAliasRoutingConfig(
            additional_version_weights=additional_version_weights
        )

        return typing.cast(None, jsii.invoke(self, "putRoutingConfig", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetRoutingConfig")
    def reset_routing_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutingConfig", []))

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
    @jsii.member(jsii_name="invokeArn")
    def invoke_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invokeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingConfig")
    def routing_config(self) -> "LambdaAliasRoutingConfigOutputReference":
        return typing.cast("LambdaAliasRoutingConfigOutputReference", jsii.get(self, "routingConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersionInput")
    def function_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingConfigInput")
    def routing_config_input(self) -> typing.Optional["LambdaAliasRoutingConfig"]:
        return typing.cast(typing.Optional["LambdaAliasRoutingConfig"], jsii.get(self, "routingConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionVersion"))

    @function_version.setter
    def function_version(self, value: builtins.str) -> None:
        jsii.set(self, "functionVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "function_version": "functionVersion",
        "name": "name",
        "description": "description",
        "routing_config": "routingConfig",
    },
)
class LambdaAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        function_version: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        routing_config: typing.Optional["LambdaAliasRoutingConfig"] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#function_name LambdaAlias#function_name}.
        :param function_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#function_version LambdaAlias#function_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#name LambdaAlias#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#description LambdaAlias#description}.
        :param routing_config: routing_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#routing_config LambdaAlias#routing_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(routing_config, dict):
            routing_config = LambdaAliasRoutingConfig(**routing_config)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
            "function_version": function_version,
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
        if routing_config is not None:
            self._values["routing_config"] = routing_config

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#function_name LambdaAlias#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#function_version LambdaAlias#function_version}.'''
        result = self._values.get("function_version")
        assert result is not None, "Required property 'function_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#name LambdaAlias#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#description LambdaAlias#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def routing_config(self) -> typing.Optional["LambdaAliasRoutingConfig"]:
        '''routing_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#routing_config LambdaAlias#routing_config}
        '''
        result = self._values.get("routing_config")
        return typing.cast(typing.Optional["LambdaAliasRoutingConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaAliasRoutingConfig",
    jsii_struct_bases=[],
    name_mapping={"additional_version_weights": "additionalVersionWeights"},
)
class LambdaAliasRoutingConfig:
    def __init__(
        self,
        *,
        additional_version_weights: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]] = None,
    ) -> None:
        '''
        :param additional_version_weights: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#additional_version_weights LambdaAlias#additional_version_weights}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_version_weights is not None:
            self._values["additional_version_weights"] = additional_version_weights

    @builtins.property
    def additional_version_weights(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_alias#additional_version_weights LambdaAlias#additional_version_weights}.'''
        result = self._values.get("additional_version_weights")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaAliasRoutingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaAliasRoutingConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaAliasRoutingConfigOutputReference",
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

    @jsii.member(jsii_name="resetAdditionalVersionWeights")
    def reset_additional_version_weights(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalVersionWeights", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalVersionWeightsInput")
    def additional_version_weights_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]], jsii.get(self, "additionalVersionWeightsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalVersionWeights")
    def additional_version_weights(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]], jsii.get(self, "additionalVersionWeights"))

    @additional_version_weights.setter
    def additional_version_weights(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, jsii.Number]],
    ) -> None:
        jsii.set(self, "additionalVersionWeights", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaAliasRoutingConfig]:
        return typing.cast(typing.Optional[LambdaAliasRoutingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LambdaAliasRoutingConfig]) -> None:
        jsii.set(self, "internalValue", value)


class LambdaCodeSigningConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaCodeSigningConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config aws_lambda_code_signing_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allowed_publishers: "LambdaCodeSigningConfigAllowedPublishers",
        description: typing.Optional[builtins.str] = None,
        policies: typing.Optional["LambdaCodeSigningConfigPolicies"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config aws_lambda_code_signing_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_publishers: allowed_publishers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#allowed_publishers LambdaCodeSigningConfig#allowed_publishers}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#description LambdaCodeSigningConfig#description}.
        :param policies: policies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#policies LambdaCodeSigningConfig#policies}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaCodeSigningConfigConfig(
            allowed_publishers=allowed_publishers,
            description=description,
            policies=policies,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAllowedPublishers")
    def put_allowed_publishers(
        self,
        *,
        signing_profile_version_arns: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param signing_profile_version_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#signing_profile_version_arns LambdaCodeSigningConfig#signing_profile_version_arns}.
        '''
        value = LambdaCodeSigningConfigAllowedPublishers(
            signing_profile_version_arns=signing_profile_version_arns
        )

        return typing.cast(None, jsii.invoke(self, "putAllowedPublishers", [value]))

    @jsii.member(jsii_name="putPolicies")
    def put_policies(self, *, untrusted_artifact_on_deployment: builtins.str) -> None:
        '''
        :param untrusted_artifact_on_deployment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#untrusted_artifact_on_deployment LambdaCodeSigningConfig#untrusted_artifact_on_deployment}.
        '''
        value = LambdaCodeSigningConfigPolicies(
            untrusted_artifact_on_deployment=untrusted_artifact_on_deployment
        )

        return typing.cast(None, jsii.invoke(self, "putPolicies", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetPolicies")
    def reset_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicies", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedPublishers")
    def allowed_publishers(
        self,
    ) -> "LambdaCodeSigningConfigAllowedPublishersOutputReference":
        return typing.cast("LambdaCodeSigningConfigAllowedPublishersOutputReference", jsii.get(self, "allowedPublishers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configId")
    def config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policies")
    def policies(self) -> "LambdaCodeSigningConfigPoliciesOutputReference":
        return typing.cast("LambdaCodeSigningConfigPoliciesOutputReference", jsii.get(self, "policies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedPublishersInput")
    def allowed_publishers_input(
        self,
    ) -> typing.Optional["LambdaCodeSigningConfigAllowedPublishers"]:
        return typing.cast(typing.Optional["LambdaCodeSigningConfigAllowedPublishers"], jsii.get(self, "allowedPublishersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policiesInput")
    def policies_input(self) -> typing.Optional["LambdaCodeSigningConfigPolicies"]:
        return typing.cast(typing.Optional["LambdaCodeSigningConfigPolicies"], jsii.get(self, "policiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaCodeSigningConfigAllowedPublishers",
    jsii_struct_bases=[],
    name_mapping={"signing_profile_version_arns": "signingProfileVersionArns"},
)
class LambdaCodeSigningConfigAllowedPublishers:
    def __init__(
        self,
        *,
        signing_profile_version_arns: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param signing_profile_version_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#signing_profile_version_arns LambdaCodeSigningConfig#signing_profile_version_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "signing_profile_version_arns": signing_profile_version_arns,
        }

    @builtins.property
    def signing_profile_version_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#signing_profile_version_arns LambdaCodeSigningConfig#signing_profile_version_arns}.'''
        result = self._values.get("signing_profile_version_arns")
        assert result is not None, "Required property 'signing_profile_version_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaCodeSigningConfigAllowedPublishers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaCodeSigningConfigAllowedPublishersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaCodeSigningConfigAllowedPublishersOutputReference",
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
    @jsii.member(jsii_name="signingProfileVersionArnsInput")
    def signing_profile_version_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "signingProfileVersionArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingProfileVersionArns")
    def signing_profile_version_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "signingProfileVersionArns"))

    @signing_profile_version_arns.setter
    def signing_profile_version_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "signingProfileVersionArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaCodeSigningConfigAllowedPublishers]:
        return typing.cast(typing.Optional[LambdaCodeSigningConfigAllowedPublishers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaCodeSigningConfigAllowedPublishers],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaCodeSigningConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allowed_publishers": "allowedPublishers",
        "description": "description",
        "policies": "policies",
    },
)
class LambdaCodeSigningConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allowed_publishers: LambdaCodeSigningConfigAllowedPublishers,
        description: typing.Optional[builtins.str] = None,
        policies: typing.Optional["LambdaCodeSigningConfigPolicies"] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allowed_publishers: allowed_publishers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#allowed_publishers LambdaCodeSigningConfig#allowed_publishers}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#description LambdaCodeSigningConfig#description}.
        :param policies: policies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#policies LambdaCodeSigningConfig#policies}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(allowed_publishers, dict):
            allowed_publishers = LambdaCodeSigningConfigAllowedPublishers(**allowed_publishers)
        if isinstance(policies, dict):
            policies = LambdaCodeSigningConfigPolicies(**policies)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_publishers": allowed_publishers,
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
        if policies is not None:
            self._values["policies"] = policies

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
    def allowed_publishers(self) -> LambdaCodeSigningConfigAllowedPublishers:
        '''allowed_publishers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#allowed_publishers LambdaCodeSigningConfig#allowed_publishers}
        '''
        result = self._values.get("allowed_publishers")
        assert result is not None, "Required property 'allowed_publishers' is missing"
        return typing.cast(LambdaCodeSigningConfigAllowedPublishers, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#description LambdaCodeSigningConfig#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policies(self) -> typing.Optional["LambdaCodeSigningConfigPolicies"]:
        '''policies block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#policies LambdaCodeSigningConfig#policies}
        '''
        result = self._values.get("policies")
        return typing.cast(typing.Optional["LambdaCodeSigningConfigPolicies"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaCodeSigningConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaCodeSigningConfigPolicies",
    jsii_struct_bases=[],
    name_mapping={"untrusted_artifact_on_deployment": "untrustedArtifactOnDeployment"},
)
class LambdaCodeSigningConfigPolicies:
    def __init__(self, *, untrusted_artifact_on_deployment: builtins.str) -> None:
        '''
        :param untrusted_artifact_on_deployment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#untrusted_artifact_on_deployment LambdaCodeSigningConfig#untrusted_artifact_on_deployment}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "untrusted_artifact_on_deployment": untrusted_artifact_on_deployment,
        }

    @builtins.property
    def untrusted_artifact_on_deployment(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_code_signing_config#untrusted_artifact_on_deployment LambdaCodeSigningConfig#untrusted_artifact_on_deployment}.'''
        result = self._values.get("untrusted_artifact_on_deployment")
        assert result is not None, "Required property 'untrusted_artifact_on_deployment' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaCodeSigningConfigPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaCodeSigningConfigPoliciesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaCodeSigningConfigPoliciesOutputReference",
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
    @jsii.member(jsii_name="untrustedArtifactOnDeploymentInput")
    def untrusted_artifact_on_deployment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "untrustedArtifactOnDeploymentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="untrustedArtifactOnDeployment")
    def untrusted_artifact_on_deployment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "untrustedArtifactOnDeployment"))

    @untrusted_artifact_on_deployment.setter
    def untrusted_artifact_on_deployment(self, value: builtins.str) -> None:
        jsii.set(self, "untrustedArtifactOnDeployment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaCodeSigningConfigPolicies]:
        return typing.cast(typing.Optional[LambdaCodeSigningConfigPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaCodeSigningConfigPolicies],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LambdaEventSourceMapping(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMapping",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping aws_lambda_event_source_mapping}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        batch_size: typing.Optional[jsii.Number] = None,
        bisect_batch_on_function_error: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        destination_config: typing.Optional["LambdaEventSourceMappingDestinationConfig"] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_source_arn: typing.Optional[builtins.str] = None,
        filter_criteria: typing.Optional["LambdaEventSourceMappingFilterCriteria"] = None,
        function_response_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        maximum_batching_window_in_seconds: typing.Optional[jsii.Number] = None,
        maximum_record_age_in_seconds: typing.Optional[jsii.Number] = None,
        maximum_retry_attempts: typing.Optional[jsii.Number] = None,
        parallelization_factor: typing.Optional[jsii.Number] = None,
        queues: typing.Optional[typing.Sequence[builtins.str]] = None,
        self_managed_event_source: typing.Optional["LambdaEventSourceMappingSelfManagedEventSource"] = None,
        source_access_configuration: typing.Optional[typing.Sequence["LambdaEventSourceMappingSourceAccessConfiguration"]] = None,
        starting_position: typing.Optional[builtins.str] = None,
        starting_position_timestamp: typing.Optional[builtins.str] = None,
        topics: typing.Optional[typing.Sequence[builtins.str]] = None,
        tumbling_window_in_seconds: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping aws_lambda_event_source_mapping} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#function_name LambdaEventSourceMapping#function_name}.
        :param batch_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#batch_size LambdaEventSourceMapping#batch_size}.
        :param bisect_batch_on_function_error: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#bisect_batch_on_function_error LambdaEventSourceMapping#bisect_batch_on_function_error}.
        :param destination_config: destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#destination_config LambdaEventSourceMapping#destination_config}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#enabled LambdaEventSourceMapping#enabled}.
        :param event_source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#event_source_arn LambdaEventSourceMapping#event_source_arn}.
        :param filter_criteria: filter_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#filter_criteria LambdaEventSourceMapping#filter_criteria}
        :param function_response_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#function_response_types LambdaEventSourceMapping#function_response_types}.
        :param maximum_batching_window_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_batching_window_in_seconds LambdaEventSourceMapping#maximum_batching_window_in_seconds}.
        :param maximum_record_age_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_record_age_in_seconds LambdaEventSourceMapping#maximum_record_age_in_seconds}.
        :param maximum_retry_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_retry_attempts LambdaEventSourceMapping#maximum_retry_attempts}.
        :param parallelization_factor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#parallelization_factor LambdaEventSourceMapping#parallelization_factor}.
        :param queues: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#queues LambdaEventSourceMapping#queues}.
        :param self_managed_event_source: self_managed_event_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#self_managed_event_source LambdaEventSourceMapping#self_managed_event_source}
        :param source_access_configuration: source_access_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#source_access_configuration LambdaEventSourceMapping#source_access_configuration}
        :param starting_position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#starting_position LambdaEventSourceMapping#starting_position}.
        :param starting_position_timestamp: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#starting_position_timestamp LambdaEventSourceMapping#starting_position_timestamp}.
        :param topics: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#topics LambdaEventSourceMapping#topics}.
        :param tumbling_window_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#tumbling_window_in_seconds LambdaEventSourceMapping#tumbling_window_in_seconds}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaEventSourceMappingConfig(
            function_name=function_name,
            batch_size=batch_size,
            bisect_batch_on_function_error=bisect_batch_on_function_error,
            destination_config=destination_config,
            enabled=enabled,
            event_source_arn=event_source_arn,
            filter_criteria=filter_criteria,
            function_response_types=function_response_types,
            maximum_batching_window_in_seconds=maximum_batching_window_in_seconds,
            maximum_record_age_in_seconds=maximum_record_age_in_seconds,
            maximum_retry_attempts=maximum_retry_attempts,
            parallelization_factor=parallelization_factor,
            queues=queues,
            self_managed_event_source=self_managed_event_source,
            source_access_configuration=source_access_configuration,
            starting_position=starting_position,
            starting_position_timestamp=starting_position_timestamp,
            topics=topics,
            tumbling_window_in_seconds=tumbling_window_in_seconds,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDestinationConfig")
    def put_destination_config(
        self,
        *,
        on_failure: typing.Optional["LambdaEventSourceMappingDestinationConfigOnFailure"] = None,
    ) -> None:
        '''
        :param on_failure: on_failure block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#on_failure LambdaEventSourceMapping#on_failure}
        '''
        value = LambdaEventSourceMappingDestinationConfig(on_failure=on_failure)

        return typing.cast(None, jsii.invoke(self, "putDestinationConfig", [value]))

    @jsii.member(jsii_name="putFilterCriteria")
    def put_filter_criteria(
        self,
        *,
        filter: typing.Optional[typing.Sequence["LambdaEventSourceMappingFilterCriteriaFilter"]] = None,
    ) -> None:
        '''
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#filter LambdaEventSourceMapping#filter}
        '''
        value = LambdaEventSourceMappingFilterCriteria(filter=filter)

        return typing.cast(None, jsii.invoke(self, "putFilterCriteria", [value]))

    @jsii.member(jsii_name="putSelfManagedEventSource")
    def put_self_managed_event_source(
        self,
        *,
        endpoints: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''
        :param endpoints: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#endpoints LambdaEventSourceMapping#endpoints}.
        '''
        value = LambdaEventSourceMappingSelfManagedEventSource(endpoints=endpoints)

        return typing.cast(None, jsii.invoke(self, "putSelfManagedEventSource", [value]))

    @jsii.member(jsii_name="resetBatchSize")
    def reset_batch_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSize", []))

    @jsii.member(jsii_name="resetBisectBatchOnFunctionError")
    def reset_bisect_batch_on_function_error(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBisectBatchOnFunctionError", []))

    @jsii.member(jsii_name="resetDestinationConfig")
    def reset_destination_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationConfig", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEventSourceArn")
    def reset_event_source_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventSourceArn", []))

    @jsii.member(jsii_name="resetFilterCriteria")
    def reset_filter_criteria(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilterCriteria", []))

    @jsii.member(jsii_name="resetFunctionResponseTypes")
    def reset_function_response_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionResponseTypes", []))

    @jsii.member(jsii_name="resetMaximumBatchingWindowInSeconds")
    def reset_maximum_batching_window_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumBatchingWindowInSeconds", []))

    @jsii.member(jsii_name="resetMaximumRecordAgeInSeconds")
    def reset_maximum_record_age_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumRecordAgeInSeconds", []))

    @jsii.member(jsii_name="resetMaximumRetryAttempts")
    def reset_maximum_retry_attempts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumRetryAttempts", []))

    @jsii.member(jsii_name="resetParallelizationFactor")
    def reset_parallelization_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParallelizationFactor", []))

    @jsii.member(jsii_name="resetQueues")
    def reset_queues(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueues", []))

    @jsii.member(jsii_name="resetSelfManagedEventSource")
    def reset_self_managed_event_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelfManagedEventSource", []))

    @jsii.member(jsii_name="resetSourceAccessConfiguration")
    def reset_source_access_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceAccessConfiguration", []))

    @jsii.member(jsii_name="resetStartingPosition")
    def reset_starting_position(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartingPosition", []))

    @jsii.member(jsii_name="resetStartingPositionTimestamp")
    def reset_starting_position_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartingPositionTimestamp", []))

    @jsii.member(jsii_name="resetTopics")
    def reset_topics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopics", []))

    @jsii.member(jsii_name="resetTumblingWindowInSeconds")
    def reset_tumbling_window_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTumblingWindowInSeconds", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationConfig")
    def destination_config(
        self,
    ) -> "LambdaEventSourceMappingDestinationConfigOutputReference":
        return typing.cast("LambdaEventSourceMappingDestinationConfigOutputReference", jsii.get(self, "destinationConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterCriteria")
    def filter_criteria(
        self,
    ) -> "LambdaEventSourceMappingFilterCriteriaOutputReference":
        return typing.cast("LambdaEventSourceMappingFilterCriteriaOutputReference", jsii.get(self, "filterCriteria"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastProcessingResult")
    def last_processing_result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastProcessingResult"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfManagedEventSource")
    def self_managed_event_source(
        self,
    ) -> "LambdaEventSourceMappingSelfManagedEventSourceOutputReference":
        return typing.cast("LambdaEventSourceMappingSelfManagedEventSourceOutputReference", jsii.get(self, "selfManagedEventSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateTransitionReason")
    def state_transition_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateTransitionReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="batchSizeInput")
    def batch_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bisectBatchOnFunctionErrorInput")
    def bisect_batch_on_function_error_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "bisectBatchOnFunctionErrorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationConfigInput")
    def destination_config_input(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingDestinationConfig"]:
        return typing.cast(typing.Optional["LambdaEventSourceMappingDestinationConfig"], jsii.get(self, "destinationConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSourceArnInput")
    def event_source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventSourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterCriteriaInput")
    def filter_criteria_input(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingFilterCriteria"]:
        return typing.cast(typing.Optional["LambdaEventSourceMappingFilterCriteria"], jsii.get(self, "filterCriteriaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionResponseTypesInput")
    def function_response_types_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "functionResponseTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumBatchingWindowInSecondsInput")
    def maximum_batching_window_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumBatchingWindowInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumRecordAgeInSecondsInput")
    def maximum_record_age_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumRecordAgeInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumRetryAttemptsInput")
    def maximum_retry_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumRetryAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parallelizationFactorInput")
    def parallelization_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "parallelizationFactorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queuesInput")
    def queues_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "queuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfManagedEventSourceInput")
    def self_managed_event_source_input(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingSelfManagedEventSource"]:
        return typing.cast(typing.Optional["LambdaEventSourceMappingSelfManagedEventSource"], jsii.get(self, "selfManagedEventSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceAccessConfigurationInput")
    def source_access_configuration_input(
        self,
    ) -> typing.Optional[typing.List["LambdaEventSourceMappingSourceAccessConfiguration"]]:
        return typing.cast(typing.Optional[typing.List["LambdaEventSourceMappingSourceAccessConfiguration"]], jsii.get(self, "sourceAccessConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startingPositionInput")
    def starting_position_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startingPositionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startingPositionTimestampInput")
    def starting_position_timestamp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startingPositionTimestampInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicsInput")
    def topics_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "topicsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tumblingWindowInSecondsInput")
    def tumbling_window_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tumblingWindowInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="batchSize")
    def batch_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSize"))

    @batch_size.setter
    def batch_size(self, value: jsii.Number) -> None:
        jsii.set(self, "batchSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bisectBatchOnFunctionError")
    def bisect_batch_on_function_error(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "bisectBatchOnFunctionError"))

    @bisect_batch_on_function_error.setter
    def bisect_batch_on_function_error(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "bisectBatchOnFunctionError", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSourceArn")
    def event_source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventSourceArn"))

    @event_source_arn.setter
    def event_source_arn(self, value: builtins.str) -> None:
        jsii.set(self, "eventSourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionResponseTypes")
    def function_response_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "functionResponseTypes"))

    @function_response_types.setter
    def function_response_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "functionResponseTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumBatchingWindowInSeconds")
    def maximum_batching_window_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumBatchingWindowInSeconds"))

    @maximum_batching_window_in_seconds.setter
    def maximum_batching_window_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "maximumBatchingWindowInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumRecordAgeInSeconds")
    def maximum_record_age_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumRecordAgeInSeconds"))

    @maximum_record_age_in_seconds.setter
    def maximum_record_age_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "maximumRecordAgeInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumRetryAttempts")
    def maximum_retry_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumRetryAttempts"))

    @maximum_retry_attempts.setter
    def maximum_retry_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maximumRetryAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parallelizationFactor")
    def parallelization_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "parallelizationFactor"))

    @parallelization_factor.setter
    def parallelization_factor(self, value: jsii.Number) -> None:
        jsii.set(self, "parallelizationFactor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queues")
    def queues(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "queues"))

    @queues.setter
    def queues(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "queues", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceAccessConfiguration")
    def source_access_configuration(
        self,
    ) -> typing.List["LambdaEventSourceMappingSourceAccessConfiguration"]:
        return typing.cast(typing.List["LambdaEventSourceMappingSourceAccessConfiguration"], jsii.get(self, "sourceAccessConfiguration"))

    @source_access_configuration.setter
    def source_access_configuration(
        self,
        value: typing.List["LambdaEventSourceMappingSourceAccessConfiguration"],
    ) -> None:
        jsii.set(self, "sourceAccessConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startingPosition")
    def starting_position(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingPosition"))

    @starting_position.setter
    def starting_position(self, value: builtins.str) -> None:
        jsii.set(self, "startingPosition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startingPositionTimestamp")
    def starting_position_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingPositionTimestamp"))

    @starting_position_timestamp.setter
    def starting_position_timestamp(self, value: builtins.str) -> None:
        jsii.set(self, "startingPositionTimestamp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topics")
    def topics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "topics"))

    @topics.setter
    def topics(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "topics", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tumblingWindowInSeconds")
    def tumbling_window_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tumblingWindowInSeconds"))

    @tumbling_window_in_seconds.setter
    def tumbling_window_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "tumblingWindowInSeconds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "batch_size": "batchSize",
        "bisect_batch_on_function_error": "bisectBatchOnFunctionError",
        "destination_config": "destinationConfig",
        "enabled": "enabled",
        "event_source_arn": "eventSourceArn",
        "filter_criteria": "filterCriteria",
        "function_response_types": "functionResponseTypes",
        "maximum_batching_window_in_seconds": "maximumBatchingWindowInSeconds",
        "maximum_record_age_in_seconds": "maximumRecordAgeInSeconds",
        "maximum_retry_attempts": "maximumRetryAttempts",
        "parallelization_factor": "parallelizationFactor",
        "queues": "queues",
        "self_managed_event_source": "selfManagedEventSource",
        "source_access_configuration": "sourceAccessConfiguration",
        "starting_position": "startingPosition",
        "starting_position_timestamp": "startingPositionTimestamp",
        "topics": "topics",
        "tumbling_window_in_seconds": "tumblingWindowInSeconds",
    },
)
class LambdaEventSourceMappingConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        batch_size: typing.Optional[jsii.Number] = None,
        bisect_batch_on_function_error: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        destination_config: typing.Optional["LambdaEventSourceMappingDestinationConfig"] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_source_arn: typing.Optional[builtins.str] = None,
        filter_criteria: typing.Optional["LambdaEventSourceMappingFilterCriteria"] = None,
        function_response_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        maximum_batching_window_in_seconds: typing.Optional[jsii.Number] = None,
        maximum_record_age_in_seconds: typing.Optional[jsii.Number] = None,
        maximum_retry_attempts: typing.Optional[jsii.Number] = None,
        parallelization_factor: typing.Optional[jsii.Number] = None,
        queues: typing.Optional[typing.Sequence[builtins.str]] = None,
        self_managed_event_source: typing.Optional["LambdaEventSourceMappingSelfManagedEventSource"] = None,
        source_access_configuration: typing.Optional[typing.Sequence["LambdaEventSourceMappingSourceAccessConfiguration"]] = None,
        starting_position: typing.Optional[builtins.str] = None,
        starting_position_timestamp: typing.Optional[builtins.str] = None,
        topics: typing.Optional[typing.Sequence[builtins.str]] = None,
        tumbling_window_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#function_name LambdaEventSourceMapping#function_name}.
        :param batch_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#batch_size LambdaEventSourceMapping#batch_size}.
        :param bisect_batch_on_function_error: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#bisect_batch_on_function_error LambdaEventSourceMapping#bisect_batch_on_function_error}.
        :param destination_config: destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#destination_config LambdaEventSourceMapping#destination_config}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#enabled LambdaEventSourceMapping#enabled}.
        :param event_source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#event_source_arn LambdaEventSourceMapping#event_source_arn}.
        :param filter_criteria: filter_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#filter_criteria LambdaEventSourceMapping#filter_criteria}
        :param function_response_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#function_response_types LambdaEventSourceMapping#function_response_types}.
        :param maximum_batching_window_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_batching_window_in_seconds LambdaEventSourceMapping#maximum_batching_window_in_seconds}.
        :param maximum_record_age_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_record_age_in_seconds LambdaEventSourceMapping#maximum_record_age_in_seconds}.
        :param maximum_retry_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_retry_attempts LambdaEventSourceMapping#maximum_retry_attempts}.
        :param parallelization_factor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#parallelization_factor LambdaEventSourceMapping#parallelization_factor}.
        :param queues: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#queues LambdaEventSourceMapping#queues}.
        :param self_managed_event_source: self_managed_event_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#self_managed_event_source LambdaEventSourceMapping#self_managed_event_source}
        :param source_access_configuration: source_access_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#source_access_configuration LambdaEventSourceMapping#source_access_configuration}
        :param starting_position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#starting_position LambdaEventSourceMapping#starting_position}.
        :param starting_position_timestamp: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#starting_position_timestamp LambdaEventSourceMapping#starting_position_timestamp}.
        :param topics: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#topics LambdaEventSourceMapping#topics}.
        :param tumbling_window_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#tumbling_window_in_seconds LambdaEventSourceMapping#tumbling_window_in_seconds}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(destination_config, dict):
            destination_config = LambdaEventSourceMappingDestinationConfig(**destination_config)
        if isinstance(filter_criteria, dict):
            filter_criteria = LambdaEventSourceMappingFilterCriteria(**filter_criteria)
        if isinstance(self_managed_event_source, dict):
            self_managed_event_source = LambdaEventSourceMappingSelfManagedEventSource(**self_managed_event_source)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if batch_size is not None:
            self._values["batch_size"] = batch_size
        if bisect_batch_on_function_error is not None:
            self._values["bisect_batch_on_function_error"] = bisect_batch_on_function_error
        if destination_config is not None:
            self._values["destination_config"] = destination_config
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_source_arn is not None:
            self._values["event_source_arn"] = event_source_arn
        if filter_criteria is not None:
            self._values["filter_criteria"] = filter_criteria
        if function_response_types is not None:
            self._values["function_response_types"] = function_response_types
        if maximum_batching_window_in_seconds is not None:
            self._values["maximum_batching_window_in_seconds"] = maximum_batching_window_in_seconds
        if maximum_record_age_in_seconds is not None:
            self._values["maximum_record_age_in_seconds"] = maximum_record_age_in_seconds
        if maximum_retry_attempts is not None:
            self._values["maximum_retry_attempts"] = maximum_retry_attempts
        if parallelization_factor is not None:
            self._values["parallelization_factor"] = parallelization_factor
        if queues is not None:
            self._values["queues"] = queues
        if self_managed_event_source is not None:
            self._values["self_managed_event_source"] = self_managed_event_source
        if source_access_configuration is not None:
            self._values["source_access_configuration"] = source_access_configuration
        if starting_position is not None:
            self._values["starting_position"] = starting_position
        if starting_position_timestamp is not None:
            self._values["starting_position_timestamp"] = starting_position_timestamp
        if topics is not None:
            self._values["topics"] = topics
        if tumbling_window_in_seconds is not None:
            self._values["tumbling_window_in_seconds"] = tumbling_window_in_seconds

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#function_name LambdaEventSourceMapping#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def batch_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#batch_size LambdaEventSourceMapping#batch_size}.'''
        result = self._values.get("batch_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bisect_batch_on_function_error(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#bisect_batch_on_function_error LambdaEventSourceMapping#bisect_batch_on_function_error}.'''
        result = self._values.get("bisect_batch_on_function_error")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def destination_config(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingDestinationConfig"]:
        '''destination_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#destination_config LambdaEventSourceMapping#destination_config}
        '''
        result = self._values.get("destination_config")
        return typing.cast(typing.Optional["LambdaEventSourceMappingDestinationConfig"], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#enabled LambdaEventSourceMapping#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def event_source_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#event_source_arn LambdaEventSourceMapping#event_source_arn}.'''
        result = self._values.get("event_source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter_criteria(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingFilterCriteria"]:
        '''filter_criteria block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#filter_criteria LambdaEventSourceMapping#filter_criteria}
        '''
        result = self._values.get("filter_criteria")
        return typing.cast(typing.Optional["LambdaEventSourceMappingFilterCriteria"], result)

    @builtins.property
    def function_response_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#function_response_types LambdaEventSourceMapping#function_response_types}.'''
        result = self._values.get("function_response_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def maximum_batching_window_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_batching_window_in_seconds LambdaEventSourceMapping#maximum_batching_window_in_seconds}.'''
        result = self._values.get("maximum_batching_window_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum_record_age_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_record_age_in_seconds LambdaEventSourceMapping#maximum_record_age_in_seconds}.'''
        result = self._values.get("maximum_record_age_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum_retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#maximum_retry_attempts LambdaEventSourceMapping#maximum_retry_attempts}.'''
        result = self._values.get("maximum_retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parallelization_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#parallelization_factor LambdaEventSourceMapping#parallelization_factor}.'''
        result = self._values.get("parallelization_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def queues(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#queues LambdaEventSourceMapping#queues}.'''
        result = self._values.get("queues")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def self_managed_event_source(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingSelfManagedEventSource"]:
        '''self_managed_event_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#self_managed_event_source LambdaEventSourceMapping#self_managed_event_source}
        '''
        result = self._values.get("self_managed_event_source")
        return typing.cast(typing.Optional["LambdaEventSourceMappingSelfManagedEventSource"], result)

    @builtins.property
    def source_access_configuration(
        self,
    ) -> typing.Optional[typing.List["LambdaEventSourceMappingSourceAccessConfiguration"]]:
        '''source_access_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#source_access_configuration LambdaEventSourceMapping#source_access_configuration}
        '''
        result = self._values.get("source_access_configuration")
        return typing.cast(typing.Optional[typing.List["LambdaEventSourceMappingSourceAccessConfiguration"]], result)

    @builtins.property
    def starting_position(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#starting_position LambdaEventSourceMapping#starting_position}.'''
        result = self._values.get("starting_position")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def starting_position_timestamp(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#starting_position_timestamp LambdaEventSourceMapping#starting_position_timestamp}.'''
        result = self._values.get("starting_position_timestamp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#topics LambdaEventSourceMapping#topics}.'''
        result = self._values.get("topics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tumbling_window_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#tumbling_window_in_seconds LambdaEventSourceMapping#tumbling_window_in_seconds}.'''
        result = self._values.get("tumbling_window_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingDestinationConfig",
    jsii_struct_bases=[],
    name_mapping={"on_failure": "onFailure"},
)
class LambdaEventSourceMappingDestinationConfig:
    def __init__(
        self,
        *,
        on_failure: typing.Optional["LambdaEventSourceMappingDestinationConfigOnFailure"] = None,
    ) -> None:
        '''
        :param on_failure: on_failure block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#on_failure LambdaEventSourceMapping#on_failure}
        '''
        if isinstance(on_failure, dict):
            on_failure = LambdaEventSourceMappingDestinationConfigOnFailure(**on_failure)
        self._values: typing.Dict[str, typing.Any] = {}
        if on_failure is not None:
            self._values["on_failure"] = on_failure

    @builtins.property
    def on_failure(
        self,
    ) -> typing.Optional["LambdaEventSourceMappingDestinationConfigOnFailure"]:
        '''on_failure block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#on_failure LambdaEventSourceMapping#on_failure}
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional["LambdaEventSourceMappingDestinationConfigOnFailure"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingDestinationConfigOnFailure",
    jsii_struct_bases=[],
    name_mapping={"destination_arn": "destinationArn"},
)
class LambdaEventSourceMappingDestinationConfigOnFailure:
    def __init__(self, *, destination_arn: builtins.str) -> None:
        '''
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#destination_arn LambdaEventSourceMapping#destination_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_arn": destination_arn,
        }

    @builtins.property
    def destination_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#destination_arn LambdaEventSourceMapping#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingDestinationConfigOnFailure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaEventSourceMappingDestinationConfigOnFailureOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingDestinationConfigOnFailureOutputReference",
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
    @jsii.member(jsii_name="destinationArnInput")
    def destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaEventSourceMappingDestinationConfigOnFailure]:
        return typing.cast(typing.Optional[LambdaEventSourceMappingDestinationConfigOnFailure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaEventSourceMappingDestinationConfigOnFailure],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LambdaEventSourceMappingDestinationConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingDestinationConfigOutputReference",
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

    @jsii.member(jsii_name="putOnFailure")
    def put_on_failure(self, *, destination_arn: builtins.str) -> None:
        '''
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#destination_arn LambdaEventSourceMapping#destination_arn}.
        '''
        value = LambdaEventSourceMappingDestinationConfigOnFailure(
            destination_arn=destination_arn
        )

        return typing.cast(None, jsii.invoke(self, "putOnFailure", [value]))

    @jsii.member(jsii_name="resetOnFailure")
    def reset_on_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnFailure", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onFailure")
    def on_failure(
        self,
    ) -> LambdaEventSourceMappingDestinationConfigOnFailureOutputReference:
        return typing.cast(LambdaEventSourceMappingDestinationConfigOnFailureOutputReference, jsii.get(self, "onFailure"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onFailureInput")
    def on_failure_input(
        self,
    ) -> typing.Optional[LambdaEventSourceMappingDestinationConfigOnFailure]:
        return typing.cast(typing.Optional[LambdaEventSourceMappingDestinationConfigOnFailure], jsii.get(self, "onFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaEventSourceMappingDestinationConfig]:
        return typing.cast(typing.Optional[LambdaEventSourceMappingDestinationConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaEventSourceMappingDestinationConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingFilterCriteria",
    jsii_struct_bases=[],
    name_mapping={"filter": "filter"},
)
class LambdaEventSourceMappingFilterCriteria:
    def __init__(
        self,
        *,
        filter: typing.Optional[typing.Sequence["LambdaEventSourceMappingFilterCriteriaFilter"]] = None,
    ) -> None:
        '''
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#filter LambdaEventSourceMapping#filter}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filter is not None:
            self._values["filter"] = filter

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional[typing.List["LambdaEventSourceMappingFilterCriteriaFilter"]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#filter LambdaEventSourceMapping#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.List["LambdaEventSourceMappingFilterCriteriaFilter"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingFilterCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingFilterCriteriaFilter",
    jsii_struct_bases=[],
    name_mapping={"pattern": "pattern"},
)
class LambdaEventSourceMappingFilterCriteriaFilter:
    def __init__(self, *, pattern: typing.Optional[builtins.str] = None) -> None:
        '''
        :param pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#pattern LambdaEventSourceMapping#pattern}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if pattern is not None:
            self._values["pattern"] = pattern

    @builtins.property
    def pattern(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#pattern LambdaEventSourceMapping#pattern}.'''
        result = self._values.get("pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingFilterCriteriaFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaEventSourceMappingFilterCriteriaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingFilterCriteriaOutputReference",
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

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.List[LambdaEventSourceMappingFilterCriteriaFilter]]:
        return typing.cast(typing.Optional[typing.List[LambdaEventSourceMappingFilterCriteriaFilter]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> typing.List[LambdaEventSourceMappingFilterCriteriaFilter]:
        return typing.cast(typing.List[LambdaEventSourceMappingFilterCriteriaFilter], jsii.get(self, "filter"))

    @filter.setter
    def filter(
        self,
        value: typing.List[LambdaEventSourceMappingFilterCriteriaFilter],
    ) -> None:
        jsii.set(self, "filter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaEventSourceMappingFilterCriteria]:
        return typing.cast(typing.Optional[LambdaEventSourceMappingFilterCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaEventSourceMappingFilterCriteria],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingSelfManagedEventSource",
    jsii_struct_bases=[],
    name_mapping={"endpoints": "endpoints"},
)
class LambdaEventSourceMappingSelfManagedEventSource:
    def __init__(
        self,
        *,
        endpoints: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''
        :param endpoints: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#endpoints LambdaEventSourceMapping#endpoints}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoints": endpoints,
        }

    @builtins.property
    def endpoints(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#endpoints LambdaEventSourceMapping#endpoints}.'''
        result = self._values.get("endpoints")
        assert result is not None, "Required property 'endpoints' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingSelfManagedEventSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaEventSourceMappingSelfManagedEventSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingSelfManagedEventSourceOutputReference",
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
    @jsii.member(jsii_name="endpointsInput")
    def endpoints_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "endpointsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoints")
    def endpoints(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "endpoints"))

    @endpoints.setter
    def endpoints(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "endpoints", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaEventSourceMappingSelfManagedEventSource]:
        return typing.cast(typing.Optional[LambdaEventSourceMappingSelfManagedEventSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaEventSourceMappingSelfManagedEventSource],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaEventSourceMappingSourceAccessConfiguration",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "uri": "uri"},
)
class LambdaEventSourceMappingSourceAccessConfiguration:
    def __init__(self, *, type: builtins.str, uri: builtins.str) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#type LambdaEventSourceMapping#type}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#uri LambdaEventSourceMapping#uri}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
            "uri": uri,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#type LambdaEventSourceMapping#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_event_source_mapping#uri LambdaEventSourceMapping#uri}.'''
        result = self._values.get("uri")
        assert result is not None, "Required property 'uri' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaEventSourceMappingSourceAccessConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunction(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_function aws_lambda_function}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        role: builtins.str,
        architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_signing_config_arn: typing.Optional[builtins.str] = None,
        dead_letter_config: typing.Optional["LambdaFunctionDeadLetterConfig"] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional["LambdaFunctionEnvironment"] = None,
        filename: typing.Optional[builtins.str] = None,
        file_system_config: typing.Optional["LambdaFunctionFileSystemConfig"] = None,
        handler: typing.Optional[builtins.str] = None,
        image_config: typing.Optional["LambdaFunctionImageConfig"] = None,
        image_uri: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        layers: typing.Optional[typing.Sequence[builtins.str]] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        package_type: typing.Optional[builtins.str] = None,
        publish: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        runtime: typing.Optional[builtins.str] = None,
        s3_bucket: typing.Optional[builtins.str] = None,
        s3_key: typing.Optional[builtins.str] = None,
        s3_object_version: typing.Optional[builtins.str] = None,
        source_code_hash: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        timeouts: typing.Optional["LambdaFunctionTimeouts"] = None,
        tracing_config: typing.Optional["LambdaFunctionTracingConfig"] = None,
        vpc_config: typing.Optional["LambdaFunctionVpcConfig"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_function aws_lambda_function} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#function_name LambdaFunction#function_name}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#role LambdaFunction#role}.
        :param architectures: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#architectures LambdaFunction#architectures}.
        :param code_signing_config_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#code_signing_config_arn LambdaFunction#code_signing_config_arn}.
        :param dead_letter_config: dead_letter_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#dead_letter_config LambdaFunction#dead_letter_config}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#description LambdaFunction#description}.
        :param environment: environment block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#environment LambdaFunction#environment}
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#filename LambdaFunction#filename}.
        :param file_system_config: file_system_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#file_system_config LambdaFunction#file_system_config}
        :param handler: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#handler LambdaFunction#handler}.
        :param image_config: image_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#image_config LambdaFunction#image_config}
        :param image_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#image_uri LambdaFunction#image_uri}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#kms_key_arn LambdaFunction#kms_key_arn}.
        :param layers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#layers LambdaFunction#layers}.
        :param memory_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#memory_size LambdaFunction#memory_size}.
        :param package_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#package_type LambdaFunction#package_type}.
        :param publish: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#publish LambdaFunction#publish}.
        :param reserved_concurrent_executions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#reserved_concurrent_executions LambdaFunction#reserved_concurrent_executions}.
        :param runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#runtime LambdaFunction#runtime}.
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_bucket LambdaFunction#s3_bucket}.
        :param s3_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_key LambdaFunction#s3_key}.
        :param s3_object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_object_version LambdaFunction#s3_object_version}.
        :param source_code_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#source_code_hash LambdaFunction#source_code_hash}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tags LambdaFunction#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tags_all LambdaFunction#tags_all}.
        :param timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#timeout LambdaFunction#timeout}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#timeouts LambdaFunction#timeouts}
        :param tracing_config: tracing_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tracing_config LambdaFunction#tracing_config}
        :param vpc_config: vpc_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#vpc_config LambdaFunction#vpc_config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaFunctionConfig(
            function_name=function_name,
            role=role,
            architectures=architectures,
            code_signing_config_arn=code_signing_config_arn,
            dead_letter_config=dead_letter_config,
            description=description,
            environment=environment,
            filename=filename,
            file_system_config=file_system_config,
            handler=handler,
            image_config=image_config,
            image_uri=image_uri,
            kms_key_arn=kms_key_arn,
            layers=layers,
            memory_size=memory_size,
            package_type=package_type,
            publish=publish,
            reserved_concurrent_executions=reserved_concurrent_executions,
            runtime=runtime,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            s3_object_version=s3_object_version,
            source_code_hash=source_code_hash,
            tags=tags,
            tags_all=tags_all,
            timeout=timeout,
            timeouts=timeouts,
            tracing_config=tracing_config,
            vpc_config=vpc_config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDeadLetterConfig")
    def put_dead_letter_config(self, *, target_arn: builtins.str) -> None:
        '''
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#target_arn LambdaFunction#target_arn}.
        '''
        value = LambdaFunctionDeadLetterConfig(target_arn=target_arn)

        return typing.cast(None, jsii.invoke(self, "putDeadLetterConfig", [value]))

    @jsii.member(jsii_name="putEnvironment")
    def put_environment(
        self,
        *,
        variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#variables LambdaFunction#variables}.
        '''
        value = LambdaFunctionEnvironment(variables=variables)

        return typing.cast(None, jsii.invoke(self, "putEnvironment", [value]))

    @jsii.member(jsii_name="putFileSystemConfig")
    def put_file_system_config(
        self,
        *,
        arn: builtins.str,
        local_mount_path: builtins.str,
    ) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#arn LambdaFunction#arn}.
        :param local_mount_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#local_mount_path LambdaFunction#local_mount_path}.
        '''
        value = LambdaFunctionFileSystemConfig(
            arn=arn, local_mount_path=local_mount_path
        )

        return typing.cast(None, jsii.invoke(self, "putFileSystemConfig", [value]))

    @jsii.member(jsii_name="putImageConfig")
    def put_image_config(
        self,
        *,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        entry_point: typing.Optional[typing.Sequence[builtins.str]] = None,
        working_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param command: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#command LambdaFunction#command}.
        :param entry_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#entry_point LambdaFunction#entry_point}.
        :param working_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#working_directory LambdaFunction#working_directory}.
        '''
        value = LambdaFunctionImageConfig(
            command=command,
            entry_point=entry_point,
            working_directory=working_directory,
        )

        return typing.cast(None, jsii.invoke(self, "putImageConfig", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#create LambdaFunction#create}.
        '''
        value = LambdaFunctionTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTracingConfig")
    def put_tracing_config(self, *, mode: builtins.str) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#mode LambdaFunction#mode}.
        '''
        value = LambdaFunctionTracingConfig(mode=mode)

        return typing.cast(None, jsii.invoke(self, "putTracingConfig", [value]))

    @jsii.member(jsii_name="putVpcConfig")
    def put_vpc_config(
        self,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_ids: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#security_group_ids LambdaFunction#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#subnet_ids LambdaFunction#subnet_ids}.
        '''
        value = LambdaFunctionVpcConfig(
            security_group_ids=security_group_ids, subnet_ids=subnet_ids
        )

        return typing.cast(None, jsii.invoke(self, "putVpcConfig", [value]))

    @jsii.member(jsii_name="resetArchitectures")
    def reset_architectures(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArchitectures", []))

    @jsii.member(jsii_name="resetCodeSigningConfigArn")
    def reset_code_signing_config_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCodeSigningConfigArn", []))

    @jsii.member(jsii_name="resetDeadLetterConfig")
    def reset_dead_letter_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeadLetterConfig", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetFilename")
    def reset_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilename", []))

    @jsii.member(jsii_name="resetFileSystemConfig")
    def reset_file_system_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemConfig", []))

    @jsii.member(jsii_name="resetHandler")
    def reset_handler(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHandler", []))

    @jsii.member(jsii_name="resetImageConfig")
    def reset_image_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageConfig", []))

    @jsii.member(jsii_name="resetImageUri")
    def reset_image_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageUri", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetLayers")
    def reset_layers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLayers", []))

    @jsii.member(jsii_name="resetMemorySize")
    def reset_memory_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemorySize", []))

    @jsii.member(jsii_name="resetPackageType")
    def reset_package_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPackageType", []))

    @jsii.member(jsii_name="resetPublish")
    def reset_publish(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublish", []))

    @jsii.member(jsii_name="resetReservedConcurrentExecutions")
    def reset_reserved_concurrent_executions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReservedConcurrentExecutions", []))

    @jsii.member(jsii_name="resetRuntime")
    def reset_runtime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuntime", []))

    @jsii.member(jsii_name="resetS3Bucket")
    def reset_s3_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Bucket", []))

    @jsii.member(jsii_name="resetS3Key")
    def reset_s3_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Key", []))

    @jsii.member(jsii_name="resetS3ObjectVersion")
    def reset_s3_object_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3ObjectVersion", []))

    @jsii.member(jsii_name="resetSourceCodeHash")
    def reset_source_code_hash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCodeHash", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTracingConfig")
    def reset_tracing_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTracingConfig", []))

    @jsii.member(jsii_name="resetVpcConfig")
    def reset_vpc_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcConfig", []))

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
    @jsii.member(jsii_name="deadLetterConfig")
    def dead_letter_config(self) -> "LambdaFunctionDeadLetterConfigOutputReference":
        return typing.cast("LambdaFunctionDeadLetterConfigOutputReference", jsii.get(self, "deadLetterConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environment")
    def environment(self) -> "LambdaFunctionEnvironmentOutputReference":
        return typing.cast("LambdaFunctionEnvironmentOutputReference", jsii.get(self, "environment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemConfig")
    def file_system_config(self) -> "LambdaFunctionFileSystemConfigOutputReference":
        return typing.cast("LambdaFunctionFileSystemConfigOutputReference", jsii.get(self, "fileSystemConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageConfig")
    def image_config(self) -> "LambdaFunctionImageConfigOutputReference":
        return typing.cast("LambdaFunctionImageConfigOutputReference", jsii.get(self, "imageConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invokeArn")
    def invoke_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invokeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifiedArn")
    def qualified_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifiedArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingJobArn")
    def signing_job_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingJobArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingProfileVersionArn")
    def signing_profile_version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingProfileVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeSize")
    def source_code_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sourceCodeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LambdaFunctionTimeoutsOutputReference":
        return typing.cast("LambdaFunctionTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tracingConfig")
    def tracing_config(self) -> "LambdaFunctionTracingConfigOutputReference":
        return typing.cast("LambdaFunctionTracingConfigOutputReference", jsii.get(self, "tracingConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> "LambdaFunctionVpcConfigOutputReference":
        return typing.cast("LambdaFunctionVpcConfigOutputReference", jsii.get(self, "vpcConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="architecturesInput")
    def architectures_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "architecturesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeSigningConfigArnInput")
    def code_signing_config_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "codeSigningConfigArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadLetterConfigInput")
    def dead_letter_config_input(
        self,
    ) -> typing.Optional["LambdaFunctionDeadLetterConfig"]:
        return typing.cast(typing.Optional["LambdaFunctionDeadLetterConfig"], jsii.get(self, "deadLetterConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional["LambdaFunctionEnvironment"]:
        return typing.cast(typing.Optional["LambdaFunctionEnvironment"], jsii.get(self, "environmentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filenameInput")
    def filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemConfigInput")
    def file_system_config_input(
        self,
    ) -> typing.Optional["LambdaFunctionFileSystemConfig"]:
        return typing.cast(typing.Optional["LambdaFunctionFileSystemConfig"], jsii.get(self, "fileSystemConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handlerInput")
    def handler_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "handlerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageConfigInput")
    def image_config_input(self) -> typing.Optional["LambdaFunctionImageConfig"]:
        return typing.cast(typing.Optional["LambdaFunctionImageConfig"], jsii.get(self, "imageConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUriInput")
    def image_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layersInput")
    def layers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "layersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySizeInput")
    def memory_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memorySizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packageTypeInput")
    def package_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "packageTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishInput")
    def publish_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publishInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reservedConcurrentExecutionsInput")
    def reserved_concurrent_executions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "reservedConcurrentExecutionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeInput")
    def runtime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runtimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInput")
    def s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyInput")
    def s3_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ObjectVersionInput")
    def s3_object_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3ObjectVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeHashInput")
    def source_code_hash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCodeHashInput"))

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
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["LambdaFunctionTimeouts"]:
        return typing.cast(typing.Optional["LambdaFunctionTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tracingConfigInput")
    def tracing_config_input(self) -> typing.Optional["LambdaFunctionTracingConfig"]:
        return typing.cast(typing.Optional["LambdaFunctionTracingConfig"], jsii.get(self, "tracingConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfigInput")
    def vpc_config_input(self) -> typing.Optional["LambdaFunctionVpcConfig"]:
        return typing.cast(typing.Optional["LambdaFunctionVpcConfig"], jsii.get(self, "vpcConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="architectures")
    def architectures(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "architectures"))

    @architectures.setter
    def architectures(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "architectures", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeSigningConfigArn")
    def code_signing_config_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "codeSigningConfigArn"))

    @code_signing_config_arn.setter
    def code_signing_config_arn(self, value: builtins.str) -> None:
        jsii.set(self, "codeSigningConfigArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filename")
    def filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filename"))

    @filename.setter
    def filename(self, value: builtins.str) -> None:
        jsii.set(self, "filename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "handler"))

    @handler.setter
    def handler(self, value: builtins.str) -> None:
        jsii.set(self, "handler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageUri"))

    @image_uri.setter
    def image_uri(self, value: builtins.str) -> None:
        jsii.set(self, "imageUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layers")
    def layers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "layers"))

    @layers.setter
    def layers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "layers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySize")
    def memory_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memorySize"))

    @memory_size.setter
    def memory_size(self, value: jsii.Number) -> None:
        jsii.set(self, "memorySize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packageType")
    def package_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "packageType"))

    @package_type.setter
    def package_type(self, value: builtins.str) -> None:
        jsii.set(self, "packageType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publish")
    def publish(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publish"))

    @publish.setter
    def publish(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "publish", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reservedConcurrentExecutions")
    def reserved_concurrent_executions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "reservedConcurrentExecutions"))

    @reserved_concurrent_executions.setter
    def reserved_concurrent_executions(self, value: jsii.Number) -> None:
        jsii.set(self, "reservedConcurrentExecutions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtime"))

    @runtime.setter
    def runtime(self, value: builtins.str) -> None:
        jsii.set(self, "runtime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @s3_bucket.setter
    def s3_bucket(self, value: builtins.str) -> None:
        jsii.set(self, "s3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Key")
    def s3_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Key"))

    @s3_key.setter
    def s3_key(self, value: builtins.str) -> None:
        jsii.set(self, "s3Key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ObjectVersion")
    def s3_object_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3ObjectVersion"))

    @s3_object_version.setter
    def s3_object_version(self, value: builtins.str) -> None:
        jsii.set(self, "s3ObjectVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeHash")
    def source_code_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodeHash"))

    @source_code_hash.setter
    def source_code_hash(self, value: builtins.str) -> None:
        jsii.set(self, "sourceCodeHash", value)

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
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "timeout", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "role": "role",
        "architectures": "architectures",
        "code_signing_config_arn": "codeSigningConfigArn",
        "dead_letter_config": "deadLetterConfig",
        "description": "description",
        "environment": "environment",
        "filename": "filename",
        "file_system_config": "fileSystemConfig",
        "handler": "handler",
        "image_config": "imageConfig",
        "image_uri": "imageUri",
        "kms_key_arn": "kmsKeyArn",
        "layers": "layers",
        "memory_size": "memorySize",
        "package_type": "packageType",
        "publish": "publish",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "runtime": "runtime",
        "s3_bucket": "s3Bucket",
        "s3_key": "s3Key",
        "s3_object_version": "s3ObjectVersion",
        "source_code_hash": "sourceCodeHash",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeout": "timeout",
        "timeouts": "timeouts",
        "tracing_config": "tracingConfig",
        "vpc_config": "vpcConfig",
    },
)
class LambdaFunctionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        role: builtins.str,
        architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_signing_config_arn: typing.Optional[builtins.str] = None,
        dead_letter_config: typing.Optional["LambdaFunctionDeadLetterConfig"] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional["LambdaFunctionEnvironment"] = None,
        filename: typing.Optional[builtins.str] = None,
        file_system_config: typing.Optional["LambdaFunctionFileSystemConfig"] = None,
        handler: typing.Optional[builtins.str] = None,
        image_config: typing.Optional["LambdaFunctionImageConfig"] = None,
        image_uri: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        layers: typing.Optional[typing.Sequence[builtins.str]] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        package_type: typing.Optional[builtins.str] = None,
        publish: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        runtime: typing.Optional[builtins.str] = None,
        s3_bucket: typing.Optional[builtins.str] = None,
        s3_key: typing.Optional[builtins.str] = None,
        s3_object_version: typing.Optional[builtins.str] = None,
        source_code_hash: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        timeouts: typing.Optional["LambdaFunctionTimeouts"] = None,
        tracing_config: typing.Optional["LambdaFunctionTracingConfig"] = None,
        vpc_config: typing.Optional["LambdaFunctionVpcConfig"] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#function_name LambdaFunction#function_name}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#role LambdaFunction#role}.
        :param architectures: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#architectures LambdaFunction#architectures}.
        :param code_signing_config_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#code_signing_config_arn LambdaFunction#code_signing_config_arn}.
        :param dead_letter_config: dead_letter_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#dead_letter_config LambdaFunction#dead_letter_config}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#description LambdaFunction#description}.
        :param environment: environment block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#environment LambdaFunction#environment}
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#filename LambdaFunction#filename}.
        :param file_system_config: file_system_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#file_system_config LambdaFunction#file_system_config}
        :param handler: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#handler LambdaFunction#handler}.
        :param image_config: image_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#image_config LambdaFunction#image_config}
        :param image_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#image_uri LambdaFunction#image_uri}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#kms_key_arn LambdaFunction#kms_key_arn}.
        :param layers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#layers LambdaFunction#layers}.
        :param memory_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#memory_size LambdaFunction#memory_size}.
        :param package_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#package_type LambdaFunction#package_type}.
        :param publish: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#publish LambdaFunction#publish}.
        :param reserved_concurrent_executions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#reserved_concurrent_executions LambdaFunction#reserved_concurrent_executions}.
        :param runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#runtime LambdaFunction#runtime}.
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_bucket LambdaFunction#s3_bucket}.
        :param s3_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_key LambdaFunction#s3_key}.
        :param s3_object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_object_version LambdaFunction#s3_object_version}.
        :param source_code_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#source_code_hash LambdaFunction#source_code_hash}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tags LambdaFunction#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tags_all LambdaFunction#tags_all}.
        :param timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#timeout LambdaFunction#timeout}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#timeouts LambdaFunction#timeouts}
        :param tracing_config: tracing_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tracing_config LambdaFunction#tracing_config}
        :param vpc_config: vpc_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#vpc_config LambdaFunction#vpc_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(dead_letter_config, dict):
            dead_letter_config = LambdaFunctionDeadLetterConfig(**dead_letter_config)
        if isinstance(environment, dict):
            environment = LambdaFunctionEnvironment(**environment)
        if isinstance(file_system_config, dict):
            file_system_config = LambdaFunctionFileSystemConfig(**file_system_config)
        if isinstance(image_config, dict):
            image_config = LambdaFunctionImageConfig(**image_config)
        if isinstance(timeouts, dict):
            timeouts = LambdaFunctionTimeouts(**timeouts)
        if isinstance(tracing_config, dict):
            tracing_config = LambdaFunctionTracingConfig(**tracing_config)
        if isinstance(vpc_config, dict):
            vpc_config = LambdaFunctionVpcConfig(**vpc_config)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
            "role": role,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if architectures is not None:
            self._values["architectures"] = architectures
        if code_signing_config_arn is not None:
            self._values["code_signing_config_arn"] = code_signing_config_arn
        if dead_letter_config is not None:
            self._values["dead_letter_config"] = dead_letter_config
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if filename is not None:
            self._values["filename"] = filename
        if file_system_config is not None:
            self._values["file_system_config"] = file_system_config
        if handler is not None:
            self._values["handler"] = handler
        if image_config is not None:
            self._values["image_config"] = image_config
        if image_uri is not None:
            self._values["image_uri"] = image_uri
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if layers is not None:
            self._values["layers"] = layers
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if package_type is not None:
            self._values["package_type"] = package_type
        if publish is not None:
            self._values["publish"] = publish
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if runtime is not None:
            self._values["runtime"] = runtime
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket
        if s3_key is not None:
            self._values["s3_key"] = s3_key
        if s3_object_version is not None:
            self._values["s3_object_version"] = s3_object_version
        if source_code_hash is not None:
            self._values["source_code_hash"] = source_code_hash
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeout is not None:
            self._values["timeout"] = timeout
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if tracing_config is not None:
            self._values["tracing_config"] = tracing_config
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#function_name LambdaFunction#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#role LambdaFunction#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def architectures(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#architectures LambdaFunction#architectures}.'''
        result = self._values.get("architectures")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def code_signing_config_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#code_signing_config_arn LambdaFunction#code_signing_config_arn}.'''
        result = self._values.get("code_signing_config_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dead_letter_config(self) -> typing.Optional["LambdaFunctionDeadLetterConfig"]:
        '''dead_letter_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#dead_letter_config LambdaFunction#dead_letter_config}
        '''
        result = self._values.get("dead_letter_config")
        return typing.cast(typing.Optional["LambdaFunctionDeadLetterConfig"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#description LambdaFunction#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional["LambdaFunctionEnvironment"]:
        '''environment block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#environment LambdaFunction#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional["LambdaFunctionEnvironment"], result)

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#filename LambdaFunction#filename}.'''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_config(self) -> typing.Optional["LambdaFunctionFileSystemConfig"]:
        '''file_system_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#file_system_config LambdaFunction#file_system_config}
        '''
        result = self._values.get("file_system_config")
        return typing.cast(typing.Optional["LambdaFunctionFileSystemConfig"], result)

    @builtins.property
    def handler(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#handler LambdaFunction#handler}.'''
        result = self._values.get("handler")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_config(self) -> typing.Optional["LambdaFunctionImageConfig"]:
        '''image_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#image_config LambdaFunction#image_config}
        '''
        result = self._values.get("image_config")
        return typing.cast(typing.Optional["LambdaFunctionImageConfig"], result)

    @builtins.property
    def image_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#image_uri LambdaFunction#image_uri}.'''
        result = self._values.get("image_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#kms_key_arn LambdaFunction#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#layers LambdaFunction#layers}.'''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#memory_size LambdaFunction#memory_size}.'''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def package_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#package_type LambdaFunction#package_type}.'''
        result = self._values.get("package_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#publish LambdaFunction#publish}.'''
        result = self._values.get("publish")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#reserved_concurrent_executions LambdaFunction#reserved_concurrent_executions}.'''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def runtime(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#runtime LambdaFunction#runtime}.'''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_bucket LambdaFunction#s3_bucket}.'''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_key LambdaFunction#s3_key}.'''
        result = self._values.get("s3_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_object_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#s3_object_version LambdaFunction#s3_object_version}.'''
        result = self._values.get("s3_object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_code_hash(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#source_code_hash LambdaFunction#source_code_hash}.'''
        result = self._values.get("source_code_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tags LambdaFunction#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tags_all LambdaFunction#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#timeout LambdaFunction#timeout}.'''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LambdaFunctionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#timeouts LambdaFunction#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LambdaFunctionTimeouts"], result)

    @builtins.property
    def tracing_config(self) -> typing.Optional["LambdaFunctionTracingConfig"]:
        '''tracing_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#tracing_config LambdaFunction#tracing_config}
        '''
        result = self._values.get("tracing_config")
        return typing.cast(typing.Optional["LambdaFunctionTracingConfig"], result)

    @builtins.property
    def vpc_config(self) -> typing.Optional["LambdaFunctionVpcConfig"]:
        '''vpc_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#vpc_config LambdaFunction#vpc_config}
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional["LambdaFunctionVpcConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionDeadLetterConfig",
    jsii_struct_bases=[],
    name_mapping={"target_arn": "targetArn"},
)
class LambdaFunctionDeadLetterConfig:
    def __init__(self, *, target_arn: builtins.str) -> None:
        '''
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#target_arn LambdaFunction#target_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_arn": target_arn,
        }

    @builtins.property
    def target_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#target_arn LambdaFunction#target_arn}.'''
        result = self._values.get("target_arn")
        assert result is not None, "Required property 'target_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionDeadLetterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionDeadLetterConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionDeadLetterConfigOutputReference",
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
    @jsii.member(jsii_name="targetArnInput")
    def target_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @target_arn.setter
    def target_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionDeadLetterConfig]:
        return typing.cast(typing.Optional[LambdaFunctionDeadLetterConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaFunctionDeadLetterConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEnvironment",
    jsii_struct_bases=[],
    name_mapping={"variables": "variables"},
)
class LambdaFunctionEnvironment:
    def __init__(
        self,
        *,
        variables: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param variables: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#variables LambdaFunction#variables}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if variables is not None:
            self._values["variables"] = variables

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#variables LambdaFunction#variables}.'''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionEnvironment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionEnvironmentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEnvironmentOutputReference",
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

    @jsii.member(jsii_name="resetVariables")
    def reset_variables(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariables", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variablesInput")
    def variables_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "variablesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "variables"))

    @variables.setter
    def variables(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "variables", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionEnvironment]:
        return typing.cast(typing.Optional[LambdaFunctionEnvironment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LambdaFunctionEnvironment]) -> None:
        jsii.set(self, "internalValue", value)


class LambdaFunctionEventInvokeConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config aws_lambda_function_event_invoke_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        destination_config: typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfig"] = None,
        maximum_event_age_in_seconds: typing.Optional[jsii.Number] = None,
        maximum_retry_attempts: typing.Optional[jsii.Number] = None,
        qualifier: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config aws_lambda_function_event_invoke_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#function_name LambdaFunctionEventInvokeConfig#function_name}.
        :param destination_config: destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination_config LambdaFunctionEventInvokeConfig#destination_config}
        :param maximum_event_age_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#maximum_event_age_in_seconds LambdaFunctionEventInvokeConfig#maximum_event_age_in_seconds}.
        :param maximum_retry_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#maximum_retry_attempts LambdaFunctionEventInvokeConfig#maximum_retry_attempts}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#qualifier LambdaFunctionEventInvokeConfig#qualifier}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaFunctionEventInvokeConfigConfig(
            function_name=function_name,
            destination_config=destination_config,
            maximum_event_age_in_seconds=maximum_event_age_in_seconds,
            maximum_retry_attempts=maximum_retry_attempts,
            qualifier=qualifier,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDestinationConfig")
    def put_destination_config(
        self,
        *,
        on_failure: typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnFailure"] = None,
        on_success: typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess"] = None,
    ) -> None:
        '''
        :param on_failure: on_failure block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#on_failure LambdaFunctionEventInvokeConfig#on_failure}
        :param on_success: on_success block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#on_success LambdaFunctionEventInvokeConfig#on_success}
        '''
        value = LambdaFunctionEventInvokeConfigDestinationConfig(
            on_failure=on_failure, on_success=on_success
        )

        return typing.cast(None, jsii.invoke(self, "putDestinationConfig", [value]))

    @jsii.member(jsii_name="resetDestinationConfig")
    def reset_destination_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationConfig", []))

    @jsii.member(jsii_name="resetMaximumEventAgeInSeconds")
    def reset_maximum_event_age_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumEventAgeInSeconds", []))

    @jsii.member(jsii_name="resetMaximumRetryAttempts")
    def reset_maximum_retry_attempts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumRetryAttempts", []))

    @jsii.member(jsii_name="resetQualifier")
    def reset_qualifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQualifier", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationConfig")
    def destination_config(
        self,
    ) -> "LambdaFunctionEventInvokeConfigDestinationConfigOutputReference":
        return typing.cast("LambdaFunctionEventInvokeConfigDestinationConfigOutputReference", jsii.get(self, "destinationConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationConfigInput")
    def destination_config_input(
        self,
    ) -> typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfig"]:
        return typing.cast(typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfig"], jsii.get(self, "destinationConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumEventAgeInSecondsInput")
    def maximum_event_age_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumEventAgeInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumRetryAttemptsInput")
    def maximum_retry_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumRetryAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifierInput")
    def qualifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "qualifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumEventAgeInSeconds")
    def maximum_event_age_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumEventAgeInSeconds"))

    @maximum_event_age_in_seconds.setter
    def maximum_event_age_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "maximumEventAgeInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maximumRetryAttempts")
    def maximum_retry_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumRetryAttempts"))

    @maximum_retry_attempts.setter
    def maximum_retry_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maximumRetryAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifier")
    def qualifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifier"))

    @qualifier.setter
    def qualifier(self, value: builtins.str) -> None:
        jsii.set(self, "qualifier", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "destination_config": "destinationConfig",
        "maximum_event_age_in_seconds": "maximumEventAgeInSeconds",
        "maximum_retry_attempts": "maximumRetryAttempts",
        "qualifier": "qualifier",
    },
)
class LambdaFunctionEventInvokeConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        destination_config: typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfig"] = None,
        maximum_event_age_in_seconds: typing.Optional[jsii.Number] = None,
        maximum_retry_attempts: typing.Optional[jsii.Number] = None,
        qualifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#function_name LambdaFunctionEventInvokeConfig#function_name}.
        :param destination_config: destination_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination_config LambdaFunctionEventInvokeConfig#destination_config}
        :param maximum_event_age_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#maximum_event_age_in_seconds LambdaFunctionEventInvokeConfig#maximum_event_age_in_seconds}.
        :param maximum_retry_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#maximum_retry_attempts LambdaFunctionEventInvokeConfig#maximum_retry_attempts}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#qualifier LambdaFunctionEventInvokeConfig#qualifier}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(destination_config, dict):
            destination_config = LambdaFunctionEventInvokeConfigDestinationConfig(**destination_config)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if destination_config is not None:
            self._values["destination_config"] = destination_config
        if maximum_event_age_in_seconds is not None:
            self._values["maximum_event_age_in_seconds"] = maximum_event_age_in_seconds
        if maximum_retry_attempts is not None:
            self._values["maximum_retry_attempts"] = maximum_retry_attempts
        if qualifier is not None:
            self._values["qualifier"] = qualifier

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#function_name LambdaFunctionEventInvokeConfig#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_config(
        self,
    ) -> typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfig"]:
        '''destination_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination_config LambdaFunctionEventInvokeConfig#destination_config}
        '''
        result = self._values.get("destination_config")
        return typing.cast(typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfig"], result)

    @builtins.property
    def maximum_event_age_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#maximum_event_age_in_seconds LambdaFunctionEventInvokeConfig#maximum_event_age_in_seconds}.'''
        result = self._values.get("maximum_event_age_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum_retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#maximum_retry_attempts LambdaFunctionEventInvokeConfig#maximum_retry_attempts}.'''
        result = self._values.get("maximum_retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def qualifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#qualifier LambdaFunctionEventInvokeConfig#qualifier}.'''
        result = self._values.get("qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionEventInvokeConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigDestinationConfig",
    jsii_struct_bases=[],
    name_mapping={"on_failure": "onFailure", "on_success": "onSuccess"},
)
class LambdaFunctionEventInvokeConfigDestinationConfig:
    def __init__(
        self,
        *,
        on_failure: typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnFailure"] = None,
        on_success: typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess"] = None,
    ) -> None:
        '''
        :param on_failure: on_failure block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#on_failure LambdaFunctionEventInvokeConfig#on_failure}
        :param on_success: on_success block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#on_success LambdaFunctionEventInvokeConfig#on_success}
        '''
        if isinstance(on_failure, dict):
            on_failure = LambdaFunctionEventInvokeConfigDestinationConfigOnFailure(**on_failure)
        if isinstance(on_success, dict):
            on_success = LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess(**on_success)
        self._values: typing.Dict[str, typing.Any] = {}
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success

    @builtins.property
    def on_failure(
        self,
    ) -> typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnFailure"]:
        '''on_failure block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#on_failure LambdaFunctionEventInvokeConfig#on_failure}
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnFailure"], result)

    @builtins.property
    def on_success(
        self,
    ) -> typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess"]:
        '''on_success block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#on_success LambdaFunctionEventInvokeConfig#on_success}
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional["LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionEventInvokeConfigDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigDestinationConfigOnFailure",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class LambdaFunctionEventInvokeConfigDestinationConfigOnFailure:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination LambdaFunctionEventInvokeConfig#destination}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination LambdaFunctionEventInvokeConfig#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionEventInvokeConfigDestinationConfigOnFailure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionEventInvokeConfigDestinationConfigOnFailureOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigDestinationConfigOnFailureOutputReference",
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
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        jsii.set(self, "destination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnFailure]:
        return typing.cast(typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnFailure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnFailure],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination LambdaFunctionEventInvokeConfig#destination}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination LambdaFunctionEventInvokeConfig#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionEventInvokeConfigDestinationConfigOnSuccessOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigDestinationConfigOnSuccessOutputReference",
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
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        jsii.set(self, "destination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess]:
        return typing.cast(typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LambdaFunctionEventInvokeConfigDestinationConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionEventInvokeConfigDestinationConfigOutputReference",
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

    @jsii.member(jsii_name="putOnFailure")
    def put_on_failure(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination LambdaFunctionEventInvokeConfig#destination}.
        '''
        value = LambdaFunctionEventInvokeConfigDestinationConfigOnFailure(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putOnFailure", [value]))

    @jsii.member(jsii_name="putOnSuccess")
    def put_on_success(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function_event_invoke_config#destination LambdaFunctionEventInvokeConfig#destination}.
        '''
        value = LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putOnSuccess", [value]))

    @jsii.member(jsii_name="resetOnFailure")
    def reset_on_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnFailure", []))

    @jsii.member(jsii_name="resetOnSuccess")
    def reset_on_success(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnSuccess", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onFailure")
    def on_failure(
        self,
    ) -> LambdaFunctionEventInvokeConfigDestinationConfigOnFailureOutputReference:
        return typing.cast(LambdaFunctionEventInvokeConfigDestinationConfigOnFailureOutputReference, jsii.get(self, "onFailure"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onSuccess")
    def on_success(
        self,
    ) -> LambdaFunctionEventInvokeConfigDestinationConfigOnSuccessOutputReference:
        return typing.cast(LambdaFunctionEventInvokeConfigDestinationConfigOnSuccessOutputReference, jsii.get(self, "onSuccess"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onFailureInput")
    def on_failure_input(
        self,
    ) -> typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnFailure]:
        return typing.cast(typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnFailure], jsii.get(self, "onFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onSuccessInput")
    def on_success_input(
        self,
    ) -> typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess]:
        return typing.cast(typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess], jsii.get(self, "onSuccessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfig]:
        return typing.cast(typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaFunctionEventInvokeConfigDestinationConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionFileSystemConfig",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "local_mount_path": "localMountPath"},
)
class LambdaFunctionFileSystemConfig:
    def __init__(self, *, arn: builtins.str, local_mount_path: builtins.str) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#arn LambdaFunction#arn}.
        :param local_mount_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#local_mount_path LambdaFunction#local_mount_path}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "local_mount_path": local_mount_path,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#arn LambdaFunction#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def local_mount_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#local_mount_path LambdaFunction#local_mount_path}.'''
        result = self._values.get("local_mount_path")
        assert result is not None, "Required property 'local_mount_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionFileSystemConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionFileSystemConfigOutputReference",
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
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localMountPathInput")
    def local_mount_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localMountPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localMountPath")
    def local_mount_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localMountPath"))

    @local_mount_path.setter
    def local_mount_path(self, value: builtins.str) -> None:
        jsii.set(self, "localMountPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionFileSystemConfig]:
        return typing.cast(typing.Optional[LambdaFunctionFileSystemConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaFunctionFileSystemConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionImageConfig",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "entry_point": "entryPoint",
        "working_directory": "workingDirectory",
    },
)
class LambdaFunctionImageConfig:
    def __init__(
        self,
        *,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        entry_point: typing.Optional[typing.Sequence[builtins.str]] = None,
        working_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param command: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#command LambdaFunction#command}.
        :param entry_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#entry_point LambdaFunction#entry_point}.
        :param working_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#working_directory LambdaFunction#working_directory}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if command is not None:
            self._values["command"] = command
        if entry_point is not None:
            self._values["entry_point"] = entry_point
        if working_directory is not None:
            self._values["working_directory"] = working_directory

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#command LambdaFunction#command}.'''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entry_point(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#entry_point LambdaFunction#entry_point}.'''
        result = self._values.get("entry_point")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def working_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#working_directory LambdaFunction#working_directory}.'''
        result = self._values.get("working_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionImageConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionImageConfigOutputReference",
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

    @jsii.member(jsii_name="resetCommand")
    def reset_command(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommand", []))

    @jsii.member(jsii_name="resetEntryPoint")
    def reset_entry_point(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntryPoint", []))

    @jsii.member(jsii_name="resetWorkingDirectory")
    def reset_working_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkingDirectory", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commandInput")
    def command_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "commandInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entryPointInput")
    def entry_point_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "entryPointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectoryInput")
    def working_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entryPoint")
    def entry_point(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "entryPoint"))

    @entry_point.setter
    def entry_point(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "entryPoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDirectory"))

    @working_directory.setter
    def working_directory(self, value: builtins.str) -> None:
        jsii.set(self, "workingDirectory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionImageConfig]:
        return typing.cast(typing.Optional[LambdaFunctionImageConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LambdaFunctionImageConfig]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class LambdaFunctionTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#create LambdaFunction#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#create LambdaFunction#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionTimeouts]:
        return typing.cast(typing.Optional[LambdaFunctionTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LambdaFunctionTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionTracingConfig",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class LambdaFunctionTracingConfig:
    def __init__(self, *, mode: builtins.str) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#mode LambdaFunction#mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mode": mode,
        }

    @builtins.property
    def mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#mode LambdaFunction#mode}.'''
        result = self._values.get("mode")
        assert result is not None, "Required property 'mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionTracingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionTracingConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionTracingConfigOutputReference",
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
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionTracingConfig]:
        return typing.cast(typing.Optional[LambdaFunctionTracingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaFunctionTracingConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionVpcConfig",
    jsii_struct_bases=[],
    name_mapping={"security_group_ids": "securityGroupIds", "subnet_ids": "subnetIds"},
)
class LambdaFunctionVpcConfig:
    def __init__(
        self,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_ids: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#security_group_ids LambdaFunction#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#subnet_ids LambdaFunction#subnet_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "security_group_ids": security_group_ids,
            "subnet_ids": subnet_ids,
        }

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#security_group_ids LambdaFunction#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_function#subnet_ids LambdaFunction#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionVpcConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaFunctionVpcConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaFunctionVpcConfigOutputReference",
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
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LambdaFunctionVpcConfig]:
        return typing.cast(typing.Optional[LambdaFunctionVpcConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LambdaFunctionVpcConfig]) -> None:
        jsii.set(self, "internalValue", value)


class LambdaLayerVersion(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaLayerVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version aws_lambda_layer_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        layer_name: builtins.str,
        compatible_architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
        compatible_runtimes: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        filename: typing.Optional[builtins.str] = None,
        license_info: typing.Optional[builtins.str] = None,
        s3_bucket: typing.Optional[builtins.str] = None,
        s3_key: typing.Optional[builtins.str] = None,
        s3_object_version: typing.Optional[builtins.str] = None,
        skip_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source_code_hash: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version aws_lambda_layer_version} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param layer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#layer_name LambdaLayerVersion#layer_name}.
        :param compatible_architectures: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#compatible_architectures LambdaLayerVersion#compatible_architectures}.
        :param compatible_runtimes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#compatible_runtimes LambdaLayerVersion#compatible_runtimes}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#description LambdaLayerVersion#description}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#filename LambdaLayerVersion#filename}.
        :param license_info: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#license_info LambdaLayerVersion#license_info}.
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_bucket LambdaLayerVersion#s3_bucket}.
        :param s3_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_key LambdaLayerVersion#s3_key}.
        :param s3_object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_object_version LambdaLayerVersion#s3_object_version}.
        :param skip_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#skip_destroy LambdaLayerVersion#skip_destroy}.
        :param source_code_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#source_code_hash LambdaLayerVersion#source_code_hash}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaLayerVersionConfig(
            layer_name=layer_name,
            compatible_architectures=compatible_architectures,
            compatible_runtimes=compatible_runtimes,
            description=description,
            filename=filename,
            license_info=license_info,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            s3_object_version=s3_object_version,
            skip_destroy=skip_destroy,
            source_code_hash=source_code_hash,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCompatibleArchitectures")
    def reset_compatible_architectures(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibleArchitectures", []))

    @jsii.member(jsii_name="resetCompatibleRuntimes")
    def reset_compatible_runtimes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompatibleRuntimes", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFilename")
    def reset_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilename", []))

    @jsii.member(jsii_name="resetLicenseInfo")
    def reset_license_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseInfo", []))

    @jsii.member(jsii_name="resetS3Bucket")
    def reset_s3_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Bucket", []))

    @jsii.member(jsii_name="resetS3Key")
    def reset_s3_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Key", []))

    @jsii.member(jsii_name="resetS3ObjectVersion")
    def reset_s3_object_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3ObjectVersion", []))

    @jsii.member(jsii_name="resetSkipDestroy")
    def reset_skip_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipDestroy", []))

    @jsii.member(jsii_name="resetSourceCodeHash")
    def reset_source_code_hash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCodeHash", []))

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
    @jsii.member(jsii_name="createdDate")
    def created_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerArn")
    def layer_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "layerArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingJobArn")
    def signing_job_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingJobArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingProfileVersionArn")
    def signing_profile_version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingProfileVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeSize")
    def source_code_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sourceCodeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleArchitecturesInput")
    def compatible_architectures_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "compatibleArchitecturesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleRuntimesInput")
    def compatible_runtimes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "compatibleRuntimesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filenameInput")
    def filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerNameInput")
    def layer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "layerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseInfoInput")
    def license_info_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "licenseInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInput")
    def s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyInput")
    def s3_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ObjectVersionInput")
    def s3_object_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3ObjectVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipDestroyInput")
    def skip_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeHashInput")
    def source_code_hash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCodeHashInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleArchitectures")
    def compatible_architectures(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibleArchitectures"))

    @compatible_architectures.setter
    def compatible_architectures(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "compatibleArchitectures", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "compatibleRuntimes"))

    @compatible_runtimes.setter
    def compatible_runtimes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "compatibleRuntimes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filename")
    def filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filename"))

    @filename.setter
    def filename(self, value: builtins.str) -> None:
        jsii.set(self, "filename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerName")
    def layer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "layerName"))

    @layer_name.setter
    def layer_name(self, value: builtins.str) -> None:
        jsii.set(self, "layerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseInfo")
    def license_info(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseInfo"))

    @license_info.setter
    def license_info(self, value: builtins.str) -> None:
        jsii.set(self, "licenseInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Bucket"))

    @s3_bucket.setter
    def s3_bucket(self, value: builtins.str) -> None:
        jsii.set(self, "s3Bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Key")
    def s3_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3Key"))

    @s3_key.setter
    def s3_key(self, value: builtins.str) -> None:
        jsii.set(self, "s3Key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ObjectVersion")
    def s3_object_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3ObjectVersion"))

    @s3_object_version.setter
    def s3_object_version(self, value: builtins.str) -> None:
        jsii.set(self, "s3ObjectVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipDestroy")
    def skip_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "skipDestroy"))

    @skip_destroy.setter
    def skip_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "skipDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCodeHash")
    def source_code_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCodeHash"))

    @source_code_hash.setter
    def source_code_hash(self, value: builtins.str) -> None:
        jsii.set(self, "sourceCodeHash", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaLayerVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "layer_name": "layerName",
        "compatible_architectures": "compatibleArchitectures",
        "compatible_runtimes": "compatibleRuntimes",
        "description": "description",
        "filename": "filename",
        "license_info": "licenseInfo",
        "s3_bucket": "s3Bucket",
        "s3_key": "s3Key",
        "s3_object_version": "s3ObjectVersion",
        "skip_destroy": "skipDestroy",
        "source_code_hash": "sourceCodeHash",
    },
)
class LambdaLayerVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        layer_name: builtins.str,
        compatible_architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
        compatible_runtimes: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        filename: typing.Optional[builtins.str] = None,
        license_info: typing.Optional[builtins.str] = None,
        s3_bucket: typing.Optional[builtins.str] = None,
        s3_key: typing.Optional[builtins.str] = None,
        s3_object_version: typing.Optional[builtins.str] = None,
        skip_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source_code_hash: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param layer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#layer_name LambdaLayerVersion#layer_name}.
        :param compatible_architectures: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#compatible_architectures LambdaLayerVersion#compatible_architectures}.
        :param compatible_runtimes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#compatible_runtimes LambdaLayerVersion#compatible_runtimes}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#description LambdaLayerVersion#description}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#filename LambdaLayerVersion#filename}.
        :param license_info: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#license_info LambdaLayerVersion#license_info}.
        :param s3_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_bucket LambdaLayerVersion#s3_bucket}.
        :param s3_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_key LambdaLayerVersion#s3_key}.
        :param s3_object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_object_version LambdaLayerVersion#s3_object_version}.
        :param skip_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#skip_destroy LambdaLayerVersion#skip_destroy}.
        :param source_code_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#source_code_hash LambdaLayerVersion#source_code_hash}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "layer_name": layer_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if compatible_architectures is not None:
            self._values["compatible_architectures"] = compatible_architectures
        if compatible_runtimes is not None:
            self._values["compatible_runtimes"] = compatible_runtimes
        if description is not None:
            self._values["description"] = description
        if filename is not None:
            self._values["filename"] = filename
        if license_info is not None:
            self._values["license_info"] = license_info
        if s3_bucket is not None:
            self._values["s3_bucket"] = s3_bucket
        if s3_key is not None:
            self._values["s3_key"] = s3_key
        if s3_object_version is not None:
            self._values["s3_object_version"] = s3_object_version
        if skip_destroy is not None:
            self._values["skip_destroy"] = skip_destroy
        if source_code_hash is not None:
            self._values["source_code_hash"] = source_code_hash

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
    def layer_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#layer_name LambdaLayerVersion#layer_name}.'''
        result = self._values.get("layer_name")
        assert result is not None, "Required property 'layer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compatible_architectures(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#compatible_architectures LambdaLayerVersion#compatible_architectures}.'''
        result = self._values.get("compatible_architectures")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def compatible_runtimes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#compatible_runtimes LambdaLayerVersion#compatible_runtimes}.'''
        result = self._values.get("compatible_runtimes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#description LambdaLayerVersion#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#filename LambdaLayerVersion#filename}.'''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license_info(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#license_info LambdaLayerVersion#license_info}.'''
        result = self._values.get("license_info")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_bucket LambdaLayerVersion#s3_bucket}.'''
        result = self._values.get("s3_bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_key LambdaLayerVersion#s3_key}.'''
        result = self._values.get("s3_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_object_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#s3_object_version LambdaLayerVersion#s3_object_version}.'''
        result = self._values.get("s3_object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#skip_destroy LambdaLayerVersion#skip_destroy}.'''
        result = self._values.get("skip_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def source_code_hash(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version#source_code_hash LambdaLayerVersion#source_code_hash}.'''
        result = self._values.get("source_code_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaLayerVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaLayerVersionPermission(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaLayerVersionPermission",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission aws_lambda_layer_version_permission}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action: builtins.str,
        layer_name: builtins.str,
        principal: builtins.str,
        statement_id: builtins.str,
        version_number: jsii.Number,
        organization_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission aws_lambda_layer_version_permission} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#action LambdaLayerVersionPermission#action}.
        :param layer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#layer_name LambdaLayerVersionPermission#layer_name}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#principal LambdaLayerVersionPermission#principal}.
        :param statement_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#statement_id LambdaLayerVersionPermission#statement_id}.
        :param version_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#version_number LambdaLayerVersionPermission#version_number}.
        :param organization_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#organization_id LambdaLayerVersionPermission#organization_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaLayerVersionPermissionConfig(
            action=action,
            layer_name=layer_name,
            principal=principal,
            statement_id=statement_id,
            version_number=version_number,
            organization_id=organization_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetOrganizationId")
    def reset_organization_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationId", []))

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
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revisionId")
    def revision_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revisionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerNameInput")
    def layer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "layerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationIdInput")
    def organization_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalInput")
    def principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdInput")
    def statement_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statementIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionNumberInput")
    def version_number_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "versionNumberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerName")
    def layer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "layerName"))

    @layer_name.setter
    def layer_name(self, value: builtins.str) -> None:
        jsii.set(self, "layerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: builtins.str) -> None:
        jsii.set(self, "organizationId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        jsii.set(self, "principal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementId")
    def statement_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statementId"))

    @statement_id.setter
    def statement_id(self, value: builtins.str) -> None:
        jsii.set(self, "statementId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionNumber")
    def version_number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "versionNumber"))

    @version_number.setter
    def version_number(self, value: jsii.Number) -> None:
        jsii.set(self, "versionNumber", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaLayerVersionPermissionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action": "action",
        "layer_name": "layerName",
        "principal": "principal",
        "statement_id": "statementId",
        "version_number": "versionNumber",
        "organization_id": "organizationId",
    },
)
class LambdaLayerVersionPermissionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action: builtins.str,
        layer_name: builtins.str,
        principal: builtins.str,
        statement_id: builtins.str,
        version_number: jsii.Number,
        organization_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#action LambdaLayerVersionPermission#action}.
        :param layer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#layer_name LambdaLayerVersionPermission#layer_name}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#principal LambdaLayerVersionPermission#principal}.
        :param statement_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#statement_id LambdaLayerVersionPermission#statement_id}.
        :param version_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#version_number LambdaLayerVersionPermission#version_number}.
        :param organization_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#organization_id LambdaLayerVersionPermission#organization_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "layer_name": layer_name,
            "principal": principal,
            "statement_id": statement_id,
            "version_number": version_number,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if organization_id is not None:
            self._values["organization_id"] = organization_id

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
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#action LambdaLayerVersionPermission#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def layer_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#layer_name LambdaLayerVersionPermission#layer_name}.'''
        result = self._values.get("layer_name")
        assert result is not None, "Required property 'layer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#principal LambdaLayerVersionPermission#principal}.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def statement_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#statement_id LambdaLayerVersionPermission#statement_id}.'''
        result = self._values.get("statement_id")
        assert result is not None, "Required property 'statement_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_number(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#version_number LambdaLayerVersionPermission#version_number}.'''
        result = self._values.get("version_number")
        assert result is not None, "Required property 'version_number' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def organization_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_layer_version_permission#organization_id LambdaLayerVersionPermission#organization_id}.'''
        result = self._values.get("organization_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaLayerVersionPermissionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaPermission(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaPermission",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission aws_lambda_permission}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action: builtins.str,
        function_name: builtins.str,
        principal: builtins.str,
        event_source_token: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
        source_account: typing.Optional[builtins.str] = None,
        source_arn: typing.Optional[builtins.str] = None,
        statement_id: typing.Optional[builtins.str] = None,
        statement_id_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission aws_lambda_permission} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#action LambdaPermission#action}.
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#function_name LambdaPermission#function_name}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#principal LambdaPermission#principal}.
        :param event_source_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#event_source_token LambdaPermission#event_source_token}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#qualifier LambdaPermission#qualifier}.
        :param source_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#source_account LambdaPermission#source_account}.
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#source_arn LambdaPermission#source_arn}.
        :param statement_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#statement_id LambdaPermission#statement_id}.
        :param statement_id_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#statement_id_prefix LambdaPermission#statement_id_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaPermissionConfig(
            action=action,
            function_name=function_name,
            principal=principal,
            event_source_token=event_source_token,
            qualifier=qualifier,
            source_account=source_account,
            source_arn=source_arn,
            statement_id=statement_id,
            statement_id_prefix=statement_id_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEventSourceToken")
    def reset_event_source_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventSourceToken", []))

    @jsii.member(jsii_name="resetQualifier")
    def reset_qualifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQualifier", []))

    @jsii.member(jsii_name="resetSourceAccount")
    def reset_source_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceAccount", []))

    @jsii.member(jsii_name="resetSourceArn")
    def reset_source_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceArn", []))

    @jsii.member(jsii_name="resetStatementId")
    def reset_statement_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatementId", []))

    @jsii.member(jsii_name="resetStatementIdPrefix")
    def reset_statement_id_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatementIdPrefix", []))

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
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSourceTokenInput")
    def event_source_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventSourceTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalInput")
    def principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifierInput")
    def qualifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "qualifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceAccountInput")
    def source_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceAccountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArnInput")
    def source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdInput")
    def statement_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statementIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdPrefixInput")
    def statement_id_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statementIdPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventSourceToken")
    def event_source_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventSourceToken"))

    @event_source_token.setter
    def event_source_token(self, value: builtins.str) -> None:
        jsii.set(self, "eventSourceToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        jsii.set(self, "principal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifier")
    def qualifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifier"))

    @qualifier.setter
    def qualifier(self, value: builtins.str) -> None:
        jsii.set(self, "qualifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceAccount")
    def source_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceAccount"))

    @source_account.setter
    def source_account(self, value: builtins.str) -> None:
        jsii.set(self, "sourceAccount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceArn")
    def source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceArn"))

    @source_arn.setter
    def source_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementId")
    def statement_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statementId"))

    @statement_id.setter
    def statement_id(self, value: builtins.str) -> None:
        jsii.set(self, "statementId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdPrefix")
    def statement_id_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statementIdPrefix"))

    @statement_id_prefix.setter
    def statement_id_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "statementIdPrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaPermissionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action": "action",
        "function_name": "functionName",
        "principal": "principal",
        "event_source_token": "eventSourceToken",
        "qualifier": "qualifier",
        "source_account": "sourceAccount",
        "source_arn": "sourceArn",
        "statement_id": "statementId",
        "statement_id_prefix": "statementIdPrefix",
    },
)
class LambdaPermissionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action: builtins.str,
        function_name: builtins.str,
        principal: builtins.str,
        event_source_token: typing.Optional[builtins.str] = None,
        qualifier: typing.Optional[builtins.str] = None,
        source_account: typing.Optional[builtins.str] = None,
        source_arn: typing.Optional[builtins.str] = None,
        statement_id: typing.Optional[builtins.str] = None,
        statement_id_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#action LambdaPermission#action}.
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#function_name LambdaPermission#function_name}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#principal LambdaPermission#principal}.
        :param event_source_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#event_source_token LambdaPermission#event_source_token}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#qualifier LambdaPermission#qualifier}.
        :param source_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#source_account LambdaPermission#source_account}.
        :param source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#source_arn LambdaPermission#source_arn}.
        :param statement_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#statement_id LambdaPermission#statement_id}.
        :param statement_id_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#statement_id_prefix LambdaPermission#statement_id_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "function_name": function_name,
            "principal": principal,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if event_source_token is not None:
            self._values["event_source_token"] = event_source_token
        if qualifier is not None:
            self._values["qualifier"] = qualifier
        if source_account is not None:
            self._values["source_account"] = source_account
        if source_arn is not None:
            self._values["source_arn"] = source_arn
        if statement_id is not None:
            self._values["statement_id"] = statement_id
        if statement_id_prefix is not None:
            self._values["statement_id_prefix"] = statement_id_prefix

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
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#action LambdaPermission#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#function_name LambdaPermission#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#principal LambdaPermission#principal}.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_source_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#event_source_token LambdaPermission#event_source_token}.'''
        result = self._values.get("event_source_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def qualifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#qualifier LambdaPermission#qualifier}.'''
        result = self._values.get("qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#source_account LambdaPermission#source_account}.'''
        result = self._values.get("source_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#source_arn LambdaPermission#source_arn}.'''
        result = self._values.get("source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statement_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#statement_id LambdaPermission#statement_id}.'''
        result = self._values.get("statement_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statement_id_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_permission#statement_id_prefix LambdaPermission#statement_id_prefix}.'''
        result = self._values.get("statement_id_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaPermissionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaProvisionedConcurrencyConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaProvisionedConcurrencyConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config aws_lambda_provisioned_concurrency_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_name: builtins.str,
        provisioned_concurrent_executions: jsii.Number,
        qualifier: builtins.str,
        timeouts: typing.Optional["LambdaProvisionedConcurrencyConfigTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config aws_lambda_provisioned_concurrency_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#function_name LambdaProvisionedConcurrencyConfig#function_name}.
        :param provisioned_concurrent_executions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#provisioned_concurrent_executions LambdaProvisionedConcurrencyConfig#provisioned_concurrent_executions}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#qualifier LambdaProvisionedConcurrencyConfig#qualifier}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#timeouts LambdaProvisionedConcurrencyConfig#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LambdaProvisionedConcurrencyConfigConfig(
            function_name=function_name,
            provisioned_concurrent_executions=provisioned_concurrent_executions,
            qualifier=qualifier,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#create LambdaProvisionedConcurrencyConfig#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#update LambdaProvisionedConcurrencyConfig#update}.
        '''
        value = LambdaProvisionedConcurrencyConfigTimeouts(
            create=create, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LambdaProvisionedConcurrencyConfigTimeoutsOutputReference":
        return typing.cast("LambdaProvisionedConcurrencyConfigTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedConcurrentExecutionsInput")
    def provisioned_concurrent_executions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "provisionedConcurrentExecutionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifierInput")
    def qualifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "qualifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional["LambdaProvisionedConcurrencyConfigTimeouts"]:
        return typing.cast(typing.Optional["LambdaProvisionedConcurrencyConfigTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        jsii.set(self, "functionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedConcurrentExecutions")
    def provisioned_concurrent_executions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedConcurrentExecutions"))

    @provisioned_concurrent_executions.setter
    def provisioned_concurrent_executions(self, value: jsii.Number) -> None:
        jsii.set(self, "provisionedConcurrentExecutions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qualifier")
    def qualifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "qualifier"))

    @qualifier.setter
    def qualifier(self, value: builtins.str) -> None:
        jsii.set(self, "qualifier", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaProvisionedConcurrencyConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "function_name": "functionName",
        "provisioned_concurrent_executions": "provisionedConcurrentExecutions",
        "qualifier": "qualifier",
        "timeouts": "timeouts",
    },
)
class LambdaProvisionedConcurrencyConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        function_name: builtins.str,
        provisioned_concurrent_executions: jsii.Number,
        qualifier: builtins.str,
        timeouts: typing.Optional["LambdaProvisionedConcurrencyConfigTimeouts"] = None,
    ) -> None:
        '''AWS Lambda.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param function_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#function_name LambdaProvisionedConcurrencyConfig#function_name}.
        :param provisioned_concurrent_executions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#provisioned_concurrent_executions LambdaProvisionedConcurrencyConfig#provisioned_concurrent_executions}.
        :param qualifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#qualifier LambdaProvisionedConcurrencyConfig#qualifier}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#timeouts LambdaProvisionedConcurrencyConfig#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = LambdaProvisionedConcurrencyConfigTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "function_name": function_name,
            "provisioned_concurrent_executions": provisioned_concurrent_executions,
            "qualifier": qualifier,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#function_name LambdaProvisionedConcurrencyConfig#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provisioned_concurrent_executions(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#provisioned_concurrent_executions LambdaProvisionedConcurrencyConfig#provisioned_concurrent_executions}.'''
        result = self._values.get("provisioned_concurrent_executions")
        assert result is not None, "Required property 'provisioned_concurrent_executions' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def qualifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#qualifier LambdaProvisionedConcurrencyConfig#qualifier}.'''
        result = self._values.get("qualifier")
        assert result is not None, "Required property 'qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LambdaProvisionedConcurrencyConfigTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#timeouts LambdaProvisionedConcurrencyConfig#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LambdaProvisionedConcurrencyConfigTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaProvisionedConcurrencyConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaProvisionedConcurrencyConfigTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class LambdaProvisionedConcurrencyConfigTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#create LambdaProvisionedConcurrencyConfig#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#update LambdaProvisionedConcurrencyConfig#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#create LambdaProvisionedConcurrencyConfig#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lambda_provisioned_concurrency_config#update LambdaProvisionedConcurrencyConfig#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaProvisionedConcurrencyConfigTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaProvisionedConcurrencyConfigTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lambdafunction.LambdaProvisionedConcurrencyConfigTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LambdaProvisionedConcurrencyConfigTimeouts]:
        return typing.cast(typing.Optional[LambdaProvisionedConcurrencyConfigTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LambdaProvisionedConcurrencyConfigTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsLambdaAlias",
    "DataAwsLambdaAliasConfig",
    "DataAwsLambdaCodeSigningConfig",
    "DataAwsLambdaCodeSigningConfigAllowedPublishers",
    "DataAwsLambdaCodeSigningConfigConfig",
    "DataAwsLambdaCodeSigningConfigPolicies",
    "DataAwsLambdaFunction",
    "DataAwsLambdaFunctionConfig",
    "DataAwsLambdaFunctionDeadLetterConfig",
    "DataAwsLambdaFunctionEnvironment",
    "DataAwsLambdaFunctionFileSystemConfig",
    "DataAwsLambdaFunctionTracingConfig",
    "DataAwsLambdaFunctionVpcConfig",
    "DataAwsLambdaInvocation",
    "DataAwsLambdaInvocationConfig",
    "DataAwsLambdaLayerVersion",
    "DataAwsLambdaLayerVersionConfig",
    "LambdaAlias",
    "LambdaAliasConfig",
    "LambdaAliasRoutingConfig",
    "LambdaAliasRoutingConfigOutputReference",
    "LambdaCodeSigningConfig",
    "LambdaCodeSigningConfigAllowedPublishers",
    "LambdaCodeSigningConfigAllowedPublishersOutputReference",
    "LambdaCodeSigningConfigConfig",
    "LambdaCodeSigningConfigPolicies",
    "LambdaCodeSigningConfigPoliciesOutputReference",
    "LambdaEventSourceMapping",
    "LambdaEventSourceMappingConfig",
    "LambdaEventSourceMappingDestinationConfig",
    "LambdaEventSourceMappingDestinationConfigOnFailure",
    "LambdaEventSourceMappingDestinationConfigOnFailureOutputReference",
    "LambdaEventSourceMappingDestinationConfigOutputReference",
    "LambdaEventSourceMappingFilterCriteria",
    "LambdaEventSourceMappingFilterCriteriaFilter",
    "LambdaEventSourceMappingFilterCriteriaOutputReference",
    "LambdaEventSourceMappingSelfManagedEventSource",
    "LambdaEventSourceMappingSelfManagedEventSourceOutputReference",
    "LambdaEventSourceMappingSourceAccessConfiguration",
    "LambdaFunction",
    "LambdaFunctionConfig",
    "LambdaFunctionDeadLetterConfig",
    "LambdaFunctionDeadLetterConfigOutputReference",
    "LambdaFunctionEnvironment",
    "LambdaFunctionEnvironmentOutputReference",
    "LambdaFunctionEventInvokeConfig",
    "LambdaFunctionEventInvokeConfigConfig",
    "LambdaFunctionEventInvokeConfigDestinationConfig",
    "LambdaFunctionEventInvokeConfigDestinationConfigOnFailure",
    "LambdaFunctionEventInvokeConfigDestinationConfigOnFailureOutputReference",
    "LambdaFunctionEventInvokeConfigDestinationConfigOnSuccess",
    "LambdaFunctionEventInvokeConfigDestinationConfigOnSuccessOutputReference",
    "LambdaFunctionEventInvokeConfigDestinationConfigOutputReference",
    "LambdaFunctionFileSystemConfig",
    "LambdaFunctionFileSystemConfigOutputReference",
    "LambdaFunctionImageConfig",
    "LambdaFunctionImageConfigOutputReference",
    "LambdaFunctionTimeouts",
    "LambdaFunctionTimeoutsOutputReference",
    "LambdaFunctionTracingConfig",
    "LambdaFunctionTracingConfigOutputReference",
    "LambdaFunctionVpcConfig",
    "LambdaFunctionVpcConfigOutputReference",
    "LambdaLayerVersion",
    "LambdaLayerVersionConfig",
    "LambdaLayerVersionPermission",
    "LambdaLayerVersionPermissionConfig",
    "LambdaPermission",
    "LambdaPermissionConfig",
    "LambdaProvisionedConcurrencyConfig",
    "LambdaProvisionedConcurrencyConfigConfig",
    "LambdaProvisionedConcurrencyConfigTimeouts",
    "LambdaProvisionedConcurrencyConfigTimeoutsOutputReference",
]

publication.publish()
