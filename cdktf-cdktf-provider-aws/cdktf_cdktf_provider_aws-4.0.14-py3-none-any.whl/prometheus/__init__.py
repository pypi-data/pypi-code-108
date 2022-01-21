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


class PrometheusAlertManagerDefinition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.prometheus.PrometheusAlertManagerDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition aws_prometheus_alert_manager_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        definition: builtins.str,
        workspace_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition aws_prometheus_alert_manager_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition#definition PrometheusAlertManagerDefinition#definition}.
        :param workspace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition#workspace_id PrometheusAlertManagerDefinition#workspace_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PrometheusAlertManagerDefinitionConfig(
            definition=definition,
            workspace_id=workspace_id,
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
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "definitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: builtins.str) -> None:
        jsii.set(self, "definition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        jsii.set(self, "workspaceId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.prometheus.PrometheusAlertManagerDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "definition": "definition",
        "workspace_id": "workspaceId",
    },
)
class PrometheusAlertManagerDefinitionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        definition: builtins.str,
        workspace_id: builtins.str,
    ) -> None:
        '''Prometheus.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition#definition PrometheusAlertManagerDefinition#definition}.
        :param workspace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition#workspace_id PrometheusAlertManagerDefinition#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
            "workspace_id": workspace_id,
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
    def definition(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition#definition PrometheusAlertManagerDefinition#definition}.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_alert_manager_definition#workspace_id PrometheusAlertManagerDefinition#workspace_id}.'''
        result = self._values.get("workspace_id")
        assert result is not None, "Required property 'workspace_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrometheusAlertManagerDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PrometheusRuleGroupNamespace(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.prometheus.PrometheusRuleGroupNamespace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace aws_prometheus_rule_group_namespace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        data: builtins.str,
        name: builtins.str,
        workspace_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace aws_prometheus_rule_group_namespace} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#data PrometheusRuleGroupNamespace#data}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#name PrometheusRuleGroupNamespace#name}.
        :param workspace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#workspace_id PrometheusRuleGroupNamespace#workspace_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PrometheusRuleGroupNamespaceConfig(
            data=data,
            name=name,
            workspace_id=workspace_id,
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
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @data.setter
    def data(self, value: builtins.str) -> None:
        jsii.set(self, "data", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        jsii.set(self, "workspaceId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.prometheus.PrometheusRuleGroupNamespaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "data": "data",
        "name": "name",
        "workspace_id": "workspaceId",
    },
)
class PrometheusRuleGroupNamespaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        data: builtins.str,
        name: builtins.str,
        workspace_id: builtins.str,
    ) -> None:
        '''Prometheus.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#data PrometheusRuleGroupNamespace#data}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#name PrometheusRuleGroupNamespace#name}.
        :param workspace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#workspace_id PrometheusRuleGroupNamespace#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "data": data,
            "name": name,
            "workspace_id": workspace_id,
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
    def data(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#data PrometheusRuleGroupNamespace#data}.'''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#name PrometheusRuleGroupNamespace#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_rule_group_namespace#workspace_id PrometheusRuleGroupNamespace#workspace_id}.'''
        result = self._values.get("workspace_id")
        assert result is not None, "Required property 'workspace_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrometheusRuleGroupNamespaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PrometheusWorkspace(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.prometheus.PrometheusWorkspace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/prometheus_workspace aws_prometheus_workspace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/prometheus_workspace aws_prometheus_workspace} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_workspace#alias PrometheusWorkspace#alias}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PrometheusWorkspaceConfig(
            alias=alias,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

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
    @jsii.member(jsii_name="prometheusEndpoint")
    def prometheus_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prometheusEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        jsii.set(self, "alias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.prometheus.PrometheusWorkspaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alias": "alias",
    },
)
class PrometheusWorkspaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Prometheus.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_workspace#alias PrometheusWorkspace#alias}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if alias is not None:
            self._values["alias"] = alias

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
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/prometheus_workspace#alias PrometheusWorkspace#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrometheusWorkspaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PrometheusAlertManagerDefinition",
    "PrometheusAlertManagerDefinitionConfig",
    "PrometheusRuleGroupNamespace",
    "PrometheusRuleGroupNamespaceConfig",
    "PrometheusWorkspace",
    "PrometheusWorkspaceConfig",
]

publication.publish()
