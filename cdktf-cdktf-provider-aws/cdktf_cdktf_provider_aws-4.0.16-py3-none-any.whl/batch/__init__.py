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


class BatchComputeEnvironment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment aws_batch_compute_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        type: builtins.str,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_environment_name_prefix: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional["BatchComputeEnvironmentComputeResources"] = None,
        service_role: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment aws_batch_compute_environment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name BatchComputeEnvironment#compute_environment_name}.
        :param compute_environment_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name_prefix BatchComputeEnvironment#compute_environment_name_prefix}.
        :param compute_resources: compute_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_resources BatchComputeEnvironment#compute_resources}
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#service_role BatchComputeEnvironment#service_role}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#state BatchComputeEnvironment#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags_all BatchComputeEnvironment#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BatchComputeEnvironmentConfig(
            type=type,
            compute_environment_name=compute_environment_name,
            compute_environment_name_prefix=compute_environment_name_prefix,
            compute_resources=compute_resources,
            service_role=service_role,
            state=state,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putComputeResources")
    def put_compute_resources(
        self,
        *,
        max_vcpus: jsii.Number,
        security_group_ids: typing.Sequence[builtins.str],
        subnets: typing.Sequence[builtins.str],
        type: builtins.str,
        allocation_strategy: typing.Optional[builtins.str] = None,
        bid_percentage: typing.Optional[jsii.Number] = None,
        desired_vcpus: typing.Optional[jsii.Number] = None,
        ec2_configuration: typing.Optional["BatchComputeEnvironmentComputeResourcesEc2Configuration"] = None,
        ec2_key_pair: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        launch_template: typing.Optional["BatchComputeEnvironmentComputeResourcesLaunchTemplate"] = None,
        min_vcpus: typing.Optional[jsii.Number] = None,
        spot_iam_fleet_role: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param max_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#max_vcpus BatchComputeEnvironment#max_vcpus}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#security_group_ids BatchComputeEnvironment#security_group_ids}.
        :param subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#subnets BatchComputeEnvironment#subnets}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#allocation_strategy BatchComputeEnvironment#allocation_strategy}.
        :param bid_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#bid_percentage BatchComputeEnvironment#bid_percentage}.
        :param desired_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#desired_vcpus BatchComputeEnvironment#desired_vcpus}.
        :param ec2_configuration: ec2_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_configuration BatchComputeEnvironment#ec2_configuration}
        :param ec2_key_pair: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_key_pair BatchComputeEnvironment#ec2_key_pair}.
        :param image_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id BatchComputeEnvironment#image_id}.
        :param instance_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_role BatchComputeEnvironment#instance_role}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_type BatchComputeEnvironment#instance_type}.
        :param launch_template: launch_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template BatchComputeEnvironment#launch_template}
        :param min_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#min_vcpus BatchComputeEnvironment#min_vcpus}.
        :param spot_iam_fleet_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#spot_iam_fleet_role BatchComputeEnvironment#spot_iam_fleet_role}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        '''
        value = BatchComputeEnvironmentComputeResources(
            max_vcpus=max_vcpus,
            security_group_ids=security_group_ids,
            subnets=subnets,
            type=type,
            allocation_strategy=allocation_strategy,
            bid_percentage=bid_percentage,
            desired_vcpus=desired_vcpus,
            ec2_configuration=ec2_configuration,
            ec2_key_pair=ec2_key_pair,
            image_id=image_id,
            instance_role=instance_role,
            instance_type=instance_type,
            launch_template=launch_template,
            min_vcpus=min_vcpus,
            spot_iam_fleet_role=spot_iam_fleet_role,
            tags=tags,
        )

        return typing.cast(None, jsii.invoke(self, "putComputeResources", [value]))

    @jsii.member(jsii_name="resetComputeEnvironmentName")
    def reset_compute_environment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeEnvironmentName", []))

    @jsii.member(jsii_name="resetComputeEnvironmentNamePrefix")
    def reset_compute_environment_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeEnvironmentNamePrefix", []))

    @jsii.member(jsii_name="resetComputeResources")
    def reset_compute_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeResources", []))

    @jsii.member(jsii_name="resetServiceRole")
    def reset_service_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceRole", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

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
    @jsii.member(jsii_name="computeResources")
    def compute_resources(
        self,
    ) -> "BatchComputeEnvironmentComputeResourcesOutputReference":
        return typing.cast("BatchComputeEnvironmentComputeResourcesOutputReference", jsii.get(self, "computeResources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsClusterArn")
    def ecs_cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecsClusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNameInput")
    def compute_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNamePrefixInput")
    def compute_environment_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentNamePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeResourcesInput")
    def compute_resources_input(
        self,
    ) -> typing.Optional["BatchComputeEnvironmentComputeResources"]:
        return typing.cast(typing.Optional["BatchComputeEnvironmentComputeResources"], jsii.get(self, "computeResourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleInput")
    def service_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))

    @compute_environment_name.setter
    def compute_environment_name(self, value: builtins.str) -> None:
        jsii.set(self, "computeEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNamePrefix")
    def compute_environment_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentNamePrefix"))

    @compute_environment_name_prefix.setter
    def compute_environment_name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "computeEnvironmentNamePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        jsii.set(self, "serviceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResources",
    jsii_struct_bases=[],
    name_mapping={
        "max_vcpus": "maxVcpus",
        "security_group_ids": "securityGroupIds",
        "subnets": "subnets",
        "type": "type",
        "allocation_strategy": "allocationStrategy",
        "bid_percentage": "bidPercentage",
        "desired_vcpus": "desiredVcpus",
        "ec2_configuration": "ec2Configuration",
        "ec2_key_pair": "ec2KeyPair",
        "image_id": "imageId",
        "instance_role": "instanceRole",
        "instance_type": "instanceType",
        "launch_template": "launchTemplate",
        "min_vcpus": "minVcpus",
        "spot_iam_fleet_role": "spotIamFleetRole",
        "tags": "tags",
    },
)
class BatchComputeEnvironmentComputeResources:
    def __init__(
        self,
        *,
        max_vcpus: jsii.Number,
        security_group_ids: typing.Sequence[builtins.str],
        subnets: typing.Sequence[builtins.str],
        type: builtins.str,
        allocation_strategy: typing.Optional[builtins.str] = None,
        bid_percentage: typing.Optional[jsii.Number] = None,
        desired_vcpus: typing.Optional[jsii.Number] = None,
        ec2_configuration: typing.Optional["BatchComputeEnvironmentComputeResourcesEc2Configuration"] = None,
        ec2_key_pair: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        launch_template: typing.Optional["BatchComputeEnvironmentComputeResourcesLaunchTemplate"] = None,
        min_vcpus: typing.Optional[jsii.Number] = None,
        spot_iam_fleet_role: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param max_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#max_vcpus BatchComputeEnvironment#max_vcpus}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#security_group_ids BatchComputeEnvironment#security_group_ids}.
        :param subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#subnets BatchComputeEnvironment#subnets}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param allocation_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#allocation_strategy BatchComputeEnvironment#allocation_strategy}.
        :param bid_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#bid_percentage BatchComputeEnvironment#bid_percentage}.
        :param desired_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#desired_vcpus BatchComputeEnvironment#desired_vcpus}.
        :param ec2_configuration: ec2_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_configuration BatchComputeEnvironment#ec2_configuration}
        :param ec2_key_pair: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_key_pair BatchComputeEnvironment#ec2_key_pair}.
        :param image_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id BatchComputeEnvironment#image_id}.
        :param instance_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_role BatchComputeEnvironment#instance_role}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_type BatchComputeEnvironment#instance_type}.
        :param launch_template: launch_template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template BatchComputeEnvironment#launch_template}
        :param min_vcpus: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#min_vcpus BatchComputeEnvironment#min_vcpus}.
        :param spot_iam_fleet_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#spot_iam_fleet_role BatchComputeEnvironment#spot_iam_fleet_role}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        '''
        if isinstance(ec2_configuration, dict):
            ec2_configuration = BatchComputeEnvironmentComputeResourcesEc2Configuration(**ec2_configuration)
        if isinstance(launch_template, dict):
            launch_template = BatchComputeEnvironmentComputeResourcesLaunchTemplate(**launch_template)
        self._values: typing.Dict[str, typing.Any] = {
            "max_vcpus": max_vcpus,
            "security_group_ids": security_group_ids,
            "subnets": subnets,
            "type": type,
        }
        if allocation_strategy is not None:
            self._values["allocation_strategy"] = allocation_strategy
        if bid_percentage is not None:
            self._values["bid_percentage"] = bid_percentage
        if desired_vcpus is not None:
            self._values["desired_vcpus"] = desired_vcpus
        if ec2_configuration is not None:
            self._values["ec2_configuration"] = ec2_configuration
        if ec2_key_pair is not None:
            self._values["ec2_key_pair"] = ec2_key_pair
        if image_id is not None:
            self._values["image_id"] = image_id
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if launch_template is not None:
            self._values["launch_template"] = launch_template
        if min_vcpus is not None:
            self._values["min_vcpus"] = min_vcpus
        if spot_iam_fleet_role is not None:
            self._values["spot_iam_fleet_role"] = spot_iam_fleet_role
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def max_vcpus(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#max_vcpus BatchComputeEnvironment#max_vcpus}.'''
        result = self._values.get("max_vcpus")
        assert result is not None, "Required property 'max_vcpus' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#security_group_ids BatchComputeEnvironment#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#subnets BatchComputeEnvironment#subnets}.'''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocation_strategy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#allocation_strategy BatchComputeEnvironment#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bid_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#bid_percentage BatchComputeEnvironment#bid_percentage}.'''
        result = self._values.get("bid_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def desired_vcpus(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#desired_vcpus BatchComputeEnvironment#desired_vcpus}.'''
        result = self._values.get("desired_vcpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2_configuration(
        self,
    ) -> typing.Optional["BatchComputeEnvironmentComputeResourcesEc2Configuration"]:
        '''ec2_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_configuration BatchComputeEnvironment#ec2_configuration}
        '''
        result = self._values.get("ec2_configuration")
        return typing.cast(typing.Optional["BatchComputeEnvironmentComputeResourcesEc2Configuration"], result)

    @builtins.property
    def ec2_key_pair(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#ec2_key_pair BatchComputeEnvironment#ec2_key_pair}.'''
        result = self._values.get("ec2_key_pair")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id BatchComputeEnvironment#image_id}.'''
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_role BatchComputeEnvironment#instance_role}.'''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#instance_type BatchComputeEnvironment#instance_type}.'''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def launch_template(
        self,
    ) -> typing.Optional["BatchComputeEnvironmentComputeResourcesLaunchTemplate"]:
        '''launch_template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template BatchComputeEnvironment#launch_template}
        '''
        result = self._values.get("launch_template")
        return typing.cast(typing.Optional["BatchComputeEnvironmentComputeResourcesLaunchTemplate"], result)

    @builtins.property
    def min_vcpus(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#min_vcpus BatchComputeEnvironment#min_vcpus}.'''
        result = self._values.get("min_vcpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def spot_iam_fleet_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#spot_iam_fleet_role BatchComputeEnvironment#spot_iam_fleet_role}.'''
        result = self._values.get("spot_iam_fleet_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentComputeResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesEc2Configuration",
    jsii_struct_bases=[],
    name_mapping={"image_id_override": "imageIdOverride", "image_type": "imageType"},
)
class BatchComputeEnvironmentComputeResourcesEc2Configuration:
    def __init__(
        self,
        *,
        image_id_override: typing.Optional[builtins.str] = None,
        image_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_id_override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id_override BatchComputeEnvironment#image_id_override}.
        :param image_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_type BatchComputeEnvironment#image_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if image_id_override is not None:
            self._values["image_id_override"] = image_id_override
        if image_type is not None:
            self._values["image_type"] = image_type

    @builtins.property
    def image_id_override(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id_override BatchComputeEnvironment#image_id_override}.'''
        result = self._values.get("image_id_override")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_type BatchComputeEnvironment#image_type}.'''
        result = self._values.get("image_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentComputeResourcesEc2Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetImageIdOverride")
    def reset_image_id_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageIdOverride", []))

    @jsii.member(jsii_name="resetImageType")
    def reset_image_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdOverrideInput")
    def image_id_override_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdOverrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTypeInput")
    def image_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdOverride")
    def image_id_override(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageIdOverride"))

    @image_id_override.setter
    def image_id_override(self, value: builtins.str) -> None:
        jsii.set(self, "imageIdOverride", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageType")
    def image_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageType"))

    @image_type.setter
    def image_type(self, value: builtins.str) -> None:
        jsii.set(self, "imageType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesLaunchTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "launch_template_id": "launchTemplateId",
        "launch_template_name": "launchTemplateName",
        "version": "version",
    },
)
class BatchComputeEnvironmentComputeResourcesLaunchTemplate:
    def __init__(
        self,
        *,
        launch_template_id: typing.Optional[builtins.str] = None,
        launch_template_name: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param launch_template_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_id BatchComputeEnvironment#launch_template_id}.
        :param launch_template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_name BatchComputeEnvironment#launch_template_name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#version BatchComputeEnvironment#version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if launch_template_id is not None:
            self._values["launch_template_id"] = launch_template_id
        if launch_template_name is not None:
            self._values["launch_template_name"] = launch_template_name
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def launch_template_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_id BatchComputeEnvironment#launch_template_id}.'''
        result = self._values.get("launch_template_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def launch_template_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_name BatchComputeEnvironment#launch_template_name}.'''
        result = self._values.get("launch_template_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#version BatchComputeEnvironment#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentComputeResourcesLaunchTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference",
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

    @jsii.member(jsii_name="resetLaunchTemplateId")
    def reset_launch_template_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplateId", []))

    @jsii.member(jsii_name="resetLaunchTemplateName")
    def reset_launch_template_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplateName", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateIdInput")
    def launch_template_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "launchTemplateIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateNameInput")
    def launch_template_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "launchTemplateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateId")
    def launch_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "launchTemplateId"))

    @launch_template_id.setter
    def launch_template_id(self, value: builtins.str) -> None:
        jsii.set(self, "launchTemplateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateName")
    def launch_template_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "launchTemplateName"))

    @launch_template_name.setter
    def launch_template_name(self, value: builtins.str) -> None:
        jsii.set(self, "launchTemplateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate],
    ) -> None:
        jsii.set(self, "internalValue", value)


class BatchComputeEnvironmentComputeResourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentComputeResourcesOutputReference",
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

    @jsii.member(jsii_name="putEc2Configuration")
    def put_ec2_configuration(
        self,
        *,
        image_id_override: typing.Optional[builtins.str] = None,
        image_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_id_override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_id_override BatchComputeEnvironment#image_id_override}.
        :param image_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#image_type BatchComputeEnvironment#image_type}.
        '''
        value = BatchComputeEnvironmentComputeResourcesEc2Configuration(
            image_id_override=image_id_override, image_type=image_type
        )

        return typing.cast(None, jsii.invoke(self, "putEc2Configuration", [value]))

    @jsii.member(jsii_name="putLaunchTemplate")
    def put_launch_template(
        self,
        *,
        launch_template_id: typing.Optional[builtins.str] = None,
        launch_template_name: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param launch_template_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_id BatchComputeEnvironment#launch_template_id}.
        :param launch_template_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#launch_template_name BatchComputeEnvironment#launch_template_name}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#version BatchComputeEnvironment#version}.
        '''
        value = BatchComputeEnvironmentComputeResourcesLaunchTemplate(
            launch_template_id=launch_template_id,
            launch_template_name=launch_template_name,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putLaunchTemplate", [value]))

    @jsii.member(jsii_name="resetAllocationStrategy")
    def reset_allocation_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllocationStrategy", []))

    @jsii.member(jsii_name="resetBidPercentage")
    def reset_bid_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBidPercentage", []))

    @jsii.member(jsii_name="resetDesiredVcpus")
    def reset_desired_vcpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDesiredVcpus", []))

    @jsii.member(jsii_name="resetEc2Configuration")
    def reset_ec2_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2Configuration", []))

    @jsii.member(jsii_name="resetEc2KeyPair")
    def reset_ec2_key_pair(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2KeyPair", []))

    @jsii.member(jsii_name="resetImageId")
    def reset_image_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageId", []))

    @jsii.member(jsii_name="resetInstanceRole")
    def reset_instance_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceRole", []))

    @jsii.member(jsii_name="resetInstanceType")
    def reset_instance_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceType", []))

    @jsii.member(jsii_name="resetLaunchTemplate")
    def reset_launch_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplate", []))

    @jsii.member(jsii_name="resetMinVcpus")
    def reset_min_vcpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinVcpus", []))

    @jsii.member(jsii_name="resetSpotIamFleetRole")
    def reset_spot_iam_fleet_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotIamFleetRole", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2Configuration")
    def ec2_configuration(
        self,
    ) -> BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference:
        return typing.cast(BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference, jsii.get(self, "ec2Configuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplate")
    def launch_template(
        self,
    ) -> BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference:
        return typing.cast(BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference, jsii.get(self, "launchTemplate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocationStrategyInput")
    def allocation_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allocationStrategyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPercentageInput")
    def bid_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bidPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredVcpusInput")
    def desired_vcpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "desiredVcpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2ConfigurationInput")
    def ec2_configuration_input(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesEc2Configuration], jsii.get(self, "ec2ConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2KeyPairInput")
    def ec2_key_pair_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2KeyPairInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdInput")
    def image_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRoleInput")
    def instance_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateInput")
    def launch_template_input(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResourcesLaunchTemplate], jsii.get(self, "launchTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxVcpusInput")
    def max_vcpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVcpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minVcpusInput")
    def min_vcpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minVcpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotIamFleetRoleInput")
    def spot_iam_fleet_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotIamFleetRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetsInput")
    def subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocationStrategy")
    def allocation_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allocationStrategy"))

    @allocation_strategy.setter
    def allocation_strategy(self, value: builtins.str) -> None:
        jsii.set(self, "allocationStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bidPercentage")
    def bid_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bidPercentage"))

    @bid_percentage.setter
    def bid_percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "bidPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredVcpus")
    def desired_vcpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "desiredVcpus"))

    @desired_vcpus.setter
    def desired_vcpus(self, value: jsii.Number) -> None:
        jsii.set(self, "desiredVcpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2KeyPair")
    def ec2_key_pair(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2KeyPair"))

    @ec2_key_pair.setter
    def ec2_key_pair(self, value: builtins.str) -> None:
        jsii.set(self, "ec2KeyPair", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: builtins.str) -> None:
        jsii.set(self, "imageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceRole"))

    @instance_role.setter
    def instance_role(self, value: builtins.str) -> None:
        jsii.set(self, "instanceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxVcpus")
    def max_vcpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpus"))

    @max_vcpus.setter
    def max_vcpus(self, value: jsii.Number) -> None:
        jsii.set(self, "maxVcpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minVcpus")
    def min_vcpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpus"))

    @min_vcpus.setter
    def min_vcpus(self, value: jsii.Number) -> None:
        jsii.set(self, "minVcpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotIamFleetRole")
    def spot_iam_fleet_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotIamFleetRole"))

    @spot_iam_fleet_role.setter
    def spot_iam_fleet_role(self, value: builtins.str) -> None:
        jsii.set(self, "spotIamFleetRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnets", value)

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
    ) -> typing.Optional[BatchComputeEnvironmentComputeResources]:
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchComputeEnvironmentComputeResources],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchComputeEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "type": "type",
        "compute_environment_name": "computeEnvironmentName",
        "compute_environment_name_prefix": "computeEnvironmentNamePrefix",
        "compute_resources": "computeResources",
        "service_role": "serviceRole",
        "state": "state",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BatchComputeEnvironmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        type: builtins.str,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_environment_name_prefix: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[BatchComputeEnvironmentComputeResources] = None,
        service_role: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name BatchComputeEnvironment#compute_environment_name}.
        :param compute_environment_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name_prefix BatchComputeEnvironment#compute_environment_name_prefix}.
        :param compute_resources: compute_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_resources BatchComputeEnvironment#compute_resources}
        :param service_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#service_role BatchComputeEnvironment#service_role}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#state BatchComputeEnvironment#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags_all BatchComputeEnvironment#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(compute_resources, dict):
            compute_resources = BatchComputeEnvironmentComputeResources(**compute_resources)
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if compute_environment_name is not None:
            self._values["compute_environment_name"] = compute_environment_name
        if compute_environment_name_prefix is not None:
            self._values["compute_environment_name_prefix"] = compute_environment_name_prefix
        if compute_resources is not None:
            self._values["compute_resources"] = compute_resources
        if service_role is not None:
            self._values["service_role"] = service_role
        if state is not None:
            self._values["state"] = state
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
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#type BatchComputeEnvironment#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_environment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name BatchComputeEnvironment#compute_environment_name}.'''
        result = self._values.get("compute_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_environment_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_environment_name_prefix BatchComputeEnvironment#compute_environment_name_prefix}.'''
        result = self._values.get("compute_environment_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_resources(
        self,
    ) -> typing.Optional[BatchComputeEnvironmentComputeResources]:
        '''compute_resources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#compute_resources BatchComputeEnvironment#compute_resources}
        '''
        result = self._values.get("compute_resources")
        return typing.cast(typing.Optional[BatchComputeEnvironmentComputeResources], result)

    @builtins.property
    def service_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#service_role BatchComputeEnvironment#service_role}.'''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#state BatchComputeEnvironment#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags BatchComputeEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_compute_environment#tags_all BatchComputeEnvironment#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchComputeEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchJobDefinition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition aws_batch_job_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        type: builtins.str,
        container_properties: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        platform_capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        propagate_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retry_strategy: typing.Optional["BatchJobDefinitionRetryStrategy"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout: typing.Optional["BatchJobDefinitionTimeout"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition aws_batch_job_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#name BatchJobDefinition#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#type BatchJobDefinition#type}.
        :param container_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#container_properties BatchJobDefinition#container_properties}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#parameters BatchJobDefinition#parameters}.
        :param platform_capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#platform_capabilities BatchJobDefinition#platform_capabilities}.
        :param propagate_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#propagate_tags BatchJobDefinition#propagate_tags}.
        :param retry_strategy: retry_strategy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#retry_strategy BatchJobDefinition#retry_strategy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags BatchJobDefinition#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags_all BatchJobDefinition#tags_all}.
        :param timeout: timeout block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#timeout BatchJobDefinition#timeout}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BatchJobDefinitionConfig(
            name=name,
            type=type,
            container_properties=container_properties,
            parameters=parameters,
            platform_capabilities=platform_capabilities,
            propagate_tags=propagate_tags,
            retry_strategy=retry_strategy,
            tags=tags,
            tags_all=tags_all,
            timeout=timeout,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putRetryStrategy")
    def put_retry_strategy(
        self,
        *,
        attempts: typing.Optional[jsii.Number] = None,
        evaluate_on_exit: typing.Optional[typing.Sequence["BatchJobDefinitionRetryStrategyEvaluateOnExit"]] = None,
    ) -> None:
        '''
        :param attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempts BatchJobDefinition#attempts}.
        :param evaluate_on_exit: evaluate_on_exit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#evaluate_on_exit BatchJobDefinition#evaluate_on_exit}
        '''
        value = BatchJobDefinitionRetryStrategy(
            attempts=attempts, evaluate_on_exit=evaluate_on_exit
        )

        return typing.cast(None, jsii.invoke(self, "putRetryStrategy", [value]))

    @jsii.member(jsii_name="putTimeout")
    def put_timeout(
        self,
        *,
        attempt_duration_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param attempt_duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempt_duration_seconds BatchJobDefinition#attempt_duration_seconds}.
        '''
        value = BatchJobDefinitionTimeout(
            attempt_duration_seconds=attempt_duration_seconds
        )

        return typing.cast(None, jsii.invoke(self, "putTimeout", [value]))

    @jsii.member(jsii_name="resetContainerProperties")
    def reset_container_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerProperties", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetPlatformCapabilities")
    def reset_platform_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatformCapabilities", []))

    @jsii.member(jsii_name="resetPropagateTags")
    def reset_propagate_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPropagateTags", []))

    @jsii.member(jsii_name="resetRetryStrategy")
    def reset_retry_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryStrategy", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

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
    @jsii.member(jsii_name="retryStrategy")
    def retry_strategy(self) -> "BatchJobDefinitionRetryStrategyOutputReference":
        return typing.cast("BatchJobDefinitionRetryStrategyOutputReference", jsii.get(self, "retryStrategy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revision")
    def revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "revision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> "BatchJobDefinitionTimeoutOutputReference":
        return typing.cast("BatchJobDefinitionTimeoutOutputReference", jsii.get(self, "timeout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPropertiesInput")
    def container_properties_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "parametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformCapabilitiesInput")
    def platform_capabilities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "platformCapabilitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagateTagsInput")
    def propagate_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "propagateTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryStrategyInput")
    def retry_strategy_input(
        self,
    ) -> typing.Optional["BatchJobDefinitionRetryStrategy"]:
        return typing.cast(typing.Optional["BatchJobDefinitionRetryStrategy"], jsii.get(self, "retryStrategyInput"))

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
    def timeout_input(self) -> typing.Optional["BatchJobDefinitionTimeout"]:
        return typing.cast(typing.Optional["BatchJobDefinitionTimeout"], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerProperties")
    def container_properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerProperties"))

    @container_properties.setter
    def container_properties(self, value: builtins.str) -> None:
        jsii.set(self, "containerProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformCapabilities")
    def platform_capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "platformCapabilities"))

    @platform_capabilities.setter
    def platform_capabilities(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "platformCapabilities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagateTags")
    def propagate_tags(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "propagateTags"))

    @propagate_tags.setter
    def propagate_tags(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "propagateTags", value)

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "type": "type",
        "container_properties": "containerProperties",
        "parameters": "parameters",
        "platform_capabilities": "platformCapabilities",
        "propagate_tags": "propagateTags",
        "retry_strategy": "retryStrategy",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeout": "timeout",
    },
)
class BatchJobDefinitionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        type: builtins.str,
        container_properties: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        platform_capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        propagate_tags: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        retry_strategy: typing.Optional["BatchJobDefinitionRetryStrategy"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeout: typing.Optional["BatchJobDefinitionTimeout"] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#name BatchJobDefinition#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#type BatchJobDefinition#type}.
        :param container_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#container_properties BatchJobDefinition#container_properties}.
        :param parameters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#parameters BatchJobDefinition#parameters}.
        :param platform_capabilities: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#platform_capabilities BatchJobDefinition#platform_capabilities}.
        :param propagate_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#propagate_tags BatchJobDefinition#propagate_tags}.
        :param retry_strategy: retry_strategy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#retry_strategy BatchJobDefinition#retry_strategy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags BatchJobDefinition#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags_all BatchJobDefinition#tags_all}.
        :param timeout: timeout block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#timeout BatchJobDefinition#timeout}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(retry_strategy, dict):
            retry_strategy = BatchJobDefinitionRetryStrategy(**retry_strategy)
        if isinstance(timeout, dict):
            timeout = BatchJobDefinitionTimeout(**timeout)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if container_properties is not None:
            self._values["container_properties"] = container_properties
        if parameters is not None:
            self._values["parameters"] = parameters
        if platform_capabilities is not None:
            self._values["platform_capabilities"] = platform_capabilities
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if retry_strategy is not None:
            self._values["retry_strategy"] = retry_strategy
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeout is not None:
            self._values["timeout"] = timeout

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#name BatchJobDefinition#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#type BatchJobDefinition#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_properties(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#container_properties BatchJobDefinition#container_properties}.'''
        result = self._values.get("container_properties")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#parameters BatchJobDefinition#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def platform_capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#platform_capabilities BatchJobDefinition#platform_capabilities}.'''
        result = self._values.get("platform_capabilities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#propagate_tags BatchJobDefinition#propagate_tags}.'''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def retry_strategy(self) -> typing.Optional["BatchJobDefinitionRetryStrategy"]:
        '''retry_strategy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#retry_strategy BatchJobDefinition#retry_strategy}
        '''
        result = self._values.get("retry_strategy")
        return typing.cast(typing.Optional["BatchJobDefinitionRetryStrategy"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags BatchJobDefinition#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#tags_all BatchJobDefinition#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeout(self) -> typing.Optional["BatchJobDefinitionTimeout"]:
        '''timeout block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#timeout BatchJobDefinition#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional["BatchJobDefinitionTimeout"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategy",
    jsii_struct_bases=[],
    name_mapping={"attempts": "attempts", "evaluate_on_exit": "evaluateOnExit"},
)
class BatchJobDefinitionRetryStrategy:
    def __init__(
        self,
        *,
        attempts: typing.Optional[jsii.Number] = None,
        evaluate_on_exit: typing.Optional[typing.Sequence["BatchJobDefinitionRetryStrategyEvaluateOnExit"]] = None,
    ) -> None:
        '''
        :param attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempts BatchJobDefinition#attempts}.
        :param evaluate_on_exit: evaluate_on_exit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#evaluate_on_exit BatchJobDefinition#evaluate_on_exit}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if attempts is not None:
            self._values["attempts"] = attempts
        if evaluate_on_exit is not None:
            self._values["evaluate_on_exit"] = evaluate_on_exit

    @builtins.property
    def attempts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempts BatchJobDefinition#attempts}.'''
        result = self._values.get("attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluate_on_exit(
        self,
    ) -> typing.Optional[typing.List["BatchJobDefinitionRetryStrategyEvaluateOnExit"]]:
        '''evaluate_on_exit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#evaluate_on_exit BatchJobDefinition#evaluate_on_exit}
        '''
        result = self._values.get("evaluate_on_exit")
        return typing.cast(typing.Optional[typing.List["BatchJobDefinitionRetryStrategyEvaluateOnExit"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionRetryStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategyEvaluateOnExit",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "on_exit_code": "onExitCode",
        "on_reason": "onReason",
        "on_status_reason": "onStatusReason",
    },
)
class BatchJobDefinitionRetryStrategyEvaluateOnExit:
    def __init__(
        self,
        *,
        action: builtins.str,
        on_exit_code: typing.Optional[builtins.str] = None,
        on_reason: typing.Optional[builtins.str] = None,
        on_status_reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#action BatchJobDefinition#action}.
        :param on_exit_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_exit_code BatchJobDefinition#on_exit_code}.
        :param on_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_reason BatchJobDefinition#on_reason}.
        :param on_status_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_status_reason BatchJobDefinition#on_status_reason}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
        }
        if on_exit_code is not None:
            self._values["on_exit_code"] = on_exit_code
        if on_reason is not None:
            self._values["on_reason"] = on_reason
        if on_status_reason is not None:
            self._values["on_status_reason"] = on_status_reason

    @builtins.property
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#action BatchJobDefinition#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_exit_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_exit_code BatchJobDefinition#on_exit_code}.'''
        result = self._values.get("on_exit_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_reason BatchJobDefinition#on_reason}.'''
        result = self._values.get("on_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_status_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#on_status_reason BatchJobDefinition#on_status_reason}.'''
        result = self._values.get("on_status_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionRetryStrategyEvaluateOnExit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchJobDefinitionRetryStrategyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionRetryStrategyOutputReference",
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

    @jsii.member(jsii_name="resetAttempts")
    def reset_attempts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttempts", []))

    @jsii.member(jsii_name="resetEvaluateOnExit")
    def reset_evaluate_on_exit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluateOnExit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attemptsInput")
    def attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "attemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluateOnExitInput")
    def evaluate_on_exit_input(
        self,
    ) -> typing.Optional[typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]]:
        return typing.cast(typing.Optional[typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]], jsii.get(self, "evaluateOnExitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attempts")
    def attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "attempts"))

    @attempts.setter
    def attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "attempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluateOnExit")
    def evaluate_on_exit(
        self,
    ) -> typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit]:
        return typing.cast(typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit], jsii.get(self, "evaluateOnExit"))

    @evaluate_on_exit.setter
    def evaluate_on_exit(
        self,
        value: typing.List[BatchJobDefinitionRetryStrategyEvaluateOnExit],
    ) -> None:
        jsii.set(self, "evaluateOnExit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BatchJobDefinitionRetryStrategy]:
        return typing.cast(typing.Optional[BatchJobDefinitionRetryStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchJobDefinitionRetryStrategy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionTimeout",
    jsii_struct_bases=[],
    name_mapping={"attempt_duration_seconds": "attemptDurationSeconds"},
)
class BatchJobDefinitionTimeout:
    def __init__(
        self,
        *,
        attempt_duration_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param attempt_duration_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempt_duration_seconds BatchJobDefinition#attempt_duration_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if attempt_duration_seconds is not None:
            self._values["attempt_duration_seconds"] = attempt_duration_seconds

    @builtins.property
    def attempt_duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_definition#attempt_duration_seconds BatchJobDefinition#attempt_duration_seconds}.'''
        result = self._values.get("attempt_duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobDefinitionTimeout(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchJobDefinitionTimeoutOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobDefinitionTimeoutOutputReference",
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

    @jsii.member(jsii_name="resetAttemptDurationSeconds")
    def reset_attempt_duration_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttemptDurationSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attemptDurationSecondsInput")
    def attempt_duration_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "attemptDurationSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attemptDurationSeconds")
    def attempt_duration_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "attemptDurationSeconds"))

    @attempt_duration_seconds.setter
    def attempt_duration_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "attemptDurationSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BatchJobDefinitionTimeout]:
        return typing.cast(typing.Optional[BatchJobDefinitionTimeout], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BatchJobDefinitionTimeout]) -> None:
        jsii.set(self, "internalValue", value)


class BatchJobQueue(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchJobQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue aws_batch_job_queue}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_environments: typing.Sequence[builtins.str],
        name: builtins.str,
        priority: jsii.Number,
        state: builtins.str,
        scheduling_policy_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue aws_batch_job_queue} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param compute_environments: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#compute_environments BatchJobQueue#compute_environments}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#name BatchJobQueue#name}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#priority BatchJobQueue#priority}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#state BatchJobQueue#state}.
        :param scheduling_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#scheduling_policy_arn BatchJobQueue#scheduling_policy_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags BatchJobQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags_all BatchJobQueue#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BatchJobQueueConfig(
            compute_environments=compute_environments,
            name=name,
            priority=priority,
            state=state,
            scheduling_policy_arn=scheduling_policy_arn,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetSchedulingPolicyArn")
    def reset_scheduling_policy_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingPolicyArn", []))

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
    @jsii.member(jsii_name="computeEnvironmentsInput")
    def compute_environments_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "computeEnvironmentsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArnInput")
    def scheduling_policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schedulingPolicyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

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
    @jsii.member(jsii_name="computeEnvironments")
    def compute_environments(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "computeEnvironments"))

    @compute_environments.setter
    def compute_environments(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "computeEnvironments", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArn")
    def scheduling_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicyArn"))

    @scheduling_policy_arn.setter
    def scheduling_policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "schedulingPolicyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

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
    jsii_type="@cdktf/provider-aws.batch.BatchJobQueueConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "compute_environments": "computeEnvironments",
        "name": "name",
        "priority": "priority",
        "state": "state",
        "scheduling_policy_arn": "schedulingPolicyArn",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BatchJobQueueConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        compute_environments: typing.Sequence[builtins.str],
        name: builtins.str,
        priority: jsii.Number,
        state: builtins.str,
        scheduling_policy_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param compute_environments: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#compute_environments BatchJobQueue#compute_environments}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#name BatchJobQueue#name}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#priority BatchJobQueue#priority}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#state BatchJobQueue#state}.
        :param scheduling_policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#scheduling_policy_arn BatchJobQueue#scheduling_policy_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags BatchJobQueue#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags_all BatchJobQueue#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environments": compute_environments,
            "name": name,
            "priority": priority,
            "state": state,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if scheduling_policy_arn is not None:
            self._values["scheduling_policy_arn"] = scheduling_policy_arn
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
    def compute_environments(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#compute_environments BatchJobQueue#compute_environments}.'''
        result = self._values.get("compute_environments")
        assert result is not None, "Required property 'compute_environments' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#name BatchJobQueue#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#priority BatchJobQueue#priority}.'''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def state(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#state BatchJobQueue#state}.'''
        result = self._values.get("state")
        assert result is not None, "Required property 'state' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheduling_policy_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#scheduling_policy_arn BatchJobQueue#scheduling_policy_arn}.'''
        result = self._values.get("scheduling_policy_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags BatchJobQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_job_queue#tags_all BatchJobQueue#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchJobQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchSchedulingPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy aws_batch_scheduling_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        fair_share_policy: typing.Optional["BatchSchedulingPolicyFairSharePolicy"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy aws_batch_scheduling_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#name BatchSchedulingPolicy#name}.
        :param fair_share_policy: fair_share_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#fair_share_policy BatchSchedulingPolicy#fair_share_policy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags BatchSchedulingPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags_all BatchSchedulingPolicy#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BatchSchedulingPolicyConfig(
            name=name,
            fair_share_policy=fair_share_policy,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFairSharePolicy")
    def put_fair_share_policy(
        self,
        *,
        compute_reservation: typing.Optional[jsii.Number] = None,
        share_decay_seconds: typing.Optional[jsii.Number] = None,
        share_distribution: typing.Optional[typing.Sequence["BatchSchedulingPolicyFairSharePolicyShareDistribution"]] = None,
    ) -> None:
        '''
        :param compute_reservation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#compute_reservation BatchSchedulingPolicy#compute_reservation}.
        :param share_decay_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_decay_seconds BatchSchedulingPolicy#share_decay_seconds}.
        :param share_distribution: share_distribution block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_distribution BatchSchedulingPolicy#share_distribution}
        '''
        value = BatchSchedulingPolicyFairSharePolicy(
            compute_reservation=compute_reservation,
            share_decay_seconds=share_decay_seconds,
            share_distribution=share_distribution,
        )

        return typing.cast(None, jsii.invoke(self, "putFairSharePolicy", [value]))

    @jsii.member(jsii_name="resetFairSharePolicy")
    def reset_fair_share_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFairSharePolicy", []))

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
    @jsii.member(jsii_name="fairSharePolicy")
    def fair_share_policy(
        self,
    ) -> "BatchSchedulingPolicyFairSharePolicyOutputReference":
        return typing.cast("BatchSchedulingPolicyFairSharePolicyOutputReference", jsii.get(self, "fairSharePolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fairSharePolicyInput")
    def fair_share_policy_input(
        self,
    ) -> typing.Optional["BatchSchedulingPolicyFairSharePolicy"]:
        return typing.cast(typing.Optional["BatchSchedulingPolicyFairSharePolicy"], jsii.get(self, "fairSharePolicyInput"))

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
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "fair_share_policy": "fairSharePolicy",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class BatchSchedulingPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        fair_share_policy: typing.Optional["BatchSchedulingPolicyFairSharePolicy"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#name BatchSchedulingPolicy#name}.
        :param fair_share_policy: fair_share_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#fair_share_policy BatchSchedulingPolicy#fair_share_policy}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags BatchSchedulingPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags_all BatchSchedulingPolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(fair_share_policy, dict):
            fair_share_policy = BatchSchedulingPolicyFairSharePolicy(**fair_share_policy)
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
        if fair_share_policy is not None:
            self._values["fair_share_policy"] = fair_share_policy
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#name BatchSchedulingPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fair_share_policy(
        self,
    ) -> typing.Optional["BatchSchedulingPolicyFairSharePolicy"]:
        '''fair_share_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#fair_share_policy BatchSchedulingPolicy#fair_share_policy}
        '''
        result = self._values.get("fair_share_policy")
        return typing.cast(typing.Optional["BatchSchedulingPolicyFairSharePolicy"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags BatchSchedulingPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#tags_all BatchSchedulingPolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchSchedulingPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "compute_reservation": "computeReservation",
        "share_decay_seconds": "shareDecaySeconds",
        "share_distribution": "shareDistribution",
    },
)
class BatchSchedulingPolicyFairSharePolicy:
    def __init__(
        self,
        *,
        compute_reservation: typing.Optional[jsii.Number] = None,
        share_decay_seconds: typing.Optional[jsii.Number] = None,
        share_distribution: typing.Optional[typing.Sequence["BatchSchedulingPolicyFairSharePolicyShareDistribution"]] = None,
    ) -> None:
        '''
        :param compute_reservation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#compute_reservation BatchSchedulingPolicy#compute_reservation}.
        :param share_decay_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_decay_seconds BatchSchedulingPolicy#share_decay_seconds}.
        :param share_distribution: share_distribution block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_distribution BatchSchedulingPolicy#share_distribution}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if compute_reservation is not None:
            self._values["compute_reservation"] = compute_reservation
        if share_decay_seconds is not None:
            self._values["share_decay_seconds"] = share_decay_seconds
        if share_distribution is not None:
            self._values["share_distribution"] = share_distribution

    @builtins.property
    def compute_reservation(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#compute_reservation BatchSchedulingPolicy#compute_reservation}.'''
        result = self._values.get("compute_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def share_decay_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_decay_seconds BatchSchedulingPolicy#share_decay_seconds}.'''
        result = self._values.get("share_decay_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def share_distribution(
        self,
    ) -> typing.Optional[typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]]:
        '''share_distribution block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_distribution BatchSchedulingPolicy#share_distribution}
        '''
        result = self._values.get("share_distribution")
        return typing.cast(typing.Optional[typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchSchedulingPolicyFairSharePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BatchSchedulingPolicyFairSharePolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicyOutputReference",
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

    @jsii.member(jsii_name="resetComputeReservation")
    def reset_compute_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeReservation", []))

    @jsii.member(jsii_name="resetShareDecaySeconds")
    def reset_share_decay_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShareDecaySeconds", []))

    @jsii.member(jsii_name="resetShareDistribution")
    def reset_share_distribution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShareDistribution", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeReservationInput")
    def compute_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "computeReservationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDecaySecondsInput")
    def share_decay_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shareDecaySecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDistributionInput")
    def share_distribution_input(
        self,
    ) -> typing.Optional[typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]]:
        return typing.cast(typing.Optional[typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]], jsii.get(self, "shareDistributionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeReservation")
    def compute_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "computeReservation"))

    @compute_reservation.setter
    def compute_reservation(self, value: jsii.Number) -> None:
        jsii.set(self, "computeReservation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDecaySeconds")
    def share_decay_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shareDecaySeconds"))

    @share_decay_seconds.setter
    def share_decay_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "shareDecaySeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDistribution")
    def share_distribution(
        self,
    ) -> typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"]:
        return typing.cast(typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"], jsii.get(self, "shareDistribution"))

    @share_distribution.setter
    def share_distribution(
        self,
        value: typing.List["BatchSchedulingPolicyFairSharePolicyShareDistribution"],
    ) -> None:
        jsii.set(self, "shareDistribution", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BatchSchedulingPolicyFairSharePolicy]:
        return typing.cast(typing.Optional[BatchSchedulingPolicyFairSharePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BatchSchedulingPolicyFairSharePolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.BatchSchedulingPolicyFairSharePolicyShareDistribution",
    jsii_struct_bases=[],
    name_mapping={
        "share_identifier": "shareIdentifier",
        "weight_factor": "weightFactor",
    },
)
class BatchSchedulingPolicyFairSharePolicyShareDistribution:
    def __init__(
        self,
        *,
        share_identifier: builtins.str,
        weight_factor: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param share_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_identifier BatchSchedulingPolicy#share_identifier}.
        :param weight_factor: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#weight_factor BatchSchedulingPolicy#weight_factor}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "share_identifier": share_identifier,
        }
        if weight_factor is not None:
            self._values["weight_factor"] = weight_factor

    @builtins.property
    def share_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#share_identifier BatchSchedulingPolicy#share_identifier}.'''
        result = self._values.get("share_identifier")
        assert result is not None, "Required property 'share_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def weight_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/batch_scheduling_policy#weight_factor BatchSchedulingPolicy#weight_factor}.'''
        result = self._values.get("weight_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchSchedulingPolicyFairSharePolicyShareDistribution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchComputeEnvironment(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchComputeEnvironment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment aws_batch_compute_environment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_environment_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment aws_batch_compute_environment} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#compute_environment_name DataAwsBatchComputeEnvironment#compute_environment_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#tags DataAwsBatchComputeEnvironment#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsBatchComputeEnvironmentConfig(
            compute_environment_name=compute_environment_name,
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
    @jsii.member(jsii_name="ecsClusterArn")
    def ecs_cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecsClusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentNameInput")
    def compute_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))

    @compute_environment_name.setter
    def compute_environment_name(self, value: builtins.str) -> None:
        jsii.set(self, "computeEnvironmentName", value)

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
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchComputeEnvironmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "compute_environment_name": "computeEnvironmentName",
        "tags": "tags",
    },
)
class DataAwsBatchComputeEnvironmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        compute_environment_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param compute_environment_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#compute_environment_name DataAwsBatchComputeEnvironment#compute_environment_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#tags DataAwsBatchComputeEnvironment#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environment_name": compute_environment_name,
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
    def compute_environment_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#compute_environment_name DataAwsBatchComputeEnvironment#compute_environment_name}.'''
        result = self._values.get("compute_environment_name")
        assert result is not None, "Required property 'compute_environment_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_compute_environment#tags DataAwsBatchComputeEnvironment#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchComputeEnvironmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchJobQueue(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueue",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue aws_batch_job_queue}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue aws_batch_job_queue} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#name DataAwsBatchJobQueue#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#tags DataAwsBatchJobQueue#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsBatchJobQueueConfig(
            name=name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="computeEnvironmentOrder")
    def compute_environment_order(
        self,
        index: builtins.str,
    ) -> "DataAwsBatchJobQueueComputeEnvironmentOrder":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsBatchJobQueueComputeEnvironmentOrder", jsii.invoke(self, "computeEnvironmentOrder", [index]))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArn")
    def scheduling_policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schedulingPolicyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

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


