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


class DataAwsEmrReleaseLabels(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.DataAwsEmrReleaseLabels",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels aws_emr_release_labels}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        filters: typing.Optional["DataAwsEmrReleaseLabelsFilters"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels aws_emr_release_labels} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filters: filters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#filters DataAwsEmrReleaseLabels#filters}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsEmrReleaseLabelsConfig(
            filters=filters,
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
        application: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#application DataAwsEmrReleaseLabels#application}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#prefix DataAwsEmrReleaseLabels#prefix}.
        '''
        value = DataAwsEmrReleaseLabelsFilters(application=application, prefix=prefix)

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filters")
    def filters(self) -> "DataAwsEmrReleaseLabelsFiltersOutputReference":
        return typing.cast("DataAwsEmrReleaseLabelsFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseLabels")
    def release_labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "releaseLabels"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional["DataAwsEmrReleaseLabelsFilters"]:
        return typing.cast(typing.Optional["DataAwsEmrReleaseLabelsFilters"], jsii.get(self, "filtersInput"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.DataAwsEmrReleaseLabelsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filters": "filters",
    },
)
class DataAwsEmrReleaseLabelsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filters: typing.Optional["DataAwsEmrReleaseLabelsFilters"] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filters: filters block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#filters DataAwsEmrReleaseLabels#filters}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filters, dict):
            filters = DataAwsEmrReleaseLabelsFilters(**filters)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if filters is not None:
            self._values["filters"] = filters

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
    def filters(self) -> typing.Optional["DataAwsEmrReleaseLabelsFilters"]:
        '''filters block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#filters DataAwsEmrReleaseLabels#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["DataAwsEmrReleaseLabelsFilters"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsEmrReleaseLabelsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.DataAwsEmrReleaseLabelsFilters",
    jsii_struct_bases=[],
    name_mapping={"application": "application", "prefix": "prefix"},
)
class DataAwsEmrReleaseLabelsFilters:
    def __init__(
        self,
        *,
        application: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param application: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#application DataAwsEmrReleaseLabels#application}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#prefix DataAwsEmrReleaseLabels#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if application is not None:
            self._values["application"] = application
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def application(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#application DataAwsEmrReleaseLabels#application}.'''
        result = self._values.get("application")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/emr_release_labels#prefix DataAwsEmrReleaseLabels#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsEmrReleaseLabelsFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsEmrReleaseLabelsFiltersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.DataAwsEmrReleaseLabelsFiltersOutputReference",
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

    @jsii.member(jsii_name="resetApplication")
    def reset_application(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplication", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationInput")
    def application_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "application"))

    @application.setter
    def application(self, value: builtins.str) -> None:
        jsii.set(self, "application", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataAwsEmrReleaseLabelsFilters]:
        return typing.cast(typing.Optional[DataAwsEmrReleaseLabelsFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsEmrReleaseLabelsFilters],
    ) -> None:
        jsii.set(self, "internalValue", value)


class EmrCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster aws_emr_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        release_label: builtins.str,
        service_role: builtins.str,
        additional_info: typing.Optional[builtins.str] = None,
        applications: typing.Optional[typing.Sequence[builtins.str]] = None,
        autoscaling_role: typing.Optional[builtins.str] = None,
        auto_termination_policy: typing.Optional["EmrClusterAutoTerminationPolicy"] = None,
        bootstrap_action: typing.Optional[typing.Sequence["EmrClusterBootstrapAction"]] = None,
        configurations: typing.Optional[builtins.str] = None,
        configurations_json: typing.Optional[builtins.str] = None,
        core_instance_fleet: typing.Optional["EmrClusterCoreInstanceFleet"] = None,
        core_instance_group: typing.Optional["EmrClusterCoreInstanceGroup"] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        ebs_root_volume_size: typing.Optional[jsii.Number] = None,
        ec2_attributes: typing.Optional["EmrClusterEc2Attributes"] = None,
        keep_job_flow_alive_when_no_steps: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kerberos_attributes: typing.Optional["EmrClusterKerberosAttributes"] = None,
        log_encryption_kms_key_id: typing.Optional[builtins.str] = None,
        log_uri: typing.Optional[builtins.str] = None,
        master_instance_fleet: typing.Optional["EmrClusterMasterInstanceFleet"] = None,
        master_instance_group: typing.Optional["EmrClusterMasterInstanceGroup"] = None,
        scale_down_behavior: typing.Optional[builtins.str] = None,
        security_configuration: typing.Optional[builtins.str] = None,
        step: typing.Optional[typing.Sequence["EmrClusterStep"]] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        visible_to_all_users: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster aws_emr_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param release_label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#release_label EmrCluster#release_label}.
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#service_role EmrCluster#service_role}.
        :param additional_info: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_info EmrCluster#additional_info}.
        :param applications: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#applications EmrCluster#applications}.
        :param autoscaling_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#autoscaling_role EmrCluster#autoscaling_role}.
        :param auto_termination_policy: auto_termination_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#auto_termination_policy EmrCluster#auto_termination_policy}
        :param bootstrap_action: bootstrap_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bootstrap_action EmrCluster#bootstrap_action}
        :param configurations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}.
        :param configurations_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations_json EmrCluster#configurations_json}.
        :param core_instance_fleet: core_instance_fleet block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#core_instance_fleet EmrCluster#core_instance_fleet}
        :param core_instance_group: core_instance_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#core_instance_group EmrCluster#core_instance_group}
        :param custom_ami_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#custom_ami_id EmrCluster#custom_ami_id}.
        :param ebs_root_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_root_volume_size EmrCluster#ebs_root_volume_size}.
        :param ec2_attributes: ec2_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ec2_attributes EmrCluster#ec2_attributes}
        :param keep_job_flow_alive_when_no_steps: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#keep_job_flow_alive_when_no_steps EmrCluster#keep_job_flow_alive_when_no_steps}.
        :param kerberos_attributes: kerberos_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#kerberos_attributes EmrCluster#kerberos_attributes}
        :param log_encryption_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#log_encryption_kms_key_id EmrCluster#log_encryption_kms_key_id}.
        :param log_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#log_uri EmrCluster#log_uri}.
        :param master_instance_fleet: master_instance_fleet block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#master_instance_fleet EmrCluster#master_instance_fleet}
        :param master_instance_group: master_instance_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#master_instance_group EmrCluster#master_instance_group}
        :param scale_down_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#scale_down_behavior EmrCluster#scale_down_behavior}.
        :param security_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#security_configuration EmrCluster#security_configuration}.
        :param step: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#step EmrCluster#step}.
        :param step_concurrency_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#step_concurrency_level EmrCluster#step_concurrency_level}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#tags EmrCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#tags_all EmrCluster#tags_all}.
        :param termination_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#termination_protection EmrCluster#termination_protection}.
        :param visible_to_all_users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#visible_to_all_users EmrCluster#visible_to_all_users}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrClusterConfig(
            name=name,
            release_label=release_label,
            service_role=service_role,
            additional_info=additional_info,
            applications=applications,
            autoscaling_role=autoscaling_role,
            auto_termination_policy=auto_termination_policy,
            bootstrap_action=bootstrap_action,
            configurations=configurations,
            configurations_json=configurations_json,
            core_instance_fleet=core_instance_fleet,
            core_instance_group=core_instance_group,
            custom_ami_id=custom_ami_id,
            ebs_root_volume_size=ebs_root_volume_size,
            ec2_attributes=ec2_attributes,
            keep_job_flow_alive_when_no_steps=keep_job_flow_alive_when_no_steps,
            kerberos_attributes=kerberos_attributes,
            log_encryption_kms_key_id=log_encryption_kms_key_id,
            log_uri=log_uri,
            master_instance_fleet=master_instance_fleet,
            master_instance_group=master_instance_group,
            scale_down_behavior=scale_down_behavior,
            security_configuration=security_configuration,
            step=step,
            step_concurrency_level=step_concurrency_level,
            tags=tags,
            tags_all=tags_all,
            termination_protection=termination_protection,
            visible_to_all_users=visible_to_all_users,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAutoTerminationPolicy")
    def put_auto_termination_policy(
        self,
        *,
        idle_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param idle_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#idle_timeout EmrCluster#idle_timeout}.
        '''
        value = EmrClusterAutoTerminationPolicy(idle_timeout=idle_timeout)

        return typing.cast(None, jsii.invoke(self, "putAutoTerminationPolicy", [value]))

    @jsii.member(jsii_name="putCoreInstanceFleet")
    def put_core_instance_fleet(
        self,
        *,
        instance_type_configs: typing.Optional[typing.Sequence["EmrClusterCoreInstanceFleetInstanceTypeConfigs"]] = None,
        launch_specifications: typing.Optional["EmrClusterCoreInstanceFleetLaunchSpecifications"] = None,
        name: typing.Optional[builtins.str] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type_configs: instance_type_configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type_configs EmrCluster#instance_type_configs}
        :param launch_specifications: launch_specifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#launch_specifications EmrCluster#launch_specifications}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param target_on_demand_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_on_demand_capacity EmrCluster#target_on_demand_capacity}.
        :param target_spot_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_spot_capacity EmrCluster#target_spot_capacity}.
        '''
        value = EmrClusterCoreInstanceFleet(
            instance_type_configs=instance_type_configs,
            launch_specifications=launch_specifications,
            name=name,
            target_on_demand_capacity=target_on_demand_capacity,
            target_spot_capacity=target_spot_capacity,
        )

        return typing.cast(None, jsii.invoke(self, "putCoreInstanceFleet", [value]))

    @jsii.member(jsii_name="putCoreInstanceGroup")
    def put_core_instance_group(
        self,
        *,
        instance_type: builtins.str,
        autoscaling_policy: typing.Optional[builtins.str] = None,
        bid_price: typing.Optional[builtins.str] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrClusterCoreInstanceGroupEbsConfig"]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.
        :param autoscaling_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#autoscaling_policy EmrCluster#autoscaling_policy}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        :param instance_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_count EmrCluster#instance_count}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        '''
        value = EmrClusterCoreInstanceGroup(
            instance_type=instance_type,
            autoscaling_policy=autoscaling_policy,
            bid_price=bid_price,
            ebs_config=ebs_config,
            instance_count=instance_count,
            name=name,
        )

        return typing.cast(None, jsii.invoke(self, "putCoreInstanceGroup", [value]))

    @jsii.member(jsii_name="putEc2Attributes")
    def put_ec2_attributes(
        self,
        *,
        instance_profile: builtins.str,
        additional_master_security_groups: typing.Optional[builtins.str] = None,
        additional_slave_security_groups: typing.Optional[builtins.str] = None,
        emr_managed_master_security_group: typing.Optional[builtins.str] = None,
        emr_managed_slave_security_group: typing.Optional[builtins.str] = None,
        key_name: typing.Optional[builtins.str] = None,
        service_access_security_group: typing.Optional[builtins.str] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param instance_profile: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_profile EmrCluster#instance_profile}.
        :param additional_master_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_master_security_groups EmrCluster#additional_master_security_groups}.
        :param additional_slave_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_slave_security_groups EmrCluster#additional_slave_security_groups}.
        :param emr_managed_master_security_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#emr_managed_master_security_group EmrCluster#emr_managed_master_security_group}.
        :param emr_managed_slave_security_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#emr_managed_slave_security_group EmrCluster#emr_managed_slave_security_group}.
        :param key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#key_name EmrCluster#key_name}.
        :param service_access_security_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#service_access_security_group EmrCluster#service_access_security_group}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#subnet_id EmrCluster#subnet_id}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#subnet_ids EmrCluster#subnet_ids}.
        '''
        value = EmrClusterEc2Attributes(
            instance_profile=instance_profile,
            additional_master_security_groups=additional_master_security_groups,
            additional_slave_security_groups=additional_slave_security_groups,
            emr_managed_master_security_group=emr_managed_master_security_group,
            emr_managed_slave_security_group=emr_managed_slave_security_group,
            key_name=key_name,
            service_access_security_group=service_access_security_group,
            subnet_id=subnet_id,
            subnet_ids=subnet_ids,
        )

        return typing.cast(None, jsii.invoke(self, "putEc2Attributes", [value]))

    @jsii.member(jsii_name="putKerberosAttributes")
    def put_kerberos_attributes(
        self,
        *,
        kdc_admin_password: builtins.str,
        realm: builtins.str,
        ad_domain_join_password: typing.Optional[builtins.str] = None,
        ad_domain_join_user: typing.Optional[builtins.str] = None,
        cross_realm_trust_principal_password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param kdc_admin_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#kdc_admin_password EmrCluster#kdc_admin_password}.
        :param realm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#realm EmrCluster#realm}.
        :param ad_domain_join_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ad_domain_join_password EmrCluster#ad_domain_join_password}.
        :param ad_domain_join_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ad_domain_join_user EmrCluster#ad_domain_join_user}.
        :param cross_realm_trust_principal_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#cross_realm_trust_principal_password EmrCluster#cross_realm_trust_principal_password}.
        '''
        value = EmrClusterKerberosAttributes(
            kdc_admin_password=kdc_admin_password,
            realm=realm,
            ad_domain_join_password=ad_domain_join_password,
            ad_domain_join_user=ad_domain_join_user,
            cross_realm_trust_principal_password=cross_realm_trust_principal_password,
        )

        return typing.cast(None, jsii.invoke(self, "putKerberosAttributes", [value]))

    @jsii.member(jsii_name="putMasterInstanceFleet")
    def put_master_instance_fleet(
        self,
        *,
        instance_type_configs: typing.Optional[typing.Sequence["EmrClusterMasterInstanceFleetInstanceTypeConfigs"]] = None,
        launch_specifications: typing.Optional["EmrClusterMasterInstanceFleetLaunchSpecifications"] = None,
        name: typing.Optional[builtins.str] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type_configs: instance_type_configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type_configs EmrCluster#instance_type_configs}
        :param launch_specifications: launch_specifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#launch_specifications EmrCluster#launch_specifications}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param target_on_demand_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_on_demand_capacity EmrCluster#target_on_demand_capacity}.
        :param target_spot_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_spot_capacity EmrCluster#target_spot_capacity}.
        '''
        value = EmrClusterMasterInstanceFleet(
            instance_type_configs=instance_type_configs,
            launch_specifications=launch_specifications,
            name=name,
            target_on_demand_capacity=target_on_demand_capacity,
            target_spot_capacity=target_spot_capacity,
        )

        return typing.cast(None, jsii.invoke(self, "putMasterInstanceFleet", [value]))

    @jsii.member(jsii_name="putMasterInstanceGroup")
    def put_master_instance_group(
        self,
        *,
        instance_type: builtins.str,
        bid_price: typing.Optional[builtins.str] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrClusterMasterInstanceGroupEbsConfig"]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        :param instance_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_count EmrCluster#instance_count}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        '''
        value = EmrClusterMasterInstanceGroup(
            instance_type=instance_type,
            bid_price=bid_price,
            ebs_config=ebs_config,
            instance_count=instance_count,
            name=name,
        )

        return typing.cast(None, jsii.invoke(self, "putMasterInstanceGroup", [value]))

    @jsii.member(jsii_name="resetAdditionalInfo")
    def reset_additional_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalInfo", []))

    @jsii.member(jsii_name="resetApplications")
    def reset_applications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplications", []))

    @jsii.member(jsii_name="resetAutoscalingRole")
    def reset_autoscaling_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingRole", []))

    @jsii.member(jsii_name="resetAutoTerminationPolicy")
    def reset_auto_termination_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoTerminationPolicy", []))

    @jsii.member(jsii_name="resetBootstrapAction")
    def reset_bootstrap_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootstrapAction", []))

    @jsii.member(jsii_name="resetConfigurations")
    def reset_configurations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurations", []))

    @jsii.member(jsii_name="resetConfigurationsJson")
    def reset_configurations_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationsJson", []))

    @jsii.member(jsii_name="resetCoreInstanceFleet")
    def reset_core_instance_fleet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreInstanceFleet", []))

    @jsii.member(jsii_name="resetCoreInstanceGroup")
    def reset_core_instance_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreInstanceGroup", []))

    @jsii.member(jsii_name="resetCustomAmiId")
    def reset_custom_ami_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAmiId", []))

    @jsii.member(jsii_name="resetEbsRootVolumeSize")
    def reset_ebs_root_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsRootVolumeSize", []))

    @jsii.member(jsii_name="resetEc2Attributes")
    def reset_ec2_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2Attributes", []))

    @jsii.member(jsii_name="resetKeepJobFlowAliveWhenNoSteps")
    def reset_keep_job_flow_alive_when_no_steps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepJobFlowAliveWhenNoSteps", []))

    @jsii.member(jsii_name="resetKerberosAttributes")
    def reset_kerberos_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKerberosAttributes", []))

    @jsii.member(jsii_name="resetLogEncryptionKmsKeyId")
    def reset_log_encryption_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogEncryptionKmsKeyId", []))

    @jsii.member(jsii_name="resetLogUri")
    def reset_log_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogUri", []))

    @jsii.member(jsii_name="resetMasterInstanceFleet")
    def reset_master_instance_fleet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterInstanceFleet", []))

    @jsii.member(jsii_name="resetMasterInstanceGroup")
    def reset_master_instance_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterInstanceGroup", []))

    @jsii.member(jsii_name="resetScaleDownBehavior")
    def reset_scale_down_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleDownBehavior", []))

    @jsii.member(jsii_name="resetSecurityConfiguration")
    def reset_security_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityConfiguration", []))

    @jsii.member(jsii_name="resetStep")
    def reset_step(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStep", []))

    @jsii.member(jsii_name="resetStepConcurrencyLevel")
    def reset_step_concurrency_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStepConcurrencyLevel", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTerminationProtection")
    def reset_termination_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationProtection", []))

    @jsii.member(jsii_name="resetVisibleToAllUsers")
    def reset_visible_to_all_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibleToAllUsers", []))

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
    @jsii.member(jsii_name="autoTerminationPolicy")
    def auto_termination_policy(
        self,
    ) -> "EmrClusterAutoTerminationPolicyOutputReference":
        return typing.cast("EmrClusterAutoTerminationPolicyOutputReference", jsii.get(self, "autoTerminationPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterState")
    def cluster_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coreInstanceFleet")
    def core_instance_fleet(self) -> "EmrClusterCoreInstanceFleetOutputReference":
        return typing.cast("EmrClusterCoreInstanceFleetOutputReference", jsii.get(self, "coreInstanceFleet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coreInstanceGroup")
    def core_instance_group(self) -> "EmrClusterCoreInstanceGroupOutputReference":
        return typing.cast("EmrClusterCoreInstanceGroupOutputReference", jsii.get(self, "coreInstanceGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2Attributes")
    def ec2_attributes(self) -> "EmrClusterEc2AttributesOutputReference":
        return typing.cast("EmrClusterEc2AttributesOutputReference", jsii.get(self, "ec2Attributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosAttributes")
    def kerberos_attributes(self) -> "EmrClusterKerberosAttributesOutputReference":
        return typing.cast("EmrClusterKerberosAttributesOutputReference", jsii.get(self, "kerberosAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterInstanceFleet")
    def master_instance_fleet(self) -> "EmrClusterMasterInstanceFleetOutputReference":
        return typing.cast("EmrClusterMasterInstanceFleetOutputReference", jsii.get(self, "masterInstanceFleet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterInstanceGroup")
    def master_instance_group(self) -> "EmrClusterMasterInstanceGroupOutputReference":
        return typing.cast("EmrClusterMasterInstanceGroupOutputReference", jsii.get(self, "masterInstanceGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterPublicDns")
    def master_public_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterPublicDns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalInfoInput")
    def additional_info_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "additionalInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationsInput")
    def applications_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "applicationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingRoleInput")
    def autoscaling_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoscalingRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoTerminationPolicyInput")
    def auto_termination_policy_input(
        self,
    ) -> typing.Optional["EmrClusterAutoTerminationPolicy"]:
        return typing.cast(typing.Optional["EmrClusterAutoTerminationPolicy"], jsii.get(self, "autoTerminationPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapActionInput")
    def bootstrap_action_input(
        self,
    ) -> typing.Optional[typing.List["EmrClusterBootstrapAction"]]:
        return typing.cast(typing.Optional[typing.List["EmrClusterBootstrapAction"]], jsii.get(self, "bootstrapActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationsInput")
    def configurations_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationsJsonInput")
    def configurations_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationsJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coreInstanceFleetInput")
    def core_instance_fleet_input(
        self,
    ) -> typing.Optional["EmrClusterCoreInstanceFleet"]:
        return typing.cast(typing.Optional["EmrClusterCoreInstanceFleet"], jsii.get(self, "coreInstanceFleetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coreInstanceGroupInput")
    def core_instance_group_input(
        self,
    ) -> typing.Optional["EmrClusterCoreInstanceGroup"]:
        return typing.cast(typing.Optional["EmrClusterCoreInstanceGroup"], jsii.get(self, "coreInstanceGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customAmiIdInput")
    def custom_ami_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customAmiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsRootVolumeSizeInput")
    def ebs_root_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsRootVolumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2AttributesInput")
    def ec2_attributes_input(self) -> typing.Optional["EmrClusterEc2Attributes"]:
        return typing.cast(typing.Optional["EmrClusterEc2Attributes"], jsii.get(self, "ec2AttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepJobFlowAliveWhenNoStepsInput")
    def keep_job_flow_alive_when_no_steps_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "keepJobFlowAliveWhenNoStepsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kerberosAttributesInput")
    def kerberos_attributes_input(
        self,
    ) -> typing.Optional["EmrClusterKerberosAttributes"]:
        return typing.cast(typing.Optional["EmrClusterKerberosAttributes"], jsii.get(self, "kerberosAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logEncryptionKmsKeyIdInput")
    def log_encryption_kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logEncryptionKmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logUriInput")
    def log_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterInstanceFleetInput")
    def master_instance_fleet_input(
        self,
    ) -> typing.Optional["EmrClusterMasterInstanceFleet"]:
        return typing.cast(typing.Optional["EmrClusterMasterInstanceFleet"], jsii.get(self, "masterInstanceFleetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterInstanceGroupInput")
    def master_instance_group_input(
        self,
    ) -> typing.Optional["EmrClusterMasterInstanceGroup"]:
        return typing.cast(typing.Optional["EmrClusterMasterInstanceGroup"], jsii.get(self, "masterInstanceGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseLabelInput")
    def release_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "releaseLabelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleDownBehaviorInput")
    def scale_down_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scaleDownBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityConfigurationInput")
    def security_configuration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleInput")
    def service_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepConcurrencyLevelInput")
    def step_concurrency_level_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "stepConcurrencyLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepInput")
    def step_input(self) -> typing.Optional[typing.List["EmrClusterStep"]]:
        return typing.cast(typing.Optional[typing.List["EmrClusterStep"]], jsii.get(self, "stepInput"))

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
    @jsii.member(jsii_name="terminationProtectionInput")
    def termination_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "terminationProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibleToAllUsersInput")
    def visible_to_all_users_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "visibleToAllUsersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalInfo")
    def additional_info(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "additionalInfo"))

    @additional_info.setter
    def additional_info(self, value: builtins.str) -> None:
        jsii.set(self, "additionalInfo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applications")
    def applications(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "applications"))

    @applications.setter
    def applications(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "applications", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingRole")
    def autoscaling_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoscalingRole"))

    @autoscaling_role.setter
    def autoscaling_role(self, value: builtins.str) -> None:
        jsii.set(self, "autoscalingRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapAction")
    def bootstrap_action(self) -> typing.List["EmrClusterBootstrapAction"]:
        return typing.cast(typing.List["EmrClusterBootstrapAction"], jsii.get(self, "bootstrapAction"))

    @bootstrap_action.setter
    def bootstrap_action(self, value: typing.List["EmrClusterBootstrapAction"]) -> None:
        jsii.set(self, "bootstrapAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurations")
    def configurations(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurations"))

    @configurations.setter
    def configurations(self, value: builtins.str) -> None:
        jsii.set(self, "configurations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationsJson")
    def configurations_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationsJson"))

    @configurations_json.setter
    def configurations_json(self, value: builtins.str) -> None:
        jsii.set(self, "configurationsJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customAmiId")
    def custom_ami_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customAmiId"))

    @custom_ami_id.setter
    def custom_ami_id(self, value: builtins.str) -> None:
        jsii.set(self, "customAmiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsRootVolumeSize")
    def ebs_root_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsRootVolumeSize"))

    @ebs_root_volume_size.setter
    def ebs_root_volume_size(self, value: jsii.Number) -> None:
        jsii.set(self, "ebsRootVolumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepJobFlowAliveWhenNoSteps")
    def keep_job_flow_alive_when_no_steps(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "keepJobFlowAliveWhenNoSteps"))

    @keep_job_flow_alive_when_no_steps.setter
    def keep_job_flow_alive_when_no_steps(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "keepJobFlowAliveWhenNoSteps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logEncryptionKmsKeyId")
    def log_encryption_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logEncryptionKmsKeyId"))

    @log_encryption_kms_key_id.setter
    def log_encryption_kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "logEncryptionKmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logUri")
    def log_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logUri"))

    @log_uri.setter
    def log_uri(self, value: builtins.str) -> None:
        jsii.set(self, "logUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseLabel")
    def release_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "releaseLabel"))

    @release_label.setter
    def release_label(self, value: builtins.str) -> None:
        jsii.set(self, "releaseLabel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleDownBehavior")
    def scale_down_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleDownBehavior"))

    @scale_down_behavior.setter
    def scale_down_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "scaleDownBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityConfiguration"))

    @security_configuration.setter
    def security_configuration(self, value: builtins.str) -> None:
        jsii.set(self, "securityConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        jsii.set(self, "serviceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="step")
    def step(self) -> typing.List["EmrClusterStep"]:
        return typing.cast(typing.List["EmrClusterStep"], jsii.get(self, "step"))

    @step.setter
    def step(self, value: typing.List["EmrClusterStep"]) -> None:
        jsii.set(self, "step", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepConcurrencyLevel")
    def step_concurrency_level(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "stepConcurrencyLevel"))

    @step_concurrency_level.setter
    def step_concurrency_level(self, value: jsii.Number) -> None:
        jsii.set(self, "stepConcurrencyLevel", value)

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
    @jsii.member(jsii_name="terminationProtection")
    def termination_protection(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "terminationProtection"))

    @termination_protection.setter
    def termination_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "terminationProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visibleToAllUsers")
    def visible_to_all_users(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "visibleToAllUsers"))

    @visible_to_all_users.setter
    def visible_to_all_users(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "visibleToAllUsers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterAutoTerminationPolicy",
    jsii_struct_bases=[],
    name_mapping={"idle_timeout": "idleTimeout"},
)
class EmrClusterAutoTerminationPolicy:
    def __init__(self, *, idle_timeout: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param idle_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#idle_timeout EmrCluster#idle_timeout}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout

    @builtins.property
    def idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#idle_timeout EmrCluster#idle_timeout}.'''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterAutoTerminationPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterAutoTerminationPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterAutoTerminationPolicyOutputReference",
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

    @jsii.member(jsii_name="resetIdleTimeout")
    def reset_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleTimeout", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleTimeoutInput")
    def idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleTimeout")
    def idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleTimeout"))

    @idle_timeout.setter
    def idle_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "idleTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterAutoTerminationPolicy]:
        return typing.cast(typing.Optional[EmrClusterAutoTerminationPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterAutoTerminationPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterBootstrapAction",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "path": "path", "args": "args"},
)
class EmrClusterBootstrapAction:
    def __init__(
        self,
        *,
        name: builtins.str,
        path: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#path EmrCluster#path}.
        :param args: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#args EmrCluster#args}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "path": path,
        }
        if args is not None:
            self._values["args"] = args

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#path EmrCluster#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#args EmrCluster#args}.'''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterBootstrapAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "release_label": "releaseLabel",
        "service_role": "serviceRole",
        "additional_info": "additionalInfo",
        "applications": "applications",
        "autoscaling_role": "autoscalingRole",
        "auto_termination_policy": "autoTerminationPolicy",
        "bootstrap_action": "bootstrapAction",
        "configurations": "configurations",
        "configurations_json": "configurationsJson",
        "core_instance_fleet": "coreInstanceFleet",
        "core_instance_group": "coreInstanceGroup",
        "custom_ami_id": "customAmiId",
        "ebs_root_volume_size": "ebsRootVolumeSize",
        "ec2_attributes": "ec2Attributes",
        "keep_job_flow_alive_when_no_steps": "keepJobFlowAliveWhenNoSteps",
        "kerberos_attributes": "kerberosAttributes",
        "log_encryption_kms_key_id": "logEncryptionKmsKeyId",
        "log_uri": "logUri",
        "master_instance_fleet": "masterInstanceFleet",
        "master_instance_group": "masterInstanceGroup",
        "scale_down_behavior": "scaleDownBehavior",
        "security_configuration": "securityConfiguration",
        "step": "step",
        "step_concurrency_level": "stepConcurrencyLevel",
        "tags": "tags",
        "tags_all": "tagsAll",
        "termination_protection": "terminationProtection",
        "visible_to_all_users": "visibleToAllUsers",
    },
)
class EmrClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        release_label: builtins.str,
        service_role: builtins.str,
        additional_info: typing.Optional[builtins.str] = None,
        applications: typing.Optional[typing.Sequence[builtins.str]] = None,
        autoscaling_role: typing.Optional[builtins.str] = None,
        auto_termination_policy: typing.Optional[EmrClusterAutoTerminationPolicy] = None,
        bootstrap_action: typing.Optional[typing.Sequence[EmrClusterBootstrapAction]] = None,
        configurations: typing.Optional[builtins.str] = None,
        configurations_json: typing.Optional[builtins.str] = None,
        core_instance_fleet: typing.Optional["EmrClusterCoreInstanceFleet"] = None,
        core_instance_group: typing.Optional["EmrClusterCoreInstanceGroup"] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        ebs_root_volume_size: typing.Optional[jsii.Number] = None,
        ec2_attributes: typing.Optional["EmrClusterEc2Attributes"] = None,
        keep_job_flow_alive_when_no_steps: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kerberos_attributes: typing.Optional["EmrClusterKerberosAttributes"] = None,
        log_encryption_kms_key_id: typing.Optional[builtins.str] = None,
        log_uri: typing.Optional[builtins.str] = None,
        master_instance_fleet: typing.Optional["EmrClusterMasterInstanceFleet"] = None,
        master_instance_group: typing.Optional["EmrClusterMasterInstanceGroup"] = None,
        scale_down_behavior: typing.Optional[builtins.str] = None,
        security_configuration: typing.Optional[builtins.str] = None,
        step: typing.Optional[typing.Sequence["EmrClusterStep"]] = None,
        step_concurrency_level: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        termination_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        visible_to_all_users: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param release_label: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#release_label EmrCluster#release_label}.
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#service_role EmrCluster#service_role}.
        :param additional_info: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_info EmrCluster#additional_info}.
        :param applications: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#applications EmrCluster#applications}.
        :param autoscaling_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#autoscaling_role EmrCluster#autoscaling_role}.
        :param auto_termination_policy: auto_termination_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#auto_termination_policy EmrCluster#auto_termination_policy}
        :param bootstrap_action: bootstrap_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bootstrap_action EmrCluster#bootstrap_action}
        :param configurations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}.
        :param configurations_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations_json EmrCluster#configurations_json}.
        :param core_instance_fleet: core_instance_fleet block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#core_instance_fleet EmrCluster#core_instance_fleet}
        :param core_instance_group: core_instance_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#core_instance_group EmrCluster#core_instance_group}
        :param custom_ami_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#custom_ami_id EmrCluster#custom_ami_id}.
        :param ebs_root_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_root_volume_size EmrCluster#ebs_root_volume_size}.
        :param ec2_attributes: ec2_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ec2_attributes EmrCluster#ec2_attributes}
        :param keep_job_flow_alive_when_no_steps: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#keep_job_flow_alive_when_no_steps EmrCluster#keep_job_flow_alive_when_no_steps}.
        :param kerberos_attributes: kerberos_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#kerberos_attributes EmrCluster#kerberos_attributes}
        :param log_encryption_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#log_encryption_kms_key_id EmrCluster#log_encryption_kms_key_id}.
        :param log_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#log_uri EmrCluster#log_uri}.
        :param master_instance_fleet: master_instance_fleet block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#master_instance_fleet EmrCluster#master_instance_fleet}
        :param master_instance_group: master_instance_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#master_instance_group EmrCluster#master_instance_group}
        :param scale_down_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#scale_down_behavior EmrCluster#scale_down_behavior}.
        :param security_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#security_configuration EmrCluster#security_configuration}.
        :param step: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#step EmrCluster#step}.
        :param step_concurrency_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#step_concurrency_level EmrCluster#step_concurrency_level}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#tags EmrCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#tags_all EmrCluster#tags_all}.
        :param termination_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#termination_protection EmrCluster#termination_protection}.
        :param visible_to_all_users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#visible_to_all_users EmrCluster#visible_to_all_users}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(auto_termination_policy, dict):
            auto_termination_policy = EmrClusterAutoTerminationPolicy(**auto_termination_policy)
        if isinstance(core_instance_fleet, dict):
            core_instance_fleet = EmrClusterCoreInstanceFleet(**core_instance_fleet)
        if isinstance(core_instance_group, dict):
            core_instance_group = EmrClusterCoreInstanceGroup(**core_instance_group)
        if isinstance(ec2_attributes, dict):
            ec2_attributes = EmrClusterEc2Attributes(**ec2_attributes)
        if isinstance(kerberos_attributes, dict):
            kerberos_attributes = EmrClusterKerberosAttributes(**kerberos_attributes)
        if isinstance(master_instance_fleet, dict):
            master_instance_fleet = EmrClusterMasterInstanceFleet(**master_instance_fleet)
        if isinstance(master_instance_group, dict):
            master_instance_group = EmrClusterMasterInstanceGroup(**master_instance_group)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "release_label": release_label,
            "service_role": service_role,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if additional_info is not None:
            self._values["additional_info"] = additional_info
        if applications is not None:
            self._values["applications"] = applications
        if autoscaling_role is not None:
            self._values["autoscaling_role"] = autoscaling_role
        if auto_termination_policy is not None:
            self._values["auto_termination_policy"] = auto_termination_policy
        if bootstrap_action is not None:
            self._values["bootstrap_action"] = bootstrap_action
        if configurations is not None:
            self._values["configurations"] = configurations
        if configurations_json is not None:
            self._values["configurations_json"] = configurations_json
        if core_instance_fleet is not None:
            self._values["core_instance_fleet"] = core_instance_fleet
        if core_instance_group is not None:
            self._values["core_instance_group"] = core_instance_group
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if ebs_root_volume_size is not None:
            self._values["ebs_root_volume_size"] = ebs_root_volume_size
        if ec2_attributes is not None:
            self._values["ec2_attributes"] = ec2_attributes
        if keep_job_flow_alive_when_no_steps is not None:
            self._values["keep_job_flow_alive_when_no_steps"] = keep_job_flow_alive_when_no_steps
        if kerberos_attributes is not None:
            self._values["kerberos_attributes"] = kerberos_attributes
        if log_encryption_kms_key_id is not None:
            self._values["log_encryption_kms_key_id"] = log_encryption_kms_key_id
        if log_uri is not None:
            self._values["log_uri"] = log_uri
        if master_instance_fleet is not None:
            self._values["master_instance_fleet"] = master_instance_fleet
        if master_instance_group is not None:
            self._values["master_instance_group"] = master_instance_group
        if scale_down_behavior is not None:
            self._values["scale_down_behavior"] = scale_down_behavior
        if security_configuration is not None:
            self._values["security_configuration"] = security_configuration
        if step is not None:
            self._values["step"] = step
        if step_concurrency_level is not None:
            self._values["step_concurrency_level"] = step_concurrency_level
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if visible_to_all_users is not None:
            self._values["visible_to_all_users"] = visible_to_all_users

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def release_label(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#release_label EmrCluster#release_label}.'''
        result = self._values.get("release_label")
        assert result is not None, "Required property 'release_label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#service_role EmrCluster#service_role}.'''
        result = self._values.get("service_role")
        assert result is not None, "Required property 'service_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_info(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_info EmrCluster#additional_info}.'''
        result = self._values.get("additional_info")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def applications(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#applications EmrCluster#applications}.'''
        result = self._values.get("applications")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def autoscaling_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#autoscaling_role EmrCluster#autoscaling_role}.'''
        result = self._values.get("autoscaling_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_termination_policy(
        self,
    ) -> typing.Optional[EmrClusterAutoTerminationPolicy]:
        '''auto_termination_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#auto_termination_policy EmrCluster#auto_termination_policy}
        '''
        result = self._values.get("auto_termination_policy")
        return typing.cast(typing.Optional[EmrClusterAutoTerminationPolicy], result)

    @builtins.property
    def bootstrap_action(
        self,
    ) -> typing.Optional[typing.List[EmrClusterBootstrapAction]]:
        '''bootstrap_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bootstrap_action EmrCluster#bootstrap_action}
        '''
        result = self._values.get("bootstrap_action")
        return typing.cast(typing.Optional[typing.List[EmrClusterBootstrapAction]], result)

    @builtins.property
    def configurations(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}.'''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configurations_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations_json EmrCluster#configurations_json}.'''
        result = self._values.get("configurations_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def core_instance_fleet(self) -> typing.Optional["EmrClusterCoreInstanceFleet"]:
        '''core_instance_fleet block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#core_instance_fleet EmrCluster#core_instance_fleet}
        '''
        result = self._values.get("core_instance_fleet")
        return typing.cast(typing.Optional["EmrClusterCoreInstanceFleet"], result)

    @builtins.property
    def core_instance_group(self) -> typing.Optional["EmrClusterCoreInstanceGroup"]:
        '''core_instance_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#core_instance_group EmrCluster#core_instance_group}
        '''
        result = self._values.get("core_instance_group")
        return typing.cast(typing.Optional["EmrClusterCoreInstanceGroup"], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#custom_ami_id EmrCluster#custom_ami_id}.'''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_root_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_root_volume_size EmrCluster#ebs_root_volume_size}.'''
        result = self._values.get("ebs_root_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2_attributes(self) -> typing.Optional["EmrClusterEc2Attributes"]:
        '''ec2_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ec2_attributes EmrCluster#ec2_attributes}
        '''
        result = self._values.get("ec2_attributes")
        return typing.cast(typing.Optional["EmrClusterEc2Attributes"], result)

    @builtins.property
    def keep_job_flow_alive_when_no_steps(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#keep_job_flow_alive_when_no_steps EmrCluster#keep_job_flow_alive_when_no_steps}.'''
        result = self._values.get("keep_job_flow_alive_when_no_steps")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kerberos_attributes(self) -> typing.Optional["EmrClusterKerberosAttributes"]:
        '''kerberos_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#kerberos_attributes EmrCluster#kerberos_attributes}
        '''
        result = self._values.get("kerberos_attributes")
        return typing.cast(typing.Optional["EmrClusterKerberosAttributes"], result)

    @builtins.property
    def log_encryption_kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#log_encryption_kms_key_id EmrCluster#log_encryption_kms_key_id}.'''
        result = self._values.get("log_encryption_kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#log_uri EmrCluster#log_uri}.'''
        result = self._values.get("log_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_instance_fleet(self) -> typing.Optional["EmrClusterMasterInstanceFleet"]:
        '''master_instance_fleet block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#master_instance_fleet EmrCluster#master_instance_fleet}
        '''
        result = self._values.get("master_instance_fleet")
        return typing.cast(typing.Optional["EmrClusterMasterInstanceFleet"], result)

    @builtins.property
    def master_instance_group(self) -> typing.Optional["EmrClusterMasterInstanceGroup"]:
        '''master_instance_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#master_instance_group EmrCluster#master_instance_group}
        '''
        result = self._values.get("master_instance_group")
        return typing.cast(typing.Optional["EmrClusterMasterInstanceGroup"], result)

    @builtins.property
    def scale_down_behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#scale_down_behavior EmrCluster#scale_down_behavior}.'''
        result = self._values.get("scale_down_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_configuration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#security_configuration EmrCluster#security_configuration}.'''
        result = self._values.get("security_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def step(self) -> typing.Optional[typing.List["EmrClusterStep"]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#step EmrCluster#step}.'''
        result = self._values.get("step")
        return typing.cast(typing.Optional[typing.List["EmrClusterStep"]], result)

    @builtins.property
    def step_concurrency_level(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#step_concurrency_level EmrCluster#step_concurrency_level}.'''
        result = self._values.get("step_concurrency_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#tags EmrCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#tags_all EmrCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def termination_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#termination_protection EmrCluster#termination_protection}.'''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def visible_to_all_users(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#visible_to_all_users EmrCluster#visible_to_all_users}.'''
        result = self._values.get("visible_to_all_users")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleet",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type_configs": "instanceTypeConfigs",
        "launch_specifications": "launchSpecifications",
        "name": "name",
        "target_on_demand_capacity": "targetOnDemandCapacity",
        "target_spot_capacity": "targetSpotCapacity",
    },
)
class EmrClusterCoreInstanceFleet:
    def __init__(
        self,
        *,
        instance_type_configs: typing.Optional[typing.Sequence["EmrClusterCoreInstanceFleetInstanceTypeConfigs"]] = None,
        launch_specifications: typing.Optional["EmrClusterCoreInstanceFleetLaunchSpecifications"] = None,
        name: typing.Optional[builtins.str] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type_configs: instance_type_configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type_configs EmrCluster#instance_type_configs}
        :param launch_specifications: launch_specifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#launch_specifications EmrCluster#launch_specifications}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param target_on_demand_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_on_demand_capacity EmrCluster#target_on_demand_capacity}.
        :param target_spot_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_spot_capacity EmrCluster#target_spot_capacity}.
        '''
        if isinstance(launch_specifications, dict):
            launch_specifications = EmrClusterCoreInstanceFleetLaunchSpecifications(**launch_specifications)
        self._values: typing.Dict[str, typing.Any] = {}
        if instance_type_configs is not None:
            self._values["instance_type_configs"] = instance_type_configs
        if launch_specifications is not None:
            self._values["launch_specifications"] = launch_specifications
        if name is not None:
            self._values["name"] = name
        if target_on_demand_capacity is not None:
            self._values["target_on_demand_capacity"] = target_on_demand_capacity
        if target_spot_capacity is not None:
            self._values["target_spot_capacity"] = target_spot_capacity

    @builtins.property
    def instance_type_configs(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceFleetInstanceTypeConfigs"]]:
        '''instance_type_configs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type_configs EmrCluster#instance_type_configs}
        '''
        result = self._values.get("instance_type_configs")
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceFleetInstanceTypeConfigs"]], result)

    @builtins.property
    def launch_specifications(
        self,
    ) -> typing.Optional["EmrClusterCoreInstanceFleetLaunchSpecifications"]:
        '''launch_specifications block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#launch_specifications EmrCluster#launch_specifications}
        '''
        result = self._values.get("launch_specifications")
        return typing.cast(typing.Optional["EmrClusterCoreInstanceFleetLaunchSpecifications"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_on_demand_capacity EmrCluster#target_on_demand_capacity}.'''
        result = self._values.get("target_on_demand_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_spot_capacity EmrCluster#target_spot_capacity}.'''
        result = self._values.get("target_spot_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetInstanceTypeConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "bid_price": "bidPrice",
        "bid_price_as_percentage_of_on_demand_price": "bidPriceAsPercentageOfOnDemandPrice",
        "configurations": "configurations",
        "ebs_config": "ebsConfig",
        "weighted_capacity": "weightedCapacity",
    },
)
class EmrClusterCoreInstanceFleetInstanceTypeConfigs:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        bid_price: typing.Optional[builtins.str] = None,
        bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number] = None,
        configurations: typing.Optional[typing.Sequence["EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations"]] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig"]] = None,
        weighted_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.
        :param bid_price_as_percentage_of_on_demand_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price_as_percentage_of_on_demand_price EmrCluster#bid_price_as_percentage_of_on_demand_price}.
        :param configurations: configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        :param weighted_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#weighted_capacity EmrCluster#weighted_capacity}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
        }
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if bid_price_as_percentage_of_on_demand_price is not None:
            self._values["bid_price_as_percentage_of_on_demand_price"] = bid_price_as_percentage_of_on_demand_price
        if configurations is not None:
            self._values["configurations"] = configurations
        if ebs_config is not None:
            self._values["ebs_config"] = ebs_config
        if weighted_capacity is not None:
            self._values["weighted_capacity"] = weighted_capacity

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.'''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_price_as_percentage_of_on_demand_price(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price_as_percentage_of_on_demand_price EmrCluster#bid_price_as_percentage_of_on_demand_price}.'''
        result = self._values.get("bid_price_as_percentage_of_on_demand_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def configurations(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations"]]:
        '''configurations block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations"]], result)

    @builtins.property
    def ebs_config(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig"]]:
        '''ebs_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        '''
        result = self._values.get("ebs_config")
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig"]], result)

    @builtins.property
    def weighted_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#weighted_capacity EmrCluster#weighted_capacity}.'''
        result = self._values.get("weighted_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleetInstanceTypeConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations",
    jsii_struct_bases=[],
    name_mapping={"classification": "classification", "properties": "properties"},
)
class EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations:
    def __init__(
        self,
        *,
        classification: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param classification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#classification EmrCluster#classification}.
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#properties EmrCluster#properties}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if classification is not None:
            self._values["classification"] = classification
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def classification(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#classification EmrCluster#classification}.'''
        result = self._values.get("classification")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#properties EmrCluster#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "size": "size",
        "type": "type",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig:
    def __init__(
        self,
        *,
        size: jsii.Number,
        type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "type": type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetLaunchSpecifications",
    jsii_struct_bases=[],
    name_mapping={
        "on_demand_specification": "onDemandSpecification",
        "spot_specification": "spotSpecification",
    },
)
class EmrClusterCoreInstanceFleetLaunchSpecifications:
    def __init__(
        self,
        *,
        on_demand_specification: typing.Optional[typing.Sequence["EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification"]] = None,
        spot_specification: typing.Optional[typing.Sequence["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"]] = None,
    ) -> None:
        '''
        :param on_demand_specification: on_demand_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#on_demand_specification EmrCluster#on_demand_specification}
        :param spot_specification: spot_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#spot_specification EmrCluster#spot_specification}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if on_demand_specification is not None:
            self._values["on_demand_specification"] = on_demand_specification
        if spot_specification is not None:
            self._values["spot_specification"] = spot_specification

    @builtins.property
    def on_demand_specification(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification"]]:
        '''on_demand_specification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#on_demand_specification EmrCluster#on_demand_specification}
        '''
        result = self._values.get("on_demand_specification")
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification"]], result)

    @builtins.property
    def spot_specification(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"]]:
        '''spot_specification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#spot_specification EmrCluster#spot_specification}
        '''
        result = self._values.get("spot_specification")
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleetLaunchSpecifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification",
    jsii_struct_bases=[],
    name_mapping={"allocation_strategy": "allocationStrategy"},
)
class EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification:
    def __init__(self, *, allocation_strategy: builtins.str) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterCoreInstanceFleetLaunchSpecificationsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetLaunchSpecificationsOutputReference",
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

    @jsii.member(jsii_name="resetOnDemandSpecification")
    def reset_on_demand_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemandSpecification", []))

    @jsii.member(jsii_name="resetSpotSpecification")
    def reset_spot_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotSpecification", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onDemandSpecificationInput")
    def on_demand_specification_input(
        self,
    ) -> typing.Optional[typing.List[EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification]]:
        return typing.cast(typing.Optional[typing.List[EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification]], jsii.get(self, "onDemandSpecificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotSpecificationInput")
    def spot_specification_input(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"]]:
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"]], jsii.get(self, "spotSpecificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onDemandSpecification")
    def on_demand_specification(
        self,
    ) -> typing.List[EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification]:
        return typing.cast(typing.List[EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification], jsii.get(self, "onDemandSpecification"))

    @on_demand_specification.setter
    def on_demand_specification(
        self,
        value: typing.List[EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification],
    ) -> None:
        jsii.set(self, "onDemandSpecification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotSpecification")
    def spot_specification(
        self,
    ) -> typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"]:
        return typing.cast(typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"], jsii.get(self, "spotSpecification"))

    @spot_specification.setter
    def spot_specification(
        self,
        value: typing.List["EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification"],
    ) -> None:
        jsii.set(self, "spotSpecification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[EmrClusterCoreInstanceFleetLaunchSpecifications]:
        return typing.cast(typing.Optional[EmrClusterCoreInstanceFleetLaunchSpecifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterCoreInstanceFleetLaunchSpecifications],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "timeout_action": "timeoutAction",
        "timeout_duration_minutes": "timeoutDurationMinutes",
        "block_duration_minutes": "blockDurationMinutes",
    },
)
class EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        timeout_action: builtins.str,
        timeout_duration_minutes: jsii.Number,
        block_duration_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.
        :param timeout_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_action EmrCluster#timeout_action}.
        :param timeout_duration_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_duration_minutes EmrCluster#timeout_duration_minutes}.
        :param block_duration_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#block_duration_minutes EmrCluster#block_duration_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
            "timeout_action": timeout_action,
            "timeout_duration_minutes": timeout_duration_minutes,
        }
        if block_duration_minutes is not None:
            self._values["block_duration_minutes"] = block_duration_minutes

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_action EmrCluster#timeout_action}.'''
        result = self._values.get("timeout_action")
        assert result is not None, "Required property 'timeout_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout_duration_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_duration_minutes EmrCluster#timeout_duration_minutes}.'''
        result = self._values.get("timeout_duration_minutes")
        assert result is not None, "Required property 'timeout_duration_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def block_duration_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#block_duration_minutes EmrCluster#block_duration_minutes}.'''
        result = self._values.get("block_duration_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterCoreInstanceFleetOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceFleetOutputReference",
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

    @jsii.member(jsii_name="putLaunchSpecifications")
    def put_launch_specifications(
        self,
        *,
        on_demand_specification: typing.Optional[typing.Sequence[EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification]] = None,
        spot_specification: typing.Optional[typing.Sequence[EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification]] = None,
    ) -> None:
        '''
        :param on_demand_specification: on_demand_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#on_demand_specification EmrCluster#on_demand_specification}
        :param spot_specification: spot_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#spot_specification EmrCluster#spot_specification}
        '''
        value = EmrClusterCoreInstanceFleetLaunchSpecifications(
            on_demand_specification=on_demand_specification,
            spot_specification=spot_specification,
        )

        return typing.cast(None, jsii.invoke(self, "putLaunchSpecifications", [value]))

    @jsii.member(jsii_name="resetInstanceTypeConfigs")
    def reset_instance_type_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypeConfigs", []))

    @jsii.member(jsii_name="resetLaunchSpecifications")
    def reset_launch_specifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchSpecifications", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTargetOnDemandCapacity")
    def reset_target_on_demand_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetOnDemandCapacity", []))

    @jsii.member(jsii_name="resetTargetSpotCapacity")
    def reset_target_spot_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetSpotCapacity", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchSpecifications")
    def launch_specifications(
        self,
    ) -> EmrClusterCoreInstanceFleetLaunchSpecificationsOutputReference:
        return typing.cast(EmrClusterCoreInstanceFleetLaunchSpecificationsOutputReference, jsii.get(self, "launchSpecifications"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeConfigsInput")
    def instance_type_configs_input(
        self,
    ) -> typing.Optional[typing.List[EmrClusterCoreInstanceFleetInstanceTypeConfigs]]:
        return typing.cast(typing.Optional[typing.List[EmrClusterCoreInstanceFleetInstanceTypeConfigs]], jsii.get(self, "instanceTypeConfigsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchSpecificationsInput")
    def launch_specifications_input(
        self,
    ) -> typing.Optional[EmrClusterCoreInstanceFleetLaunchSpecifications]:
        return typing.cast(typing.Optional[EmrClusterCoreInstanceFleetLaunchSpecifications], jsii.get(self, "launchSpecificationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOnDemandCapacityInput")
    def target_on_demand_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetOnDemandCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetSpotCapacityInput")
    def target_spot_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetSpotCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeConfigs")
    def instance_type_configs(
        self,
    ) -> typing.List[EmrClusterCoreInstanceFleetInstanceTypeConfigs]:
        return typing.cast(typing.List[EmrClusterCoreInstanceFleetInstanceTypeConfigs], jsii.get(self, "instanceTypeConfigs"))

    @instance_type_configs.setter
    def instance_type_configs(
        self,
        value: typing.List[EmrClusterCoreInstanceFleetInstanceTypeConfigs],
    ) -> None:
        jsii.set(self, "instanceTypeConfigs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetOnDemandCapacity"))

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "targetOnDemandCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetSpotCapacity")
    def target_spot_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetSpotCapacity"))

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "targetSpotCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterCoreInstanceFleet]:
        return typing.cast(typing.Optional[EmrClusterCoreInstanceFleet], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterCoreInstanceFleet],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceGroup",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "autoscaling_policy": "autoscalingPolicy",
        "bid_price": "bidPrice",
        "ebs_config": "ebsConfig",
        "instance_count": "instanceCount",
        "name": "name",
    },
)
class EmrClusterCoreInstanceGroup:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        autoscaling_policy: typing.Optional[builtins.str] = None,
        bid_price: typing.Optional[builtins.str] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrClusterCoreInstanceGroupEbsConfig"]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.
        :param autoscaling_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#autoscaling_policy EmrCluster#autoscaling_policy}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        :param instance_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_count EmrCluster#instance_count}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
        }
        if autoscaling_policy is not None:
            self._values["autoscaling_policy"] = autoscaling_policy
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if ebs_config is not None:
            self._values["ebs_config"] = ebs_config
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autoscaling_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#autoscaling_policy EmrCluster#autoscaling_policy}.'''
        result = self._values.get("autoscaling_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.'''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_config(
        self,
    ) -> typing.Optional[typing.List["EmrClusterCoreInstanceGroupEbsConfig"]]:
        '''ebs_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        '''
        result = self._values.get("ebs_config")
        return typing.cast(typing.Optional[typing.List["EmrClusterCoreInstanceGroupEbsConfig"]], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_count EmrCluster#instance_count}.'''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceGroupEbsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "size": "size",
        "type": "type",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EmrClusterCoreInstanceGroupEbsConfig:
    def __init__(
        self,
        *,
        size: jsii.Number,
        type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "type": type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterCoreInstanceGroupEbsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterCoreInstanceGroupOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterCoreInstanceGroupOutputReference",
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

    @jsii.member(jsii_name="resetAutoscalingPolicy")
    def reset_autoscaling_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingPolicy", []))

    @jsii.member(jsii_name="resetBidPrice")
    def reset_bid_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBidPrice", []))

    @jsii.member(jsii_name="resetEbsConfig")
    def reset_ebs_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsConfig", []))

    @jsii.member(jsii_name="resetInstanceCount")
    def reset_instance_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceCount", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingPolicyInput")
    def autoscaling_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoscalingPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPriceInput")
    def bid_price_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bidPriceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsConfigInput")
    def ebs_config_input(
        self,
    ) -> typing.Optional[typing.List[EmrClusterCoreInstanceGroupEbsConfig]]:
        return typing.cast(typing.Optional[typing.List[EmrClusterCoreInstanceGroupEbsConfig]], jsii.get(self, "ebsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCountInput")
    def instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingPolicy")
    def autoscaling_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoscalingPolicy"))

    @autoscaling_policy.setter
    def autoscaling_policy(self, value: builtins.str) -> None:
        jsii.set(self, "autoscalingPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPrice")
    def bid_price(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bidPrice"))

    @bid_price.setter
    def bid_price(self, value: builtins.str) -> None:
        jsii.set(self, "bidPrice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsConfig")
    def ebs_config(self) -> typing.List[EmrClusterCoreInstanceGroupEbsConfig]:
        return typing.cast(typing.List[EmrClusterCoreInstanceGroupEbsConfig], jsii.get(self, "ebsConfig"))

    @ebs_config.setter
    def ebs_config(
        self,
        value: typing.List[EmrClusterCoreInstanceGroupEbsConfig],
    ) -> None:
        jsii.set(self, "ebsConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceCount"))

    @instance_count.setter
    def instance_count(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterCoreInstanceGroup]:
        return typing.cast(typing.Optional[EmrClusterCoreInstanceGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterCoreInstanceGroup],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterEc2Attributes",
    jsii_struct_bases=[],
    name_mapping={
        "instance_profile": "instanceProfile",
        "additional_master_security_groups": "additionalMasterSecurityGroups",
        "additional_slave_security_groups": "additionalSlaveSecurityGroups",
        "emr_managed_master_security_group": "emrManagedMasterSecurityGroup",
        "emr_managed_slave_security_group": "emrManagedSlaveSecurityGroup",
        "key_name": "keyName",
        "service_access_security_group": "serviceAccessSecurityGroup",
        "subnet_id": "subnetId",
        "subnet_ids": "subnetIds",
    },
)
class EmrClusterEc2Attributes:
    def __init__(
        self,
        *,
        instance_profile: builtins.str,
        additional_master_security_groups: typing.Optional[builtins.str] = None,
        additional_slave_security_groups: typing.Optional[builtins.str] = None,
        emr_managed_master_security_group: typing.Optional[builtins.str] = None,
        emr_managed_slave_security_group: typing.Optional[builtins.str] = None,
        key_name: typing.Optional[builtins.str] = None,
        service_access_security_group: typing.Optional[builtins.str] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param instance_profile: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_profile EmrCluster#instance_profile}.
        :param additional_master_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_master_security_groups EmrCluster#additional_master_security_groups}.
        :param additional_slave_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_slave_security_groups EmrCluster#additional_slave_security_groups}.
        :param emr_managed_master_security_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#emr_managed_master_security_group EmrCluster#emr_managed_master_security_group}.
        :param emr_managed_slave_security_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#emr_managed_slave_security_group EmrCluster#emr_managed_slave_security_group}.
        :param key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#key_name EmrCluster#key_name}.
        :param service_access_security_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#service_access_security_group EmrCluster#service_access_security_group}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#subnet_id EmrCluster#subnet_id}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#subnet_ids EmrCluster#subnet_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_profile": instance_profile,
        }
        if additional_master_security_groups is not None:
            self._values["additional_master_security_groups"] = additional_master_security_groups
        if additional_slave_security_groups is not None:
            self._values["additional_slave_security_groups"] = additional_slave_security_groups
        if emr_managed_master_security_group is not None:
            self._values["emr_managed_master_security_group"] = emr_managed_master_security_group
        if emr_managed_slave_security_group is not None:
            self._values["emr_managed_slave_security_group"] = emr_managed_slave_security_group
        if key_name is not None:
            self._values["key_name"] = key_name
        if service_access_security_group is not None:
            self._values["service_access_security_group"] = service_access_security_group
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids

    @builtins.property
    def instance_profile(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_profile EmrCluster#instance_profile}.'''
        result = self._values.get("instance_profile")
        assert result is not None, "Required property 'instance_profile' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_master_security_groups(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_master_security_groups EmrCluster#additional_master_security_groups}.'''
        result = self._values.get("additional_master_security_groups")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_slave_security_groups(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#additional_slave_security_groups EmrCluster#additional_slave_security_groups}.'''
        result = self._values.get("additional_slave_security_groups")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def emr_managed_master_security_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#emr_managed_master_security_group EmrCluster#emr_managed_master_security_group}.'''
        result = self._values.get("emr_managed_master_security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def emr_managed_slave_security_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#emr_managed_slave_security_group EmrCluster#emr_managed_slave_security_group}.'''
        result = self._values.get("emr_managed_slave_security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#key_name EmrCluster#key_name}.'''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_access_security_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#service_access_security_group EmrCluster#service_access_security_group}.'''
        result = self._values.get("service_access_security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#subnet_id EmrCluster#subnet_id}.'''
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#subnet_ids EmrCluster#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterEc2Attributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterEc2AttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterEc2AttributesOutputReference",
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

    @jsii.member(jsii_name="resetAdditionalMasterSecurityGroups")
    def reset_additional_master_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalMasterSecurityGroups", []))

    @jsii.member(jsii_name="resetAdditionalSlaveSecurityGroups")
    def reset_additional_slave_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalSlaveSecurityGroups", []))

    @jsii.member(jsii_name="resetEmrManagedMasterSecurityGroup")
    def reset_emr_managed_master_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmrManagedMasterSecurityGroup", []))

    @jsii.member(jsii_name="resetEmrManagedSlaveSecurityGroup")
    def reset_emr_managed_slave_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmrManagedSlaveSecurityGroup", []))

    @jsii.member(jsii_name="resetKeyName")
    def reset_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyName", []))

    @jsii.member(jsii_name="resetServiceAccessSecurityGroup")
    def reset_service_access_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccessSecurityGroup", []))

    @jsii.member(jsii_name="resetSubnetId")
    def reset_subnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetId", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalMasterSecurityGroupsInput")
    def additional_master_security_groups_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "additionalMasterSecurityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalSlaveSecurityGroupsInput")
    def additional_slave_security_groups_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "additionalSlaveSecurityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emrManagedMasterSecurityGroupInput")
    def emr_managed_master_security_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emrManagedMasterSecurityGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emrManagedSlaveSecurityGroupInput")
    def emr_managed_slave_security_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emrManagedSlaveSecurityGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfileInput")
    def instance_profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyNameInput")
    def key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessSecurityGroupInput")
    def service_access_security_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccessSecurityGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalMasterSecurityGroups")
    def additional_master_security_groups(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "additionalMasterSecurityGroups"))

    @additional_master_security_groups.setter
    def additional_master_security_groups(self, value: builtins.str) -> None:
        jsii.set(self, "additionalMasterSecurityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalSlaveSecurityGroups")
    def additional_slave_security_groups(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "additionalSlaveSecurityGroups"))

    @additional_slave_security_groups.setter
    def additional_slave_security_groups(self, value: builtins.str) -> None:
        jsii.set(self, "additionalSlaveSecurityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emrManagedMasterSecurityGroup")
    def emr_managed_master_security_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emrManagedMasterSecurityGroup"))

    @emr_managed_master_security_group.setter
    def emr_managed_master_security_group(self, value: builtins.str) -> None:
        jsii.set(self, "emrManagedMasterSecurityGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emrManagedSlaveSecurityGroup")
    def emr_managed_slave_security_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emrManagedSlaveSecurityGroup"))

    @emr_managed_slave_security_group.setter
    def emr_managed_slave_security_group(self, value: builtins.str) -> None:
        jsii.set(self, "emrManagedSlaveSecurityGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfile"))

    @instance_profile.setter
    def instance_profile(self, value: builtins.str) -> None:
        jsii.set(self, "instanceProfile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyName")
    def key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyName"))

    @key_name.setter
    def key_name(self, value: builtins.str) -> None:
        jsii.set(self, "keyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessSecurityGroup")
    def service_access_security_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccessSecurityGroup"))

    @service_access_security_group.setter
    def service_access_security_group(self, value: builtins.str) -> None:
        jsii.set(self, "serviceAccessSecurityGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "subnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterEc2Attributes]:
        return typing.cast(typing.Optional[EmrClusterEc2Attributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[EmrClusterEc2Attributes]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterKerberosAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "kdc_admin_password": "kdcAdminPassword",
        "realm": "realm",
        "ad_domain_join_password": "adDomainJoinPassword",
        "ad_domain_join_user": "adDomainJoinUser",
        "cross_realm_trust_principal_password": "crossRealmTrustPrincipalPassword",
    },
)
class EmrClusterKerberosAttributes:
    def __init__(
        self,
        *,
        kdc_admin_password: builtins.str,
        realm: builtins.str,
        ad_domain_join_password: typing.Optional[builtins.str] = None,
        ad_domain_join_user: typing.Optional[builtins.str] = None,
        cross_realm_trust_principal_password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param kdc_admin_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#kdc_admin_password EmrCluster#kdc_admin_password}.
        :param realm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#realm EmrCluster#realm}.
        :param ad_domain_join_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ad_domain_join_password EmrCluster#ad_domain_join_password}.
        :param ad_domain_join_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ad_domain_join_user EmrCluster#ad_domain_join_user}.
        :param cross_realm_trust_principal_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#cross_realm_trust_principal_password EmrCluster#cross_realm_trust_principal_password}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "kdc_admin_password": kdc_admin_password,
            "realm": realm,
        }
        if ad_domain_join_password is not None:
            self._values["ad_domain_join_password"] = ad_domain_join_password
        if ad_domain_join_user is not None:
            self._values["ad_domain_join_user"] = ad_domain_join_user
        if cross_realm_trust_principal_password is not None:
            self._values["cross_realm_trust_principal_password"] = cross_realm_trust_principal_password

    @builtins.property
    def kdc_admin_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#kdc_admin_password EmrCluster#kdc_admin_password}.'''
        result = self._values.get("kdc_admin_password")
        assert result is not None, "Required property 'kdc_admin_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def realm(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#realm EmrCluster#realm}.'''
        result = self._values.get("realm")
        assert result is not None, "Required property 'realm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ad_domain_join_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ad_domain_join_password EmrCluster#ad_domain_join_password}.'''
        result = self._values.get("ad_domain_join_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ad_domain_join_user(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ad_domain_join_user EmrCluster#ad_domain_join_user}.'''
        result = self._values.get("ad_domain_join_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cross_realm_trust_principal_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#cross_realm_trust_principal_password EmrCluster#cross_realm_trust_principal_password}.'''
        result = self._values.get("cross_realm_trust_principal_password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterKerberosAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterKerberosAttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterKerberosAttributesOutputReference",
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

    @jsii.member(jsii_name="resetAdDomainJoinPassword")
    def reset_ad_domain_join_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdDomainJoinPassword", []))

    @jsii.member(jsii_name="resetAdDomainJoinUser")
    def reset_ad_domain_join_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdDomainJoinUser", []))

    @jsii.member(jsii_name="resetCrossRealmTrustPrincipalPassword")
    def reset_cross_realm_trust_principal_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrossRealmTrustPrincipalPassword", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adDomainJoinPasswordInput")
    def ad_domain_join_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adDomainJoinPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adDomainJoinUserInput")
    def ad_domain_join_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adDomainJoinUserInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRealmTrustPrincipalPasswordInput")
    def cross_realm_trust_principal_password_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crossRealmTrustPrincipalPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kdcAdminPasswordInput")
    def kdc_admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kdcAdminPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realmInput")
    def realm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adDomainJoinPassword")
    def ad_domain_join_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adDomainJoinPassword"))

    @ad_domain_join_password.setter
    def ad_domain_join_password(self, value: builtins.str) -> None:
        jsii.set(self, "adDomainJoinPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adDomainJoinUser")
    def ad_domain_join_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adDomainJoinUser"))

    @ad_domain_join_user.setter
    def ad_domain_join_user(self, value: builtins.str) -> None:
        jsii.set(self, "adDomainJoinUser", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRealmTrustPrincipalPassword")
    def cross_realm_trust_principal_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crossRealmTrustPrincipalPassword"))

    @cross_realm_trust_principal_password.setter
    def cross_realm_trust_principal_password(self, value: builtins.str) -> None:
        jsii.set(self, "crossRealmTrustPrincipalPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kdcAdminPassword")
    def kdc_admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kdcAdminPassword"))

    @kdc_admin_password.setter
    def kdc_admin_password(self, value: builtins.str) -> None:
        jsii.set(self, "kdcAdminPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realm")
    def realm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "realm"))

    @realm.setter
    def realm(self, value: builtins.str) -> None:
        jsii.set(self, "realm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterKerberosAttributes]:
        return typing.cast(typing.Optional[EmrClusterKerberosAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterKerberosAttributes],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleet",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type_configs": "instanceTypeConfigs",
        "launch_specifications": "launchSpecifications",
        "name": "name",
        "target_on_demand_capacity": "targetOnDemandCapacity",
        "target_spot_capacity": "targetSpotCapacity",
    },
)
class EmrClusterMasterInstanceFleet:
    def __init__(
        self,
        *,
        instance_type_configs: typing.Optional[typing.Sequence["EmrClusterMasterInstanceFleetInstanceTypeConfigs"]] = None,
        launch_specifications: typing.Optional["EmrClusterMasterInstanceFleetLaunchSpecifications"] = None,
        name: typing.Optional[builtins.str] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type_configs: instance_type_configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type_configs EmrCluster#instance_type_configs}
        :param launch_specifications: launch_specifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#launch_specifications EmrCluster#launch_specifications}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        :param target_on_demand_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_on_demand_capacity EmrCluster#target_on_demand_capacity}.
        :param target_spot_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_spot_capacity EmrCluster#target_spot_capacity}.
        '''
        if isinstance(launch_specifications, dict):
            launch_specifications = EmrClusterMasterInstanceFleetLaunchSpecifications(**launch_specifications)
        self._values: typing.Dict[str, typing.Any] = {}
        if instance_type_configs is not None:
            self._values["instance_type_configs"] = instance_type_configs
        if launch_specifications is not None:
            self._values["launch_specifications"] = launch_specifications
        if name is not None:
            self._values["name"] = name
        if target_on_demand_capacity is not None:
            self._values["target_on_demand_capacity"] = target_on_demand_capacity
        if target_spot_capacity is not None:
            self._values["target_spot_capacity"] = target_spot_capacity

    @builtins.property
    def instance_type_configs(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceFleetInstanceTypeConfigs"]]:
        '''instance_type_configs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type_configs EmrCluster#instance_type_configs}
        '''
        result = self._values.get("instance_type_configs")
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceFleetInstanceTypeConfigs"]], result)

    @builtins.property
    def launch_specifications(
        self,
    ) -> typing.Optional["EmrClusterMasterInstanceFleetLaunchSpecifications"]:
        '''launch_specifications block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#launch_specifications EmrCluster#launch_specifications}
        '''
        result = self._values.get("launch_specifications")
        return typing.cast(typing.Optional["EmrClusterMasterInstanceFleetLaunchSpecifications"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_on_demand_capacity EmrCluster#target_on_demand_capacity}.'''
        result = self._values.get("target_on_demand_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#target_spot_capacity EmrCluster#target_spot_capacity}.'''
        result = self._values.get("target_spot_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetInstanceTypeConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "bid_price": "bidPrice",
        "bid_price_as_percentage_of_on_demand_price": "bidPriceAsPercentageOfOnDemandPrice",
        "configurations": "configurations",
        "ebs_config": "ebsConfig",
        "weighted_capacity": "weightedCapacity",
    },
)
class EmrClusterMasterInstanceFleetInstanceTypeConfigs:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        bid_price: typing.Optional[builtins.str] = None,
        bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number] = None,
        configurations: typing.Optional[typing.Sequence["EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations"]] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig"]] = None,
        weighted_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.
        :param bid_price_as_percentage_of_on_demand_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price_as_percentage_of_on_demand_price EmrCluster#bid_price_as_percentage_of_on_demand_price}.
        :param configurations: configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        :param weighted_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#weighted_capacity EmrCluster#weighted_capacity}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
        }
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if bid_price_as_percentage_of_on_demand_price is not None:
            self._values["bid_price_as_percentage_of_on_demand_price"] = bid_price_as_percentage_of_on_demand_price
        if configurations is not None:
            self._values["configurations"] = configurations
        if ebs_config is not None:
            self._values["ebs_config"] = ebs_config
        if weighted_capacity is not None:
            self._values["weighted_capacity"] = weighted_capacity

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.'''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_price_as_percentage_of_on_demand_price(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price_as_percentage_of_on_demand_price EmrCluster#bid_price_as_percentage_of_on_demand_price}.'''
        result = self._values.get("bid_price_as_percentage_of_on_demand_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def configurations(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations"]]:
        '''configurations block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#configurations EmrCluster#configurations}
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations"]], result)

    @builtins.property
    def ebs_config(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig"]]:
        '''ebs_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        '''
        result = self._values.get("ebs_config")
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig"]], result)

    @builtins.property
    def weighted_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#weighted_capacity EmrCluster#weighted_capacity}.'''
        result = self._values.get("weighted_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleetInstanceTypeConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations",
    jsii_struct_bases=[],
    name_mapping={"classification": "classification", "properties": "properties"},
)
class EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations:
    def __init__(
        self,
        *,
        classification: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param classification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#classification EmrCluster#classification}.
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#properties EmrCluster#properties}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if classification is not None:
            self._values["classification"] = classification
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def classification(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#classification EmrCluster#classification}.'''
        result = self._values.get("classification")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#properties EmrCluster#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "size": "size",
        "type": "type",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig:
    def __init__(
        self,
        *,
        size: jsii.Number,
        type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "type": type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetLaunchSpecifications",
    jsii_struct_bases=[],
    name_mapping={
        "on_demand_specification": "onDemandSpecification",
        "spot_specification": "spotSpecification",
    },
)
class EmrClusterMasterInstanceFleetLaunchSpecifications:
    def __init__(
        self,
        *,
        on_demand_specification: typing.Optional[typing.Sequence["EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification"]] = None,
        spot_specification: typing.Optional[typing.Sequence["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"]] = None,
    ) -> None:
        '''
        :param on_demand_specification: on_demand_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#on_demand_specification EmrCluster#on_demand_specification}
        :param spot_specification: spot_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#spot_specification EmrCluster#spot_specification}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if on_demand_specification is not None:
            self._values["on_demand_specification"] = on_demand_specification
        if spot_specification is not None:
            self._values["spot_specification"] = spot_specification

    @builtins.property
    def on_demand_specification(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification"]]:
        '''on_demand_specification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#on_demand_specification EmrCluster#on_demand_specification}
        '''
        result = self._values.get("on_demand_specification")
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification"]], result)

    @builtins.property
    def spot_specification(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"]]:
        '''spot_specification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#spot_specification EmrCluster#spot_specification}
        '''
        result = self._values.get("spot_specification")
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleetLaunchSpecifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification",
    jsii_struct_bases=[],
    name_mapping={"allocation_strategy": "allocationStrategy"},
)
class EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification:
    def __init__(self, *, allocation_strategy: builtins.str) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterMasterInstanceFleetLaunchSpecificationsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetLaunchSpecificationsOutputReference",
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

    @jsii.member(jsii_name="resetOnDemandSpecification")
    def reset_on_demand_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemandSpecification", []))

    @jsii.member(jsii_name="resetSpotSpecification")
    def reset_spot_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotSpecification", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onDemandSpecificationInput")
    def on_demand_specification_input(
        self,
    ) -> typing.Optional[typing.List[EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification]]:
        return typing.cast(typing.Optional[typing.List[EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification]], jsii.get(self, "onDemandSpecificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotSpecificationInput")
    def spot_specification_input(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"]]:
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"]], jsii.get(self, "spotSpecificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onDemandSpecification")
    def on_demand_specification(
        self,
    ) -> typing.List[EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification]:
        return typing.cast(typing.List[EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification], jsii.get(self, "onDemandSpecification"))

    @on_demand_specification.setter
    def on_demand_specification(
        self,
        value: typing.List[EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification],
    ) -> None:
        jsii.set(self, "onDemandSpecification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotSpecification")
    def spot_specification(
        self,
    ) -> typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"]:
        return typing.cast(typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"], jsii.get(self, "spotSpecification"))

    @spot_specification.setter
    def spot_specification(
        self,
        value: typing.List["EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification"],
    ) -> None:
        jsii.set(self, "spotSpecification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[EmrClusterMasterInstanceFleetLaunchSpecifications]:
        return typing.cast(typing.Optional[EmrClusterMasterInstanceFleetLaunchSpecifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterMasterInstanceFleetLaunchSpecifications],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "timeout_action": "timeoutAction",
        "timeout_duration_minutes": "timeoutDurationMinutes",
        "block_duration_minutes": "blockDurationMinutes",
    },
)
class EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        timeout_action: builtins.str,
        timeout_duration_minutes: jsii.Number,
        block_duration_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.
        :param timeout_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_action EmrCluster#timeout_action}.
        :param timeout_duration_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_duration_minutes EmrCluster#timeout_duration_minutes}.
        :param block_duration_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#block_duration_minutes EmrCluster#block_duration_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
            "timeout_action": timeout_action,
            "timeout_duration_minutes": timeout_duration_minutes,
        }
        if block_duration_minutes is not None:
            self._values["block_duration_minutes"] = block_duration_minutes

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#allocation_strategy EmrCluster#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_action EmrCluster#timeout_action}.'''
        result = self._values.get("timeout_action")
        assert result is not None, "Required property 'timeout_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout_duration_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#timeout_duration_minutes EmrCluster#timeout_duration_minutes}.'''
        result = self._values.get("timeout_duration_minutes")
        assert result is not None, "Required property 'timeout_duration_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def block_duration_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#block_duration_minutes EmrCluster#block_duration_minutes}.'''
        result = self._values.get("block_duration_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterMasterInstanceFleetOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceFleetOutputReference",
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

    @jsii.member(jsii_name="putLaunchSpecifications")
    def put_launch_specifications(
        self,
        *,
        on_demand_specification: typing.Optional[typing.Sequence[EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification]] = None,
        spot_specification: typing.Optional[typing.Sequence[EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification]] = None,
    ) -> None:
        '''
        :param on_demand_specification: on_demand_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#on_demand_specification EmrCluster#on_demand_specification}
        :param spot_specification: spot_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#spot_specification EmrCluster#spot_specification}
        '''
        value = EmrClusterMasterInstanceFleetLaunchSpecifications(
            on_demand_specification=on_demand_specification,
            spot_specification=spot_specification,
        )

        return typing.cast(None, jsii.invoke(self, "putLaunchSpecifications", [value]))

    @jsii.member(jsii_name="resetInstanceTypeConfigs")
    def reset_instance_type_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypeConfigs", []))

    @jsii.member(jsii_name="resetLaunchSpecifications")
    def reset_launch_specifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchSpecifications", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTargetOnDemandCapacity")
    def reset_target_on_demand_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetOnDemandCapacity", []))

    @jsii.member(jsii_name="resetTargetSpotCapacity")
    def reset_target_spot_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetSpotCapacity", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchSpecifications")
    def launch_specifications(
        self,
    ) -> EmrClusterMasterInstanceFleetLaunchSpecificationsOutputReference:
        return typing.cast(EmrClusterMasterInstanceFleetLaunchSpecificationsOutputReference, jsii.get(self, "launchSpecifications"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeConfigsInput")
    def instance_type_configs_input(
        self,
    ) -> typing.Optional[typing.List[EmrClusterMasterInstanceFleetInstanceTypeConfigs]]:
        return typing.cast(typing.Optional[typing.List[EmrClusterMasterInstanceFleetInstanceTypeConfigs]], jsii.get(self, "instanceTypeConfigsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchSpecificationsInput")
    def launch_specifications_input(
        self,
    ) -> typing.Optional[EmrClusterMasterInstanceFleetLaunchSpecifications]:
        return typing.cast(typing.Optional[EmrClusterMasterInstanceFleetLaunchSpecifications], jsii.get(self, "launchSpecificationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOnDemandCapacityInput")
    def target_on_demand_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetOnDemandCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetSpotCapacityInput")
    def target_spot_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetSpotCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeConfigs")
    def instance_type_configs(
        self,
    ) -> typing.List[EmrClusterMasterInstanceFleetInstanceTypeConfigs]:
        return typing.cast(typing.List[EmrClusterMasterInstanceFleetInstanceTypeConfigs], jsii.get(self, "instanceTypeConfigs"))

    @instance_type_configs.setter
    def instance_type_configs(
        self,
        value: typing.List[EmrClusterMasterInstanceFleetInstanceTypeConfigs],
    ) -> None:
        jsii.set(self, "instanceTypeConfigs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetOnDemandCapacity"))

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "targetOnDemandCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetSpotCapacity")
    def target_spot_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetSpotCapacity"))

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "targetSpotCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterMasterInstanceFleet]:
        return typing.cast(typing.Optional[EmrClusterMasterInstanceFleet], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterMasterInstanceFleet],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceGroup",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "bid_price": "bidPrice",
        "ebs_config": "ebsConfig",
        "instance_count": "instanceCount",
        "name": "name",
    },
)
class EmrClusterMasterInstanceGroup:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        bid_price: typing.Optional[builtins.str] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrClusterMasterInstanceGroupEbsConfig"]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        :param instance_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_count EmrCluster#instance_count}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
        }
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if ebs_config is not None:
            self._values["ebs_config"] = ebs_config
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_type EmrCluster#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#bid_price EmrCluster#bid_price}.'''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_config(
        self,
    ) -> typing.Optional[typing.List["EmrClusterMasterInstanceGroupEbsConfig"]]:
        '''ebs_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#ebs_config EmrCluster#ebs_config}
        '''
        result = self._values.get("ebs_config")
        return typing.cast(typing.Optional[typing.List["EmrClusterMasterInstanceGroupEbsConfig"]], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#instance_count EmrCluster#instance_count}.'''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceGroupEbsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "size": "size",
        "type": "type",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EmrClusterMasterInstanceGroupEbsConfig:
    def __init__(
        self,
        *,
        size: jsii.Number,
        type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "type": type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#size EmrCluster#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#type EmrCluster#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#iops EmrCluster#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#volumes_per_instance EmrCluster#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterMasterInstanceGroupEbsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrClusterMasterInstanceGroupOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrClusterMasterInstanceGroupOutputReference",
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

    @jsii.member(jsii_name="resetBidPrice")
    def reset_bid_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBidPrice", []))

    @jsii.member(jsii_name="resetEbsConfig")
    def reset_ebs_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsConfig", []))

    @jsii.member(jsii_name="resetInstanceCount")
    def reset_instance_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceCount", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPriceInput")
    def bid_price_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bidPriceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsConfigInput")
    def ebs_config_input(
        self,
    ) -> typing.Optional[typing.List[EmrClusterMasterInstanceGroupEbsConfig]]:
        return typing.cast(typing.Optional[typing.List[EmrClusterMasterInstanceGroupEbsConfig]], jsii.get(self, "ebsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCountInput")
    def instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPrice")
    def bid_price(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bidPrice"))

    @bid_price.setter
    def bid_price(self, value: builtins.str) -> None:
        jsii.set(self, "bidPrice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsConfig")
    def ebs_config(self) -> typing.List[EmrClusterMasterInstanceGroupEbsConfig]:
        return typing.cast(typing.List[EmrClusterMasterInstanceGroupEbsConfig], jsii.get(self, "ebsConfig"))

    @ebs_config.setter
    def ebs_config(
        self,
        value: typing.List[EmrClusterMasterInstanceGroupEbsConfig],
    ) -> None:
        jsii.set(self, "ebsConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceCount"))

    @instance_count.setter
    def instance_count(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrClusterMasterInstanceGroup]:
        return typing.cast(typing.Optional[EmrClusterMasterInstanceGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrClusterMasterInstanceGroup],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterStep",
    jsii_struct_bases=[],
    name_mapping={
        "action_on_failure": "actionOnFailure",
        "hadoop_jar_step": "hadoopJarStep",
        "name": "name",
    },
)
class EmrClusterStep:
    def __init__(
        self,
        *,
        action_on_failure: typing.Optional[builtins.str] = None,
        hadoop_jar_step: typing.Optional[typing.Sequence["EmrClusterStepHadoopJarStep"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_on_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#action_on_failure EmrCluster#action_on_failure}.
        :param hadoop_jar_step: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#hadoop_jar_step EmrCluster#hadoop_jar_step}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if action_on_failure is not None:
            self._values["action_on_failure"] = action_on_failure
        if hadoop_jar_step is not None:
            self._values["hadoop_jar_step"] = hadoop_jar_step
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def action_on_failure(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#action_on_failure EmrCluster#action_on_failure}.'''
        result = self._values.get("action_on_failure")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hadoop_jar_step(
        self,
    ) -> typing.Optional[typing.List["EmrClusterStepHadoopJarStep"]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#hadoop_jar_step EmrCluster#hadoop_jar_step}.'''
        result = self._values.get("hadoop_jar_step")
        return typing.cast(typing.Optional[typing.List["EmrClusterStepHadoopJarStep"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#name EmrCluster#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrClusterStepHadoopJarStep",
    jsii_struct_bases=[],
    name_mapping={
        "args": "args",
        "jar": "jar",
        "main_class": "mainClass",
        "properties": "properties",
    },
)
class EmrClusterStepHadoopJarStep:
    def __init__(
        self,
        *,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        jar: typing.Optional[builtins.str] = None,
        main_class: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param args: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#args EmrCluster#args}.
        :param jar: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#jar EmrCluster#jar}.
        :param main_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#main_class EmrCluster#main_class}.
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#properties EmrCluster#properties}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if args is not None:
            self._values["args"] = args
        if jar is not None:
            self._values["jar"] = jar
        if main_class is not None:
            self._values["main_class"] = main_class
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#args EmrCluster#args}.'''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jar(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#jar EmrCluster#jar}.'''
        result = self._values.get("jar")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def main_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#main_class EmrCluster#main_class}.'''
        result = self._values.get("main_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_cluster#properties EmrCluster#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrClusterStepHadoopJarStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrInstanceFleet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet aws_emr_instance_fleet}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        instance_type_configs: typing.Optional[typing.Sequence["EmrInstanceFleetInstanceTypeConfigs"]] = None,
        launch_specifications: typing.Optional["EmrInstanceFleetLaunchSpecifications"] = None,
        name: typing.Optional[builtins.str] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet aws_emr_instance_fleet} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#cluster_id EmrInstanceFleet#cluster_id}.
        :param instance_type_configs: instance_type_configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#instance_type_configs EmrInstanceFleet#instance_type_configs}
        :param launch_specifications: launch_specifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#launch_specifications EmrInstanceFleet#launch_specifications}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#name EmrInstanceFleet#name}.
        :param target_on_demand_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#target_on_demand_capacity EmrInstanceFleet#target_on_demand_capacity}.
        :param target_spot_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#target_spot_capacity EmrInstanceFleet#target_spot_capacity}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrInstanceFleetConfig(
            cluster_id=cluster_id,
            instance_type_configs=instance_type_configs,
            launch_specifications=launch_specifications,
            name=name,
            target_on_demand_capacity=target_on_demand_capacity,
            target_spot_capacity=target_spot_capacity,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLaunchSpecifications")
    def put_launch_specifications(
        self,
        *,
        on_demand_specification: typing.Optional[typing.Sequence["EmrInstanceFleetLaunchSpecificationsOnDemandSpecification"]] = None,
        spot_specification: typing.Optional[typing.Sequence["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]] = None,
    ) -> None:
        '''
        :param on_demand_specification: on_demand_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#on_demand_specification EmrInstanceFleet#on_demand_specification}
        :param spot_specification: spot_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#spot_specification EmrInstanceFleet#spot_specification}
        '''
        value = EmrInstanceFleetLaunchSpecifications(
            on_demand_specification=on_demand_specification,
            spot_specification=spot_specification,
        )

        return typing.cast(None, jsii.invoke(self, "putLaunchSpecifications", [value]))

    @jsii.member(jsii_name="resetInstanceTypeConfigs")
    def reset_instance_type_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypeConfigs", []))

    @jsii.member(jsii_name="resetLaunchSpecifications")
    def reset_launch_specifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchSpecifications", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTargetOnDemandCapacity")
    def reset_target_on_demand_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetOnDemandCapacity", []))

    @jsii.member(jsii_name="resetTargetSpotCapacity")
    def reset_target_spot_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetSpotCapacity", []))

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
    @jsii.member(jsii_name="launchSpecifications")
    def launch_specifications(
        self,
    ) -> "EmrInstanceFleetLaunchSpecificationsOutputReference":
        return typing.cast("EmrInstanceFleetLaunchSpecificationsOutputReference", jsii.get(self, "launchSpecifications"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedOnDemandCapacity")
    def provisioned_on_demand_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedOnDemandCapacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedSpotCapacity")
    def provisioned_spot_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedSpotCapacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeConfigsInput")
    def instance_type_configs_input(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigs"]]:
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigs"]], jsii.get(self, "instanceTypeConfigsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchSpecificationsInput")
    def launch_specifications_input(
        self,
    ) -> typing.Optional["EmrInstanceFleetLaunchSpecifications"]:
        return typing.cast(typing.Optional["EmrInstanceFleetLaunchSpecifications"], jsii.get(self, "launchSpecificationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOnDemandCapacityInput")
    def target_on_demand_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetOnDemandCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetSpotCapacityInput")
    def target_spot_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetSpotCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        jsii.set(self, "clusterId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeConfigs")
    def instance_type_configs(
        self,
    ) -> typing.List["EmrInstanceFleetInstanceTypeConfigs"]:
        return typing.cast(typing.List["EmrInstanceFleetInstanceTypeConfigs"], jsii.get(self, "instanceTypeConfigs"))

    @instance_type_configs.setter
    def instance_type_configs(
        self,
        value: typing.List["EmrInstanceFleetInstanceTypeConfigs"],
    ) -> None:
        jsii.set(self, "instanceTypeConfigs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetOnDemandCapacity"))

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "targetOnDemandCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetSpotCapacity")
    def target_spot_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetSpotCapacity"))

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "targetSpotCapacity", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_id": "clusterId",
        "instance_type_configs": "instanceTypeConfigs",
        "launch_specifications": "launchSpecifications",
        "name": "name",
        "target_on_demand_capacity": "targetOnDemandCapacity",
        "target_spot_capacity": "targetSpotCapacity",
    },
)
class EmrInstanceFleetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_id: builtins.str,
        instance_type_configs: typing.Optional[typing.Sequence["EmrInstanceFleetInstanceTypeConfigs"]] = None,
        launch_specifications: typing.Optional["EmrInstanceFleetLaunchSpecifications"] = None,
        name: typing.Optional[builtins.str] = None,
        target_on_demand_capacity: typing.Optional[jsii.Number] = None,
        target_spot_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#cluster_id EmrInstanceFleet#cluster_id}.
        :param instance_type_configs: instance_type_configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#instance_type_configs EmrInstanceFleet#instance_type_configs}
        :param launch_specifications: launch_specifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#launch_specifications EmrInstanceFleet#launch_specifications}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#name EmrInstanceFleet#name}.
        :param target_on_demand_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#target_on_demand_capacity EmrInstanceFleet#target_on_demand_capacity}.
        :param target_spot_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#target_spot_capacity EmrInstanceFleet#target_spot_capacity}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(launch_specifications, dict):
            launch_specifications = EmrInstanceFleetLaunchSpecifications(**launch_specifications)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_id": cluster_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if instance_type_configs is not None:
            self._values["instance_type_configs"] = instance_type_configs
        if launch_specifications is not None:
            self._values["launch_specifications"] = launch_specifications
        if name is not None:
            self._values["name"] = name
        if target_on_demand_capacity is not None:
            self._values["target_on_demand_capacity"] = target_on_demand_capacity
        if target_spot_capacity is not None:
            self._values["target_spot_capacity"] = target_spot_capacity

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
    def cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#cluster_id EmrInstanceFleet#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type_configs(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigs"]]:
        '''instance_type_configs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#instance_type_configs EmrInstanceFleet#instance_type_configs}
        '''
        result = self._values.get("instance_type_configs")
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigs"]], result)

    @builtins.property
    def launch_specifications(
        self,
    ) -> typing.Optional["EmrInstanceFleetLaunchSpecifications"]:
        '''launch_specifications block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#launch_specifications EmrInstanceFleet#launch_specifications}
        '''
        result = self._values.get("launch_specifications")
        return typing.cast(typing.Optional["EmrInstanceFleetLaunchSpecifications"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#name EmrInstanceFleet#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#target_on_demand_capacity EmrInstanceFleet#target_on_demand_capacity}.'''
        result = self._values.get("target_on_demand_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#target_spot_capacity EmrInstanceFleet#target_spot_capacity}.'''
        result = self._values.get("target_spot_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetInstanceTypeConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "bid_price": "bidPrice",
        "bid_price_as_percentage_of_on_demand_price": "bidPriceAsPercentageOfOnDemandPrice",
        "configurations": "configurations",
        "ebs_config": "ebsConfig",
        "weighted_capacity": "weightedCapacity",
    },
)
class EmrInstanceFleetInstanceTypeConfigs:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        bid_price: typing.Optional[builtins.str] = None,
        bid_price_as_percentage_of_on_demand_price: typing.Optional[jsii.Number] = None,
        configurations: typing.Optional[typing.Sequence["EmrInstanceFleetInstanceTypeConfigsConfigurations"]] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrInstanceFleetInstanceTypeConfigsEbsConfig"]] = None,
        weighted_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#instance_type EmrInstanceFleet#instance_type}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#bid_price EmrInstanceFleet#bid_price}.
        :param bid_price_as_percentage_of_on_demand_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#bid_price_as_percentage_of_on_demand_price EmrInstanceFleet#bid_price_as_percentage_of_on_demand_price}.
        :param configurations: configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#configurations EmrInstanceFleet#configurations}
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#ebs_config EmrInstanceFleet#ebs_config}
        :param weighted_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#weighted_capacity EmrInstanceFleet#weighted_capacity}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
        }
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if bid_price_as_percentage_of_on_demand_price is not None:
            self._values["bid_price_as_percentage_of_on_demand_price"] = bid_price_as_percentage_of_on_demand_price
        if configurations is not None:
            self._values["configurations"] = configurations
        if ebs_config is not None:
            self._values["ebs_config"] = ebs_config
        if weighted_capacity is not None:
            self._values["weighted_capacity"] = weighted_capacity

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#instance_type EmrInstanceFleet#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#bid_price EmrInstanceFleet#bid_price}.'''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_price_as_percentage_of_on_demand_price(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#bid_price_as_percentage_of_on_demand_price EmrInstanceFleet#bid_price_as_percentage_of_on_demand_price}.'''
        result = self._values.get("bid_price_as_percentage_of_on_demand_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def configurations(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigsConfigurations"]]:
        '''configurations block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#configurations EmrInstanceFleet#configurations}
        '''
        result = self._values.get("configurations")
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigsConfigurations"]], result)

    @builtins.property
    def ebs_config(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigsEbsConfig"]]:
        '''ebs_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#ebs_config EmrInstanceFleet#ebs_config}
        '''
        result = self._values.get("ebs_config")
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetInstanceTypeConfigsEbsConfig"]], result)

    @builtins.property
    def weighted_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#weighted_capacity EmrInstanceFleet#weighted_capacity}.'''
        result = self._values.get("weighted_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetInstanceTypeConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetInstanceTypeConfigsConfigurations",
    jsii_struct_bases=[],
    name_mapping={"classification": "classification", "properties": "properties"},
)
class EmrInstanceFleetInstanceTypeConfigsConfigurations:
    def __init__(
        self,
        *,
        classification: typing.Optional[builtins.str] = None,
        properties: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param classification: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#classification EmrInstanceFleet#classification}.
        :param properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#properties EmrInstanceFleet#properties}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if classification is not None:
            self._values["classification"] = classification
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def classification(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#classification EmrInstanceFleet#classification}.'''
        result = self._values.get("classification")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#properties EmrInstanceFleet#properties}.'''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetInstanceTypeConfigsConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetInstanceTypeConfigsEbsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "size": "size",
        "type": "type",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EmrInstanceFleetInstanceTypeConfigsEbsConfig:
    def __init__(
        self,
        *,
        size: jsii.Number,
        type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#size EmrInstanceFleet#size}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#type EmrInstanceFleet#type}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#iops EmrInstanceFleet#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#volumes_per_instance EmrInstanceFleet#volumes_per_instance}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "type": type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#size EmrInstanceFleet#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#type EmrInstanceFleet#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#iops EmrInstanceFleet#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#volumes_per_instance EmrInstanceFleet#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetInstanceTypeConfigsEbsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetLaunchSpecifications",
    jsii_struct_bases=[],
    name_mapping={
        "on_demand_specification": "onDemandSpecification",
        "spot_specification": "spotSpecification",
    },
)
class EmrInstanceFleetLaunchSpecifications:
    def __init__(
        self,
        *,
        on_demand_specification: typing.Optional[typing.Sequence["EmrInstanceFleetLaunchSpecificationsOnDemandSpecification"]] = None,
        spot_specification: typing.Optional[typing.Sequence["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]] = None,
    ) -> None:
        '''
        :param on_demand_specification: on_demand_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#on_demand_specification EmrInstanceFleet#on_demand_specification}
        :param spot_specification: spot_specification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#spot_specification EmrInstanceFleet#spot_specification}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if on_demand_specification is not None:
            self._values["on_demand_specification"] = on_demand_specification
        if spot_specification is not None:
            self._values["spot_specification"] = spot_specification

    @builtins.property
    def on_demand_specification(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetLaunchSpecificationsOnDemandSpecification"]]:
        '''on_demand_specification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#on_demand_specification EmrInstanceFleet#on_demand_specification}
        '''
        result = self._values.get("on_demand_specification")
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetLaunchSpecificationsOnDemandSpecification"]], result)

    @builtins.property
    def spot_specification(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]]:
        '''spot_specification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#spot_specification EmrInstanceFleet#spot_specification}
        '''
        result = self._values.get("spot_specification")
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetLaunchSpecifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetLaunchSpecificationsOnDemandSpecification",
    jsii_struct_bases=[],
    name_mapping={"allocation_strategy": "allocationStrategy"},
)
class EmrInstanceFleetLaunchSpecificationsOnDemandSpecification:
    def __init__(self, *, allocation_strategy: builtins.str) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#allocation_strategy EmrInstanceFleet#allocation_strategy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#allocation_strategy EmrInstanceFleet#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetLaunchSpecificationsOnDemandSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrInstanceFleetLaunchSpecificationsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetLaunchSpecificationsOutputReference",
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

    @jsii.member(jsii_name="resetOnDemandSpecification")
    def reset_on_demand_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemandSpecification", []))

    @jsii.member(jsii_name="resetSpotSpecification")
    def reset_spot_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotSpecification", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onDemandSpecificationInput")
    def on_demand_specification_input(
        self,
    ) -> typing.Optional[typing.List[EmrInstanceFleetLaunchSpecificationsOnDemandSpecification]]:
        return typing.cast(typing.Optional[typing.List[EmrInstanceFleetLaunchSpecificationsOnDemandSpecification]], jsii.get(self, "onDemandSpecificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotSpecificationInput")
    def spot_specification_input(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]]:
        return typing.cast(typing.Optional[typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]], jsii.get(self, "spotSpecificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="onDemandSpecification")
    def on_demand_specification(
        self,
    ) -> typing.List[EmrInstanceFleetLaunchSpecificationsOnDemandSpecification]:
        return typing.cast(typing.List[EmrInstanceFleetLaunchSpecificationsOnDemandSpecification], jsii.get(self, "onDemandSpecification"))

    @on_demand_specification.setter
    def on_demand_specification(
        self,
        value: typing.List[EmrInstanceFleetLaunchSpecificationsOnDemandSpecification],
    ) -> None:
        jsii.set(self, "onDemandSpecification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotSpecification")
    def spot_specification(
        self,
    ) -> typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"]:
        return typing.cast(typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"], jsii.get(self, "spotSpecification"))

    @spot_specification.setter
    def spot_specification(
        self,
        value: typing.List["EmrInstanceFleetLaunchSpecificationsSpotSpecification"],
    ) -> None:
        jsii.set(self, "spotSpecification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EmrInstanceFleetLaunchSpecifications]:
        return typing.cast(typing.Optional[EmrInstanceFleetLaunchSpecifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EmrInstanceFleetLaunchSpecifications],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceFleetLaunchSpecificationsSpotSpecification",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "timeout_action": "timeoutAction",
        "timeout_duration_minutes": "timeoutDurationMinutes",
        "block_duration_minutes": "blockDurationMinutes",
    },
)
class EmrInstanceFleetLaunchSpecificationsSpotSpecification:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        timeout_action: builtins.str,
        timeout_duration_minutes: jsii.Number,
        block_duration_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#allocation_strategy EmrInstanceFleet#allocation_strategy}.
        :param timeout_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#timeout_action EmrInstanceFleet#timeout_action}.
        :param timeout_duration_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#timeout_duration_minutes EmrInstanceFleet#timeout_duration_minutes}.
        :param block_duration_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#block_duration_minutes EmrInstanceFleet#block_duration_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
            "timeout_action": timeout_action,
            "timeout_duration_minutes": timeout_duration_minutes,
        }
        if block_duration_minutes is not None:
            self._values["block_duration_minutes"] = block_duration_minutes

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#allocation_strategy EmrInstanceFleet#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#timeout_action EmrInstanceFleet#timeout_action}.'''
        result = self._values.get("timeout_action")
        assert result is not None, "Required property 'timeout_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout_duration_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#timeout_duration_minutes EmrInstanceFleet#timeout_duration_minutes}.'''
        result = self._values.get("timeout_duration_minutes")
        assert result is not None, "Required property 'timeout_duration_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def block_duration_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_fleet#block_duration_minutes EmrInstanceFleet#block_duration_minutes}.'''
        result = self._values.get("block_duration_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceFleetLaunchSpecificationsSpotSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrInstanceGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group aws_emr_instance_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        instance_type: builtins.str,
        autoscaling_policy: typing.Optional[builtins.str] = None,
        bid_price: typing.Optional[builtins.str] = None,
        configurations_json: typing.Optional[builtins.str] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrInstanceGroupEbsConfig"]] = None,
        ebs_optimized: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group aws_emr_instance_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#cluster_id EmrInstanceGroup#cluster_id}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#instance_type EmrInstanceGroup#instance_type}.
        :param autoscaling_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#autoscaling_policy EmrInstanceGroup#autoscaling_policy}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#bid_price EmrInstanceGroup#bid_price}.
        :param configurations_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#configurations_json EmrInstanceGroup#configurations_json}.
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#ebs_config EmrInstanceGroup#ebs_config}
        :param ebs_optimized: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#ebs_optimized EmrInstanceGroup#ebs_optimized}.
        :param instance_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#instance_count EmrInstanceGroup#instance_count}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#name EmrInstanceGroup#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrInstanceGroupConfig(
            cluster_id=cluster_id,
            instance_type=instance_type,
            autoscaling_policy=autoscaling_policy,
            bid_price=bid_price,
            configurations_json=configurations_json,
            ebs_config=ebs_config,
            ebs_optimized=ebs_optimized,
            instance_count=instance_count,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoscalingPolicy")
    def reset_autoscaling_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscalingPolicy", []))

    @jsii.member(jsii_name="resetBidPrice")
    def reset_bid_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBidPrice", []))

    @jsii.member(jsii_name="resetConfigurationsJson")
    def reset_configurations_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationsJson", []))

    @jsii.member(jsii_name="resetEbsConfig")
    def reset_ebs_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsConfig", []))

    @jsii.member(jsii_name="resetEbsOptimized")
    def reset_ebs_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsOptimized", []))

    @jsii.member(jsii_name="resetInstanceCount")
    def reset_instance_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceCount", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

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
    @jsii.member(jsii_name="runningInstanceCount")
    def running_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "runningInstanceCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingPolicyInput")
    def autoscaling_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoscalingPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPriceInput")
    def bid_price_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bidPriceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationsJsonInput")
    def configurations_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationsJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsConfigInput")
    def ebs_config_input(
        self,
    ) -> typing.Optional[typing.List["EmrInstanceGroupEbsConfig"]]:
        return typing.cast(typing.Optional[typing.List["EmrInstanceGroupEbsConfig"]], jsii.get(self, "ebsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsOptimizedInput")
    def ebs_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ebsOptimizedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCountInput")
    def instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingPolicy")
    def autoscaling_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoscalingPolicy"))

    @autoscaling_policy.setter
    def autoscaling_policy(self, value: builtins.str) -> None:
        jsii.set(self, "autoscalingPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPrice")
    def bid_price(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bidPrice"))

    @bid_price.setter
    def bid_price(self, value: builtins.str) -> None:
        jsii.set(self, "bidPrice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        jsii.set(self, "clusterId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationsJson")
    def configurations_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationsJson"))

    @configurations_json.setter
    def configurations_json(self, value: builtins.str) -> None:
        jsii.set(self, "configurationsJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsConfig")
    def ebs_config(self) -> typing.List["EmrInstanceGroupEbsConfig"]:
        return typing.cast(typing.List["EmrInstanceGroupEbsConfig"], jsii.get(self, "ebsConfig"))

    @ebs_config.setter
    def ebs_config(self, value: typing.List["EmrInstanceGroupEbsConfig"]) -> None:
        jsii.set(self, "ebsConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsOptimized")
    def ebs_optimized(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ebsOptimized"))

    @ebs_optimized.setter
    def ebs_optimized(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ebsOptimized", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceCount"))

    @instance_count.setter
    def instance_count(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_id": "clusterId",
        "instance_type": "instanceType",
        "autoscaling_policy": "autoscalingPolicy",
        "bid_price": "bidPrice",
        "configurations_json": "configurationsJson",
        "ebs_config": "ebsConfig",
        "ebs_optimized": "ebsOptimized",
        "instance_count": "instanceCount",
        "name": "name",
    },
)
class EmrInstanceGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_id: builtins.str,
        instance_type: builtins.str,
        autoscaling_policy: typing.Optional[builtins.str] = None,
        bid_price: typing.Optional[builtins.str] = None,
        configurations_json: typing.Optional[builtins.str] = None,
        ebs_config: typing.Optional[typing.Sequence["EmrInstanceGroupEbsConfig"]] = None,
        ebs_optimized: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_count: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#cluster_id EmrInstanceGroup#cluster_id}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#instance_type EmrInstanceGroup#instance_type}.
        :param autoscaling_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#autoscaling_policy EmrInstanceGroup#autoscaling_policy}.
        :param bid_price: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#bid_price EmrInstanceGroup#bid_price}.
        :param configurations_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#configurations_json EmrInstanceGroup#configurations_json}.
        :param ebs_config: ebs_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#ebs_config EmrInstanceGroup#ebs_config}
        :param ebs_optimized: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#ebs_optimized EmrInstanceGroup#ebs_optimized}.
        :param instance_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#instance_count EmrInstanceGroup#instance_count}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#name EmrInstanceGroup#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_id": cluster_id,
            "instance_type": instance_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if autoscaling_policy is not None:
            self._values["autoscaling_policy"] = autoscaling_policy
        if bid_price is not None:
            self._values["bid_price"] = bid_price
        if configurations_json is not None:
            self._values["configurations_json"] = configurations_json
        if ebs_config is not None:
            self._values["ebs_config"] = ebs_config
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if instance_count is not None:
            self._values["instance_count"] = instance_count
        if name is not None:
            self._values["name"] = name

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
    def cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#cluster_id EmrInstanceGroup#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#instance_type EmrInstanceGroup#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autoscaling_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#autoscaling_policy EmrInstanceGroup#autoscaling_policy}.'''
        result = self._values.get("autoscaling_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_price(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#bid_price EmrInstanceGroup#bid_price}.'''
        result = self._values.get("bid_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configurations_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#configurations_json EmrInstanceGroup#configurations_json}.'''
        result = self._values.get("configurations_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_config(self) -> typing.Optional[typing.List["EmrInstanceGroupEbsConfig"]]:
        '''ebs_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#ebs_config EmrInstanceGroup#ebs_config}
        '''
        result = self._values.get("ebs_config")
        return typing.cast(typing.Optional[typing.List["EmrInstanceGroupEbsConfig"]], result)

    @builtins.property
    def ebs_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#ebs_optimized EmrInstanceGroup#ebs_optimized}.'''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#instance_count EmrInstanceGroup#instance_count}.'''
        result = self._values.get("instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#name EmrInstanceGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrInstanceGroupEbsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "size": "size",
        "type": "type",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class EmrInstanceGroupEbsConfig:
    def __init__(
        self,
        *,
        size: jsii.Number,
        type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#size EmrInstanceGroup#size}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#type EmrInstanceGroup#type}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#iops EmrInstanceGroup#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#volumes_per_instance EmrInstanceGroup#volumes_per_instance}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "type": type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#size EmrInstanceGroup#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#type EmrInstanceGroup#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#iops EmrInstanceGroup#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_instance_group#volumes_per_instance EmrInstanceGroup#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrInstanceGroupEbsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrManagedScalingPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrManagedScalingPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy aws_emr_managed_scaling_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        compute_limits: typing.Sequence["EmrManagedScalingPolicyComputeLimits"],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy aws_emr_managed_scaling_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#cluster_id EmrManagedScalingPolicy#cluster_id}.
        :param compute_limits: compute_limits block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#compute_limits EmrManagedScalingPolicy#compute_limits}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrManagedScalingPolicyConfig(
            cluster_id=cluster_id,
            compute_limits=compute_limits,
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
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeLimitsInput")
    def compute_limits_input(
        self,
    ) -> typing.Optional[typing.List["EmrManagedScalingPolicyComputeLimits"]]:
        return typing.cast(typing.Optional[typing.List["EmrManagedScalingPolicyComputeLimits"]], jsii.get(self, "computeLimitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        jsii.set(self, "clusterId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeLimits")
    def compute_limits(self) -> typing.List["EmrManagedScalingPolicyComputeLimits"]:
        return typing.cast(typing.List["EmrManagedScalingPolicyComputeLimits"], jsii.get(self, "computeLimits"))

    @compute_limits.setter
    def compute_limits(
        self,
        value: typing.List["EmrManagedScalingPolicyComputeLimits"],
    ) -> None:
        jsii.set(self, "computeLimits", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrManagedScalingPolicyComputeLimits",
    jsii_struct_bases=[],
    name_mapping={
        "maximum_capacity_units": "maximumCapacityUnits",
        "minimum_capacity_units": "minimumCapacityUnits",
        "unit_type": "unitType",
        "maximum_core_capacity_units": "maximumCoreCapacityUnits",
        "maximum_ondemand_capacity_units": "maximumOndemandCapacityUnits",
    },
)
class EmrManagedScalingPolicyComputeLimits:
    def __init__(
        self,
        *,
        maximum_capacity_units: jsii.Number,
        minimum_capacity_units: jsii.Number,
        unit_type: builtins.str,
        maximum_core_capacity_units: typing.Optional[jsii.Number] = None,
        maximum_ondemand_capacity_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param maximum_capacity_units: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#maximum_capacity_units EmrManagedScalingPolicy#maximum_capacity_units}.
        :param minimum_capacity_units: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#minimum_capacity_units EmrManagedScalingPolicy#minimum_capacity_units}.
        :param unit_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#unit_type EmrManagedScalingPolicy#unit_type}.
        :param maximum_core_capacity_units: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#maximum_core_capacity_units EmrManagedScalingPolicy#maximum_core_capacity_units}.
        :param maximum_ondemand_capacity_units: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#maximum_ondemand_capacity_units EmrManagedScalingPolicy#maximum_ondemand_capacity_units}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "maximum_capacity_units": maximum_capacity_units,
            "minimum_capacity_units": minimum_capacity_units,
            "unit_type": unit_type,
        }
        if maximum_core_capacity_units is not None:
            self._values["maximum_core_capacity_units"] = maximum_core_capacity_units
        if maximum_ondemand_capacity_units is not None:
            self._values["maximum_ondemand_capacity_units"] = maximum_ondemand_capacity_units

    @builtins.property
    def maximum_capacity_units(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#maximum_capacity_units EmrManagedScalingPolicy#maximum_capacity_units}.'''
        result = self._values.get("maximum_capacity_units")
        assert result is not None, "Required property 'maximum_capacity_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def minimum_capacity_units(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#minimum_capacity_units EmrManagedScalingPolicy#minimum_capacity_units}.'''
        result = self._values.get("minimum_capacity_units")
        assert result is not None, "Required property 'minimum_capacity_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#unit_type EmrManagedScalingPolicy#unit_type}.'''
        result = self._values.get("unit_type")
        assert result is not None, "Required property 'unit_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def maximum_core_capacity_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#maximum_core_capacity_units EmrManagedScalingPolicy#maximum_core_capacity_units}.'''
        result = self._values.get("maximum_core_capacity_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum_ondemand_capacity_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#maximum_ondemand_capacity_units EmrManagedScalingPolicy#maximum_ondemand_capacity_units}.'''
        result = self._values.get("maximum_ondemand_capacity_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrManagedScalingPolicyComputeLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrManagedScalingPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_id": "clusterId",
        "compute_limits": "computeLimits",
    },
)
class EmrManagedScalingPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_id: builtins.str,
        compute_limits: typing.Sequence[EmrManagedScalingPolicyComputeLimits],
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#cluster_id EmrManagedScalingPolicy#cluster_id}.
        :param compute_limits: compute_limits block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#compute_limits EmrManagedScalingPolicy#compute_limits}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_id": cluster_id,
            "compute_limits": compute_limits,
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
    def cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#cluster_id EmrManagedScalingPolicy#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_limits(self) -> typing.List[EmrManagedScalingPolicyComputeLimits]:
        '''compute_limits block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_managed_scaling_policy#compute_limits EmrManagedScalingPolicy#compute_limits}
        '''
        result = self._values.get("compute_limits")
        assert result is not None, "Required property 'compute_limits' is missing"
        return typing.cast(typing.List[EmrManagedScalingPolicyComputeLimits], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrManagedScalingPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrSecurityConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrSecurityConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration aws_emr_security_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        configuration: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration aws_emr_security_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#configuration EmrSecurityConfiguration#configuration}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#name EmrSecurityConfiguration#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#name_prefix EmrSecurityConfiguration#name_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrSecurityConfigurationConfig(
            configuration=configuration,
            name=name,
            name_prefix=name_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: builtins.str) -> None:
        jsii.set(self, "configuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrSecurityConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "configuration": "configuration",
        "name": "name",
        "name_prefix": "namePrefix",
    },
)
class EmrSecurityConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        configuration: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#configuration EmrSecurityConfiguration#configuration}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#name EmrSecurityConfiguration#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#name_prefix EmrSecurityConfiguration#name_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "configuration": configuration,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix

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
    def configuration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#configuration EmrSecurityConfiguration#configuration}.'''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#name EmrSecurityConfiguration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_security_configuration#name_prefix EmrSecurityConfiguration#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrSecurityConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrStudio(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrStudio",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_studio aws_emr_studio}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        auth_mode: builtins.str,
        default_s3_location: builtins.str,
        engine_security_group_id: builtins.str,
        name: builtins.str,
        service_role: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
        workspace_security_group_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        idp_auth_url: typing.Optional[builtins.str] = None,
        idp_relay_state_parameter_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_role: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_studio aws_emr_studio} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param auth_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#auth_mode EmrStudio#auth_mode}.
        :param default_s3_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#default_s3_location EmrStudio#default_s3_location}.
        :param engine_security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#engine_security_group_id EmrStudio#engine_security_group_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#name EmrStudio#name}.
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#service_role EmrStudio#service_role}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#subnet_ids EmrStudio#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#vpc_id EmrStudio#vpc_id}.
        :param workspace_security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#workspace_security_group_id EmrStudio#workspace_security_group_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#description EmrStudio#description}.
        :param idp_auth_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#idp_auth_url EmrStudio#idp_auth_url}.
        :param idp_relay_state_parameter_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#idp_relay_state_parameter_name EmrStudio#idp_relay_state_parameter_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#tags EmrStudio#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#tags_all EmrStudio#tags_all}.
        :param user_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#user_role EmrStudio#user_role}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrStudioConfig(
            auth_mode=auth_mode,
            default_s3_location=default_s3_location,
            engine_security_group_id=engine_security_group_id,
            name=name,
            service_role=service_role,
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
            workspace_security_group_id=workspace_security_group_id,
            description=description,
            idp_auth_url=idp_auth_url,
            idp_relay_state_parameter_name=idp_relay_state_parameter_name,
            tags=tags,
            tags_all=tags_all,
            user_role=user_role,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetIdpAuthUrl")
    def reset_idp_auth_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpAuthUrl", []))

    @jsii.member(jsii_name="resetIdpRelayStateParameterName")
    def reset_idp_relay_state_parameter_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpRelayStateParameterName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUserRole")
    def reset_user_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserRole", []))

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
    @jsii.member(jsii_name="authModeInput")
    def auth_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultS3LocationInput")
    def default_s3_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultS3LocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineSecurityGroupIdInput")
    def engine_security_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineSecurityGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpAuthUrlInput")
    def idp_auth_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpAuthUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpRelayStateParameterNameInput")
    def idp_relay_state_parameter_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpRelayStateParameterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleInput")
    def service_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

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
    @jsii.member(jsii_name="userRoleInput")
    def user_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceSecurityGroupIdInput")
    def workspace_security_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceSecurityGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authMode")
    def auth_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMode"))

    @auth_mode.setter
    def auth_mode(self, value: builtins.str) -> None:
        jsii.set(self, "authMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultS3Location")
    def default_s3_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultS3Location"))

    @default_s3_location.setter
    def default_s3_location(self, value: builtins.str) -> None:
        jsii.set(self, "defaultS3Location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineSecurityGroupId")
    def engine_security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineSecurityGroupId"))

    @engine_security_group_id.setter
    def engine_security_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "engineSecurityGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpAuthUrl")
    def idp_auth_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpAuthUrl"))

    @idp_auth_url.setter
    def idp_auth_url(self, value: builtins.str) -> None:
        jsii.set(self, "idpAuthUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idpRelayStateParameterName")
    def idp_relay_state_parameter_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpRelayStateParameterName"))

    @idp_relay_state_parameter_name.setter
    def idp_relay_state_parameter_name(self, value: builtins.str) -> None:
        jsii.set(self, "idpRelayStateParameterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        jsii.set(self, "serviceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

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
    @jsii.member(jsii_name="userRole")
    def user_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userRole"))

    @user_role.setter
    def user_role(self, value: builtins.str) -> None:
        jsii.set(self, "userRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceSecurityGroupId")
    def workspace_security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceSecurityGroupId"))

    @workspace_security_group_id.setter
    def workspace_security_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "workspaceSecurityGroupId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrStudioConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "auth_mode": "authMode",
        "default_s3_location": "defaultS3Location",
        "engine_security_group_id": "engineSecurityGroupId",
        "name": "name",
        "service_role": "serviceRole",
        "subnet_ids": "subnetIds",
        "vpc_id": "vpcId",
        "workspace_security_group_id": "workspaceSecurityGroupId",
        "description": "description",
        "idp_auth_url": "idpAuthUrl",
        "idp_relay_state_parameter_name": "idpRelayStateParameterName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "user_role": "userRole",
    },
)
class EmrStudioConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        auth_mode: builtins.str,
        default_s3_location: builtins.str,
        engine_security_group_id: builtins.str,
        name: builtins.str,
        service_role: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
        workspace_security_group_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        idp_auth_url: typing.Optional[builtins.str] = None,
        idp_relay_state_parameter_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_role: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param auth_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#auth_mode EmrStudio#auth_mode}.
        :param default_s3_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#default_s3_location EmrStudio#default_s3_location}.
        :param engine_security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#engine_security_group_id EmrStudio#engine_security_group_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#name EmrStudio#name}.
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#service_role EmrStudio#service_role}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#subnet_ids EmrStudio#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#vpc_id EmrStudio#vpc_id}.
        :param workspace_security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#workspace_security_group_id EmrStudio#workspace_security_group_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#description EmrStudio#description}.
        :param idp_auth_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#idp_auth_url EmrStudio#idp_auth_url}.
        :param idp_relay_state_parameter_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#idp_relay_state_parameter_name EmrStudio#idp_relay_state_parameter_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#tags EmrStudio#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#tags_all EmrStudio#tags_all}.
        :param user_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#user_role EmrStudio#user_role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "auth_mode": auth_mode,
            "default_s3_location": default_s3_location,
            "engine_security_group_id": engine_security_group_id,
            "name": name,
            "service_role": service_role,
            "subnet_ids": subnet_ids,
            "vpc_id": vpc_id,
            "workspace_security_group_id": workspace_security_group_id,
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
        if idp_auth_url is not None:
            self._values["idp_auth_url"] = idp_auth_url
        if idp_relay_state_parameter_name is not None:
            self._values["idp_relay_state_parameter_name"] = idp_relay_state_parameter_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if user_role is not None:
            self._values["user_role"] = user_role

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
    def auth_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#auth_mode EmrStudio#auth_mode}.'''
        result = self._values.get("auth_mode")
        assert result is not None, "Required property 'auth_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_s3_location(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#default_s3_location EmrStudio#default_s3_location}.'''
        result = self._values.get("default_s3_location")
        assert result is not None, "Required property 'default_s3_location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def engine_security_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#engine_security_group_id EmrStudio#engine_security_group_id}.'''
        result = self._values.get("engine_security_group_id")
        assert result is not None, "Required property 'engine_security_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#name EmrStudio#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#service_role EmrStudio#service_role}.'''
        result = self._values.get("service_role")
        assert result is not None, "Required property 'service_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#subnet_ids EmrStudio#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#vpc_id EmrStudio#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_security_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#workspace_security_group_id EmrStudio#workspace_security_group_id}.'''
        result = self._values.get("workspace_security_group_id")
        assert result is not None, "Required property 'workspace_security_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#description EmrStudio#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_auth_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#idp_auth_url EmrStudio#idp_auth_url}.'''
        result = self._values.get("idp_auth_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_relay_state_parameter_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#idp_relay_state_parameter_name EmrStudio#idp_relay_state_parameter_name}.'''
        result = self._values.get("idp_relay_state_parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#tags EmrStudio#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#tags_all EmrStudio#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def user_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio#user_role EmrStudio#user_role}.'''
        result = self._values.get("user_role")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrStudioConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrStudioSessionMapping(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.emr.EmrStudioSessionMapping",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping aws_emr_studio_session_mapping}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity_type: builtins.str,
        session_policy_arn: builtins.str,
        studio_id: builtins.str,
        identity_id: typing.Optional[builtins.str] = None,
        identity_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping aws_emr_studio_session_mapping} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_type EmrStudioSessionMapping#identity_type}.
        :param session_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#session_policy_arn EmrStudioSessionMapping#session_policy_arn}.
        :param studio_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#studio_id EmrStudioSessionMapping#studio_id}.
        :param identity_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_id EmrStudioSessionMapping#identity_id}.
        :param identity_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_name EmrStudioSessionMapping#identity_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EmrStudioSessionMappingConfig(
            identity_type=identity_type,
            session_policy_arn=session_policy_arn,
            studio_id=studio_id,
            identity_id=identity_id,
            identity_name=identity_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetIdentityId")
    def reset_identity_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityId", []))

    @jsii.member(jsii_name="resetIdentityName")
    def reset_identity_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityName", []))

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
    @jsii.member(jsii_name="identityIdInput")
    def identity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityNameInput")
    def identity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityTypeInput")
    def identity_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionPolicyArnInput")
    def session_policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionPolicyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="studioIdInput")
    def studio_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "studioIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityId")
    def identity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityId"))

    @identity_id.setter
    def identity_id(self, value: builtins.str) -> None:
        jsii.set(self, "identityId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityName")
    def identity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityName"))

    @identity_name.setter
    def identity_name(self, value: builtins.str) -> None:
        jsii.set(self, "identityName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityType")
    def identity_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityType"))

    @identity_type.setter
    def identity_type(self, value: builtins.str) -> None:
        jsii.set(self, "identityType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionPolicyArn")
    def session_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionPolicyArn"))

    @session_policy_arn.setter
    def session_policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sessionPolicyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="studioId")
    def studio_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "studioId"))

    @studio_id.setter
    def studio_id(self, value: builtins.str) -> None:
        jsii.set(self, "studioId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.emr.EmrStudioSessionMappingConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity_type": "identityType",
        "session_policy_arn": "sessionPolicyArn",
        "studio_id": "studioId",
        "identity_id": "identityId",
        "identity_name": "identityName",
    },
)
class EmrStudioSessionMappingConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity_type: builtins.str,
        session_policy_arn: builtins.str,
        studio_id: builtins.str,
        identity_id: typing.Optional[builtins.str] = None,
        identity_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Elastic MapReduce.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_type EmrStudioSessionMapping#identity_type}.
        :param session_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#session_policy_arn EmrStudioSessionMapping#session_policy_arn}.
        :param studio_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#studio_id EmrStudioSessionMapping#studio_id}.
        :param identity_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_id EmrStudioSessionMapping#identity_id}.
        :param identity_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_name EmrStudioSessionMapping#identity_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identity_type": identity_type,
            "session_policy_arn": session_policy_arn,
            "studio_id": studio_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if identity_id is not None:
            self._values["identity_id"] = identity_id
        if identity_name is not None:
            self._values["identity_name"] = identity_name

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
    def identity_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_type EmrStudioSessionMapping#identity_type}.'''
        result = self._values.get("identity_type")
        assert result is not None, "Required property 'identity_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def session_policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#session_policy_arn EmrStudioSessionMapping#session_policy_arn}.'''
        result = self._values.get("session_policy_arn")
        assert result is not None, "Required property 'session_policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def studio_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#studio_id EmrStudioSessionMapping#studio_id}.'''
        result = self._values.get("studio_id")
        assert result is not None, "Required property 'studio_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def identity_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_id EmrStudioSessionMapping#identity_id}.'''
        result = self._values.get("identity_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/emr_studio_session_mapping#identity_name EmrStudioSessionMapping#identity_name}.'''
        result = self._values.get("identity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrStudioSessionMappingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsEmrReleaseLabels",
    "DataAwsEmrReleaseLabelsConfig",
    "DataAwsEmrReleaseLabelsFilters",
    "DataAwsEmrReleaseLabelsFiltersOutputReference",
    "EmrCluster",
    "EmrClusterAutoTerminationPolicy",
    "EmrClusterAutoTerminationPolicyOutputReference",
    "EmrClusterBootstrapAction",
    "EmrClusterConfig",
    "EmrClusterCoreInstanceFleet",
    "EmrClusterCoreInstanceFleetInstanceTypeConfigs",
    "EmrClusterCoreInstanceFleetInstanceTypeConfigsConfigurations",
    "EmrClusterCoreInstanceFleetInstanceTypeConfigsEbsConfig",
    "EmrClusterCoreInstanceFleetLaunchSpecifications",
    "EmrClusterCoreInstanceFleetLaunchSpecificationsOnDemandSpecification",
    "EmrClusterCoreInstanceFleetLaunchSpecificationsOutputReference",
    "EmrClusterCoreInstanceFleetLaunchSpecificationsSpotSpecification",
    "EmrClusterCoreInstanceFleetOutputReference",
    "EmrClusterCoreInstanceGroup",
    "EmrClusterCoreInstanceGroupEbsConfig",
    "EmrClusterCoreInstanceGroupOutputReference",
    "EmrClusterEc2Attributes",
    "EmrClusterEc2AttributesOutputReference",
    "EmrClusterKerberosAttributes",
    "EmrClusterKerberosAttributesOutputReference",
    "EmrClusterMasterInstanceFleet",
    "EmrClusterMasterInstanceFleetInstanceTypeConfigs",
    "EmrClusterMasterInstanceFleetInstanceTypeConfigsConfigurations",
    "EmrClusterMasterInstanceFleetInstanceTypeConfigsEbsConfig",
    "EmrClusterMasterInstanceFleetLaunchSpecifications",
    "EmrClusterMasterInstanceFleetLaunchSpecificationsOnDemandSpecification",
    "EmrClusterMasterInstanceFleetLaunchSpecificationsOutputReference",
    "EmrClusterMasterInstanceFleetLaunchSpecificationsSpotSpecification",
    "EmrClusterMasterInstanceFleetOutputReference",
    "EmrClusterMasterInstanceGroup",
    "EmrClusterMasterInstanceGroupEbsConfig",
    "EmrClusterMasterInstanceGroupOutputReference",
    "EmrClusterStep",
    "EmrClusterStepHadoopJarStep",
    "EmrInstanceFleet",
    "EmrInstanceFleetConfig",
    "EmrInstanceFleetInstanceTypeConfigs",
    "EmrInstanceFleetInstanceTypeConfigsConfigurations",
    "EmrInstanceFleetInstanceTypeConfigsEbsConfig",
    "EmrInstanceFleetLaunchSpecifications",
    "EmrInstanceFleetLaunchSpecificationsOnDemandSpecification",
    "EmrInstanceFleetLaunchSpecificationsOutputReference",
    "EmrInstanceFleetLaunchSpecificationsSpotSpecification",
    "EmrInstanceGroup",
    "EmrInstanceGroupConfig",
    "EmrInstanceGroupEbsConfig",
    "EmrManagedScalingPolicy",
    "EmrManagedScalingPolicyComputeLimits",
    "EmrManagedScalingPolicyConfig",
    "EmrSecurityConfiguration",
    "EmrSecurityConfigurationConfig",
    "EmrStudio",
    "EmrStudioConfig",
    "EmrStudioSessionMapping",
    "EmrStudioSessionMappingConfig",
]

publication.publish()
