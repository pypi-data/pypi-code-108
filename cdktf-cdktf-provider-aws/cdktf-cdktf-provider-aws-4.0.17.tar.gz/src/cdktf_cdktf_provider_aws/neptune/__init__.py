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


class DataAwsNeptuneEngineVersion(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.DataAwsNeptuneEngineVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version aws_neptune_engine_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        engine: typing.Optional[builtins.str] = None,
        parameter_group_family: typing.Optional[builtins.str] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version aws_neptune_engine_version} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#engine DataAwsNeptuneEngineVersion#engine}.
        :param parameter_group_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#parameter_group_family DataAwsNeptuneEngineVersion#parameter_group_family}.
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#preferred_versions DataAwsNeptuneEngineVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#version DataAwsNeptuneEngineVersion#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsNeptuneEngineVersionConfig(
            engine=engine,
            parameter_group_family=parameter_group_family,
            preferred_versions=preferred_versions,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetParameterGroupFamily")
    def reset_parameter_group_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterGroupFamily", []))

    @jsii.member(jsii_name="resetPreferredVersions")
    def reset_preferred_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredVersions", []))

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
    @jsii.member(jsii_name="engineDescription")
    def engine_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineDescription"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exportableLogTypes")
    def exportable_log_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exportableLogTypes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedTimezones")
    def supported_timezones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedTimezones"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsLogExportsToCloudwatch")
    def supports_log_exports_to_cloudwatch(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsLogExportsToCloudwatch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsReadReplica")
    def supports_read_replica(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsReadReplica"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validUpgradeTargets")
    def valid_upgrade_targets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validUpgradeTargets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionDescription")
    def version_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionDescription"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupFamilyInput")
    def parameter_group_family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterGroupFamilyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredVersionsInput")
    def preferred_versions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupFamily")
    def parameter_group_family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupFamily"))

    @parameter_group_family.setter
    def parameter_group_family(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupFamily", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredVersions")
    def preferred_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredVersions"))

    @preferred_versions.setter
    def preferred_versions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.DataAwsNeptuneEngineVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "engine": "engine",
        "parameter_group_family": "parameterGroupFamily",
        "preferred_versions": "preferredVersions",
        "version": "version",
    },
)
class DataAwsNeptuneEngineVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        engine: typing.Optional[builtins.str] = None,
        parameter_group_family: typing.Optional[builtins.str] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#engine DataAwsNeptuneEngineVersion#engine}.
        :param parameter_group_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#parameter_group_family DataAwsNeptuneEngineVersion#parameter_group_family}.
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#preferred_versions DataAwsNeptuneEngineVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#version DataAwsNeptuneEngineVersion#version}.
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
        if engine is not None:
            self._values["engine"] = engine
        if parameter_group_family is not None:
            self._values["parameter_group_family"] = parameter_group_family
        if preferred_versions is not None:
            self._values["preferred_versions"] = preferred_versions
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
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#engine DataAwsNeptuneEngineVersion#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_group_family(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#parameter_group_family DataAwsNeptuneEngineVersion#parameter_group_family}.'''
        result = self._values.get("parameter_group_family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#preferred_versions DataAwsNeptuneEngineVersion#preferred_versions}.'''
        result = self._values.get("preferred_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_engine_version#version DataAwsNeptuneEngineVersion#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNeptuneEngineVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsNeptuneOrderableDbInstance(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.DataAwsNeptuneOrderableDbInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance aws_neptune_orderable_db_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        instance_class: typing.Optional[builtins.str] = None,
        license_model: typing.Optional[builtins.str] = None,
        preferred_instance_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance aws_neptune_orderable_db_instance} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#engine DataAwsNeptuneOrderableDbInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#engine_version DataAwsNeptuneOrderableDbInstance#engine_version}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#instance_class DataAwsNeptuneOrderableDbInstance#instance_class}.
        :param license_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#license_model DataAwsNeptuneOrderableDbInstance#license_model}.
        :param preferred_instance_classes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#preferred_instance_classes DataAwsNeptuneOrderableDbInstance#preferred_instance_classes}.
        :param vpc: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#vpc DataAwsNeptuneOrderableDbInstance#vpc}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsNeptuneOrderableDbInstanceConfig(
            engine=engine,
            engine_version=engine_version,
            instance_class=instance_class,
            license_model=license_model,
            preferred_instance_classes=preferred_instance_classes,
            vpc=vpc,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetInstanceClass")
    def reset_instance_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceClass", []))

    @jsii.member(jsii_name="resetLicenseModel")
    def reset_license_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseModel", []))

    @jsii.member(jsii_name="resetPreferredInstanceClasses")
    def reset_preferred_instance_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredInstanceClasses", []))

    @jsii.member(jsii_name="resetVpc")
    def reset_vpc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpc", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxIopsPerDbInstance")
    def max_iops_per_db_instance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIopsPerDbInstance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxIopsPerGib")
    def max_iops_per_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIopsPerGib"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStorageSize")
    def max_storage_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStorageSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minIopsPerDbInstance")
    def min_iops_per_db_instance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minIopsPerDbInstance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minIopsPerGib")
    def min_iops_per_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minIopsPerGib"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minStorageSize")
    def min_storage_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minStorageSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAzCapable")
    def multi_az_capable(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "multiAzCapable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readReplicaCapable")
    def read_replica_capable(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "readReplicaCapable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsEnhancedMonitoring")
    def supports_enhanced_monitoring(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsEnhancedMonitoring"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsIamDatabaseAuthentication")
    def supports_iam_database_authentication(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsIamDatabaseAuthentication"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsIops")
    def supports_iops(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsIops"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsPerformanceInsights")
    def supports_performance_insights(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsPerformanceInsights"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsStorageEncryption")
    def supports_storage_encryption(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsStorageEncryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceClassInput")
    def instance_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModelInput")
    def license_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "licenseModelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredInstanceClassesInput")
    def preferred_instance_classes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredInstanceClassesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcInput")
    def vpc_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "vpcInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceClass")
    def instance_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceClass"))

    @instance_class.setter
    def instance_class(self, value: builtins.str) -> None:
        jsii.set(self, "instanceClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseModel"))

    @license_model.setter
    def license_model(self, value: builtins.str) -> None:
        jsii.set(self, "licenseModel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredInstanceClasses")
    def preferred_instance_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredInstanceClasses"))

    @preferred_instance_classes.setter
    def preferred_instance_classes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredInstanceClasses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "vpc", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.DataAwsNeptuneOrderableDbInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "engine": "engine",
        "engine_version": "engineVersion",
        "instance_class": "instanceClass",
        "license_model": "licenseModel",
        "preferred_instance_classes": "preferredInstanceClasses",
        "vpc": "vpc",
    },
)
class DataAwsNeptuneOrderableDbInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        instance_class: typing.Optional[builtins.str] = None,
        license_model: typing.Optional[builtins.str] = None,
        preferred_instance_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#engine DataAwsNeptuneOrderableDbInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#engine_version DataAwsNeptuneOrderableDbInstance#engine_version}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#instance_class DataAwsNeptuneOrderableDbInstance#instance_class}.
        :param license_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#license_model DataAwsNeptuneOrderableDbInstance#license_model}.
        :param preferred_instance_classes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#preferred_instance_classes DataAwsNeptuneOrderableDbInstance#preferred_instance_classes}.
        :param vpc: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#vpc DataAwsNeptuneOrderableDbInstance#vpc}.
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
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if instance_class is not None:
            self._values["instance_class"] = instance_class
        if license_model is not None:
            self._values["license_model"] = license_model
        if preferred_instance_classes is not None:
            self._values["preferred_instance_classes"] = preferred_instance_classes
        if vpc is not None:
            self._values["vpc"] = vpc

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
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#engine DataAwsNeptuneOrderableDbInstance#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#engine_version DataAwsNeptuneOrderableDbInstance#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#instance_class DataAwsNeptuneOrderableDbInstance#instance_class}.'''
        result = self._values.get("instance_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license_model(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#license_model DataAwsNeptuneOrderableDbInstance#license_model}.'''
        result = self._values.get("license_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_instance_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#preferred_instance_classes DataAwsNeptuneOrderableDbInstance#preferred_instance_classes}.'''
        result = self._values.get("preferred_instance_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/neptune_orderable_db_instance#vpc DataAwsNeptuneOrderableDbInstance#vpc}.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsNeptuneOrderableDbInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster aws_neptune_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_identifier_prefix: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        iam_database_authentication_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        neptune_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        neptune_subnet_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["NeptuneClusterTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster aws_neptune_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#apply_immediately NeptuneCluster#apply_immediately}.
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#availability_zones NeptuneCluster#availability_zones}.
        :param backup_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#backup_retention_period NeptuneCluster#backup_retention_period}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#cluster_identifier NeptuneCluster#cluster_identifier}.
        :param cluster_identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#cluster_identifier_prefix NeptuneCluster#cluster_identifier_prefix}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#copy_tags_to_snapshot NeptuneCluster#copy_tags_to_snapshot}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#deletion_protection NeptuneCluster#deletion_protection}.
        :param enable_cloudwatch_logs_exports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#enable_cloudwatch_logs_exports NeptuneCluster#enable_cloudwatch_logs_exports}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#engine NeptuneCluster#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#engine_version NeptuneCluster#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#final_snapshot_identifier NeptuneCluster#final_snapshot_identifier}.
        :param iam_database_authentication_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#iam_database_authentication_enabled NeptuneCluster#iam_database_authentication_enabled}.
        :param iam_roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#iam_roles NeptuneCluster#iam_roles}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#kms_key_arn NeptuneCluster#kms_key_arn}.
        :param neptune_cluster_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#neptune_cluster_parameter_group_name NeptuneCluster#neptune_cluster_parameter_group_name}.
        :param neptune_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#neptune_subnet_group_name NeptuneCluster#neptune_subnet_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#port NeptuneCluster#port}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#preferred_backup_window NeptuneCluster#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#preferred_maintenance_window NeptuneCluster#preferred_maintenance_window}.
        :param replication_source_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#replication_source_identifier NeptuneCluster#replication_source_identifier}.
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#skip_final_snapshot NeptuneCluster#skip_final_snapshot}.
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#snapshot_identifier NeptuneCluster#snapshot_identifier}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#storage_encrypted NeptuneCluster#storage_encrypted}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#tags NeptuneCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#tags_all NeptuneCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#timeouts NeptuneCluster#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#vpc_security_group_ids NeptuneCluster#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneClusterConfig(
            apply_immediately=apply_immediately,
            availability_zones=availability_zones,
            backup_retention_period=backup_retention_period,
            cluster_identifier=cluster_identifier,
            cluster_identifier_prefix=cluster_identifier_prefix,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            deletion_protection=deletion_protection,
            enable_cloudwatch_logs_exports=enable_cloudwatch_logs_exports,
            engine=engine,
            engine_version=engine_version,
            final_snapshot_identifier=final_snapshot_identifier,
            iam_database_authentication_enabled=iam_database_authentication_enabled,
            iam_roles=iam_roles,
            kms_key_arn=kms_key_arn,
            neptune_cluster_parameter_group_name=neptune_cluster_parameter_group_name,
            neptune_subnet_group_name=neptune_subnet_group_name,
            port=port,
            preferred_backup_window=preferred_backup_window,
            preferred_maintenance_window=preferred_maintenance_window,
            replication_source_identifier=replication_source_identifier,
            skip_final_snapshot=skip_final_snapshot,
            snapshot_identifier=snapshot_identifier,
            storage_encrypted=storage_encrypted,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            vpc_security_group_ids=vpc_security_group_ids,
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
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#create NeptuneCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#delete NeptuneCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#update NeptuneCluster#update}.
        '''
        value = NeptuneClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAvailabilityZones")
    def reset_availability_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZones", []))

    @jsii.member(jsii_name="resetBackupRetentionPeriod")
    def reset_backup_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupRetentionPeriod", []))

    @jsii.member(jsii_name="resetClusterIdentifier")
    def reset_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterIdentifier", []))

    @jsii.member(jsii_name="resetClusterIdentifierPrefix")
    def reset_cluster_identifier_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterIdentifierPrefix", []))

    @jsii.member(jsii_name="resetCopyTagsToSnapshot")
    def reset_copy_tags_to_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToSnapshot", []))

    @jsii.member(jsii_name="resetDeletionProtection")
    def reset_deletion_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionProtection", []))

    @jsii.member(jsii_name="resetEnableCloudwatchLogsExports")
    def reset_enable_cloudwatch_logs_exports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableCloudwatchLogsExports", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetFinalSnapshotIdentifier")
    def reset_final_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFinalSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetIamDatabaseAuthenticationEnabled")
    def reset_iam_database_authentication_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamDatabaseAuthenticationEnabled", []))

    @jsii.member(jsii_name="resetIamRoles")
    def reset_iam_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRoles", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetNeptuneClusterParameterGroupName")
    def reset_neptune_cluster_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNeptuneClusterParameterGroupName", []))

    @jsii.member(jsii_name="resetNeptuneSubnetGroupName")
    def reset_neptune_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNeptuneSubnetGroupName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPreferredBackupWindow")
    def reset_preferred_backup_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredBackupWindow", []))

    @jsii.member(jsii_name="resetPreferredMaintenanceWindow")
    def reset_preferred_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredMaintenanceWindow", []))

    @jsii.member(jsii_name="resetReplicationSourceIdentifier")
    def reset_replication_source_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationSourceIdentifier", []))

    @jsii.member(jsii_name="resetSkipFinalSnapshot")
    def reset_skip_final_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipFinalSnapshot", []))

    @jsii.member(jsii_name="resetSnapshotIdentifier")
    def reset_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetStorageEncrypted")
    def reset_storage_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageEncrypted", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVpcSecurityGroupIds")
    def reset_vpc_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcSecurityGroupIds", []))

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
    @jsii.member(jsii_name="clusterMembers")
    def cluster_members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clusterMembers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterResourceId")
    def cluster_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readerEndpoint")
    def reader_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readerEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "NeptuneClusterTimeoutsOutputReference":
        return typing.cast("NeptuneClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediatelyInput")
    def apply_immediately_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "applyImmediatelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZonesInput")
    def availability_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZonesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRetentionPeriodInput")
    def backup_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupRetentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierPrefixInput")
    def cluster_identifier_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshotInput")
    def copy_tags_to_snapshot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deletionProtectionInput")
    def deletion_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deletionProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableCloudwatchLogsExportsInput")
    def enable_cloudwatch_logs_exports_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enableCloudwatchLogsExportsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotIdentifierInput")
    def final_snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "finalSnapshotIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamDatabaseAuthenticationEnabledInput")
    def iam_database_authentication_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "iamDatabaseAuthenticationEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRolesInput")
    def iam_roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "iamRolesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneClusterParameterGroupNameInput")
    def neptune_cluster_parameter_group_name_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "neptuneClusterParameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneSubnetGroupNameInput")
    def neptune_subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "neptuneSubnetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindowInput")
    def preferred_backup_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredBackupWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindowInput")
    def preferred_maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSourceIdentifierInput")
    def replication_source_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSourceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipFinalSnapshotInput")
    def skip_final_snapshot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipFinalSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdentifierInput")
    def snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncryptedInput")
    def storage_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "storageEncryptedInput"))

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
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["NeptuneClusterTimeouts"]:
        return typing.cast(typing.Optional["NeptuneClusterTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediately")
    def apply_immediately(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "applyImmediately"))

    @apply_immediately.setter
    def apply_immediately(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "applyImmediately", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "availabilityZones", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupRetentionPeriod"))

    @backup_retention_period.setter
    def backup_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "backupRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierPrefix")
    def cluster_identifier_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifierPrefix"))

    @cluster_identifier_prefix.setter
    def cluster_identifier_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifierPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshot")
    def copy_tags_to_snapshot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToSnapshot"))

    @copy_tags_to_snapshot.setter
    def copy_tags_to_snapshot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToSnapshot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deletionProtection")
    def deletion_protection(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deletionProtection"))

    @deletion_protection.setter
    def deletion_protection(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deletionProtection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableCloudwatchLogsExports")
    def enable_cloudwatch_logs_exports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enableCloudwatchLogsExports"))

    @enable_cloudwatch_logs_exports.setter
    def enable_cloudwatch_logs_exports(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "enableCloudwatchLogsExports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotIdentifier")
    def final_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finalSnapshotIdentifier"))

    @final_snapshot_identifier.setter
    def final_snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "finalSnapshotIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamDatabaseAuthenticationEnabled")
    def iam_database_authentication_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "iamDatabaseAuthenticationEnabled"))

    @iam_database_authentication_enabled.setter
    def iam_database_authentication_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "iamDatabaseAuthenticationEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoles")
    def iam_roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "iamRoles"))

    @iam_roles.setter
    def iam_roles(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "iamRoles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneClusterParameterGroupName")
    def neptune_cluster_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "neptuneClusterParameterGroupName"))

    @neptune_cluster_parameter_group_name.setter
    def neptune_cluster_parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "neptuneClusterParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneSubnetGroupName")
    def neptune_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "neptuneSubnetGroupName"))

    @neptune_subnet_group_name.setter
    def neptune_subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "neptuneSubnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredBackupWindow"))

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: builtins.str) -> None:
        jsii.set(self, "preferredBackupWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSourceIdentifier")
    def replication_source_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSourceIdentifier"))

    @replication_source_identifier.setter
    def replication_source_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "replicationSourceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipFinalSnapshot")
    def skip_final_snapshot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "skipFinalSnapshot"))

    @skip_final_snapshot.setter
    def skip_final_snapshot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "skipFinalSnapshot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotIdentifier"))

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "storageEncrypted"))

    @storage_encrypted.setter
    def storage_encrypted(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "storageEncrypted", value)

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
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "apply_immediately": "applyImmediately",
        "availability_zones": "availabilityZones",
        "backup_retention_period": "backupRetentionPeriod",
        "cluster_identifier": "clusterIdentifier",
        "cluster_identifier_prefix": "clusterIdentifierPrefix",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "deletion_protection": "deletionProtection",
        "enable_cloudwatch_logs_exports": "enableCloudwatchLogsExports",
        "engine": "engine",
        "engine_version": "engineVersion",
        "final_snapshot_identifier": "finalSnapshotIdentifier",
        "iam_database_authentication_enabled": "iamDatabaseAuthenticationEnabled",
        "iam_roles": "iamRoles",
        "kms_key_arn": "kmsKeyArn",
        "neptune_cluster_parameter_group_name": "neptuneClusterParameterGroupName",
        "neptune_subnet_group_name": "neptuneSubnetGroupName",
        "port": "port",
        "preferred_backup_window": "preferredBackupWindow",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "replication_source_identifier": "replicationSourceIdentifier",
        "skip_final_snapshot": "skipFinalSnapshot",
        "snapshot_identifier": "snapshotIdentifier",
        "storage_encrypted": "storageEncrypted",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class NeptuneClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_identifier_prefix: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        iam_database_authentication_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        neptune_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        neptune_subnet_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["NeptuneClusterTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#apply_immediately NeptuneCluster#apply_immediately}.
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#availability_zones NeptuneCluster#availability_zones}.
        :param backup_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#backup_retention_period NeptuneCluster#backup_retention_period}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#cluster_identifier NeptuneCluster#cluster_identifier}.
        :param cluster_identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#cluster_identifier_prefix NeptuneCluster#cluster_identifier_prefix}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#copy_tags_to_snapshot NeptuneCluster#copy_tags_to_snapshot}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#deletion_protection NeptuneCluster#deletion_protection}.
        :param enable_cloudwatch_logs_exports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#enable_cloudwatch_logs_exports NeptuneCluster#enable_cloudwatch_logs_exports}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#engine NeptuneCluster#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#engine_version NeptuneCluster#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#final_snapshot_identifier NeptuneCluster#final_snapshot_identifier}.
        :param iam_database_authentication_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#iam_database_authentication_enabled NeptuneCluster#iam_database_authentication_enabled}.
        :param iam_roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#iam_roles NeptuneCluster#iam_roles}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#kms_key_arn NeptuneCluster#kms_key_arn}.
        :param neptune_cluster_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#neptune_cluster_parameter_group_name NeptuneCluster#neptune_cluster_parameter_group_name}.
        :param neptune_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#neptune_subnet_group_name NeptuneCluster#neptune_subnet_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#port NeptuneCluster#port}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#preferred_backup_window NeptuneCluster#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#preferred_maintenance_window NeptuneCluster#preferred_maintenance_window}.
        :param replication_source_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#replication_source_identifier NeptuneCluster#replication_source_identifier}.
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#skip_final_snapshot NeptuneCluster#skip_final_snapshot}.
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#snapshot_identifier NeptuneCluster#snapshot_identifier}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#storage_encrypted NeptuneCluster#storage_encrypted}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#tags NeptuneCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#tags_all NeptuneCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#timeouts NeptuneCluster#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#vpc_security_group_ids NeptuneCluster#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = NeptuneClusterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if apply_immediately is not None:
            self._values["apply_immediately"] = apply_immediately
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if backup_retention_period is not None:
            self._values["backup_retention_period"] = backup_retention_period
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_identifier_prefix is not None:
            self._values["cluster_identifier_prefix"] = cluster_identifier_prefix
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if enable_cloudwatch_logs_exports is not None:
            self._values["enable_cloudwatch_logs_exports"] = enable_cloudwatch_logs_exports
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_identifier is not None:
            self._values["final_snapshot_identifier"] = final_snapshot_identifier
        if iam_database_authentication_enabled is not None:
            self._values["iam_database_authentication_enabled"] = iam_database_authentication_enabled
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if neptune_cluster_parameter_group_name is not None:
            self._values["neptune_cluster_parameter_group_name"] = neptune_cluster_parameter_group_name
        if neptune_subnet_group_name is not None:
            self._values["neptune_subnet_group_name"] = neptune_subnet_group_name
        if port is not None:
            self._values["port"] = port
        if preferred_backup_window is not None:
            self._values["preferred_backup_window"] = preferred_backup_window
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if replication_source_identifier is not None:
            self._values["replication_source_identifier"] = replication_source_identifier
        if skip_final_snapshot is not None:
            self._values["skip_final_snapshot"] = skip_final_snapshot
        if snapshot_identifier is not None:
            self._values["snapshot_identifier"] = snapshot_identifier
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if vpc_security_group_ids is not None:
            self._values["vpc_security_group_ids"] = vpc_security_group_ids

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
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#apply_immediately NeptuneCluster#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#availability_zones NeptuneCluster#availability_zones}.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#backup_retention_period NeptuneCluster#backup_retention_period}.'''
        result = self._values.get("backup_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#cluster_identifier NeptuneCluster#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_identifier_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#cluster_identifier_prefix NeptuneCluster#cluster_identifier_prefix}.'''
        result = self._values.get("cluster_identifier_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#copy_tags_to_snapshot NeptuneCluster#copy_tags_to_snapshot}.'''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def deletion_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#deletion_protection NeptuneCluster#deletion_protection}.'''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_cloudwatch_logs_exports(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#enable_cloudwatch_logs_exports NeptuneCluster#enable_cloudwatch_logs_exports}.'''
        result = self._values.get("enable_cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#engine NeptuneCluster#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#engine_version NeptuneCluster#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#final_snapshot_identifier NeptuneCluster#final_snapshot_identifier}.'''
        result = self._values.get("final_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_database_authentication_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#iam_database_authentication_enabled NeptuneCluster#iam_database_authentication_enabled}.'''
        result = self._values.get("iam_database_authentication_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iam_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#iam_roles NeptuneCluster#iam_roles}.'''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#kms_key_arn NeptuneCluster#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def neptune_cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#neptune_cluster_parameter_group_name NeptuneCluster#neptune_cluster_parameter_group_name}.'''
        result = self._values.get("neptune_cluster_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def neptune_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#neptune_subnet_group_name NeptuneCluster#neptune_subnet_group_name}.'''
        result = self._values.get("neptune_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#port NeptuneCluster#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_backup_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#preferred_backup_window NeptuneCluster#preferred_backup_window}.'''
        result = self._values.get("preferred_backup_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#preferred_maintenance_window NeptuneCluster#preferred_maintenance_window}.'''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_source_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#replication_source_identifier NeptuneCluster#replication_source_identifier}.'''
        result = self._values.get("replication_source_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_final_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#skip_final_snapshot NeptuneCluster#skip_final_snapshot}.'''
        result = self._values.get("skip_final_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#snapshot_identifier NeptuneCluster#snapshot_identifier}.'''
        result = self._values.get("snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#storage_encrypted NeptuneCluster#storage_encrypted}.'''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#tags NeptuneCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#tags_all NeptuneCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["NeptuneClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#timeouts NeptuneCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["NeptuneClusterTimeouts"], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#vpc_security_group_ids NeptuneCluster#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneClusterEndpoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint aws_neptune_cluster_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_endpoint_identifier: builtins.str,
        cluster_identifier: builtins.str,
        endpoint_type: builtins.str,
        excluded_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        static_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint aws_neptune_cluster_endpoint} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_endpoint_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#cluster_endpoint_identifier NeptuneClusterEndpoint#cluster_endpoint_identifier}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#cluster_identifier NeptuneClusterEndpoint#cluster_identifier}.
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#endpoint_type NeptuneClusterEndpoint#endpoint_type}.
        :param excluded_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#excluded_members NeptuneClusterEndpoint#excluded_members}.
        :param static_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#static_members NeptuneClusterEndpoint#static_members}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#tags NeptuneClusterEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#tags_all NeptuneClusterEndpoint#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneClusterEndpointConfig(
            cluster_endpoint_identifier=cluster_endpoint_identifier,
            cluster_identifier=cluster_identifier,
            endpoint_type=endpoint_type,
            excluded_members=excluded_members,
            static_members=static_members,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetExcludedMembers")
    def reset_excluded_members(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedMembers", []))

    @jsii.member(jsii_name="resetStaticMembers")
    def reset_static_members(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticMembers", []))

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
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpointIdentifierInput")
    def cluster_endpoint_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterEndpointIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointTypeInput")
    def endpoint_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedMembersInput")
    def excluded_members_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedMembersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticMembersInput")
    def static_members_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "staticMembersInput"))

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
    @jsii.member(jsii_name="clusterEndpointIdentifier")
    def cluster_endpoint_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterEndpointIdentifier"))

    @cluster_endpoint_identifier.setter
    def cluster_endpoint_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterEndpointIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @endpoint_type.setter
    def endpoint_type(self, value: builtins.str) -> None:
        jsii.set(self, "endpointType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludedMembers")
    def excluded_members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedMembers"))

    @excluded_members.setter
    def excluded_members(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "excludedMembers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticMembers")
    def static_members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "staticMembers"))

    @static_members.setter
    def static_members(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "staticMembers", value)

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
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_endpoint_identifier": "clusterEndpointIdentifier",
        "cluster_identifier": "clusterIdentifier",
        "endpoint_type": "endpointType",
        "excluded_members": "excludedMembers",
        "static_members": "staticMembers",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NeptuneClusterEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_endpoint_identifier: builtins.str,
        cluster_identifier: builtins.str,
        endpoint_type: builtins.str,
        excluded_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        static_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_endpoint_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#cluster_endpoint_identifier NeptuneClusterEndpoint#cluster_endpoint_identifier}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#cluster_identifier NeptuneClusterEndpoint#cluster_identifier}.
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#endpoint_type NeptuneClusterEndpoint#endpoint_type}.
        :param excluded_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#excluded_members NeptuneClusterEndpoint#excluded_members}.
        :param static_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#static_members NeptuneClusterEndpoint#static_members}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#tags NeptuneClusterEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#tags_all NeptuneClusterEndpoint#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_endpoint_identifier": cluster_endpoint_identifier,
            "cluster_identifier": cluster_identifier,
            "endpoint_type": endpoint_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if excluded_members is not None:
            self._values["excluded_members"] = excluded_members
        if static_members is not None:
            self._values["static_members"] = static_members
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
    def cluster_endpoint_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#cluster_endpoint_identifier NeptuneClusterEndpoint#cluster_endpoint_identifier}.'''
        result = self._values.get("cluster_endpoint_identifier")
        assert result is not None, "Required property 'cluster_endpoint_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#cluster_identifier NeptuneClusterEndpoint#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#endpoint_type NeptuneClusterEndpoint#endpoint_type}.'''
        result = self._values.get("endpoint_type")
        assert result is not None, "Required property 'endpoint_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def excluded_members(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#excluded_members NeptuneClusterEndpoint#excluded_members}.'''
        result = self._values.get("excluded_members")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def static_members(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#static_members NeptuneClusterEndpoint#static_members}.'''
        result = self._values.get("static_members")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#tags NeptuneClusterEndpoint#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_endpoint#tags_all NeptuneClusterEndpoint#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneClusterInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance aws_neptune_cluster_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_identifier: builtins.str,
        instance_class: builtins.str,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        neptune_parameter_group_name: typing.Optional[builtins.str] = None,
        neptune_subnet_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        promotion_tier: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["NeptuneClusterInstanceTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance aws_neptune_cluster_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#cluster_identifier NeptuneClusterInstance#cluster_identifier}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#instance_class NeptuneClusterInstance#instance_class}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#apply_immediately NeptuneClusterInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#auto_minor_version_upgrade NeptuneClusterInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#availability_zone NeptuneClusterInstance#availability_zone}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#engine NeptuneClusterInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#engine_version NeptuneClusterInstance#engine_version}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#identifier NeptuneClusterInstance#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#identifier_prefix NeptuneClusterInstance#identifier_prefix}.
        :param neptune_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#neptune_parameter_group_name NeptuneClusterInstance#neptune_parameter_group_name}.
        :param neptune_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#neptune_subnet_group_name NeptuneClusterInstance#neptune_subnet_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#port NeptuneClusterInstance#port}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#preferred_backup_window NeptuneClusterInstance#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#preferred_maintenance_window NeptuneClusterInstance#preferred_maintenance_window}.
        :param promotion_tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#promotion_tier NeptuneClusterInstance#promotion_tier}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#publicly_accessible NeptuneClusterInstance#publicly_accessible}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#tags NeptuneClusterInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#tags_all NeptuneClusterInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#timeouts NeptuneClusterInstance#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneClusterInstanceConfig(
            cluster_identifier=cluster_identifier,
            instance_class=instance_class,
            apply_immediately=apply_immediately,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            engine=engine,
            engine_version=engine_version,
            identifier=identifier,
            identifier_prefix=identifier_prefix,
            neptune_parameter_group_name=neptune_parameter_group_name,
            neptune_subnet_group_name=neptune_subnet_group_name,
            port=port,
            preferred_backup_window=preferred_backup_window,
            preferred_maintenance_window=preferred_maintenance_window,
            promotion_tier=promotion_tier,
            publicly_accessible=publicly_accessible,
            tags=tags,
            tags_all=tags_all,
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
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#create NeptuneClusterInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#delete NeptuneClusterInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#update NeptuneClusterInstance#update}.
        '''
        value = NeptuneClusterInstanceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAutoMinorVersionUpgrade")
    def reset_auto_minor_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoMinorVersionUpgrade", []))

    @jsii.member(jsii_name="resetAvailabilityZone")
    def reset_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZone", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetIdentifier")
    def reset_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifier", []))

    @jsii.member(jsii_name="resetIdentifierPrefix")
    def reset_identifier_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifierPrefix", []))

    @jsii.member(jsii_name="resetNeptuneParameterGroupName")
    def reset_neptune_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNeptuneParameterGroupName", []))

    @jsii.member(jsii_name="resetNeptuneSubnetGroupName")
    def reset_neptune_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNeptuneSubnetGroupName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPreferredBackupWindow")
    def reset_preferred_backup_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredBackupWindow", []))

    @jsii.member(jsii_name="resetPreferredMaintenanceWindow")
    def reset_preferred_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredMaintenanceWindow", []))

    @jsii.member(jsii_name="resetPromotionTier")
    def reset_promotion_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPromotionTier", []))

    @jsii.member(jsii_name="resetPubliclyAccessible")
    def reset_publicly_accessible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPubliclyAccessible", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

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
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbiResourceId")
    def dbi_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbiResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "storageEncrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "NeptuneClusterInstanceTimeoutsOutputReference":
        return typing.cast("NeptuneClusterInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writer")
    def writer(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "writer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediatelyInput")
    def apply_immediately_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "applyImmediatelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgradeInput")
    def auto_minor_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoMinorVersionUpgradeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierPrefixInput")
    def identifier_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceClassInput")
    def instance_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneParameterGroupNameInput")
    def neptune_parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "neptuneParameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneSubnetGroupNameInput")
    def neptune_subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "neptuneSubnetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindowInput")
    def preferred_backup_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredBackupWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindowInput")
    def preferred_maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="promotionTierInput")
    def promotion_tier_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "promotionTierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessibleInput")
    def publicly_accessible_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publiclyAccessibleInput"))

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
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["NeptuneClusterInstanceTimeouts"]:
        return typing.cast(typing.Optional["NeptuneClusterInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediately")
    def apply_immediately(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "applyImmediately"))

    @apply_immediately.setter
    def apply_immediately(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "applyImmediately", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoMinorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identifier"))

    @identifier.setter
    def identifier(self, value: builtins.str) -> None:
        jsii.set(self, "identifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierPrefix")
    def identifier_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identifierPrefix"))

    @identifier_prefix.setter
    def identifier_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "identifierPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceClass")
    def instance_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceClass"))

    @instance_class.setter
    def instance_class(self, value: builtins.str) -> None:
        jsii.set(self, "instanceClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneParameterGroupName")
    def neptune_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "neptuneParameterGroupName"))

    @neptune_parameter_group_name.setter
    def neptune_parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "neptuneParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneSubnetGroupName")
    def neptune_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "neptuneSubnetGroupName"))

    @neptune_subnet_group_name.setter
    def neptune_subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "neptuneSubnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredBackupWindow"))

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: builtins.str) -> None:
        jsii.set(self, "preferredBackupWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="promotionTier")
    def promotion_tier(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "promotionTier"))

    @promotion_tier.setter
    def promotion_tier(self, value: jsii.Number) -> None:
        jsii.set(self, "promotionTier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publiclyAccessible"))

    @publicly_accessible.setter
    def publicly_accessible(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "publiclyAccessible", value)

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
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_identifier": "clusterIdentifier",
        "instance_class": "instanceClass",
        "apply_immediately": "applyImmediately",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zone": "availabilityZone",
        "engine": "engine",
        "engine_version": "engineVersion",
        "identifier": "identifier",
        "identifier_prefix": "identifierPrefix",
        "neptune_parameter_group_name": "neptuneParameterGroupName",
        "neptune_subnet_group_name": "neptuneSubnetGroupName",
        "port": "port",
        "preferred_backup_window": "preferredBackupWindow",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "promotion_tier": "promotionTier",
        "publicly_accessible": "publiclyAccessible",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class NeptuneClusterInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_identifier: builtins.str,
        instance_class: builtins.str,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        neptune_parameter_group_name: typing.Optional[builtins.str] = None,
        neptune_subnet_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        promotion_tier: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["NeptuneClusterInstanceTimeouts"] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#cluster_identifier NeptuneClusterInstance#cluster_identifier}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#instance_class NeptuneClusterInstance#instance_class}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#apply_immediately NeptuneClusterInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#auto_minor_version_upgrade NeptuneClusterInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#availability_zone NeptuneClusterInstance#availability_zone}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#engine NeptuneClusterInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#engine_version NeptuneClusterInstance#engine_version}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#identifier NeptuneClusterInstance#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#identifier_prefix NeptuneClusterInstance#identifier_prefix}.
        :param neptune_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#neptune_parameter_group_name NeptuneClusterInstance#neptune_parameter_group_name}.
        :param neptune_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#neptune_subnet_group_name NeptuneClusterInstance#neptune_subnet_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#port NeptuneClusterInstance#port}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#preferred_backup_window NeptuneClusterInstance#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#preferred_maintenance_window NeptuneClusterInstance#preferred_maintenance_window}.
        :param promotion_tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#promotion_tier NeptuneClusterInstance#promotion_tier}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#publicly_accessible NeptuneClusterInstance#publicly_accessible}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#tags NeptuneClusterInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#tags_all NeptuneClusterInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#timeouts NeptuneClusterInstance#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = NeptuneClusterInstanceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
            "instance_class": instance_class,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if apply_immediately is not None:
            self._values["apply_immediately"] = apply_immediately
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if identifier is not None:
            self._values["identifier"] = identifier
        if identifier_prefix is not None:
            self._values["identifier_prefix"] = identifier_prefix
        if neptune_parameter_group_name is not None:
            self._values["neptune_parameter_group_name"] = neptune_parameter_group_name
        if neptune_subnet_group_name is not None:
            self._values["neptune_subnet_group_name"] = neptune_subnet_group_name
        if port is not None:
            self._values["port"] = port
        if preferred_backup_window is not None:
            self._values["preferred_backup_window"] = preferred_backup_window
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if promotion_tier is not None:
            self._values["promotion_tier"] = promotion_tier
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
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
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#cluster_identifier NeptuneClusterInstance#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#instance_class NeptuneClusterInstance#instance_class}.'''
        result = self._values.get("instance_class")
        assert result is not None, "Required property 'instance_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#apply_immediately NeptuneClusterInstance#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#auto_minor_version_upgrade NeptuneClusterInstance#auto_minor_version_upgrade}.'''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#availability_zone NeptuneClusterInstance#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#engine NeptuneClusterInstance#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#engine_version NeptuneClusterInstance#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#identifier NeptuneClusterInstance#identifier}.'''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#identifier_prefix NeptuneClusterInstance#identifier_prefix}.'''
        result = self._values.get("identifier_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def neptune_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#neptune_parameter_group_name NeptuneClusterInstance#neptune_parameter_group_name}.'''
        result = self._values.get("neptune_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def neptune_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#neptune_subnet_group_name NeptuneClusterInstance#neptune_subnet_group_name}.'''
        result = self._values.get("neptune_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#port NeptuneClusterInstance#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_backup_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#preferred_backup_window NeptuneClusterInstance#preferred_backup_window}.'''
        result = self._values.get("preferred_backup_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#preferred_maintenance_window NeptuneClusterInstance#preferred_maintenance_window}.'''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def promotion_tier(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#promotion_tier NeptuneClusterInstance#promotion_tier}.'''
        result = self._values.get("promotion_tier")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#publicly_accessible NeptuneClusterInstance#publicly_accessible}.'''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#tags NeptuneClusterInstance#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#tags_all NeptuneClusterInstance#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["NeptuneClusterInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#timeouts NeptuneClusterInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["NeptuneClusterInstanceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class NeptuneClusterInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#create NeptuneClusterInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#delete NeptuneClusterInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#update NeptuneClusterInstance#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#create NeptuneClusterInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#delete NeptuneClusterInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_instance#update NeptuneClusterInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneClusterInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterInstanceTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

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
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NeptuneClusterInstanceTimeouts]:
        return typing.cast(typing.Optional[NeptuneClusterInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NeptuneClusterInstanceTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class NeptuneClusterParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group aws_neptune_cluster_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["NeptuneClusterParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group aws_neptune_cluster_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#family NeptuneClusterParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#description NeptuneClusterParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name NeptuneClusterParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name_prefix NeptuneClusterParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#parameter NeptuneClusterParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#tags NeptuneClusterParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#tags_all NeptuneClusterParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneClusterParameterGroupConfig(
            family=family,
            description=description,
            name=name,
            name_prefix=name_prefix,
            parameter=parameter,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.List["NeptuneClusterParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["NeptuneClusterParameterGroupParameter"]], jsii.get(self, "parameterInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> typing.List["NeptuneClusterParameterGroupParameter"]:
        return typing.cast(typing.List["NeptuneClusterParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(
        self,
        value: typing.List["NeptuneClusterParameterGroupParameter"],
    ) -> None:
        jsii.set(self, "parameter", value)

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
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterParameterGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "family": "family",
        "description": "description",
        "name": "name",
        "name_prefix": "namePrefix",
        "parameter": "parameter",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NeptuneClusterParameterGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        family: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["NeptuneClusterParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#family NeptuneClusterParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#description NeptuneClusterParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name NeptuneClusterParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name_prefix NeptuneClusterParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#parameter NeptuneClusterParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#tags NeptuneClusterParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#tags_all NeptuneClusterParameterGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "family": family,
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
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if parameter is not None:
            self._values["parameter"] = parameter
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
    def family(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#family NeptuneClusterParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#description NeptuneClusterParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name NeptuneClusterParameterGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name_prefix NeptuneClusterParameterGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["NeptuneClusterParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#parameter NeptuneClusterParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["NeptuneClusterParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#tags NeptuneClusterParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#tags_all NeptuneClusterParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value", "apply_method": "applyMethod"},
)
class NeptuneClusterParameterGroupParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: builtins.str,
        apply_method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name NeptuneClusterParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#value NeptuneClusterParameterGroup#value}.
        :param apply_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#apply_method NeptuneClusterParameterGroup#apply_method}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }
        if apply_method is not None:
            self._values["apply_method"] = apply_method

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#name NeptuneClusterParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#value NeptuneClusterParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_parameter_group#apply_method NeptuneClusterParameterGroup#apply_method}.'''
        result = self._values.get("apply_method")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneClusterSnapshot(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot aws_neptune_cluster_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_cluster_identifier: builtins.str,
        db_cluster_snapshot_identifier: builtins.str,
        timeouts: typing.Optional["NeptuneClusterSnapshotTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot aws_neptune_cluster_snapshot} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#db_cluster_identifier NeptuneClusterSnapshot#db_cluster_identifier}.
        :param db_cluster_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#db_cluster_snapshot_identifier NeptuneClusterSnapshot#db_cluster_snapshot_identifier}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#timeouts NeptuneClusterSnapshot#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneClusterSnapshotConfig(
            db_cluster_identifier=db_cluster_identifier,
            db_cluster_snapshot_identifier=db_cluster_snapshot_identifier,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#create NeptuneClusterSnapshot#create}.
        '''
        value = NeptuneClusterSnapshotTimeouts(create=create)

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
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allocatedStorage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterSnapshotArn")
    def db_cluster_snapshot_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterSnapshotArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseModel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotType")
    def snapshot_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbClusterSnapshotArn")
    def source_db_cluster_snapshot_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDbClusterSnapshotArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "storageEncrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "NeptuneClusterSnapshotTimeoutsOutputReference":
        return typing.cast("NeptuneClusterSnapshotTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifierInput")
    def db_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterSnapshotIdentifierInput")
    def db_cluster_snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterSnapshotIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["NeptuneClusterSnapshotTimeouts"]:
        return typing.cast(typing.Optional["NeptuneClusterSnapshotTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterIdentifier"))

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterSnapshotIdentifier")
    def db_cluster_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterSnapshotIdentifier"))

    @db_cluster_snapshot_identifier.setter
    def db_cluster_snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbClusterSnapshotIdentifier", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_cluster_identifier": "dbClusterIdentifier",
        "db_cluster_snapshot_identifier": "dbClusterSnapshotIdentifier",
        "timeouts": "timeouts",
    },
)
class NeptuneClusterSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_cluster_identifier: builtins.str,
        db_cluster_snapshot_identifier: builtins.str,
        timeouts: typing.Optional["NeptuneClusterSnapshotTimeouts"] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#db_cluster_identifier NeptuneClusterSnapshot#db_cluster_identifier}.
        :param db_cluster_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#db_cluster_snapshot_identifier NeptuneClusterSnapshot#db_cluster_snapshot_identifier}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#timeouts NeptuneClusterSnapshot#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = NeptuneClusterSnapshotTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "db_cluster_identifier": db_cluster_identifier,
            "db_cluster_snapshot_identifier": db_cluster_snapshot_identifier,
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
    def db_cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#db_cluster_identifier NeptuneClusterSnapshot#db_cluster_identifier}.'''
        result = self._values.get("db_cluster_identifier")
        assert result is not None, "Required property 'db_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_cluster_snapshot_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#db_cluster_snapshot_identifier NeptuneClusterSnapshot#db_cluster_snapshot_identifier}.'''
        result = self._values.get("db_cluster_snapshot_identifier")
        assert result is not None, "Required property 'db_cluster_snapshot_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeouts(self) -> typing.Optional["NeptuneClusterSnapshotTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#timeouts NeptuneClusterSnapshot#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["NeptuneClusterSnapshotTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterSnapshotTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class NeptuneClusterSnapshotTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#create NeptuneClusterSnapshot#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster_snapshot#create NeptuneClusterSnapshot#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterSnapshotTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneClusterSnapshotTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterSnapshotTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[NeptuneClusterSnapshotTimeouts]:
        return typing.cast(typing.Optional[NeptuneClusterSnapshotTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NeptuneClusterSnapshotTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class NeptuneClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#create NeptuneCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#delete NeptuneCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#update NeptuneCluster#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#create NeptuneCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#delete NeptuneCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_cluster#update NeptuneCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneClusterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneClusterTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

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
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NeptuneClusterTimeouts]:
        return typing.cast(typing.Optional[NeptuneClusterTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[NeptuneClusterTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class NeptuneEventSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneEventSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription aws_neptune_event_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["NeptuneEventSubscriptionTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription aws_neptune_event_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#sns_topic_arn NeptuneEventSubscription#sns_topic_arn}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#enabled NeptuneEventSubscription#enabled}.
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#event_categories NeptuneEventSubscription#event_categories}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#name NeptuneEventSubscription#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#name_prefix NeptuneEventSubscription#name_prefix}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#source_ids NeptuneEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#source_type NeptuneEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#tags NeptuneEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#tags_all NeptuneEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#timeouts NeptuneEventSubscription#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneEventSubscriptionConfig(
            sns_topic_arn=sns_topic_arn,
            enabled=enabled,
            event_categories=event_categories,
            name=name,
            name_prefix=name_prefix,
            source_ids=source_ids,
            source_type=source_type,
            tags=tags,
            tags_all=tags_all,
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
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#create NeptuneEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#delete NeptuneEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#update NeptuneEventSubscription#update}.
        '''
        value = NeptuneEventSubscriptionTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEventCategories")
    def reset_event_categories(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventCategories", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetSourceIds")
    def reset_source_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceIds", []))

    @jsii.member(jsii_name="resetSourceType")
    def reset_source_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerAwsId")
    def customer_aws_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerAwsId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "NeptuneEventSubscriptionTimeoutsOutputReference":
        return typing.cast("NeptuneEventSubscriptionTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventCategoriesInput")
    def event_categories_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventCategoriesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArnInput")
    def sns_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIdsInput")
    def source_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sourceIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceTypeInput")
    def source_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTypeInput"))

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
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["NeptuneEventSubscriptionTimeouts"]:
        return typing.cast(typing.Optional["NeptuneEventSubscriptionTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventCategories")
    def event_categories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventCategories"))

    @event_categories.setter
    def event_categories(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "eventCategories", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIds")
    def source_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sourceIds"))

    @source_ids.setter
    def source_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "sourceIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceType"))

    @source_type.setter
    def source_type(self, value: builtins.str) -> None:
        jsii.set(self, "sourceType", value)

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
    jsii_type="@cdktf/provider-aws.neptune.NeptuneEventSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "sns_topic_arn": "snsTopicArn",
        "enabled": "enabled",
        "event_categories": "eventCategories",
        "name": "name",
        "name_prefix": "namePrefix",
        "source_ids": "sourceIds",
        "source_type": "sourceType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class NeptuneEventSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["NeptuneEventSubscriptionTimeouts"] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#sns_topic_arn NeptuneEventSubscription#sns_topic_arn}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#enabled NeptuneEventSubscription#enabled}.
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#event_categories NeptuneEventSubscription#event_categories}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#name NeptuneEventSubscription#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#name_prefix NeptuneEventSubscription#name_prefix}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#source_ids NeptuneEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#source_type NeptuneEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#tags NeptuneEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#tags_all NeptuneEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#timeouts NeptuneEventSubscription#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = NeptuneEventSubscriptionTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "sns_topic_arn": sns_topic_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_categories is not None:
            self._values["event_categories"] = event_categories
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if source_ids is not None:
            self._values["source_ids"] = source_ids
        if source_type is not None:
            self._values["source_type"] = source_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
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
    def sns_topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#sns_topic_arn NeptuneEventSubscription#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        assert result is not None, "Required property 'sns_topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#enabled NeptuneEventSubscription#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def event_categories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#event_categories NeptuneEventSubscription#event_categories}.'''
        result = self._values.get("event_categories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#name NeptuneEventSubscription#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#name_prefix NeptuneEventSubscription#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#source_ids NeptuneEventSubscription#source_ids}.'''
        result = self._values.get("source_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#source_type NeptuneEventSubscription#source_type}.'''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#tags NeptuneEventSubscription#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#tags_all NeptuneEventSubscription#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["NeptuneEventSubscriptionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#timeouts NeptuneEventSubscription#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["NeptuneEventSubscriptionTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneEventSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneEventSubscriptionTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class NeptuneEventSubscriptionTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#create NeptuneEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#delete NeptuneEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#update NeptuneEventSubscription#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#create NeptuneEventSubscription#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#delete NeptuneEventSubscription#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_event_subscription#update NeptuneEventSubscription#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneEventSubscriptionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneEventSubscriptionTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneEventSubscriptionTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

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
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NeptuneEventSubscriptionTimeouts]:
        return typing.cast(typing.Optional[NeptuneEventSubscriptionTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NeptuneEventSubscriptionTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class NeptuneParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group aws_neptune_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["NeptuneParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group aws_neptune_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#family NeptuneParameterGroup#family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#name NeptuneParameterGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#description NeptuneParameterGroup#description}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#parameter NeptuneParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#tags NeptuneParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#tags_all NeptuneParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneParameterGroupConfig(
            family=family,
            name=name,
            description=description,
            parameter=parameter,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.List["NeptuneParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["NeptuneParameterGroupParameter"]], jsii.get(self, "parameterInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> typing.List["NeptuneParameterGroupParameter"]:
        return typing.cast(typing.List["NeptuneParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(self, value: typing.List["NeptuneParameterGroupParameter"]) -> None:
        jsii.set(self, "parameter", value)

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
    jsii_type="@cdktf/provider-aws.neptune.NeptuneParameterGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "family": "family",
        "name": "name",
        "description": "description",
        "parameter": "parameter",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NeptuneParameterGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        family: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["NeptuneParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#family NeptuneParameterGroup#family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#name NeptuneParameterGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#description NeptuneParameterGroup#description}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#parameter NeptuneParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#tags NeptuneParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#tags_all NeptuneParameterGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "family": family,
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
        if parameter is not None:
            self._values["parameter"] = parameter
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
    def family(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#family NeptuneParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#name NeptuneParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#description NeptuneParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["NeptuneParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#parameter NeptuneParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["NeptuneParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#tags NeptuneParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#tags_all NeptuneParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value", "apply_method": "applyMethod"},
)
class NeptuneParameterGroupParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: builtins.str,
        apply_method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#name NeptuneParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#value NeptuneParameterGroup#value}.
        :param apply_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#apply_method NeptuneParameterGroup#apply_method}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }
        if apply_method is not None:
            self._values["apply_method"] = apply_method

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#name NeptuneParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#value NeptuneParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_parameter_group#apply_method NeptuneParameterGroup#apply_method}.'''
        result = self._values.get("apply_method")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NeptuneSubnetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.neptune.NeptuneSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group aws_neptune_subnet_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        subnet_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group aws_neptune_subnet_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#subnet_ids NeptuneSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#description NeptuneSubnetGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#name NeptuneSubnetGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#name_prefix NeptuneSubnetGroup#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#tags NeptuneSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#tags_all NeptuneSubnetGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NeptuneSubnetGroupConfig(
            subnet_ids=subnet_ids,
            description=description,
            name=name,
            name_prefix=name_prefix,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

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
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.neptune.NeptuneSubnetGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "subnet_ids": "subnetIds",
        "description": "description",
        "name": "name",
        "name_prefix": "namePrefix",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class NeptuneSubnetGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        subnet_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Neptune.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#subnet_ids NeptuneSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#description NeptuneSubnetGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#name NeptuneSubnetGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#name_prefix NeptuneSubnetGroup#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#tags NeptuneSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#tags_all NeptuneSubnetGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "subnet_ids": subnet_ids,
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
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
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
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#subnet_ids NeptuneSubnetGroup#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#description NeptuneSubnetGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#name NeptuneSubnetGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#name_prefix NeptuneSubnetGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#tags NeptuneSubnetGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/neptune_subnet_group#tags_all NeptuneSubnetGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NeptuneSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsNeptuneEngineVersion",
    "DataAwsNeptuneEngineVersionConfig",
    "DataAwsNeptuneOrderableDbInstance",
    "DataAwsNeptuneOrderableDbInstanceConfig",
    "NeptuneCluster",
    "NeptuneClusterConfig",
    "NeptuneClusterEndpoint",
    "NeptuneClusterEndpointConfig",
    "NeptuneClusterInstance",
    "NeptuneClusterInstanceConfig",
    "NeptuneClusterInstanceTimeouts",
    "NeptuneClusterInstanceTimeoutsOutputReference",
    "NeptuneClusterParameterGroup",
    "NeptuneClusterParameterGroupConfig",
    "NeptuneClusterParameterGroupParameter",
    "NeptuneClusterSnapshot",
    "NeptuneClusterSnapshotConfig",
    "NeptuneClusterSnapshotTimeouts",
    "NeptuneClusterSnapshotTimeoutsOutputReference",
    "NeptuneClusterTimeouts",
    "NeptuneClusterTimeoutsOutputReference",
    "NeptuneEventSubscription",
    "NeptuneEventSubscriptionConfig",
    "NeptuneEventSubscriptionTimeouts",
    "NeptuneEventSubscriptionTimeoutsOutputReference",
    "NeptuneParameterGroup",
    "NeptuneParameterGroupConfig",
    "NeptuneParameterGroupParameter",
    "NeptuneSubnetGroup",
    "NeptuneSubnetGroupConfig",
]

publication.publish()
