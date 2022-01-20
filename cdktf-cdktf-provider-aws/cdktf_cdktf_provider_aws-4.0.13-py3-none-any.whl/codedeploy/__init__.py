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


class CodedeployApp(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployApp",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app aws_codedeploy_app}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        compute_platform: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app aws_codedeploy_app} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#name CodedeployApp#name}.
        :param compute_platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#compute_platform CodedeployApp#compute_platform}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#tags CodedeployApp#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#tags_all CodedeployApp#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodedeployAppConfig(
            name=name,
            compute_platform=compute_platform,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetComputePlatform")
    def reset_compute_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputePlatform", []))

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
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="githubAccountName")
    def github_account_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "githubAccountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="linkedToGithub")
    def linked_to_github(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "linkedToGithub"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computePlatformInput")
    def compute_platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computePlatformInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="computePlatform")
    def compute_platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computePlatform"))

    @compute_platform.setter
    def compute_platform(self, value: builtins.str) -> None:
        jsii.set(self, "computePlatform", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployAppConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "compute_platform": "computePlatform",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class CodedeployAppConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        compute_platform: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CodeDeploy.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#name CodedeployApp#name}.
        :param compute_platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#compute_platform CodedeployApp#compute_platform}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#tags CodedeployApp#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#tags_all CodedeployApp#tags_all}.
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
        if compute_platform is not None:
            self._values["compute_platform"] = compute_platform
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#name CodedeployApp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_platform(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#compute_platform CodedeployApp#compute_platform}.'''
        result = self._values.get("compute_platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#tags CodedeployApp#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_app#tags_all CodedeployApp#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployAppConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config aws_codedeploy_deployment_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        deployment_config_name: builtins.str,
        compute_platform: typing.Optional[builtins.str] = None,
        minimum_healthy_hosts: typing.Optional["CodedeployDeploymentConfigMinimumHealthyHosts"] = None,
        traffic_routing_config: typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfig"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config aws_codedeploy_deployment_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param deployment_config_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#deployment_config_name CodedeployDeploymentConfig#deployment_config_name}.
        :param compute_platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#compute_platform CodedeployDeploymentConfig#compute_platform}.
        :param minimum_healthy_hosts: minimum_healthy_hosts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#minimum_healthy_hosts CodedeployDeploymentConfig#minimum_healthy_hosts}
        :param traffic_routing_config: traffic_routing_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#traffic_routing_config CodedeployDeploymentConfig#traffic_routing_config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodedeployDeploymentConfigConfig(
            deployment_config_name=deployment_config_name,
            compute_platform=compute_platform,
            minimum_healthy_hosts=minimum_healthy_hosts,
            traffic_routing_config=traffic_routing_config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putMinimumHealthyHosts")
    def put_minimum_healthy_hosts(
        self,
        *,
        type: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#type CodedeployDeploymentConfig#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#value CodedeployDeploymentConfig#value}.
        '''
        value_ = CodedeployDeploymentConfigMinimumHealthyHosts(type=type, value=value)

        return typing.cast(None, jsii.invoke(self, "putMinimumHealthyHosts", [value_]))

    @jsii.member(jsii_name="putTrafficRoutingConfig")
    def put_traffic_routing_config(
        self,
        *,
        time_based_canary: typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary"] = None,
        time_based_linear: typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear"] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param time_based_canary: time_based_canary block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#time_based_canary CodedeployDeploymentConfig#time_based_canary}
        :param time_based_linear: time_based_linear block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#time_based_linear CodedeployDeploymentConfig#time_based_linear}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#type CodedeployDeploymentConfig#type}.
        '''
        value = CodedeployDeploymentConfigTrafficRoutingConfig(
            time_based_canary=time_based_canary,
            time_based_linear=time_based_linear,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putTrafficRoutingConfig", [value]))

    @jsii.member(jsii_name="resetComputePlatform")
    def reset_compute_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputePlatform", []))

    @jsii.member(jsii_name="resetMinimumHealthyHosts")
    def reset_minimum_healthy_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumHealthyHosts", []))

    @jsii.member(jsii_name="resetTrafficRoutingConfig")
    def reset_traffic_routing_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficRoutingConfig", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigId")
    def deployment_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumHealthyHosts")
    def minimum_healthy_hosts(
        self,
    ) -> "CodedeployDeploymentConfigMinimumHealthyHostsOutputReference":
        return typing.cast("CodedeployDeploymentConfigMinimumHealthyHostsOutputReference", jsii.get(self, "minimumHealthyHosts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trafficRoutingConfig")
    def traffic_routing_config(
        self,
    ) -> "CodedeployDeploymentConfigTrafficRoutingConfigOutputReference":
        return typing.cast("CodedeployDeploymentConfigTrafficRoutingConfigOutputReference", jsii.get(self, "trafficRoutingConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computePlatformInput")
    def compute_platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computePlatformInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigNameInput")
    def deployment_config_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentConfigNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumHealthyHostsInput")
    def minimum_healthy_hosts_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigMinimumHealthyHosts"]:
        return typing.cast(typing.Optional["CodedeployDeploymentConfigMinimumHealthyHosts"], jsii.get(self, "minimumHealthyHostsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trafficRoutingConfigInput")
    def traffic_routing_config_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfig"]:
        return typing.cast(typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfig"], jsii.get(self, "trafficRoutingConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computePlatform")
    def compute_platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computePlatform"))

    @compute_platform.setter
    def compute_platform(self, value: builtins.str) -> None:
        jsii.set(self, "computePlatform", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigName"))

    @deployment_config_name.setter
    def deployment_config_name(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentConfigName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "deployment_config_name": "deploymentConfigName",
        "compute_platform": "computePlatform",
        "minimum_healthy_hosts": "minimumHealthyHosts",
        "traffic_routing_config": "trafficRoutingConfig",
    },
)
class CodedeployDeploymentConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        deployment_config_name: builtins.str,
        compute_platform: typing.Optional[builtins.str] = None,
        minimum_healthy_hosts: typing.Optional["CodedeployDeploymentConfigMinimumHealthyHosts"] = None,
        traffic_routing_config: typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfig"] = None,
    ) -> None:
        '''AWS CodeDeploy.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param deployment_config_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#deployment_config_name CodedeployDeploymentConfig#deployment_config_name}.
        :param compute_platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#compute_platform CodedeployDeploymentConfig#compute_platform}.
        :param minimum_healthy_hosts: minimum_healthy_hosts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#minimum_healthy_hosts CodedeployDeploymentConfig#minimum_healthy_hosts}
        :param traffic_routing_config: traffic_routing_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#traffic_routing_config CodedeployDeploymentConfig#traffic_routing_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(minimum_healthy_hosts, dict):
            minimum_healthy_hosts = CodedeployDeploymentConfigMinimumHealthyHosts(**minimum_healthy_hosts)
        if isinstance(traffic_routing_config, dict):
            traffic_routing_config = CodedeployDeploymentConfigTrafficRoutingConfig(**traffic_routing_config)
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_config_name": deployment_config_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if compute_platform is not None:
            self._values["compute_platform"] = compute_platform
        if minimum_healthy_hosts is not None:
            self._values["minimum_healthy_hosts"] = minimum_healthy_hosts
        if traffic_routing_config is not None:
            self._values["traffic_routing_config"] = traffic_routing_config

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
    def deployment_config_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#deployment_config_name CodedeployDeploymentConfig#deployment_config_name}.'''
        result = self._values.get("deployment_config_name")
        assert result is not None, "Required property 'deployment_config_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_platform(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#compute_platform CodedeployDeploymentConfig#compute_platform}.'''
        result = self._values.get("compute_platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum_healthy_hosts(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigMinimumHealthyHosts"]:
        '''minimum_healthy_hosts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#minimum_healthy_hosts CodedeployDeploymentConfig#minimum_healthy_hosts}
        '''
        result = self._values.get("minimum_healthy_hosts")
        return typing.cast(typing.Optional["CodedeployDeploymentConfigMinimumHealthyHosts"], result)

    @builtins.property
    def traffic_routing_config(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfig"]:
        '''traffic_routing_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#traffic_routing_config CodedeployDeploymentConfig#traffic_routing_config}
        '''
        result = self._values.get("traffic_routing_config")
        return typing.cast(typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigMinimumHealthyHosts",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "value": "value"},
)
class CodedeployDeploymentConfigMinimumHealthyHosts:
    def __init__(
        self,
        *,
        type: typing.Optional[builtins.str] = None,
        value: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#type CodedeployDeploymentConfig#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#value CodedeployDeploymentConfig#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if type is not None:
            self._values["type"] = type
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#type CodedeployDeploymentConfig#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#value CodedeployDeploymentConfig#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentConfigMinimumHealthyHosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentConfigMinimumHealthyHostsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigMinimumHealthyHostsOutputReference",
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

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentConfigMinimumHealthyHosts]:
        return typing.cast(typing.Optional[CodedeployDeploymentConfigMinimumHealthyHosts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentConfigMinimumHealthyHosts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigTrafficRoutingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "time_based_canary": "timeBasedCanary",
        "time_based_linear": "timeBasedLinear",
        "type": "type",
    },
)
class CodedeployDeploymentConfigTrafficRoutingConfig:
    def __init__(
        self,
        *,
        time_based_canary: typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary"] = None,
        time_based_linear: typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear"] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param time_based_canary: time_based_canary block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#time_based_canary CodedeployDeploymentConfig#time_based_canary}
        :param time_based_linear: time_based_linear block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#time_based_linear CodedeployDeploymentConfig#time_based_linear}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#type CodedeployDeploymentConfig#type}.
        '''
        if isinstance(time_based_canary, dict):
            time_based_canary = CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary(**time_based_canary)
        if isinstance(time_based_linear, dict):
            time_based_linear = CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear(**time_based_linear)
        self._values: typing.Dict[str, typing.Any] = {}
        if time_based_canary is not None:
            self._values["time_based_canary"] = time_based_canary
        if time_based_linear is not None:
            self._values["time_based_linear"] = time_based_linear
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def time_based_canary(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary"]:
        '''time_based_canary block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#time_based_canary CodedeployDeploymentConfig#time_based_canary}
        '''
        result = self._values.get("time_based_canary")
        return typing.cast(typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary"], result)

    @builtins.property
    def time_based_linear(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear"]:
        '''time_based_linear block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#time_based_linear CodedeployDeploymentConfig#time_based_linear}
        '''
        result = self._values.get("time_based_linear")
        return typing.cast(typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#type CodedeployDeploymentConfig#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentConfigTrafficRoutingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentConfigTrafficRoutingConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigTrafficRoutingConfigOutputReference",
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

    @jsii.member(jsii_name="putTimeBasedCanary")
    def put_time_based_canary(
        self,
        *,
        interval: typing.Optional[jsii.Number] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#interval CodedeployDeploymentConfig#interval}.
        :param percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#percentage CodedeployDeploymentConfig#percentage}.
        '''
        value = CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary(
            interval=interval, percentage=percentage
        )

        return typing.cast(None, jsii.invoke(self, "putTimeBasedCanary", [value]))

    @jsii.member(jsii_name="putTimeBasedLinear")
    def put_time_based_linear(
        self,
        *,
        interval: typing.Optional[jsii.Number] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#interval CodedeployDeploymentConfig#interval}.
        :param percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#percentage CodedeployDeploymentConfig#percentage}.
        '''
        value = CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear(
            interval=interval, percentage=percentage
        )

        return typing.cast(None, jsii.invoke(self, "putTimeBasedLinear", [value]))

    @jsii.member(jsii_name="resetTimeBasedCanary")
    def reset_time_based_canary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeBasedCanary", []))

    @jsii.member(jsii_name="resetTimeBasedLinear")
    def reset_time_based_linear(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeBasedLinear", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeBasedCanary")
    def time_based_canary(
        self,
    ) -> "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanaryOutputReference":
        return typing.cast("CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanaryOutputReference", jsii.get(self, "timeBasedCanary"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeBasedLinear")
    def time_based_linear(
        self,
    ) -> "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinearOutputReference":
        return typing.cast("CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinearOutputReference", jsii.get(self, "timeBasedLinear"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeBasedCanaryInput")
    def time_based_canary_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary"]:
        return typing.cast(typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary"], jsii.get(self, "timeBasedCanaryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeBasedLinearInput")
    def time_based_linear_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear"]:
        return typing.cast(typing.Optional["CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear"], jsii.get(self, "timeBasedLinearInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfig]:
        return typing.cast(typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "percentage": "percentage"},
)
class CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary:
    def __init__(
        self,
        *,
        interval: typing.Optional[jsii.Number] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#interval CodedeployDeploymentConfig#interval}.
        :param percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#percentage CodedeployDeploymentConfig#percentage}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if interval is not None:
            self._values["interval"] = interval
        if percentage is not None:
            self._values["percentage"] = percentage

    @builtins.property
    def interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#interval CodedeployDeploymentConfig#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#percentage CodedeployDeploymentConfig#percentage}.'''
        result = self._values.get("percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanaryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanaryOutputReference",
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

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetPercentage")
    def reset_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPercentage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="percentageInput")
    def percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "percentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="percentage")
    def percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "percentage"))

    @percentage.setter
    def percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "percentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary]:
        return typing.cast(typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "percentage": "percentage"},
)
class CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear:
    def __init__(
        self,
        *,
        interval: typing.Optional[jsii.Number] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#interval CodedeployDeploymentConfig#interval}.
        :param percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#percentage CodedeployDeploymentConfig#percentage}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if interval is not None:
            self._values["interval"] = interval
        if percentage is not None:
            self._values["percentage"] = percentage

    @builtins.property
    def interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#interval CodedeployDeploymentConfig#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_config#percentage CodedeployDeploymentConfig#percentage}.'''
        result = self._values.get("percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinearOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinearOutputReference",
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

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetPercentage")
    def reset_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPercentage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="percentageInput")
    def percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "percentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: jsii.Number) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="percentage")
    def percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "percentage"))

    @percentage.setter
    def percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "percentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear]:
        return typing.cast(typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CodedeployDeploymentGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group aws_codedeploy_deployment_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_name: builtins.str,
        deployment_group_name: builtins.str,
        service_role_arn: builtins.str,
        alarm_configuration: typing.Optional["CodedeployDeploymentGroupAlarmConfiguration"] = None,
        auto_rollback_configuration: typing.Optional["CodedeployDeploymentGroupAutoRollbackConfiguration"] = None,
        autoscaling_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        blue_green_deployment_config: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfig"] = None,
        deployment_config_name: typing.Optional[builtins.str] = None,
        deployment_style: typing.Optional["CodedeployDeploymentGroupDeploymentStyle"] = None,
        ec2_tag_filter: typing.Optional[typing.Sequence["CodedeployDeploymentGroupEc2TagFilter"]] = None,
        ec2_tag_set: typing.Optional[typing.Sequence["CodedeployDeploymentGroupEc2TagSet"]] = None,
        ecs_service: typing.Optional["CodedeployDeploymentGroupEcsService"] = None,
        load_balancer_info: typing.Optional["CodedeployDeploymentGroupLoadBalancerInfo"] = None,
        on_premises_instance_tag_filter: typing.Optional[typing.Sequence["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        trigger_configuration: typing.Optional[typing.Sequence["CodedeployDeploymentGroupTriggerConfiguration"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group aws_codedeploy_deployment_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#app_name CodedeployDeploymentGroup#app_name}.
        :param deployment_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_group_name CodedeployDeploymentGroup#deployment_group_name}.
        :param service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#service_role_arn CodedeployDeploymentGroup#service_role_arn}.
        :param alarm_configuration: alarm_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#alarm_configuration CodedeployDeploymentGroup#alarm_configuration}
        :param auto_rollback_configuration: auto_rollback_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#auto_rollback_configuration CodedeployDeploymentGroup#auto_rollback_configuration}
        :param autoscaling_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#autoscaling_groups CodedeployDeploymentGroup#autoscaling_groups}.
        :param blue_green_deployment_config: blue_green_deployment_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#blue_green_deployment_config CodedeployDeploymentGroup#blue_green_deployment_config}
        :param deployment_config_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_config_name CodedeployDeploymentGroup#deployment_config_name}.
        :param deployment_style: deployment_style block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_style CodedeployDeploymentGroup#deployment_style}
        :param ec2_tag_filter: ec2_tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_filter CodedeployDeploymentGroup#ec2_tag_filter}
        :param ec2_tag_set: ec2_tag_set block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_set CodedeployDeploymentGroup#ec2_tag_set}
        :param ecs_service: ecs_service block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ecs_service CodedeployDeploymentGroup#ecs_service}
        :param load_balancer_info: load_balancer_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#load_balancer_info CodedeployDeploymentGroup#load_balancer_info}
        :param on_premises_instance_tag_filter: on_premises_instance_tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#on_premises_instance_tag_filter CodedeployDeploymentGroup#on_premises_instance_tag_filter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#tags CodedeployDeploymentGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#tags_all CodedeployDeploymentGroup#tags_all}.
        :param trigger_configuration: trigger_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_configuration CodedeployDeploymentGroup#trigger_configuration}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CodedeployDeploymentGroupConfig(
            app_name=app_name,
            deployment_group_name=deployment_group_name,
            service_role_arn=service_role_arn,
            alarm_configuration=alarm_configuration,
            auto_rollback_configuration=auto_rollback_configuration,
            autoscaling_groups=autoscaling_groups,
            blue_green_deployment_config=blue_green_deployment_config,
            deployment_config_name=deployment_config_name,
            deployment_style=deployment_style,
            ec2_tag_filter=ec2_tag_filter,
            ec2_tag_set=ec2_tag_set,
            ecs_service=ecs_service,
            load_balancer_info=load_balancer_info,
            on_premises_instance_tag_filter=on_premises_instance_tag_filter,
            tags=tags,
            tags_all=tags_all,
            trigger_configuration=trigger_configuration,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAlarmConfiguration")
    def put_alarm_configuration(
        self,
        *,
        alarms: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_poll_alarm_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param alarms: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#alarms CodedeployDeploymentGroup#alarms}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#enabled CodedeployDeploymentGroup#enabled}.
        :param ignore_poll_alarm_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ignore_poll_alarm_failure CodedeployDeploymentGroup#ignore_poll_alarm_failure}.
        '''
        value = CodedeployDeploymentGroupAlarmConfiguration(
            alarms=alarms,
            enabled=enabled,
            ignore_poll_alarm_failure=ignore_poll_alarm_failure,
        )

        return typing.cast(None, jsii.invoke(self, "putAlarmConfiguration", [value]))

    @jsii.member(jsii_name="putAutoRollbackConfiguration")
    def put_auto_rollback_configuration(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        events: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#enabled CodedeployDeploymentGroup#enabled}.
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#events CodedeployDeploymentGroup#events}.
        '''
        value = CodedeployDeploymentGroupAutoRollbackConfiguration(
            enabled=enabled, events=events
        )

        return typing.cast(None, jsii.invoke(self, "putAutoRollbackConfiguration", [value]))

    @jsii.member(jsii_name="putBlueGreenDeploymentConfig")
    def put_blue_green_deployment_config(
        self,
        *,
        deployment_ready_option: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption"] = None,
        green_fleet_provisioning_option: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption"] = None,
        terminate_blue_instances_on_deployment_success: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess"] = None,
    ) -> None:
        '''
        :param deployment_ready_option: deployment_ready_option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_ready_option CodedeployDeploymentGroup#deployment_ready_option}
        :param green_fleet_provisioning_option: green_fleet_provisioning_option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#green_fleet_provisioning_option CodedeployDeploymentGroup#green_fleet_provisioning_option}
        :param terminate_blue_instances_on_deployment_success: terminate_blue_instances_on_deployment_success block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#terminate_blue_instances_on_deployment_success CodedeployDeploymentGroup#terminate_blue_instances_on_deployment_success}
        '''
        value = CodedeployDeploymentGroupBlueGreenDeploymentConfig(
            deployment_ready_option=deployment_ready_option,
            green_fleet_provisioning_option=green_fleet_provisioning_option,
            terminate_blue_instances_on_deployment_success=terminate_blue_instances_on_deployment_success,
        )

        return typing.cast(None, jsii.invoke(self, "putBlueGreenDeploymentConfig", [value]))

    @jsii.member(jsii_name="putDeploymentStyle")
    def put_deployment_style(
        self,
        *,
        deployment_option: typing.Optional[builtins.str] = None,
        deployment_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_option CodedeployDeploymentGroup#deployment_option}.
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_type CodedeployDeploymentGroup#deployment_type}.
        '''
        value = CodedeployDeploymentGroupDeploymentStyle(
            deployment_option=deployment_option, deployment_type=deployment_type
        )

        return typing.cast(None, jsii.invoke(self, "putDeploymentStyle", [value]))

    @jsii.member(jsii_name="putEcsService")
    def put_ecs_service(
        self,
        *,
        cluster_name: builtins.str,
        service_name: builtins.str,
    ) -> None:
        '''
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#cluster_name CodedeployDeploymentGroup#cluster_name}.
        :param service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#service_name CodedeployDeploymentGroup#service_name}.
        '''
        value = CodedeployDeploymentGroupEcsService(
            cluster_name=cluster_name, service_name=service_name
        )

        return typing.cast(None, jsii.invoke(self, "putEcsService", [value]))

    @jsii.member(jsii_name="putLoadBalancerInfo")
    def put_load_balancer_info(
        self,
        *,
        elb_info: typing.Optional[typing.Sequence["CodedeployDeploymentGroupLoadBalancerInfoElbInfo"]] = None,
        target_group_info: typing.Optional[typing.Sequence["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]] = None,
        target_group_pair_info: typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo"] = None,
    ) -> None:
        '''
        :param elb_info: elb_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#elb_info CodedeployDeploymentGroup#elb_info}
        :param target_group_info: target_group_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group_info CodedeployDeploymentGroup#target_group_info}
        :param target_group_pair_info: target_group_pair_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group_pair_info CodedeployDeploymentGroup#target_group_pair_info}
        '''
        value = CodedeployDeploymentGroupLoadBalancerInfo(
            elb_info=elb_info,
            target_group_info=target_group_info,
            target_group_pair_info=target_group_pair_info,
        )

        return typing.cast(None, jsii.invoke(self, "putLoadBalancerInfo", [value]))

    @jsii.member(jsii_name="resetAlarmConfiguration")
    def reset_alarm_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlarmConfiguration", []))

    @jsii.member(jsii_name="resetAutoRollbackConfiguration")
    def reset_auto_rollback_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRollbackConfiguration", []))

    @jsii.member(jsii_name="resetAutoscalingGroups")
    def reset_autoscaling_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingGroups", []))

    @jsii.member(jsii_name="resetBlueGreenDeploymentConfig")
    def reset_blue_green_deployment_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlueGreenDeploymentConfig", []))

    @jsii.member(jsii_name="resetDeploymentConfigName")
    def reset_deployment_config_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentConfigName", []))

    @jsii.member(jsii_name="resetDeploymentStyle")
    def reset_deployment_style(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentStyle", []))

    @jsii.member(jsii_name="resetEc2TagFilter")
    def reset_ec2_tag_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2TagFilter", []))

    @jsii.member(jsii_name="resetEc2TagSet")
    def reset_ec2_tag_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2TagSet", []))

    @jsii.member(jsii_name="resetEcsService")
    def reset_ecs_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEcsService", []))

    @jsii.member(jsii_name="resetLoadBalancerInfo")
    def reset_load_balancer_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancerInfo", []))

    @jsii.member(jsii_name="resetOnPremisesInstanceTagFilter")
    def reset_on_premises_instance_tag_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnPremisesInstanceTagFilter", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTriggerConfiguration")
    def reset_trigger_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggerConfiguration", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmConfiguration")
    def alarm_configuration(
        self,
    ) -> "CodedeployDeploymentGroupAlarmConfigurationOutputReference":
        return typing.cast("CodedeployDeploymentGroupAlarmConfigurationOutputReference", jsii.get(self, "alarmConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoRollbackConfiguration")
    def auto_rollback_configuration(
        self,
    ) -> "CodedeployDeploymentGroupAutoRollbackConfigurationOutputReference":
        return typing.cast("CodedeployDeploymentGroupAutoRollbackConfigurationOutputReference", jsii.get(self, "autoRollbackConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blueGreenDeploymentConfig")
    def blue_green_deployment_config(
        self,
    ) -> "CodedeployDeploymentGroupBlueGreenDeploymentConfigOutputReference":
        return typing.cast("CodedeployDeploymentGroupBlueGreenDeploymentConfigOutputReference", jsii.get(self, "blueGreenDeploymentConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computePlatform")
    def compute_platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computePlatform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupId")
    def deployment_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentStyle")
    def deployment_style(
        self,
    ) -> "CodedeployDeploymentGroupDeploymentStyleOutputReference":
        return typing.cast("CodedeployDeploymentGroupDeploymentStyleOutputReference", jsii.get(self, "deploymentStyle"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsService")
    def ecs_service(self) -> "CodedeployDeploymentGroupEcsServiceOutputReference":
        return typing.cast("CodedeployDeploymentGroupEcsServiceOutputReference", jsii.get(self, "ecsService"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadBalancerInfo")
    def load_balancer_info(
        self,
    ) -> "CodedeployDeploymentGroupLoadBalancerInfoOutputReference":
        return typing.cast("CodedeployDeploymentGroupLoadBalancerInfoOutputReference", jsii.get(self, "loadBalancerInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmConfigurationInput")
    def alarm_configuration_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupAlarmConfiguration"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupAlarmConfiguration"], jsii.get(self, "alarmConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appNameInput")
    def app_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoRollbackConfigurationInput")
    def auto_rollback_configuration_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupAutoRollbackConfiguration"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupAutoRollbackConfiguration"], jsii.get(self, "autoRollbackConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingGroupsInput")
    def autoscaling_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "autoscalingGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blueGreenDeploymentConfigInput")
    def blue_green_deployment_config_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfig"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfig"], jsii.get(self, "blueGreenDeploymentConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigNameInput")
    def deployment_config_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentConfigNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupNameInput")
    def deployment_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentStyleInput")
    def deployment_style_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupDeploymentStyle"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupDeploymentStyle"], jsii.get(self, "deploymentStyleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2TagFilterInput")
    def ec2_tag_filter_input(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagFilter"]]:
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagFilter"]], jsii.get(self, "ec2TagFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2TagSetInput")
    def ec2_tag_set_input(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagSet"]]:
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagSet"]], jsii.get(self, "ec2TagSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsServiceInput")
    def ecs_service_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupEcsService"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupEcsService"], jsii.get(self, "ecsServiceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadBalancerInfoInput")
    def load_balancer_info_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfo"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfo"], jsii.get(self, "loadBalancerInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onPremisesInstanceTagFilterInput")
    def on_premises_instance_tag_filter_input(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]]:
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]], jsii.get(self, "onPremisesInstanceTagFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArnInput")
    def service_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleArnInput"))

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
    @jsii.member(jsii_name="triggerConfigurationInput")
    def trigger_configuration_input(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupTriggerConfiguration"]]:
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupTriggerConfiguration"]], jsii.get(self, "triggerConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appName")
    def app_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appName"))

    @app_name.setter
    def app_name(self, value: builtins.str) -> None:
        jsii.set(self, "appName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingGroups")
    def autoscaling_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "autoscalingGroups"))

    @autoscaling_groups.setter
    def autoscaling_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "autoscalingGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigName"))

    @deployment_config_name.setter
    def deployment_config_name(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentConfigName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupName"))

    @deployment_group_name.setter
    def deployment_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2TagFilter")
    def ec2_tag_filter(self) -> typing.List["CodedeployDeploymentGroupEc2TagFilter"]:
        return typing.cast(typing.List["CodedeployDeploymentGroupEc2TagFilter"], jsii.get(self, "ec2TagFilter"))

    @ec2_tag_filter.setter
    def ec2_tag_filter(
        self,
        value: typing.List["CodedeployDeploymentGroupEc2TagFilter"],
    ) -> None:
        jsii.set(self, "ec2TagFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2TagSet")
    def ec2_tag_set(self) -> typing.List["CodedeployDeploymentGroupEc2TagSet"]:
        return typing.cast(typing.List["CodedeployDeploymentGroupEc2TagSet"], jsii.get(self, "ec2TagSet"))

    @ec2_tag_set.setter
    def ec2_tag_set(
        self,
        value: typing.List["CodedeployDeploymentGroupEc2TagSet"],
    ) -> None:
        jsii.set(self, "ec2TagSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onPremisesInstanceTagFilter")
    def on_premises_instance_tag_filter(
        self,
    ) -> typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]:
        return typing.cast(typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"], jsii.get(self, "onPremisesInstanceTagFilter"))

    @on_premises_instance_tag_filter.setter
    def on_premises_instance_tag_filter(
        self,
        value: typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"],
    ) -> None:
        jsii.set(self, "onPremisesInstanceTagFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRoleArn"))

    @service_role_arn.setter
    def service_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceRoleArn", value)

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
    @jsii.member(jsii_name="triggerConfiguration")
    def trigger_configuration(
        self,
    ) -> typing.List["CodedeployDeploymentGroupTriggerConfiguration"]:
        return typing.cast(typing.List["CodedeployDeploymentGroupTriggerConfiguration"], jsii.get(self, "triggerConfiguration"))

    @trigger_configuration.setter
    def trigger_configuration(
        self,
        value: typing.List["CodedeployDeploymentGroupTriggerConfiguration"],
    ) -> None:
        jsii.set(self, "triggerConfiguration", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupAlarmConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "alarms": "alarms",
        "enabled": "enabled",
        "ignore_poll_alarm_failure": "ignorePollAlarmFailure",
    },
)
class CodedeployDeploymentGroupAlarmConfiguration:
    def __init__(
        self,
        *,
        alarms: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_poll_alarm_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param alarms: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#alarms CodedeployDeploymentGroup#alarms}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#enabled CodedeployDeploymentGroup#enabled}.
        :param ignore_poll_alarm_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ignore_poll_alarm_failure CodedeployDeploymentGroup#ignore_poll_alarm_failure}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alarms is not None:
            self._values["alarms"] = alarms
        if enabled is not None:
            self._values["enabled"] = enabled
        if ignore_poll_alarm_failure is not None:
            self._values["ignore_poll_alarm_failure"] = ignore_poll_alarm_failure

    @builtins.property
    def alarms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#alarms CodedeployDeploymentGroup#alarms}.'''
        result = self._values.get("alarms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#enabled CodedeployDeploymentGroup#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ignore_poll_alarm_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ignore_poll_alarm_failure CodedeployDeploymentGroup#ignore_poll_alarm_failure}.'''
        result = self._values.get("ignore_poll_alarm_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupAlarmConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupAlarmConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupAlarmConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetAlarms")
    def reset_alarms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlarms", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetIgnorePollAlarmFailure")
    def reset_ignore_poll_alarm_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnorePollAlarmFailure", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmsInput")
    def alarms_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "alarmsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePollAlarmFailureInput")
    def ignore_poll_alarm_failure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignorePollAlarmFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarms")
    def alarms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "alarms"))

    @alarms.setter
    def alarms(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "alarms", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePollAlarmFailure")
    def ignore_poll_alarm_failure(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignorePollAlarmFailure"))

    @ignore_poll_alarm_failure.setter
    def ignore_poll_alarm_failure(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignorePollAlarmFailure", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupAlarmConfiguration]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupAlarmConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupAlarmConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupAutoRollbackConfiguration",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "events": "events"},
)
class CodedeployDeploymentGroupAutoRollbackConfiguration:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        events: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#enabled CodedeployDeploymentGroup#enabled}.
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#events CodedeployDeploymentGroup#events}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if events is not None:
            self._values["events"] = events

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#enabled CodedeployDeploymentGroup#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def events(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#events CodedeployDeploymentGroup#events}.'''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupAutoRollbackConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupAutoRollbackConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupAutoRollbackConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEvents")
    def reset_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvents", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventsInput")
    def events_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="events")
    def events(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "events"))

    @events.setter
    def events(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "events", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupAutoRollbackConfiguration]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupAutoRollbackConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupAutoRollbackConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfig",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_ready_option": "deploymentReadyOption",
        "green_fleet_provisioning_option": "greenFleetProvisioningOption",
        "terminate_blue_instances_on_deployment_success": "terminateBlueInstancesOnDeploymentSuccess",
    },
)
class CodedeployDeploymentGroupBlueGreenDeploymentConfig:
    def __init__(
        self,
        *,
        deployment_ready_option: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption"] = None,
        green_fleet_provisioning_option: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption"] = None,
        terminate_blue_instances_on_deployment_success: typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess"] = None,
    ) -> None:
        '''
        :param deployment_ready_option: deployment_ready_option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_ready_option CodedeployDeploymentGroup#deployment_ready_option}
        :param green_fleet_provisioning_option: green_fleet_provisioning_option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#green_fleet_provisioning_option CodedeployDeploymentGroup#green_fleet_provisioning_option}
        :param terminate_blue_instances_on_deployment_success: terminate_blue_instances_on_deployment_success block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#terminate_blue_instances_on_deployment_success CodedeployDeploymentGroup#terminate_blue_instances_on_deployment_success}
        '''
        if isinstance(deployment_ready_option, dict):
            deployment_ready_option = CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption(**deployment_ready_option)
        if isinstance(green_fleet_provisioning_option, dict):
            green_fleet_provisioning_option = CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption(**green_fleet_provisioning_option)
        if isinstance(terminate_blue_instances_on_deployment_success, dict):
            terminate_blue_instances_on_deployment_success = CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess(**terminate_blue_instances_on_deployment_success)
        self._values: typing.Dict[str, typing.Any] = {}
        if deployment_ready_option is not None:
            self._values["deployment_ready_option"] = deployment_ready_option
        if green_fleet_provisioning_option is not None:
            self._values["green_fleet_provisioning_option"] = green_fleet_provisioning_option
        if terminate_blue_instances_on_deployment_success is not None:
            self._values["terminate_blue_instances_on_deployment_success"] = terminate_blue_instances_on_deployment_success

    @builtins.property
    def deployment_ready_option(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption"]:
        '''deployment_ready_option block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_ready_option CodedeployDeploymentGroup#deployment_ready_option}
        '''
        result = self._values.get("deployment_ready_option")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption"], result)

    @builtins.property
    def green_fleet_provisioning_option(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption"]:
        '''green_fleet_provisioning_option block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#green_fleet_provisioning_option CodedeployDeploymentGroup#green_fleet_provisioning_option}
        '''
        result = self._values.get("green_fleet_provisioning_option")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption"], result)

    @builtins.property
    def terminate_blue_instances_on_deployment_success(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess"]:
        '''terminate_blue_instances_on_deployment_success block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#terminate_blue_instances_on_deployment_success CodedeployDeploymentGroup#terminate_blue_instances_on_deployment_success}
        '''
        result = self._values.get("terminate_blue_instances_on_deployment_success")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupBlueGreenDeploymentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption",
    jsii_struct_bases=[],
    name_mapping={
        "action_on_timeout": "actionOnTimeout",
        "wait_time_in_minutes": "waitTimeInMinutes",
    },
)
class CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption:
    def __init__(
        self,
        *,
        action_on_timeout: typing.Optional[builtins.str] = None,
        wait_time_in_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param action_on_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action_on_timeout CodedeployDeploymentGroup#action_on_timeout}.
        :param wait_time_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#wait_time_in_minutes CodedeployDeploymentGroup#wait_time_in_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if action_on_timeout is not None:
            self._values["action_on_timeout"] = action_on_timeout
        if wait_time_in_minutes is not None:
            self._values["wait_time_in_minutes"] = wait_time_in_minutes

    @builtins.property
    def action_on_timeout(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action_on_timeout CodedeployDeploymentGroup#action_on_timeout}.'''
        result = self._values.get("action_on_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wait_time_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#wait_time_in_minutes CodedeployDeploymentGroup#wait_time_in_minutes}.'''
        result = self._values.get("wait_time_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOptionOutputReference",
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

    @jsii.member(jsii_name="resetActionOnTimeout")
    def reset_action_on_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionOnTimeout", []))

    @jsii.member(jsii_name="resetWaitTimeInMinutes")
    def reset_wait_time_in_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitTimeInMinutes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionOnTimeoutInput")
    def action_on_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionOnTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitTimeInMinutesInput")
    def wait_time_in_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitTimeInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionOnTimeout")
    def action_on_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionOnTimeout"))

    @action_on_timeout.setter
    def action_on_timeout(self, value: builtins.str) -> None:
        jsii.set(self, "actionOnTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitTimeInMinutes")
    def wait_time_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitTimeInMinutes"))

    @wait_time_in_minutes.setter
    def wait_time_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "waitTimeInMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption",
    jsii_struct_bases=[],
    name_mapping={"action": "action"},
)
class CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption:
    def __init__(self, *, action: typing.Optional[builtins.str] = None) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action CodedeployDeploymentGroup#action}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action CodedeployDeploymentGroup#action}.'''
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOptionOutputReference",
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

    @jsii.member(jsii_name="resetAction")
    def reset_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CodedeployDeploymentGroupBlueGreenDeploymentConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigOutputReference",
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

    @jsii.member(jsii_name="putDeploymentReadyOption")
    def put_deployment_ready_option(
        self,
        *,
        action_on_timeout: typing.Optional[builtins.str] = None,
        wait_time_in_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param action_on_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action_on_timeout CodedeployDeploymentGroup#action_on_timeout}.
        :param wait_time_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#wait_time_in_minutes CodedeployDeploymentGroup#wait_time_in_minutes}.
        '''
        value = CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption(
            action_on_timeout=action_on_timeout,
            wait_time_in_minutes=wait_time_in_minutes,
        )

        return typing.cast(None, jsii.invoke(self, "putDeploymentReadyOption", [value]))

    @jsii.member(jsii_name="putGreenFleetProvisioningOption")
    def put_green_fleet_provisioning_option(
        self,
        *,
        action: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action CodedeployDeploymentGroup#action}.
        '''
        value = CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption(
            action=action
        )

        return typing.cast(None, jsii.invoke(self, "putGreenFleetProvisioningOption", [value]))

    @jsii.member(jsii_name="putTerminateBlueInstancesOnDeploymentSuccess")
    def put_terminate_blue_instances_on_deployment_success(
        self,
        *,
        action: typing.Optional[builtins.str] = None,
        termination_wait_time_in_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action CodedeployDeploymentGroup#action}.
        :param termination_wait_time_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#termination_wait_time_in_minutes CodedeployDeploymentGroup#termination_wait_time_in_minutes}.
        '''
        value = CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess(
            action=action,
            termination_wait_time_in_minutes=termination_wait_time_in_minutes,
        )

        return typing.cast(None, jsii.invoke(self, "putTerminateBlueInstancesOnDeploymentSuccess", [value]))

    @jsii.member(jsii_name="resetDeploymentReadyOption")
    def reset_deployment_ready_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentReadyOption", []))

    @jsii.member(jsii_name="resetGreenFleetProvisioningOption")
    def reset_green_fleet_provisioning_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGreenFleetProvisioningOption", []))

    @jsii.member(jsii_name="resetTerminateBlueInstancesOnDeploymentSuccess")
    def reset_terminate_blue_instances_on_deployment_success(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminateBlueInstancesOnDeploymentSuccess", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentReadyOption")
    def deployment_ready_option(
        self,
    ) -> CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOptionOutputReference:
        return typing.cast(CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOptionOutputReference, jsii.get(self, "deploymentReadyOption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="greenFleetProvisioningOption")
    def green_fleet_provisioning_option(
        self,
    ) -> CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOptionOutputReference:
        return typing.cast(CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOptionOutputReference, jsii.get(self, "greenFleetProvisioningOption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminateBlueInstancesOnDeploymentSuccess")
    def terminate_blue_instances_on_deployment_success(
        self,
    ) -> "CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccessOutputReference":
        return typing.cast("CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccessOutputReference", jsii.get(self, "terminateBlueInstancesOnDeploymentSuccess"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentReadyOptionInput")
    def deployment_ready_option_input(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption], jsii.get(self, "deploymentReadyOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="greenFleetProvisioningOptionInput")
    def green_fleet_provisioning_option_input(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption], jsii.get(self, "greenFleetProvisioningOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminateBlueInstancesOnDeploymentSuccessInput")
    def terminate_blue_instances_on_deployment_success_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess"], jsii.get(self, "terminateBlueInstancesOnDeploymentSuccessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfig]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "termination_wait_time_in_minutes": "terminationWaitTimeInMinutes",
    },
)
class CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess:
    def __init__(
        self,
        *,
        action: typing.Optional[builtins.str] = None,
        termination_wait_time_in_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action CodedeployDeploymentGroup#action}.
        :param termination_wait_time_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#termination_wait_time_in_minutes CodedeployDeploymentGroup#termination_wait_time_in_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action
        if termination_wait_time_in_minutes is not None:
            self._values["termination_wait_time_in_minutes"] = termination_wait_time_in_minutes

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#action CodedeployDeploymentGroup#action}.'''
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def termination_wait_time_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#termination_wait_time_in_minutes CodedeployDeploymentGroup#termination_wait_time_in_minutes}.'''
        result = self._values.get("termination_wait_time_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccessOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccessOutputReference",
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

    @jsii.member(jsii_name="resetAction")
    def reset_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAction", []))

    @jsii.member(jsii_name="resetTerminationWaitTimeInMinutes")
    def reset_termination_wait_time_in_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationWaitTimeInMinutes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminationWaitTimeInMinutesInput")
    def termination_wait_time_in_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "terminationWaitTimeInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminationWaitTimeInMinutes")
    def termination_wait_time_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "terminationWaitTimeInMinutes"))

    @termination_wait_time_in_minutes.setter
    def termination_wait_time_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "terminationWaitTimeInMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "app_name": "appName",
        "deployment_group_name": "deploymentGroupName",
        "service_role_arn": "serviceRoleArn",
        "alarm_configuration": "alarmConfiguration",
        "auto_rollback_configuration": "autoRollbackConfiguration",
        "autoscaling_groups": "autoscalingGroups",
        "blue_green_deployment_config": "blueGreenDeploymentConfig",
        "deployment_config_name": "deploymentConfigName",
        "deployment_style": "deploymentStyle",
        "ec2_tag_filter": "ec2TagFilter",
        "ec2_tag_set": "ec2TagSet",
        "ecs_service": "ecsService",
        "load_balancer_info": "loadBalancerInfo",
        "on_premises_instance_tag_filter": "onPremisesInstanceTagFilter",
        "tags": "tags",
        "tags_all": "tagsAll",
        "trigger_configuration": "triggerConfiguration",
    },
)
class CodedeployDeploymentGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        app_name: builtins.str,
        deployment_group_name: builtins.str,
        service_role_arn: builtins.str,
        alarm_configuration: typing.Optional[CodedeployDeploymentGroupAlarmConfiguration] = None,
        auto_rollback_configuration: typing.Optional[CodedeployDeploymentGroupAutoRollbackConfiguration] = None,
        autoscaling_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        blue_green_deployment_config: typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfig] = None,
        deployment_config_name: typing.Optional[builtins.str] = None,
        deployment_style: typing.Optional["CodedeployDeploymentGroupDeploymentStyle"] = None,
        ec2_tag_filter: typing.Optional[typing.Sequence["CodedeployDeploymentGroupEc2TagFilter"]] = None,
        ec2_tag_set: typing.Optional[typing.Sequence["CodedeployDeploymentGroupEc2TagSet"]] = None,
        ecs_service: typing.Optional["CodedeployDeploymentGroupEcsService"] = None,
        load_balancer_info: typing.Optional["CodedeployDeploymentGroupLoadBalancerInfo"] = None,
        on_premises_instance_tag_filter: typing.Optional[typing.Sequence["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        trigger_configuration: typing.Optional[typing.Sequence["CodedeployDeploymentGroupTriggerConfiguration"]] = None,
    ) -> None:
        '''AWS CodeDeploy.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param app_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#app_name CodedeployDeploymentGroup#app_name}.
        :param deployment_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_group_name CodedeployDeploymentGroup#deployment_group_name}.
        :param service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#service_role_arn CodedeployDeploymentGroup#service_role_arn}.
        :param alarm_configuration: alarm_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#alarm_configuration CodedeployDeploymentGroup#alarm_configuration}
        :param auto_rollback_configuration: auto_rollback_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#auto_rollback_configuration CodedeployDeploymentGroup#auto_rollback_configuration}
        :param autoscaling_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#autoscaling_groups CodedeployDeploymentGroup#autoscaling_groups}.
        :param blue_green_deployment_config: blue_green_deployment_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#blue_green_deployment_config CodedeployDeploymentGroup#blue_green_deployment_config}
        :param deployment_config_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_config_name CodedeployDeploymentGroup#deployment_config_name}.
        :param deployment_style: deployment_style block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_style CodedeployDeploymentGroup#deployment_style}
        :param ec2_tag_filter: ec2_tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_filter CodedeployDeploymentGroup#ec2_tag_filter}
        :param ec2_tag_set: ec2_tag_set block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_set CodedeployDeploymentGroup#ec2_tag_set}
        :param ecs_service: ecs_service block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ecs_service CodedeployDeploymentGroup#ecs_service}
        :param load_balancer_info: load_balancer_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#load_balancer_info CodedeployDeploymentGroup#load_balancer_info}
        :param on_premises_instance_tag_filter: on_premises_instance_tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#on_premises_instance_tag_filter CodedeployDeploymentGroup#on_premises_instance_tag_filter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#tags CodedeployDeploymentGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#tags_all CodedeployDeploymentGroup#tags_all}.
        :param trigger_configuration: trigger_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_configuration CodedeployDeploymentGroup#trigger_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(alarm_configuration, dict):
            alarm_configuration = CodedeployDeploymentGroupAlarmConfiguration(**alarm_configuration)
        if isinstance(auto_rollback_configuration, dict):
            auto_rollback_configuration = CodedeployDeploymentGroupAutoRollbackConfiguration(**auto_rollback_configuration)
        if isinstance(blue_green_deployment_config, dict):
            blue_green_deployment_config = CodedeployDeploymentGroupBlueGreenDeploymentConfig(**blue_green_deployment_config)
        if isinstance(deployment_style, dict):
            deployment_style = CodedeployDeploymentGroupDeploymentStyle(**deployment_style)
        if isinstance(ecs_service, dict):
            ecs_service = CodedeployDeploymentGroupEcsService(**ecs_service)
        if isinstance(load_balancer_info, dict):
            load_balancer_info = CodedeployDeploymentGroupLoadBalancerInfo(**load_balancer_info)
        self._values: typing.Dict[str, typing.Any] = {
            "app_name": app_name,
            "deployment_group_name": deployment_group_name,
            "service_role_arn": service_role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if alarm_configuration is not None:
            self._values["alarm_configuration"] = alarm_configuration
        if auto_rollback_configuration is not None:
            self._values["auto_rollback_configuration"] = auto_rollback_configuration
        if autoscaling_groups is not None:
            self._values["autoscaling_groups"] = autoscaling_groups
        if blue_green_deployment_config is not None:
            self._values["blue_green_deployment_config"] = blue_green_deployment_config
        if deployment_config_name is not None:
            self._values["deployment_config_name"] = deployment_config_name
        if deployment_style is not None:
            self._values["deployment_style"] = deployment_style
        if ec2_tag_filter is not None:
            self._values["ec2_tag_filter"] = ec2_tag_filter
        if ec2_tag_set is not None:
            self._values["ec2_tag_set"] = ec2_tag_set
        if ecs_service is not None:
            self._values["ecs_service"] = ecs_service
        if load_balancer_info is not None:
            self._values["load_balancer_info"] = load_balancer_info
        if on_premises_instance_tag_filter is not None:
            self._values["on_premises_instance_tag_filter"] = on_premises_instance_tag_filter
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if trigger_configuration is not None:
            self._values["trigger_configuration"] = trigger_configuration

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
    def app_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#app_name CodedeployDeploymentGroup#app_name}.'''
        result = self._values.get("app_name")
        assert result is not None, "Required property 'app_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deployment_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_group_name CodedeployDeploymentGroup#deployment_group_name}.'''
        result = self._values.get("deployment_group_name")
        assert result is not None, "Required property 'deployment_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#service_role_arn CodedeployDeploymentGroup#service_role_arn}.'''
        result = self._values.get("service_role_arn")
        assert result is not None, "Required property 'service_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_configuration(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupAlarmConfiguration]:
        '''alarm_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#alarm_configuration CodedeployDeploymentGroup#alarm_configuration}
        '''
        result = self._values.get("alarm_configuration")
        return typing.cast(typing.Optional[CodedeployDeploymentGroupAlarmConfiguration], result)

    @builtins.property
    def auto_rollback_configuration(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupAutoRollbackConfiguration]:
        '''auto_rollback_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#auto_rollback_configuration CodedeployDeploymentGroup#auto_rollback_configuration}
        '''
        result = self._values.get("auto_rollback_configuration")
        return typing.cast(typing.Optional[CodedeployDeploymentGroupAutoRollbackConfiguration], result)

    @builtins.property
    def autoscaling_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#autoscaling_groups CodedeployDeploymentGroup#autoscaling_groups}.'''
        result = self._values.get("autoscaling_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def blue_green_deployment_config(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfig]:
        '''blue_green_deployment_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#blue_green_deployment_config CodedeployDeploymentGroup#blue_green_deployment_config}
        '''
        result = self._values.get("blue_green_deployment_config")
        return typing.cast(typing.Optional[CodedeployDeploymentGroupBlueGreenDeploymentConfig], result)

    @builtins.property
    def deployment_config_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_config_name CodedeployDeploymentGroup#deployment_config_name}.'''
        result = self._values.get("deployment_config_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_style(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupDeploymentStyle"]:
        '''deployment_style block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_style CodedeployDeploymentGroup#deployment_style}
        '''
        result = self._values.get("deployment_style")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupDeploymentStyle"], result)

    @builtins.property
    def ec2_tag_filter(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagFilter"]]:
        '''ec2_tag_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_filter CodedeployDeploymentGroup#ec2_tag_filter}
        '''
        result = self._values.get("ec2_tag_filter")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagFilter"]], result)

    @builtins.property
    def ec2_tag_set(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagSet"]]:
        '''ec2_tag_set block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_set CodedeployDeploymentGroup#ec2_tag_set}
        '''
        result = self._values.get("ec2_tag_set")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagSet"]], result)

    @builtins.property
    def ecs_service(self) -> typing.Optional["CodedeployDeploymentGroupEcsService"]:
        '''ecs_service block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ecs_service CodedeployDeploymentGroup#ecs_service}
        '''
        result = self._values.get("ecs_service")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupEcsService"], result)

    @builtins.property
    def load_balancer_info(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfo"]:
        '''load_balancer_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#load_balancer_info CodedeployDeploymentGroup#load_balancer_info}
        '''
        result = self._values.get("load_balancer_info")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfo"], result)

    @builtins.property
    def on_premises_instance_tag_filter(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]]:
        '''on_premises_instance_tag_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#on_premises_instance_tag_filter CodedeployDeploymentGroup#on_premises_instance_tag_filter}
        '''
        result = self._values.get("on_premises_instance_tag_filter")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupOnPremisesInstanceTagFilter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#tags CodedeployDeploymentGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#tags_all CodedeployDeploymentGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def trigger_configuration(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupTriggerConfiguration"]]:
        '''trigger_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_configuration CodedeployDeploymentGroup#trigger_configuration}
        '''
        result = self._values.get("trigger_configuration")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupTriggerConfiguration"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupDeploymentStyle",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_option": "deploymentOption",
        "deployment_type": "deploymentType",
    },
)
class CodedeployDeploymentGroupDeploymentStyle:
    def __init__(
        self,
        *,
        deployment_option: typing.Optional[builtins.str] = None,
        deployment_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_option CodedeployDeploymentGroup#deployment_option}.
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_type CodedeployDeploymentGroup#deployment_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if deployment_option is not None:
            self._values["deployment_option"] = deployment_option
        if deployment_type is not None:
            self._values["deployment_type"] = deployment_type

    @builtins.property
    def deployment_option(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_option CodedeployDeploymentGroup#deployment_option}.'''
        result = self._values.get("deployment_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#deployment_type CodedeployDeploymentGroup#deployment_type}.'''
        result = self._values.get("deployment_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupDeploymentStyle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupDeploymentStyleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupDeploymentStyleOutputReference",
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

    @jsii.member(jsii_name="resetDeploymentOption")
    def reset_deployment_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentOption", []))

    @jsii.member(jsii_name="resetDeploymentType")
    def reset_deployment_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentOptionInput")
    def deployment_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTypeInput")
    def deployment_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentOption")
    def deployment_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentOption"))

    @deployment_option.setter
    def deployment_option(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentType"))

    @deployment_type.setter
    def deployment_type(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupDeploymentStyle]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupDeploymentStyle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupDeploymentStyle],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupEc2TagFilter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "type": "type", "value": "value"},
)
class CodedeployDeploymentGroupEc2TagFilter:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#key CodedeployDeploymentGroup#key}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#type CodedeployDeploymentGroup#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#value CodedeployDeploymentGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if type is not None:
            self._values["type"] = type
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#key CodedeployDeploymentGroup#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#type CodedeployDeploymentGroup#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#value CodedeployDeploymentGroup#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupEc2TagFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupEc2TagSet",
    jsii_struct_bases=[],
    name_mapping={"ec2_tag_filter": "ec2TagFilter"},
)
class CodedeployDeploymentGroupEc2TagSet:
    def __init__(
        self,
        *,
        ec2_tag_filter: typing.Optional[typing.Sequence["CodedeployDeploymentGroupEc2TagSetEc2TagFilter"]] = None,
    ) -> None:
        '''
        :param ec2_tag_filter: ec2_tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_filter CodedeployDeploymentGroup#ec2_tag_filter}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if ec2_tag_filter is not None:
            self._values["ec2_tag_filter"] = ec2_tag_filter

    @builtins.property
    def ec2_tag_filter(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagSetEc2TagFilter"]]:
        '''ec2_tag_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#ec2_tag_filter CodedeployDeploymentGroup#ec2_tag_filter}
        '''
        result = self._values.get("ec2_tag_filter")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupEc2TagSetEc2TagFilter"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupEc2TagSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupEc2TagSetEc2TagFilter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "type": "type", "value": "value"},
)
class CodedeployDeploymentGroupEc2TagSetEc2TagFilter:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#key CodedeployDeploymentGroup#key}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#type CodedeployDeploymentGroup#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#value CodedeployDeploymentGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if type is not None:
            self._values["type"] = type
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#key CodedeployDeploymentGroup#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#type CodedeployDeploymentGroup#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#value CodedeployDeploymentGroup#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupEc2TagSetEc2TagFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupEcsService",
    jsii_struct_bases=[],
    name_mapping={"cluster_name": "clusterName", "service_name": "serviceName"},
)
class CodedeployDeploymentGroupEcsService:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        service_name: builtins.str,
    ) -> None:
        '''
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#cluster_name CodedeployDeploymentGroup#cluster_name}.
        :param service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#service_name CodedeployDeploymentGroup#service_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
            "service_name": service_name,
        }

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#cluster_name CodedeployDeploymentGroup#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#service_name CodedeployDeploymentGroup#service_name}.'''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupEcsService(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupEcsServiceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupEcsServiceOutputReference",
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
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceNameInput")
    def service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        jsii.set(self, "serviceName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CodedeployDeploymentGroupEcsService]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupEcsService], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupEcsService],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfo",
    jsii_struct_bases=[],
    name_mapping={
        "elb_info": "elbInfo",
        "target_group_info": "targetGroupInfo",
        "target_group_pair_info": "targetGroupPairInfo",
    },
)
class CodedeployDeploymentGroupLoadBalancerInfo:
    def __init__(
        self,
        *,
        elb_info: typing.Optional[typing.Sequence["CodedeployDeploymentGroupLoadBalancerInfoElbInfo"]] = None,
        target_group_info: typing.Optional[typing.Sequence["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]] = None,
        target_group_pair_info: typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo"] = None,
    ) -> None:
        '''
        :param elb_info: elb_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#elb_info CodedeployDeploymentGroup#elb_info}
        :param target_group_info: target_group_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group_info CodedeployDeploymentGroup#target_group_info}
        :param target_group_pair_info: target_group_pair_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group_pair_info CodedeployDeploymentGroup#target_group_pair_info}
        '''
        if isinstance(target_group_pair_info, dict):
            target_group_pair_info = CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo(**target_group_pair_info)
        self._values: typing.Dict[str, typing.Any] = {}
        if elb_info is not None:
            self._values["elb_info"] = elb_info
        if target_group_info is not None:
            self._values["target_group_info"] = target_group_info
        if target_group_pair_info is not None:
            self._values["target_group_pair_info"] = target_group_pair_info

    @builtins.property
    def elb_info(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoElbInfo"]]:
        '''elb_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#elb_info CodedeployDeploymentGroup#elb_info}
        '''
        result = self._values.get("elb_info")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoElbInfo"]], result)

    @builtins.property
    def target_group_info(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]]:
        '''target_group_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group_info CodedeployDeploymentGroup#target_group_info}
        '''
        result = self._values.get("target_group_info")
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]], result)

    @builtins.property
    def target_group_pair_info(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo"]:
        '''target_group_pair_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group_pair_info CodedeployDeploymentGroup#target_group_pair_info}
        '''
        result = self._values.get("target_group_pair_info")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoElbInfo",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class CodedeployDeploymentGroupLoadBalancerInfoElbInfo:
    def __init__(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#name CodedeployDeploymentGroup#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#name CodedeployDeploymentGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfoElbInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupLoadBalancerInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoOutputReference",
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

    @jsii.member(jsii_name="putTargetGroupPairInfo")
    def put_target_group_pair_info(
        self,
        *,
        prod_traffic_route: "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute",
        target_group: typing.Sequence["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"],
        test_traffic_route: typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute"] = None,
    ) -> None:
        '''
        :param prod_traffic_route: prod_traffic_route block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#prod_traffic_route CodedeployDeploymentGroup#prod_traffic_route}
        :param target_group: target_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group CodedeployDeploymentGroup#target_group}
        :param test_traffic_route: test_traffic_route block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#test_traffic_route CodedeployDeploymentGroup#test_traffic_route}
        '''
        value = CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo(
            prod_traffic_route=prod_traffic_route,
            target_group=target_group,
            test_traffic_route=test_traffic_route,
        )

        return typing.cast(None, jsii.invoke(self, "putTargetGroupPairInfo", [value]))

    @jsii.member(jsii_name="resetElbInfo")
    def reset_elb_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElbInfo", []))

    @jsii.member(jsii_name="resetTargetGroupInfo")
    def reset_target_group_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetGroupInfo", []))

    @jsii.member(jsii_name="resetTargetGroupPairInfo")
    def reset_target_group_pair_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetGroupPairInfo", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupPairInfo")
    def target_group_pair_info(
        self,
    ) -> "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoOutputReference":
        return typing.cast("CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoOutputReference", jsii.get(self, "targetGroupPairInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elbInfoInput")
    def elb_info_input(
        self,
    ) -> typing.Optional[typing.List[CodedeployDeploymentGroupLoadBalancerInfoElbInfo]]:
        return typing.cast(typing.Optional[typing.List[CodedeployDeploymentGroupLoadBalancerInfoElbInfo]], jsii.get(self, "elbInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupInfoInput")
    def target_group_info_input(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]]:
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]], jsii.get(self, "targetGroupInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupPairInfoInput")
    def target_group_pair_info_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo"], jsii.get(self, "targetGroupPairInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elbInfo")
    def elb_info(self) -> typing.List[CodedeployDeploymentGroupLoadBalancerInfoElbInfo]:
        return typing.cast(typing.List[CodedeployDeploymentGroupLoadBalancerInfoElbInfo], jsii.get(self, "elbInfo"))

    @elb_info.setter
    def elb_info(
        self,
        value: typing.List[CodedeployDeploymentGroupLoadBalancerInfoElbInfo],
    ) -> None:
        jsii.set(self, "elbInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupInfo")
    def target_group_info(
        self,
    ) -> typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"]:
        return typing.cast(typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"], jsii.get(self, "targetGroupInfo"))

    @target_group_info.setter
    def target_group_info(
        self,
        value: typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo"],
    ) -> None:
        jsii.set(self, "targetGroupInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupLoadBalancerInfo]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupLoadBalancerInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupLoadBalancerInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo:
    def __init__(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#name CodedeployDeploymentGroup#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#name CodedeployDeploymentGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo",
    jsii_struct_bases=[],
    name_mapping={
        "prod_traffic_route": "prodTrafficRoute",
        "target_group": "targetGroup",
        "test_traffic_route": "testTrafficRoute",
    },
)
class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo:
    def __init__(
        self,
        *,
        prod_traffic_route: "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute",
        target_group: typing.Sequence["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"],
        test_traffic_route: typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute"] = None,
    ) -> None:
        '''
        :param prod_traffic_route: prod_traffic_route block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#prod_traffic_route CodedeployDeploymentGroup#prod_traffic_route}
        :param target_group: target_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group CodedeployDeploymentGroup#target_group}
        :param test_traffic_route: test_traffic_route block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#test_traffic_route CodedeployDeploymentGroup#test_traffic_route}
        '''
        if isinstance(prod_traffic_route, dict):
            prod_traffic_route = CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute(**prod_traffic_route)
        if isinstance(test_traffic_route, dict):
            test_traffic_route = CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute(**test_traffic_route)
        self._values: typing.Dict[str, typing.Any] = {
            "prod_traffic_route": prod_traffic_route,
            "target_group": target_group,
        }
        if test_traffic_route is not None:
            self._values["test_traffic_route"] = test_traffic_route

    @builtins.property
    def prod_traffic_route(
        self,
    ) -> "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute":
        '''prod_traffic_route block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#prod_traffic_route CodedeployDeploymentGroup#prod_traffic_route}
        '''
        result = self._values.get("prod_traffic_route")
        assert result is not None, "Required property 'prod_traffic_route' is missing"
        return typing.cast("CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute", result)

    @builtins.property
    def target_group(
        self,
    ) -> typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"]:
        '''target_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#target_group CodedeployDeploymentGroup#target_group}
        '''
        result = self._values.get("target_group")
        assert result is not None, "Required property 'target_group' is missing"
        return typing.cast(typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"], result)

    @builtins.property
    def test_traffic_route(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute"]:
        '''test_traffic_route block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#test_traffic_route CodedeployDeploymentGroup#test_traffic_route}
        '''
        result = self._values.get("test_traffic_route")
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoOutputReference",
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

    @jsii.member(jsii_name="putProdTrafficRoute")
    def put_prod_traffic_route(
        self,
        *,
        listener_arns: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param listener_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#listener_arns CodedeployDeploymentGroup#listener_arns}.
        '''
        value = CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute(
            listener_arns=listener_arns
        )

        return typing.cast(None, jsii.invoke(self, "putProdTrafficRoute", [value]))

    @jsii.member(jsii_name="putTestTrafficRoute")
    def put_test_traffic_route(
        self,
        *,
        listener_arns: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param listener_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#listener_arns CodedeployDeploymentGroup#listener_arns}.
        '''
        value = CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute(
            listener_arns=listener_arns
        )

        return typing.cast(None, jsii.invoke(self, "putTestTrafficRoute", [value]))

    @jsii.member(jsii_name="resetTestTrafficRoute")
    def reset_test_traffic_route(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTestTrafficRoute", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prodTrafficRoute")
    def prod_traffic_route(
        self,
    ) -> "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRouteOutputReference":
        return typing.cast("CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRouteOutputReference", jsii.get(self, "prodTrafficRoute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="testTrafficRoute")
    def test_traffic_route(
        self,
    ) -> "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRouteOutputReference":
        return typing.cast("CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRouteOutputReference", jsii.get(self, "testTrafficRoute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prodTrafficRouteInput")
    def prod_traffic_route_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute"], jsii.get(self, "prodTrafficRouteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupInput")
    def target_group_input(
        self,
    ) -> typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"]]:
        return typing.cast(typing.Optional[typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"]], jsii.get(self, "targetGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="testTrafficRouteInput")
    def test_traffic_route_input(
        self,
    ) -> typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute"]:
        return typing.cast(typing.Optional["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute"], jsii.get(self, "testTrafficRouteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroup")
    def target_group(
        self,
    ) -> typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"]:
        return typing.cast(typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"], jsii.get(self, "targetGroup"))

    @target_group.setter
    def target_group(
        self,
        value: typing.List["CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup"],
    ) -> None:
        jsii.set(self, "targetGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute",
    jsii_struct_bases=[],
    name_mapping={"listener_arns": "listenerArns"},
)
class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute:
    def __init__(self, *, listener_arns: typing.Sequence[builtins.str]) -> None:
        '''
        :param listener_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#listener_arns CodedeployDeploymentGroup#listener_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener_arns": listener_arns,
        }

    @builtins.property
    def listener_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#listener_arns CodedeployDeploymentGroup#listener_arns}.'''
        result = self._values.get("listener_arns")
        assert result is not None, "Required property 'listener_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRouteOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRouteOutputReference",
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
    @jsii.member(jsii_name="listenerArnsInput")
    def listener_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "listenerArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="listenerArns")
    def listener_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "listenerArns"))

    @listener_arns.setter
    def listener_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "listenerArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#name CodedeployDeploymentGroup#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#name CodedeployDeploymentGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute",
    jsii_struct_bases=[],
    name_mapping={"listener_arns": "listenerArns"},
)
class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute:
    def __init__(self, *, listener_arns: typing.Sequence[builtins.str]) -> None:
        '''
        :param listener_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#listener_arns CodedeployDeploymentGroup#listener_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener_arns": listener_arns,
        }

    @builtins.property
    def listener_arns(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#listener_arns CodedeployDeploymentGroup#listener_arns}.'''
        result = self._values.get("listener_arns")
        assert result is not None, "Required property 'listener_arns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRouteOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRouteOutputReference",
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
    @jsii.member(jsii_name="listenerArnsInput")
    def listener_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "listenerArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="listenerArns")
    def listener_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "listenerArns"))

    @listener_arns.setter
    def listener_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "listenerArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute]:
        return typing.cast(typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupOnPremisesInstanceTagFilter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "type": "type", "value": "value"},
)
class CodedeployDeploymentGroupOnPremisesInstanceTagFilter:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#key CodedeployDeploymentGroup#key}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#type CodedeployDeploymentGroup#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#value CodedeployDeploymentGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if type is not None:
            self._values["type"] = type
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#key CodedeployDeploymentGroup#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#type CodedeployDeploymentGroup#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#value CodedeployDeploymentGroup#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupOnPremisesInstanceTagFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.codedeploy.CodedeployDeploymentGroupTriggerConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "trigger_events": "triggerEvents",
        "trigger_name": "triggerName",
        "trigger_target_arn": "triggerTargetArn",
    },
)
class CodedeployDeploymentGroupTriggerConfiguration:
    def __init__(
        self,
        *,
        trigger_events: typing.Sequence[builtins.str],
        trigger_name: builtins.str,
        trigger_target_arn: builtins.str,
    ) -> None:
        '''
        :param trigger_events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_events CodedeployDeploymentGroup#trigger_events}.
        :param trigger_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_name CodedeployDeploymentGroup#trigger_name}.
        :param trigger_target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_target_arn CodedeployDeploymentGroup#trigger_target_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "trigger_events": trigger_events,
            "trigger_name": trigger_name,
            "trigger_target_arn": trigger_target_arn,
        }

    @builtins.property
    def trigger_events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_events CodedeployDeploymentGroup#trigger_events}.'''
        result = self._values.get("trigger_events")
        assert result is not None, "Required property 'trigger_events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def trigger_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_name CodedeployDeploymentGroup#trigger_name}.'''
        result = self._values.get("trigger_name")
        assert result is not None, "Required property 'trigger_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def trigger_target_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/codedeploy_deployment_group#trigger_target_arn CodedeployDeploymentGroup#trigger_target_arn}.'''
        result = self._values.get("trigger_target_arn")
        assert result is not None, "Required property 'trigger_target_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodedeployDeploymentGroupTriggerConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodedeployApp",
    "CodedeployAppConfig",
    "CodedeployDeploymentConfig",
    "CodedeployDeploymentConfigConfig",
    "CodedeployDeploymentConfigMinimumHealthyHosts",
    "CodedeployDeploymentConfigMinimumHealthyHostsOutputReference",
    "CodedeployDeploymentConfigTrafficRoutingConfig",
    "CodedeployDeploymentConfigTrafficRoutingConfigOutputReference",
    "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanary",
    "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedCanaryOutputReference",
    "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinear",
    "CodedeployDeploymentConfigTrafficRoutingConfigTimeBasedLinearOutputReference",
    "CodedeployDeploymentGroup",
    "CodedeployDeploymentGroupAlarmConfiguration",
    "CodedeployDeploymentGroupAlarmConfigurationOutputReference",
    "CodedeployDeploymentGroupAutoRollbackConfiguration",
    "CodedeployDeploymentGroupAutoRollbackConfigurationOutputReference",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfig",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOption",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigDeploymentReadyOptionOutputReference",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOption",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigGreenFleetProvisioningOptionOutputReference",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigOutputReference",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccess",
    "CodedeployDeploymentGroupBlueGreenDeploymentConfigTerminateBlueInstancesOnDeploymentSuccessOutputReference",
    "CodedeployDeploymentGroupConfig",
    "CodedeployDeploymentGroupDeploymentStyle",
    "CodedeployDeploymentGroupDeploymentStyleOutputReference",
    "CodedeployDeploymentGroupEc2TagFilter",
    "CodedeployDeploymentGroupEc2TagSet",
    "CodedeployDeploymentGroupEc2TagSetEc2TagFilter",
    "CodedeployDeploymentGroupEcsService",
    "CodedeployDeploymentGroupEcsServiceOutputReference",
    "CodedeployDeploymentGroupLoadBalancerInfo",
    "CodedeployDeploymentGroupLoadBalancerInfoElbInfo",
    "CodedeployDeploymentGroupLoadBalancerInfoOutputReference",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupInfo",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfo",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoOutputReference",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRoute",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoProdTrafficRouteOutputReference",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTargetGroup",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRoute",
    "CodedeployDeploymentGroupLoadBalancerInfoTargetGroupPairInfoTestTrafficRouteOutputReference",
    "CodedeployDeploymentGroupOnPremisesInstanceTagFilter",
    "CodedeployDeploymentGroupTriggerConfiguration",
]

publication.publish()
