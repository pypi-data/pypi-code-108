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


class SecurityhubAccount(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_account aws_securityhub_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_account aws_securityhub_account} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubAccountConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class SecurityhubAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubActionTarget(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubActionTarget",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target aws_securityhub_action_target}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        identifier: builtins.str,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target aws_securityhub_action_target} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#description SecurityhubActionTarget#description}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#identifier SecurityhubActionTarget#identifier}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#name SecurityhubActionTarget#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubActionTargetConfig(
            description=description,
            identifier=identifier,
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubActionTargetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "description": "description",
        "identifier": "identifier",
        "name": "name",
    },
)
class SecurityhubActionTargetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        description: builtins.str,
        identifier: builtins.str,
        name: builtins.str,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#description SecurityhubActionTarget#description}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#identifier SecurityhubActionTarget#identifier}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#name SecurityhubActionTarget#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "identifier": identifier,
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
    def description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#description SecurityhubActionTarget#description}.'''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#identifier SecurityhubActionTarget#identifier}.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_action_target#name SecurityhubActionTarget#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubActionTargetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubFindingAggregator(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubFindingAggregator",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator aws_securityhub_finding_aggregator}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        linking_mode: builtins.str,
        specified_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator aws_securityhub_finding_aggregator} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param linking_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator#linking_mode SecurityhubFindingAggregator#linking_mode}.
        :param specified_regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator#specified_regions SecurityhubFindingAggregator#specified_regions}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubFindingAggregatorConfig(
            linking_mode=linking_mode,
            specified_regions=specified_regions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetSpecifiedRegions")
    def reset_specified_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpecifiedRegions", []))

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
    @jsii.member(jsii_name="linkingModeInput")
    def linking_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "linkingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specifiedRegionsInput")
    def specified_regions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "specifiedRegionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="linkingMode")
    def linking_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "linkingMode"))

    @linking_mode.setter
    def linking_mode(self, value: builtins.str) -> None:
        jsii.set(self, "linkingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specifiedRegions")
    def specified_regions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "specifiedRegions"))

    @specified_regions.setter
    def specified_regions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "specifiedRegions", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubFindingAggregatorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "linking_mode": "linkingMode",
        "specified_regions": "specifiedRegions",
    },
)
class SecurityhubFindingAggregatorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        linking_mode: builtins.str,
        specified_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param linking_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator#linking_mode SecurityhubFindingAggregator#linking_mode}.
        :param specified_regions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator#specified_regions SecurityhubFindingAggregator#specified_regions}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "linking_mode": linking_mode,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if specified_regions is not None:
            self._values["specified_regions"] = specified_regions

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
    def linking_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator#linking_mode SecurityhubFindingAggregator#linking_mode}.'''
        result = self._values.get("linking_mode")
        assert result is not None, "Required property 'linking_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def specified_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_finding_aggregator#specified_regions SecurityhubFindingAggregator#specified_regions}.'''
        result = self._values.get("specified_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubFindingAggregatorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsight(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsight",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight aws_securityhub_insight}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        filters: "SecurityhubInsightFilters",
        group_by_attribute: builtins.str,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight aws_securityhub_insight} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filters: filters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#filters SecurityhubInsight#filters}
        :param group_by_attribute: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#group_by_attribute SecurityhubInsight#group_by_attribute}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#name SecurityhubInsight#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubInsightConfig(
            filters=filters,
            group_by_attribute=group_by_attribute,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFilters")
    def put_filters(
        self,
        *,
        aws_account_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersAwsAccountId"]] = None,
        company_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersCompanyName"]] = None,
        compliance_status: typing.Optional[typing.Sequence["SecurityhubInsightFiltersComplianceStatus"]] = None,
        confidence: typing.Optional[typing.Sequence["SecurityhubInsightFiltersConfidence"]] = None,
        created_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersCreatedAt"]] = None,
        criticality: typing.Optional[typing.Sequence["SecurityhubInsightFiltersCriticality"]] = None,
        description: typing.Optional[typing.Sequence["SecurityhubInsightFiltersDescription"]] = None,
        finding_provider_fields_confidence: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsConfidence"]] = None,
        finding_provider_fields_criticality: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsCriticality"]] = None,
        finding_provider_fields_related_findings_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId"]] = None,
        finding_provider_fields_related_findings_product_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn"]] = None,
        finding_provider_fields_severity_label: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel"]] = None,
        finding_provider_fields_severity_original: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal"]] = None,
        finding_provider_fields_types: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsTypes"]] = None,
        first_observed_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFirstObservedAt"]] = None,
        generator_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersGeneratorId"]] = None,
        id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersId"]] = None,
        keyword: typing.Optional[typing.Sequence["SecurityhubInsightFiltersKeyword"]] = None,
        last_observed_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersLastObservedAt"]] = None,
        malware_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwareName"]] = None,
        malware_path: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwarePath"]] = None,
        malware_state: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwareState"]] = None,
        malware_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwareType"]] = None,
        network_destination_domain: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationDomain"]] = None,
        network_destination_ipv4: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationIpv4"]] = None,
        network_destination_ipv6: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationIpv6"]] = None,
        network_destination_port: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationPort"]] = None,
        network_direction: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDirection"]] = None,
        network_protocol: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkProtocol"]] = None,
        network_source_domain: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceDomain"]] = None,
        network_source_ipv4: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceIpv4"]] = None,
        network_source_ipv6: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceIpv6"]] = None,
        network_source_mac: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceMac"]] = None,
        network_source_port: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourcePort"]] = None,
        note_text: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNoteText"]] = None,
        note_updated_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNoteUpdatedAt"]] = None,
        note_updated_by: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNoteUpdatedBy"]] = None,
        process_launched_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessLaunchedAt"]] = None,
        process_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessName"]] = None,
        process_parent_pid: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessParentPid"]] = None,
        process_path: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessPath"]] = None,
        process_pid: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessPid"]] = None,
        process_terminated_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessTerminatedAt"]] = None,
        product_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProductArn"]] = None,
        product_fields: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProductFields"]] = None,
        product_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProductName"]] = None,
        recommendation_text: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRecommendationText"]] = None,
        record_state: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRecordState"]] = None,
        related_findings_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRelatedFindingsId"]] = None,
        related_findings_product_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRelatedFindingsProductArn"]] = None,
        resource_aws_ec2_instance_iam_instance_profile_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]] = None,
        resource_aws_ec2_instance_image_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]] = None,
        resource_aws_ec2_instance_ipv4_addresses: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]] = None,
        resource_aws_ec2_instance_ipv6_addresses: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]] = None,
        resource_aws_ec2_instance_key_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]] = None,
        resource_aws_ec2_instance_launched_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]] = None,
        resource_aws_ec2_instance_subnet_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]] = None,
        resource_aws_ec2_instance_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]] = None,
        resource_aws_ec2_instance_vpc_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]] = None,
        resource_aws_iam_access_key_created_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]] = None,
        resource_aws_iam_access_key_status: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]] = None,
        resource_aws_iam_access_key_user_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]] = None,
        resource_aws_s3_bucket_owner_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]] = None,
        resource_aws_s3_bucket_owner_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]] = None,
        resource_container_image_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerImageId"]] = None,
        resource_container_image_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerImageName"]] = None,
        resource_container_launched_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerLaunchedAt"]] = None,
        resource_container_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerName"]] = None,
        resource_details_other: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceDetailsOther"]] = None,
        resource_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceId"]] = None,
        resource_partition: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourcePartition"]] = None,
        resource_region: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceRegion"]] = None,
        resource_tags: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceTags"]] = None,
        resource_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceType"]] = None,
        severity_label: typing.Optional[typing.Sequence["SecurityhubInsightFiltersSeverityLabel"]] = None,
        source_url: typing.Optional[typing.Sequence["SecurityhubInsightFiltersSourceUrl"]] = None,
        threat_intel_indicator_category: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]] = None,
        threat_intel_indicator_last_observed_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]] = None,
        threat_intel_indicator_source: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorSource"]] = None,
        threat_intel_indicator_source_url: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]] = None,
        threat_intel_indicator_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorType"]] = None,
        threat_intel_indicator_value: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorValue"]] = None,
        title: typing.Optional[typing.Sequence["SecurityhubInsightFiltersTitle"]] = None,
        type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersType"]] = None,
        updated_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersUpdatedAt"]] = None,
        user_defined_values: typing.Optional[typing.Sequence["SecurityhubInsightFiltersUserDefinedValues"]] = None,
        verification_state: typing.Optional[typing.Sequence["SecurityhubInsightFiltersVerificationState"]] = None,
        workflow_status: typing.Optional[typing.Sequence["SecurityhubInsightFiltersWorkflowStatus"]] = None,
    ) -> None:
        '''
        :param aws_account_id: aws_account_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#aws_account_id SecurityhubInsight#aws_account_id}
        :param company_name: company_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#company_name SecurityhubInsight#company_name}
        :param compliance_status: compliance_status block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#compliance_status SecurityhubInsight#compliance_status}
        :param confidence: confidence block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#confidence SecurityhubInsight#confidence}
        :param created_at: created_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#created_at SecurityhubInsight#created_at}
        :param criticality: criticality block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#criticality SecurityhubInsight#criticality}
        :param description: description block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#description SecurityhubInsight#description}
        :param finding_provider_fields_confidence: finding_provider_fields_confidence block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_confidence SecurityhubInsight#finding_provider_fields_confidence}
        :param finding_provider_fields_criticality: finding_provider_fields_criticality block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_criticality SecurityhubInsight#finding_provider_fields_criticality}
        :param finding_provider_fields_related_findings_id: finding_provider_fields_related_findings_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_related_findings_id SecurityhubInsight#finding_provider_fields_related_findings_id}
        :param finding_provider_fields_related_findings_product_arn: finding_provider_fields_related_findings_product_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_related_findings_product_arn SecurityhubInsight#finding_provider_fields_related_findings_product_arn}
        :param finding_provider_fields_severity_label: finding_provider_fields_severity_label block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_severity_label SecurityhubInsight#finding_provider_fields_severity_label}
        :param finding_provider_fields_severity_original: finding_provider_fields_severity_original block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_severity_original SecurityhubInsight#finding_provider_fields_severity_original}
        :param finding_provider_fields_types: finding_provider_fields_types block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_types SecurityhubInsight#finding_provider_fields_types}
        :param first_observed_at: first_observed_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#first_observed_at SecurityhubInsight#first_observed_at}
        :param generator_id: generator_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#generator_id SecurityhubInsight#generator_id}
        :param id: id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#id SecurityhubInsight#id}
        :param keyword: keyword block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#keyword SecurityhubInsight#keyword}
        :param last_observed_at: last_observed_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#last_observed_at SecurityhubInsight#last_observed_at}
        :param malware_name: malware_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_name SecurityhubInsight#malware_name}
        :param malware_path: malware_path block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_path SecurityhubInsight#malware_path}
        :param malware_state: malware_state block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_state SecurityhubInsight#malware_state}
        :param malware_type: malware_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_type SecurityhubInsight#malware_type}
        :param network_destination_domain: network_destination_domain block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_domain SecurityhubInsight#network_destination_domain}
        :param network_destination_ipv4: network_destination_ipv4 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_ipv4 SecurityhubInsight#network_destination_ipv4}
        :param network_destination_ipv6: network_destination_ipv6 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_ipv6 SecurityhubInsight#network_destination_ipv6}
        :param network_destination_port: network_destination_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_port SecurityhubInsight#network_destination_port}
        :param network_direction: network_direction block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_direction SecurityhubInsight#network_direction}
        :param network_protocol: network_protocol block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_protocol SecurityhubInsight#network_protocol}
        :param network_source_domain: network_source_domain block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_domain SecurityhubInsight#network_source_domain}
        :param network_source_ipv4: network_source_ipv4 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_ipv4 SecurityhubInsight#network_source_ipv4}
        :param network_source_ipv6: network_source_ipv6 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_ipv6 SecurityhubInsight#network_source_ipv6}
        :param network_source_mac: network_source_mac block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_mac SecurityhubInsight#network_source_mac}
        :param network_source_port: network_source_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_port SecurityhubInsight#network_source_port}
        :param note_text: note_text block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_text SecurityhubInsight#note_text}
        :param note_updated_at: note_updated_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_updated_at SecurityhubInsight#note_updated_at}
        :param note_updated_by: note_updated_by block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_updated_by SecurityhubInsight#note_updated_by}
        :param process_launched_at: process_launched_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_launched_at SecurityhubInsight#process_launched_at}
        :param process_name: process_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_name SecurityhubInsight#process_name}
        :param process_parent_pid: process_parent_pid block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_parent_pid SecurityhubInsight#process_parent_pid}
        :param process_path: process_path block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_path SecurityhubInsight#process_path}
        :param process_pid: process_pid block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_pid SecurityhubInsight#process_pid}
        :param process_terminated_at: process_terminated_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_terminated_at SecurityhubInsight#process_terminated_at}
        :param product_arn: product_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_arn SecurityhubInsight#product_arn}
        :param product_fields: product_fields block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_fields SecurityhubInsight#product_fields}
        :param product_name: product_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_name SecurityhubInsight#product_name}
        :param recommendation_text: recommendation_text block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#recommendation_text SecurityhubInsight#recommendation_text}
        :param record_state: record_state block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#record_state SecurityhubInsight#record_state}
        :param related_findings_id: related_findings_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#related_findings_id SecurityhubInsight#related_findings_id}
        :param related_findings_product_arn: related_findings_product_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#related_findings_product_arn SecurityhubInsight#related_findings_product_arn}
        :param resource_aws_ec2_instance_iam_instance_profile_arn: resource_aws_ec2_instance_iam_instance_profile_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_iam_instance_profile_arn SecurityhubInsight#resource_aws_ec2_instance_iam_instance_profile_arn}
        :param resource_aws_ec2_instance_image_id: resource_aws_ec2_instance_image_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_image_id SecurityhubInsight#resource_aws_ec2_instance_image_id}
        :param resource_aws_ec2_instance_ipv4_addresses: resource_aws_ec2_instance_ipv4_addresses block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_ipv4_addresses SecurityhubInsight#resource_aws_ec2_instance_ipv4_addresses}
        :param resource_aws_ec2_instance_ipv6_addresses: resource_aws_ec2_instance_ipv6_addresses block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_ipv6_addresses SecurityhubInsight#resource_aws_ec2_instance_ipv6_addresses}
        :param resource_aws_ec2_instance_key_name: resource_aws_ec2_instance_key_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_key_name SecurityhubInsight#resource_aws_ec2_instance_key_name}
        :param resource_aws_ec2_instance_launched_at: resource_aws_ec2_instance_launched_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_launched_at SecurityhubInsight#resource_aws_ec2_instance_launched_at}
        :param resource_aws_ec2_instance_subnet_id: resource_aws_ec2_instance_subnet_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_subnet_id SecurityhubInsight#resource_aws_ec2_instance_subnet_id}
        :param resource_aws_ec2_instance_type: resource_aws_ec2_instance_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_type SecurityhubInsight#resource_aws_ec2_instance_type}
        :param resource_aws_ec2_instance_vpc_id: resource_aws_ec2_instance_vpc_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_vpc_id SecurityhubInsight#resource_aws_ec2_instance_vpc_id}
        :param resource_aws_iam_access_key_created_at: resource_aws_iam_access_key_created_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_created_at SecurityhubInsight#resource_aws_iam_access_key_created_at}
        :param resource_aws_iam_access_key_status: resource_aws_iam_access_key_status block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_status SecurityhubInsight#resource_aws_iam_access_key_status}
        :param resource_aws_iam_access_key_user_name: resource_aws_iam_access_key_user_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_user_name SecurityhubInsight#resource_aws_iam_access_key_user_name}
        :param resource_aws_s3_bucket_owner_id: resource_aws_s3_bucket_owner_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_s3_bucket_owner_id SecurityhubInsight#resource_aws_s3_bucket_owner_id}
        :param resource_aws_s3_bucket_owner_name: resource_aws_s3_bucket_owner_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_s3_bucket_owner_name SecurityhubInsight#resource_aws_s3_bucket_owner_name}
        :param resource_container_image_id: resource_container_image_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_image_id SecurityhubInsight#resource_container_image_id}
        :param resource_container_image_name: resource_container_image_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_image_name SecurityhubInsight#resource_container_image_name}
        :param resource_container_launched_at: resource_container_launched_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_launched_at SecurityhubInsight#resource_container_launched_at}
        :param resource_container_name: resource_container_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_name SecurityhubInsight#resource_container_name}
        :param resource_details_other: resource_details_other block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_details_other SecurityhubInsight#resource_details_other}
        :param resource_id: resource_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_id SecurityhubInsight#resource_id}
        :param resource_partition: resource_partition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_partition SecurityhubInsight#resource_partition}
        :param resource_region: resource_region block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_region SecurityhubInsight#resource_region}
        :param resource_tags: resource_tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_tags SecurityhubInsight#resource_tags}
        :param resource_type: resource_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_type SecurityhubInsight#resource_type}
        :param severity_label: severity_label block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#severity_label SecurityhubInsight#severity_label}
        :param source_url: source_url block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#source_url SecurityhubInsight#source_url}
        :param threat_intel_indicator_category: threat_intel_indicator_category block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_category SecurityhubInsight#threat_intel_indicator_category}
        :param threat_intel_indicator_last_observed_at: threat_intel_indicator_last_observed_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_last_observed_at SecurityhubInsight#threat_intel_indicator_last_observed_at}
        :param threat_intel_indicator_source: threat_intel_indicator_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_source SecurityhubInsight#threat_intel_indicator_source}
        :param threat_intel_indicator_source_url: threat_intel_indicator_source_url block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_source_url SecurityhubInsight#threat_intel_indicator_source_url}
        :param threat_intel_indicator_type: threat_intel_indicator_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_type SecurityhubInsight#threat_intel_indicator_type}
        :param threat_intel_indicator_value: threat_intel_indicator_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_value SecurityhubInsight#threat_intel_indicator_value}
        :param title: title block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#title SecurityhubInsight#title}
        :param type: type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#type SecurityhubInsight#type}
        :param updated_at: updated_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#updated_at SecurityhubInsight#updated_at}
        :param user_defined_values: user_defined_values block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#user_defined_values SecurityhubInsight#user_defined_values}
        :param verification_state: verification_state block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#verification_state SecurityhubInsight#verification_state}
        :param workflow_status: workflow_status block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#workflow_status SecurityhubInsight#workflow_status}
        '''
        value = SecurityhubInsightFilters(
            aws_account_id=aws_account_id,
            company_name=company_name,
            compliance_status=compliance_status,
            confidence=confidence,
            created_at=created_at,
            criticality=criticality,
            description=description,
            finding_provider_fields_confidence=finding_provider_fields_confidence,
            finding_provider_fields_criticality=finding_provider_fields_criticality,
            finding_provider_fields_related_findings_id=finding_provider_fields_related_findings_id,
            finding_provider_fields_related_findings_product_arn=finding_provider_fields_related_findings_product_arn,
            finding_provider_fields_severity_label=finding_provider_fields_severity_label,
            finding_provider_fields_severity_original=finding_provider_fields_severity_original,
            finding_provider_fields_types=finding_provider_fields_types,
            first_observed_at=first_observed_at,
            generator_id=generator_id,
            id=id,
            keyword=keyword,
            last_observed_at=last_observed_at,
            malware_name=malware_name,
            malware_path=malware_path,
            malware_state=malware_state,
            malware_type=malware_type,
            network_destination_domain=network_destination_domain,
            network_destination_ipv4=network_destination_ipv4,
            network_destination_ipv6=network_destination_ipv6,
            network_destination_port=network_destination_port,
            network_direction=network_direction,
            network_protocol=network_protocol,
            network_source_domain=network_source_domain,
            network_source_ipv4=network_source_ipv4,
            network_source_ipv6=network_source_ipv6,
            network_source_mac=network_source_mac,
            network_source_port=network_source_port,
            note_text=note_text,
            note_updated_at=note_updated_at,
            note_updated_by=note_updated_by,
            process_launched_at=process_launched_at,
            process_name=process_name,
            process_parent_pid=process_parent_pid,
            process_path=process_path,
            process_pid=process_pid,
            process_terminated_at=process_terminated_at,
            product_arn=product_arn,
            product_fields=product_fields,
            product_name=product_name,
            recommendation_text=recommendation_text,
            record_state=record_state,
            related_findings_id=related_findings_id,
            related_findings_product_arn=related_findings_product_arn,
            resource_aws_ec2_instance_iam_instance_profile_arn=resource_aws_ec2_instance_iam_instance_profile_arn,
            resource_aws_ec2_instance_image_id=resource_aws_ec2_instance_image_id,
            resource_aws_ec2_instance_ipv4_addresses=resource_aws_ec2_instance_ipv4_addresses,
            resource_aws_ec2_instance_ipv6_addresses=resource_aws_ec2_instance_ipv6_addresses,
            resource_aws_ec2_instance_key_name=resource_aws_ec2_instance_key_name,
            resource_aws_ec2_instance_launched_at=resource_aws_ec2_instance_launched_at,
            resource_aws_ec2_instance_subnet_id=resource_aws_ec2_instance_subnet_id,
            resource_aws_ec2_instance_type=resource_aws_ec2_instance_type,
            resource_aws_ec2_instance_vpc_id=resource_aws_ec2_instance_vpc_id,
            resource_aws_iam_access_key_created_at=resource_aws_iam_access_key_created_at,
            resource_aws_iam_access_key_status=resource_aws_iam_access_key_status,
            resource_aws_iam_access_key_user_name=resource_aws_iam_access_key_user_name,
            resource_aws_s3_bucket_owner_id=resource_aws_s3_bucket_owner_id,
            resource_aws_s3_bucket_owner_name=resource_aws_s3_bucket_owner_name,
            resource_container_image_id=resource_container_image_id,
            resource_container_image_name=resource_container_image_name,
            resource_container_launched_at=resource_container_launched_at,
            resource_container_name=resource_container_name,
            resource_details_other=resource_details_other,
            resource_id=resource_id,
            resource_partition=resource_partition,
            resource_region=resource_region,
            resource_tags=resource_tags,
            resource_type=resource_type,
            severity_label=severity_label,
            source_url=source_url,
            threat_intel_indicator_category=threat_intel_indicator_category,
            threat_intel_indicator_last_observed_at=threat_intel_indicator_last_observed_at,
            threat_intel_indicator_source=threat_intel_indicator_source,
            threat_intel_indicator_source_url=threat_intel_indicator_source_url,
            threat_intel_indicator_type=threat_intel_indicator_type,
            threat_intel_indicator_value=threat_intel_indicator_value,
            title=title,
            type=type,
            updated_at=updated_at,
            user_defined_values=user_defined_values,
            verification_state=verification_state,
            workflow_status=workflow_status,
        )

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

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
    @jsii.member(jsii_name="filters")
    def filters(self) -> "SecurityhubInsightFiltersOutputReference":
        return typing.cast("SecurityhubInsightFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional["SecurityhubInsightFilters"]:
        return typing.cast(typing.Optional["SecurityhubInsightFilters"], jsii.get(self, "filtersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupByAttributeInput")
    def group_by_attribute_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupByAttributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupByAttribute")
    def group_by_attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupByAttribute"))

    @group_by_attribute.setter
    def group_by_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "groupByAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filters": "filters",
        "group_by_attribute": "groupByAttribute",
        "name": "name",
    },
)
class SecurityhubInsightConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filters: "SecurityhubInsightFilters",
        group_by_attribute: builtins.str,
        name: builtins.str,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filters: filters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#filters SecurityhubInsight#filters}
        :param group_by_attribute: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#group_by_attribute SecurityhubInsight#group_by_attribute}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#name SecurityhubInsight#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filters, dict):
            filters = SecurityhubInsightFilters(**filters)
        self._values: typing.Dict[str, typing.Any] = {
            "filters": filters,
            "group_by_attribute": group_by_attribute,
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
    def filters(self) -> "SecurityhubInsightFilters":
        '''filters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#filters SecurityhubInsight#filters}
        '''
        result = self._values.get("filters")
        assert result is not None, "Required property 'filters' is missing"
        return typing.cast("SecurityhubInsightFilters", result)

    @builtins.property
    def group_by_attribute(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#group_by_attribute SecurityhubInsight#group_by_attribute}.'''
        result = self._values.get("group_by_attribute")
        assert result is not None, "Required property 'group_by_attribute' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#name SecurityhubInsight#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFilters",
    jsii_struct_bases=[],
    name_mapping={
        "aws_account_id": "awsAccountId",
        "company_name": "companyName",
        "compliance_status": "complianceStatus",
        "confidence": "confidence",
        "created_at": "createdAt",
        "criticality": "criticality",
        "description": "description",
        "finding_provider_fields_confidence": "findingProviderFieldsConfidence",
        "finding_provider_fields_criticality": "findingProviderFieldsCriticality",
        "finding_provider_fields_related_findings_id": "findingProviderFieldsRelatedFindingsId",
        "finding_provider_fields_related_findings_product_arn": "findingProviderFieldsRelatedFindingsProductArn",
        "finding_provider_fields_severity_label": "findingProviderFieldsSeverityLabel",
        "finding_provider_fields_severity_original": "findingProviderFieldsSeverityOriginal",
        "finding_provider_fields_types": "findingProviderFieldsTypes",
        "first_observed_at": "firstObservedAt",
        "generator_id": "generatorId",
        "id": "id",
        "keyword": "keyword",
        "last_observed_at": "lastObservedAt",
        "malware_name": "malwareName",
        "malware_path": "malwarePath",
        "malware_state": "malwareState",
        "malware_type": "malwareType",
        "network_destination_domain": "networkDestinationDomain",
        "network_destination_ipv4": "networkDestinationIpv4",
        "network_destination_ipv6": "networkDestinationIpv6",
        "network_destination_port": "networkDestinationPort",
        "network_direction": "networkDirection",
        "network_protocol": "networkProtocol",
        "network_source_domain": "networkSourceDomain",
        "network_source_ipv4": "networkSourceIpv4",
        "network_source_ipv6": "networkSourceIpv6",
        "network_source_mac": "networkSourceMac",
        "network_source_port": "networkSourcePort",
        "note_text": "noteText",
        "note_updated_at": "noteUpdatedAt",
        "note_updated_by": "noteUpdatedBy",
        "process_launched_at": "processLaunchedAt",
        "process_name": "processName",
        "process_parent_pid": "processParentPid",
        "process_path": "processPath",
        "process_pid": "processPid",
        "process_terminated_at": "processTerminatedAt",
        "product_arn": "productArn",
        "product_fields": "productFields",
        "product_name": "productName",
        "recommendation_text": "recommendationText",
        "record_state": "recordState",
        "related_findings_id": "relatedFindingsId",
        "related_findings_product_arn": "relatedFindingsProductArn",
        "resource_aws_ec2_instance_iam_instance_profile_arn": "resourceAwsEc2InstanceIamInstanceProfileArn",
        "resource_aws_ec2_instance_image_id": "resourceAwsEc2InstanceImageId",
        "resource_aws_ec2_instance_ipv4_addresses": "resourceAwsEc2InstanceIpv4Addresses",
        "resource_aws_ec2_instance_ipv6_addresses": "resourceAwsEc2InstanceIpv6Addresses",
        "resource_aws_ec2_instance_key_name": "resourceAwsEc2InstanceKeyName",
        "resource_aws_ec2_instance_launched_at": "resourceAwsEc2InstanceLaunchedAt",
        "resource_aws_ec2_instance_subnet_id": "resourceAwsEc2InstanceSubnetId",
        "resource_aws_ec2_instance_type": "resourceAwsEc2InstanceType",
        "resource_aws_ec2_instance_vpc_id": "resourceAwsEc2InstanceVpcId",
        "resource_aws_iam_access_key_created_at": "resourceAwsIamAccessKeyCreatedAt",
        "resource_aws_iam_access_key_status": "resourceAwsIamAccessKeyStatus",
        "resource_aws_iam_access_key_user_name": "resourceAwsIamAccessKeyUserName",
        "resource_aws_s3_bucket_owner_id": "resourceAwsS3BucketOwnerId",
        "resource_aws_s3_bucket_owner_name": "resourceAwsS3BucketOwnerName",
        "resource_container_image_id": "resourceContainerImageId",
        "resource_container_image_name": "resourceContainerImageName",
        "resource_container_launched_at": "resourceContainerLaunchedAt",
        "resource_container_name": "resourceContainerName",
        "resource_details_other": "resourceDetailsOther",
        "resource_id": "resourceId",
        "resource_partition": "resourcePartition",
        "resource_region": "resourceRegion",
        "resource_tags": "resourceTags",
        "resource_type": "resourceType",
        "severity_label": "severityLabel",
        "source_url": "sourceUrl",
        "threat_intel_indicator_category": "threatIntelIndicatorCategory",
        "threat_intel_indicator_last_observed_at": "threatIntelIndicatorLastObservedAt",
        "threat_intel_indicator_source": "threatIntelIndicatorSource",
        "threat_intel_indicator_source_url": "threatIntelIndicatorSourceUrl",
        "threat_intel_indicator_type": "threatIntelIndicatorType",
        "threat_intel_indicator_value": "threatIntelIndicatorValue",
        "title": "title",
        "type": "type",
        "updated_at": "updatedAt",
        "user_defined_values": "userDefinedValues",
        "verification_state": "verificationState",
        "workflow_status": "workflowStatus",
    },
)
class SecurityhubInsightFilters:
    def __init__(
        self,
        *,
        aws_account_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersAwsAccountId"]] = None,
        company_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersCompanyName"]] = None,
        compliance_status: typing.Optional[typing.Sequence["SecurityhubInsightFiltersComplianceStatus"]] = None,
        confidence: typing.Optional[typing.Sequence["SecurityhubInsightFiltersConfidence"]] = None,
        created_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersCreatedAt"]] = None,
        criticality: typing.Optional[typing.Sequence["SecurityhubInsightFiltersCriticality"]] = None,
        description: typing.Optional[typing.Sequence["SecurityhubInsightFiltersDescription"]] = None,
        finding_provider_fields_confidence: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsConfidence"]] = None,
        finding_provider_fields_criticality: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsCriticality"]] = None,
        finding_provider_fields_related_findings_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId"]] = None,
        finding_provider_fields_related_findings_product_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn"]] = None,
        finding_provider_fields_severity_label: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel"]] = None,
        finding_provider_fields_severity_original: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal"]] = None,
        finding_provider_fields_types: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFindingProviderFieldsTypes"]] = None,
        first_observed_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersFirstObservedAt"]] = None,
        generator_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersGeneratorId"]] = None,
        id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersId"]] = None,
        keyword: typing.Optional[typing.Sequence["SecurityhubInsightFiltersKeyword"]] = None,
        last_observed_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersLastObservedAt"]] = None,
        malware_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwareName"]] = None,
        malware_path: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwarePath"]] = None,
        malware_state: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwareState"]] = None,
        malware_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersMalwareType"]] = None,
        network_destination_domain: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationDomain"]] = None,
        network_destination_ipv4: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationIpv4"]] = None,
        network_destination_ipv6: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationIpv6"]] = None,
        network_destination_port: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDestinationPort"]] = None,
        network_direction: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkDirection"]] = None,
        network_protocol: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkProtocol"]] = None,
        network_source_domain: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceDomain"]] = None,
        network_source_ipv4: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceIpv4"]] = None,
        network_source_ipv6: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceIpv6"]] = None,
        network_source_mac: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourceMac"]] = None,
        network_source_port: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNetworkSourcePort"]] = None,
        note_text: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNoteText"]] = None,
        note_updated_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNoteUpdatedAt"]] = None,
        note_updated_by: typing.Optional[typing.Sequence["SecurityhubInsightFiltersNoteUpdatedBy"]] = None,
        process_launched_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessLaunchedAt"]] = None,
        process_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessName"]] = None,
        process_parent_pid: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessParentPid"]] = None,
        process_path: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessPath"]] = None,
        process_pid: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessPid"]] = None,
        process_terminated_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProcessTerminatedAt"]] = None,
        product_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProductArn"]] = None,
        product_fields: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProductFields"]] = None,
        product_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersProductName"]] = None,
        recommendation_text: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRecommendationText"]] = None,
        record_state: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRecordState"]] = None,
        related_findings_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRelatedFindingsId"]] = None,
        related_findings_product_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersRelatedFindingsProductArn"]] = None,
        resource_aws_ec2_instance_iam_instance_profile_arn: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]] = None,
        resource_aws_ec2_instance_image_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]] = None,
        resource_aws_ec2_instance_ipv4_addresses: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]] = None,
        resource_aws_ec2_instance_ipv6_addresses: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]] = None,
        resource_aws_ec2_instance_key_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]] = None,
        resource_aws_ec2_instance_launched_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]] = None,
        resource_aws_ec2_instance_subnet_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]] = None,
        resource_aws_ec2_instance_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]] = None,
        resource_aws_ec2_instance_vpc_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]] = None,
        resource_aws_iam_access_key_created_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]] = None,
        resource_aws_iam_access_key_status: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]] = None,
        resource_aws_iam_access_key_user_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]] = None,
        resource_aws_s3_bucket_owner_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]] = None,
        resource_aws_s3_bucket_owner_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]] = None,
        resource_container_image_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerImageId"]] = None,
        resource_container_image_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerImageName"]] = None,
        resource_container_launched_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerLaunchedAt"]] = None,
        resource_container_name: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceContainerName"]] = None,
        resource_details_other: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceDetailsOther"]] = None,
        resource_id: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceId"]] = None,
        resource_partition: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourcePartition"]] = None,
        resource_region: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceRegion"]] = None,
        resource_tags: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceTags"]] = None,
        resource_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersResourceType"]] = None,
        severity_label: typing.Optional[typing.Sequence["SecurityhubInsightFiltersSeverityLabel"]] = None,
        source_url: typing.Optional[typing.Sequence["SecurityhubInsightFiltersSourceUrl"]] = None,
        threat_intel_indicator_category: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]] = None,
        threat_intel_indicator_last_observed_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]] = None,
        threat_intel_indicator_source: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorSource"]] = None,
        threat_intel_indicator_source_url: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]] = None,
        threat_intel_indicator_type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorType"]] = None,
        threat_intel_indicator_value: typing.Optional[typing.Sequence["SecurityhubInsightFiltersThreatIntelIndicatorValue"]] = None,
        title: typing.Optional[typing.Sequence["SecurityhubInsightFiltersTitle"]] = None,
        type: typing.Optional[typing.Sequence["SecurityhubInsightFiltersType"]] = None,
        updated_at: typing.Optional[typing.Sequence["SecurityhubInsightFiltersUpdatedAt"]] = None,
        user_defined_values: typing.Optional[typing.Sequence["SecurityhubInsightFiltersUserDefinedValues"]] = None,
        verification_state: typing.Optional[typing.Sequence["SecurityhubInsightFiltersVerificationState"]] = None,
        workflow_status: typing.Optional[typing.Sequence["SecurityhubInsightFiltersWorkflowStatus"]] = None,
    ) -> None:
        '''
        :param aws_account_id: aws_account_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#aws_account_id SecurityhubInsight#aws_account_id}
        :param company_name: company_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#company_name SecurityhubInsight#company_name}
        :param compliance_status: compliance_status block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#compliance_status SecurityhubInsight#compliance_status}
        :param confidence: confidence block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#confidence SecurityhubInsight#confidence}
        :param created_at: created_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#created_at SecurityhubInsight#created_at}
        :param criticality: criticality block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#criticality SecurityhubInsight#criticality}
        :param description: description block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#description SecurityhubInsight#description}
        :param finding_provider_fields_confidence: finding_provider_fields_confidence block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_confidence SecurityhubInsight#finding_provider_fields_confidence}
        :param finding_provider_fields_criticality: finding_provider_fields_criticality block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_criticality SecurityhubInsight#finding_provider_fields_criticality}
        :param finding_provider_fields_related_findings_id: finding_provider_fields_related_findings_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_related_findings_id SecurityhubInsight#finding_provider_fields_related_findings_id}
        :param finding_provider_fields_related_findings_product_arn: finding_provider_fields_related_findings_product_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_related_findings_product_arn SecurityhubInsight#finding_provider_fields_related_findings_product_arn}
        :param finding_provider_fields_severity_label: finding_provider_fields_severity_label block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_severity_label SecurityhubInsight#finding_provider_fields_severity_label}
        :param finding_provider_fields_severity_original: finding_provider_fields_severity_original block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_severity_original SecurityhubInsight#finding_provider_fields_severity_original}
        :param finding_provider_fields_types: finding_provider_fields_types block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_types SecurityhubInsight#finding_provider_fields_types}
        :param first_observed_at: first_observed_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#first_observed_at SecurityhubInsight#first_observed_at}
        :param generator_id: generator_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#generator_id SecurityhubInsight#generator_id}
        :param id: id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#id SecurityhubInsight#id}
        :param keyword: keyword block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#keyword SecurityhubInsight#keyword}
        :param last_observed_at: last_observed_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#last_observed_at SecurityhubInsight#last_observed_at}
        :param malware_name: malware_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_name SecurityhubInsight#malware_name}
        :param malware_path: malware_path block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_path SecurityhubInsight#malware_path}
        :param malware_state: malware_state block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_state SecurityhubInsight#malware_state}
        :param malware_type: malware_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_type SecurityhubInsight#malware_type}
        :param network_destination_domain: network_destination_domain block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_domain SecurityhubInsight#network_destination_domain}
        :param network_destination_ipv4: network_destination_ipv4 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_ipv4 SecurityhubInsight#network_destination_ipv4}
        :param network_destination_ipv6: network_destination_ipv6 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_ipv6 SecurityhubInsight#network_destination_ipv6}
        :param network_destination_port: network_destination_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_port SecurityhubInsight#network_destination_port}
        :param network_direction: network_direction block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_direction SecurityhubInsight#network_direction}
        :param network_protocol: network_protocol block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_protocol SecurityhubInsight#network_protocol}
        :param network_source_domain: network_source_domain block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_domain SecurityhubInsight#network_source_domain}
        :param network_source_ipv4: network_source_ipv4 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_ipv4 SecurityhubInsight#network_source_ipv4}
        :param network_source_ipv6: network_source_ipv6 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_ipv6 SecurityhubInsight#network_source_ipv6}
        :param network_source_mac: network_source_mac block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_mac SecurityhubInsight#network_source_mac}
        :param network_source_port: network_source_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_port SecurityhubInsight#network_source_port}
        :param note_text: note_text block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_text SecurityhubInsight#note_text}
        :param note_updated_at: note_updated_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_updated_at SecurityhubInsight#note_updated_at}
        :param note_updated_by: note_updated_by block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_updated_by SecurityhubInsight#note_updated_by}
        :param process_launched_at: process_launched_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_launched_at SecurityhubInsight#process_launched_at}
        :param process_name: process_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_name SecurityhubInsight#process_name}
        :param process_parent_pid: process_parent_pid block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_parent_pid SecurityhubInsight#process_parent_pid}
        :param process_path: process_path block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_path SecurityhubInsight#process_path}
        :param process_pid: process_pid block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_pid SecurityhubInsight#process_pid}
        :param process_terminated_at: process_terminated_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_terminated_at SecurityhubInsight#process_terminated_at}
        :param product_arn: product_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_arn SecurityhubInsight#product_arn}
        :param product_fields: product_fields block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_fields SecurityhubInsight#product_fields}
        :param product_name: product_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_name SecurityhubInsight#product_name}
        :param recommendation_text: recommendation_text block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#recommendation_text SecurityhubInsight#recommendation_text}
        :param record_state: record_state block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#record_state SecurityhubInsight#record_state}
        :param related_findings_id: related_findings_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#related_findings_id SecurityhubInsight#related_findings_id}
        :param related_findings_product_arn: related_findings_product_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#related_findings_product_arn SecurityhubInsight#related_findings_product_arn}
        :param resource_aws_ec2_instance_iam_instance_profile_arn: resource_aws_ec2_instance_iam_instance_profile_arn block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_iam_instance_profile_arn SecurityhubInsight#resource_aws_ec2_instance_iam_instance_profile_arn}
        :param resource_aws_ec2_instance_image_id: resource_aws_ec2_instance_image_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_image_id SecurityhubInsight#resource_aws_ec2_instance_image_id}
        :param resource_aws_ec2_instance_ipv4_addresses: resource_aws_ec2_instance_ipv4_addresses block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_ipv4_addresses SecurityhubInsight#resource_aws_ec2_instance_ipv4_addresses}
        :param resource_aws_ec2_instance_ipv6_addresses: resource_aws_ec2_instance_ipv6_addresses block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_ipv6_addresses SecurityhubInsight#resource_aws_ec2_instance_ipv6_addresses}
        :param resource_aws_ec2_instance_key_name: resource_aws_ec2_instance_key_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_key_name SecurityhubInsight#resource_aws_ec2_instance_key_name}
        :param resource_aws_ec2_instance_launched_at: resource_aws_ec2_instance_launched_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_launched_at SecurityhubInsight#resource_aws_ec2_instance_launched_at}
        :param resource_aws_ec2_instance_subnet_id: resource_aws_ec2_instance_subnet_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_subnet_id SecurityhubInsight#resource_aws_ec2_instance_subnet_id}
        :param resource_aws_ec2_instance_type: resource_aws_ec2_instance_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_type SecurityhubInsight#resource_aws_ec2_instance_type}
        :param resource_aws_ec2_instance_vpc_id: resource_aws_ec2_instance_vpc_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_vpc_id SecurityhubInsight#resource_aws_ec2_instance_vpc_id}
        :param resource_aws_iam_access_key_created_at: resource_aws_iam_access_key_created_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_created_at SecurityhubInsight#resource_aws_iam_access_key_created_at}
        :param resource_aws_iam_access_key_status: resource_aws_iam_access_key_status block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_status SecurityhubInsight#resource_aws_iam_access_key_status}
        :param resource_aws_iam_access_key_user_name: resource_aws_iam_access_key_user_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_user_name SecurityhubInsight#resource_aws_iam_access_key_user_name}
        :param resource_aws_s3_bucket_owner_id: resource_aws_s3_bucket_owner_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_s3_bucket_owner_id SecurityhubInsight#resource_aws_s3_bucket_owner_id}
        :param resource_aws_s3_bucket_owner_name: resource_aws_s3_bucket_owner_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_s3_bucket_owner_name SecurityhubInsight#resource_aws_s3_bucket_owner_name}
        :param resource_container_image_id: resource_container_image_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_image_id SecurityhubInsight#resource_container_image_id}
        :param resource_container_image_name: resource_container_image_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_image_name SecurityhubInsight#resource_container_image_name}
        :param resource_container_launched_at: resource_container_launched_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_launched_at SecurityhubInsight#resource_container_launched_at}
        :param resource_container_name: resource_container_name block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_name SecurityhubInsight#resource_container_name}
        :param resource_details_other: resource_details_other block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_details_other SecurityhubInsight#resource_details_other}
        :param resource_id: resource_id block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_id SecurityhubInsight#resource_id}
        :param resource_partition: resource_partition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_partition SecurityhubInsight#resource_partition}
        :param resource_region: resource_region block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_region SecurityhubInsight#resource_region}
        :param resource_tags: resource_tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_tags SecurityhubInsight#resource_tags}
        :param resource_type: resource_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_type SecurityhubInsight#resource_type}
        :param severity_label: severity_label block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#severity_label SecurityhubInsight#severity_label}
        :param source_url: source_url block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#source_url SecurityhubInsight#source_url}
        :param threat_intel_indicator_category: threat_intel_indicator_category block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_category SecurityhubInsight#threat_intel_indicator_category}
        :param threat_intel_indicator_last_observed_at: threat_intel_indicator_last_observed_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_last_observed_at SecurityhubInsight#threat_intel_indicator_last_observed_at}
        :param threat_intel_indicator_source: threat_intel_indicator_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_source SecurityhubInsight#threat_intel_indicator_source}
        :param threat_intel_indicator_source_url: threat_intel_indicator_source_url block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_source_url SecurityhubInsight#threat_intel_indicator_source_url}
        :param threat_intel_indicator_type: threat_intel_indicator_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_type SecurityhubInsight#threat_intel_indicator_type}
        :param threat_intel_indicator_value: threat_intel_indicator_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_value SecurityhubInsight#threat_intel_indicator_value}
        :param title: title block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#title SecurityhubInsight#title}
        :param type: type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#type SecurityhubInsight#type}
        :param updated_at: updated_at block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#updated_at SecurityhubInsight#updated_at}
        :param user_defined_values: user_defined_values block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#user_defined_values SecurityhubInsight#user_defined_values}
        :param verification_state: verification_state block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#verification_state SecurityhubInsight#verification_state}
        :param workflow_status: workflow_status block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#workflow_status SecurityhubInsight#workflow_status}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if aws_account_id is not None:
            self._values["aws_account_id"] = aws_account_id
        if company_name is not None:
            self._values["company_name"] = company_name
        if compliance_status is not None:
            self._values["compliance_status"] = compliance_status
        if confidence is not None:
            self._values["confidence"] = confidence
        if created_at is not None:
            self._values["created_at"] = created_at
        if criticality is not None:
            self._values["criticality"] = criticality
        if description is not None:
            self._values["description"] = description
        if finding_provider_fields_confidence is not None:
            self._values["finding_provider_fields_confidence"] = finding_provider_fields_confidence
        if finding_provider_fields_criticality is not None:
            self._values["finding_provider_fields_criticality"] = finding_provider_fields_criticality
        if finding_provider_fields_related_findings_id is not None:
            self._values["finding_provider_fields_related_findings_id"] = finding_provider_fields_related_findings_id
        if finding_provider_fields_related_findings_product_arn is not None:
            self._values["finding_provider_fields_related_findings_product_arn"] = finding_provider_fields_related_findings_product_arn
        if finding_provider_fields_severity_label is not None:
            self._values["finding_provider_fields_severity_label"] = finding_provider_fields_severity_label
        if finding_provider_fields_severity_original is not None:
            self._values["finding_provider_fields_severity_original"] = finding_provider_fields_severity_original
        if finding_provider_fields_types is not None:
            self._values["finding_provider_fields_types"] = finding_provider_fields_types
        if first_observed_at is not None:
            self._values["first_observed_at"] = first_observed_at
        if generator_id is not None:
            self._values["generator_id"] = generator_id
        if id is not None:
            self._values["id"] = id
        if keyword is not None:
            self._values["keyword"] = keyword
        if last_observed_at is not None:
            self._values["last_observed_at"] = last_observed_at
        if malware_name is not None:
            self._values["malware_name"] = malware_name
        if malware_path is not None:
            self._values["malware_path"] = malware_path
        if malware_state is not None:
            self._values["malware_state"] = malware_state
        if malware_type is not None:
            self._values["malware_type"] = malware_type
        if network_destination_domain is not None:
            self._values["network_destination_domain"] = network_destination_domain
        if network_destination_ipv4 is not None:
            self._values["network_destination_ipv4"] = network_destination_ipv4
        if network_destination_ipv6 is not None:
            self._values["network_destination_ipv6"] = network_destination_ipv6
        if network_destination_port is not None:
            self._values["network_destination_port"] = network_destination_port
        if network_direction is not None:
            self._values["network_direction"] = network_direction
        if network_protocol is not None:
            self._values["network_protocol"] = network_protocol
        if network_source_domain is not None:
            self._values["network_source_domain"] = network_source_domain
        if network_source_ipv4 is not None:
            self._values["network_source_ipv4"] = network_source_ipv4
        if network_source_ipv6 is not None:
            self._values["network_source_ipv6"] = network_source_ipv6
        if network_source_mac is not None:
            self._values["network_source_mac"] = network_source_mac
        if network_source_port is not None:
            self._values["network_source_port"] = network_source_port
        if note_text is not None:
            self._values["note_text"] = note_text
        if note_updated_at is not None:
            self._values["note_updated_at"] = note_updated_at
        if note_updated_by is not None:
            self._values["note_updated_by"] = note_updated_by
        if process_launched_at is not None:
            self._values["process_launched_at"] = process_launched_at
        if process_name is not None:
            self._values["process_name"] = process_name
        if process_parent_pid is not None:
            self._values["process_parent_pid"] = process_parent_pid
        if process_path is not None:
            self._values["process_path"] = process_path
        if process_pid is not None:
            self._values["process_pid"] = process_pid
        if process_terminated_at is not None:
            self._values["process_terminated_at"] = process_terminated_at
        if product_arn is not None:
            self._values["product_arn"] = product_arn
        if product_fields is not None:
            self._values["product_fields"] = product_fields
        if product_name is not None:
            self._values["product_name"] = product_name
        if recommendation_text is not None:
            self._values["recommendation_text"] = recommendation_text
        if record_state is not None:
            self._values["record_state"] = record_state
        if related_findings_id is not None:
            self._values["related_findings_id"] = related_findings_id
        if related_findings_product_arn is not None:
            self._values["related_findings_product_arn"] = related_findings_product_arn
        if resource_aws_ec2_instance_iam_instance_profile_arn is not None:
            self._values["resource_aws_ec2_instance_iam_instance_profile_arn"] = resource_aws_ec2_instance_iam_instance_profile_arn
        if resource_aws_ec2_instance_image_id is not None:
            self._values["resource_aws_ec2_instance_image_id"] = resource_aws_ec2_instance_image_id
        if resource_aws_ec2_instance_ipv4_addresses is not None:
            self._values["resource_aws_ec2_instance_ipv4_addresses"] = resource_aws_ec2_instance_ipv4_addresses
        if resource_aws_ec2_instance_ipv6_addresses is not None:
            self._values["resource_aws_ec2_instance_ipv6_addresses"] = resource_aws_ec2_instance_ipv6_addresses
        if resource_aws_ec2_instance_key_name is not None:
            self._values["resource_aws_ec2_instance_key_name"] = resource_aws_ec2_instance_key_name
        if resource_aws_ec2_instance_launched_at is not None:
            self._values["resource_aws_ec2_instance_launched_at"] = resource_aws_ec2_instance_launched_at
        if resource_aws_ec2_instance_subnet_id is not None:
            self._values["resource_aws_ec2_instance_subnet_id"] = resource_aws_ec2_instance_subnet_id
        if resource_aws_ec2_instance_type is not None:
            self._values["resource_aws_ec2_instance_type"] = resource_aws_ec2_instance_type
        if resource_aws_ec2_instance_vpc_id is not None:
            self._values["resource_aws_ec2_instance_vpc_id"] = resource_aws_ec2_instance_vpc_id
        if resource_aws_iam_access_key_created_at is not None:
            self._values["resource_aws_iam_access_key_created_at"] = resource_aws_iam_access_key_created_at
        if resource_aws_iam_access_key_status is not None:
            self._values["resource_aws_iam_access_key_status"] = resource_aws_iam_access_key_status
        if resource_aws_iam_access_key_user_name is not None:
            self._values["resource_aws_iam_access_key_user_name"] = resource_aws_iam_access_key_user_name
        if resource_aws_s3_bucket_owner_id is not None:
            self._values["resource_aws_s3_bucket_owner_id"] = resource_aws_s3_bucket_owner_id
        if resource_aws_s3_bucket_owner_name is not None:
            self._values["resource_aws_s3_bucket_owner_name"] = resource_aws_s3_bucket_owner_name
        if resource_container_image_id is not None:
            self._values["resource_container_image_id"] = resource_container_image_id
        if resource_container_image_name is not None:
            self._values["resource_container_image_name"] = resource_container_image_name
        if resource_container_launched_at is not None:
            self._values["resource_container_launched_at"] = resource_container_launched_at
        if resource_container_name is not None:
            self._values["resource_container_name"] = resource_container_name
        if resource_details_other is not None:
            self._values["resource_details_other"] = resource_details_other
        if resource_id is not None:
            self._values["resource_id"] = resource_id
        if resource_partition is not None:
            self._values["resource_partition"] = resource_partition
        if resource_region is not None:
            self._values["resource_region"] = resource_region
        if resource_tags is not None:
            self._values["resource_tags"] = resource_tags
        if resource_type is not None:
            self._values["resource_type"] = resource_type
        if severity_label is not None:
            self._values["severity_label"] = severity_label
        if source_url is not None:
            self._values["source_url"] = source_url
        if threat_intel_indicator_category is not None:
            self._values["threat_intel_indicator_category"] = threat_intel_indicator_category
        if threat_intel_indicator_last_observed_at is not None:
            self._values["threat_intel_indicator_last_observed_at"] = threat_intel_indicator_last_observed_at
        if threat_intel_indicator_source is not None:
            self._values["threat_intel_indicator_source"] = threat_intel_indicator_source
        if threat_intel_indicator_source_url is not None:
            self._values["threat_intel_indicator_source_url"] = threat_intel_indicator_source_url
        if threat_intel_indicator_type is not None:
            self._values["threat_intel_indicator_type"] = threat_intel_indicator_type
        if threat_intel_indicator_value is not None:
            self._values["threat_intel_indicator_value"] = threat_intel_indicator_value
        if title is not None:
            self._values["title"] = title
        if type is not None:
            self._values["type"] = type
        if updated_at is not None:
            self._values["updated_at"] = updated_at
        if user_defined_values is not None:
            self._values["user_defined_values"] = user_defined_values
        if verification_state is not None:
            self._values["verification_state"] = verification_state
        if workflow_status is not None:
            self._values["workflow_status"] = workflow_status

    @builtins.property
    def aws_account_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersAwsAccountId"]]:
        '''aws_account_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#aws_account_id SecurityhubInsight#aws_account_id}
        '''
        result = self._values.get("aws_account_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersAwsAccountId"]], result)

    @builtins.property
    def company_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersCompanyName"]]:
        '''company_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#company_name SecurityhubInsight#company_name}
        '''
        result = self._values.get("company_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersCompanyName"]], result)

    @builtins.property
    def compliance_status(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersComplianceStatus"]]:
        '''compliance_status block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#compliance_status SecurityhubInsight#compliance_status}
        '''
        result = self._values.get("compliance_status")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersComplianceStatus"]], result)

    @builtins.property
    def confidence(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersConfidence"]]:
        '''confidence block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#confidence SecurityhubInsight#confidence}
        '''
        result = self._values.get("confidence")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersConfidence"]], result)

    @builtins.property
    def created_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersCreatedAt"]]:
        '''created_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#created_at SecurityhubInsight#created_at}
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersCreatedAt"]], result)

    @builtins.property
    def criticality(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersCriticality"]]:
        '''criticality block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#criticality SecurityhubInsight#criticality}
        '''
        result = self._values.get("criticality")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersCriticality"]], result)

    @builtins.property
    def description(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersDescription"]]:
        '''description block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#description SecurityhubInsight#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersDescription"]], result)

    @builtins.property
    def finding_provider_fields_confidence(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsConfidence"]]:
        '''finding_provider_fields_confidence block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_confidence SecurityhubInsight#finding_provider_fields_confidence}
        '''
        result = self._values.get("finding_provider_fields_confidence")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsConfidence"]], result)

    @builtins.property
    def finding_provider_fields_criticality(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsCriticality"]]:
        '''finding_provider_fields_criticality block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_criticality SecurityhubInsight#finding_provider_fields_criticality}
        '''
        result = self._values.get("finding_provider_fields_criticality")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsCriticality"]], result)

    @builtins.property
    def finding_provider_fields_related_findings_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId"]]:
        '''finding_provider_fields_related_findings_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_related_findings_id SecurityhubInsight#finding_provider_fields_related_findings_id}
        '''
        result = self._values.get("finding_provider_fields_related_findings_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId"]], result)

    @builtins.property
    def finding_provider_fields_related_findings_product_arn(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn"]]:
        '''finding_provider_fields_related_findings_product_arn block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_related_findings_product_arn SecurityhubInsight#finding_provider_fields_related_findings_product_arn}
        '''
        result = self._values.get("finding_provider_fields_related_findings_product_arn")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn"]], result)

    @builtins.property
    def finding_provider_fields_severity_label(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel"]]:
        '''finding_provider_fields_severity_label block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_severity_label SecurityhubInsight#finding_provider_fields_severity_label}
        '''
        result = self._values.get("finding_provider_fields_severity_label")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel"]], result)

    @builtins.property
    def finding_provider_fields_severity_original(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal"]]:
        '''finding_provider_fields_severity_original block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_severity_original SecurityhubInsight#finding_provider_fields_severity_original}
        '''
        result = self._values.get("finding_provider_fields_severity_original")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal"]], result)

    @builtins.property
    def finding_provider_fields_types(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsTypes"]]:
        '''finding_provider_fields_types block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#finding_provider_fields_types SecurityhubInsight#finding_provider_fields_types}
        '''
        result = self._values.get("finding_provider_fields_types")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFindingProviderFieldsTypes"]], result)

    @builtins.property
    def first_observed_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersFirstObservedAt"]]:
        '''first_observed_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#first_observed_at SecurityhubInsight#first_observed_at}
        '''
        result = self._values.get("first_observed_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersFirstObservedAt"]], result)

    @builtins.property
    def generator_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersGeneratorId"]]:
        '''generator_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#generator_id SecurityhubInsight#generator_id}
        '''
        result = self._values.get("generator_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersGeneratorId"]], result)

    @builtins.property
    def id(self) -> typing.Optional[typing.List["SecurityhubInsightFiltersId"]]:
        '''id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#id SecurityhubInsight#id}
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersId"]], result)

    @builtins.property
    def keyword(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersKeyword"]]:
        '''keyword block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#keyword SecurityhubInsight#keyword}
        '''
        result = self._values.get("keyword")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersKeyword"]], result)

    @builtins.property
    def last_observed_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersLastObservedAt"]]:
        '''last_observed_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#last_observed_at SecurityhubInsight#last_observed_at}
        '''
        result = self._values.get("last_observed_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersLastObservedAt"]], result)

    @builtins.property
    def malware_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersMalwareName"]]:
        '''malware_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_name SecurityhubInsight#malware_name}
        '''
        result = self._values.get("malware_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersMalwareName"]], result)

    @builtins.property
    def malware_path(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersMalwarePath"]]:
        '''malware_path block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_path SecurityhubInsight#malware_path}
        '''
        result = self._values.get("malware_path")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersMalwarePath"]], result)

    @builtins.property
    def malware_state(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersMalwareState"]]:
        '''malware_state block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_state SecurityhubInsight#malware_state}
        '''
        result = self._values.get("malware_state")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersMalwareState"]], result)

    @builtins.property
    def malware_type(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersMalwareType"]]:
        '''malware_type block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#malware_type SecurityhubInsight#malware_type}
        '''
        result = self._values.get("malware_type")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersMalwareType"]], result)

    @builtins.property
    def network_destination_domain(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationDomain"]]:
        '''network_destination_domain block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_domain SecurityhubInsight#network_destination_domain}
        '''
        result = self._values.get("network_destination_domain")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationDomain"]], result)

    @builtins.property
    def network_destination_ipv4(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationIpv4"]]:
        '''network_destination_ipv4 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_ipv4 SecurityhubInsight#network_destination_ipv4}
        '''
        result = self._values.get("network_destination_ipv4")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationIpv4"]], result)

    @builtins.property
    def network_destination_ipv6(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationIpv6"]]:
        '''network_destination_ipv6 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_ipv6 SecurityhubInsight#network_destination_ipv6}
        '''
        result = self._values.get("network_destination_ipv6")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationIpv6"]], result)

    @builtins.property
    def network_destination_port(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationPort"]]:
        '''network_destination_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_destination_port SecurityhubInsight#network_destination_port}
        '''
        result = self._values.get("network_destination_port")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDestinationPort"]], result)

    @builtins.property
    def network_direction(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDirection"]]:
        '''network_direction block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_direction SecurityhubInsight#network_direction}
        '''
        result = self._values.get("network_direction")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkDirection"]], result)

    @builtins.property
    def network_protocol(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkProtocol"]]:
        '''network_protocol block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_protocol SecurityhubInsight#network_protocol}
        '''
        result = self._values.get("network_protocol")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkProtocol"]], result)

    @builtins.property
    def network_source_domain(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceDomain"]]:
        '''network_source_domain block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_domain SecurityhubInsight#network_source_domain}
        '''
        result = self._values.get("network_source_domain")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceDomain"]], result)

    @builtins.property
    def network_source_ipv4(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceIpv4"]]:
        '''network_source_ipv4 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_ipv4 SecurityhubInsight#network_source_ipv4}
        '''
        result = self._values.get("network_source_ipv4")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceIpv4"]], result)

    @builtins.property
    def network_source_ipv6(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceIpv6"]]:
        '''network_source_ipv6 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_ipv6 SecurityhubInsight#network_source_ipv6}
        '''
        result = self._values.get("network_source_ipv6")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceIpv6"]], result)

    @builtins.property
    def network_source_mac(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceMac"]]:
        '''network_source_mac block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_mac SecurityhubInsight#network_source_mac}
        '''
        result = self._values.get("network_source_mac")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourceMac"]], result)

    @builtins.property
    def network_source_port(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourcePort"]]:
        '''network_source_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#network_source_port SecurityhubInsight#network_source_port}
        '''
        result = self._values.get("network_source_port")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNetworkSourcePort"]], result)

    @builtins.property
    def note_text(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNoteText"]]:
        '''note_text block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_text SecurityhubInsight#note_text}
        '''
        result = self._values.get("note_text")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNoteText"]], result)

    @builtins.property
    def note_updated_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNoteUpdatedAt"]]:
        '''note_updated_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_updated_at SecurityhubInsight#note_updated_at}
        '''
        result = self._values.get("note_updated_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNoteUpdatedAt"]], result)

    @builtins.property
    def note_updated_by(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersNoteUpdatedBy"]]:
        '''note_updated_by block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#note_updated_by SecurityhubInsight#note_updated_by}
        '''
        result = self._values.get("note_updated_by")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersNoteUpdatedBy"]], result)

    @builtins.property
    def process_launched_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessLaunchedAt"]]:
        '''process_launched_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_launched_at SecurityhubInsight#process_launched_at}
        '''
        result = self._values.get("process_launched_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessLaunchedAt"]], result)

    @builtins.property
    def process_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessName"]]:
        '''process_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_name SecurityhubInsight#process_name}
        '''
        result = self._values.get("process_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessName"]], result)

    @builtins.property
    def process_parent_pid(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessParentPid"]]:
        '''process_parent_pid block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_parent_pid SecurityhubInsight#process_parent_pid}
        '''
        result = self._values.get("process_parent_pid")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessParentPid"]], result)

    @builtins.property
    def process_path(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessPath"]]:
        '''process_path block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_path SecurityhubInsight#process_path}
        '''
        result = self._values.get("process_path")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessPath"]], result)

    @builtins.property
    def process_pid(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessPid"]]:
        '''process_pid block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_pid SecurityhubInsight#process_pid}
        '''
        result = self._values.get("process_pid")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessPid"]], result)

    @builtins.property
    def process_terminated_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessTerminatedAt"]]:
        '''process_terminated_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#process_terminated_at SecurityhubInsight#process_terminated_at}
        '''
        result = self._values.get("process_terminated_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessTerminatedAt"]], result)

    @builtins.property
    def product_arn(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProductArn"]]:
        '''product_arn block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_arn SecurityhubInsight#product_arn}
        '''
        result = self._values.get("product_arn")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProductArn"]], result)

    @builtins.property
    def product_fields(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProductFields"]]:
        '''product_fields block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_fields SecurityhubInsight#product_fields}
        '''
        result = self._values.get("product_fields")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProductFields"]], result)

    @builtins.property
    def product_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProductName"]]:
        '''product_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#product_name SecurityhubInsight#product_name}
        '''
        result = self._values.get("product_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProductName"]], result)

    @builtins.property
    def recommendation_text(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRecommendationText"]]:
        '''recommendation_text block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#recommendation_text SecurityhubInsight#recommendation_text}
        '''
        result = self._values.get("recommendation_text")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRecommendationText"]], result)

    @builtins.property
    def record_state(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRecordState"]]:
        '''record_state block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#record_state SecurityhubInsight#record_state}
        '''
        result = self._values.get("record_state")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRecordState"]], result)

    @builtins.property
    def related_findings_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsId"]]:
        '''related_findings_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#related_findings_id SecurityhubInsight#related_findings_id}
        '''
        result = self._values.get("related_findings_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsId"]], result)

    @builtins.property
    def related_findings_product_arn(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"]]:
        '''related_findings_product_arn block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#related_findings_product_arn SecurityhubInsight#related_findings_product_arn}
        '''
        result = self._values.get("related_findings_product_arn")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"]], result)

    @builtins.property
    def resource_aws_ec2_instance_iam_instance_profile_arn(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]]:
        '''resource_aws_ec2_instance_iam_instance_profile_arn block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_iam_instance_profile_arn SecurityhubInsight#resource_aws_ec2_instance_iam_instance_profile_arn}
        '''
        result = self._values.get("resource_aws_ec2_instance_iam_instance_profile_arn")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]], result)

    @builtins.property
    def resource_aws_ec2_instance_image_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]]:
        '''resource_aws_ec2_instance_image_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_image_id SecurityhubInsight#resource_aws_ec2_instance_image_id}
        '''
        result = self._values.get("resource_aws_ec2_instance_image_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]], result)

    @builtins.property
    def resource_aws_ec2_instance_ipv4_addresses(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]]:
        '''resource_aws_ec2_instance_ipv4_addresses block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_ipv4_addresses SecurityhubInsight#resource_aws_ec2_instance_ipv4_addresses}
        '''
        result = self._values.get("resource_aws_ec2_instance_ipv4_addresses")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]], result)

    @builtins.property
    def resource_aws_ec2_instance_ipv6_addresses(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]]:
        '''resource_aws_ec2_instance_ipv6_addresses block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_ipv6_addresses SecurityhubInsight#resource_aws_ec2_instance_ipv6_addresses}
        '''
        result = self._values.get("resource_aws_ec2_instance_ipv6_addresses")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]], result)

    @builtins.property
    def resource_aws_ec2_instance_key_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]]:
        '''resource_aws_ec2_instance_key_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_key_name SecurityhubInsight#resource_aws_ec2_instance_key_name}
        '''
        result = self._values.get("resource_aws_ec2_instance_key_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]], result)

    @builtins.property
    def resource_aws_ec2_instance_launched_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]]:
        '''resource_aws_ec2_instance_launched_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_launched_at SecurityhubInsight#resource_aws_ec2_instance_launched_at}
        '''
        result = self._values.get("resource_aws_ec2_instance_launched_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]], result)

    @builtins.property
    def resource_aws_ec2_instance_subnet_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]]:
        '''resource_aws_ec2_instance_subnet_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_subnet_id SecurityhubInsight#resource_aws_ec2_instance_subnet_id}
        '''
        result = self._values.get("resource_aws_ec2_instance_subnet_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]], result)

    @builtins.property
    def resource_aws_ec2_instance_type(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]]:
        '''resource_aws_ec2_instance_type block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_type SecurityhubInsight#resource_aws_ec2_instance_type}
        '''
        result = self._values.get("resource_aws_ec2_instance_type")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]], result)

    @builtins.property
    def resource_aws_ec2_instance_vpc_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]]:
        '''resource_aws_ec2_instance_vpc_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_ec2_instance_vpc_id SecurityhubInsight#resource_aws_ec2_instance_vpc_id}
        '''
        result = self._values.get("resource_aws_ec2_instance_vpc_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]], result)

    @builtins.property
    def resource_aws_iam_access_key_created_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]]:
        '''resource_aws_iam_access_key_created_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_created_at SecurityhubInsight#resource_aws_iam_access_key_created_at}
        '''
        result = self._values.get("resource_aws_iam_access_key_created_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]], result)

    @builtins.property
    def resource_aws_iam_access_key_status(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]]:
        '''resource_aws_iam_access_key_status block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_status SecurityhubInsight#resource_aws_iam_access_key_status}
        '''
        result = self._values.get("resource_aws_iam_access_key_status")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]], result)

    @builtins.property
    def resource_aws_iam_access_key_user_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]]:
        '''resource_aws_iam_access_key_user_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_iam_access_key_user_name SecurityhubInsight#resource_aws_iam_access_key_user_name}
        '''
        result = self._values.get("resource_aws_iam_access_key_user_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]], result)

    @builtins.property
    def resource_aws_s3_bucket_owner_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]]:
        '''resource_aws_s3_bucket_owner_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_s3_bucket_owner_id SecurityhubInsight#resource_aws_s3_bucket_owner_id}
        '''
        result = self._values.get("resource_aws_s3_bucket_owner_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]], result)

    @builtins.property
    def resource_aws_s3_bucket_owner_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]]:
        '''resource_aws_s3_bucket_owner_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_aws_s3_bucket_owner_name SecurityhubInsight#resource_aws_s3_bucket_owner_name}
        '''
        result = self._values.get("resource_aws_s3_bucket_owner_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]], result)

    @builtins.property
    def resource_container_image_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageId"]]:
        '''resource_container_image_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_image_id SecurityhubInsight#resource_container_image_id}
        '''
        result = self._values.get("resource_container_image_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageId"]], result)

    @builtins.property
    def resource_container_image_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageName"]]:
        '''resource_container_image_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_image_name SecurityhubInsight#resource_container_image_name}
        '''
        result = self._values.get("resource_container_image_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageName"]], result)

    @builtins.property
    def resource_container_launched_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"]]:
        '''resource_container_launched_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_launched_at SecurityhubInsight#resource_container_launched_at}
        '''
        result = self._values.get("resource_container_launched_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"]], result)

    @builtins.property
    def resource_container_name(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerName"]]:
        '''resource_container_name block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_container_name SecurityhubInsight#resource_container_name}
        '''
        result = self._values.get("resource_container_name")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerName"]], result)

    @builtins.property
    def resource_details_other(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceDetailsOther"]]:
        '''resource_details_other block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_details_other SecurityhubInsight#resource_details_other}
        '''
        result = self._values.get("resource_details_other")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceDetailsOther"]], result)

    @builtins.property
    def resource_id(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceId"]]:
        '''resource_id block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_id SecurityhubInsight#resource_id}
        '''
        result = self._values.get("resource_id")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceId"]], result)

    @builtins.property
    def resource_partition(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourcePartition"]]:
        '''resource_partition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_partition SecurityhubInsight#resource_partition}
        '''
        result = self._values.get("resource_partition")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourcePartition"]], result)

    @builtins.property
    def resource_region(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceRegion"]]:
        '''resource_region block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_region SecurityhubInsight#resource_region}
        '''
        result = self._values.get("resource_region")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceRegion"]], result)

    @builtins.property
    def resource_tags(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceTags"]]:
        '''resource_tags block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_tags SecurityhubInsight#resource_tags}
        '''
        result = self._values.get("resource_tags")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceTags"]], result)

    @builtins.property
    def resource_type(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceType"]]:
        '''resource_type block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#resource_type SecurityhubInsight#resource_type}
        '''
        result = self._values.get("resource_type")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceType"]], result)

    @builtins.property
    def severity_label(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersSeverityLabel"]]:
        '''severity_label block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#severity_label SecurityhubInsight#severity_label}
        '''
        result = self._values.get("severity_label")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersSeverityLabel"]], result)

    @builtins.property
    def source_url(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersSourceUrl"]]:
        '''source_url block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#source_url SecurityhubInsight#source_url}
        '''
        result = self._values.get("source_url")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersSourceUrl"]], result)

    @builtins.property
    def threat_intel_indicator_category(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]]:
        '''threat_intel_indicator_category block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_category SecurityhubInsight#threat_intel_indicator_category}
        '''
        result = self._values.get("threat_intel_indicator_category")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]], result)

    @builtins.property
    def threat_intel_indicator_last_observed_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]]:
        '''threat_intel_indicator_last_observed_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_last_observed_at SecurityhubInsight#threat_intel_indicator_last_observed_at}
        '''
        result = self._values.get("threat_intel_indicator_last_observed_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]], result)

    @builtins.property
    def threat_intel_indicator_source(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"]]:
        '''threat_intel_indicator_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_source SecurityhubInsight#threat_intel_indicator_source}
        '''
        result = self._values.get("threat_intel_indicator_source")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"]], result)

    @builtins.property
    def threat_intel_indicator_source_url(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]]:
        '''threat_intel_indicator_source_url block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_source_url SecurityhubInsight#threat_intel_indicator_source_url}
        '''
        result = self._values.get("threat_intel_indicator_source_url")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]], result)

    @builtins.property
    def threat_intel_indicator_type(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"]]:
        '''threat_intel_indicator_type block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_type SecurityhubInsight#threat_intel_indicator_type}
        '''
        result = self._values.get("threat_intel_indicator_type")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"]], result)

    @builtins.property
    def threat_intel_indicator_value(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"]]:
        '''threat_intel_indicator_value block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#threat_intel_indicator_value SecurityhubInsight#threat_intel_indicator_value}
        '''
        result = self._values.get("threat_intel_indicator_value")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"]], result)

    @builtins.property
    def title(self) -> typing.Optional[typing.List["SecurityhubInsightFiltersTitle"]]:
        '''title block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#title SecurityhubInsight#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersTitle"]], result)

    @builtins.property
    def type(self) -> typing.Optional[typing.List["SecurityhubInsightFiltersType"]]:
        '''type block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#type SecurityhubInsight#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersType"]], result)

    @builtins.property
    def updated_at(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersUpdatedAt"]]:
        '''updated_at block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#updated_at SecurityhubInsight#updated_at}
        '''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersUpdatedAt"]], result)

    @builtins.property
    def user_defined_values(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersUserDefinedValues"]]:
        '''user_defined_values block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#user_defined_values SecurityhubInsight#user_defined_values}
        '''
        result = self._values.get("user_defined_values")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersUserDefinedValues"]], result)

    @builtins.property
    def verification_state(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersVerificationState"]]:
        '''verification_state block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#verification_state SecurityhubInsight#verification_state}
        '''
        result = self._values.get("verification_state")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersVerificationState"]], result)

    @builtins.property
    def workflow_status(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersWorkflowStatus"]]:
        '''workflow_status block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#workflow_status SecurityhubInsight#workflow_status}
        '''
        result = self._values.get("workflow_status")
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersWorkflowStatus"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersAwsAccountId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersAwsAccountId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersAwsAccountId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersCompanyName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersCompanyName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersCompanyName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersComplianceStatus",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersComplianceStatus:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersComplianceStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersConfidence",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersConfidence:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersConfidence(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersCreatedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersCreatedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersCreatedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersCreatedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersCreatedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersCreatedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersCreatedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersCreatedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersCreatedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersCreatedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersCreatedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersCreatedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersCreatedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersCreatedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersCreatedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersCriticality",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersCriticality:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersCriticality(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersDescription",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersDescription:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersDescription(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsConfidence",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersFindingProviderFieldsConfidence:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsConfidence(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsCriticality",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersFindingProviderFieldsCriticality:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsCriticality(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFindingProviderFieldsTypes",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersFindingProviderFieldsTypes:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFindingProviderFieldsTypes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFirstObservedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersFirstObservedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersFirstObservedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersFirstObservedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersFirstObservedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersFirstObservedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFirstObservedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFirstObservedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersFirstObservedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersFirstObservedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersFirstObservedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersFirstObservedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersFirstObservedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersFirstObservedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersFirstObservedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersGeneratorId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersGeneratorId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersGeneratorId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersKeyword",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class SecurityhubInsightFiltersKeyword:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersKeyword(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersLastObservedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersLastObservedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersLastObservedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersLastObservedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersLastObservedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersLastObservedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersLastObservedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersLastObservedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersLastObservedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersLastObservedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersLastObservedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersLastObservedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersLastObservedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersLastObservedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersLastObservedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersMalwareName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersMalwareName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersMalwareName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersMalwarePath",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersMalwarePath:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersMalwarePath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersMalwareState",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersMalwareState:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersMalwareState(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersMalwareType",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersMalwareType:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersMalwareType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkDestinationDomain",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNetworkDestinationDomain:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkDestinationDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkDestinationIpv4",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class SecurityhubInsightFiltersNetworkDestinationIpv4:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkDestinationIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkDestinationIpv6",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class SecurityhubInsightFiltersNetworkDestinationIpv6:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkDestinationIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkDestinationPort",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersNetworkDestinationPort:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkDestinationPort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkDirection",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNetworkDirection:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkDirection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkProtocol",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNetworkProtocol:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkProtocol(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkSourceDomain",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNetworkSourceDomain:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkSourceDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkSourceIpv4",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class SecurityhubInsightFiltersNetworkSourceIpv4:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkSourceIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkSourceIpv6",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class SecurityhubInsightFiltersNetworkSourceIpv6:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkSourceIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkSourceMac",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNetworkSourceMac:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkSourceMac(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNetworkSourcePort",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersNetworkSourcePort:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNetworkSourcePort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNoteText",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNoteText:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNoteText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNoteUpdatedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersNoteUpdatedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersNoteUpdatedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersNoteUpdatedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersNoteUpdatedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersNoteUpdatedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNoteUpdatedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNoteUpdatedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersNoteUpdatedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNoteUpdatedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersNoteUpdatedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNoteUpdatedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersNoteUpdatedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersNoteUpdatedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersNoteUpdatedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersNoteUpdatedBy",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersNoteUpdatedBy:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersNoteUpdatedBy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersOutputReference",
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

    @jsii.member(jsii_name="resetAwsAccountId")
    def reset_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccountId", []))

    @jsii.member(jsii_name="resetCompanyName")
    def reset_company_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompanyName", []))

    @jsii.member(jsii_name="resetComplianceStatus")
    def reset_compliance_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplianceStatus", []))

    @jsii.member(jsii_name="resetConfidence")
    def reset_confidence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfidence", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetCriticality")
    def reset_criticality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCriticality", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsConfidence")
    def reset_finding_provider_fields_confidence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsConfidence", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsCriticality")
    def reset_finding_provider_fields_criticality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsCriticality", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsRelatedFindingsId")
    def reset_finding_provider_fields_related_findings_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsRelatedFindingsId", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsRelatedFindingsProductArn")
    def reset_finding_provider_fields_related_findings_product_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsRelatedFindingsProductArn", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsSeverityLabel")
    def reset_finding_provider_fields_severity_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsSeverityLabel", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsSeverityOriginal")
    def reset_finding_provider_fields_severity_original(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsSeverityOriginal", []))

    @jsii.member(jsii_name="resetFindingProviderFieldsTypes")
    def reset_finding_provider_fields_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFindingProviderFieldsTypes", []))

    @jsii.member(jsii_name="resetFirstObservedAt")
    def reset_first_observed_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstObservedAt", []))

    @jsii.member(jsii_name="resetGeneratorId")
    def reset_generator_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeneratorId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyword")
    def reset_keyword(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyword", []))

    @jsii.member(jsii_name="resetLastObservedAt")
    def reset_last_observed_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastObservedAt", []))

    @jsii.member(jsii_name="resetMalwareName")
    def reset_malware_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMalwareName", []))

    @jsii.member(jsii_name="resetMalwarePath")
    def reset_malware_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMalwarePath", []))

    @jsii.member(jsii_name="resetMalwareState")
    def reset_malware_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMalwareState", []))

    @jsii.member(jsii_name="resetMalwareType")
    def reset_malware_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMalwareType", []))

    @jsii.member(jsii_name="resetNetworkDestinationDomain")
    def reset_network_destination_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkDestinationDomain", []))

    @jsii.member(jsii_name="resetNetworkDestinationIpv4")
    def reset_network_destination_ipv4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkDestinationIpv4", []))

    @jsii.member(jsii_name="resetNetworkDestinationIpv6")
    def reset_network_destination_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkDestinationIpv6", []))

    @jsii.member(jsii_name="resetNetworkDestinationPort")
    def reset_network_destination_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkDestinationPort", []))

    @jsii.member(jsii_name="resetNetworkDirection")
    def reset_network_direction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkDirection", []))

    @jsii.member(jsii_name="resetNetworkProtocol")
    def reset_network_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkProtocol", []))

    @jsii.member(jsii_name="resetNetworkSourceDomain")
    def reset_network_source_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSourceDomain", []))

    @jsii.member(jsii_name="resetNetworkSourceIpv4")
    def reset_network_source_ipv4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSourceIpv4", []))

    @jsii.member(jsii_name="resetNetworkSourceIpv6")
    def reset_network_source_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSourceIpv6", []))

    @jsii.member(jsii_name="resetNetworkSourceMac")
    def reset_network_source_mac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSourceMac", []))

    @jsii.member(jsii_name="resetNetworkSourcePort")
    def reset_network_source_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSourcePort", []))

    @jsii.member(jsii_name="resetNoteText")
    def reset_note_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoteText", []))

    @jsii.member(jsii_name="resetNoteUpdatedAt")
    def reset_note_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoteUpdatedAt", []))

    @jsii.member(jsii_name="resetNoteUpdatedBy")
    def reset_note_updated_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoteUpdatedBy", []))

    @jsii.member(jsii_name="resetProcessLaunchedAt")
    def reset_process_launched_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessLaunchedAt", []))

    @jsii.member(jsii_name="resetProcessName")
    def reset_process_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessName", []))

    @jsii.member(jsii_name="resetProcessParentPid")
    def reset_process_parent_pid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessParentPid", []))

    @jsii.member(jsii_name="resetProcessPath")
    def reset_process_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessPath", []))

    @jsii.member(jsii_name="resetProcessPid")
    def reset_process_pid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessPid", []))

    @jsii.member(jsii_name="resetProcessTerminatedAt")
    def reset_process_terminated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProcessTerminatedAt", []))

    @jsii.member(jsii_name="resetProductArn")
    def reset_product_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductArn", []))

    @jsii.member(jsii_name="resetProductFields")
    def reset_product_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductFields", []))

    @jsii.member(jsii_name="resetProductName")
    def reset_product_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductName", []))

    @jsii.member(jsii_name="resetRecommendationText")
    def reset_recommendation_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecommendationText", []))

    @jsii.member(jsii_name="resetRecordState")
    def reset_record_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordState", []))

    @jsii.member(jsii_name="resetRelatedFindingsId")
    def reset_related_findings_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRelatedFindingsId", []))

    @jsii.member(jsii_name="resetRelatedFindingsProductArn")
    def reset_related_findings_product_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRelatedFindingsProductArn", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceIamInstanceProfileArn")
    def reset_resource_aws_ec2_instance_iam_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceIamInstanceProfileArn", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceImageId")
    def reset_resource_aws_ec2_instance_image_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceImageId", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceIpv4Addresses")
    def reset_resource_aws_ec2_instance_ipv4_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceIpv4Addresses", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceIpv6Addresses")
    def reset_resource_aws_ec2_instance_ipv6_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceIpv6Addresses", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceKeyName")
    def reset_resource_aws_ec2_instance_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceKeyName", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceLaunchedAt")
    def reset_resource_aws_ec2_instance_launched_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceLaunchedAt", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceSubnetId")
    def reset_resource_aws_ec2_instance_subnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceSubnetId", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceType")
    def reset_resource_aws_ec2_instance_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceType", []))

    @jsii.member(jsii_name="resetResourceAwsEc2InstanceVpcId")
    def reset_resource_aws_ec2_instance_vpc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsEc2InstanceVpcId", []))

    @jsii.member(jsii_name="resetResourceAwsIamAccessKeyCreatedAt")
    def reset_resource_aws_iam_access_key_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsIamAccessKeyCreatedAt", []))

    @jsii.member(jsii_name="resetResourceAwsIamAccessKeyStatus")
    def reset_resource_aws_iam_access_key_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsIamAccessKeyStatus", []))

    @jsii.member(jsii_name="resetResourceAwsIamAccessKeyUserName")
    def reset_resource_aws_iam_access_key_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsIamAccessKeyUserName", []))

    @jsii.member(jsii_name="resetResourceAwsS3BucketOwnerId")
    def reset_resource_aws_s3_bucket_owner_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsS3BucketOwnerId", []))

    @jsii.member(jsii_name="resetResourceAwsS3BucketOwnerName")
    def reset_resource_aws_s3_bucket_owner_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceAwsS3BucketOwnerName", []))

    @jsii.member(jsii_name="resetResourceContainerImageId")
    def reset_resource_container_image_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceContainerImageId", []))

    @jsii.member(jsii_name="resetResourceContainerImageName")
    def reset_resource_container_image_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceContainerImageName", []))

    @jsii.member(jsii_name="resetResourceContainerLaunchedAt")
    def reset_resource_container_launched_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceContainerLaunchedAt", []))

    @jsii.member(jsii_name="resetResourceContainerName")
    def reset_resource_container_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceContainerName", []))

    @jsii.member(jsii_name="resetResourceDetailsOther")
    def reset_resource_details_other(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceDetailsOther", []))

    @jsii.member(jsii_name="resetResourceId")
    def reset_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceId", []))

    @jsii.member(jsii_name="resetResourcePartition")
    def reset_resource_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourcePartition", []))

    @jsii.member(jsii_name="resetResourceRegion")
    def reset_resource_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceRegion", []))

    @jsii.member(jsii_name="resetResourceTags")
    def reset_resource_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTags", []))

    @jsii.member(jsii_name="resetResourceType")
    def reset_resource_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceType", []))

    @jsii.member(jsii_name="resetSeverityLabel")
    def reset_severity_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeverityLabel", []))

    @jsii.member(jsii_name="resetSourceUrl")
    def reset_source_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceUrl", []))

    @jsii.member(jsii_name="resetThreatIntelIndicatorCategory")
    def reset_threat_intel_indicator_category(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreatIntelIndicatorCategory", []))

    @jsii.member(jsii_name="resetThreatIntelIndicatorLastObservedAt")
    def reset_threat_intel_indicator_last_observed_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreatIntelIndicatorLastObservedAt", []))

    @jsii.member(jsii_name="resetThreatIntelIndicatorSource")
    def reset_threat_intel_indicator_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreatIntelIndicatorSource", []))

    @jsii.member(jsii_name="resetThreatIntelIndicatorSourceUrl")
    def reset_threat_intel_indicator_source_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreatIntelIndicatorSourceUrl", []))

    @jsii.member(jsii_name="resetThreatIntelIndicatorType")
    def reset_threat_intel_indicator_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreatIntelIndicatorType", []))

    @jsii.member(jsii_name="resetThreatIntelIndicatorValue")
    def reset_threat_intel_indicator_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreatIntelIndicatorValue", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @jsii.member(jsii_name="resetUserDefinedValues")
    def reset_user_defined_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDefinedValues", []))

    @jsii.member(jsii_name="resetVerificationState")
    def reset_verification_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerificationState", []))

    @jsii.member(jsii_name="resetWorkflowStatus")
    def reset_workflow_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkflowStatus", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountIdInput")
    def aws_account_id_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersAwsAccountId]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersAwsAccountId]], jsii.get(self, "awsAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="companyNameInput")
    def company_name_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersCompanyName]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersCompanyName]], jsii.get(self, "companyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="complianceStatusInput")
    def compliance_status_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersComplianceStatus]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersComplianceStatus]], jsii.get(self, "complianceStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confidenceInput")
    def confidence_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersConfidence]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersConfidence]], jsii.get(self, "confidenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersCreatedAt]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersCreatedAt]], jsii.get(self, "createdAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criticalityInput")
    def criticality_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersCriticality]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersCriticality]], jsii.get(self, "criticalityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersDescription]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersDescription]], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsConfidenceInput")
    def finding_provider_fields_confidence_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsConfidence]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsConfidence]], jsii.get(self, "findingProviderFieldsConfidenceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsCriticalityInput")
    def finding_provider_fields_criticality_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsCriticality]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsCriticality]], jsii.get(self, "findingProviderFieldsCriticalityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsRelatedFindingsIdInput")
    def finding_provider_fields_related_findings_id_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId]], jsii.get(self, "findingProviderFieldsRelatedFindingsIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsRelatedFindingsProductArnInput")
    def finding_provider_fields_related_findings_product_arn_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn]], jsii.get(self, "findingProviderFieldsRelatedFindingsProductArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsSeverityLabelInput")
    def finding_provider_fields_severity_label_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel]], jsii.get(self, "findingProviderFieldsSeverityLabelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsSeverityOriginalInput")
    def finding_provider_fields_severity_original_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal]], jsii.get(self, "findingProviderFieldsSeverityOriginalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsTypesInput")
    def finding_provider_fields_types_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsTypes]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFindingProviderFieldsTypes]], jsii.get(self, "findingProviderFieldsTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firstObservedAtInput")
    def first_observed_at_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersFirstObservedAt]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersFirstObservedAt]], jsii.get(self, "firstObservedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatorIdInput")
    def generator_id_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersGeneratorId]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersGeneratorId]], jsii.get(self, "generatorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[typing.List[SecurityhubInsightFiltersId]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersId]], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keywordInput")
    def keyword_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersKeyword]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersKeyword]], jsii.get(self, "keywordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastObservedAtInput")
    def last_observed_at_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersLastObservedAt]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersLastObservedAt]], jsii.get(self, "lastObservedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwareNameInput")
    def malware_name_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersMalwareName]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersMalwareName]], jsii.get(self, "malwareNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwarePathInput")
    def malware_path_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersMalwarePath]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersMalwarePath]], jsii.get(self, "malwarePathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwareStateInput")
    def malware_state_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersMalwareState]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersMalwareState]], jsii.get(self, "malwareStateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwareTypeInput")
    def malware_type_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersMalwareType]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersMalwareType]], jsii.get(self, "malwareTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationDomainInput")
    def network_destination_domain_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationDomain]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationDomain]], jsii.get(self, "networkDestinationDomainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationIpv4Input")
    def network_destination_ipv4_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationIpv4]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationIpv4]], jsii.get(self, "networkDestinationIpv4Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationIpv6Input")
    def network_destination_ipv6_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationIpv6]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationIpv6]], jsii.get(self, "networkDestinationIpv6Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationPortInput")
    def network_destination_port_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationPort]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDestinationPort]], jsii.get(self, "networkDestinationPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDirectionInput")
    def network_direction_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDirection]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkDirection]], jsii.get(self, "networkDirectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkProtocolInput")
    def network_protocol_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkProtocol]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkProtocol]], jsii.get(self, "networkProtocolInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceDomainInput")
    def network_source_domain_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceDomain]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceDomain]], jsii.get(self, "networkSourceDomainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceIpv4Input")
    def network_source_ipv4_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceIpv4]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceIpv4]], jsii.get(self, "networkSourceIpv4Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceIpv6Input")
    def network_source_ipv6_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceIpv6]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceIpv6]], jsii.get(self, "networkSourceIpv6Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceMacInput")
    def network_source_mac_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceMac]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourceMac]], jsii.get(self, "networkSourceMacInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourcePortInput")
    def network_source_port_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourcePort]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNetworkSourcePort]], jsii.get(self, "networkSourcePortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteTextInput")
    def note_text_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNoteText]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNoteText]], jsii.get(self, "noteTextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteUpdatedAtInput")
    def note_updated_at_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNoteUpdatedAt]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNoteUpdatedAt]], jsii.get(self, "noteUpdatedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteUpdatedByInput")
    def note_updated_by_input(
        self,
    ) -> typing.Optional[typing.List[SecurityhubInsightFiltersNoteUpdatedBy]]:
        return typing.cast(typing.Optional[typing.List[SecurityhubInsightFiltersNoteUpdatedBy]], jsii.get(self, "noteUpdatedByInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processLaunchedAtInput")
    def process_launched_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessLaunchedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessLaunchedAt"]], jsii.get(self, "processLaunchedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processNameInput")
    def process_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessName"]], jsii.get(self, "processNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processParentPidInput")
    def process_parent_pid_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessParentPid"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessParentPid"]], jsii.get(self, "processParentPidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processPathInput")
    def process_path_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessPath"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessPath"]], jsii.get(self, "processPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processPidInput")
    def process_pid_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessPid"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessPid"]], jsii.get(self, "processPidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processTerminatedAtInput")
    def process_terminated_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProcessTerminatedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProcessTerminatedAt"]], jsii.get(self, "processTerminatedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArnInput")
    def product_arn_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProductArn"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProductArn"]], jsii.get(self, "productArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productFieldsInput")
    def product_fields_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProductFields"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProductFields"]], jsii.get(self, "productFieldsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productNameInput")
    def product_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersProductName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersProductName"]], jsii.get(self, "productNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recommendationTextInput")
    def recommendation_text_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRecommendationText"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRecommendationText"]], jsii.get(self, "recommendationTextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordStateInput")
    def record_state_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRecordState"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRecordState"]], jsii.get(self, "recordStateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="relatedFindingsIdInput")
    def related_findings_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsId"]], jsii.get(self, "relatedFindingsIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="relatedFindingsProductArnInput")
    def related_findings_product_arn_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"]], jsii.get(self, "relatedFindingsProductArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceIamInstanceProfileArnInput")
    def resource_aws_ec2_instance_iam_instance_profile_arn_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]], jsii.get(self, "resourceAwsEc2InstanceIamInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceImageIdInput")
    def resource_aws_ec2_instance_image_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]], jsii.get(self, "resourceAwsEc2InstanceImageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceIpv4AddressesInput")
    def resource_aws_ec2_instance_ipv4_addresses_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]], jsii.get(self, "resourceAwsEc2InstanceIpv4AddressesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceIpv6AddressesInput")
    def resource_aws_ec2_instance_ipv6_addresses_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]], jsii.get(self, "resourceAwsEc2InstanceIpv6AddressesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceKeyNameInput")
    def resource_aws_ec2_instance_key_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]], jsii.get(self, "resourceAwsEc2InstanceKeyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceLaunchedAtInput")
    def resource_aws_ec2_instance_launched_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]], jsii.get(self, "resourceAwsEc2InstanceLaunchedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceSubnetIdInput")
    def resource_aws_ec2_instance_subnet_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]], jsii.get(self, "resourceAwsEc2InstanceSubnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceTypeInput")
    def resource_aws_ec2_instance_type_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]], jsii.get(self, "resourceAwsEc2InstanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceVpcIdInput")
    def resource_aws_ec2_instance_vpc_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]], jsii.get(self, "resourceAwsEc2InstanceVpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsIamAccessKeyCreatedAtInput")
    def resource_aws_iam_access_key_created_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]], jsii.get(self, "resourceAwsIamAccessKeyCreatedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsIamAccessKeyStatusInput")
    def resource_aws_iam_access_key_status_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]], jsii.get(self, "resourceAwsIamAccessKeyStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsIamAccessKeyUserNameInput")
    def resource_aws_iam_access_key_user_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]], jsii.get(self, "resourceAwsIamAccessKeyUserNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsS3BucketOwnerIdInput")
    def resource_aws_s3_bucket_owner_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]], jsii.get(self, "resourceAwsS3BucketOwnerIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsS3BucketOwnerNameInput")
    def resource_aws_s3_bucket_owner_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]], jsii.get(self, "resourceAwsS3BucketOwnerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerImageIdInput")
    def resource_container_image_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageId"]], jsii.get(self, "resourceContainerImageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerImageNameInput")
    def resource_container_image_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerImageName"]], jsii.get(self, "resourceContainerImageNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerLaunchedAtInput")
    def resource_container_launched_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"]], jsii.get(self, "resourceContainerLaunchedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerNameInput")
    def resource_container_name_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerName"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceContainerName"]], jsii.get(self, "resourceContainerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceDetailsOtherInput")
    def resource_details_other_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceDetailsOther"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceDetailsOther"]], jsii.get(self, "resourceDetailsOtherInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdInput")
    def resource_id_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceId"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceId"]], jsii.get(self, "resourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcePartitionInput")
    def resource_partition_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourcePartition"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourcePartition"]], jsii.get(self, "resourcePartitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceRegionInput")
    def resource_region_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceRegion"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceRegion"]], jsii.get(self, "resourceRegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTagsInput")
    def resource_tags_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceTags"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceTags"]], jsii.get(self, "resourceTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeInput")
    def resource_type_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersResourceType"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersResourceType"]], jsii.get(self, "resourceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="severityLabelInput")
    def severity_label_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersSeverityLabel"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersSeverityLabel"]], jsii.get(self, "severityLabelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceUrlInput")
    def source_url_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersSourceUrl"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersSourceUrl"]], jsii.get(self, "sourceUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorCategoryInput")
    def threat_intel_indicator_category_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]], jsii.get(self, "threatIntelIndicatorCategoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorLastObservedAtInput")
    def threat_intel_indicator_last_observed_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]], jsii.get(self, "threatIntelIndicatorLastObservedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorSourceInput")
    def threat_intel_indicator_source_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"]], jsii.get(self, "threatIntelIndicatorSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorSourceUrlInput")
    def threat_intel_indicator_source_url_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]], jsii.get(self, "threatIntelIndicatorSourceUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorTypeInput")
    def threat_intel_indicator_type_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"]], jsii.get(self, "threatIntelIndicatorTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorValueInput")
    def threat_intel_indicator_value_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"]], jsii.get(self, "threatIntelIndicatorValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersTitle"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersTitle"]], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersType"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersType"]], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersUpdatedAt"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersUpdatedAt"]], jsii.get(self, "updatedAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDefinedValuesInput")
    def user_defined_values_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersUserDefinedValues"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersUserDefinedValues"]], jsii.get(self, "userDefinedValuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationStateInput")
    def verification_state_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersVerificationState"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersVerificationState"]], jsii.get(self, "verificationStateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowStatusInput")
    def workflow_status_input(
        self,
    ) -> typing.Optional[typing.List["SecurityhubInsightFiltersWorkflowStatus"]]:
        return typing.cast(typing.Optional[typing.List["SecurityhubInsightFiltersWorkflowStatus"]], jsii.get(self, "workflowStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> typing.List[SecurityhubInsightFiltersAwsAccountId]:
        return typing.cast(typing.List[SecurityhubInsightFiltersAwsAccountId], jsii.get(self, "awsAccountId"))

    @aws_account_id.setter
    def aws_account_id(
        self,
        value: typing.List[SecurityhubInsightFiltersAwsAccountId],
    ) -> None:
        jsii.set(self, "awsAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="companyName")
    def company_name(self) -> typing.List[SecurityhubInsightFiltersCompanyName]:
        return typing.cast(typing.List[SecurityhubInsightFiltersCompanyName], jsii.get(self, "companyName"))

    @company_name.setter
    def company_name(
        self,
        value: typing.List[SecurityhubInsightFiltersCompanyName],
    ) -> None:
        jsii.set(self, "companyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="complianceStatus")
    def compliance_status(
        self,
    ) -> typing.List[SecurityhubInsightFiltersComplianceStatus]:
        return typing.cast(typing.List[SecurityhubInsightFiltersComplianceStatus], jsii.get(self, "complianceStatus"))

    @compliance_status.setter
    def compliance_status(
        self,
        value: typing.List[SecurityhubInsightFiltersComplianceStatus],
    ) -> None:
        jsii.set(self, "complianceStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confidence")
    def confidence(self) -> typing.List[SecurityhubInsightFiltersConfidence]:
        return typing.cast(typing.List[SecurityhubInsightFiltersConfidence], jsii.get(self, "confidence"))

    @confidence.setter
    def confidence(
        self,
        value: typing.List[SecurityhubInsightFiltersConfidence],
    ) -> None:
        jsii.set(self, "confidence", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.List[SecurityhubInsightFiltersCreatedAt]:
        return typing.cast(typing.List[SecurityhubInsightFiltersCreatedAt], jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(
        self,
        value: typing.List[SecurityhubInsightFiltersCreatedAt],
    ) -> None:
        jsii.set(self, "createdAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criticality")
    def criticality(self) -> typing.List[SecurityhubInsightFiltersCriticality]:
        return typing.cast(typing.List[SecurityhubInsightFiltersCriticality], jsii.get(self, "criticality"))

    @criticality.setter
    def criticality(
        self,
        value: typing.List[SecurityhubInsightFiltersCriticality],
    ) -> None:
        jsii.set(self, "criticality", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.List[SecurityhubInsightFiltersDescription]:
        return typing.cast(typing.List[SecurityhubInsightFiltersDescription], jsii.get(self, "description"))

    @description.setter
    def description(
        self,
        value: typing.List[SecurityhubInsightFiltersDescription],
    ) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsConfidence")
    def finding_provider_fields_confidence(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsConfidence]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsConfidence], jsii.get(self, "findingProviderFieldsConfidence"))

    @finding_provider_fields_confidence.setter
    def finding_provider_fields_confidence(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsConfidence],
    ) -> None:
        jsii.set(self, "findingProviderFieldsConfidence", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsCriticality")
    def finding_provider_fields_criticality(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsCriticality]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsCriticality], jsii.get(self, "findingProviderFieldsCriticality"))

    @finding_provider_fields_criticality.setter
    def finding_provider_fields_criticality(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsCriticality],
    ) -> None:
        jsii.set(self, "findingProviderFieldsCriticality", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsRelatedFindingsId")
    def finding_provider_fields_related_findings_id(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId], jsii.get(self, "findingProviderFieldsRelatedFindingsId"))

    @finding_provider_fields_related_findings_id.setter
    def finding_provider_fields_related_findings_id(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId],
    ) -> None:
        jsii.set(self, "findingProviderFieldsRelatedFindingsId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsRelatedFindingsProductArn")
    def finding_provider_fields_related_findings_product_arn(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn], jsii.get(self, "findingProviderFieldsRelatedFindingsProductArn"))

    @finding_provider_fields_related_findings_product_arn.setter
    def finding_provider_fields_related_findings_product_arn(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn],
    ) -> None:
        jsii.set(self, "findingProviderFieldsRelatedFindingsProductArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsSeverityLabel")
    def finding_provider_fields_severity_label(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel], jsii.get(self, "findingProviderFieldsSeverityLabel"))

    @finding_provider_fields_severity_label.setter
    def finding_provider_fields_severity_label(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel],
    ) -> None:
        jsii.set(self, "findingProviderFieldsSeverityLabel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsSeverityOriginal")
    def finding_provider_fields_severity_original(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal], jsii.get(self, "findingProviderFieldsSeverityOriginal"))

    @finding_provider_fields_severity_original.setter
    def finding_provider_fields_severity_original(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal],
    ) -> None:
        jsii.set(self, "findingProviderFieldsSeverityOriginal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="findingProviderFieldsTypes")
    def finding_provider_fields_types(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFindingProviderFieldsTypes]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFindingProviderFieldsTypes], jsii.get(self, "findingProviderFieldsTypes"))

    @finding_provider_fields_types.setter
    def finding_provider_fields_types(
        self,
        value: typing.List[SecurityhubInsightFiltersFindingProviderFieldsTypes],
    ) -> None:
        jsii.set(self, "findingProviderFieldsTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firstObservedAt")
    def first_observed_at(
        self,
    ) -> typing.List[SecurityhubInsightFiltersFirstObservedAt]:
        return typing.cast(typing.List[SecurityhubInsightFiltersFirstObservedAt], jsii.get(self, "firstObservedAt"))

    @first_observed_at.setter
    def first_observed_at(
        self,
        value: typing.List[SecurityhubInsightFiltersFirstObservedAt],
    ) -> None:
        jsii.set(self, "firstObservedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatorId")
    def generator_id(self) -> typing.List[SecurityhubInsightFiltersGeneratorId]:
        return typing.cast(typing.List[SecurityhubInsightFiltersGeneratorId], jsii.get(self, "generatorId"))

    @generator_id.setter
    def generator_id(
        self,
        value: typing.List[SecurityhubInsightFiltersGeneratorId],
    ) -> None:
        jsii.set(self, "generatorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> typing.List[SecurityhubInsightFiltersId]:
        return typing.cast(typing.List[SecurityhubInsightFiltersId], jsii.get(self, "id"))

    @id.setter
    def id(self, value: typing.List[SecurityhubInsightFiltersId]) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyword")
    def keyword(self) -> typing.List[SecurityhubInsightFiltersKeyword]:
        return typing.cast(typing.List[SecurityhubInsightFiltersKeyword], jsii.get(self, "keyword"))

    @keyword.setter
    def keyword(self, value: typing.List[SecurityhubInsightFiltersKeyword]) -> None:
        jsii.set(self, "keyword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastObservedAt")
    def last_observed_at(self) -> typing.List[SecurityhubInsightFiltersLastObservedAt]:
        return typing.cast(typing.List[SecurityhubInsightFiltersLastObservedAt], jsii.get(self, "lastObservedAt"))

    @last_observed_at.setter
    def last_observed_at(
        self,
        value: typing.List[SecurityhubInsightFiltersLastObservedAt],
    ) -> None:
        jsii.set(self, "lastObservedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwareName")
    def malware_name(self) -> typing.List[SecurityhubInsightFiltersMalwareName]:
        return typing.cast(typing.List[SecurityhubInsightFiltersMalwareName], jsii.get(self, "malwareName"))

    @malware_name.setter
    def malware_name(
        self,
        value: typing.List[SecurityhubInsightFiltersMalwareName],
    ) -> None:
        jsii.set(self, "malwareName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwarePath")
    def malware_path(self) -> typing.List[SecurityhubInsightFiltersMalwarePath]:
        return typing.cast(typing.List[SecurityhubInsightFiltersMalwarePath], jsii.get(self, "malwarePath"))

    @malware_path.setter
    def malware_path(
        self,
        value: typing.List[SecurityhubInsightFiltersMalwarePath],
    ) -> None:
        jsii.set(self, "malwarePath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwareState")
    def malware_state(self) -> typing.List[SecurityhubInsightFiltersMalwareState]:
        return typing.cast(typing.List[SecurityhubInsightFiltersMalwareState], jsii.get(self, "malwareState"))

    @malware_state.setter
    def malware_state(
        self,
        value: typing.List[SecurityhubInsightFiltersMalwareState],
    ) -> None:
        jsii.set(self, "malwareState", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="malwareType")
    def malware_type(self) -> typing.List[SecurityhubInsightFiltersMalwareType]:
        return typing.cast(typing.List[SecurityhubInsightFiltersMalwareType], jsii.get(self, "malwareType"))

    @malware_type.setter
    def malware_type(
        self,
        value: typing.List[SecurityhubInsightFiltersMalwareType],
    ) -> None:
        jsii.set(self, "malwareType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationDomain")
    def network_destination_domain(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkDestinationDomain]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkDestinationDomain], jsii.get(self, "networkDestinationDomain"))

    @network_destination_domain.setter
    def network_destination_domain(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkDestinationDomain],
    ) -> None:
        jsii.set(self, "networkDestinationDomain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationIpv4")
    def network_destination_ipv4(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkDestinationIpv4]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkDestinationIpv4], jsii.get(self, "networkDestinationIpv4"))

    @network_destination_ipv4.setter
    def network_destination_ipv4(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkDestinationIpv4],
    ) -> None:
        jsii.set(self, "networkDestinationIpv4", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationIpv6")
    def network_destination_ipv6(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkDestinationIpv6]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkDestinationIpv6], jsii.get(self, "networkDestinationIpv6"))

    @network_destination_ipv6.setter
    def network_destination_ipv6(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkDestinationIpv6],
    ) -> None:
        jsii.set(self, "networkDestinationIpv6", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDestinationPort")
    def network_destination_port(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkDestinationPort]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkDestinationPort], jsii.get(self, "networkDestinationPort"))

    @network_destination_port.setter
    def network_destination_port(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkDestinationPort],
    ) -> None:
        jsii.set(self, "networkDestinationPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkDirection")
    def network_direction(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkDirection]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkDirection], jsii.get(self, "networkDirection"))

    @network_direction.setter
    def network_direction(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkDirection],
    ) -> None:
        jsii.set(self, "networkDirection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkProtocol")
    def network_protocol(self) -> typing.List[SecurityhubInsightFiltersNetworkProtocol]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkProtocol], jsii.get(self, "networkProtocol"))

    @network_protocol.setter
    def network_protocol(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkProtocol],
    ) -> None:
        jsii.set(self, "networkProtocol", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceDomain")
    def network_source_domain(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkSourceDomain]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkSourceDomain], jsii.get(self, "networkSourceDomain"))

    @network_source_domain.setter
    def network_source_domain(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkSourceDomain],
    ) -> None:
        jsii.set(self, "networkSourceDomain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceIpv4")
    def network_source_ipv4(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkSourceIpv4]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkSourceIpv4], jsii.get(self, "networkSourceIpv4"))

    @network_source_ipv4.setter
    def network_source_ipv4(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkSourceIpv4],
    ) -> None:
        jsii.set(self, "networkSourceIpv4", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceIpv6")
    def network_source_ipv6(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkSourceIpv6]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkSourceIpv6], jsii.get(self, "networkSourceIpv6"))

    @network_source_ipv6.setter
    def network_source_ipv6(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkSourceIpv6],
    ) -> None:
        jsii.set(self, "networkSourceIpv6", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourceMac")
    def network_source_mac(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkSourceMac]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkSourceMac], jsii.get(self, "networkSourceMac"))

    @network_source_mac.setter
    def network_source_mac(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkSourceMac],
    ) -> None:
        jsii.set(self, "networkSourceMac", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkSourcePort")
    def network_source_port(
        self,
    ) -> typing.List[SecurityhubInsightFiltersNetworkSourcePort]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNetworkSourcePort], jsii.get(self, "networkSourcePort"))

    @network_source_port.setter
    def network_source_port(
        self,
        value: typing.List[SecurityhubInsightFiltersNetworkSourcePort],
    ) -> None:
        jsii.set(self, "networkSourcePort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteText")
    def note_text(self) -> typing.List[SecurityhubInsightFiltersNoteText]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNoteText], jsii.get(self, "noteText"))

    @note_text.setter
    def note_text(self, value: typing.List[SecurityhubInsightFiltersNoteText]) -> None:
        jsii.set(self, "noteText", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteUpdatedAt")
    def note_updated_at(self) -> typing.List[SecurityhubInsightFiltersNoteUpdatedAt]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNoteUpdatedAt], jsii.get(self, "noteUpdatedAt"))

    @note_updated_at.setter
    def note_updated_at(
        self,
        value: typing.List[SecurityhubInsightFiltersNoteUpdatedAt],
    ) -> None:
        jsii.set(self, "noteUpdatedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noteUpdatedBy")
    def note_updated_by(self) -> typing.List[SecurityhubInsightFiltersNoteUpdatedBy]:
        return typing.cast(typing.List[SecurityhubInsightFiltersNoteUpdatedBy], jsii.get(self, "noteUpdatedBy"))

    @note_updated_by.setter
    def note_updated_by(
        self,
        value: typing.List[SecurityhubInsightFiltersNoteUpdatedBy],
    ) -> None:
        jsii.set(self, "noteUpdatedBy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processLaunchedAt")
    def process_launched_at(
        self,
    ) -> typing.List["SecurityhubInsightFiltersProcessLaunchedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProcessLaunchedAt"], jsii.get(self, "processLaunchedAt"))

    @process_launched_at.setter
    def process_launched_at(
        self,
        value: typing.List["SecurityhubInsightFiltersProcessLaunchedAt"],
    ) -> None:
        jsii.set(self, "processLaunchedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processName")
    def process_name(self) -> typing.List["SecurityhubInsightFiltersProcessName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProcessName"], jsii.get(self, "processName"))

    @process_name.setter
    def process_name(
        self,
        value: typing.List["SecurityhubInsightFiltersProcessName"],
    ) -> None:
        jsii.set(self, "processName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processParentPid")
    def process_parent_pid(
        self,
    ) -> typing.List["SecurityhubInsightFiltersProcessParentPid"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProcessParentPid"], jsii.get(self, "processParentPid"))

    @process_parent_pid.setter
    def process_parent_pid(
        self,
        value: typing.List["SecurityhubInsightFiltersProcessParentPid"],
    ) -> None:
        jsii.set(self, "processParentPid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processPath")
    def process_path(self) -> typing.List["SecurityhubInsightFiltersProcessPath"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProcessPath"], jsii.get(self, "processPath"))

    @process_path.setter
    def process_path(
        self,
        value: typing.List["SecurityhubInsightFiltersProcessPath"],
    ) -> None:
        jsii.set(self, "processPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processPid")
    def process_pid(self) -> typing.List["SecurityhubInsightFiltersProcessPid"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProcessPid"], jsii.get(self, "processPid"))

    @process_pid.setter
    def process_pid(
        self,
        value: typing.List["SecurityhubInsightFiltersProcessPid"],
    ) -> None:
        jsii.set(self, "processPid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="processTerminatedAt")
    def process_terminated_at(
        self,
    ) -> typing.List["SecurityhubInsightFiltersProcessTerminatedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProcessTerminatedAt"], jsii.get(self, "processTerminatedAt"))

    @process_terminated_at.setter
    def process_terminated_at(
        self,
        value: typing.List["SecurityhubInsightFiltersProcessTerminatedAt"],
    ) -> None:
        jsii.set(self, "processTerminatedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    def product_arn(self) -> typing.List["SecurityhubInsightFiltersProductArn"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProductArn"], jsii.get(self, "productArn"))

    @product_arn.setter
    def product_arn(
        self,
        value: typing.List["SecurityhubInsightFiltersProductArn"],
    ) -> None:
        jsii.set(self, "productArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productFields")
    def product_fields(self) -> typing.List["SecurityhubInsightFiltersProductFields"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProductFields"], jsii.get(self, "productFields"))

    @product_fields.setter
    def product_fields(
        self,
        value: typing.List["SecurityhubInsightFiltersProductFields"],
    ) -> None:
        jsii.set(self, "productFields", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productName")
    def product_name(self) -> typing.List["SecurityhubInsightFiltersProductName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersProductName"], jsii.get(self, "productName"))

    @product_name.setter
    def product_name(
        self,
        value: typing.List["SecurityhubInsightFiltersProductName"],
    ) -> None:
        jsii.set(self, "productName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recommendationText")
    def recommendation_text(
        self,
    ) -> typing.List["SecurityhubInsightFiltersRecommendationText"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersRecommendationText"], jsii.get(self, "recommendationText"))

    @recommendation_text.setter
    def recommendation_text(
        self,
        value: typing.List["SecurityhubInsightFiltersRecommendationText"],
    ) -> None:
        jsii.set(self, "recommendationText", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordState")
    def record_state(self) -> typing.List["SecurityhubInsightFiltersRecordState"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersRecordState"], jsii.get(self, "recordState"))

    @record_state.setter
    def record_state(
        self,
        value: typing.List["SecurityhubInsightFiltersRecordState"],
    ) -> None:
        jsii.set(self, "recordState", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="relatedFindingsId")
    def related_findings_id(
        self,
    ) -> typing.List["SecurityhubInsightFiltersRelatedFindingsId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersRelatedFindingsId"], jsii.get(self, "relatedFindingsId"))

    @related_findings_id.setter
    def related_findings_id(
        self,
        value: typing.List["SecurityhubInsightFiltersRelatedFindingsId"],
    ) -> None:
        jsii.set(self, "relatedFindingsId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="relatedFindingsProductArn")
    def related_findings_product_arn(
        self,
    ) -> typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"], jsii.get(self, "relatedFindingsProductArn"))

    @related_findings_product_arn.setter
    def related_findings_product_arn(
        self,
        value: typing.List["SecurityhubInsightFiltersRelatedFindingsProductArn"],
    ) -> None:
        jsii.set(self, "relatedFindingsProductArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceIamInstanceProfileArn")
    def resource_aws_ec2_instance_iam_instance_profile_arn(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"], jsii.get(self, "resourceAwsEc2InstanceIamInstanceProfileArn"))

    @resource_aws_ec2_instance_iam_instance_profile_arn.setter
    def resource_aws_ec2_instance_iam_instance_profile_arn(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceIamInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceImageId")
    def resource_aws_ec2_instance_image_id(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"], jsii.get(self, "resourceAwsEc2InstanceImageId"))

    @resource_aws_ec2_instance_image_id.setter
    def resource_aws_ec2_instance_image_id(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceImageId"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceImageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceIpv4Addresses")
    def resource_aws_ec2_instance_ipv4_addresses(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"], jsii.get(self, "resourceAwsEc2InstanceIpv4Addresses"))

    @resource_aws_ec2_instance_ipv4_addresses.setter
    def resource_aws_ec2_instance_ipv4_addresses(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceIpv4Addresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceIpv6Addresses")
    def resource_aws_ec2_instance_ipv6_addresses(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"], jsii.get(self, "resourceAwsEc2InstanceIpv6Addresses"))

    @resource_aws_ec2_instance_ipv6_addresses.setter
    def resource_aws_ec2_instance_ipv6_addresses(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceIpv6Addresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceKeyName")
    def resource_aws_ec2_instance_key_name(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"], jsii.get(self, "resourceAwsEc2InstanceKeyName"))

    @resource_aws_ec2_instance_key_name.setter
    def resource_aws_ec2_instance_key_name(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceKeyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceLaunchedAt")
    def resource_aws_ec2_instance_launched_at(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"], jsii.get(self, "resourceAwsEc2InstanceLaunchedAt"))

    @resource_aws_ec2_instance_launched_at.setter
    def resource_aws_ec2_instance_launched_at(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceLaunchedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceSubnetId")
    def resource_aws_ec2_instance_subnet_id(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"], jsii.get(self, "resourceAwsEc2InstanceSubnetId"))

    @resource_aws_ec2_instance_subnet_id.setter
    def resource_aws_ec2_instance_subnet_id(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceSubnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceType")
    def resource_aws_ec2_instance_type(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"], jsii.get(self, "resourceAwsEc2InstanceType"))

    @resource_aws_ec2_instance_type.setter
    def resource_aws_ec2_instance_type(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceType"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsEc2InstanceVpcId")
    def resource_aws_ec2_instance_vpc_id(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"], jsii.get(self, "resourceAwsEc2InstanceVpcId"))

    @resource_aws_ec2_instance_vpc_id.setter
    def resource_aws_ec2_instance_vpc_id(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId"],
    ) -> None:
        jsii.set(self, "resourceAwsEc2InstanceVpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsIamAccessKeyCreatedAt")
    def resource_aws_iam_access_key_created_at(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"], jsii.get(self, "resourceAwsIamAccessKeyCreatedAt"))

    @resource_aws_iam_access_key_created_at.setter
    def resource_aws_iam_access_key_created_at(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt"],
    ) -> None:
        jsii.set(self, "resourceAwsIamAccessKeyCreatedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsIamAccessKeyStatus")
    def resource_aws_iam_access_key_status(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"], jsii.get(self, "resourceAwsIamAccessKeyStatus"))

    @resource_aws_iam_access_key_status.setter
    def resource_aws_iam_access_key_status(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus"],
    ) -> None:
        jsii.set(self, "resourceAwsIamAccessKeyStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsIamAccessKeyUserName")
    def resource_aws_iam_access_key_user_name(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"], jsii.get(self, "resourceAwsIamAccessKeyUserName"))

    @resource_aws_iam_access_key_user_name.setter
    def resource_aws_iam_access_key_user_name(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName"],
    ) -> None:
        jsii.set(self, "resourceAwsIamAccessKeyUserName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsS3BucketOwnerId")
    def resource_aws_s3_bucket_owner_id(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"], jsii.get(self, "resourceAwsS3BucketOwnerId"))

    @resource_aws_s3_bucket_owner_id.setter
    def resource_aws_s3_bucket_owner_id(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerId"],
    ) -> None:
        jsii.set(self, "resourceAwsS3BucketOwnerId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceAwsS3BucketOwnerName")
    def resource_aws_s3_bucket_owner_name(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"], jsii.get(self, "resourceAwsS3BucketOwnerName"))

    @resource_aws_s3_bucket_owner_name.setter
    def resource_aws_s3_bucket_owner_name(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceAwsS3BucketOwnerName"],
    ) -> None:
        jsii.set(self, "resourceAwsS3BucketOwnerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerImageId")
    def resource_container_image_id(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceContainerImageId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceContainerImageId"], jsii.get(self, "resourceContainerImageId"))

    @resource_container_image_id.setter
    def resource_container_image_id(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceContainerImageId"],
    ) -> None:
        jsii.set(self, "resourceContainerImageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerImageName")
    def resource_container_image_name(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceContainerImageName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceContainerImageName"], jsii.get(self, "resourceContainerImageName"))

    @resource_container_image_name.setter
    def resource_container_image_name(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceContainerImageName"],
    ) -> None:
        jsii.set(self, "resourceContainerImageName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerLaunchedAt")
    def resource_container_launched_at(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"], jsii.get(self, "resourceContainerLaunchedAt"))

    @resource_container_launched_at.setter
    def resource_container_launched_at(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceContainerLaunchedAt"],
    ) -> None:
        jsii.set(self, "resourceContainerLaunchedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceContainerName")
    def resource_container_name(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceContainerName"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceContainerName"], jsii.get(self, "resourceContainerName"))

    @resource_container_name.setter
    def resource_container_name(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceContainerName"],
    ) -> None:
        jsii.set(self, "resourceContainerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceDetailsOther")
    def resource_details_other(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourceDetailsOther"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceDetailsOther"], jsii.get(self, "resourceDetailsOther"))

    @resource_details_other.setter
    def resource_details_other(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceDetailsOther"],
    ) -> None:
        jsii.set(self, "resourceDetailsOther", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> typing.List["SecurityhubInsightFiltersResourceId"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceId"], jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceId"],
    ) -> None:
        jsii.set(self, "resourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcePartition")
    def resource_partition(
        self,
    ) -> typing.List["SecurityhubInsightFiltersResourcePartition"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourcePartition"], jsii.get(self, "resourcePartition"))

    @resource_partition.setter
    def resource_partition(
        self,
        value: typing.List["SecurityhubInsightFiltersResourcePartition"],
    ) -> None:
        jsii.set(self, "resourcePartition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceRegion")
    def resource_region(self) -> typing.List["SecurityhubInsightFiltersResourceRegion"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceRegion"], jsii.get(self, "resourceRegion"))

    @resource_region.setter
    def resource_region(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceRegion"],
    ) -> None:
        jsii.set(self, "resourceRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTags")
    def resource_tags(self) -> typing.List["SecurityhubInsightFiltersResourceTags"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceTags"], jsii.get(self, "resourceTags"))

    @resource_tags.setter
    def resource_tags(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceTags"],
    ) -> None:
        jsii.set(self, "resourceTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> typing.List["SecurityhubInsightFiltersResourceType"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersResourceType"], jsii.get(self, "resourceType"))

    @resource_type.setter
    def resource_type(
        self,
        value: typing.List["SecurityhubInsightFiltersResourceType"],
    ) -> None:
        jsii.set(self, "resourceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="severityLabel")
    def severity_label(self) -> typing.List["SecurityhubInsightFiltersSeverityLabel"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersSeverityLabel"], jsii.get(self, "severityLabel"))

    @severity_label.setter
    def severity_label(
        self,
        value: typing.List["SecurityhubInsightFiltersSeverityLabel"],
    ) -> None:
        jsii.set(self, "severityLabel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceUrl")
    def source_url(self) -> typing.List["SecurityhubInsightFiltersSourceUrl"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersSourceUrl"], jsii.get(self, "sourceUrl"))

    @source_url.setter
    def source_url(
        self,
        value: typing.List["SecurityhubInsightFiltersSourceUrl"],
    ) -> None:
        jsii.set(self, "sourceUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorCategory")
    def threat_intel_indicator_category(
        self,
    ) -> typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"], jsii.get(self, "threatIntelIndicatorCategory"))

    @threat_intel_indicator_category.setter
    def threat_intel_indicator_category(
        self,
        value: typing.List["SecurityhubInsightFiltersThreatIntelIndicatorCategory"],
    ) -> None:
        jsii.set(self, "threatIntelIndicatorCategory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorLastObservedAt")
    def threat_intel_indicator_last_observed_at(
        self,
    ) -> typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"], jsii.get(self, "threatIntelIndicatorLastObservedAt"))

    @threat_intel_indicator_last_observed_at.setter
    def threat_intel_indicator_last_observed_at(
        self,
        value: typing.List["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt"],
    ) -> None:
        jsii.set(self, "threatIntelIndicatorLastObservedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorSource")
    def threat_intel_indicator_source(
        self,
    ) -> typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"], jsii.get(self, "threatIntelIndicatorSource"))

    @threat_intel_indicator_source.setter
    def threat_intel_indicator_source(
        self,
        value: typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSource"],
    ) -> None:
        jsii.set(self, "threatIntelIndicatorSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorSourceUrl")
    def threat_intel_indicator_source_url(
        self,
    ) -> typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"], jsii.get(self, "threatIntelIndicatorSourceUrl"))

    @threat_intel_indicator_source_url.setter
    def threat_intel_indicator_source_url(
        self,
        value: typing.List["SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl"],
    ) -> None:
        jsii.set(self, "threatIntelIndicatorSourceUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorType")
    def threat_intel_indicator_type(
        self,
    ) -> typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"], jsii.get(self, "threatIntelIndicatorType"))

    @threat_intel_indicator_type.setter
    def threat_intel_indicator_type(
        self,
        value: typing.List["SecurityhubInsightFiltersThreatIntelIndicatorType"],
    ) -> None:
        jsii.set(self, "threatIntelIndicatorType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="threatIntelIndicatorValue")
    def threat_intel_indicator_value(
        self,
    ) -> typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"], jsii.get(self, "threatIntelIndicatorValue"))

    @threat_intel_indicator_value.setter
    def threat_intel_indicator_value(
        self,
        value: typing.List["SecurityhubInsightFiltersThreatIntelIndicatorValue"],
    ) -> None:
        jsii.set(self, "threatIntelIndicatorValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> typing.List["SecurityhubInsightFiltersTitle"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersTitle"], jsii.get(self, "title"))

    @title.setter
    def title(self, value: typing.List["SecurityhubInsightFiltersTitle"]) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> typing.List["SecurityhubInsightFiltersType"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersType"], jsii.get(self, "type"))

    @type.setter
    def type(self, value: typing.List["SecurityhubInsightFiltersType"]) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> typing.List["SecurityhubInsightFiltersUpdatedAt"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersUpdatedAt"], jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(
        self,
        value: typing.List["SecurityhubInsightFiltersUpdatedAt"],
    ) -> None:
        jsii.set(self, "updatedAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDefinedValues")
    def user_defined_values(
        self,
    ) -> typing.List["SecurityhubInsightFiltersUserDefinedValues"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersUserDefinedValues"], jsii.get(self, "userDefinedValues"))

    @user_defined_values.setter
    def user_defined_values(
        self,
        value: typing.List["SecurityhubInsightFiltersUserDefinedValues"],
    ) -> None:
        jsii.set(self, "userDefinedValues", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationState")
    def verification_state(
        self,
    ) -> typing.List["SecurityhubInsightFiltersVerificationState"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersVerificationState"], jsii.get(self, "verificationState"))

    @verification_state.setter
    def verification_state(
        self,
        value: typing.List["SecurityhubInsightFiltersVerificationState"],
    ) -> None:
        jsii.set(self, "verificationState", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowStatus")
    def workflow_status(self) -> typing.List["SecurityhubInsightFiltersWorkflowStatus"]:
        return typing.cast(typing.List["SecurityhubInsightFiltersWorkflowStatus"], jsii.get(self, "workflowStatus"))

    @workflow_status.setter
    def workflow_status(
        self,
        value: typing.List["SecurityhubInsightFiltersWorkflowStatus"],
    ) -> None:
        jsii.set(self, "workflowStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SecurityhubInsightFilters]:
        return typing.cast(typing.Optional[SecurityhubInsightFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SecurityhubInsightFilters]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessLaunchedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersProcessLaunchedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersProcessLaunchedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersProcessLaunchedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersProcessLaunchedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersProcessLaunchedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessLaunchedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessLaunchedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersProcessLaunchedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessLaunchedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersProcessLaunchedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessLaunchedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersProcessLaunchedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersProcessLaunchedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersProcessLaunchedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersProcessName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessParentPid",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersProcessParentPid:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessParentPid(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessPath",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersProcessPath:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessPid",
    jsii_struct_bases=[],
    name_mapping={"eq": "eq", "gte": "gte", "lte": "lte"},
)
class SecurityhubInsightFiltersProcessPid:
    def __init__(
        self,
        *,
        eq: typing.Optional[builtins.str] = None,
        gte: typing.Optional[builtins.str] = None,
        lte: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.
        :param gte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.
        :param lte: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if eq is not None:
            self._values["eq"] = eq
        if gte is not None:
            self._values["gte"] = gte
        if lte is not None:
            self._values["lte"] = lte

    @builtins.property
    def eq(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#eq SecurityhubInsight#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#gte SecurityhubInsight#gte}.'''
        result = self._values.get("gte")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lte(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#lte SecurityhubInsight#lte}.'''
        result = self._values.get("lte")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessPid(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessTerminatedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersProcessTerminatedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersProcessTerminatedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersProcessTerminatedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersProcessTerminatedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersProcessTerminatedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessTerminatedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessTerminatedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersProcessTerminatedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProcessTerminatedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersProcessTerminatedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProcessTerminatedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersProcessTerminatedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersProcessTerminatedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersProcessTerminatedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProductArn",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersProductArn:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProductArn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProductFields",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "key": "key", "value": "value"},
)
class SecurityhubInsightFiltersProductFields:
    def __init__(
        self,
        *,
        comparison: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "key": key,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProductFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersProductName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersProductName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersProductName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersRecommendationText",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersRecommendationText:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersRecommendationText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersRecordState",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersRecordState:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersRecordState(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersRelatedFindingsId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersRelatedFindingsId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersRelatedFindingsId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersRelatedFindingsProductArn",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersRelatedFindingsProductArn:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersRelatedFindingsProductArn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceImageId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceImageId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceImageId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#cidr SecurityhubInsight#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceType",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceType:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsS3BucketOwnerId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsS3BucketOwnerId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsS3BucketOwnerId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceAwsS3BucketOwnerName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceAwsS3BucketOwnerName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceAwsS3BucketOwnerName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceContainerImageId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceContainerImageId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceContainerImageId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceContainerImageName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceContainerImageName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceContainerImageName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceContainerLaunchedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersResourceContainerLaunchedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceContainerLaunchedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersResourceContainerLaunchedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceContainerLaunchedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceContainerName",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceContainerName:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceContainerName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceDetailsOther",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "key": "key", "value": "value"},
)
class SecurityhubInsightFiltersResourceDetailsOther:
    def __init__(
        self,
        *,
        comparison: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "key": key,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceDetailsOther(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceId",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceId:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourcePartition",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourcePartition:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourcePartition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceRegion",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceRegion:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceRegion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceTags",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "key": "key", "value": "value"},
)
class SecurityhubInsightFiltersResourceTags:
    def __init__(
        self,
        *,
        comparison: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "key": key,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersResourceType",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersResourceType:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersResourceType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersSeverityLabel",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersSeverityLabel:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersSeverityLabel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersSourceUrl",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersSourceUrl:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersSourceUrl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorCategory",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorCategory:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorCategory(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorSource",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorSource:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorType",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorType:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersThreatIntelIndicatorValue",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersThreatIntelIndicatorValue:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersThreatIntelIndicatorValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersTitle",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersTitle:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersTitle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersType",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersType:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersUpdatedAt",
    jsii_struct_bases=[],
    name_mapping={"date_range": "dateRange", "end": "end", "start": "start"},
)
class SecurityhubInsightFiltersUpdatedAt:
    def __init__(
        self,
        *,
        date_range: typing.Optional["SecurityhubInsightFiltersUpdatedAtDateRange"] = None,
        end: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param date_range: date_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        :param end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.
        :param start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.
        '''
        if isinstance(date_range, dict):
            date_range = SecurityhubInsightFiltersUpdatedAtDateRange(**date_range)
        self._values: typing.Dict[str, typing.Any] = {}
        if date_range is not None:
            self._values["date_range"] = date_range
        if end is not None:
            self._values["end"] = end
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def date_range(
        self,
    ) -> typing.Optional["SecurityhubInsightFiltersUpdatedAtDateRange"]:
        '''date_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#date_range SecurityhubInsight#date_range}
        '''
        result = self._values.get("date_range")
        return typing.cast(typing.Optional["SecurityhubInsightFiltersUpdatedAtDateRange"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#end SecurityhubInsight#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#start SecurityhubInsight#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersUpdatedAt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersUpdatedAtDateRange",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class SecurityhubInsightFiltersUpdatedAtDateRange:
    def __init__(self, *, unit: builtins.str, value: jsii.Number) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#unit SecurityhubInsight#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersUpdatedAtDateRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInsightFiltersUpdatedAtDateRangeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersUpdatedAtDateRangeOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[SecurityhubInsightFiltersUpdatedAtDateRange]:
        return typing.cast(typing.Optional[SecurityhubInsightFiltersUpdatedAtDateRange], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SecurityhubInsightFiltersUpdatedAtDateRange],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersUserDefinedValues",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "key": "key", "value": "value"},
)
class SecurityhubInsightFiltersUserDefinedValues:
    def __init__(
        self,
        *,
        comparison: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "key": key,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#key SecurityhubInsight#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersUserDefinedValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersVerificationState",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersVerificationState:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersVerificationState(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInsightFiltersWorkflowStatus",
    jsii_struct_bases=[],
    name_mapping={"comparison": "comparison", "value": "value"},
)
class SecurityhubInsightFiltersWorkflowStatus:
    def __init__(self, *, comparison: builtins.str, value: builtins.str) -> None:
        '''
        :param comparison: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison": comparison,
            "value": value,
        }

    @builtins.property
    def comparison(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#comparison SecurityhubInsight#comparison}.'''
        result = self._values.get("comparison")
        assert result is not None, "Required property 'comparison' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_insight#value SecurityhubInsight#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInsightFiltersWorkflowStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubInviteAccepter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInviteAccepter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_invite_accepter aws_securityhub_invite_accepter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        master_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_invite_accepter aws_securityhub_invite_accepter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param master_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_invite_accepter#master_id SecurityhubInviteAccepter#master_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubInviteAccepterConfig(
            master_id=master_id,
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
    @jsii.member(jsii_name="invitationId")
    def invitation_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "invitationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterIdInput")
    def master_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterId")
    def master_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterId"))

    @master_id.setter
    def master_id(self, value: builtins.str) -> None:
        jsii.set(self, "masterId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubInviteAccepterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "master_id": "masterId",
    },
)
class SecurityhubInviteAccepterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        master_id: builtins.str,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param master_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_invite_accepter#master_id SecurityhubInviteAccepter#master_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "master_id": master_id,
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
    def master_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_invite_accepter#master_id SecurityhubInviteAccepter#master_id}.'''
        result = self._values.get("master_id")
        assert result is not None, "Required property 'master_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubInviteAccepterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubMember(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubMember",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member aws_securityhub_member}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        email: builtins.str,
        invite: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member aws_securityhub_member} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#account_id SecurityhubMember#account_id}.
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#email SecurityhubMember#email}.
        :param invite: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#invite SecurityhubMember#invite}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubMemberConfig(
            account_id=account_id,
            email=email,
            invite=invite,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetInvite")
    def reset_invite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvite", []))

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
    @jsii.member(jsii_name="masterId")
    def master_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberStatus")
    def member_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memberStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inviteInput")
    def invite_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "inviteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invite")
    def invite(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "invite"))

    @invite.setter
    def invite(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "invite", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubMemberConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_id": "accountId",
        "email": "email",
        "invite": "invite",
    },
)
class SecurityhubMemberConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_id: builtins.str,
        email: builtins.str,
        invite: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#account_id SecurityhubMember#account_id}.
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#email SecurityhubMember#email}.
        :param invite: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#invite SecurityhubMember#invite}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "email": email,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if invite is not None:
            self._values["invite"] = invite

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
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#account_id SecurityhubMember#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#email SecurityhubMember#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def invite(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_member#invite SecurityhubMember#invite}.'''
        result = self._values.get("invite")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubMemberConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubOrganizationAdminAccount(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubOrganizationAdminAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_admin_account aws_securityhub_organization_admin_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        admin_account_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_admin_account aws_securityhub_organization_admin_account} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param admin_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_admin_account#admin_account_id SecurityhubOrganizationAdminAccount#admin_account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubOrganizationAdminAccountConfig(
            admin_account_id=admin_account_id,
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
    @jsii.member(jsii_name="adminAccountIdInput")
    def admin_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminAccountId")
    def admin_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminAccountId"))

    @admin_account_id.setter
    def admin_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "adminAccountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubOrganizationAdminAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "admin_account_id": "adminAccountId",
    },
)
class SecurityhubOrganizationAdminAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        admin_account_id: builtins.str,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param admin_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_admin_account#admin_account_id SecurityhubOrganizationAdminAccount#admin_account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "admin_account_id": admin_account_id,
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
    def admin_account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_admin_account#admin_account_id SecurityhubOrganizationAdminAccount#admin_account_id}.'''
        result = self._values.get("admin_account_id")
        assert result is not None, "Required property 'admin_account_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubOrganizationAdminAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubOrganizationConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubOrganizationConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_configuration aws_securityhub_organization_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        auto_enable: typing.Union[builtins.bool, cdktf.IResolvable],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_configuration aws_securityhub_organization_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param auto_enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_configuration#auto_enable SecurityhubOrganizationConfiguration#auto_enable}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubOrganizationConfigurationConfig(
            auto_enable=auto_enable,
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
    @jsii.member(jsii_name="autoEnableInput")
    def auto_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoEnableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoEnable")
    def auto_enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoEnable"))

    @auto_enable.setter
    def auto_enable(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoEnable", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubOrganizationConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "auto_enable": "autoEnable",
    },
)
class SecurityhubOrganizationConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        auto_enable: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param auto_enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_configuration#auto_enable SecurityhubOrganizationConfiguration#auto_enable}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "auto_enable": auto_enable,
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
    def auto_enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_organization_configuration#auto_enable SecurityhubOrganizationConfiguration#auto_enable}.'''
        result = self._values.get("auto_enable")
        assert result is not None, "Required property 'auto_enable' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubOrganizationConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubProductSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubProductSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_product_subscription aws_securityhub_product_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        product_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_product_subscription aws_securityhub_product_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param product_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_product_subscription#product_arn SecurityhubProductSubscription#product_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubProductSubscriptionConfig(
            product_arn=product_arn,
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArnInput")
    def product_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    def product_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productArn"))

    @product_arn.setter
    def product_arn(self, value: builtins.str) -> None:
        jsii.set(self, "productArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubProductSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "product_arn": "productArn",
    },
)
class SecurityhubProductSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        product_arn: builtins.str,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param product_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_product_subscription#product_arn SecurityhubProductSubscription#product_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "product_arn": product_arn,
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
    def product_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_product_subscription#product_arn SecurityhubProductSubscription#product_arn}.'''
        result = self._values.get("product_arn")
        assert result is not None, "Required property 'product_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubProductSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubStandardsControl(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubStandardsControl",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control aws_securityhub_standards_control}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        control_status: builtins.str,
        standards_control_arn: builtins.str,
        disabled_reason: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control aws_securityhub_standards_control} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param control_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#control_status SecurityhubStandardsControl#control_status}.
        :param standards_control_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#standards_control_arn SecurityhubStandardsControl#standards_control_arn}.
        :param disabled_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#disabled_reason SecurityhubStandardsControl#disabled_reason}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubStandardsControlConfig(
            control_status=control_status,
            standards_control_arn=standards_control_arn,
            disabled_reason=disabled_reason,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDisabledReason")
    def reset_disabled_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabledReason", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlId")
    def control_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "controlId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlStatusUpdatedAt")
    def control_status_updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "controlStatusUpdatedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="relatedRequirements")
    def related_requirements(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "relatedRequirements"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remediationUrl")
    def remediation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remediationUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="severityRating")
    def severity_rating(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "severityRating"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlStatusInput")
    def control_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "controlStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disabledReasonInput")
    def disabled_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "disabledReasonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="standardsControlArnInput")
    def standards_control_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "standardsControlArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlStatus")
    def control_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "controlStatus"))

    @control_status.setter
    def control_status(self, value: builtins.str) -> None:
        jsii.set(self, "controlStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disabledReason")
    def disabled_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "disabledReason"))

    @disabled_reason.setter
    def disabled_reason(self, value: builtins.str) -> None:
        jsii.set(self, "disabledReason", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="standardsControlArn")
    def standards_control_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "standardsControlArn"))

    @standards_control_arn.setter
    def standards_control_arn(self, value: builtins.str) -> None:
        jsii.set(self, "standardsControlArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubStandardsControlConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "control_status": "controlStatus",
        "standards_control_arn": "standardsControlArn",
        "disabled_reason": "disabledReason",
    },
)
class SecurityhubStandardsControlConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        control_status: builtins.str,
        standards_control_arn: builtins.str,
        disabled_reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param control_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#control_status SecurityhubStandardsControl#control_status}.
        :param standards_control_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#standards_control_arn SecurityhubStandardsControl#standards_control_arn}.
        :param disabled_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#disabled_reason SecurityhubStandardsControl#disabled_reason}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "control_status": control_status,
            "standards_control_arn": standards_control_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if disabled_reason is not None:
            self._values["disabled_reason"] = disabled_reason

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
    def control_status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#control_status SecurityhubStandardsControl#control_status}.'''
        result = self._values.get("control_status")
        assert result is not None, "Required property 'control_status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def standards_control_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#standards_control_arn SecurityhubStandardsControl#standards_control_arn}.'''
        result = self._values.get("standards_control_arn")
        assert result is not None, "Required property 'standards_control_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disabled_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_control#disabled_reason SecurityhubStandardsControl#disabled_reason}.'''
        result = self._values.get("disabled_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubStandardsControlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityhubStandardsSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubStandardsSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_subscription aws_securityhub_standards_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        standards_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_subscription aws_securityhub_standards_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param standards_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_subscription#standards_arn SecurityhubStandardsSubscription#standards_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecurityhubStandardsSubscriptionConfig(
            standards_arn=standards_arn,
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
    @jsii.member(jsii_name="standardsArnInput")
    def standards_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "standardsArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="standardsArn")
    def standards_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "standardsArn"))

    @standards_arn.setter
    def standards_arn(self, value: builtins.str) -> None:
        jsii.set(self, "standardsArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.securityhub.SecurityhubStandardsSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "standards_arn": "standardsArn",
    },
)
class SecurityhubStandardsSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        standards_arn: builtins.str,
    ) -> None:
        '''AWS Security Hub.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param standards_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_subscription#standards_arn SecurityhubStandardsSubscription#standards_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "standards_arn": standards_arn,
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
    def standards_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/securityhub_standards_subscription#standards_arn SecurityhubStandardsSubscription#standards_arn}.'''
        result = self._values.get("standards_arn")
        assert result is not None, "Required property 'standards_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityhubStandardsSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecurityhubAccount",
    "SecurityhubAccountConfig",
    "SecurityhubActionTarget",
    "SecurityhubActionTargetConfig",
    "SecurityhubFindingAggregator",
    "SecurityhubFindingAggregatorConfig",
    "SecurityhubInsight",
    "SecurityhubInsightConfig",
    "SecurityhubInsightFilters",
    "SecurityhubInsightFiltersAwsAccountId",
    "SecurityhubInsightFiltersCompanyName",
    "SecurityhubInsightFiltersComplianceStatus",
    "SecurityhubInsightFiltersConfidence",
    "SecurityhubInsightFiltersCreatedAt",
    "SecurityhubInsightFiltersCreatedAtDateRange",
    "SecurityhubInsightFiltersCreatedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersCriticality",
    "SecurityhubInsightFiltersDescription",
    "SecurityhubInsightFiltersFindingProviderFieldsConfidence",
    "SecurityhubInsightFiltersFindingProviderFieldsCriticality",
    "SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsId",
    "SecurityhubInsightFiltersFindingProviderFieldsRelatedFindingsProductArn",
    "SecurityhubInsightFiltersFindingProviderFieldsSeverityLabel",
    "SecurityhubInsightFiltersFindingProviderFieldsSeverityOriginal",
    "SecurityhubInsightFiltersFindingProviderFieldsTypes",
    "SecurityhubInsightFiltersFirstObservedAt",
    "SecurityhubInsightFiltersFirstObservedAtDateRange",
    "SecurityhubInsightFiltersFirstObservedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersGeneratorId",
    "SecurityhubInsightFiltersId",
    "SecurityhubInsightFiltersKeyword",
    "SecurityhubInsightFiltersLastObservedAt",
    "SecurityhubInsightFiltersLastObservedAtDateRange",
    "SecurityhubInsightFiltersLastObservedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersMalwareName",
    "SecurityhubInsightFiltersMalwarePath",
    "SecurityhubInsightFiltersMalwareState",
    "SecurityhubInsightFiltersMalwareType",
    "SecurityhubInsightFiltersNetworkDestinationDomain",
    "SecurityhubInsightFiltersNetworkDestinationIpv4",
    "SecurityhubInsightFiltersNetworkDestinationIpv6",
    "SecurityhubInsightFiltersNetworkDestinationPort",
    "SecurityhubInsightFiltersNetworkDirection",
    "SecurityhubInsightFiltersNetworkProtocol",
    "SecurityhubInsightFiltersNetworkSourceDomain",
    "SecurityhubInsightFiltersNetworkSourceIpv4",
    "SecurityhubInsightFiltersNetworkSourceIpv6",
    "SecurityhubInsightFiltersNetworkSourceMac",
    "SecurityhubInsightFiltersNetworkSourcePort",
    "SecurityhubInsightFiltersNoteText",
    "SecurityhubInsightFiltersNoteUpdatedAt",
    "SecurityhubInsightFiltersNoteUpdatedAtDateRange",
    "SecurityhubInsightFiltersNoteUpdatedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersNoteUpdatedBy",
    "SecurityhubInsightFiltersOutputReference",
    "SecurityhubInsightFiltersProcessLaunchedAt",
    "SecurityhubInsightFiltersProcessLaunchedAtDateRange",
    "SecurityhubInsightFiltersProcessLaunchedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersProcessName",
    "SecurityhubInsightFiltersProcessParentPid",
    "SecurityhubInsightFiltersProcessPath",
    "SecurityhubInsightFiltersProcessPid",
    "SecurityhubInsightFiltersProcessTerminatedAt",
    "SecurityhubInsightFiltersProcessTerminatedAtDateRange",
    "SecurityhubInsightFiltersProcessTerminatedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersProductArn",
    "SecurityhubInsightFiltersProductFields",
    "SecurityhubInsightFiltersProductName",
    "SecurityhubInsightFiltersRecommendationText",
    "SecurityhubInsightFiltersRecordState",
    "SecurityhubInsightFiltersRelatedFindingsId",
    "SecurityhubInsightFiltersRelatedFindingsProductArn",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceIamInstanceProfileArn",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceImageId",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceIpv4Addresses",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceIpv6Addresses",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceKeyName",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAt",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRange",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceLaunchedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceSubnetId",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceType",
    "SecurityhubInsightFiltersResourceAwsEc2InstanceVpcId",
    "SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAt",
    "SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRange",
    "SecurityhubInsightFiltersResourceAwsIamAccessKeyCreatedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersResourceAwsIamAccessKeyStatus",
    "SecurityhubInsightFiltersResourceAwsIamAccessKeyUserName",
    "SecurityhubInsightFiltersResourceAwsS3BucketOwnerId",
    "SecurityhubInsightFiltersResourceAwsS3BucketOwnerName",
    "SecurityhubInsightFiltersResourceContainerImageId",
    "SecurityhubInsightFiltersResourceContainerImageName",
    "SecurityhubInsightFiltersResourceContainerLaunchedAt",
    "SecurityhubInsightFiltersResourceContainerLaunchedAtDateRange",
    "SecurityhubInsightFiltersResourceContainerLaunchedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersResourceContainerName",
    "SecurityhubInsightFiltersResourceDetailsOther",
    "SecurityhubInsightFiltersResourceId",
    "SecurityhubInsightFiltersResourcePartition",
    "SecurityhubInsightFiltersResourceRegion",
    "SecurityhubInsightFiltersResourceTags",
    "SecurityhubInsightFiltersResourceType",
    "SecurityhubInsightFiltersSeverityLabel",
    "SecurityhubInsightFiltersSourceUrl",
    "SecurityhubInsightFiltersThreatIntelIndicatorCategory",
    "SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAt",
    "SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRange",
    "SecurityhubInsightFiltersThreatIntelIndicatorLastObservedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersThreatIntelIndicatorSource",
    "SecurityhubInsightFiltersThreatIntelIndicatorSourceUrl",
    "SecurityhubInsightFiltersThreatIntelIndicatorType",
    "SecurityhubInsightFiltersThreatIntelIndicatorValue",
    "SecurityhubInsightFiltersTitle",
    "SecurityhubInsightFiltersType",
    "SecurityhubInsightFiltersUpdatedAt",
    "SecurityhubInsightFiltersUpdatedAtDateRange",
    "SecurityhubInsightFiltersUpdatedAtDateRangeOutputReference",
    "SecurityhubInsightFiltersUserDefinedValues",
    "SecurityhubInsightFiltersVerificationState",
    "SecurityhubInsightFiltersWorkflowStatus",
    "SecurityhubInviteAccepter",
    "SecurityhubInviteAccepterConfig",
    "SecurityhubMember",
    "SecurityhubMemberConfig",
    "SecurityhubOrganizationAdminAccount",
    "SecurityhubOrganizationAdminAccountConfig",
    "SecurityhubOrganizationConfiguration",
    "SecurityhubOrganizationConfigurationConfig",
    "SecurityhubProductSubscription",
    "SecurityhubProductSubscriptionConfig",
    "SecurityhubStandardsControl",
    "SecurityhubStandardsControlConfig",
    "SecurityhubStandardsSubscription",
    "SecurityhubStandardsSubscriptionConfig",
]

publication.publish()
