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


class DataAwsElasticacheCluster(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster aws_elasticache_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster aws_elasticache_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster#cluster_id DataAwsElasticacheCluster#cluster_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster#tags DataAwsElasticacheCluster#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsElasticacheClusterConfig(
            cluster_id=cluster_id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="cacheNodes")
    def cache_nodes(self, index: builtins.str) -> "DataAwsElasticacheClusterCacheNodes":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsElasticacheClusterCacheNodes", jsii.invoke(self, "cacheNodes", [index]))

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterAddress")
    def cluster_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationEndpoint")
    def configuration_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationEndpoint"))

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
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTopicArn")
    def notification_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationTopicArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numCacheNodes")
    def num_cache_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCacheNodes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupId")
    def replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNames")
    def security_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupNames"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotRetentionLimit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        jsii.set(self, "clusterId", value)

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


class DataAwsElasticacheClusterCacheNodes(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheClusterCacheNodes",
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
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_id": "clusterId",
        "tags": "tags",
    },
)
class DataAwsElasticacheClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster#cluster_id DataAwsElasticacheCluster#cluster_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster#tags DataAwsElasticacheCluster#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
    def cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster#cluster_id DataAwsElasticacheCluster#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_cluster#tags DataAwsElasticacheCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticacheClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsElasticacheReplicationGroup(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheReplicationGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/elasticache_replication_group aws_elasticache_replication_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        replication_group_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/elasticache_replication_group aws_elasticache_replication_group} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_replication_group#replication_group_id DataAwsElasticacheReplicationGroup#replication_group_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsElasticacheReplicationGroupConfig(
            replication_group_id=replication_group_id,
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
    @jsii.member(jsii_name="authTokenEnabled")
    def auth_token_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "authTokenEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticFailoverEnabled")
    def automatic_failover_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "automaticFailoverEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationEndpointAddress")
    def configuration_endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberClusters")
    def member_clusters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "memberClusters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAzEnabled")
    def multi_az_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "multiAzEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberCacheClusters")
    def number_cache_clusters(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberCacheClusters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryEndpointAddress")
    def primary_endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readerEndpointAddress")
    def reader_endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readerEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupDescription")
    def replication_group_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationGroupDescription"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotRetentionLimit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupIdInput")
    def replication_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupId")
    def replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationGroupId"))

    @replication_group_id.setter
    def replication_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationGroupId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheReplicationGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "replication_group_id": "replicationGroupId",
    },
)
class DataAwsElasticacheReplicationGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        replication_group_id: builtins.str,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_replication_group#replication_group_id DataAwsElasticacheReplicationGroup#replication_group_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "replication_group_id": replication_group_id,
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
    def replication_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_replication_group#replication_group_id DataAwsElasticacheReplicationGroup#replication_group_id}.'''
        result = self._values.get("replication_group_id")
        assert result is not None, "Required property 'replication_group_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticacheReplicationGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsElasticacheUser(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user aws_elasticache_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user_id: builtins.str,
        access_string: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        no_password_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user aws_elasticache_user} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#user_id DataAwsElasticacheUser#user_id}.
        :param access_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#access_string DataAwsElasticacheUser#access_string}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#engine DataAwsElasticacheUser#engine}.
        :param no_password_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#no_password_required DataAwsElasticacheUser#no_password_required}.
        :param passwords: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#passwords DataAwsElasticacheUser#passwords}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#user_name DataAwsElasticacheUser#user_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsElasticacheUserConfig(
            user_id=user_id,
            access_string=access_string,
            engine=engine,
            no_password_required=no_password_required,
            passwords=passwords,
            user_name=user_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccessString")
    def reset_access_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessString", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetNoPasswordRequired")
    def reset_no_password_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoPasswordRequired", []))

    @jsii.member(jsii_name="resetPasswords")
    def reset_passwords(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswords", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

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
    @jsii.member(jsii_name="accessStringInput")
    def access_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noPasswordRequiredInput")
    def no_password_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noPasswordRequiredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordsInput")
    def passwords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "passwordsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessString")
    def access_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessString"))

    @access_string.setter
    def access_string(self, value: builtins.str) -> None:
        jsii.set(self, "accessString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noPasswordRequired")
    def no_password_required(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noPasswordRequired"))

    @no_password_required.setter
    def no_password_required(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "noPasswordRequired", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwords")
    def passwords(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passwords"))

    @passwords.setter
    def passwords(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "passwords", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.DataAwsElasticacheUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user_id": "userId",
        "access_string": "accessString",
        "engine": "engine",
        "no_password_required": "noPasswordRequired",
        "passwords": "passwords",
        "user_name": "userName",
    },
)
class DataAwsElasticacheUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user_id: builtins.str,
        access_string: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        no_password_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#user_id DataAwsElasticacheUser#user_id}.
        :param access_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#access_string DataAwsElasticacheUser#access_string}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#engine DataAwsElasticacheUser#engine}.
        :param no_password_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#no_password_required DataAwsElasticacheUser#no_password_required}.
        :param passwords: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#passwords DataAwsElasticacheUser#passwords}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#user_name DataAwsElasticacheUser#user_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user_id": user_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if access_string is not None:
            self._values["access_string"] = access_string
        if engine is not None:
            self._values["engine"] = engine
        if no_password_required is not None:
            self._values["no_password_required"] = no_password_required
        if passwords is not None:
            self._values["passwords"] = passwords
        if user_name is not None:
            self._values["user_name"] = user_name

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
    def user_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#user_id DataAwsElasticacheUser#user_id}.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_string(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#access_string DataAwsElasticacheUser#access_string}.'''
        result = self._values.get("access_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#engine DataAwsElasticacheUser#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_password_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#no_password_required DataAwsElasticacheUser#no_password_required}.'''
        result = self._values.get("no_password_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def passwords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#passwords DataAwsElasticacheUser#passwords}.'''
        result = self._values.get("passwords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/elasticache_user#user_name DataAwsElasticacheUser#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsElasticacheUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster aws_elasticache_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_id: builtins.str,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        az_mode: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        node_type: typing.Optional[builtins.str] = None,
        notification_topic_arn: typing.Optional[builtins.str] = None,
        num_cache_nodes: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        replication_group_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster aws_elasticache_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#cluster_id ElasticacheCluster#cluster_id}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#apply_immediately ElasticacheCluster#apply_immediately}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#availability_zone ElasticacheCluster#availability_zone}.
        :param az_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#az_mode ElasticacheCluster#az_mode}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#engine ElasticacheCluster#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#engine_version ElasticacheCluster#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#final_snapshot_identifier ElasticacheCluster#final_snapshot_identifier}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#maintenance_window ElasticacheCluster#maintenance_window}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#node_type ElasticacheCluster#node_type}.
        :param notification_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#notification_topic_arn ElasticacheCluster#notification_topic_arn}.
        :param num_cache_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#num_cache_nodes ElasticacheCluster#num_cache_nodes}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#parameter_group_name ElasticacheCluster#parameter_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#port ElasticacheCluster#port}.
        :param preferred_availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#preferred_availability_zones ElasticacheCluster#preferred_availability_zones}.
        :param replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#replication_group_id ElasticacheCluster#replication_group_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#security_group_ids ElasticacheCluster#security_group_ids}.
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#security_group_names ElasticacheCluster#security_group_names}.
        :param snapshot_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_arns ElasticacheCluster#snapshot_arns}.
        :param snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_name ElasticacheCluster#snapshot_name}.
        :param snapshot_retention_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_retention_limit ElasticacheCluster#snapshot_retention_limit}.
        :param snapshot_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_window ElasticacheCluster#snapshot_window}.
        :param subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#subnet_group_name ElasticacheCluster#subnet_group_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#tags ElasticacheCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#tags_all ElasticacheCluster#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheClusterConfig(
            cluster_id=cluster_id,
            apply_immediately=apply_immediately,
            availability_zone=availability_zone,
            az_mode=az_mode,
            engine=engine,
            engine_version=engine_version,
            final_snapshot_identifier=final_snapshot_identifier,
            maintenance_window=maintenance_window,
            node_type=node_type,
            notification_topic_arn=notification_topic_arn,
            num_cache_nodes=num_cache_nodes,
            parameter_group_name=parameter_group_name,
            port=port,
            preferred_availability_zones=preferred_availability_zones,
            replication_group_id=replication_group_id,
            security_group_ids=security_group_ids,
            security_group_names=security_group_names,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            subnet_group_name=subnet_group_name,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="cacheNodes")
    def cache_nodes(self, index: builtins.str) -> "ElasticacheClusterCacheNodes":
        '''
        :param index: -
        '''
        return typing.cast("ElasticacheClusterCacheNodes", jsii.invoke(self, "cacheNodes", [index]))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAvailabilityZone")
    def reset_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZone", []))

    @jsii.member(jsii_name="resetAzMode")
    def reset_az_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzMode", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetFinalSnapshotIdentifier")
    def reset_final_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFinalSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetNodeType")
    def reset_node_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeType", []))

    @jsii.member(jsii_name="resetNotificationTopicArn")
    def reset_notification_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationTopicArn", []))

    @jsii.member(jsii_name="resetNumCacheNodes")
    def reset_num_cache_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumCacheNodes", []))

    @jsii.member(jsii_name="resetParameterGroupName")
    def reset_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterGroupName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPreferredAvailabilityZones")
    def reset_preferred_availability_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredAvailabilityZones", []))

    @jsii.member(jsii_name="resetReplicationGroupId")
    def reset_replication_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationGroupId", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSecurityGroupNames")
    def reset_security_group_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupNames", []))

    @jsii.member(jsii_name="resetSnapshotArns")
    def reset_snapshot_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotArns", []))

    @jsii.member(jsii_name="resetSnapshotName")
    def reset_snapshot_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotName", []))

    @jsii.member(jsii_name="resetSnapshotRetentionLimit")
    def reset_snapshot_retention_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotRetentionLimit", []))

    @jsii.member(jsii_name="resetSnapshotWindow")
    def reset_snapshot_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotWindow", []))

    @jsii.member(jsii_name="resetSubnetGroupName")
    def reset_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetGroupName", []))

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
    @jsii.member(jsii_name="clusterAddress")
    def cluster_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationEndpoint")
    def configuration_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionActual")
    def engine_version_actual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersionActual"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediatelyInput")
    def apply_immediately_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "applyImmediatelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="azModeInput")
    def az_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

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
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeTypeInput")
    def node_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTopicArnInput")
    def notification_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numCacheNodesInput")
    def num_cache_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numCacheNodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupNameInput")
    def parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredAvailabilityZonesInput")
    def preferred_availability_zones_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredAvailabilityZonesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupIdInput")
    def replication_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNamesInput")
    def security_group_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArnsInput")
    def snapshot_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "snapshotArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotNameInput")
    def snapshot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimitInput")
    def snapshot_retention_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "snapshotRetentionLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindowInput")
    def snapshot_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupNameInput")
    def subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetGroupNameInput"))

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
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="azMode")
    def az_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azMode"))

    @az_mode.setter
    def az_mode(self, value: builtins.str) -> None:
        jsii.set(self, "azMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        jsii.set(self, "clusterId", value)

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
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindow"))

    @maintenance_window.setter
    def maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTopicArn")
    def notification_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationTopicArn"))

    @notification_topic_arn.setter
    def notification_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "notificationTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numCacheNodes")
    def num_cache_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCacheNodes"))

    @num_cache_nodes.setter
    def num_cache_nodes(self, value: jsii.Number) -> None:
        jsii.set(self, "numCacheNodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @parameter_group_name.setter
    def parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredAvailabilityZones")
    def preferred_availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredAvailabilityZones"))

    @preferred_availability_zones.setter
    def preferred_availability_zones(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredAvailabilityZones", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupId")
    def replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationGroupId"))

    @replication_group_id.setter
    def replication_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNames")
    def security_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupNames"))

    @security_group_names.setter
    def security_group_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArns")
    def snapshot_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "snapshotArns"))

    @snapshot_arns.setter
    def snapshot_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "snapshotArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotName")
    def snapshot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotName"))

    @snapshot_name.setter
    def snapshot_name(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotRetentionLimit"))

    @snapshot_retention_limit.setter
    def snapshot_retention_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "snapshotRetentionLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotWindow"))

    @snapshot_window.setter
    def snapshot_window(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetGroupName"))

    @subnet_group_name.setter
    def subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "subnetGroupName", value)

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


