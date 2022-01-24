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


class DataAwsServiceDiscoveryDnsNamespace(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.DataAwsServiceDiscoveryDnsNamespace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace aws_service_discovery_dns_namespace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        type: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace aws_service_discovery_dns_namespace} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace#name DataAwsServiceDiscoveryDnsNamespace#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace#type DataAwsServiceDiscoveryDnsNamespace#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsServiceDiscoveryDnsNamespaceConfig(
            name=name,
            type=type,
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
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.DataAwsServiceDiscoveryDnsNamespaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "type": "type",
    },
)
class DataAwsServiceDiscoveryDnsNamespaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        type: builtins.str,
    ) -> None:
        '''AWS Service Discovery.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace#name DataAwsServiceDiscoveryDnsNamespace#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace#type DataAwsServiceDiscoveryDnsNamespace#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace#name DataAwsServiceDiscoveryDnsNamespace#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/service_discovery_dns_namespace#type DataAwsServiceDiscoveryDnsNamespace#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsServiceDiscoveryDnsNamespaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryHttpNamespace(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryHttpNamespace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace aws_service_discovery_http_namespace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace aws_service_discovery_http_namespace} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#name ServiceDiscoveryHttpNamespace#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#description ServiceDiscoveryHttpNamespace#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#tags ServiceDiscoveryHttpNamespace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#tags_all ServiceDiscoveryHttpNamespace#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceDiscoveryHttpNamespaceConfig(
            name=name,
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
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryHttpNamespaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ServiceDiscoveryHttpNamespaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Service Discovery.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#name ServiceDiscoveryHttpNamespace#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#description ServiceDiscoveryHttpNamespace#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#tags ServiceDiscoveryHttpNamespace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#tags_all ServiceDiscoveryHttpNamespace#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#name ServiceDiscoveryHttpNamespace#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#description ServiceDiscoveryHttpNamespace#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#tags ServiceDiscoveryHttpNamespace#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_http_namespace#tags_all ServiceDiscoveryHttpNamespace#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryHttpNamespaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance aws_service_discovery_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        attributes: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        instance_id: builtins.str,
        service_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance aws_service_discovery_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#attributes ServiceDiscoveryInstance#attributes}.
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#instance_id ServiceDiscoveryInstance#instance_id}.
        :param service_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#service_id ServiceDiscoveryInstance#service_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceDiscoveryInstanceConfig(
            attributes=attributes,
            instance_id=instance_id,
            service_id=service_id,
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
    @jsii.member(jsii_name="attributesInput")
    def attributes_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "attributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceIdInput")
    def service_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributes")
    def attributes(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "attributes"))

    @attributes.setter
    def attributes(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "attributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        jsii.set(self, "instanceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceId"))

    @service_id.setter
    def service_id(self, value: builtins.str) -> None:
        jsii.set(self, "serviceId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "attributes": "attributes",
        "instance_id": "instanceId",
        "service_id": "serviceId",
    },
)
class ServiceDiscoveryInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        attributes: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
        instance_id: builtins.str,
        service_id: builtins.str,
    ) -> None:
        '''AWS Service Discovery.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#attributes ServiceDiscoveryInstance#attributes}.
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#instance_id ServiceDiscoveryInstance#instance_id}.
        :param service_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#service_id ServiceDiscoveryInstance#service_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "attributes": attributes,
            "instance_id": instance_id,
            "service_id": service_id,
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
    def attributes(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#attributes ServiceDiscoveryInstance#attributes}.'''
        result = self._values.get("attributes")
        assert result is not None, "Required property 'attributes' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def instance_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#instance_id ServiceDiscoveryInstance#instance_id}.'''
        result = self._values.get("instance_id")
        assert result is not None, "Required property 'instance_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_instance#service_id ServiceDiscoveryInstance#service_id}.'''
        result = self._values.get("service_id")
        assert result is not None, "Required property 'service_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryPrivateDnsNamespace(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryPrivateDnsNamespace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace aws_service_discovery_private_dns_namespace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        vpc: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace aws_service_discovery_private_dns_namespace} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#name ServiceDiscoveryPrivateDnsNamespace#name}.
        :param vpc: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#vpc ServiceDiscoveryPrivateDnsNamespace#vpc}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#description ServiceDiscoveryPrivateDnsNamespace#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#tags ServiceDiscoveryPrivateDnsNamespace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#tags_all ServiceDiscoveryPrivateDnsNamespace#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceDiscoveryPrivateDnsNamespaceConfig(
            name=name,
            vpc=vpc,
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
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZone"))

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
    @jsii.member(jsii_name="vpcInput")
    def vpc_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcInput"))

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
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: builtins.str) -> None:
        jsii.set(self, "vpc", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryPrivateDnsNamespaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "vpc": "vpc",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ServiceDiscoveryPrivateDnsNamespaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        vpc: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Service Discovery.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#name ServiceDiscoveryPrivateDnsNamespace#name}.
        :param vpc: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#vpc ServiceDiscoveryPrivateDnsNamespace#vpc}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#description ServiceDiscoveryPrivateDnsNamespace#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#tags ServiceDiscoveryPrivateDnsNamespace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#tags_all ServiceDiscoveryPrivateDnsNamespace#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "vpc": vpc,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#name ServiceDiscoveryPrivateDnsNamespace#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#vpc ServiceDiscoveryPrivateDnsNamespace#vpc}.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#description ServiceDiscoveryPrivateDnsNamespace#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#tags ServiceDiscoveryPrivateDnsNamespace#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_private_dns_namespace#tags_all ServiceDiscoveryPrivateDnsNamespace#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryPrivateDnsNamespaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryPublicDnsNamespace(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryPublicDnsNamespace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace aws_service_discovery_public_dns_namespace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace aws_service_discovery_public_dns_namespace} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#name ServiceDiscoveryPublicDnsNamespace#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#description ServiceDiscoveryPublicDnsNamespace#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#tags ServiceDiscoveryPublicDnsNamespace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#tags_all ServiceDiscoveryPublicDnsNamespace#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceDiscoveryPublicDnsNamespaceConfig(
            name=name,
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
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZone"))

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
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryPublicDnsNamespaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ServiceDiscoveryPublicDnsNamespaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Service Discovery.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#name ServiceDiscoveryPublicDnsNamespace#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#description ServiceDiscoveryPublicDnsNamespace#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#tags ServiceDiscoveryPublicDnsNamespace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#tags_all ServiceDiscoveryPublicDnsNamespace#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#name ServiceDiscoveryPublicDnsNamespace#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#description ServiceDiscoveryPublicDnsNamespace#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#tags ServiceDiscoveryPublicDnsNamespace#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_public_dns_namespace#tags_all ServiceDiscoveryPublicDnsNamespace#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryPublicDnsNamespaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryService(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryService",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service aws_service_discovery_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        dns_config: typing.Optional["ServiceDiscoveryServiceDnsConfig"] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        health_check_config: typing.Optional["ServiceDiscoveryServiceHealthCheckConfig"] = None,
        health_check_custom_config: typing.Optional["ServiceDiscoveryServiceHealthCheckCustomConfig"] = None,
        namespace_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service aws_service_discovery_service} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#name ServiceDiscoveryService#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#description ServiceDiscoveryService#description}.
        :param dns_config: dns_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#dns_config ServiceDiscoveryService#dns_config}
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#force_destroy ServiceDiscoveryService#force_destroy}.
        :param health_check_config: health_check_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#health_check_config ServiceDiscoveryService#health_check_config}
        :param health_check_custom_config: health_check_custom_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#health_check_custom_config ServiceDiscoveryService#health_check_custom_config}
        :param namespace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#namespace_id ServiceDiscoveryService#namespace_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#tags ServiceDiscoveryService#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#tags_all ServiceDiscoveryService#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceDiscoveryServiceConfig(
            name=name,
            description=description,
            dns_config=dns_config,
            force_destroy=force_destroy,
            health_check_config=health_check_config,
            health_check_custom_config=health_check_custom_config,
            namespace_id=namespace_id,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDnsConfig")
    def put_dns_config(
        self,
        *,
        dns_records: typing.Sequence["ServiceDiscoveryServiceDnsConfigDnsRecords"],
        namespace_id: builtins.str,
        routing_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_records: dns_records block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#dns_records ServiceDiscoveryService#dns_records}
        :param namespace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#namespace_id ServiceDiscoveryService#namespace_id}.
        :param routing_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#routing_policy ServiceDiscoveryService#routing_policy}.
        '''
        value = ServiceDiscoveryServiceDnsConfig(
            dns_records=dns_records,
            namespace_id=namespace_id,
            routing_policy=routing_policy,
        )

        return typing.cast(None, jsii.invoke(self, "putDnsConfig", [value]))

    @jsii.member(jsii_name="putHealthCheckConfig")
    def put_health_check_config(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
        resource_path: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param failure_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#failure_threshold ServiceDiscoveryService#failure_threshold}.
        :param resource_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#resource_path ServiceDiscoveryService#resource_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#type ServiceDiscoveryService#type}.
        '''
        value = ServiceDiscoveryServiceHealthCheckConfig(
            failure_threshold=failure_threshold, resource_path=resource_path, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putHealthCheckConfig", [value]))

    @jsii.member(jsii_name="putHealthCheckCustomConfig")
    def put_health_check_custom_config(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param failure_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#failure_threshold ServiceDiscoveryService#failure_threshold}.
        '''
        value = ServiceDiscoveryServiceHealthCheckCustomConfig(
            failure_threshold=failure_threshold
        )

        return typing.cast(None, jsii.invoke(self, "putHealthCheckCustomConfig", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDnsConfig")
    def reset_dns_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsConfig", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetHealthCheckConfig")
    def reset_health_check_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckConfig", []))

    @jsii.member(jsii_name="resetHealthCheckCustomConfig")
    def reset_health_check_custom_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckCustomConfig", []))

    @jsii.member(jsii_name="resetNamespaceId")
    def reset_namespace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceId", []))

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
    @jsii.member(jsii_name="dnsConfig")
    def dns_config(self) -> "ServiceDiscoveryServiceDnsConfigOutputReference":
        return typing.cast("ServiceDiscoveryServiceDnsConfigOutputReference", jsii.get(self, "dnsConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthCheckConfig")
    def health_check_config(
        self,
    ) -> "ServiceDiscoveryServiceHealthCheckConfigOutputReference":
        return typing.cast("ServiceDiscoveryServiceHealthCheckConfigOutputReference", jsii.get(self, "healthCheckConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthCheckCustomConfig")
    def health_check_custom_config(
        self,
    ) -> "ServiceDiscoveryServiceHealthCheckCustomConfigOutputReference":
        return typing.cast("ServiceDiscoveryServiceHealthCheckCustomConfigOutputReference", jsii.get(self, "healthCheckCustomConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsConfigInput")
    def dns_config_input(self) -> typing.Optional["ServiceDiscoveryServiceDnsConfig"]:
        return typing.cast(typing.Optional["ServiceDiscoveryServiceDnsConfig"], jsii.get(self, "dnsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthCheckConfigInput")
    def health_check_config_input(
        self,
    ) -> typing.Optional["ServiceDiscoveryServiceHealthCheckConfig"]:
        return typing.cast(typing.Optional["ServiceDiscoveryServiceHealthCheckConfig"], jsii.get(self, "healthCheckConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthCheckCustomConfigInput")
    def health_check_custom_config_input(
        self,
    ) -> typing.Optional["ServiceDiscoveryServiceHealthCheckCustomConfig"]:
        return typing.cast(typing.Optional["ServiceDiscoveryServiceHealthCheckCustomConfig"], jsii.get(self, "healthCheckCustomConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

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
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        jsii.set(self, "namespaceId", value)

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
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "dns_config": "dnsConfig",
        "force_destroy": "forceDestroy",
        "health_check_config": "healthCheckConfig",
        "health_check_custom_config": "healthCheckCustomConfig",
        "namespace_id": "namespaceId",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ServiceDiscoveryServiceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        dns_config: typing.Optional["ServiceDiscoveryServiceDnsConfig"] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        health_check_config: typing.Optional["ServiceDiscoveryServiceHealthCheckConfig"] = None,
        health_check_custom_config: typing.Optional["ServiceDiscoveryServiceHealthCheckCustomConfig"] = None,
        namespace_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Service Discovery.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#name ServiceDiscoveryService#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#description ServiceDiscoveryService#description}.
        :param dns_config: dns_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#dns_config ServiceDiscoveryService#dns_config}
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#force_destroy ServiceDiscoveryService#force_destroy}.
        :param health_check_config: health_check_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#health_check_config ServiceDiscoveryService#health_check_config}
        :param health_check_custom_config: health_check_custom_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#health_check_custom_config ServiceDiscoveryService#health_check_custom_config}
        :param namespace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#namespace_id ServiceDiscoveryService#namespace_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#tags ServiceDiscoveryService#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#tags_all ServiceDiscoveryService#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(dns_config, dict):
            dns_config = ServiceDiscoveryServiceDnsConfig(**dns_config)
        if isinstance(health_check_config, dict):
            health_check_config = ServiceDiscoveryServiceHealthCheckConfig(**health_check_config)
        if isinstance(health_check_custom_config, dict):
            health_check_custom_config = ServiceDiscoveryServiceHealthCheckCustomConfig(**health_check_custom_config)
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
        if description is not None:
            self._values["description"] = description
        if dns_config is not None:
            self._values["dns_config"] = dns_config
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if health_check_config is not None:
            self._values["health_check_config"] = health_check_config
        if health_check_custom_config is not None:
            self._values["health_check_custom_config"] = health_check_custom_config
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#name ServiceDiscoveryService#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#description ServiceDiscoveryService#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_config(self) -> typing.Optional["ServiceDiscoveryServiceDnsConfig"]:
        '''dns_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#dns_config ServiceDiscoveryService#dns_config}
        '''
        result = self._values.get("dns_config")
        return typing.cast(typing.Optional["ServiceDiscoveryServiceDnsConfig"], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#force_destroy ServiceDiscoveryService#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def health_check_config(
        self,
    ) -> typing.Optional["ServiceDiscoveryServiceHealthCheckConfig"]:
        '''health_check_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#health_check_config ServiceDiscoveryService#health_check_config}
        '''
        result = self._values.get("health_check_config")
        return typing.cast(typing.Optional["ServiceDiscoveryServiceHealthCheckConfig"], result)

    @builtins.property
    def health_check_custom_config(
        self,
    ) -> typing.Optional["ServiceDiscoveryServiceHealthCheckCustomConfig"]:
        '''health_check_custom_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#health_check_custom_config ServiceDiscoveryService#health_check_custom_config}
        '''
        result = self._values.get("health_check_custom_config")
        return typing.cast(typing.Optional["ServiceDiscoveryServiceHealthCheckCustomConfig"], result)

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#namespace_id ServiceDiscoveryService#namespace_id}.'''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#tags ServiceDiscoveryService#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#tags_all ServiceDiscoveryService#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceDnsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "dns_records": "dnsRecords",
        "namespace_id": "namespaceId",
        "routing_policy": "routingPolicy",
    },
)
class ServiceDiscoveryServiceDnsConfig:
    def __init__(
        self,
        *,
        dns_records: typing.Sequence["ServiceDiscoveryServiceDnsConfigDnsRecords"],
        namespace_id: builtins.str,
        routing_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_records: dns_records block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#dns_records ServiceDiscoveryService#dns_records}
        :param namespace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#namespace_id ServiceDiscoveryService#namespace_id}.
        :param routing_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#routing_policy ServiceDiscoveryService#routing_policy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dns_records": dns_records,
            "namespace_id": namespace_id,
        }
        if routing_policy is not None:
            self._values["routing_policy"] = routing_policy

    @builtins.property
    def dns_records(self) -> typing.List["ServiceDiscoveryServiceDnsConfigDnsRecords"]:
        '''dns_records block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#dns_records ServiceDiscoveryService#dns_records}
        '''
        result = self._values.get("dns_records")
        assert result is not None, "Required property 'dns_records' is missing"
        return typing.cast(typing.List["ServiceDiscoveryServiceDnsConfigDnsRecords"], result)

    @builtins.property
    def namespace_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#namespace_id ServiceDiscoveryService#namespace_id}.'''
        result = self._values.get("namespace_id")
        assert result is not None, "Required property 'namespace_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def routing_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#routing_policy ServiceDiscoveryService#routing_policy}.'''
        result = self._values.get("routing_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryServiceDnsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceDnsConfigDnsRecords",
    jsii_struct_bases=[],
    name_mapping={"ttl": "ttl", "type": "type"},
)
class ServiceDiscoveryServiceDnsConfigDnsRecords:
    def __init__(self, *, ttl: jsii.Number, type: builtins.str) -> None:
        '''
        :param ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#ttl ServiceDiscoveryService#ttl}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#type ServiceDiscoveryService#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ttl": ttl,
            "type": type,
        }

    @builtins.property
    def ttl(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#ttl ServiceDiscoveryService#ttl}.'''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#type ServiceDiscoveryService#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryServiceDnsConfigDnsRecords(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryServiceDnsConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceDnsConfigOutputReference",
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

    @jsii.member(jsii_name="resetRoutingPolicy")
    def reset_routing_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutingPolicy", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsRecordsInput")
    def dns_records_input(
        self,
    ) -> typing.Optional[typing.List[ServiceDiscoveryServiceDnsConfigDnsRecords]]:
        return typing.cast(typing.Optional[typing.List[ServiceDiscoveryServiceDnsConfigDnsRecords]], jsii.get(self, "dnsRecordsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceIdInput")
    def namespace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingPolicyInput")
    def routing_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routingPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsRecords")
    def dns_records(self) -> typing.List[ServiceDiscoveryServiceDnsConfigDnsRecords]:
        return typing.cast(typing.List[ServiceDiscoveryServiceDnsConfigDnsRecords], jsii.get(self, "dnsRecords"))

    @dns_records.setter
    def dns_records(
        self,
        value: typing.List[ServiceDiscoveryServiceDnsConfigDnsRecords],
    ) -> None:
        jsii.set(self, "dnsRecords", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @namespace_id.setter
    def namespace_id(self, value: builtins.str) -> None:
        jsii.set(self, "namespaceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingPolicy")
    def routing_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routingPolicy"))

    @routing_policy.setter
    def routing_policy(self, value: builtins.str) -> None:
        jsii.set(self, "routingPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceDiscoveryServiceDnsConfig]:
        return typing.cast(typing.Optional[ServiceDiscoveryServiceDnsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceDiscoveryServiceDnsConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceHealthCheckConfig",
    jsii_struct_bases=[],
    name_mapping={
        "failure_threshold": "failureThreshold",
        "resource_path": "resourcePath",
        "type": "type",
    },
)
class ServiceDiscoveryServiceHealthCheckConfig:
    def __init__(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
        resource_path: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param failure_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#failure_threshold ServiceDiscoveryService#failure_threshold}.
        :param resource_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#resource_path ServiceDiscoveryService#resource_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#type ServiceDiscoveryService#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if failure_threshold is not None:
            self._values["failure_threshold"] = failure_threshold
        if resource_path is not None:
            self._values["resource_path"] = resource_path
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def failure_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#failure_threshold ServiceDiscoveryService#failure_threshold}.'''
        result = self._values.get("failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resource_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#resource_path ServiceDiscoveryService#resource_path}.'''
        result = self._values.get("resource_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#type ServiceDiscoveryService#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryServiceHealthCheckConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryServiceHealthCheckConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceHealthCheckConfigOutputReference",
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

    @jsii.member(jsii_name="resetFailureThreshold")
    def reset_failure_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureThreshold", []))

    @jsii.member(jsii_name="resetResourcePath")
    def reset_resource_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourcePath", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureThresholdInput")
    def failure_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failureThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcePathInput")
    def resource_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourcePathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureThreshold")
    def failure_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "failureThreshold"))

    @failure_threshold.setter
    def failure_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "failureThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcePath")
    def resource_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourcePath"))

    @resource_path.setter
    def resource_path(self, value: builtins.str) -> None:
        jsii.set(self, "resourcePath", value)

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
    ) -> typing.Optional[ServiceDiscoveryServiceHealthCheckConfig]:
        return typing.cast(typing.Optional[ServiceDiscoveryServiceHealthCheckConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceDiscoveryServiceHealthCheckConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceHealthCheckCustomConfig",
    jsii_struct_bases=[],
    name_mapping={"failure_threshold": "failureThreshold"},
)
class ServiceDiscoveryServiceHealthCheckCustomConfig:
    def __init__(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param failure_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#failure_threshold ServiceDiscoveryService#failure_threshold}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if failure_threshold is not None:
            self._values["failure_threshold"] = failure_threshold

    @builtins.property
    def failure_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/service_discovery_service#failure_threshold ServiceDiscoveryService#failure_threshold}.'''
        result = self._values.get("failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceDiscoveryServiceHealthCheckCustomConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceDiscoveryServiceHealthCheckCustomConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.servicediscovery.ServiceDiscoveryServiceHealthCheckCustomConfigOutputReference",
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

    @jsii.member(jsii_name="resetFailureThreshold")
    def reset_failure_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureThreshold", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureThresholdInput")
    def failure_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failureThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureThreshold")
    def failure_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "failureThreshold"))

    @failure_threshold.setter
    def failure_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "failureThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceDiscoveryServiceHealthCheckCustomConfig]:
        return typing.cast(typing.Optional[ServiceDiscoveryServiceHealthCheckCustomConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceDiscoveryServiceHealthCheckCustomConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsServiceDiscoveryDnsNamespace",
    "DataAwsServiceDiscoveryDnsNamespaceConfig",
    "ServiceDiscoveryHttpNamespace",
    "ServiceDiscoveryHttpNamespaceConfig",
    "ServiceDiscoveryInstance",
    "ServiceDiscoveryInstanceConfig",
    "ServiceDiscoveryPrivateDnsNamespace",
    "ServiceDiscoveryPrivateDnsNamespaceConfig",
    "ServiceDiscoveryPublicDnsNamespace",
    "ServiceDiscoveryPublicDnsNamespaceConfig",
    "ServiceDiscoveryService",
    "ServiceDiscoveryServiceConfig",
    "ServiceDiscoveryServiceDnsConfig",
    "ServiceDiscoveryServiceDnsConfigDnsRecords",
    "ServiceDiscoveryServiceDnsConfigOutputReference",
    "ServiceDiscoveryServiceHealthCheckConfig",
    "ServiceDiscoveryServiceHealthCheckConfigOutputReference",
    "ServiceDiscoveryServiceHealthCheckCustomConfig",
    "ServiceDiscoveryServiceHealthCheckCustomConfigOutputReference",
]

publication.publish()
