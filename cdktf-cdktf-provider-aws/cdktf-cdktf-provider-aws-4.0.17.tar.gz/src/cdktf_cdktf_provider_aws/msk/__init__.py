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


class DataAwsMskBrokerNodes(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodes",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes aws_msk_broker_nodes}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes aws_msk_broker_nodes} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#cluster_arn DataAwsMskBrokerNodes#cluster_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskBrokerNodesConfig(
            cluster_arn=cluster_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="nodeInfoList")
    def node_info_list(
        self,
        index: builtins.str,
    ) -> "DataAwsMskBrokerNodesNodeInfoList":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsMskBrokerNodesNodeInfoList", jsii.invoke(self, "nodeInfoList", [index]))

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
    @jsii.member(jsii_name="clusterArnInput")
    def cluster_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @cluster_arn.setter
    def cluster_arn(self, value: builtins.str) -> None:
        jsii.set(self, "clusterArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_arn": "clusterArn",
    },
)
class DataAwsMskBrokerNodesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_arn: builtins.str,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#cluster_arn DataAwsMskBrokerNodes#cluster_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_arn": cluster_arn,
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
    def cluster_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#cluster_arn DataAwsMskBrokerNodes#cluster_arn}.'''
        result = self._values.get("cluster_arn")
        assert result is not None, "Required property 'cluster_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskBrokerNodesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskBrokerNodesNodeInfoList(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodesNodeInfoList",
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
    @jsii.member(jsii_name="attachedEniId")
    def attached_eni_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attachedEniId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerId")
    def broker_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "brokerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSubnet")
    def client_subnet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSubnet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientVpcIpAddress")
    def client_vpc_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientVpcIpAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoints")
    def endpoints(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "endpoints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeArn")
    def node_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeArn"))