class ElasticacheClusterCacheNodes(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheClusterCacheNodes",
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
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_id": "clusterId",
        "apply_immediately": "applyImmediately",
        "availability_zone": "availabilityZone",
        "az_mode": "azMode",
        "engine": "engine",
        "engine_version": "engineVersion",
        "final_snapshot_identifier": "finalSnapshotIdentifier",
        "maintenance_window": "maintenanceWindow",
        "node_type": "nodeType",
        "notification_topic_arn": "notificationTopicArn",
        "num_cache_nodes": "numCacheNodes",
        "parameter_group_name": "parameterGroupName",
        "port": "port",
        "preferred_availability_zones": "preferredAvailabilityZones",
        "replication_group_id": "replicationGroupId",
        "security_group_ids": "securityGroupIds",
        "security_group_names": "securityGroupNames",
        "snapshot_arns": "snapshotArns",
        "snapshot_name": "snapshotName",
        "snapshot_retention_limit": "snapshotRetentionLimit",
        "snapshot_window": "snapshotWindow",
        "subnet_group_name": "subnetGroupName",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ElasticacheClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_id: builtins.str,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        az_mode: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        node_type: typing.Optional[builtins.str] = None,
        notification_topic_arn: typing.Optional[builtins.str] = None,
        num_cache_nodes: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        replication_group_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#cluster_id ElasticacheCluster#cluster_id}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#apply_immediately ElasticacheCluster#apply_immediately}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#availability_zone ElasticacheCluster#availability_zone}.
        :param az_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#az_mode ElasticacheCluster#az_mode}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#engine ElasticacheCluster#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#engine_version ElasticacheCluster#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#final_snapshot_identifier ElasticacheCluster#final_snapshot_identifier}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#maintenance_window ElasticacheCluster#maintenance_window}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#node_type ElasticacheCluster#node_type}.
        :param notification_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#notification_topic_arn ElasticacheCluster#notification_topic_arn}.
        :param num_cache_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#num_cache_nodes ElasticacheCluster#num_cache_nodes}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#parameter_group_name ElasticacheCluster#parameter_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#port ElasticacheCluster#port}.
        :param preferred_availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#preferred_availability_zones ElasticacheCluster#preferred_availability_zones}.
        :param replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#replication_group_id ElasticacheCluster#replication_group_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#security_group_ids ElasticacheCluster#security_group_ids}.
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#security_group_names ElasticacheCluster#security_group_names}.
        :param snapshot_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_arns ElasticacheCluster#snapshot_arns}.
        :param snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_name ElasticacheCluster#snapshot_name}.
        :param snapshot_retention_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_retention_limit ElasticacheCluster#snapshot_retention_limit}.
        :param snapshot_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_window ElasticacheCluster#snapshot_window}.
        :param subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#subnet_group_name ElasticacheCluster#subnet_group_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#tags ElasticacheCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#tags_all ElasticacheCluster#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
        if apply_immediately is not None:
            self._values["apply_immediately"] = apply_immediately
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if az_mode is not None:
            self._values["az_mode"] = az_mode
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_identifier is not None:
            self._values["final_snapshot_identifier"] = final_snapshot_identifier
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if node_type is not None:
            self._values["node_type"] = node_type
        if notification_topic_arn is not None:
            self._values["notification_topic_arn"] = notification_topic_arn
        if num_cache_nodes is not None:
            self._values["num_cache_nodes"] = num_cache_nodes
        if parameter_group_name is not None:
            self._values["parameter_group_name"] = parameter_group_name
        if port is not None:
            self._values["port"] = port
        if preferred_availability_zones is not None:
            self._values["preferred_availability_zones"] = preferred_availability_zones
        if replication_group_id is not None:
            self._values["replication_group_id"] = replication_group_id
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if security_group_names is not None:
            self._values["security_group_names"] = security_group_names
        if snapshot_arns is not None:
            self._values["snapshot_arns"] = snapshot_arns
        if snapshot_name is not None:
            self._values["snapshot_name"] = snapshot_name
        if snapshot_retention_limit is not None:
            self._values["snapshot_retention_limit"] = snapshot_retention_limit
        if snapshot_window is not None:
            self._values["snapshot_window"] = snapshot_window
        if subnet_group_name is not None:
            self._values["subnet_group_name"] = subnet_group_name
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
    def cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#cluster_id ElasticacheCluster#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#apply_immediately ElasticacheCluster#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#availability_zone ElasticacheCluster#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def az_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#az_mode ElasticacheCluster#az_mode}.'''
        result = self._values.get("az_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#engine ElasticacheCluster#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#engine_version ElasticacheCluster#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#final_snapshot_identifier ElasticacheCluster#final_snapshot_identifier}.'''
        result = self._values.get("final_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#maintenance_window ElasticacheCluster#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#node_type ElasticacheCluster#node_type}.'''
        result = self._values.get("node_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#notification_topic_arn ElasticacheCluster#notification_topic_arn}.'''
        result = self._values.get("notification_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_cache_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#num_cache_nodes ElasticacheCluster#num_cache_nodes}.'''
        result = self._values.get("num_cache_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#parameter_group_name ElasticacheCluster#parameter_group_name}.'''
        result = self._values.get("parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#port ElasticacheCluster#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_availability_zones(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#preferred_availability_zones ElasticacheCluster#preferred_availability_zones}.'''
        result = self._values.get("preferred_availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def replication_group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#replication_group_id ElasticacheCluster#replication_group_id}.'''
        result = self._values.get("replication_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#security_group_ids ElasticacheCluster#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_group_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#security_group_names ElasticacheCluster#security_group_names}.'''
        result = self._values.get("security_group_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_arns ElasticacheCluster#snapshot_arns}.'''
        result = self._values.get("snapshot_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_name ElasticacheCluster#snapshot_name}.'''
        result = self._values.get("snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_retention_limit ElasticacheCluster#snapshot_retention_limit}.'''
        result = self._values.get("snapshot_retention_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snapshot_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#snapshot_window ElasticacheCluster#snapshot_window}.'''
        result = self._values.get("snapshot_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#subnet_group_name ElasticacheCluster#subnet_group_name}.'''
        result = self._values.get("subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#tags ElasticacheCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_cluster#tags_all ElasticacheCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheGlobalReplicationGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheGlobalReplicationGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group aws_elasticache_global_replication_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        global_replication_group_id_suffix: builtins.str,
        primary_replication_group_id: builtins.str,
        global_replication_group_description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group aws_elasticache_global_replication_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param global_replication_group_id_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#global_replication_group_id_suffix ElasticacheGlobalReplicationGroup#global_replication_group_id_suffix}.
        :param primary_replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#primary_replication_group_id ElasticacheGlobalReplicationGroup#primary_replication_group_id}.
        :param global_replication_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#global_replication_group_description ElasticacheGlobalReplicationGroup#global_replication_group_description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheGlobalReplicationGroupConfig(
            global_replication_group_id_suffix=global_replication_group_id_suffix,
            primary_replication_group_id=primary_replication_group_id,
            global_replication_group_description=global_replication_group_description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetGlobalReplicationGroupDescription")
    def reset_global_replication_group_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalReplicationGroupDescription", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actualEngineVersion")
    def actual_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actualEngineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="atRestEncryptionEnabled")
    def at_rest_encryption_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "atRestEncryptionEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTokenEnabled")
    def auth_token_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "authTokenEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheNodeType")
    def cache_node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheNodeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEnabled")
    def cluster_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "clusterEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionActual")
    def engine_version_actual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersionActual"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalReplicationGroupId")
    def global_replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalReplicationGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transitEncryptionEnabled")
    def transit_encryption_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "transitEncryptionEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalReplicationGroupDescriptionInput")
    def global_replication_group_description_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalReplicationGroupDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalReplicationGroupIdSuffixInput")
    def global_replication_group_id_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalReplicationGroupIdSuffixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryReplicationGroupIdInput")
    def primary_replication_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "primaryReplicationGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalReplicationGroupDescription")
    def global_replication_group_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalReplicationGroupDescription"))

    @global_replication_group_description.setter
    def global_replication_group_description(self, value: builtins.str) -> None:
        jsii.set(self, "globalReplicationGroupDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalReplicationGroupIdSuffix")
    def global_replication_group_id_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalReplicationGroupIdSuffix"))

    @global_replication_group_id_suffix.setter
    def global_replication_group_id_suffix(self, value: builtins.str) -> None:
        jsii.set(self, "globalReplicationGroupIdSuffix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryReplicationGroupId")
    def primary_replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryReplicationGroupId"))

    @primary_replication_group_id.setter
    def primary_replication_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "primaryReplicationGroupId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheGlobalReplicationGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "global_replication_group_id_suffix": "globalReplicationGroupIdSuffix",
        "primary_replication_group_id": "primaryReplicationGroupId",
        "global_replication_group_description": "globalReplicationGroupDescription",
    },
)
class ElasticacheGlobalReplicationGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        global_replication_group_id_suffix: builtins.str,
        primary_replication_group_id: builtins.str,
        global_replication_group_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param global_replication_group_id_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#global_replication_group_id_suffix ElasticacheGlobalReplicationGroup#global_replication_group_id_suffix}.
        :param primary_replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#primary_replication_group_id ElasticacheGlobalReplicationGroup#primary_replication_group_id}.
        :param global_replication_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#global_replication_group_description ElasticacheGlobalReplicationGroup#global_replication_group_description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "global_replication_group_id_suffix": global_replication_group_id_suffix,
            "primary_replication_group_id": primary_replication_group_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if global_replication_group_description is not None:
            self._values["global_replication_group_description"] = global_replication_group_description

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
    def global_replication_group_id_suffix(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#global_replication_group_id_suffix ElasticacheGlobalReplicationGroup#global_replication_group_id_suffix}.'''
        result = self._values.get("global_replication_group_id_suffix")
        assert result is not None, "Required property 'global_replication_group_id_suffix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_replication_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#primary_replication_group_id ElasticacheGlobalReplicationGroup#primary_replication_group_id}.'''
        result = self._values.get("primary_replication_group_id")
        assert result is not None, "Required property 'primary_replication_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def global_replication_group_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_global_replication_group#global_replication_group_description ElasticacheGlobalReplicationGroup#global_replication_group_description}.'''
        result = self._values.get("global_replication_group_description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheGlobalReplicationGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group aws_elasticache_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["ElasticacheParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group aws_elasticache_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#family ElasticacheParameterGroup#family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#name ElasticacheParameterGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#description ElasticacheParameterGroup#description}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#parameter ElasticacheParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#tags ElasticacheParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#tags_all ElasticacheParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheParameterGroupConfig(
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
    ) -> typing.Optional[typing.List["ElasticacheParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["ElasticacheParameterGroupParameter"]], jsii.get(self, "parameterInput"))

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
    def parameter(self) -> typing.List["ElasticacheParameterGroupParameter"]:
        return typing.cast(typing.List["ElasticacheParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(
        self,
        value: typing.List["ElasticacheParameterGroupParameter"],
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
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheParameterGroupConfig",
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
class ElasticacheParameterGroupConfig(cdktf.TerraformMetaArguments):
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
        parameter: typing.Optional[typing.Sequence["ElasticacheParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#family ElasticacheParameterGroup#family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#name ElasticacheParameterGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#description ElasticacheParameterGroup#description}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#parameter ElasticacheParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#tags ElasticacheParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#tags_all ElasticacheParameterGroup#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#family ElasticacheParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#name ElasticacheParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#description ElasticacheParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["ElasticacheParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#parameter ElasticacheParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["ElasticacheParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#tags ElasticacheParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#tags_all ElasticacheParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ElasticacheParameterGroupParameter:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#name ElasticacheParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#value ElasticacheParameterGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#name ElasticacheParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_parameter_group#value ElasticacheParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheReplicationGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheReplicationGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group aws_elasticache_replication_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        replication_group_description: builtins.str,
        replication_group_id: builtins.str,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        at_rest_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auth_token: typing.Optional[builtins.str] = None,
        automatic_failover_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cluster_mode: typing.Optional["ElasticacheReplicationGroupClusterMode"] = None,
        data_tiering_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        global_replication_group_id: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        multi_az_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        node_type: typing.Optional[builtins.str] = None,
        notification_topic_arn: typing.Optional[builtins.str] = None,
        number_cache_clusters: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["ElasticacheReplicationGroupTimeouts"] = None,
        transit_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group aws_elasticache_replication_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param replication_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replication_group_description ElasticacheReplicationGroup#replication_group_description}.
        :param replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replication_group_id ElasticacheReplicationGroup#replication_group_id}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#apply_immediately ElasticacheReplicationGroup#apply_immediately}.
        :param at_rest_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#at_rest_encryption_enabled ElasticacheReplicationGroup#at_rest_encryption_enabled}.
        :param auth_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#auth_token ElasticacheReplicationGroup#auth_token}.
        :param automatic_failover_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#automatic_failover_enabled ElasticacheReplicationGroup#automatic_failover_enabled}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#auto_minor_version_upgrade ElasticacheReplicationGroup#auto_minor_version_upgrade}.
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#availability_zones ElasticacheReplicationGroup#availability_zones}.
        :param cluster_mode: cluster_mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#cluster_mode ElasticacheReplicationGroup#cluster_mode}
        :param data_tiering_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#data_tiering_enabled ElasticacheReplicationGroup#data_tiering_enabled}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#engine ElasticacheReplicationGroup#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#engine_version ElasticacheReplicationGroup#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#final_snapshot_identifier ElasticacheReplicationGroup#final_snapshot_identifier}.
        :param global_replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#global_replication_group_id ElasticacheReplicationGroup#global_replication_group_id}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#kms_key_id ElasticacheReplicationGroup#kms_key_id}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#maintenance_window ElasticacheReplicationGroup#maintenance_window}.
        :param multi_az_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#multi_az_enabled ElasticacheReplicationGroup#multi_az_enabled}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#node_type ElasticacheReplicationGroup#node_type}.
        :param notification_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#notification_topic_arn ElasticacheReplicationGroup#notification_topic_arn}.
        :param number_cache_clusters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#number_cache_clusters ElasticacheReplicationGroup#number_cache_clusters}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#parameter_group_name ElasticacheReplicationGroup#parameter_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#port ElasticacheReplicationGroup#port}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#security_group_ids ElasticacheReplicationGroup#security_group_ids}.
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#security_group_names ElasticacheReplicationGroup#security_group_names}.
        :param snapshot_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_arns ElasticacheReplicationGroup#snapshot_arns}.
        :param snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_name ElasticacheReplicationGroup#snapshot_name}.
        :param snapshot_retention_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_retention_limit ElasticacheReplicationGroup#snapshot_retention_limit}.
        :param snapshot_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_window ElasticacheReplicationGroup#snapshot_window}.
        :param subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#subnet_group_name ElasticacheReplicationGroup#subnet_group_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#tags ElasticacheReplicationGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#tags_all ElasticacheReplicationGroup#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#timeouts ElasticacheReplicationGroup#timeouts}
        :param transit_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#transit_encryption_enabled ElasticacheReplicationGroup#transit_encryption_enabled}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheReplicationGroupConfig(
            replication_group_description=replication_group_description,
            replication_group_id=replication_group_id,
            apply_immediately=apply_immediately,
            at_rest_encryption_enabled=at_rest_encryption_enabled,
            auth_token=auth_token,
            automatic_failover_enabled=automatic_failover_enabled,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zones=availability_zones,
            cluster_mode=cluster_mode,
            data_tiering_enabled=data_tiering_enabled,
            engine=engine,
            engine_version=engine_version,
            final_snapshot_identifier=final_snapshot_identifier,
            global_replication_group_id=global_replication_group_id,
            kms_key_id=kms_key_id,
            maintenance_window=maintenance_window,
            multi_az_enabled=multi_az_enabled,
            node_type=node_type,
            notification_topic_arn=notification_topic_arn,
            number_cache_clusters=number_cache_clusters,
            parameter_group_name=parameter_group_name,
            port=port,
            security_group_ids=security_group_ids,
            security_group_names=security_group_names,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            subnet_group_name=subnet_group_name,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            transit_encryption_enabled=transit_encryption_enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putClusterMode")
    def put_cluster_mode(
        self,
        *,
        replicas_per_node_group: jsii.Number,
        num_node_groups: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param replicas_per_node_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replicas_per_node_group ElasticacheReplicationGroup#replicas_per_node_group}.
        :param num_node_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#num_node_groups ElasticacheReplicationGroup#num_node_groups}.
        '''
        value = ElasticacheReplicationGroupClusterMode(
            replicas_per_node_group=replicas_per_node_group,
            num_node_groups=num_node_groups,
        )

        return typing.cast(None, jsii.invoke(self, "putClusterMode", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#create ElasticacheReplicationGroup#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#delete ElasticacheReplicationGroup#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#update ElasticacheReplicationGroup#update}.
        '''
        value = ElasticacheReplicationGroupTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAtRestEncryptionEnabled")
    def reset_at_rest_encryption_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAtRestEncryptionEnabled", []))

    @jsii.member(jsii_name="resetAuthToken")
    def reset_auth_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthToken", []))

    @jsii.member(jsii_name="resetAutomaticFailoverEnabled")
    def reset_automatic_failover_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticFailoverEnabled", []))

    @jsii.member(jsii_name="resetAutoMinorVersionUpgrade")
    def reset_auto_minor_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoMinorVersionUpgrade", []))

    @jsii.member(jsii_name="resetAvailabilityZones")
    def reset_availability_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZones", []))

    @jsii.member(jsii_name="resetClusterMode")
    def reset_cluster_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMode", []))

    @jsii.member(jsii_name="resetDataTieringEnabled")
    def reset_data_tiering_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataTieringEnabled", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetFinalSnapshotIdentifier")
    def reset_final_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFinalSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetGlobalReplicationGroupId")
    def reset_global_replication_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalReplicationGroupId", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetMultiAzEnabled")
    def reset_multi_az_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiAzEnabled", []))

    @jsii.member(jsii_name="resetNodeType")
    def reset_node_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeType", []))

    @jsii.member(jsii_name="resetNotificationTopicArn")
    def reset_notification_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationTopicArn", []))

    @jsii.member(jsii_name="resetNumberCacheClusters")
    def reset_number_cache_clusters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberCacheClusters", []))

    @jsii.member(jsii_name="resetParameterGroupName")
    def reset_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterGroupName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSecurityGroupNames")
    def reset_security_group_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupNames", []))

    @jsii.member(jsii_name="resetSnapshotArns")
    def reset_snapshot_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotArns", []))

    @jsii.member(jsii_name="resetSnapshotName")
    def reset_snapshot_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotName", []))

    @jsii.member(jsii_name="resetSnapshotRetentionLimit")
    def reset_snapshot_retention_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotRetentionLimit", []))

    @jsii.member(jsii_name="resetSnapshotWindow")
    def reset_snapshot_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotWindow", []))

    @jsii.member(jsii_name="resetSubnetGroupName")
    def reset_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetGroupName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTransitEncryptionEnabled")
    def reset_transit_encryption_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransitEncryptionEnabled", []))

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
    @jsii.member(jsii_name="clusterEnabled")
    def cluster_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "clusterEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterMode")
    def cluster_mode(self) -> "ElasticacheReplicationGroupClusterModeOutputReference":
        return typing.cast("ElasticacheReplicationGroupClusterModeOutputReference", jsii.get(self, "clusterMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationEndpointAddress")
    def configuration_endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionActual")
    def engine_version_actual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersionActual"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberClusters")
    def member_clusters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "memberClusters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryEndpointAddress")
    def primary_endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readerEndpointAddress")
    def reader_endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readerEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ElasticacheReplicationGroupTimeoutsOutputReference":
        return typing.cast("ElasticacheReplicationGroupTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediatelyInput")
    def apply_immediately_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "applyImmediatelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="atRestEncryptionEnabledInput")
    def at_rest_encryption_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "atRestEncryptionEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTokenInput")
    def auth_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticFailoverEnabledInput")
    def automatic_failover_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "automaticFailoverEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgradeInput")
    def auto_minor_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoMinorVersionUpgradeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZonesInput")
    def availability_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZonesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterModeInput")
    def cluster_mode_input(
        self,
    ) -> typing.Optional["ElasticacheReplicationGroupClusterMode"]:
        return typing.cast(typing.Optional["ElasticacheReplicationGroupClusterMode"], jsii.get(self, "clusterModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataTieringEnabledInput")
    def data_tiering_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "dataTieringEnabledInput"))

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
    @jsii.member(jsii_name="globalReplicationGroupIdInput")
    def global_replication_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalReplicationGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAzEnabledInput")
    def multi_az_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "multiAzEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeTypeInput")
    def node_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTopicArnInput")
    def notification_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberCacheClustersInput")
    def number_cache_clusters_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberCacheClustersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupNameInput")
    def parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupDescriptionInput")
    def replication_group_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationGroupDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupIdInput")
    def replication_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNamesInput")
    def security_group_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArnsInput")
    def snapshot_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "snapshotArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotNameInput")
    def snapshot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimitInput")
    def snapshot_retention_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "snapshotRetentionLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindowInput")
    def snapshot_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupNameInput")
    def subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetGroupNameInput"))

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
    def timeouts_input(self) -> typing.Optional["ElasticacheReplicationGroupTimeouts"]:
        return typing.cast(typing.Optional["ElasticacheReplicationGroupTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transitEncryptionEnabledInput")
    def transit_encryption_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "transitEncryptionEnabledInput"))

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
    @jsii.member(jsii_name="atRestEncryptionEnabled")
    def at_rest_encryption_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "atRestEncryptionEnabled"))

    @at_rest_encryption_enabled.setter
    def at_rest_encryption_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "atRestEncryptionEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authToken")
    def auth_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authToken"))

    @auth_token.setter
    def auth_token(self, value: builtins.str) -> None:
        jsii.set(self, "authToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticFailoverEnabled")
    def automatic_failover_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "automaticFailoverEnabled"))

    @automatic_failover_enabled.setter
    def automatic_failover_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "automaticFailoverEnabled", value)

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
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "availabilityZones", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataTieringEnabled")
    def data_tiering_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "dataTieringEnabled"))

    @data_tiering_enabled.setter
    def data_tiering_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "dataTieringEnabled", value)

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
    @jsii.member(jsii_name="globalReplicationGroupId")
    def global_replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalReplicationGroupId"))

    @global_replication_group_id.setter
    def global_replication_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "globalReplicationGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindow"))

    @maintenance_window.setter
    def maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAzEnabled")
    def multi_az_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "multiAzEnabled"))

    @multi_az_enabled.setter
    def multi_az_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "multiAzEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTopicArn")
    def notification_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationTopicArn"))

    @notification_topic_arn.setter
    def notification_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "notificationTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberCacheClusters")
    def number_cache_clusters(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberCacheClusters"))

    @number_cache_clusters.setter
    def number_cache_clusters(self, value: jsii.Number) -> None:
        jsii.set(self, "numberCacheClusters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @parameter_group_name.setter
    def parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupDescription")
    def replication_group_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationGroupDescription"))

    @replication_group_description.setter
    def replication_group_description(self, value: builtins.str) -> None:
        jsii.set(self, "replicationGroupDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationGroupId")
    def replication_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationGroupId"))

    @replication_group_id.setter
    def replication_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNames")
    def security_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupNames"))

    @security_group_names.setter
    def security_group_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArns")
    def snapshot_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "snapshotArns"))

    @snapshot_arns.setter
    def snapshot_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "snapshotArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotName")
    def snapshot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotName"))

    @snapshot_name.setter
    def snapshot_name(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotRetentionLimit"))

    @snapshot_retention_limit.setter
    def snapshot_retention_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "snapshotRetentionLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotWindow"))

    @snapshot_window.setter
    def snapshot_window(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetGroupName"))

    @subnet_group_name.setter
    def subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "subnetGroupName", value)

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
    @jsii.member(jsii_name="transitEncryptionEnabled")
    def transit_encryption_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "transitEncryptionEnabled"))

    @transit_encryption_enabled.setter
    def transit_encryption_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "transitEncryptionEnabled", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheReplicationGroupClusterMode",
    jsii_struct_bases=[],
    name_mapping={
        "replicas_per_node_group": "replicasPerNodeGroup",
        "num_node_groups": "numNodeGroups",
    },
)
class ElasticacheReplicationGroupClusterMode:
    def __init__(
        self,
        *,
        replicas_per_node_group: jsii.Number,
        num_node_groups: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param replicas_per_node_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replicas_per_node_group ElasticacheReplicationGroup#replicas_per_node_group}.
        :param num_node_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#num_node_groups ElasticacheReplicationGroup#num_node_groups}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "replicas_per_node_group": replicas_per_node_group,
        }
        if num_node_groups is not None:
            self._values["num_node_groups"] = num_node_groups

    @builtins.property
    def replicas_per_node_group(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replicas_per_node_group ElasticacheReplicationGroup#replicas_per_node_group}.'''
        result = self._values.get("replicas_per_node_group")
        assert result is not None, "Required property 'replicas_per_node_group' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def num_node_groups(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#num_node_groups ElasticacheReplicationGroup#num_node_groups}.'''
        result = self._values.get("num_node_groups")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheReplicationGroupClusterMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheReplicationGroupClusterModeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheReplicationGroupClusterModeOutputReference",
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

    @jsii.member(jsii_name="resetNumNodeGroups")
    def reset_num_node_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumNodeGroups", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numNodeGroupsInput")
    def num_node_groups_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numNodeGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicasPerNodeGroupInput")
    def replicas_per_node_group_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicasPerNodeGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numNodeGroups")
    def num_node_groups(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numNodeGroups"))

    @num_node_groups.setter
    def num_node_groups(self, value: jsii.Number) -> None:
        jsii.set(self, "numNodeGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicasPerNodeGroup")
    def replicas_per_node_group(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicasPerNodeGroup"))

    @replicas_per_node_group.setter
    def replicas_per_node_group(self, value: jsii.Number) -> None:
        jsii.set(self, "replicasPerNodeGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElasticacheReplicationGroupClusterMode]:
        return typing.cast(typing.Optional[ElasticacheReplicationGroupClusterMode], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElasticacheReplicationGroupClusterMode],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheReplicationGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "replication_group_description": "replicationGroupDescription",
        "replication_group_id": "replicationGroupId",
        "apply_immediately": "applyImmediately",
        "at_rest_encryption_enabled": "atRestEncryptionEnabled",
        "auth_token": "authToken",
        "automatic_failover_enabled": "automaticFailoverEnabled",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zones": "availabilityZones",
        "cluster_mode": "clusterMode",
        "data_tiering_enabled": "dataTieringEnabled",
        "engine": "engine",
        "engine_version": "engineVersion",
        "final_snapshot_identifier": "finalSnapshotIdentifier",
        "global_replication_group_id": "globalReplicationGroupId",
        "kms_key_id": "kmsKeyId",
        "maintenance_window": "maintenanceWindow",
        "multi_az_enabled": "multiAzEnabled",
        "node_type": "nodeType",
        "notification_topic_arn": "notificationTopicArn",
        "number_cache_clusters": "numberCacheClusters",
        "parameter_group_name": "parameterGroupName",
        "port": "port",
        "security_group_ids": "securityGroupIds",
        "security_group_names": "securityGroupNames",
        "snapshot_arns": "snapshotArns",
        "snapshot_name": "snapshotName",
        "snapshot_retention_limit": "snapshotRetentionLimit",
        "snapshot_window": "snapshotWindow",
        "subnet_group_name": "subnetGroupName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "transit_encryption_enabled": "transitEncryptionEnabled",
    },
)
class ElasticacheReplicationGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        replication_group_description: builtins.str,
        replication_group_id: builtins.str,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        at_rest_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auth_token: typing.Optional[builtins.str] = None,
        automatic_failover_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cluster_mode: typing.Optional[ElasticacheReplicationGroupClusterMode] = None,
        data_tiering_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        global_replication_group_id: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        multi_az_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        node_type: typing.Optional[builtins.str] = None,
        notification_topic_arn: typing.Optional[builtins.str] = None,
        number_cache_clusters: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["ElasticacheReplicationGroupTimeouts"] = None,
        transit_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param replication_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replication_group_description ElasticacheReplicationGroup#replication_group_description}.
        :param replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replication_group_id ElasticacheReplicationGroup#replication_group_id}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#apply_immediately ElasticacheReplicationGroup#apply_immediately}.
        :param at_rest_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#at_rest_encryption_enabled ElasticacheReplicationGroup#at_rest_encryption_enabled}.
        :param auth_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#auth_token ElasticacheReplicationGroup#auth_token}.
        :param automatic_failover_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#automatic_failover_enabled ElasticacheReplicationGroup#automatic_failover_enabled}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#auto_minor_version_upgrade ElasticacheReplicationGroup#auto_minor_version_upgrade}.
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#availability_zones ElasticacheReplicationGroup#availability_zones}.
        :param cluster_mode: cluster_mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#cluster_mode ElasticacheReplicationGroup#cluster_mode}
        :param data_tiering_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#data_tiering_enabled ElasticacheReplicationGroup#data_tiering_enabled}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#engine ElasticacheReplicationGroup#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#engine_version ElasticacheReplicationGroup#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#final_snapshot_identifier ElasticacheReplicationGroup#final_snapshot_identifier}.
        :param global_replication_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#global_replication_group_id ElasticacheReplicationGroup#global_replication_group_id}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#kms_key_id ElasticacheReplicationGroup#kms_key_id}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#maintenance_window ElasticacheReplicationGroup#maintenance_window}.
        :param multi_az_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#multi_az_enabled ElasticacheReplicationGroup#multi_az_enabled}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#node_type ElasticacheReplicationGroup#node_type}.
        :param notification_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#notification_topic_arn ElasticacheReplicationGroup#notification_topic_arn}.
        :param number_cache_clusters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#number_cache_clusters ElasticacheReplicationGroup#number_cache_clusters}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#parameter_group_name ElasticacheReplicationGroup#parameter_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#port ElasticacheReplicationGroup#port}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#security_group_ids ElasticacheReplicationGroup#security_group_ids}.
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#security_group_names ElasticacheReplicationGroup#security_group_names}.
        :param snapshot_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_arns ElasticacheReplicationGroup#snapshot_arns}.
        :param snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_name ElasticacheReplicationGroup#snapshot_name}.
        :param snapshot_retention_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_retention_limit ElasticacheReplicationGroup#snapshot_retention_limit}.
        :param snapshot_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_window ElasticacheReplicationGroup#snapshot_window}.
        :param subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#subnet_group_name ElasticacheReplicationGroup#subnet_group_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#tags ElasticacheReplicationGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#tags_all ElasticacheReplicationGroup#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#timeouts ElasticacheReplicationGroup#timeouts}
        :param transit_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#transit_encryption_enabled ElasticacheReplicationGroup#transit_encryption_enabled}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cluster_mode, dict):
            cluster_mode = ElasticacheReplicationGroupClusterMode(**cluster_mode)
        if isinstance(timeouts, dict):
            timeouts = ElasticacheReplicationGroupTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "replication_group_description": replication_group_description,
            "replication_group_id": replication_group_id,
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
        if at_rest_encryption_enabled is not None:
            self._values["at_rest_encryption_enabled"] = at_rest_encryption_enabled
        if auth_token is not None:
            self._values["auth_token"] = auth_token
        if automatic_failover_enabled is not None:
            self._values["automatic_failover_enabled"] = automatic_failover_enabled
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if cluster_mode is not None:
            self._values["cluster_mode"] = cluster_mode
        if data_tiering_enabled is not None:
            self._values["data_tiering_enabled"] = data_tiering_enabled
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_identifier is not None:
            self._values["final_snapshot_identifier"] = final_snapshot_identifier
        if global_replication_group_id is not None:
            self._values["global_replication_group_id"] = global_replication_group_id
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if multi_az_enabled is not None:
            self._values["multi_az_enabled"] = multi_az_enabled
        if node_type is not None:
            self._values["node_type"] = node_type
        if notification_topic_arn is not None:
            self._values["notification_topic_arn"] = notification_topic_arn
        if number_cache_clusters is not None:
            self._values["number_cache_clusters"] = number_cache_clusters
        if parameter_group_name is not None:
            self._values["parameter_group_name"] = parameter_group_name
        if port is not None:
            self._values["port"] = port
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if security_group_names is not None:
            self._values["security_group_names"] = security_group_names
        if snapshot_arns is not None:
            self._values["snapshot_arns"] = snapshot_arns
        if snapshot_name is not None:
            self._values["snapshot_name"] = snapshot_name
        if snapshot_retention_limit is not None:
            self._values["snapshot_retention_limit"] = snapshot_retention_limit
        if snapshot_window is not None:
            self._values["snapshot_window"] = snapshot_window
        if subnet_group_name is not None:
            self._values["subnet_group_name"] = subnet_group_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if transit_encryption_enabled is not None:
            self._values["transit_encryption_enabled"] = transit_encryption_enabled

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
    def replication_group_description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replication_group_description ElasticacheReplicationGroup#replication_group_description}.'''
        result = self._values.get("replication_group_description")
        assert result is not None, "Required property 'replication_group_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replication_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#replication_group_id ElasticacheReplicationGroup#replication_group_id}.'''
        result = self._values.get("replication_group_id")
        assert result is not None, "Required property 'replication_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#apply_immediately ElasticacheReplicationGroup#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def at_rest_encryption_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#at_rest_encryption_enabled ElasticacheReplicationGroup#at_rest_encryption_enabled}.'''
        result = self._values.get("at_rest_encryption_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auth_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#auth_token ElasticacheReplicationGroup#auth_token}.'''
        result = self._values.get("auth_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automatic_failover_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#automatic_failover_enabled ElasticacheReplicationGroup#automatic_failover_enabled}.'''
        result = self._values.get("automatic_failover_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#auto_minor_version_upgrade ElasticacheReplicationGroup#auto_minor_version_upgrade}.'''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#availability_zones ElasticacheReplicationGroup#availability_zones}.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cluster_mode(self) -> typing.Optional[ElasticacheReplicationGroupClusterMode]:
        '''cluster_mode block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#cluster_mode ElasticacheReplicationGroup#cluster_mode}
        '''
        result = self._values.get("cluster_mode")
        return typing.cast(typing.Optional[ElasticacheReplicationGroupClusterMode], result)

    @builtins.property
    def data_tiering_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#data_tiering_enabled ElasticacheReplicationGroup#data_tiering_enabled}.'''
        result = self._values.get("data_tiering_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#engine ElasticacheReplicationGroup#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#engine_version ElasticacheReplicationGroup#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#final_snapshot_identifier ElasticacheReplicationGroup#final_snapshot_identifier}.'''
        result = self._values.get("final_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def global_replication_group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#global_replication_group_id ElasticacheReplicationGroup#global_replication_group_id}.'''
        result = self._values.get("global_replication_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#kms_key_id ElasticacheReplicationGroup#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#maintenance_window ElasticacheReplicationGroup#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_az_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#multi_az_enabled ElasticacheReplicationGroup#multi_az_enabled}.'''
        result = self._values.get("multi_az_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def node_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#node_type ElasticacheReplicationGroup#node_type}.'''
        result = self._values.get("node_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#notification_topic_arn ElasticacheReplicationGroup#notification_topic_arn}.'''
        result = self._values.get("notification_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_cache_clusters(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#number_cache_clusters ElasticacheReplicationGroup#number_cache_clusters}.'''
        result = self._values.get("number_cache_clusters")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#parameter_group_name ElasticacheReplicationGroup#parameter_group_name}.'''
        result = self._values.get("parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#port ElasticacheReplicationGroup#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#security_group_ids ElasticacheReplicationGroup#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_group_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#security_group_names ElasticacheReplicationGroup#security_group_names}.'''
        result = self._values.get("security_group_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_arns ElasticacheReplicationGroup#snapshot_arns}.'''
        result = self._values.get("snapshot_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_name ElasticacheReplicationGroup#snapshot_name}.'''
        result = self._values.get("snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_retention_limit ElasticacheReplicationGroup#snapshot_retention_limit}.'''
        result = self._values.get("snapshot_retention_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snapshot_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#snapshot_window ElasticacheReplicationGroup#snapshot_window}.'''
        result = self._values.get("snapshot_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#subnet_group_name ElasticacheReplicationGroup#subnet_group_name}.'''
        result = self._values.get("subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#tags ElasticacheReplicationGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#tags_all ElasticacheReplicationGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ElasticacheReplicationGroupTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#timeouts ElasticacheReplicationGroup#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ElasticacheReplicationGroupTimeouts"], result)

    @builtins.property
    def transit_encryption_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#transit_encryption_enabled ElasticacheReplicationGroup#transit_encryption_enabled}.'''
        result = self._values.get("transit_encryption_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheReplicationGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheReplicationGroupTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ElasticacheReplicationGroupTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#create ElasticacheReplicationGroup#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#delete ElasticacheReplicationGroup#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#update ElasticacheReplicationGroup#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#create ElasticacheReplicationGroup#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#delete ElasticacheReplicationGroup#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group#update ElasticacheReplicationGroup#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheReplicationGroupTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheReplicationGroupTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheReplicationGroupTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[ElasticacheReplicationGroupTimeouts]:
        return typing.cast(typing.Optional[ElasticacheReplicationGroupTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElasticacheReplicationGroupTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ElasticacheSecurityGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheSecurityGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group aws_elasticache_security_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        security_group_names: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group aws_elasticache_security_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#name ElasticacheSecurityGroup#name}.
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#security_group_names ElasticacheSecurityGroup#security_group_names}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#description ElasticacheSecurityGroup#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheSecurityGroupConfig(
            name=name,
            security_group_names=security_group_names,
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNamesInput")
    def security_group_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupNamesInput"))

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
    @jsii.member(jsii_name="securityGroupNames")
    def security_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupNames"))

    @security_group_names.setter
    def security_group_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupNames", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheSecurityGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "security_group_names": "securityGroupNames",
        "description": "description",
    },
)
class ElasticacheSecurityGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        security_group_names: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#name ElasticacheSecurityGroup#name}.
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#security_group_names ElasticacheSecurityGroup#security_group_names}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#description ElasticacheSecurityGroup#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "security_group_names": security_group_names,
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#name ElasticacheSecurityGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#security_group_names ElasticacheSecurityGroup#security_group_names}.'''
        result = self._values.get("security_group_names")
        assert result is not None, "Required property 'security_group_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_security_group#description ElasticacheSecurityGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheSecurityGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheSubnetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group aws_elasticache_subnet_group}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group aws_elasticache_subnet_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#name ElasticacheSubnetGroup#name}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#subnet_ids ElasticacheSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#description ElasticacheSubnetGroup#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#tags ElasticacheSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#tags_all ElasticacheSubnetGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheSubnetGroupConfig(
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
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheSubnetGroupConfig",
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
class ElasticacheSubnetGroupConfig(cdktf.TerraformMetaArguments):
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
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#name ElasticacheSubnetGroup#name}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#subnet_ids ElasticacheSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#description ElasticacheSubnetGroup#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#tags ElasticacheSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#tags_all ElasticacheSubnetGroup#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#name ElasticacheSubnetGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#subnet_ids ElasticacheSubnetGroup#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#description ElasticacheSubnetGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#tags ElasticacheSubnetGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_subnet_group#tags_all ElasticacheSubnetGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user aws_elasticache_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_string: builtins.str,
        engine: builtins.str,
        user_id: builtins.str,
        user_name: builtins.str,
        no_password_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user aws_elasticache_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#access_string ElasticacheUser#access_string}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#engine ElasticacheUser#engine}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#user_id ElasticacheUser#user_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#user_name ElasticacheUser#user_name}.
        :param no_password_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#no_password_required ElasticacheUser#no_password_required}.
        :param passwords: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#passwords ElasticacheUser#passwords}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#tags ElasticacheUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#tags_all ElasticacheUser#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheUserConfig(
            access_string=access_string,
            engine=engine,
            user_id=user_id,
            user_name=user_name,
            no_password_required=no_password_required,
            passwords=passwords,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetNoPasswordRequired")
    def reset_no_password_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoPasswordRequired", []))

    @jsii.member(jsii_name="resetPasswords")
    def reset_passwords(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswords", []))

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
    @jsii.member(jsii_name="accessStringInput")
    def access_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noPasswordRequiredInput")
    def no_password_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noPasswordRequiredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordsInput")
    def passwords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "passwordsInput"))

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
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessString")
    def access_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessString"))

    @access_string.setter
    def access_string(self, value: builtins.str) -> None:
        jsii.set(self, "accessString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noPasswordRequired")
    def no_password_required(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noPasswordRequired"))

    @no_password_required.setter
    def no_password_required(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "noPasswordRequired", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwords")
    def passwords(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passwords"))

    @passwords.setter
    def passwords(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "passwords", value)

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
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_string": "accessString",
        "engine": "engine",
        "user_id": "userId",
        "user_name": "userName",
        "no_password_required": "noPasswordRequired",
        "passwords": "passwords",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ElasticacheUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_string: builtins.str,
        engine: builtins.str,
        user_id: builtins.str,
        user_name: builtins.str,
        no_password_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#access_string ElasticacheUser#access_string}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#engine ElasticacheUser#engine}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#user_id ElasticacheUser#user_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#user_name ElasticacheUser#user_name}.
        :param no_password_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#no_password_required ElasticacheUser#no_password_required}.
        :param passwords: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#passwords ElasticacheUser#passwords}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#tags ElasticacheUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#tags_all ElasticacheUser#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "access_string": access_string,
            "engine": engine,
            "user_id": user_id,
            "user_name": user_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if no_password_required is not None:
            self._values["no_password_required"] = no_password_required
        if passwords is not None:
            self._values["passwords"] = passwords
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
    def access_string(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#access_string ElasticacheUser#access_string}.'''
        result = self._values.get("access_string")
        assert result is not None, "Required property 'access_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def engine(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#engine ElasticacheUser#engine}.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#user_id ElasticacheUser#user_id}.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#user_name ElasticacheUser#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def no_password_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#no_password_required ElasticacheUser#no_password_required}.'''
        result = self._values.get("no_password_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def passwords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#passwords ElasticacheUser#passwords}.'''
        result = self._values.get("passwords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#tags ElasticacheUser#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user#tags_all ElasticacheUser#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticacheUserGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheUserGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group aws_elasticache_user_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        user_group_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group aws_elasticache_user_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#engine ElasticacheUserGroup#engine}.
        :param user_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#user_group_id ElasticacheUserGroup#user_group_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#tags ElasticacheUserGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#tags_all ElasticacheUserGroup#tags_all}.
        :param user_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#user_ids ElasticacheUserGroup#user_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ElasticacheUserGroupConfig(
            engine=engine,
            user_group_id=user_group_id,
            tags=tags,
            tags_all=tags_all,
            user_ids=user_ids,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUserIds")
    def reset_user_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserIds", []))

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
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

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
    @jsii.member(jsii_name="userGroupIdInput")
    def user_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdsInput")
    def user_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

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
    @jsii.member(jsii_name="userGroupId")
    def user_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userGroupId"))

    @user_group_id.setter
    def user_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "userGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIds")
    def user_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userIds"))

    @user_ids.setter
    def user_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "userIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.elasticache.ElasticacheUserGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "engine": "engine",
        "user_group_id": "userGroupId",
        "tags": "tags",
        "tags_all": "tagsAll",
        "user_ids": "userIds",
    },
)
class ElasticacheUserGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        engine: builtins.str,
        user_group_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS ElastiCache.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#engine ElasticacheUserGroup#engine}.
        :param user_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#user_group_id ElasticacheUserGroup#user_group_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#tags ElasticacheUserGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#tags_all ElasticacheUserGroup#tags_all}.
        :param user_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#user_ids ElasticacheUserGroup#user_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "engine": engine,
            "user_group_id": user_group_id,
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
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if user_ids is not None:
            self._values["user_ids"] = user_ids

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
    def engine(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#engine ElasticacheUserGroup#engine}.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#user_group_id ElasticacheUserGroup#user_group_id}.'''
        result = self._values.get("user_group_id")
        assert result is not None, "Required property 'user_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#tags ElasticacheUserGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#tags_all ElasticacheUserGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def user_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/elasticache_user_group#user_ids ElasticacheUserGroup#user_ids}.'''
        result = self._values.get("user_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticacheUserGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsElasticacheCluster",
    "DataAwsElasticacheClusterCacheNodes",
    "DataAwsElasticacheClusterConfig",
    "DataAwsElasticacheReplicationGroup",
    "DataAwsElasticacheReplicationGroupConfig",
    "DataAwsElasticacheUser",
    "DataAwsElasticacheUserConfig",
    "ElasticacheCluster",
    "ElasticacheClusterCacheNodes",
    "ElasticacheClusterConfig",
    "ElasticacheGlobalReplicationGroup",
    "ElasticacheGlobalReplicationGroupConfig",
    "ElasticacheParameterGroup",
    "ElasticacheParameterGroupConfig",
    "ElasticacheParameterGroupParameter",
    "ElasticacheReplicationGroup",
    "ElasticacheReplicationGroupClusterMode",
    "ElasticacheReplicationGroupClusterModeOutputReference",
    "ElasticacheReplicationGroupConfig",
    "ElasticacheReplicationGroupTimeouts",
    "ElasticacheReplicationGroupTimeoutsOutputReference",
    "ElasticacheSecurityGroup",
    "ElasticacheSecurityGroupConfig",
    "ElasticacheSubnetGroup",
    "ElasticacheSubnetGroupConfig",
    "ElasticacheUser",
    "ElasticacheUserConfig",
    "ElasticacheUserGroup",
    "ElasticacheUserGroupConfig",
]

publication.publish()
