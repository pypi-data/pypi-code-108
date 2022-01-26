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


class DataAwsRedshiftCluster(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.DataAwsRedshiftCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster aws_redshift_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster aws_redshift_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster#cluster_identifier DataAwsRedshiftCluster#cluster_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster#tags DataAwsRedshiftCluster#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRedshiftClusterConfig(
            cluster_identifier=cluster_identifier,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowVersionUpgrade")
    def allow_version_upgrade(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "allowVersionUpgrade"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automatedSnapshotRetentionPeriod")
    def automated_snapshot_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "automatedSnapshotRetentionPeriod"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterParameterGroupName")
    def cluster_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterParameterGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterPublicKey")
    def cluster_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterPublicKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterRevisionNumber")
    def cluster_revision_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterRevisionNumber"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSecurityGroups")
    def cluster_security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clusterSecurityGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSubnetGroupName")
    def cluster_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterSubnetGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableLogging")
    def enable_logging(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableLogging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedVpcRouting")
    def enhanced_vpc_routing(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enhancedVpcRouting"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoles")
    def iam_roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "iamRoles"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterUsername"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfNodes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "publiclyAccessible"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KeyPrefix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroupIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

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
    jsii_type="@cdktf/provider-aws.redshift.DataAwsRedshiftClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_identifier": "clusterIdentifier",
        "tags": "tags",
    },
)
class DataAwsRedshiftClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster#cluster_identifier DataAwsRedshiftCluster#cluster_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster#tags DataAwsRedshiftCluster#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
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
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster#cluster_identifier DataAwsRedshiftCluster#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_cluster#tags DataAwsRedshiftCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRedshiftClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsRedshiftOrderableCluster(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.DataAwsRedshiftOrderableCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster aws_redshift_orderable_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_type: typing.Optional[builtins.str] = None,
        cluster_version: typing.Optional[builtins.str] = None,
        node_type: typing.Optional[builtins.str] = None,
        preferred_node_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster aws_redshift_orderable_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#cluster_type DataAwsRedshiftOrderableCluster#cluster_type}.
        :param cluster_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#cluster_version DataAwsRedshiftOrderableCluster#cluster_version}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#node_type DataAwsRedshiftOrderableCluster#node_type}.
        :param preferred_node_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#preferred_node_types DataAwsRedshiftOrderableCluster#preferred_node_types}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRedshiftOrderableClusterConfig(
            cluster_type=cluster_type,
            cluster_version=cluster_version,
            node_type=node_type,
            preferred_node_types=preferred_node_types,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetClusterType")
    def reset_cluster_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterType", []))

    @jsii.member(jsii_name="resetClusterVersion")
    def reset_cluster_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterVersion", []))

    @jsii.member(jsii_name="resetNodeType")
    def reset_node_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeType", []))

    @jsii.member(jsii_name="resetPreferredNodeTypes")
    def reset_preferred_node_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredNodeTypes", []))

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
    @jsii.member(jsii_name="clusterTypeInput")
    def cluster_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersionInput")
    def cluster_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeTypeInput")
    def node_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredNodeTypesInput")
    def preferred_node_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredNodeTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @cluster_type.setter
    def cluster_type(self, value: builtins.str) -> None:
        jsii.set(self, "clusterType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterVersion"))

    @cluster_version.setter
    def cluster_version(self, value: builtins.str) -> None:
        jsii.set(self, "clusterVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredNodeTypes")
    def preferred_node_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredNodeTypes"))

    @preferred_node_types.setter
    def preferred_node_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredNodeTypes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.DataAwsRedshiftOrderableClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_type": "clusterType",
        "cluster_version": "clusterVersion",
        "node_type": "nodeType",
        "preferred_node_types": "preferredNodeTypes",
    },
)
class DataAwsRedshiftOrderableClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        cluster_version: typing.Optional[builtins.str] = None,
        node_type: typing.Optional[builtins.str] = None,
        preferred_node_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#cluster_type DataAwsRedshiftOrderableCluster#cluster_type}.
        :param cluster_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#cluster_version DataAwsRedshiftOrderableCluster#cluster_version}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#node_type DataAwsRedshiftOrderableCluster#node_type}.
        :param preferred_node_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#preferred_node_types DataAwsRedshiftOrderableCluster#preferred_node_types}.
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
        if cluster_type is not None:
            self._values["cluster_type"] = cluster_type
        if cluster_version is not None:
            self._values["cluster_version"] = cluster_version
        if node_type is not None:
            self._values["node_type"] = node_type
        if preferred_node_types is not None:
            self._values["preferred_node_types"] = preferred_node_types

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
    def cluster_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#cluster_type DataAwsRedshiftOrderableCluster#cluster_type}.'''
        result = self._values.get("cluster_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#cluster_version DataAwsRedshiftOrderableCluster#cluster_version}.'''
        result = self._values.get("cluster_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#node_type DataAwsRedshiftOrderableCluster#node_type}.'''
        result = self._values.get("node_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_node_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_orderable_cluster#preferred_node_types DataAwsRedshiftOrderableCluster#preferred_node_types}.'''
        result = self._values.get("preferred_node_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRedshiftOrderableClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsRedshiftServiceAccount(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.DataAwsRedshiftServiceAccount",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/redshift_service_account aws_redshift_service_account}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        region: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/redshift_service_account aws_redshift_service_account} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_service_account#region DataAwsRedshiftServiceAccount#region}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRedshiftServiceAccountConfig(
            region=region,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

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
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.DataAwsRedshiftServiceAccountConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "region": "region",
    },
)
class DataAwsRedshiftServiceAccountConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_service_account#region DataAwsRedshiftServiceAccount#region}.
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
        if region is not None:
            self._values["region"] = region

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
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/redshift_service_account#region DataAwsRedshiftServiceAccount#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRedshiftServiceAccountConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster aws_redshift_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_identifier: builtins.str,
        node_type: builtins.str,
        allow_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        automated_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        cluster_public_key: typing.Optional[builtins.str] = None,
        cluster_revision_number: typing.Optional[builtins.str] = None,
        cluster_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        cluster_subnet_group_name: typing.Optional[builtins.str] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        cluster_version: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        endpoint: typing.Optional[builtins.str] = None,
        enhanced_vpc_routing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        logging: typing.Optional["RedshiftClusterLogging"] = None,
        master_password: typing.Optional[builtins.str] = None,
        master_username: typing.Optional[builtins.str] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
        owner_account: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_cluster_identifier: typing.Optional[builtins.str] = None,
        snapshot_copy: typing.Optional["RedshiftClusterSnapshotCopy"] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RedshiftClusterTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster aws_redshift_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_identifier RedshiftCluster#cluster_identifier}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#node_type RedshiftCluster#node_type}.
        :param allow_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#allow_version_upgrade RedshiftCluster#allow_version_upgrade}.
        :param automated_snapshot_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#automated_snapshot_retention_period RedshiftCluster#automated_snapshot_retention_period}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#availability_zone RedshiftCluster#availability_zone}.
        :param cluster_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_parameter_group_name RedshiftCluster#cluster_parameter_group_name}.
        :param cluster_public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_public_key RedshiftCluster#cluster_public_key}.
        :param cluster_revision_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_revision_number RedshiftCluster#cluster_revision_number}.
        :param cluster_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_security_groups RedshiftCluster#cluster_security_groups}.
        :param cluster_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_subnet_group_name RedshiftCluster#cluster_subnet_group_name}.
        :param cluster_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_type RedshiftCluster#cluster_type}.
        :param cluster_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_version RedshiftCluster#cluster_version}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#database_name RedshiftCluster#database_name}.
        :param elastic_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#elastic_ip RedshiftCluster#elastic_ip}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#encrypted RedshiftCluster#encrypted}.
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#endpoint RedshiftCluster#endpoint}.
        :param enhanced_vpc_routing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#enhanced_vpc_routing RedshiftCluster#enhanced_vpc_routing}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#final_snapshot_identifier RedshiftCluster#final_snapshot_identifier}.
        :param iam_roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#iam_roles RedshiftCluster#iam_roles}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#kms_key_id RedshiftCluster#kms_key_id}.
        :param logging: logging block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#logging RedshiftCluster#logging}
        :param master_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#master_password RedshiftCluster#master_password}.
        :param master_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#master_username RedshiftCluster#master_username}.
        :param number_of_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#number_of_nodes RedshiftCluster#number_of_nodes}.
        :param owner_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#owner_account RedshiftCluster#owner_account}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#port RedshiftCluster#port}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#preferred_maintenance_window RedshiftCluster#preferred_maintenance_window}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#publicly_accessible RedshiftCluster#publicly_accessible}.
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#skip_final_snapshot RedshiftCluster#skip_final_snapshot}.
        :param snapshot_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_cluster_identifier RedshiftCluster#snapshot_cluster_identifier}.
        :param snapshot_copy: snapshot_copy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_copy RedshiftCluster#snapshot_copy}
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_identifier RedshiftCluster#snapshot_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#tags RedshiftCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#tags_all RedshiftCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#timeouts RedshiftCluster#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#vpc_security_group_ids RedshiftCluster#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftClusterConfig(
            cluster_identifier=cluster_identifier,
            node_type=node_type,
            allow_version_upgrade=allow_version_upgrade,
            automated_snapshot_retention_period=automated_snapshot_retention_period,
            availability_zone=availability_zone,
            cluster_parameter_group_name=cluster_parameter_group_name,
            cluster_public_key=cluster_public_key,
            cluster_revision_number=cluster_revision_number,
            cluster_security_groups=cluster_security_groups,
            cluster_subnet_group_name=cluster_subnet_group_name,
            cluster_type=cluster_type,
            cluster_version=cluster_version,
            database_name=database_name,
            elastic_ip=elastic_ip,
            encrypted=encrypted,
            endpoint=endpoint,
            enhanced_vpc_routing=enhanced_vpc_routing,
            final_snapshot_identifier=final_snapshot_identifier,
            iam_roles=iam_roles,
            kms_key_id=kms_key_id,
            logging=logging,
            master_password=master_password,
            master_username=master_username,
            number_of_nodes=number_of_nodes,
            owner_account=owner_account,
            port=port,
            preferred_maintenance_window=preferred_maintenance_window,
            publicly_accessible=publicly_accessible,
            skip_final_snapshot=skip_final_snapshot,
            snapshot_cluster_identifier=snapshot_cluster_identifier,
            snapshot_copy=snapshot_copy,
            snapshot_identifier=snapshot_identifier,
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

    @jsii.member(jsii_name="clusterNodes")
    def cluster_nodes(self, index: builtins.str) -> "RedshiftClusterClusterNodes":
        '''
        :param index: -
        '''
        return typing.cast("RedshiftClusterClusterNodes", jsii.invoke(self, "clusterNodes", [index]))

    @jsii.member(jsii_name="putLogging")
    def put_logging(
        self,
        *,
        enable: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket_name: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#enable RedshiftCluster#enable}.
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#bucket_name RedshiftCluster#bucket_name}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#s3_key_prefix RedshiftCluster#s3_key_prefix}.
        '''
        value = RedshiftClusterLogging(
            enable=enable, bucket_name=bucket_name, s3_key_prefix=s3_key_prefix
        )

        return typing.cast(None, jsii.invoke(self, "putLogging", [value]))

    @jsii.member(jsii_name="putSnapshotCopy")
    def put_snapshot_copy(
        self,
        *,
        destination_region: builtins.str,
        grant_name: typing.Optional[builtins.str] = None,
        retention_period: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param destination_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#destination_region RedshiftCluster#destination_region}.
        :param grant_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#grant_name RedshiftCluster#grant_name}.
        :param retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#retention_period RedshiftCluster#retention_period}.
        '''
        value = RedshiftClusterSnapshotCopy(
            destination_region=destination_region,
            grant_name=grant_name,
            retention_period=retention_period,
        )

        return typing.cast(None, jsii.invoke(self, "putSnapshotCopy", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#create RedshiftCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#delete RedshiftCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#update RedshiftCluster#update}.
        '''
        value = RedshiftClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAllowVersionUpgrade")
    def reset_allow_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowVersionUpgrade", []))

    @jsii.member(jsii_name="resetAutomatedSnapshotRetentionPeriod")
    def reset_automated_snapshot_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomatedSnapshotRetentionPeriod", []))

    @jsii.member(jsii_name="resetAvailabilityZone")
    def reset_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZone", []))

    @jsii.member(jsii_name="resetClusterParameterGroupName")
    def reset_cluster_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterParameterGroupName", []))

    @jsii.member(jsii_name="resetClusterPublicKey")
    def reset_cluster_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterPublicKey", []))

    @jsii.member(jsii_name="resetClusterRevisionNumber")
    def reset_cluster_revision_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRevisionNumber", []))

    @jsii.member(jsii_name="resetClusterSecurityGroups")
    def reset_cluster_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterSecurityGroups", []))

    @jsii.member(jsii_name="resetClusterSubnetGroupName")
    def reset_cluster_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterSubnetGroupName", []))

    @jsii.member(jsii_name="resetClusterType")
    def reset_cluster_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterType", []))

    @jsii.member(jsii_name="resetClusterVersion")
    def reset_cluster_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterVersion", []))

    @jsii.member(jsii_name="resetDatabaseName")
    def reset_database_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseName", []))

    @jsii.member(jsii_name="resetElasticIp")
    def reset_elastic_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticIp", []))

    @jsii.member(jsii_name="resetEncrypted")
    def reset_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncrypted", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetEnhancedVpcRouting")
    def reset_enhanced_vpc_routing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnhancedVpcRouting", []))

    @jsii.member(jsii_name="resetFinalSnapshotIdentifier")
    def reset_final_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFinalSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetIamRoles")
    def reset_iam_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRoles", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetLogging")
    def reset_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogging", []))

    @jsii.member(jsii_name="resetMasterPassword")
    def reset_master_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterPassword", []))

    @jsii.member(jsii_name="resetMasterUsername")
    def reset_master_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterUsername", []))

    @jsii.member(jsii_name="resetNumberOfNodes")
    def reset_number_of_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfNodes", []))

    @jsii.member(jsii_name="resetOwnerAccount")
    def reset_owner_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwnerAccount", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPreferredMaintenanceWindow")
    def reset_preferred_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredMaintenanceWindow", []))

    @jsii.member(jsii_name="resetPubliclyAccessible")
    def reset_publicly_accessible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPubliclyAccessible", []))

    @jsii.member(jsii_name="resetSkipFinalSnapshot")
    def reset_skip_final_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipFinalSnapshot", []))

    @jsii.member(jsii_name="resetSnapshotClusterIdentifier")
    def reset_snapshot_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotClusterIdentifier", []))

    @jsii.member(jsii_name="resetSnapshotCopy")
    def reset_snapshot_copy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotCopy", []))

    @jsii.member(jsii_name="resetSnapshotIdentifier")
    def reset_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotIdentifier", []))

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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logging")
    def logging(self) -> "RedshiftClusterLoggingOutputReference":
        return typing.cast("RedshiftClusterLoggingOutputReference", jsii.get(self, "logging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopy")
    def snapshot_copy(self) -> "RedshiftClusterSnapshotCopyOutputReference":
        return typing.cast("RedshiftClusterSnapshotCopyOutputReference", jsii.get(self, "snapshotCopy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "RedshiftClusterTimeoutsOutputReference":
        return typing.cast("RedshiftClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowVersionUpgradeInput")
    def allow_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowVersionUpgradeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automatedSnapshotRetentionPeriodInput")
    def automated_snapshot_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automatedSnapshotRetentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterParameterGroupNameInput")
    def cluster_parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterParameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterPublicKeyInput")
    def cluster_public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterPublicKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterRevisionNumberInput")
    def cluster_revision_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterRevisionNumberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSecurityGroupsInput")
    def cluster_security_groups_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clusterSecurityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSubnetGroupNameInput")
    def cluster_subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterSubnetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterTypeInput")
    def cluster_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersionInput")
    def cluster_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticIpInput")
    def elastic_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticIpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "encryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedVpcRoutingInput")
    def enhanced_vpc_routing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enhancedVpcRoutingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotIdentifierInput")
    def final_snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "finalSnapshotIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRolesInput")
    def iam_roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "iamRolesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInput")
    def logging_input(self) -> typing.Optional["RedshiftClusterLogging"]:
        return typing.cast(typing.Optional["RedshiftClusterLogging"], jsii.get(self, "loggingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterPasswordInput")
    def master_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsernameInput")
    def master_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterUsernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeTypeInput")
    def node_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodesInput")
    def number_of_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfNodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerAccountInput")
    def owner_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerAccountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindowInput")
    def preferred_maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessibleInput")
    def publicly_accessible_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publiclyAccessibleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipFinalSnapshotInput")
    def skip_final_snapshot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipFinalSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotClusterIdentifierInput")
    def snapshot_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopyInput")
    def snapshot_copy_input(self) -> typing.Optional["RedshiftClusterSnapshotCopy"]:
        return typing.cast(typing.Optional["RedshiftClusterSnapshotCopy"], jsii.get(self, "snapshotCopyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdentifierInput")
    def snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdentifierInput"))

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
    def timeouts_input(self) -> typing.Optional["RedshiftClusterTimeouts"]:
        return typing.cast(typing.Optional["RedshiftClusterTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowVersionUpgrade")
    def allow_version_upgrade(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowVersionUpgrade"))

    @allow_version_upgrade.setter
    def allow_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automatedSnapshotRetentionPeriod")
    def automated_snapshot_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "automatedSnapshotRetentionPeriod"))

    @automated_snapshot_retention_period.setter
    def automated_snapshot_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "automatedSnapshotRetentionPeriod", value)

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
    @jsii.member(jsii_name="clusterParameterGroupName")
    def cluster_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterParameterGroupName"))

    @cluster_parameter_group_name.setter
    def cluster_parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterPublicKey")
    def cluster_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterPublicKey"))

    @cluster_public_key.setter
    def cluster_public_key(self, value: builtins.str) -> None:
        jsii.set(self, "clusterPublicKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterRevisionNumber")
    def cluster_revision_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterRevisionNumber"))

    @cluster_revision_number.setter
    def cluster_revision_number(self, value: builtins.str) -> None:
        jsii.set(self, "clusterRevisionNumber", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSecurityGroups")
    def cluster_security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clusterSecurityGroups"))

    @cluster_security_groups.setter
    def cluster_security_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "clusterSecurityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterSubnetGroupName")
    def cluster_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterSubnetGroupName"))

    @cluster_subnet_group_name.setter
    def cluster_subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterSubnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @cluster_type.setter
    def cluster_type(self, value: builtins.str) -> None:
        jsii.set(self, "clusterType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterVersion"))

    @cluster_version.setter
    def cluster_version(self, value: builtins.str) -> None:
        jsii.set(self, "clusterVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticIp"))

    @elastic_ip.setter
    def elastic_ip(self, value: builtins.str) -> None:
        jsii.set(self, "elasticIp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedVpcRouting")
    def enhanced_vpc_routing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enhancedVpcRouting"))

    @enhanced_vpc_routing.setter
    def enhanced_vpc_routing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enhancedVpcRouting", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotIdentifier")
    def final_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finalSnapshotIdentifier"))

    @final_snapshot_identifier.setter
    def final_snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "finalSnapshotIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoles")
    def iam_roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "iamRoles"))

    @iam_roles.setter
    def iam_roles(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "iamRoles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterPassword")
    def master_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterPassword"))

    @master_password.setter
    def master_password(self, value: builtins.str) -> None:
        jsii.set(self, "masterPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterUsername"))

    @master_username.setter
    def master_username(self, value: builtins.str) -> None:
        jsii.set(self, "masterUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfNodes"))

    @number_of_nodes.setter
    def number_of_nodes(self, value: jsii.Number) -> None:
        jsii.set(self, "numberOfNodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerAccount")
    def owner_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerAccount"))

    @owner_account.setter
    def owner_account(self, value: builtins.str) -> None:
        jsii.set(self, "ownerAccount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

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
    @jsii.member(jsii_name="snapshotClusterIdentifier")
    def snapshot_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotClusterIdentifier"))

    @snapshot_cluster_identifier.setter
    def snapshot_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotIdentifier"))

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotIdentifier", value)

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


class RedshiftClusterClusterNodes(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterClusterNodes",
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
    @jsii.member(jsii_name="nodeRole")
    def node_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateIpAddress")
    def private_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIpAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicIpAddress")
    def public_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicIpAddress"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_identifier": "clusterIdentifier",
        "node_type": "nodeType",
        "allow_version_upgrade": "allowVersionUpgrade",
        "automated_snapshot_retention_period": "automatedSnapshotRetentionPeriod",
        "availability_zone": "availabilityZone",
        "cluster_parameter_group_name": "clusterParameterGroupName",
        "cluster_public_key": "clusterPublicKey",
        "cluster_revision_number": "clusterRevisionNumber",
        "cluster_security_groups": "clusterSecurityGroups",
        "cluster_subnet_group_name": "clusterSubnetGroupName",
        "cluster_type": "clusterType",
        "cluster_version": "clusterVersion",
        "database_name": "databaseName",
        "elastic_ip": "elasticIp",
        "encrypted": "encrypted",
        "endpoint": "endpoint",
        "enhanced_vpc_routing": "enhancedVpcRouting",
        "final_snapshot_identifier": "finalSnapshotIdentifier",
        "iam_roles": "iamRoles",
        "kms_key_id": "kmsKeyId",
        "logging": "logging",
        "master_password": "masterPassword",
        "master_username": "masterUsername",
        "number_of_nodes": "numberOfNodes",
        "owner_account": "ownerAccount",
        "port": "port",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "publicly_accessible": "publiclyAccessible",
        "skip_final_snapshot": "skipFinalSnapshot",
        "snapshot_cluster_identifier": "snapshotClusterIdentifier",
        "snapshot_copy": "snapshotCopy",
        "snapshot_identifier": "snapshotIdentifier",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class RedshiftClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_identifier: builtins.str,
        node_type: builtins.str,
        allow_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        automated_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        cluster_public_key: typing.Optional[builtins.str] = None,
        cluster_revision_number: typing.Optional[builtins.str] = None,
        cluster_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        cluster_subnet_group_name: typing.Optional[builtins.str] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        cluster_version: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        endpoint: typing.Optional[builtins.str] = None,
        enhanced_vpc_routing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        logging: typing.Optional["RedshiftClusterLogging"] = None,
        master_password: typing.Optional[builtins.str] = None,
        master_username: typing.Optional[builtins.str] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
        owner_account: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_cluster_identifier: typing.Optional[builtins.str] = None,
        snapshot_copy: typing.Optional["RedshiftClusterSnapshotCopy"] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RedshiftClusterTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_identifier RedshiftCluster#cluster_identifier}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#node_type RedshiftCluster#node_type}.
        :param allow_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#allow_version_upgrade RedshiftCluster#allow_version_upgrade}.
        :param automated_snapshot_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#automated_snapshot_retention_period RedshiftCluster#automated_snapshot_retention_period}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#availability_zone RedshiftCluster#availability_zone}.
        :param cluster_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_parameter_group_name RedshiftCluster#cluster_parameter_group_name}.
        :param cluster_public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_public_key RedshiftCluster#cluster_public_key}.
        :param cluster_revision_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_revision_number RedshiftCluster#cluster_revision_number}.
        :param cluster_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_security_groups RedshiftCluster#cluster_security_groups}.
        :param cluster_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_subnet_group_name RedshiftCluster#cluster_subnet_group_name}.
        :param cluster_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_type RedshiftCluster#cluster_type}.
        :param cluster_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_version RedshiftCluster#cluster_version}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#database_name RedshiftCluster#database_name}.
        :param elastic_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#elastic_ip RedshiftCluster#elastic_ip}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#encrypted RedshiftCluster#encrypted}.
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#endpoint RedshiftCluster#endpoint}.
        :param enhanced_vpc_routing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#enhanced_vpc_routing RedshiftCluster#enhanced_vpc_routing}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#final_snapshot_identifier RedshiftCluster#final_snapshot_identifier}.
        :param iam_roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#iam_roles RedshiftCluster#iam_roles}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#kms_key_id RedshiftCluster#kms_key_id}.
        :param logging: logging block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#logging RedshiftCluster#logging}
        :param master_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#master_password RedshiftCluster#master_password}.
        :param master_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#master_username RedshiftCluster#master_username}.
        :param number_of_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#number_of_nodes RedshiftCluster#number_of_nodes}.
        :param owner_account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#owner_account RedshiftCluster#owner_account}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#port RedshiftCluster#port}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#preferred_maintenance_window RedshiftCluster#preferred_maintenance_window}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#publicly_accessible RedshiftCluster#publicly_accessible}.
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#skip_final_snapshot RedshiftCluster#skip_final_snapshot}.
        :param snapshot_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_cluster_identifier RedshiftCluster#snapshot_cluster_identifier}.
        :param snapshot_copy: snapshot_copy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_copy RedshiftCluster#snapshot_copy}
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_identifier RedshiftCluster#snapshot_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#tags RedshiftCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#tags_all RedshiftCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#timeouts RedshiftCluster#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#vpc_security_group_ids RedshiftCluster#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(logging, dict):
            logging = RedshiftClusterLogging(**logging)
        if isinstance(snapshot_copy, dict):
            snapshot_copy = RedshiftClusterSnapshotCopy(**snapshot_copy)
        if isinstance(timeouts, dict):
            timeouts = RedshiftClusterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
            "node_type": node_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_version_upgrade is not None:
            self._values["allow_version_upgrade"] = allow_version_upgrade
        if automated_snapshot_retention_period is not None:
            self._values["automated_snapshot_retention_period"] = automated_snapshot_retention_period
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if cluster_parameter_group_name is not None:
            self._values["cluster_parameter_group_name"] = cluster_parameter_group_name
        if cluster_public_key is not None:
            self._values["cluster_public_key"] = cluster_public_key
        if cluster_revision_number is not None:
            self._values["cluster_revision_number"] = cluster_revision_number
        if cluster_security_groups is not None:
            self._values["cluster_security_groups"] = cluster_security_groups
        if cluster_subnet_group_name is not None:
            self._values["cluster_subnet_group_name"] = cluster_subnet_group_name
        if cluster_type is not None:
            self._values["cluster_type"] = cluster_type
        if cluster_version is not None:
            self._values["cluster_version"] = cluster_version
        if database_name is not None:
            self._values["database_name"] = database_name
        if elastic_ip is not None:
            self._values["elastic_ip"] = elastic_ip
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if enhanced_vpc_routing is not None:
            self._values["enhanced_vpc_routing"] = enhanced_vpc_routing
        if final_snapshot_identifier is not None:
            self._values["final_snapshot_identifier"] = final_snapshot_identifier
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if logging is not None:
            self._values["logging"] = logging
        if master_password is not None:
            self._values["master_password"] = master_password
        if master_username is not None:
            self._values["master_username"] = master_username
        if number_of_nodes is not None:
            self._values["number_of_nodes"] = number_of_nodes
        if owner_account is not None:
            self._values["owner_account"] = owner_account
        if port is not None:
            self._values["port"] = port
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if skip_final_snapshot is not None:
            self._values["skip_final_snapshot"] = skip_final_snapshot
        if snapshot_cluster_identifier is not None:
            self._values["snapshot_cluster_identifier"] = snapshot_cluster_identifier
        if snapshot_copy is not None:
            self._values["snapshot_copy"] = snapshot_copy
        if snapshot_identifier is not None:
            self._values["snapshot_identifier"] = snapshot_identifier
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
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_identifier RedshiftCluster#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def node_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#node_type RedshiftCluster#node_type}.'''
        result = self._values.get("node_type")
        assert result is not None, "Required property 'node_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#allow_version_upgrade RedshiftCluster#allow_version_upgrade}.'''
        result = self._values.get("allow_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def automated_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#automated_snapshot_retention_period RedshiftCluster#automated_snapshot_retention_period}.'''
        result = self._values.get("automated_snapshot_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#availability_zone RedshiftCluster#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_parameter_group_name RedshiftCluster#cluster_parameter_group_name}.'''
        result = self._values.get("cluster_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_public_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_public_key RedshiftCluster#cluster_public_key}.'''
        result = self._values.get("cluster_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_revision_number(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_revision_number RedshiftCluster#cluster_revision_number}.'''
        result = self._values.get("cluster_revision_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_security_groups RedshiftCluster#cluster_security_groups}.'''
        result = self._values.get("cluster_security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cluster_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_subnet_group_name RedshiftCluster#cluster_subnet_group_name}.'''
        result = self._values.get("cluster_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_type RedshiftCluster#cluster_type}.'''
        result = self._values.get("cluster_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#cluster_version RedshiftCluster#cluster_version}.'''
        result = self._values.get("cluster_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#database_name RedshiftCluster#database_name}.'''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elastic_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#elastic_ip RedshiftCluster#elastic_ip}.'''
        result = self._values.get("elastic_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#encrypted RedshiftCluster#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#endpoint RedshiftCluster#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enhanced_vpc_routing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#enhanced_vpc_routing RedshiftCluster#enhanced_vpc_routing}.'''
        result = self._values.get("enhanced_vpc_routing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def final_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#final_snapshot_identifier RedshiftCluster#final_snapshot_identifier}.'''
        result = self._values.get("final_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#iam_roles RedshiftCluster#iam_roles}.'''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#kms_key_id RedshiftCluster#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging(self) -> typing.Optional["RedshiftClusterLogging"]:
        '''logging block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#logging RedshiftCluster#logging}
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional["RedshiftClusterLogging"], result)

    @builtins.property
    def master_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#master_password RedshiftCluster#master_password}.'''
        result = self._values.get("master_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#master_username RedshiftCluster#master_username}.'''
        result = self._values.get("master_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#number_of_nodes RedshiftCluster#number_of_nodes}.'''
        result = self._values.get("number_of_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def owner_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#owner_account RedshiftCluster#owner_account}.'''
        result = self._values.get("owner_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#port RedshiftCluster#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#preferred_maintenance_window RedshiftCluster#preferred_maintenance_window}.'''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#publicly_accessible RedshiftCluster#publicly_accessible}.'''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def skip_final_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#skip_final_snapshot RedshiftCluster#skip_final_snapshot}.'''
        result = self._values.get("skip_final_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def snapshot_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_cluster_identifier RedshiftCluster#snapshot_cluster_identifier}.'''
        result = self._values.get("snapshot_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_copy(self) -> typing.Optional["RedshiftClusterSnapshotCopy"]:
        '''snapshot_copy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_copy RedshiftCluster#snapshot_copy}
        '''
        result = self._values.get("snapshot_copy")
        return typing.cast(typing.Optional["RedshiftClusterSnapshotCopy"], result)

    @builtins.property
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#snapshot_identifier RedshiftCluster#snapshot_identifier}.'''
        result = self._values.get("snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#tags RedshiftCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#tags_all RedshiftCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["RedshiftClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#timeouts RedshiftCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["RedshiftClusterTimeouts"], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#vpc_security_group_ids RedshiftCluster#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterLogging",
    jsii_struct_bases=[],
    name_mapping={
        "enable": "enable",
        "bucket_name": "bucketName",
        "s3_key_prefix": "s3KeyPrefix",
    },
)
class RedshiftClusterLogging:
    def __init__(
        self,
        *,
        enable: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket_name: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#enable RedshiftCluster#enable}.
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#bucket_name RedshiftCluster#bucket_name}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#s3_key_prefix RedshiftCluster#s3_key_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enable": enable,
        }
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if s3_key_prefix is not None:
            self._values["s3_key_prefix"] = s3_key_prefix

    @builtins.property
    def enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#enable RedshiftCluster#enable}.'''
        result = self._values.get("enable")
        assert result is not None, "Required property 'enable' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#bucket_name RedshiftCluster#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#s3_key_prefix RedshiftCluster#s3_key_prefix}.'''
        result = self._values.get("s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftClusterLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftClusterLoggingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterLoggingOutputReference",
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

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetS3KeyPrefix")
    def reset_s3_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3KeyPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableInput")
    def enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefixInput")
    def s3_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enable")
    def enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KeyPrefix"))

    @s3_key_prefix.setter
    def s3_key_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "s3KeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RedshiftClusterLogging]:
        return typing.cast(typing.Optional[RedshiftClusterLogging], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RedshiftClusterLogging]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterSnapshotCopy",
    jsii_struct_bases=[],
    name_mapping={
        "destination_region": "destinationRegion",
        "grant_name": "grantName",
        "retention_period": "retentionPeriod",
    },
)
class RedshiftClusterSnapshotCopy:
    def __init__(
        self,
        *,
        destination_region: builtins.str,
        grant_name: typing.Optional[builtins.str] = None,
        retention_period: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param destination_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#destination_region RedshiftCluster#destination_region}.
        :param grant_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#grant_name RedshiftCluster#grant_name}.
        :param retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#retention_period RedshiftCluster#retention_period}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_region": destination_region,
        }
        if grant_name is not None:
            self._values["grant_name"] = grant_name
        if retention_period is not None:
            self._values["retention_period"] = retention_period

    @builtins.property
    def destination_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#destination_region RedshiftCluster#destination_region}.'''
        result = self._values.get("destination_region")
        assert result is not None, "Required property 'destination_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def grant_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#grant_name RedshiftCluster#grant_name}.'''
        result = self._values.get("grant_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#retention_period RedshiftCluster#retention_period}.'''
        result = self._values.get("retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftClusterSnapshotCopy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftClusterSnapshotCopyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterSnapshotCopyOutputReference",
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

    @jsii.member(jsii_name="resetGrantName")
    def reset_grant_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrantName", []))

    @jsii.member(jsii_name="resetRetentionPeriod")
    def reset_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionPeriod", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationRegionInput")
    def destination_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationRegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantNameInput")
    def grant_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "grantNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionPeriodInput")
    def retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationRegion")
    def destination_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationRegion"))

    @destination_region.setter
    def destination_region(self, value: builtins.str) -> None:
        jsii.set(self, "destinationRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantName")
    def grant_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "grantName"))

    @grant_name.setter
    def grant_name(self, value: builtins.str) -> None:
        jsii.set(self, "grantName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionPeriod"))

    @retention_period.setter
    def retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "retentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RedshiftClusterSnapshotCopy]:
        return typing.cast(typing.Optional[RedshiftClusterSnapshotCopy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RedshiftClusterSnapshotCopy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class RedshiftClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#create RedshiftCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#delete RedshiftCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#update RedshiftCluster#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#create RedshiftCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#delete RedshiftCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_cluster#update RedshiftCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftClusterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftClusterTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[RedshiftClusterTimeouts]:
        return typing.cast(typing.Optional[RedshiftClusterTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RedshiftClusterTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class RedshiftEventSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftEventSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription aws_redshift_event_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        severity: typing.Optional[builtins.str] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RedshiftEventSubscriptionTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription aws_redshift_event_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#name RedshiftEventSubscription#name}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#sns_topic_arn RedshiftEventSubscription#sns_topic_arn}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#enabled RedshiftEventSubscription#enabled}.
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#event_categories RedshiftEventSubscription#event_categories}.
        :param severity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#severity RedshiftEventSubscription#severity}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#source_ids RedshiftEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#source_type RedshiftEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#tags RedshiftEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#tags_all RedshiftEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#timeouts RedshiftEventSubscription#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftEventSubscriptionConfig(
            name=name,
            sns_topic_arn=sns_topic_arn,
            enabled=enabled,
            event_categories=event_categories,
            severity=severity,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#create RedshiftEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#delete RedshiftEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#update RedshiftEventSubscription#update}.
        '''
        value = RedshiftEventSubscriptionTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEventCategories")
    def reset_event_categories(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventCategories", []))

    @jsii.member(jsii_name="resetSeverity")
    def reset_severity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeverity", []))

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
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "RedshiftEventSubscriptionTimeoutsOutputReference":
        return typing.cast("RedshiftEventSubscriptionTimeoutsOutputReference", jsii.get(self, "timeouts"))

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
    @jsii.member(jsii_name="severityInput")
    def severity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "severityInput"))

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
    def timeouts_input(self) -> typing.Optional["RedshiftEventSubscriptionTimeouts"]:
        return typing.cast(typing.Optional["RedshiftEventSubscriptionTimeouts"], jsii.get(self, "timeoutsInput"))

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
    @jsii.member(jsii_name="severity")
    def severity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "severity"))

    @severity.setter
    def severity(self, value: builtins.str) -> None:
        jsii.set(self, "severity", value)

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
    jsii_type="@cdktf/provider-aws.redshift.RedshiftEventSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "sns_topic_arn": "snsTopicArn",
        "enabled": "enabled",
        "event_categories": "eventCategories",
        "severity": "severity",
        "source_ids": "sourceIds",
        "source_type": "sourceType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class RedshiftEventSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        severity: typing.Optional[builtins.str] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RedshiftEventSubscriptionTimeouts"] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#name RedshiftEventSubscription#name}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#sns_topic_arn RedshiftEventSubscription#sns_topic_arn}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#enabled RedshiftEventSubscription#enabled}.
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#event_categories RedshiftEventSubscription#event_categories}.
        :param severity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#severity RedshiftEventSubscription#severity}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#source_ids RedshiftEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#source_type RedshiftEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#tags RedshiftEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#tags_all RedshiftEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#timeouts RedshiftEventSubscription#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = RedshiftEventSubscriptionTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
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
        if severity is not None:
            self._values["severity"] = severity
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#name RedshiftEventSubscription#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sns_topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#sns_topic_arn RedshiftEventSubscription#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        assert result is not None, "Required property 'sns_topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#enabled RedshiftEventSubscription#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def event_categories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#event_categories RedshiftEventSubscription#event_categories}.'''
        result = self._values.get("event_categories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def severity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#severity RedshiftEventSubscription#severity}.'''
        result = self._values.get("severity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#source_ids RedshiftEventSubscription#source_ids}.'''
        result = self._values.get("source_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#source_type RedshiftEventSubscription#source_type}.'''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#tags RedshiftEventSubscription#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#tags_all RedshiftEventSubscription#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["RedshiftEventSubscriptionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#timeouts RedshiftEventSubscription#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["RedshiftEventSubscriptionTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftEventSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftEventSubscriptionTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class RedshiftEventSubscriptionTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#create RedshiftEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#delete RedshiftEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#update RedshiftEventSubscription#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#create RedshiftEventSubscription#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#delete RedshiftEventSubscription#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_event_subscription#update RedshiftEventSubscription#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftEventSubscriptionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftEventSubscriptionTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftEventSubscriptionTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[RedshiftEventSubscriptionTimeouts]:
        return typing.cast(typing.Optional[RedshiftEventSubscriptionTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RedshiftEventSubscriptionTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class RedshiftParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group aws_redshift_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["RedshiftParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group aws_redshift_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#family RedshiftParameterGroup#family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#name RedshiftParameterGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#description RedshiftParameterGroup#description}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#parameter RedshiftParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#tags RedshiftParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#tags_all RedshiftParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftParameterGroupConfig(
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
    ) -> typing.Optional[typing.List["RedshiftParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["RedshiftParameterGroupParameter"]], jsii.get(self, "parameterInput"))

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
    def parameter(self) -> typing.List["RedshiftParameterGroupParameter"]:
        return typing.cast(typing.List["RedshiftParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(self, value: typing.List["RedshiftParameterGroupParameter"]) -> None:
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
    jsii_type="@cdktf/provider-aws.redshift.RedshiftParameterGroupConfig",
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
class RedshiftParameterGroupConfig(cdktf.TerraformMetaArguments):
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
        parameter: typing.Optional[typing.Sequence["RedshiftParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#family RedshiftParameterGroup#family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#name RedshiftParameterGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#description RedshiftParameterGroup#description}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#parameter RedshiftParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#tags RedshiftParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#tags_all RedshiftParameterGroup#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#family RedshiftParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#name RedshiftParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#description RedshiftParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["RedshiftParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#parameter RedshiftParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["RedshiftParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#tags RedshiftParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#tags_all RedshiftParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class RedshiftParameterGroupParameter:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#name RedshiftParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#value RedshiftParameterGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#name RedshiftParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_parameter_group#value RedshiftParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftScheduledAction(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledAction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action aws_redshift_scheduled_action}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        iam_role: builtins.str,
        name: builtins.str,
        schedule: builtins.str,
        target_action: "RedshiftScheduledActionTargetAction",
        description: typing.Optional[builtins.str] = None,
        enable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        end_time: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action aws_redshift_scheduled_action} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param iam_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#iam_role RedshiftScheduledAction#iam_role}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#name RedshiftScheduledAction#name}.
        :param schedule: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#schedule RedshiftScheduledAction#schedule}.
        :param target_action: target_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#target_action RedshiftScheduledAction#target_action}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#description RedshiftScheduledAction#description}.
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#enable RedshiftScheduledAction#enable}.
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#end_time RedshiftScheduledAction#end_time}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#start_time RedshiftScheduledAction#start_time}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftScheduledActionConfig(
            iam_role=iam_role,
            name=name,
            schedule=schedule,
            target_action=target_action,
            description=description,
            enable=enable,
            end_time=end_time,
            start_time=start_time,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTargetAction")
    def put_target_action(
        self,
        *,
        pause_cluster: typing.Optional["RedshiftScheduledActionTargetActionPauseCluster"] = None,
        resize_cluster: typing.Optional["RedshiftScheduledActionTargetActionResizeCluster"] = None,
        resume_cluster: typing.Optional["RedshiftScheduledActionTargetActionResumeCluster"] = None,
    ) -> None:
        '''
        :param pause_cluster: pause_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#pause_cluster RedshiftScheduledAction#pause_cluster}
        :param resize_cluster: resize_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#resize_cluster RedshiftScheduledAction#resize_cluster}
        :param resume_cluster: resume_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#resume_cluster RedshiftScheduledAction#resume_cluster}
        '''
        value = RedshiftScheduledActionTargetAction(
            pause_cluster=pause_cluster,
            resize_cluster=resize_cluster,
            resume_cluster=resume_cluster,
        )

        return typing.cast(None, jsii.invoke(self, "putTargetAction", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnable")
    def reset_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnable", []))

    @jsii.member(jsii_name="resetEndTime")
    def reset_end_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndTime", []))

    @jsii.member(jsii_name="resetStartTime")
    def reset_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTime", []))

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
    @jsii.member(jsii_name="targetAction")
    def target_action(self) -> "RedshiftScheduledActionTargetActionOutputReference":
        return typing.cast("RedshiftScheduledActionTargetActionOutputReference", jsii.get(self, "targetAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableInput")
    def enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endTimeInput")
    def end_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleInput")
    def iam_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetActionInput")
    def target_action_input(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetAction"]:
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetAction"], jsii.get(self, "targetActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enable")
    def enable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endTime")
    def end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endTime"))

    @end_time.setter
    def end_time(self, value: builtins.str) -> None:
        jsii.set(self, "endTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRole")
    def iam_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRole"))

    @iam_role.setter
    def iam_role(self, value: builtins.str) -> None:
        jsii.set(self, "iamRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(self, value: builtins.str) -> None:
        jsii.set(self, "schedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        jsii.set(self, "startTime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "iam_role": "iamRole",
        "name": "name",
        "schedule": "schedule",
        "target_action": "targetAction",
        "description": "description",
        "enable": "enable",
        "end_time": "endTime",
        "start_time": "startTime",
    },
)
class RedshiftScheduledActionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        iam_role: builtins.str,
        name: builtins.str,
        schedule: builtins.str,
        target_action: "RedshiftScheduledActionTargetAction",
        description: typing.Optional[builtins.str] = None,
        enable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        end_time: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param iam_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#iam_role RedshiftScheduledAction#iam_role}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#name RedshiftScheduledAction#name}.
        :param schedule: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#schedule RedshiftScheduledAction#schedule}.
        :param target_action: target_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#target_action RedshiftScheduledAction#target_action}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#description RedshiftScheduledAction#description}.
        :param enable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#enable RedshiftScheduledAction#enable}.
        :param end_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#end_time RedshiftScheduledAction#end_time}.
        :param start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#start_time RedshiftScheduledAction#start_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(target_action, dict):
            target_action = RedshiftScheduledActionTargetAction(**target_action)
        self._values: typing.Dict[str, typing.Any] = {
            "iam_role": iam_role,
            "name": name,
            "schedule": schedule,
            "target_action": target_action,
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
        if enable is not None:
            self._values["enable"] = enable
        if end_time is not None:
            self._values["end_time"] = end_time
        if start_time is not None:
            self._values["start_time"] = start_time

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
    def iam_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#iam_role RedshiftScheduledAction#iam_role}.'''
        result = self._values.get("iam_role")
        assert result is not None, "Required property 'iam_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#name RedshiftScheduledAction#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#schedule RedshiftScheduledAction#schedule}.'''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_action(self) -> "RedshiftScheduledActionTargetAction":
        '''target_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#target_action RedshiftScheduledAction#target_action}
        '''
        result = self._values.get("target_action")
        assert result is not None, "Required property 'target_action' is missing"
        return typing.cast("RedshiftScheduledActionTargetAction", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#description RedshiftScheduledAction#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#enable RedshiftScheduledAction#enable}.'''
        result = self._values.get("enable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def end_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#end_time RedshiftScheduledAction#end_time}.'''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#start_time RedshiftScheduledAction#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftScheduledActionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetAction",
    jsii_struct_bases=[],
    name_mapping={
        "pause_cluster": "pauseCluster",
        "resize_cluster": "resizeCluster",
        "resume_cluster": "resumeCluster",
    },
)
class RedshiftScheduledActionTargetAction:
    def __init__(
        self,
        *,
        pause_cluster: typing.Optional["RedshiftScheduledActionTargetActionPauseCluster"] = None,
        resize_cluster: typing.Optional["RedshiftScheduledActionTargetActionResizeCluster"] = None,
        resume_cluster: typing.Optional["RedshiftScheduledActionTargetActionResumeCluster"] = None,
    ) -> None:
        '''
        :param pause_cluster: pause_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#pause_cluster RedshiftScheduledAction#pause_cluster}
        :param resize_cluster: resize_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#resize_cluster RedshiftScheduledAction#resize_cluster}
        :param resume_cluster: resume_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#resume_cluster RedshiftScheduledAction#resume_cluster}
        '''
        if isinstance(pause_cluster, dict):
            pause_cluster = RedshiftScheduledActionTargetActionPauseCluster(**pause_cluster)
        if isinstance(resize_cluster, dict):
            resize_cluster = RedshiftScheduledActionTargetActionResizeCluster(**resize_cluster)
        if isinstance(resume_cluster, dict):
            resume_cluster = RedshiftScheduledActionTargetActionResumeCluster(**resume_cluster)
        self._values: typing.Dict[str, typing.Any] = {}
        if pause_cluster is not None:
            self._values["pause_cluster"] = pause_cluster
        if resize_cluster is not None:
            self._values["resize_cluster"] = resize_cluster
        if resume_cluster is not None:
            self._values["resume_cluster"] = resume_cluster

    @builtins.property
    def pause_cluster(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetActionPauseCluster"]:
        '''pause_cluster block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#pause_cluster RedshiftScheduledAction#pause_cluster}
        '''
        result = self._values.get("pause_cluster")
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetActionPauseCluster"], result)

    @builtins.property
    def resize_cluster(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetActionResizeCluster"]:
        '''resize_cluster block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#resize_cluster RedshiftScheduledAction#resize_cluster}
        '''
        result = self._values.get("resize_cluster")
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetActionResizeCluster"], result)

    @builtins.property
    def resume_cluster(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetActionResumeCluster"]:
        '''resume_cluster block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#resume_cluster RedshiftScheduledAction#resume_cluster}
        '''
        result = self._values.get("resume_cluster")
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetActionResumeCluster"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftScheduledActionTargetAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftScheduledActionTargetActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionOutputReference",
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

    @jsii.member(jsii_name="putPauseCluster")
    def put_pause_cluster(self, *, cluster_identifier: builtins.str) -> None:
        '''
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.
        '''
        value = RedshiftScheduledActionTargetActionPauseCluster(
            cluster_identifier=cluster_identifier
        )

        return typing.cast(None, jsii.invoke(self, "putPauseCluster", [value]))

    @jsii.member(jsii_name="putResizeCluster")
    def put_resize_cluster(
        self,
        *,
        cluster_identifier: builtins.str,
        classic: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        node_type: typing.Optional[builtins.str] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.
        :param classic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#classic RedshiftScheduledAction#classic}.
        :param cluster_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_type RedshiftScheduledAction#cluster_type}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#node_type RedshiftScheduledAction#node_type}.
        :param number_of_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#number_of_nodes RedshiftScheduledAction#number_of_nodes}.
        '''
        value = RedshiftScheduledActionTargetActionResizeCluster(
            cluster_identifier=cluster_identifier,
            classic=classic,
            cluster_type=cluster_type,
            node_type=node_type,
            number_of_nodes=number_of_nodes,
        )

        return typing.cast(None, jsii.invoke(self, "putResizeCluster", [value]))

    @jsii.member(jsii_name="putResumeCluster")
    def put_resume_cluster(self, *, cluster_identifier: builtins.str) -> None:
        '''
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.
        '''
        value = RedshiftScheduledActionTargetActionResumeCluster(
            cluster_identifier=cluster_identifier
        )

        return typing.cast(None, jsii.invoke(self, "putResumeCluster", [value]))

    @jsii.member(jsii_name="resetPauseCluster")
    def reset_pause_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPauseCluster", []))

    @jsii.member(jsii_name="resetResizeCluster")
    def reset_resize_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResizeCluster", []))

    @jsii.member(jsii_name="resetResumeCluster")
    def reset_resume_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResumeCluster", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pauseCluster")
    def pause_cluster(
        self,
    ) -> "RedshiftScheduledActionTargetActionPauseClusterOutputReference":
        return typing.cast("RedshiftScheduledActionTargetActionPauseClusterOutputReference", jsii.get(self, "pauseCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resizeCluster")
    def resize_cluster(
        self,
    ) -> "RedshiftScheduledActionTargetActionResizeClusterOutputReference":
        return typing.cast("RedshiftScheduledActionTargetActionResizeClusterOutputReference", jsii.get(self, "resizeCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resumeCluster")
    def resume_cluster(
        self,
    ) -> "RedshiftScheduledActionTargetActionResumeClusterOutputReference":
        return typing.cast("RedshiftScheduledActionTargetActionResumeClusterOutputReference", jsii.get(self, "resumeCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pauseClusterInput")
    def pause_cluster_input(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetActionPauseCluster"]:
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetActionPauseCluster"], jsii.get(self, "pauseClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resizeClusterInput")
    def resize_cluster_input(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetActionResizeCluster"]:
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetActionResizeCluster"], jsii.get(self, "resizeClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resumeClusterInput")
    def resume_cluster_input(
        self,
    ) -> typing.Optional["RedshiftScheduledActionTargetActionResumeCluster"]:
        return typing.cast(typing.Optional["RedshiftScheduledActionTargetActionResumeCluster"], jsii.get(self, "resumeClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RedshiftScheduledActionTargetAction]:
        return typing.cast(typing.Optional[RedshiftScheduledActionTargetAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RedshiftScheduledActionTargetAction],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionPauseCluster",
    jsii_struct_bases=[],
    name_mapping={"cluster_identifier": "clusterIdentifier"},
)
class RedshiftScheduledActionTargetActionPauseCluster:
    def __init__(self, *, cluster_identifier: builtins.str) -> None:
        '''
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
        }

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftScheduledActionTargetActionPauseCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftScheduledActionTargetActionPauseClusterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionPauseClusterOutputReference",
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
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[RedshiftScheduledActionTargetActionPauseCluster]:
        return typing.cast(typing.Optional[RedshiftScheduledActionTargetActionPauseCluster], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RedshiftScheduledActionTargetActionPauseCluster],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionResizeCluster",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_identifier": "clusterIdentifier",
        "classic": "classic",
        "cluster_type": "clusterType",
        "node_type": "nodeType",
        "number_of_nodes": "numberOfNodes",
    },
)
class RedshiftScheduledActionTargetActionResizeCluster:
    def __init__(
        self,
        *,
        cluster_identifier: builtins.str,
        classic: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        node_type: typing.Optional[builtins.str] = None,
        number_of_nodes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.
        :param classic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#classic RedshiftScheduledAction#classic}.
        :param cluster_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_type RedshiftScheduledAction#cluster_type}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#node_type RedshiftScheduledAction#node_type}.
        :param number_of_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#number_of_nodes RedshiftScheduledAction#number_of_nodes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
        }
        if classic is not None:
            self._values["classic"] = classic
        if cluster_type is not None:
            self._values["cluster_type"] = cluster_type
        if node_type is not None:
            self._values["node_type"] = node_type
        if number_of_nodes is not None:
            self._values["number_of_nodes"] = number_of_nodes

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def classic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#classic RedshiftScheduledAction#classic}.'''
        result = self._values.get("classic")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cluster_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_type RedshiftScheduledAction#cluster_type}.'''
        result = self._values.get("cluster_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#node_type RedshiftScheduledAction#node_type}.'''
        result = self._values.get("node_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#number_of_nodes RedshiftScheduledAction#number_of_nodes}.'''
        result = self._values.get("number_of_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftScheduledActionTargetActionResizeCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftScheduledActionTargetActionResizeClusterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionResizeClusterOutputReference",
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

    @jsii.member(jsii_name="resetClassic")
    def reset_classic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClassic", []))

    @jsii.member(jsii_name="resetClusterType")
    def reset_cluster_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterType", []))

    @jsii.member(jsii_name="resetNodeType")
    def reset_node_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeType", []))

    @jsii.member(jsii_name="resetNumberOfNodes")
    def reset_number_of_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfNodes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="classicInput")
    def classic_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "classicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterTypeInput")
    def cluster_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeTypeInput")
    def node_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodesInput")
    def number_of_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfNodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="classic")
    def classic(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "classic"))

    @classic.setter
    def classic(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "classic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @cluster_type.setter
    def cluster_type(self, value: builtins.str) -> None:
        jsii.set(self, "clusterType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfNodes"))

    @number_of_nodes.setter
    def number_of_nodes(self, value: jsii.Number) -> None:
        jsii.set(self, "numberOfNodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[RedshiftScheduledActionTargetActionResizeCluster]:
        return typing.cast(typing.Optional[RedshiftScheduledActionTargetActionResizeCluster], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RedshiftScheduledActionTargetActionResizeCluster],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionResumeCluster",
    jsii_struct_bases=[],
    name_mapping={"cluster_identifier": "clusterIdentifier"},
)
class RedshiftScheduledActionTargetActionResumeCluster:
    def __init__(self, *, cluster_identifier: builtins.str) -> None:
        '''
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
        }

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_scheduled_action#cluster_identifier RedshiftScheduledAction#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftScheduledActionTargetActionResumeCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftScheduledActionTargetActionResumeClusterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftScheduledActionTargetActionResumeClusterOutputReference",
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
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[RedshiftScheduledActionTargetActionResumeCluster]:
        return typing.cast(typing.Optional[RedshiftScheduledActionTargetActionResumeCluster], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RedshiftScheduledActionTargetActionResumeCluster],
    ) -> None:
        jsii.set(self, "internalValue", value)


class RedshiftSecurityGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSecurityGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group aws_redshift_security_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ingress: typing.Sequence["RedshiftSecurityGroupIngress"],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group aws_redshift_security_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ingress: ingress block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#ingress RedshiftSecurityGroup#ingress}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#name RedshiftSecurityGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#description RedshiftSecurityGroup#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftSecurityGroupConfig(
            ingress=ingress,
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingressInput")
    def ingress_input(
        self,
    ) -> typing.Optional[typing.List["RedshiftSecurityGroupIngress"]]:
        return typing.cast(typing.Optional[typing.List["RedshiftSecurityGroupIngress"]], jsii.get(self, "ingressInput"))

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
    @jsii.member(jsii_name="ingress")
    def ingress(self) -> typing.List["RedshiftSecurityGroupIngress"]:
        return typing.cast(typing.List["RedshiftSecurityGroupIngress"], jsii.get(self, "ingress"))

    @ingress.setter
    def ingress(self, value: typing.List["RedshiftSecurityGroupIngress"]) -> None:
        jsii.set(self, "ingress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSecurityGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "ingress": "ingress",
        "name": "name",
        "description": "description",
    },
)
class RedshiftSecurityGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        ingress: typing.Sequence["RedshiftSecurityGroupIngress"],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param ingress: ingress block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#ingress RedshiftSecurityGroup#ingress}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#name RedshiftSecurityGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#description RedshiftSecurityGroup#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "ingress": ingress,
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
    def ingress(self) -> typing.List["RedshiftSecurityGroupIngress"]:
        '''ingress block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#ingress RedshiftSecurityGroup#ingress}
        '''
        result = self._values.get("ingress")
        assert result is not None, "Required property 'ingress' is missing"
        return typing.cast(typing.List["RedshiftSecurityGroupIngress"], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#name RedshiftSecurityGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#description RedshiftSecurityGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftSecurityGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSecurityGroupIngress",
    jsii_struct_bases=[],
    name_mapping={
        "cidr": "cidr",
        "security_group_name": "securityGroupName",
        "security_group_owner_id": "securityGroupOwnerId",
    },
)
class RedshiftSecurityGroupIngress:
    def __init__(
        self,
        *,
        cidr: typing.Optional[builtins.str] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        security_group_owner_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#cidr RedshiftSecurityGroup#cidr}.
        :param security_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#security_group_name RedshiftSecurityGroup#security_group_name}.
        :param security_group_owner_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#security_group_owner_id RedshiftSecurityGroup#security_group_owner_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cidr is not None:
            self._values["cidr"] = cidr
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if security_group_owner_id is not None:
            self._values["security_group_owner_id"] = security_group_owner_id

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#cidr RedshiftSecurityGroup#cidr}.'''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#security_group_name RedshiftSecurityGroup#security_group_name}.'''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_owner_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_security_group#security_group_owner_id RedshiftSecurityGroup#security_group_owner_id}.'''
        result = self._values.get("security_group_owner_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftSecurityGroupIngress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftSnapshotCopyGrant(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSnapshotCopyGrant",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant aws_redshift_snapshot_copy_grant}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        snapshot_copy_grant_name: builtins.str,
        kms_key_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant aws_redshift_snapshot_copy_grant} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param snapshot_copy_grant_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#snapshot_copy_grant_name RedshiftSnapshotCopyGrant#snapshot_copy_grant_name}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#kms_key_id RedshiftSnapshotCopyGrant#kms_key_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#tags RedshiftSnapshotCopyGrant#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#tags_all RedshiftSnapshotCopyGrant#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftSnapshotCopyGrantConfig(
            snapshot_copy_grant_name=snapshot_copy_grant_name,
            kms_key_id=kms_key_id,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

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
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopyGrantNameInput")
    def snapshot_copy_grant_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotCopyGrantNameInput"))

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
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCopyGrantName")
    def snapshot_copy_grant_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotCopyGrantName"))

    @snapshot_copy_grant_name.setter
    def snapshot_copy_grant_name(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotCopyGrantName", value)

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
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSnapshotCopyGrantConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "snapshot_copy_grant_name": "snapshotCopyGrantName",
        "kms_key_id": "kmsKeyId",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class RedshiftSnapshotCopyGrantConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        snapshot_copy_grant_name: builtins.str,
        kms_key_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param snapshot_copy_grant_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#snapshot_copy_grant_name RedshiftSnapshotCopyGrant#snapshot_copy_grant_name}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#kms_key_id RedshiftSnapshotCopyGrant#kms_key_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#tags RedshiftSnapshotCopyGrant#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#tags_all RedshiftSnapshotCopyGrant#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "snapshot_copy_grant_name": snapshot_copy_grant_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
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
    def snapshot_copy_grant_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#snapshot_copy_grant_name RedshiftSnapshotCopyGrant#snapshot_copy_grant_name}.'''
        result = self._values.get("snapshot_copy_grant_name")
        assert result is not None, "Required property 'snapshot_copy_grant_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#kms_key_id RedshiftSnapshotCopyGrant#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#tags RedshiftSnapshotCopyGrant#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_copy_grant#tags_all RedshiftSnapshotCopyGrant#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftSnapshotCopyGrantConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftSnapshotSchedule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSnapshotSchedule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule aws_redshift_snapshot_schedule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        definitions: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule aws_redshift_snapshot_schedule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param definitions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#definitions RedshiftSnapshotSchedule#definitions}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#description RedshiftSnapshotSchedule#description}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#force_destroy RedshiftSnapshotSchedule#force_destroy}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#identifier RedshiftSnapshotSchedule#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#identifier_prefix RedshiftSnapshotSchedule#identifier_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#tags RedshiftSnapshotSchedule#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#tags_all RedshiftSnapshotSchedule#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftSnapshotScheduleConfig(
            definitions=definitions,
            description=description,
            force_destroy=force_destroy,
            identifier=identifier,
            identifier_prefix=identifier_prefix,
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

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetIdentifier")
    def reset_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifier", []))

    @jsii.member(jsii_name="resetIdentifierPrefix")
    def reset_identifier_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifierPrefix", []))

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
    @jsii.member(jsii_name="definitionsInput")
    def definitions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "definitionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierPrefixInput")
    def identifier_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierPrefixInput"))

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
    @jsii.member(jsii_name="definitions")
    def definitions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "definitions"))

    @definitions.setter
    def definitions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "definitions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDestroy", value)

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


class RedshiftSnapshotScheduleAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSnapshotScheduleAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association aws_redshift_snapshot_schedule_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_identifier: builtins.str,
        schedule_identifier: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association aws_redshift_snapshot_schedule_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association#cluster_identifier RedshiftSnapshotScheduleAssociation#cluster_identifier}.
        :param schedule_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association#schedule_identifier RedshiftSnapshotScheduleAssociation#schedule_identifier}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftSnapshotScheduleAssociationConfig(
            cluster_identifier=cluster_identifier,
            schedule_identifier=schedule_identifier,
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
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleIdentifierInput")
    def schedule_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduleIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleIdentifier")
    def schedule_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheduleIdentifier"))

    @schedule_identifier.setter
    def schedule_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "scheduleIdentifier", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSnapshotScheduleAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_identifier": "clusterIdentifier",
        "schedule_identifier": "scheduleIdentifier",
    },
)
class RedshiftSnapshotScheduleAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_identifier: builtins.str,
        schedule_identifier: builtins.str,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association#cluster_identifier RedshiftSnapshotScheduleAssociation#cluster_identifier}.
        :param schedule_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association#schedule_identifier RedshiftSnapshotScheduleAssociation#schedule_identifier}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
            "schedule_identifier": schedule_identifier,
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
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association#cluster_identifier RedshiftSnapshotScheduleAssociation#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule_association#schedule_identifier RedshiftSnapshotScheduleAssociation#schedule_identifier}.'''
        result = self._values.get("schedule_identifier")
        assert result is not None, "Required property 'schedule_identifier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftSnapshotScheduleAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSnapshotScheduleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "definitions": "definitions",
        "description": "description",
        "force_destroy": "forceDestroy",
        "identifier": "identifier",
        "identifier_prefix": "identifierPrefix",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class RedshiftSnapshotScheduleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        definitions: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param definitions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#definitions RedshiftSnapshotSchedule#definitions}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#description RedshiftSnapshotSchedule#description}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#force_destroy RedshiftSnapshotSchedule#force_destroy}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#identifier RedshiftSnapshotSchedule#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#identifier_prefix RedshiftSnapshotSchedule#identifier_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#tags RedshiftSnapshotSchedule#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#tags_all RedshiftSnapshotSchedule#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "definitions": definitions,
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
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if identifier is not None:
            self._values["identifier"] = identifier
        if identifier_prefix is not None:
            self._values["identifier_prefix"] = identifier_prefix
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
    def definitions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#definitions RedshiftSnapshotSchedule#definitions}.'''
        result = self._values.get("definitions")
        assert result is not None, "Required property 'definitions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#description RedshiftSnapshotSchedule#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#force_destroy RedshiftSnapshotSchedule#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#identifier RedshiftSnapshotSchedule#identifier}.'''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#identifier_prefix RedshiftSnapshotSchedule#identifier_prefix}.'''
        result = self._values.get("identifier_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#tags RedshiftSnapshotSchedule#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_snapshot_schedule#tags_all RedshiftSnapshotSchedule#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftSnapshotScheduleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftSubnetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group aws_redshift_subnet_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group aws_redshift_subnet_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#name RedshiftSubnetGroup#name}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#subnet_ids RedshiftSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#description RedshiftSubnetGroup#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#tags RedshiftSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#tags_all RedshiftSubnetGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RedshiftSubnetGroupConfig(
            name=name,
            subnet_ids=subnet_ids,
            description=description,
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
    jsii_type="@cdktf/provider-aws.redshift.RedshiftSubnetGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "subnet_ids": "subnetIds",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class RedshiftSubnetGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Redshift.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#name RedshiftSubnetGroup#name}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#subnet_ids RedshiftSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#description RedshiftSubnetGroup#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#tags RedshiftSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#tags_all RedshiftSubnetGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#name RedshiftSubnetGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#subnet_ids RedshiftSubnetGroup#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#description RedshiftSubnetGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#tags RedshiftSubnetGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/redshift_subnet_group#tags_all RedshiftSubnetGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsRedshiftCluster",
    "DataAwsRedshiftClusterConfig",
    "DataAwsRedshiftOrderableCluster",
    "DataAwsRedshiftOrderableClusterConfig",
    "DataAwsRedshiftServiceAccount",
    "DataAwsRedshiftServiceAccountConfig",
    "RedshiftCluster",
    "RedshiftClusterClusterNodes",
    "RedshiftClusterConfig",
    "RedshiftClusterLogging",
    "RedshiftClusterLoggingOutputReference",
    "RedshiftClusterSnapshotCopy",
    "RedshiftClusterSnapshotCopyOutputReference",
    "RedshiftClusterTimeouts",
    "RedshiftClusterTimeoutsOutputReference",
    "RedshiftEventSubscription",
    "RedshiftEventSubscriptionConfig",
    "RedshiftEventSubscriptionTimeouts",
    "RedshiftEventSubscriptionTimeoutsOutputReference",
    "RedshiftParameterGroup",
    "RedshiftParameterGroupConfig",
    "RedshiftParameterGroupParameter",
    "RedshiftScheduledAction",
    "RedshiftScheduledActionConfig",
    "RedshiftScheduledActionTargetAction",
    "RedshiftScheduledActionTargetActionOutputReference",
    "RedshiftScheduledActionTargetActionPauseCluster",
    "RedshiftScheduledActionTargetActionPauseClusterOutputReference",
    "RedshiftScheduledActionTargetActionResizeCluster",
    "RedshiftScheduledActionTargetActionResizeClusterOutputReference",
    "RedshiftScheduledActionTargetActionResumeCluster",
    "RedshiftScheduledActionTargetActionResumeClusterOutputReference",
    "RedshiftSecurityGroup",
    "RedshiftSecurityGroupConfig",
    "RedshiftSecurityGroupIngress",
    "RedshiftSnapshotCopyGrant",
    "RedshiftSnapshotCopyGrantConfig",
    "RedshiftSnapshotSchedule",
    "RedshiftSnapshotScheduleAssociation",
    "RedshiftSnapshotScheduleAssociationConfig",
    "RedshiftSnapshotScheduleConfig",
    "RedshiftSubnetGroup",
    "RedshiftSubnetGroupConfig",
]

publication.publish()