class DataAwsMskCluster(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster aws_msk_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster aws_msk_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#cluster_name DataAwsMskCluster#cluster_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#tags DataAwsMskCluster#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskClusterConfig(
            cluster_name=cluster_name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokers")
    def bootstrap_brokers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslIam")
    def bootstrap_brokers_sasl_iam(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslIam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslScram")
    def bootstrap_brokers_sasl_scram(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersTls")
    def bootstrap_brokers_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersion")
    def kafka_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kafkaVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodes")
    def number_of_broker_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfBrokerNodes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectString")
    def zookeeper_connect_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectString"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

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
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_name": "clusterName",
        "tags": "tags",
    },
)
class DataAwsMskClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#cluster_name DataAwsMskCluster#cluster_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#tags DataAwsMskCluster#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
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
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#cluster_name DataAwsMskCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#tags DataAwsMskCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskConfiguration(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration aws_msk_configuration}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration aws_msk_configuration} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#name DataAwsMskConfiguration#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskConfigurationConfig(
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersions")
    def kafka_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "kafkaVersions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverProperties")
    def server_properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverProperties"))

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
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsMskConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#name DataAwsMskConfiguration#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#name DataAwsMskConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskKafkaVersion(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskKafkaVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version aws_msk_kafka_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version aws_msk_kafka_version} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#preferred_versions DataAwsMskKafkaVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#version DataAwsMskKafkaVersion#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskKafkaVersionConfig(
            preferred_versions=preferred_versions,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredVersionsInput")
    def preferred_versions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

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
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskKafkaVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "preferred_versions": "preferredVersions",
        "version": "version",
    },
)
class DataAwsMskKafkaVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#preferred_versions DataAwsMskKafkaVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#version DataAwsMskKafkaVersion#version}.
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
    def preferred_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#preferred_versions DataAwsMskKafkaVersion#preferred_versions}.'''
        result = self._values.get("preferred_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#version DataAwsMskKafkaVersion#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskKafkaVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskconnectCustomPlugin(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectCustomPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin aws_mskconnect_custom_plugin}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin aws_mskconnect_custom_plugin} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#name DataAwsMskconnectCustomPlugin#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskconnectCustomPluginConfig(
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

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
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectCustomPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsMskconnectCustomPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#name DataAwsMskconnectCustomPlugin#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#name DataAwsMskconnectCustomPlugin#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskconnectCustomPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskconnectWorkerConfiguration(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectWorkerConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration aws_mskconnect_worker_configuration}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration aws_mskconnect_worker_configuration} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#name DataAwsMskconnectWorkerConfiguration#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskconnectWorkerConfigurationConfig(
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesFileContent")
    def properties_file_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "propertiesFileContent"))

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
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectWorkerConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsMskconnectWorkerConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#name DataAwsMskconnectWorkerConfiguration#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#name DataAwsMskconnectWorkerConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskconnectWorkerConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster aws_msk_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        broker_node_group_info: "MskClusterBrokerNodeGroupInfo",
        cluster_name: builtins.str,
        kafka_version: builtins.str,
        number_of_broker_nodes: jsii.Number,
        client_authentication: typing.Optional["MskClusterClientAuthentication"] = None,
        configuration_info: typing.Optional["MskClusterConfigurationInfo"] = None,
        encryption_info: typing.Optional["MskClusterEncryptionInfo"] = None,
        enhanced_monitoring: typing.Optional[builtins.str] = None,
        logging_info: typing.Optional["MskClusterLoggingInfo"] = None,
        open_monitoring: typing.Optional["MskClusterOpenMonitoring"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["MskClusterTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster aws_msk_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param broker_node_group_info: broker_node_group_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_node_group_info MskCluster#broker_node_group_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cluster_name MskCluster#cluster_name}.
        :param kafka_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#kafka_version MskCluster#kafka_version}.
        :param number_of_broker_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#number_of_broker_nodes MskCluster#number_of_broker_nodes}.
        :param client_authentication: client_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_authentication MskCluster#client_authentication}
        :param configuration_info: configuration_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#configuration_info MskCluster#configuration_info}
        :param encryption_info: encryption_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_info MskCluster#encryption_info}
        :param enhanced_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enhanced_monitoring MskCluster#enhanced_monitoring}.
        :param logging_info: logging_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#logging_info MskCluster#logging_info}
        :param open_monitoring: open_monitoring block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#open_monitoring MskCluster#open_monitoring}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags MskCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags_all MskCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#timeouts MskCluster#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskClusterConfig(
            broker_node_group_info=broker_node_group_info,
            cluster_name=cluster_name,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            client_authentication=client_authentication,
            configuration_info=configuration_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
            logging_info=logging_info,
            open_monitoring=open_monitoring,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putBrokerNodeGroupInfo")
    def put_broker_node_group_info(
        self,
        *,
        client_subnets: typing.Sequence[builtins.str],
        ebs_volume_size: jsii.Number,
        instance_type: builtins.str,
        security_groups: typing.Sequence[builtins.str],
        az_distribution: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_subnets MskCluster#client_subnets}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_volume_size MskCluster#ebs_volume_size}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#instance_type MskCluster#instance_type}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#security_groups MskCluster#security_groups}.
        :param az_distribution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#az_distribution MskCluster#az_distribution}.
        '''
        value = MskClusterBrokerNodeGroupInfo(
            client_subnets=client_subnets,
            ebs_volume_size=ebs_volume_size,
            instance_type=instance_type,
            security_groups=security_groups,
            az_distribution=az_distribution,
        )

        return typing.cast(None, jsii.invoke(self, "putBrokerNodeGroupInfo", [value]))

    @jsii.member(jsii_name="putClientAuthentication")
    def put_client_authentication(
        self,
        *,
        sasl: typing.Optional["MskClusterClientAuthenticationSasl"] = None,
        tls: typing.Optional["MskClusterClientAuthenticationTls"] = None,
    ) -> None:
        '''
        :param sasl: sasl block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#sasl MskCluster#sasl}
        :param tls: tls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tls MskCluster#tls}
        '''
        value = MskClusterClientAuthentication(sasl=sasl, tls=tls)

        return typing.cast(None, jsii.invoke(self, "putClientAuthentication", [value]))

    @jsii.member(jsii_name="putConfigurationInfo")
    def put_configuration_info(
        self,
        *,
        arn: builtins.str,
        revision: jsii.Number,
    ) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#arn MskCluster#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#revision MskCluster#revision}.
        '''
        value = MskClusterConfigurationInfo(arn=arn, revision=revision)

        return typing.cast(None, jsii.invoke(self, "putConfigurationInfo", [value]))

    @jsii.member(jsii_name="putEncryptionInfo")
    def put_encryption_info(
        self,
        *,
        encryption_at_rest_kms_key_arn: typing.Optional[builtins.str] = None,
        encryption_in_transit: typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"] = None,
    ) -> None:
        '''
        :param encryption_at_rest_kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_at_rest_kms_key_arn MskCluster#encryption_at_rest_kms_key_arn}.
        :param encryption_in_transit: encryption_in_transit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_in_transit MskCluster#encryption_in_transit}
        '''
        value = MskClusterEncryptionInfo(
            encryption_at_rest_kms_key_arn=encryption_at_rest_kms_key_arn,
            encryption_in_transit=encryption_in_transit,
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionInfo", [value]))

    @jsii.member(jsii_name="putLoggingInfo")
    def put_logging_info(
        self,
        *,
        broker_logs: "MskClusterLoggingInfoBrokerLogs",
    ) -> None:
        '''
        :param broker_logs: broker_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_logs MskCluster#broker_logs}
        '''
        value = MskClusterLoggingInfo(broker_logs=broker_logs)

        return typing.cast(None, jsii.invoke(self, "putLoggingInfo", [value]))

    @jsii.member(jsii_name="putOpenMonitoring")
    def put_open_monitoring(
        self,
        *,
        prometheus: "MskClusterOpenMonitoringPrometheus",
    ) -> None:
        '''
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prometheus MskCluster#prometheus}
        '''
        value = MskClusterOpenMonitoring(prometheus=prometheus)

        return typing.cast(None, jsii.invoke(self, "putOpenMonitoring", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#create MskCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delete MskCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#update MskCluster#update}.
        '''
        value = MskClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetClientAuthentication")
    def reset_client_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientAuthentication", []))

    @jsii.member(jsii_name="resetConfigurationInfo")
    def reset_configuration_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationInfo", []))

    @jsii.member(jsii_name="resetEncryptionInfo")
    def reset_encryption_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionInfo", []))

    @jsii.member(jsii_name="resetEnhancedMonitoring")
    def reset_enhanced_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnhancedMonitoring", []))

    @jsii.member(jsii_name="resetLoggingInfo")
    def reset_logging_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingInfo", []))

    @jsii.member(jsii_name="resetOpenMonitoring")
    def reset_open_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenMonitoring", []))

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
    @jsii.member(jsii_name="bootstrapBrokers")
    def bootstrap_brokers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslIam")
    def bootstrap_brokers_sasl_iam(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslIam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslScram")
    def bootstrap_brokers_sasl_scram(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersTls")
    def bootstrap_brokers_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerNodeGroupInfo")
    def broker_node_group_info(self) -> "MskClusterBrokerNodeGroupInfoOutputReference":
        return typing.cast("MskClusterBrokerNodeGroupInfoOutputReference", jsii.get(self, "brokerNodeGroupInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientAuthentication")
    def client_authentication(self) -> "MskClusterClientAuthenticationOutputReference":
        return typing.cast("MskClusterClientAuthenticationOutputReference", jsii.get(self, "clientAuthentication"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInfo")
    def configuration_info(self) -> "MskClusterConfigurationInfoOutputReference":
        return typing.cast("MskClusterConfigurationInfoOutputReference", jsii.get(self, "configurationInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="currentVersion")
    def current_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "currentVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInfo")
    def encryption_info(self) -> "MskClusterEncryptionInfoOutputReference":
        return typing.cast("MskClusterEncryptionInfoOutputReference", jsii.get(self, "encryptionInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInfo")
    def logging_info(self) -> "MskClusterLoggingInfoOutputReference":
        return typing.cast("MskClusterLoggingInfoOutputReference", jsii.get(self, "loggingInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openMonitoring")
    def open_monitoring(self) -> "MskClusterOpenMonitoringOutputReference":
        return typing.cast("MskClusterOpenMonitoringOutputReference", jsii.get(self, "openMonitoring"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MskClusterTimeoutsOutputReference":
        return typing.cast("MskClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectString")
    def zookeeper_connect_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectString"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectStringTls")
    def zookeeper_connect_string_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectStringTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerNodeGroupInfoInput")
    def broker_node_group_info_input(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfo"]:
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfo"], jsii.get(self, "brokerNodeGroupInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientAuthenticationInput")
    def client_authentication_input(
        self,
    ) -> typing.Optional["MskClusterClientAuthentication"]:
        return typing.cast(typing.Optional["MskClusterClientAuthentication"], jsii.get(self, "clientAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInfoInput")
    def configuration_info_input(
        self,
    ) -> typing.Optional["MskClusterConfigurationInfo"]:
        return typing.cast(typing.Optional["MskClusterConfigurationInfo"], jsii.get(self, "configurationInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInfoInput")
    def encryption_info_input(self) -> typing.Optional["MskClusterEncryptionInfo"]:
        return typing.cast(typing.Optional["MskClusterEncryptionInfo"], jsii.get(self, "encryptionInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedMonitoringInput")
    def enhanced_monitoring_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enhancedMonitoringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersionInput")
    def kafka_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kafkaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInfoInput")
    def logging_info_input(self) -> typing.Optional["MskClusterLoggingInfo"]:
        return typing.cast(typing.Optional["MskClusterLoggingInfo"], jsii.get(self, "loggingInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodesInput")
    def number_of_broker_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfBrokerNodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openMonitoringInput")
    def open_monitoring_input(self) -> typing.Optional["MskClusterOpenMonitoring"]:
        return typing.cast(typing.Optional["MskClusterOpenMonitoring"], jsii.get(self, "openMonitoringInput"))

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
    def timeouts_input(self) -> typing.Optional["MskClusterTimeouts"]:
        return typing.cast(typing.Optional["MskClusterTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedMonitoring")
    def enhanced_monitoring(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enhancedMonitoring"))

    @enhanced_monitoring.setter
    def enhanced_monitoring(self, value: builtins.str) -> None:
        jsii.set(self, "enhancedMonitoring", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersion")
    def kafka_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kafkaVersion"))

    @kafka_version.setter
    def kafka_version(self, value: builtins.str) -> None:
        jsii.set(self, "kafkaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodes")
    def number_of_broker_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfBrokerNodes"))

    @number_of_broker_nodes.setter
    def number_of_broker_nodes(self, value: jsii.Number) -> None:
        jsii.set(self, "numberOfBrokerNodes", value)

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
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfo",
    jsii_struct_bases=[],
    name_mapping={
        "client_subnets": "clientSubnets",
        "ebs_volume_size": "ebsVolumeSize",
        "instance_type": "instanceType",
        "security_groups": "securityGroups",
        "az_distribution": "azDistribution",
    },
)
class MskClusterBrokerNodeGroupInfo:
    def __init__(
        self,
        *,
        client_subnets: typing.Sequence[builtins.str],
        ebs_volume_size: jsii.Number,
        instance_type: builtins.str,
        security_groups: typing.Sequence[builtins.str],
        az_distribution: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_subnets MskCluster#client_subnets}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_volume_size MskCluster#ebs_volume_size}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#instance_type MskCluster#instance_type}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#security_groups MskCluster#security_groups}.
        :param az_distribution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#az_distribution MskCluster#az_distribution}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_subnets": client_subnets,
            "ebs_volume_size": ebs_volume_size,
            "instance_type": instance_type,
            "security_groups": security_groups,
        }
        if az_distribution is not None:
            self._values["az_distribution"] = az_distribution

    @builtins.property
    def client_subnets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_subnets MskCluster#client_subnets}.'''
        result = self._values.get("client_subnets")
        assert result is not None, "Required property 'client_subnets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def ebs_volume_size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_volume_size MskCluster#ebs_volume_size}.'''
        result = self._values.get("ebs_volume_size")
        assert result is not None, "Required property 'ebs_volume_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#instance_type MskCluster#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_groups(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#security_groups MskCluster#security_groups}.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def az_distribution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#az_distribution MskCluster#az_distribution}.'''
        result = self._values.get("az_distribution")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterBrokerNodeGroupInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoOutputReference",
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

    @jsii.member(jsii_name="resetAzDistribution")
    def reset_az_distribution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzDistribution", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="azDistributionInput")
    def az_distribution_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azDistributionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSubnetsInput")
    def client_subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clientSubnetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeSizeInput")
    def ebs_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupsInput")
    def security_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="azDistribution")
    def az_distribution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azDistribution"))

    @az_distribution.setter
    def az_distribution(self, value: builtins.str) -> None:
        jsii.set(self, "azDistribution", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSubnets")
    def client_subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientSubnets"))

    @client_subnets.setter
    def client_subnets(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "clientSubnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeSize")
    def ebs_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeSize"))

    @ebs_volume_size.setter
    def ebs_volume_size(self, value: jsii.Number) -> None:
        jsii.set(self, "ebsVolumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterBrokerNodeGroupInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthentication",
    jsii_struct_bases=[],
    name_mapping={"sasl": "sasl", "tls": "tls"},
)
class MskClusterClientAuthentication:
    def __init__(
        self,
        *,
        sasl: typing.Optional["MskClusterClientAuthenticationSasl"] = None,
        tls: typing.Optional["MskClusterClientAuthenticationTls"] = None,
    ) -> None:
        '''
        :param sasl: sasl block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#sasl MskCluster#sasl}
        :param tls: tls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tls MskCluster#tls}
        '''
        if isinstance(sasl, dict):
            sasl = MskClusterClientAuthenticationSasl(**sasl)
        if isinstance(tls, dict):
            tls = MskClusterClientAuthenticationTls(**tls)
        self._values: typing.Dict[str, typing.Any] = {}
        if sasl is not None:
            self._values["sasl"] = sasl
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def sasl(self) -> typing.Optional["MskClusterClientAuthenticationSasl"]:
        '''sasl block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#sasl MskCluster#sasl}
        '''
        result = self._values.get("sasl")
        return typing.cast(typing.Optional["MskClusterClientAuthenticationSasl"], result)

    @builtins.property
    def tls(self) -> typing.Optional["MskClusterClientAuthenticationTls"]:
        '''tls block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tls MskCluster#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional["MskClusterClientAuthenticationTls"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterClientAuthentication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterClientAuthenticationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationOutputReference",
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

    @jsii.member(jsii_name="putSasl")
    def put_sasl(
        self,
        *,
        iam: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        scram: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param iam: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#iam MskCluster#iam}.
        :param scram: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#scram MskCluster#scram}.
        '''
        value = MskClusterClientAuthenticationSasl(iam=iam, scram=scram)

        return typing.cast(None, jsii.invoke(self, "putSasl", [value]))

    @jsii.member(jsii_name="putTls")
    def put_tls(
        self,
        *,
        certificate_authority_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param certificate_authority_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#certificate_authority_arns MskCluster#certificate_authority_arns}.
        '''
        value = MskClusterClientAuthenticationTls(
            certificate_authority_arns=certificate_authority_arns
        )

        return typing.cast(None, jsii.invoke(self, "putTls", [value]))

    @jsii.member(jsii_name="resetSasl")
    def reset_sasl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSasl", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sasl")
    def sasl(self) -> "MskClusterClientAuthenticationSaslOutputReference":
        return typing.cast("MskClusterClientAuthenticationSaslOutputReference", jsii.get(self, "sasl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tls")
    def tls(self) -> "MskClusterClientAuthenticationTlsOutputReference":
        return typing.cast("MskClusterClientAuthenticationTlsOutputReference", jsii.get(self, "tls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslInput")
    def sasl_input(self) -> typing.Optional["MskClusterClientAuthenticationSasl"]:
        return typing.cast(typing.Optional["MskClusterClientAuthenticationSasl"], jsii.get(self, "saslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsInput")
    def tls_input(self) -> typing.Optional["MskClusterClientAuthenticationTls"]:
        return typing.cast(typing.Optional["MskClusterClientAuthenticationTls"], jsii.get(self, "tlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterClientAuthentication]:
        return typing.cast(typing.Optional[MskClusterClientAuthentication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterClientAuthentication],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationSasl",
    jsii_struct_bases=[],
    name_mapping={"iam": "iam", "scram": "scram"},
)
class MskClusterClientAuthenticationSasl:
    def __init__(
        self,
        *,
        iam: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        scram: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param iam: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#iam MskCluster#iam}.
        :param scram: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#scram MskCluster#scram}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam is not None:
            self._values["iam"] = iam
        if scram is not None:
            self._values["scram"] = scram

    @builtins.property
    def iam(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#iam MskCluster#iam}.'''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def scram(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#scram MskCluster#scram}.'''
        result = self._values.get("scram")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterClientAuthenticationSasl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterClientAuthenticationSaslOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationSaslOutputReference",
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

    @jsii.member(jsii_name="resetIam")
    def reset_iam(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIam", []))

    @jsii.member(jsii_name="resetScram")
    def reset_scram(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScram", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamInput")
    def iam_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "iamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scramInput")
    def scram_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "scramInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iam")
    def iam(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "iam"))

    @iam.setter
    def iam(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "iam", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scram")
    def scram(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "scram"))

    @scram.setter
    def scram(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "scram", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterClientAuthenticationSasl]:
        return typing.cast(typing.Optional[MskClusterClientAuthenticationSasl], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterClientAuthenticationSasl],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationTls",
    jsii_struct_bases=[],
    name_mapping={"certificate_authority_arns": "certificateAuthorityArns"},
)
class MskClusterClientAuthenticationTls:
    def __init__(
        self,
        *,
        certificate_authority_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param certificate_authority_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#certificate_authority_arns MskCluster#certificate_authority_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if certificate_authority_arns is not None:
            self._values["certificate_authority_arns"] = certificate_authority_arns

    @builtins.property
    def certificate_authority_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#certificate_authority_arns MskCluster#certificate_authority_arns}.'''
        result = self._values.get("certificate_authority_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterClientAuthenticationTls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterClientAuthenticationTlsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationTlsOutputReference",
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

    @jsii.member(jsii_name="resetCertificateAuthorityArns")
    def reset_certificate_authority_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateAuthorityArns", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateAuthorityArnsInput")
    def certificate_authority_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "certificateAuthorityArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateAuthorityArns")
    def certificate_authority_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "certificateAuthorityArns"))

    @certificate_authority_arns.setter
    def certificate_authority_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "certificateAuthorityArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterClientAuthenticationTls]:
        return typing.cast(typing.Optional[MskClusterClientAuthenticationTls], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterClientAuthenticationTls],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "broker_node_group_info": "brokerNodeGroupInfo",
        "cluster_name": "clusterName",
        "kafka_version": "kafkaVersion",
        "number_of_broker_nodes": "numberOfBrokerNodes",
        "client_authentication": "clientAuthentication",
        "configuration_info": "configurationInfo",
        "encryption_info": "encryptionInfo",
        "enhanced_monitoring": "enhancedMonitoring",
        "logging_info": "loggingInfo",
        "open_monitoring": "openMonitoring",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class MskClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        broker_node_group_info: MskClusterBrokerNodeGroupInfo,
        cluster_name: builtins.str,
        kafka_version: builtins.str,
        number_of_broker_nodes: jsii.Number,
        client_authentication: typing.Optional[MskClusterClientAuthentication] = None,
        configuration_info: typing.Optional["MskClusterConfigurationInfo"] = None,
        encryption_info: typing.Optional["MskClusterEncryptionInfo"] = None,
        enhanced_monitoring: typing.Optional[builtins.str] = None,
        logging_info: typing.Optional["MskClusterLoggingInfo"] = None,
        open_monitoring: typing.Optional["MskClusterOpenMonitoring"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["MskClusterTimeouts"] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param broker_node_group_info: broker_node_group_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_node_group_info MskCluster#broker_node_group_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cluster_name MskCluster#cluster_name}.
        :param kafka_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#kafka_version MskCluster#kafka_version}.
        :param number_of_broker_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#number_of_broker_nodes MskCluster#number_of_broker_nodes}.
        :param client_authentication: client_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_authentication MskCluster#client_authentication}
        :param configuration_info: configuration_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#configuration_info MskCluster#configuration_info}
        :param encryption_info: encryption_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_info MskCluster#encryption_info}
        :param enhanced_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enhanced_monitoring MskCluster#enhanced_monitoring}.
        :param logging_info: logging_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#logging_info MskCluster#logging_info}
        :param open_monitoring: open_monitoring block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#open_monitoring MskCluster#open_monitoring}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags MskCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags_all MskCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#timeouts MskCluster#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(broker_node_group_info, dict):
            broker_node_group_info = MskClusterBrokerNodeGroupInfo(**broker_node_group_info)
        if isinstance(client_authentication, dict):
            client_authentication = MskClusterClientAuthentication(**client_authentication)
        if isinstance(configuration_info, dict):
            configuration_info = MskClusterConfigurationInfo(**configuration_info)
        if isinstance(encryption_info, dict):
            encryption_info = MskClusterEncryptionInfo(**encryption_info)
        if isinstance(logging_info, dict):
            logging_info = MskClusterLoggingInfo(**logging_info)
        if isinstance(open_monitoring, dict):
            open_monitoring = MskClusterOpenMonitoring(**open_monitoring)
        if isinstance(timeouts, dict):
            timeouts = MskClusterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "broker_node_group_info": broker_node_group_info,
            "cluster_name": cluster_name,
            "kafka_version": kafka_version,
            "number_of_broker_nodes": number_of_broker_nodes,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if client_authentication is not None:
            self._values["client_authentication"] = client_authentication
        if configuration_info is not None:
            self._values["configuration_info"] = configuration_info
        if encryption_info is not None:
            self._values["encryption_info"] = encryption_info
        if enhanced_monitoring is not None:
            self._values["enhanced_monitoring"] = enhanced_monitoring
        if logging_info is not None:
            self._values["logging_info"] = logging_info
        if open_monitoring is not None:
            self._values["open_monitoring"] = open_monitoring
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
    def broker_node_group_info(self) -> MskClusterBrokerNodeGroupInfo:
        '''broker_node_group_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_node_group_info MskCluster#broker_node_group_info}
        '''
        result = self._values.get("broker_node_group_info")
        assert result is not None, "Required property 'broker_node_group_info' is missing"
        return typing.cast(MskClusterBrokerNodeGroupInfo, result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cluster_name MskCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kafka_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#kafka_version MskCluster#kafka_version}.'''
        result = self._values.get("kafka_version")
        assert result is not None, "Required property 'kafka_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_broker_nodes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#number_of_broker_nodes MskCluster#number_of_broker_nodes}.'''
        result = self._values.get("number_of_broker_nodes")
        assert result is not None, "Required property 'number_of_broker_nodes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def client_authentication(self) -> typing.Optional[MskClusterClientAuthentication]:
        '''client_authentication block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_authentication MskCluster#client_authentication}
        '''
        result = self._values.get("client_authentication")
        return typing.cast(typing.Optional[MskClusterClientAuthentication], result)

    @builtins.property
    def configuration_info(self) -> typing.Optional["MskClusterConfigurationInfo"]:
        '''configuration_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#configuration_info MskCluster#configuration_info}
        '''
        result = self._values.get("configuration_info")
        return typing.cast(typing.Optional["MskClusterConfigurationInfo"], result)

    @builtins.property
    def encryption_info(self) -> typing.Optional["MskClusterEncryptionInfo"]:
        '''encryption_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_info MskCluster#encryption_info}
        '''
        result = self._values.get("encryption_info")
        return typing.cast(typing.Optional["MskClusterEncryptionInfo"], result)

    @builtins.property
    def enhanced_monitoring(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enhanced_monitoring MskCluster#enhanced_monitoring}.'''
        result = self._values.get("enhanced_monitoring")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_info(self) -> typing.Optional["MskClusterLoggingInfo"]:
        '''logging_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#logging_info MskCluster#logging_info}
        '''
        result = self._values.get("logging_info")
        return typing.cast(typing.Optional["MskClusterLoggingInfo"], result)

    @builtins.property
    def open_monitoring(self) -> typing.Optional["MskClusterOpenMonitoring"]:
        '''open_monitoring block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#open_monitoring MskCluster#open_monitoring}
        '''
        result = self._values.get("open_monitoring")
        return typing.cast(typing.Optional["MskClusterOpenMonitoring"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags MskCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags_all MskCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MskClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#timeouts MskCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MskClusterTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterConfigurationInfo",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "revision": "revision"},
)
class MskClusterConfigurationInfo:
    def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#arn MskCluster#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#revision MskCluster#revision}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "revision": revision,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#arn MskCluster#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#revision MskCluster#revision}.'''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterConfigurationInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterConfigurationInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterConfigurationInfoOutputReference",
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
    @jsii.member(jsii_name="revisionInput")
    def revision_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "revisionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revision")
    def revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "revision"))

    @revision.setter
    def revision(self, value: jsii.Number) -> None:
        jsii.set(self, "revision", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterConfigurationInfo]:
        return typing.cast(typing.Optional[MskClusterConfigurationInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterConfigurationInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfo",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_at_rest_kms_key_arn": "encryptionAtRestKmsKeyArn",
        "encryption_in_transit": "encryptionInTransit",
    },
)
class MskClusterEncryptionInfo:
    def __init__(
        self,
        *,
        encryption_at_rest_kms_key_arn: typing.Optional[builtins.str] = None,
        encryption_in_transit: typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"] = None,
    ) -> None:
        '''
        :param encryption_at_rest_kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_at_rest_kms_key_arn MskCluster#encryption_at_rest_kms_key_arn}.
        :param encryption_in_transit: encryption_in_transit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_in_transit MskCluster#encryption_in_transit}
        '''
        if isinstance(encryption_in_transit, dict):
            encryption_in_transit = MskClusterEncryptionInfoEncryptionInTransit(**encryption_in_transit)
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_at_rest_kms_key_arn is not None:
            self._values["encryption_at_rest_kms_key_arn"] = encryption_at_rest_kms_key_arn
        if encryption_in_transit is not None:
            self._values["encryption_in_transit"] = encryption_in_transit

    @builtins.property
    def encryption_at_rest_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_at_rest_kms_key_arn MskCluster#encryption_at_rest_kms_key_arn}.'''
        result = self._values.get("encryption_at_rest_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_in_transit(
        self,
    ) -> typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"]:
        '''encryption_in_transit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_in_transit MskCluster#encryption_in_transit}
        '''
        result = self._values.get("encryption_in_transit")
        return typing.cast(typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterEncryptionInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfoEncryptionInTransit",
    jsii_struct_bases=[],
    name_mapping={"client_broker": "clientBroker", "in_cluster": "inCluster"},
)
class MskClusterEncryptionInfoEncryptionInTransit:
    def __init__(
        self,
        *,
        client_broker: typing.Optional[builtins.str] = None,
        in_cluster: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param client_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_broker MskCluster#client_broker}.
        :param in_cluster: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#in_cluster MskCluster#in_cluster}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if client_broker is not None:
            self._values["client_broker"] = client_broker
        if in_cluster is not None:
            self._values["in_cluster"] = in_cluster

    @builtins.property
    def client_broker(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_broker MskCluster#client_broker}.'''
        result = self._values.get("client_broker")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def in_cluster(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#in_cluster MskCluster#in_cluster}.'''
        result = self._values.get("in_cluster")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterEncryptionInfoEncryptionInTransit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterEncryptionInfoEncryptionInTransitOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfoEncryptionInTransitOutputReference",
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

    @jsii.member(jsii_name="resetClientBroker")
    def reset_client_broker(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientBroker", []))

    @jsii.member(jsii_name="resetInCluster")
    def reset_in_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInCluster", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientBrokerInput")
    def client_broker_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientBrokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inClusterInput")
    def in_cluster_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "inClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientBroker")
    def client_broker(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientBroker"))

    @client_broker.setter
    def client_broker(self, value: builtins.str) -> None:
        jsii.set(self, "clientBroker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inCluster")
    def in_cluster(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "inCluster"))

    @in_cluster.setter
    def in_cluster(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "inCluster", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterEncryptionInfoEncryptionInTransit]:
        return typing.cast(typing.Optional[MskClusterEncryptionInfoEncryptionInTransit], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterEncryptionInfoEncryptionInTransit],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterEncryptionInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfoOutputReference",
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

    @jsii.member(jsii_name="putEncryptionInTransit")
    def put_encryption_in_transit(
        self,
        *,
        client_broker: typing.Optional[builtins.str] = None,
        in_cluster: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param client_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_broker MskCluster#client_broker}.
        :param in_cluster: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#in_cluster MskCluster#in_cluster}.
        '''
        value = MskClusterEncryptionInfoEncryptionInTransit(
            client_broker=client_broker, in_cluster=in_cluster
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionInTransit", [value]))

    @jsii.member(jsii_name="resetEncryptionAtRestKmsKeyArn")
    def reset_encryption_at_rest_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAtRestKmsKeyArn", []))

    @jsii.member(jsii_name="resetEncryptionInTransit")
    def reset_encryption_in_transit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionInTransit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInTransit")
    def encryption_in_transit(
        self,
    ) -> MskClusterEncryptionInfoEncryptionInTransitOutputReference:
        return typing.cast(MskClusterEncryptionInfoEncryptionInTransitOutputReference, jsii.get(self, "encryptionInTransit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionAtRestKmsKeyArnInput")
    def encryption_at_rest_kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionAtRestKmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInTransitInput")
    def encryption_in_transit_input(
        self,
    ) -> typing.Optional[MskClusterEncryptionInfoEncryptionInTransit]:
        return typing.cast(typing.Optional[MskClusterEncryptionInfoEncryptionInTransit], jsii.get(self, "encryptionInTransitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionAtRestKmsKeyArn")
    def encryption_at_rest_kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionAtRestKmsKeyArn"))

    @encryption_at_rest_kms_key_arn.setter
    def encryption_at_rest_kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionAtRestKmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterEncryptionInfo]:
        return typing.cast(typing.Optional[MskClusterEncryptionInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterEncryptionInfo]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfo",
    jsii_struct_bases=[],
    name_mapping={"broker_logs": "brokerLogs"},
)
class MskClusterLoggingInfo:
    def __init__(self, *, broker_logs: "MskClusterLoggingInfoBrokerLogs") -> None:
        '''
        :param broker_logs: broker_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_logs MskCluster#broker_logs}
        '''
        if isinstance(broker_logs, dict):
            broker_logs = MskClusterLoggingInfoBrokerLogs(**broker_logs)
        self._values: typing.Dict[str, typing.Any] = {
            "broker_logs": broker_logs,
        }

    @builtins.property
    def broker_logs(self) -> "MskClusterLoggingInfoBrokerLogs":
        '''broker_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_logs MskCluster#broker_logs}
        '''
        result = self._values.get("broker_logs")
        assert result is not None, "Required property 'broker_logs' is missing"
        return typing.cast("MskClusterLoggingInfoBrokerLogs", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogs",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_logs": "cloudwatchLogs",
        "firehose": "firehose",
        "s3": "s3",
    },
)
class MskClusterLoggingInfoBrokerLogs:
    def __init__(
        self,
        *,
        cloudwatch_logs: typing.Optional["MskClusterLoggingInfoBrokerLogsCloudwatchLogs"] = None,
        firehose: typing.Optional["MskClusterLoggingInfoBrokerLogsFirehose"] = None,
        s3: typing.Optional["MskClusterLoggingInfoBrokerLogsS3"] = None,
    ) -> None:
        '''
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cloudwatch_logs MskCluster#cloudwatch_logs}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#firehose MskCluster#firehose}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#s3 MskCluster#s3}
        '''
        if isinstance(cloudwatch_logs, dict):
            cloudwatch_logs = MskClusterLoggingInfoBrokerLogsCloudwatchLogs(**cloudwatch_logs)
        if isinstance(firehose, dict):
            firehose = MskClusterLoggingInfoBrokerLogsFirehose(**firehose)
        if isinstance(s3, dict):
            s3 = MskClusterLoggingInfoBrokerLogsS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {}
        if cloudwatch_logs is not None:
            self._values["cloudwatch_logs"] = cloudwatch_logs
        if firehose is not None:
            self._values["firehose"] = firehose
        if s3 is not None:
            self._values["s3"] = s3

    @builtins.property
    def cloudwatch_logs(
        self,
    ) -> typing.Optional["MskClusterLoggingInfoBrokerLogsCloudwatchLogs"]:
        '''cloudwatch_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cloudwatch_logs MskCluster#cloudwatch_logs}
        '''
        result = self._values.get("cloudwatch_logs")
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsCloudwatchLogs"], result)

    @builtins.property
    def firehose(self) -> typing.Optional["MskClusterLoggingInfoBrokerLogsFirehose"]:
        '''firehose block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#firehose MskCluster#firehose}
        '''
        result = self._values.get("firehose")
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsFirehose"], result)

    @builtins.property
    def s3(self) -> typing.Optional["MskClusterLoggingInfoBrokerLogsS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#s3 MskCluster#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsS3"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsCloudwatchLogs",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "log_group": "logGroup"},
)
class MskClusterLoggingInfoBrokerLogsCloudwatchLogs:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        log_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param log_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#log_group MskCluster#log_group}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if log_group is not None:
            self._values["log_group"] = log_group

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def log_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#log_group MskCluster#log_group}.'''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogsCloudwatchLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference",
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

    @jsii.member(jsii_name="resetLogGroup")
    def reset_log_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogGroup", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupInput")
    def log_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: builtins.str) -> None:
        jsii.set(self, "logGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsFirehose",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "delivery_stream": "deliveryStream"},
)
class MskClusterLoggingInfoBrokerLogsFirehose:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        delivery_stream: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param delivery_stream: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delivery_stream MskCluster#delivery_stream}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if delivery_stream is not None:
            self._values["delivery_stream"] = delivery_stream

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def delivery_stream(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delivery_stream MskCluster#delivery_stream}.'''
        result = self._values.get("delivery_stream")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogsFirehose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterLoggingInfoBrokerLogsFirehoseOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsFirehoseOutputReference",
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

    @jsii.member(jsii_name="resetDeliveryStream")
    def reset_delivery_stream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryStream", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamInput")
    def delivery_stream_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStream"))

    @delivery_stream.setter
    def delivery_stream(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStream", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterLoggingInfoBrokerLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsOutputReference",
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

    @jsii.member(jsii_name="putCloudwatchLogs")
    def put_cloudwatch_logs(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        log_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param log_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#log_group MskCluster#log_group}.
        '''
        value = MskClusterLoggingInfoBrokerLogsCloudwatchLogs(
            enabled=enabled, log_group=log_group
        )

        return typing.cast(None, jsii.invoke(self, "putCloudwatchLogs", [value]))

    @jsii.member(jsii_name="putFirehose")
    def put_firehose(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        delivery_stream: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param delivery_stream: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delivery_stream MskCluster#delivery_stream}.
        '''
        value = MskClusterLoggingInfoBrokerLogsFirehose(
            enabled=enabled, delivery_stream=delivery_stream
        )

        return typing.cast(None, jsii.invoke(self, "putFirehose", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#bucket MskCluster#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prefix MskCluster#prefix}.
        '''
        value = MskClusterLoggingInfoBrokerLogsS3(
            enabled=enabled, bucket=bucket, prefix=prefix
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="resetCloudwatchLogs")
    def reset_cloudwatch_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogs", []))

    @jsii.member(jsii_name="resetFirehose")
    def reset_firehose(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehose", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogs")
    def cloudwatch_logs(
        self,
    ) -> MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference:
        return typing.cast(MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference, jsii.get(self, "cloudwatchLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehose")
    def firehose(self) -> MskClusterLoggingInfoBrokerLogsFirehoseOutputReference:
        return typing.cast(MskClusterLoggingInfoBrokerLogsFirehoseOutputReference, jsii.get(self, "firehose"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "MskClusterLoggingInfoBrokerLogsS3OutputReference":
        return typing.cast("MskClusterLoggingInfoBrokerLogsS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsInput")
    def cloudwatch_logs_input(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs], jsii.get(self, "cloudwatchLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseInput")
    def firehose_input(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose], jsii.get(self, "firehoseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["MskClusterLoggingInfoBrokerLogsS3"]:
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterLoggingInfoBrokerLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsS3",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "bucket": "bucket", "prefix": "prefix"},
)
class MskClusterLoggingInfoBrokerLogsS3:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#bucket MskCluster#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prefix MskCluster#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if bucket is not None:
            self._values["bucket"] = bucket
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#bucket MskCluster#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prefix MskCluster#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogsS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterLoggingInfoBrokerLogsS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsS3OutputReference",
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

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterLoggingInfoBrokerLogsS3]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogsS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterLoggingInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoOutputReference",
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

    @jsii.member(jsii_name="putBrokerLogs")
    def put_broker_logs(
        self,
        *,
        cloudwatch_logs: typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs] = None,
        firehose: typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose] = None,
        s3: typing.Optional[MskClusterLoggingInfoBrokerLogsS3] = None,
    ) -> None:
        '''
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cloudwatch_logs MskCluster#cloudwatch_logs}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#firehose MskCluster#firehose}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#s3 MskCluster#s3}
        '''
        value = MskClusterLoggingInfoBrokerLogs(
            cloudwatch_logs=cloudwatch_logs, firehose=firehose, s3=s3
        )

        return typing.cast(None, jsii.invoke(self, "putBrokerLogs", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerLogs")
    def broker_logs(self) -> MskClusterLoggingInfoBrokerLogsOutputReference:
        return typing.cast(MskClusterLoggingInfoBrokerLogsOutputReference, jsii.get(self, "brokerLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerLogsInput")
    def broker_logs_input(self) -> typing.Optional[MskClusterLoggingInfoBrokerLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogs], jsii.get(self, "brokerLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterLoggingInfo]:
        return typing.cast(typing.Optional[MskClusterLoggingInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterLoggingInfo]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoring",
    jsii_struct_bases=[],
    name_mapping={"prometheus": "prometheus"},
)
class MskClusterOpenMonitoring:
    def __init__(self, *, prometheus: "MskClusterOpenMonitoringPrometheus") -> None:
        '''
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prometheus MskCluster#prometheus}
        '''
        if isinstance(prometheus, dict):
            prometheus = MskClusterOpenMonitoringPrometheus(**prometheus)
        self._values: typing.Dict[str, typing.Any] = {
            "prometheus": prometheus,
        }

    @builtins.property
    def prometheus(self) -> "MskClusterOpenMonitoringPrometheus":
        '''prometheus block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prometheus MskCluster#prometheus}
        '''
        result = self._values.get("prometheus")
        assert result is not None, "Required property 'prometheus' is missing"
        return typing.cast("MskClusterOpenMonitoringPrometheus", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoring(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterOpenMonitoringOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringOutputReference",
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

    @jsii.member(jsii_name="putPrometheus")
    def put_prometheus(
        self,
        *,
        jmx_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"] = None,
        node_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"] = None,
    ) -> None:
        '''
        :param jmx_exporter: jmx_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#jmx_exporter MskCluster#jmx_exporter}
        :param node_exporter: node_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#node_exporter MskCluster#node_exporter}
        '''
        value = MskClusterOpenMonitoringPrometheus(
            jmx_exporter=jmx_exporter, node_exporter=node_exporter
        )

        return typing.cast(None, jsii.invoke(self, "putPrometheus", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prometheus")
    def prometheus(self) -> "MskClusterOpenMonitoringPrometheusOutputReference":
        return typing.cast("MskClusterOpenMonitoringPrometheusOutputReference", jsii.get(self, "prometheus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prometheusInput")
    def prometheus_input(self) -> typing.Optional["MskClusterOpenMonitoringPrometheus"]:
        return typing.cast(typing.Optional["MskClusterOpenMonitoringPrometheus"], jsii.get(self, "prometheusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterOpenMonitoring]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoring], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterOpenMonitoring]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheus",
    jsii_struct_bases=[],
    name_mapping={"jmx_exporter": "jmxExporter", "node_exporter": "nodeExporter"},
)
class MskClusterOpenMonitoringPrometheus:
    def __init__(
        self,
        *,
        jmx_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"] = None,
        node_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"] = None,
    ) -> None:
        '''
        :param jmx_exporter: jmx_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#jmx_exporter MskCluster#jmx_exporter}
        :param node_exporter: node_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#node_exporter MskCluster#node_exporter}
        '''
        if isinstance(jmx_exporter, dict):
            jmx_exporter = MskClusterOpenMonitoringPrometheusJmxExporter(**jmx_exporter)
        if isinstance(node_exporter, dict):
            node_exporter = MskClusterOpenMonitoringPrometheusNodeExporter(**node_exporter)
        self._values: typing.Dict[str, typing.Any] = {}
        if jmx_exporter is not None:
            self._values["jmx_exporter"] = jmx_exporter
        if node_exporter is not None:
            self._values["node_exporter"] = node_exporter

    @builtins.property
    def jmx_exporter(
        self,
    ) -> typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"]:
        '''jmx_exporter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#jmx_exporter MskCluster#jmx_exporter}
        '''
        result = self._values.get("jmx_exporter")
        return typing.cast(typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"], result)

    @builtins.property
    def node_exporter(
        self,
    ) -> typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"]:
        '''node_exporter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#node_exporter MskCluster#node_exporter}
        '''
        result = self._values.get("node_exporter")
        return typing.cast(typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoringPrometheus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusJmxExporter",
    jsii_struct_bases=[],
    name_mapping={"enabled_in_broker": "enabledInBroker"},
)
class MskClusterOpenMonitoringPrometheusJmxExporter:
    def __init__(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled_in_broker": enabled_in_broker,
        }

    @builtins.property
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.'''
        result = self._values.get("enabled_in_broker")
        assert result is not None, "Required property 'enabled_in_broker' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoringPrometheusJmxExporter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterOpenMonitoringPrometheusJmxExporterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusJmxExporterOutputReference",
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
    @jsii.member(jsii_name="enabledInBrokerInput")
    def enabled_in_broker_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInBrokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInBroker")
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabledInBroker"))

    @enabled_in_broker.setter
    def enabled_in_broker(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enabledInBroker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusNodeExporter",
    jsii_struct_bases=[],
    name_mapping={"enabled_in_broker": "enabledInBroker"},
)
class MskClusterOpenMonitoringPrometheusNodeExporter:
    def __init__(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled_in_broker": enabled_in_broker,
        }

    @builtins.property
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.'''
        result = self._values.get("enabled_in_broker")
        assert result is not None, "Required property 'enabled_in_broker' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoringPrometheusNodeExporter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterOpenMonitoringPrometheusNodeExporterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusNodeExporterOutputReference",
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
    @jsii.member(jsii_name="enabledInBrokerInput")
    def enabled_in_broker_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInBrokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInBroker")
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabledInBroker"))

    @enabled_in_broker.setter
    def enabled_in_broker(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enabledInBroker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterOpenMonitoringPrometheusOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusOutputReference",
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

    @jsii.member(jsii_name="putJmxExporter")
    def put_jmx_exporter(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        value = MskClusterOpenMonitoringPrometheusJmxExporter(
            enabled_in_broker=enabled_in_broker
        )

        return typing.cast(None, jsii.invoke(self, "putJmxExporter", [value]))

    @jsii.member(jsii_name="putNodeExporter")
    def put_node_exporter(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        value = MskClusterOpenMonitoringPrometheusNodeExporter(
            enabled_in_broker=enabled_in_broker
        )

        return typing.cast(None, jsii.invoke(self, "putNodeExporter", [value]))

    @jsii.member(jsii_name="resetJmxExporter")
    def reset_jmx_exporter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJmxExporter", []))

    @jsii.member(jsii_name="resetNodeExporter")
    def reset_node_exporter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeExporter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jmxExporter")
    def jmx_exporter(
        self,
    ) -> MskClusterOpenMonitoringPrometheusJmxExporterOutputReference:
        return typing.cast(MskClusterOpenMonitoringPrometheusJmxExporterOutputReference, jsii.get(self, "jmxExporter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeExporter")
    def node_exporter(
        self,
    ) -> MskClusterOpenMonitoringPrometheusNodeExporterOutputReference:
        return typing.cast(MskClusterOpenMonitoringPrometheusNodeExporterOutputReference, jsii.get(self, "nodeExporter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jmxExporterInput")
    def jmx_exporter_input(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter], jsii.get(self, "jmxExporterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeExporterInput")
    def node_exporter_input(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter], jsii.get(self, "nodeExporterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterOpenMonitoringPrometheus]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterOpenMonitoringPrometheus],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class MskClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#create MskCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delete MskCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#update MskCluster#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#create MskCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delete MskCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#update MskCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[MskClusterTimeouts]:
        return typing.cast(typing.Optional[MskClusterTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class MskConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration aws_msk_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        server_properties: builtins.str,
        description: typing.Optional[builtins.str] = None,
        kafka_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration aws_msk_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#name MskConfiguration#name}.
        :param server_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#server_properties MskConfiguration#server_properties}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#description MskConfiguration#description}.
        :param kafka_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#kafka_versions MskConfiguration#kafka_versions}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskConfigurationConfig(
            name=name,
            server_properties=server_properties,
            description=description,
            kafka_versions=kafka_versions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetKafkaVersions")
    def reset_kafka_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKafkaVersions", []))

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
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersionsInput")
    def kafka_versions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "kafkaVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverPropertiesInput")
    def server_properties_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersions")
    def kafka_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "kafkaVersions"))

    @kafka_versions.setter
    def kafka_versions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "kafkaVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverProperties")
    def server_properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverProperties"))

    @server_properties.setter
    def server_properties(self, value: builtins.str) -> None:
        jsii.set(self, "serverProperties", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "server_properties": "serverProperties",
        "description": "description",
        "kafka_versions": "kafkaVersions",
    },
)
class MskConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        server_properties: builtins.str,
        description: typing.Optional[builtins.str] = None,
        kafka_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#name MskConfiguration#name}.
        :param server_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#server_properties MskConfiguration#server_properties}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#description MskConfiguration#description}.
        :param kafka_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#kafka_versions MskConfiguration#kafka_versions}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "server_properties": server_properties,
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
        if kafka_versions is not None:
            self._values["kafka_versions"] = kafka_versions

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#name MskConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_properties(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#server_properties MskConfiguration#server_properties}.'''
        result = self._values.get("server_properties")
        assert result is not None, "Required property 'server_properties' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#description MskConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kafka_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#kafka_versions MskConfiguration#kafka_versions}.'''
        result = self._values.get("kafka_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskScramSecretAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskScramSecretAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association aws_msk_scram_secret_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_arn: builtins.str,
        secret_arn_list: typing.Sequence[builtins.str],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association aws_msk_scram_secret_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#cluster_arn MskScramSecretAssociation#cluster_arn}.
        :param secret_arn_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#secret_arn_list MskScramSecretAssociation#secret_arn_list}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskScramSecretAssociationConfig(
            cluster_arn=cluster_arn,
            secret_arn_list=secret_arn_list,
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
    @jsii.member(jsii_name="clusterArnInput")
    def cluster_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArnListInput")
    def secret_arn_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secretArnListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @cluster_arn.setter
    def cluster_arn(self, value: builtins.str) -> None:
        jsii.set(self, "clusterArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArnList")
    def secret_arn_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secretArnList"))

    @secret_arn_list.setter
    def secret_arn_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "secretArnList", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskScramSecretAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_arn": "clusterArn",
        "secret_arn_list": "secretArnList",
    },
)
class MskScramSecretAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_arn: builtins.str,
        secret_arn_list: typing.Sequence[builtins.str],
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#cluster_arn MskScramSecretAssociation#cluster_arn}.
        :param secret_arn_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#secret_arn_list MskScramSecretAssociation#secret_arn_list}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_arn": cluster_arn,
            "secret_arn_list": secret_arn_list,
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
    def cluster_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#cluster_arn MskScramSecretAssociation#cluster_arn}.'''
        result = self._values.get("cluster_arn")
        assert result is not None, "Required property 'cluster_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_arn_list(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#secret_arn_list MskScramSecretAssociation#secret_arn_list}.'''
        result = self._values.get("secret_arn_list")
        assert result is not None, "Required property 'secret_arn_list' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskScramSecretAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPlugin(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin aws_mskconnect_custom_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content_type: builtins.str,
        location: "MskconnectCustomPluginLocation",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["MskconnectCustomPluginTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin aws_mskconnect_custom_plugin} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#content_type MskconnectCustomPlugin#content_type}.
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#location MskconnectCustomPlugin#location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#name MskconnectCustomPlugin#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#description MskconnectCustomPlugin#description}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#timeouts MskconnectCustomPlugin#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskconnectCustomPluginConfig(
            content_type=content_type,
            location=location,
            name=name,
            description=description,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLocation")
    def put_location(self, *, s3: "MskconnectCustomPluginLocationS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#s3 MskconnectCustomPlugin#s3}
        '''
        value = MskconnectCustomPluginLocation(s3=s3)

        return typing.cast(None, jsii.invoke(self, "putLocation", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#create MskconnectCustomPlugin#create}.
        '''
        value = MskconnectCustomPluginTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> "MskconnectCustomPluginLocationOutputReference":
        return typing.cast("MskconnectCustomPluginLocationOutputReference", jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MskconnectCustomPluginTimeoutsOutputReference":
        return typing.cast("MskconnectCustomPluginTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional["MskconnectCustomPluginLocation"]:
        return typing.cast(typing.Optional["MskconnectCustomPluginLocation"], jsii.get(self, "locationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["MskconnectCustomPluginTimeouts"]:
        return typing.cast(typing.Optional["MskconnectCustomPluginTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        jsii.set(self, "contentType", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content_type": "contentType",
        "location": "location",
        "name": "name",
        "description": "description",
        "timeouts": "timeouts",
    },
)
class MskconnectCustomPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content_type: builtins.str,
        location: "MskconnectCustomPluginLocation",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["MskconnectCustomPluginTimeouts"] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#content_type MskconnectCustomPlugin#content_type}.
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#location MskconnectCustomPlugin#location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#name MskconnectCustomPlugin#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#description MskconnectCustomPlugin#description}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#timeouts MskconnectCustomPlugin#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(location, dict):
            location = MskconnectCustomPluginLocation(**location)
        if isinstance(timeouts, dict):
            timeouts = MskconnectCustomPluginTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "content_type": content_type,
            "location": location,
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
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#content_type MskconnectCustomPlugin#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> "MskconnectCustomPluginLocation":
        '''location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#location MskconnectCustomPlugin#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast("MskconnectCustomPluginLocation", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#name MskconnectCustomPlugin#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#description MskconnectCustomPlugin#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MskconnectCustomPluginTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#timeouts MskconnectCustomPlugin#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MskconnectCustomPluginTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocation",
    jsii_struct_bases=[],
    name_mapping={"s3": "s3"},
)
class MskconnectCustomPluginLocation:
    def __init__(self, *, s3: "MskconnectCustomPluginLocationS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#s3 MskconnectCustomPlugin#s3}
        '''
        if isinstance(s3, dict):
            s3 = MskconnectCustomPluginLocationS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {
            "s3": s3,
        }

    @builtins.property
    def s3(self) -> "MskconnectCustomPluginLocationS3":
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#s3 MskconnectCustomPlugin#s3}
        '''
        result = self._values.get("s3")
        assert result is not None, "Required property 's3' is missing"
        return typing.cast("MskconnectCustomPluginLocationS3", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPluginLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocationOutputReference",
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

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        bucket_arn: builtins.str,
        file_key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#bucket_arn MskconnectCustomPlugin#bucket_arn}.
        :param file_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#file_key MskconnectCustomPlugin#file_key}.
        :param object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#object_version MskconnectCustomPlugin#object_version}.
        '''
        value = MskconnectCustomPluginLocationS3(
            bucket_arn=bucket_arn, file_key=file_key, object_version=object_version
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "MskconnectCustomPluginLocationS3OutputReference":
        return typing.cast("MskconnectCustomPluginLocationS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["MskconnectCustomPluginLocationS3"]:
        return typing.cast(typing.Optional["MskconnectCustomPluginLocationS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectCustomPluginLocation]:
        return typing.cast(typing.Optional[MskconnectCustomPluginLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectCustomPluginLocation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocationS3",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "file_key": "fileKey",
        "object_version": "objectVersion",
    },
)
class MskconnectCustomPluginLocationS3:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        file_key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#bucket_arn MskconnectCustomPlugin#bucket_arn}.
        :param file_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#file_key MskconnectCustomPlugin#file_key}.
        :param object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#object_version MskconnectCustomPlugin#object_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
            "file_key": file_key,
        }
        if object_version is not None:
            self._values["object_version"] = object_version

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#bucket_arn MskconnectCustomPlugin#bucket_arn}.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#file_key MskconnectCustomPlugin#file_key}.'''
        result = self._values.get("file_key")
        assert result is not None, "Required property 'file_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#object_version MskconnectCustomPlugin#object_version}.'''
        result = self._values.get("object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginLocationS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPluginLocationS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocationS3OutputReference",
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

    @jsii.member(jsii_name="resetObjectVersion")
    def reset_object_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArnInput")
    def bucket_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileKeyInput")
    def file_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectVersionInput")
    def object_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketArn"))

    @bucket_arn.setter
    def bucket_arn(self, value: builtins.str) -> None:
        jsii.set(self, "bucketArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileKey")
    def file_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileKey"))

    @file_key.setter
    def file_key(self, value: builtins.str) -> None:
        jsii.set(self, "fileKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectVersion")
    def object_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectVersion"))

    @object_version.setter
    def object_version(self, value: builtins.str) -> None:
        jsii.set(self, "objectVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectCustomPluginLocationS3]:
        return typing.cast(typing.Optional[MskconnectCustomPluginLocationS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectCustomPluginLocationS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class MskconnectCustomPluginTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#create MskconnectCustomPlugin#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#create MskconnectCustomPlugin#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPluginTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[MskconnectCustomPluginTimeouts]:
        return typing.cast(typing.Optional[MskconnectCustomPluginTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectCustomPluginTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectWorkerConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectWorkerConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration aws_mskconnect_worker_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        properties_file_content: builtins.str,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration aws_mskconnect_worker_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#name MskconnectWorkerConfiguration#name}.
        :param properties_file_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#properties_file_content MskconnectWorkerConfiguration#properties_file_content}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#description MskconnectWorkerConfiguration#description}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskconnectWorkerConfigurationConfig(
            name=name,
            properties_file_content=properties_file_content,
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
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesFileContentInput")
    def properties_file_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propertiesFileContentInput"))

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
    @jsii.member(jsii_name="propertiesFileContent")
    def properties_file_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "propertiesFileContent"))

    @properties_file_content.setter
    def properties_file_content(self, value: builtins.str) -> None:
        jsii.set(self, "propertiesFileContent", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectWorkerConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "properties_file_content": "propertiesFileContent",
        "description": "description",
    },
)
class MskconnectWorkerConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        properties_file_content: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#name MskconnectWorkerConfiguration#name}.
        :param properties_file_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#properties_file_content MskconnectWorkerConfiguration#properties_file_content}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#description MskconnectWorkerConfiguration#description}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "properties_file_content": properties_file_content,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#name MskconnectWorkerConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def properties_file_content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#properties_file_content MskconnectWorkerConfiguration#properties_file_content}.'''
        result = self._values.get("properties_file_content")
        assert result is not None, "Required property 'properties_file_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#description MskconnectWorkerConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectWorkerConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsMskBrokerNodes",
    "DataAwsMskBrokerNodesConfig",
    "DataAwsMskBrokerNodesNodeInfoList",
    "DataAwsMskCluster",
    "DataAwsMskClusterConfig",
    "DataAwsMskConfiguration",
    "DataAwsMskConfigurationConfig",
    "DataAwsMskKafkaVersion",
    "DataAwsMskKafkaVersionConfig",
    "DataAwsMskconnectCustomPlugin",
    "DataAwsMskconnectCustomPluginConfig",
    "DataAwsMskconnectWorkerConfiguration",
    "DataAwsMskconnectWorkerConfigurationConfig",
    "MskCluster",
    "MskClusterBrokerNodeGroupInfo",
    "MskClusterBrokerNodeGroupInfoOutputReference",
    "MskClusterClientAuthentication",
    "MskClusterClientAuthenticationOutputReference",
    "MskClusterClientAuthenticationSasl",
    "MskClusterClientAuthenticationSaslOutputReference",
    "MskClusterClientAuthenticationTls",
    "MskClusterClientAuthenticationTlsOutputReference",
    "MskClusterConfig",
    "MskClusterConfigurationInfo",
    "MskClusterConfigurationInfoOutputReference",
    "MskClusterEncryptionInfo",
    "MskClusterEncryptionInfoEncryptionInTransit",
    "MskClusterEncryptionInfoEncryptionInTransitOutputReference",
    "MskClusterEncryptionInfoOutputReference",
    "MskClusterLoggingInfo",
    "MskClusterLoggingInfoBrokerLogs",
    "MskClusterLoggingInfoBrokerLogsCloudwatchLogs",
    "MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference",
    "MskClusterLoggingInfoBrokerLogsFirehose",
    "MskClusterLoggingInfoBrokerLogsFirehoseOutputReference",
    "MskClusterLoggingInfoBrokerLogsOutputReference",
    "MskClusterLoggingInfoBrokerLogsS3",
    "MskClusterLoggingInfoBrokerLogsS3OutputReference",
    "MskClusterLoggingInfoOutputReference",
    "MskClusterOpenMonitoring",
    "MskClusterOpenMonitoringOutputReference",
    "MskClusterOpenMonitoringPrometheus",
    "MskClusterOpenMonitoringPrometheusJmxExporter",
    "MskClusterOpenMonitoringPrometheusJmxExporterOutputReference",
    "MskClusterOpenMonitoringPrometheusNodeExporter",
    "MskClusterOpenMonitoringPrometheusNodeExporterOutputReference",
    "MskClusterOpenMonitoringPrometheusOutputReference",
    "MskClusterTimeouts",
    "MskClusterTimeoutsOutputReference",
    "MskConfiguration",
    "MskConfigurationConfig",
    "MskScramSecretAssociation",
    "MskScramSecretAssociationConfig",
    "MskconnectCustomPlugin",
    "MskconnectCustomPluginConfig",
    "MskconnectCustomPluginLocation",
    "MskconnectCustomPluginLocationOutputReference",
    "MskconnectCustomPluginLocationS3",
    "MskconnectCustomPluginLocationS3OutputReference",
    "MskconnectCustomPluginTimeouts",
    "MskconnectCustomPluginTimeoutsOutputReference",
    "MskconnectWorkerConfiguration",
    "MskconnectWorkerConfigurationConfig",
]

publication.publish()