class DataAwsBatchJobQueueComputeEnvironmentOrder(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueueComputeEnvironmentOrder",
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
    @jsii.member(jsii_name="computeEnvironment")
    def compute_environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="order")
    def order(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "order"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchJobQueueConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "tags": "tags",
    },
)
class DataAwsBatchJobQueueConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#name DataAwsBatchJobQueue#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#tags DataAwsBatchJobQueue#tags}.
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#name DataAwsBatchJobQueue#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_job_queue#tags DataAwsBatchJobQueue#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchJobQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchSchedulingPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy aws_batch_scheduling_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        arn: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy aws_batch_scheduling_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#arn DataAwsBatchSchedulingPolicy#arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#tags DataAwsBatchSchedulingPolicy#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsBatchSchedulingPolicyConfig(
            arn=arn,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="fairSharePolicy")
    def fair_share_policy(
        self,
        index: builtins.str,
    ) -> "DataAwsBatchSchedulingPolicyFairSharePolicy":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsBatchSchedulingPolicyFairSharePolicy", jsii.invoke(self, "fairSharePolicy", [index]))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

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
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "tags": "tags",
    },
)
class DataAwsBatchSchedulingPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Batch.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#arn DataAwsBatchSchedulingPolicy#arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#tags DataAwsBatchSchedulingPolicy#tags}.
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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#arn DataAwsBatchSchedulingPolicy#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/batch_scheduling_policy#tags DataAwsBatchSchedulingPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsBatchSchedulingPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsBatchSchedulingPolicyFairSharePolicy(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicy",
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
    @jsii.member(jsii_name="computeReservation")
    def compute_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "computeReservation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDecaySeconds")
    def share_decay_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shareDecaySeconds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shareDistribution")
    def share_distribution(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "shareDistribution"))


class DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.batch.DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution",
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
    @jsii.member(jsii_name="shareIdentifier")
    def share_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shareIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weightFactor")
    def weight_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weightFactor"))


__all__ = [
    "BatchComputeEnvironment",
    "BatchComputeEnvironmentComputeResources",
    "BatchComputeEnvironmentComputeResourcesEc2Configuration",
    "BatchComputeEnvironmentComputeResourcesEc2ConfigurationOutputReference",
    "BatchComputeEnvironmentComputeResourcesLaunchTemplate",
    "BatchComputeEnvironmentComputeResourcesLaunchTemplateOutputReference",
    "BatchComputeEnvironmentComputeResourcesOutputReference",
    "BatchComputeEnvironmentConfig",
    "BatchJobDefinition",
    "BatchJobDefinitionConfig",
    "BatchJobDefinitionRetryStrategy",
    "BatchJobDefinitionRetryStrategyEvaluateOnExit",
    "BatchJobDefinitionRetryStrategyOutputReference",
    "BatchJobDefinitionTimeout",
    "BatchJobDefinitionTimeoutOutputReference",
    "BatchJobQueue",
    "BatchJobQueueConfig",
    "BatchSchedulingPolicy",
    "BatchSchedulingPolicyConfig",
    "BatchSchedulingPolicyFairSharePolicy",
    "BatchSchedulingPolicyFairSharePolicyOutputReference",
    "BatchSchedulingPolicyFairSharePolicyShareDistribution",
    "DataAwsBatchComputeEnvironment",
    "DataAwsBatchComputeEnvironmentConfig",
    "DataAwsBatchJobQueue",
    "DataAwsBatchJobQueueComputeEnvironmentOrder",
    "DataAwsBatchJobQueueConfig",
    "DataAwsBatchSchedulingPolicy",
    "DataAwsBatchSchedulingPolicyConfig",
    "DataAwsBatchSchedulingPolicyFairSharePolicy",
    "DataAwsBatchSchedulingPolicyFairSharePolicyShareDistribution",
]

publication.publish()
